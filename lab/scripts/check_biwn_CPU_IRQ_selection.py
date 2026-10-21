"""Compare local selection against actual original interrupt paths, not another LLM."""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import check_biwn_media_setup_cpu as media
import biwn_CPU_IRQ_select_owner as owner

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'verification/CPU-IRQ-selection-core-experimental-candidate.json').read_text())
    assert manifest['status'] == 'compiled_core_tests_passed_pending_behavior_comparison'
    core_path = Path(manifest['core_path'])
    assert owner.sha(core_path) == manifest['core_sha256']
    oracle = media.scheduler.Native(diagnostic_core=core_path)
    runtime = media.Runtime.__new__(media.Runtime)
    runtime.oracle, runtime.device, runtime.core = oracle, oracle.device, oracle.lib
    core = oracle.lib
    core.BIWNSetCPUInterruptSelector.argtypes = [c.c_void_p]
    core.m68k_set_irq2.argtypes = [c.c_uint]
    core.BIWNCPUCheckInterruptsForTest.argtypes = []
    core.m68k_diag_interrupt_count.restype = c.c_uint
    core.M68KStateSave.argtypes = [c.c_void_p]
    core.M68KStateSave.restype = c.c_size_t
    out = ROOT / 'verification/CPU-IRQ-selection-checks' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    fixture = out / 'fixture.c'
    fixture.write_text('#include "' + str(core_path.parent / 'src/m68000/cpudefs.h') + '"\n'
                       'void biwn_irq_fixture(struct regstruct *state,unsigned usp,unsigned isp,unsigned level,unsigned mask)'
                       '{state->interruptCycles=0;state->remainingCycles=0;state->usp=usp;state->isp=isp;state->intLevel=level;state->intmask=mask;state->stopped=0;}\n')
    library = out / 'libfixture.dylib'
    subprocess.run(['clang', '-dynamiclib', '-std=c89', '-O2', str(fixture), '-o', str(library)],
                   env=dict(os.environ, DEVELOPER_DIR='/Library/Developer/CommandLineTools'), check=True)
    fixture_library = c.CDLL(str(library))
    seed = fixture_library.biwn_irq_fixture
    seed.argtypes = [c.c_void_p] + [c.c_uint] * 4
    private = c.addressof((c.c_uint8 * 1).in_dll(core, 'regs'))
    memory = bytearray(0x200000)
    for vector in range(256):
        memory[vector * 4:vector * 4 + 4] = (0x190000 + vector * 4).to_bytes(4, 'big')
    initial = media.CPU()
    initial.registers[:] = [0x12340000 + i * 0x102 for i in range(16)]
    initial.pc, initial.usp, initial.ssp = 0x12340, 0x180800, 0x1e0000
    rows = []

    def run(kind, previous, level, mask, supervisor, source):
        core.BIWNSetCPUInterruptSelector(None)
        initial.sr = (0x2000 if supervisor else 0) | mask << 8 | 0x15
        initial.registers[15] = initial.ssp if supervisor else initial.usp
        runtime.device.seed(bytes(memory), 0)
        runtime.seed_cpu(initial)
        seed(private, initial.usp, initial.ssp, previous if kind else level, mask)
        before = c.create_string_buffer(512)
        assert core.M68KStateSave(before) == 148
        keep = owner.install_selector(core) if source else None
        before_count = core.m68k_diag_interrupt_count()
        if kind:
            core.m68k_set_irq2(level)
        else:
            core.BIWNCPUCheckInterruptsForTest()
        raw = c.create_string_buffer(512)
        assert core.M68KStateSave(raw) == 148
        result = dict(before=before.raw[:148], CPU=raw.raw[:148], RAM=runtime.device.ram(),
                      serviced=core.m68k_diag_interrupt_count() - before_count)
        if keep:
            assert core.BIWNCPUInterruptOwnedCount() == 1
            assert core.BIWNCPUInterruptOriginalCount() == 0 and core.BIWNCPUInterruptRejectedCount() == 0
            # Check the exact public function inputs too, including every
            # ignored-but-valid previous level for the ordinary-check kind.
            assert keep[1](kind, previous, level, mask) == (level if result['serviced'] else 0)
        core.BIWNSetCPUInterruptSelector(None)
        return result

    try:
        for kind, previous, level, mask, supervisor in itertools.product(range(2), range(8), range(8), range(8), [False, True]):
            original = run(kind, previous, level, mask, supervisor, False)
            source = run(kind, previous, level, mask, supervisor, True)
            if original != source:
                detail = dict(kind=kind, previous=previous, level=level, mask=mask, supervisor=supervisor,
                              equal={k: original[k] == source[k] for k in original},
                              original_serviced=original['serviced'], source_serviced=source['serviced'])
                (out / 'mismatch.json').write_text(json.dumps(detail, indent=2) + '\n')
                raise AssertionError(str(out / 'mismatch.json'))
            rows.append(dict(kind=kind, previous=previous, level=level, mask=mask, supervisor=supervisor,
                             serviced=source['serviced'], CPU_sha256=hashlib.sha256(source['CPU']).hexdigest(),
                             RAM_sha256=hashlib.sha256(source['RAM']).hexdigest()))
        # Host-domain rejection is a separate API requirement, outside original
        # emulator behavior. Check invalid unsigned values without calling devices.
        keep = owner.install_selector(core)
        fn = keep[1]
        guards = []
        for position, values in [(0, [2, 8, 0xffffffff]), (1, [8, 255, 0xffffffff]),
                                 (2, [8, 255, 0xffffffff]), (3, [8, 255, 0xffffffff])]:
            for kind in range(2):
                for value in values:
                    args = [kind, 0, 2, 0]
                    args[position] = value
                    assert fn(*args) == -1
                    guards.append(args)
        core.BIWNSetCPUInterruptSelector(None)
        # A rejected delegated choice must not fall through to original IRQ
        # entry, nor resume original CPU instructions in a subsequent execute.
        bad_type = c.CFUNCTYPE(c.c_int, c.c_uint, c.c_uint, c.c_uint, c.c_uint)
        bad = bad_type(lambda *_: -1)
        runtime.device.seed(bytes(memory), 0)
        runtime.seed_cpu(initial)
        seed(private, initial.usp, initial.ssp, 0, 0)
        core.BIWNSetCPUInterruptSelector(c.cast(bad, c.c_void_p))
        before_count = core.m68k_diag_interrupt_count()
        core.m68k_set_irq2(2)
        before = c.create_string_buffer(512)
        assert core.M68KStateSave(before) == 148
        core.m68k_execute(1000)
        after = c.create_string_buffer(512)
        assert core.M68KStateSave(after) == 148
        assert before.raw[:148] == after.raw[:148]
        assert core.m68k_diag_interrupt_count() == before_count
        assert core.BIWNCPUInterruptRejectedCount() == 1 and core.BIWNCPUInterruptOriginalCount() == 0
        core.BIWNSetCPUInterruptSelector(None)
        (out / 'cases.json').write_text(json.dumps(rows, indent=2) + '\n')
        report = dict(status='native_original_and_source_interrupt_selection_match', directory=str(out),
                      recorded_at=datetime.now(timezone.utc).isoformat(), cases=len(rows), invalid_API_guards=len(guards),
                      rejected_choice_freezes_without_original_fallback=True, original_core_path=str(core_path),
                      core_sha256=manifest['core_sha256'], core_suite_exit=manifest['core-tests_exit'],
                      local_model_authored_selector=True, coordinator_recovered_contract_and_verifier=True,
                      whole_game_complete=False, scope='Every valid kind/previous/level/mask input with user and supervisor CPU. Actual original m68k_set_irq2 or m68ki_check_interrupts versus delegated decision; full148byteCPUstate, service count and2MBRAM match. Entry/ACK still original in this fixture. Core default-off inertness in long frame replay, event-line resampling, combined source entry/runtime integration, hardware accuracy and standalone execution remain separate.')
        assert owner.sha(core_path) == manifest['core_sha256']
        for p in [out / 'report.json', ROOT / 'verification/CPU-IRQ-selection-current.json']:
            p.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report), flush=True)
    finally:
        core.BIWNSetCPUInterruptSelector(None)
        oracle.close()


if __name__ == '__main__':
    main()
