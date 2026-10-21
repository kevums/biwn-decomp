"""Compare the live-RAM DSP owner at startup and command1/2 boundaries.

Complements the separate silent/sample-voice fixtures. It does not run a song,
game frames, physical audio, or replace the original DSP IRQ provider.
"""
import argparse
import ctypes as c
import json
import random
import struct
from datetime import datetime, timezone
from pathlib import Path

import check_biwn_music_DSP_bootstrap as boot
import biwn_DSP_program_router as router

ROOT = boot.ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, required=True)
    parser.add_argument('--owner-candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    session = Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping = json.loads((session/'music-DSP-engine-generation.json').read_text())
    rows = {row['address']: row for row in mapping['instructions_decoded']}
    # The two SSI/timer vector stubs below this address belong to the separate
    # mixer/interrupt fixtures. Retain them in the combined316-location gate.
    mixer_vectors = {0xf1b010, 0xf1b016, 0xf1b018, 0xf1b020, 0xf1b026, 0xf1b028}
    target = {pc for pc in rows if pc < 0xf1b148}-mixer_vectors
    out = ROOT/'verification/BIWN-music-DSP-bootstrap-owner'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    baseline = (ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    helper = json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text())
    runtime = boot.media.Runtime(Path(helper['directory'])/'libentry-helpers.dylib', [], diagnostic_core=args.core)
    core = runtime.core
    core.DSPGetPC.restype = c.c_uint32
    core.DSPExec.argtypes = [c.c_int32]
    core.DSPStateLoad.argtypes = [c.c_void_p]
    core.DSPStateLoad.restype = c.c_size_t
    core.DSPWriteLong.argtypes = [c.c_uint32, c.c_uint32, c.c_uint32]
    core.DSPReadLong.argtypes = [c.c_uint32, c.c_uint32]
    core.DSPReadLong.restype = c.c_uint32
    core.DACStateLoad.argtypes = [c.c_void_p, c.c_uint32]
    core.DACStateLoad.restype = c.c_size_t
    counter = c.c_uint32.in_dll(core, 'dsp_exec_opcode_count')
    rng = random.Random(0xc01d)
    coverage = set()
    cases = []

    def raw(name):
        buf = c.create_string_buffer(200000)
        size = runtime.savers[name](buf)
        return buf.raw[:size]

    def checkpoint(kind, **fields):
        logical = raw('DSP')[:8496]
        hardware = runtime.snapshot()['hardware']
        hardware['DSP'] = dict(size=8496, sha256=boot.sha(logical))
        return dict(kind=kind, DSP=boot.sha(logical), RAM=boot.sha(runtime.device.ram()),
                    hardware=hardware, **fields)

    def exercise(owned):
        trace = []
        def pump(stop):
            for _ in range(10000):
                pc = core.DSPGetPC()
                if pc == stop:return
                assert pc in rows, hex(pc)
                before = core.BIWNDSPOwnedInstructionCount() if owned else counter.value
                core.DSPExec(1)
                count = (core.BIWNDSPOwnedInstructionCount()-before if owned else
                         (counter.value-before)&0xffffffff)
                assert count in [1, 2], (hex(pc), count)
                if not owned:
                    coverage.add(pc)
                    if count == 2:coverage.add(pc+rows[pc]['size'])
                trace.append(checkpoint('step', PC=pc, instructions=count))
            raise AssertionError(('DSP bootstrap bound', hex(stop), hex(core.DSPGetPC())))
        pump(0xf1b144)
        # Command1 stops the engine at the command wait loop. Command2 then
        # copies the supplied song header and acknowledges the mailbox.
        for command in commands:
            core.DSPWriteLong(0xf1badc, command, 6)
            core.DSPWriteLong(0xf1a114, 5, 6)
            assert core.DSPGetPC() == 0xf1b000
            trace.append(checkpoint('CPU_mailbox_IRQ', command=command))
            pump(0xf1b144 if command == 1 else 0xf1b148)
            assert core.DSPReadLong(0xf1badc, 6) == 0
        return trace

    try:
        for case in range(8):
            commands = [1, 2] if case&1 else [2]
            runtime.reset(baseline, case%3)
            payload = baseline[0x7248:0x8458]
            c.memmove(core.DSPGetRAM(), payload, len(payload))
            core.DSPWriteLong(0xf1bae0, 0x3bce0, 6)
            core.DSPWriteLong(0xf1bae4, 0, 6)
            initial = bytearray(raw('DSP'))
            assert len(initial) == 8729
            struct.pack_into('=I', initial, 8192, 0xf1b126)
            struct.pack_into('=I', initial, 8212, (0x40000 if case&1 else 0)|(case&7))
            struct.pack_into('=I', initial, 8228, 0x2001)
            initial[8236:8239] = bytes([case&1, (case>>2)&1, (case>>1)&1])
            struct.pack_into('=64I', initial, 8239, *[rng.getrandbits(32) for _ in range(64)])
            initial[8495] = 0
            initial = bytes(initial)
            RAM = runtime.device.ram()
            DAC = raw('DAC')
            # The version9 loader canonicalizes part of the DAC state. Apply
            # it before both paths, then retain that exact shared starting state.
            assert core.DACStateLoad(c.create_string_buffer(DAC), 9) == len(DAC)
            DAC = raw('DAC')
            assert core.DSPStateLoad(c.create_string_buffer(initial)) == len(initial)
            native = exercise(False)
            final_native = checkpoint('final')
            runtime.reset(RAM, case%3)
            assert core.DACStateLoad(c.create_string_buffer(DAC), 9) == len(DAC)
            assert core.DSPStateLoad(c.create_string_buffer(initial)) == len(initial)
            folder = out/('case-'+str(case));folder.mkdir()
            owner = router.install(core, folder, args.owner_candidate)
            try:
                rebuilt = exercise(True)
                final_rebuilt = checkpoint('final')
            finally:
                report = owner[3]()
            if native != rebuilt or final_native != final_rebuilt:
                boot.save(folder/'mismatch.json', dict(native=native, rebuilt=rebuilt,
                          native_final=final_native, rebuilt_final=final_rebuilt))
                raise AssertionError(str(folder/'mismatch.json'))
            assert report['errors'] == report['uncovered'] == 0
            assert report['core_counts']['Original'] == report['core_counts']['Rejected'] == 0
            assert report['core_counts']['Owned'] > 0
            cases.append(dict(case=case, commands=commands, checkpoints=len(native),
                              owner_report=str(folder/'DSP-owner-report.json'), matched=True))
            boot.save(out/'cases.json', cases)
            print('case', case, commands, len(native), 'native/source checkpoints match', flush=True)
        missing = sorted(target-coverage)
        coverage_report = dict(expected=len(target), observed=len(target&coverage),
                               covered_PC=sorted(coverage), missing_PC=missing)
        boot.save(out/'coverage.json', coverage_report)
        assert not missing, [hex(pc) for pc in missing]
        candidate = json.loads(args.owner_candidate.read_text())
        report = dict(status='DSP_source_owner_startup_command1_command2_native_match',
            directory=str(out), core=str(args.core), core_sha256=boot.sha(args.core.read_bytes()),
            owner_candidate=str(args.owner_candidate), cases=cases, coverage=coverage_report,
            owner_candidate_sha256=boot.sha(args.owner_candidate.read_bytes()),
            owner_library_sha256=boot.sha(Path(candidate['library']).read_bytes()),
            test_script_sha256=boot.sha(Path(__file__).read_bytes()),
            separate_mixer_vector_PC=sorted(mixer_vectors),
            recorded_at=datetime.now(timezone.utc).isoformat(), whole_game_complete=False,
            scope='Eight explicit startup register/flag profiles; command2 or command1 then2; per-atomic DSP logical8496 bytes, full2MB RAM and saved peripherals compare. Captured game payload/song header, external CPU mailbox/IRQ and original IRQ/device providers retained. No game frames, song playback, physical audio or standalone claim.')
        boot.save(args.output, report)
        boot.save(out/'status.json', dict(status='terminal_pass'))
        print(report['status'], coverage_report['observed'], '/', coverage_report['expected'], flush=True)
    except BaseException as error:
        boot.save(out/'status.json', dict(status='terminal_failed', error=repr(error)))
        raise
    finally:
        runtime.oracle.close()


if __name__ == '__main__':main()
