"""Exercise both exact marker programs through the actual native owner bridge."""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import capstone
import check_biwn_media_setup_cpu as media
import biwn_fast_CPU_bridge as bridge

ROOT = Path(__file__).resolve().parents[1]


def main():
    candidate_path = ROOT / 'verification/dual-marker-native-CPU-experimental-candidate.json'
    candidate = json.loads(candidate_path.read_text())
    pinned = json.loads((ROOT / 'verification/CPU-IRQ-selection-core-experimental-candidate.json').read_text())
    core_path = Path(pinned['core_path'])
    assert candidate['required_core_sha256'] == pinned['core_sha256']
    oracle = media.scheduler.Native(diagnostic_core=core_path)
    runtime = media.Runtime.__new__(media.Runtime)
    runtime.oracle, runtime.device, runtime.core = oracle, oracle.device, oracle.lib
    core = oracle.lib
    out = ROOT / 'verification/dual-marker-bridge-checks' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    fixture = out / 'fixture.c'
    fixture.write_text('#include "' + str(core_path.parent / 'src/m68000/cpudefs.h') + '"\n'
                       'void marker_fixture(struct regstruct *s,unsigned usp,unsigned isp)'
                       '{s->usp=usp;s->isp=isp;s->interruptCycles=0;s->remainingCycles=0;s->intLevel=0;s->stopped=0;}\n')
    fixture_library = out / 'libfixture.dylib'
    subprocess.run(['clang', '-dynamiclib', '-std=c89', str(fixture), '-o', str(fixture_library)],
                   check=True, env=dict(os.environ, DEVELOPER_DIR='/Library/Developer/CommandLineTools'))
    fixture_keep = c.CDLL(str(fixture_library))
    seed = fixture_keep.marker_fixture
    seed.argtypes = [c.c_void_p, c.c_uint, c.c_uint]
    private = c.addressof((c.c_uint8 * 1).in_dll(core, 'regs'))
    ram = c.c_void_p.in_dll(core, 'jaguarMainRAM').value
    core.BIWNSetCPUExecOwner.argtypes = [bridge.OWNER, c.c_int]
    core.BIWNSetCPURetiredObserver.argtypes = [bridge.RETIRED]
    for name in ['Owned', 'Original', 'Rejected']:
        getattr(core, 'BIWNCPU' + name + 'InstructionCount').restype = c.c_uint64
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
    variants = [('original', bytes.fromhex(candidate['original_marker_bytes'])),
                ('repaired', bytes.fromhex(candidate['repaired_marker_bytes']))]
    initial = media.CPU()
    initial.registers[:] = [0x1c7fff, 0, 0x12345678, 0, 1, 2, 3, 4] + [0x70000 + i * 0x1000 for i in range(8)]
    initial.usp, initial.ssp = 0x180800, 0x1e0000
    rows = []

    def run(memory, source):
        core.BIWNSetCPUExecOwner(bridge.OWNER(), 0)
        core.BIWNSetCPURetiredObserver(bridge.RETIRED())
        runtime.device.seed(memory, 0)
        runtime.seed_cpu(initial)
        seed(private, initial.usp, initial.ssp)
        keep = bridge.install(core, out, 'C', ram, candidate_path, trace=False) if source else None
        cycles = core.m68k_execute(1)
        result = dict(CPU=media.scheduler.cpu_dict(runtime.cpu()), RAM=runtime.device.ram(), cycles=cycles)
        stats = keep[4]() if keep else None
        core.BIWNSetCPUExecOwner(bridge.OWNER(), 0)
        core.BIWNSetCPURetiredObserver(bridge.RETIRED())
        return result, stats

    try:
        for label, program in variants:
            for instruction in decoder.disasm(program, 0x1b0ee):
                count = 0
                for sr in list(range(32)) + list(range(0x2000, 0x2020)):
                    for operand in [0, 1, 2]:
                        initial.sr, initial.pc = sr, instruction.address
                        initial.registers[15] = initial.ssp if sr & 0x2000 else initial.usp
                        initial.registers[0] = [0x1c7fff, 0, 0xffffffff][operand]
                        initial.registers[10] = [0x71000, 0x1c7ffe, 0x1c8000][operand]
                        memory = bytearray(0x200000)
                        memory[0x1b0ee:0x1b100] = program
                        address = initial.registers[10]
                        memory[address:address + 4] = [0x12345678, 0, 0xffffffff][operand].to_bytes(4, 'big')
                        native, _ = run(bytes(memory), False)
                        source, stats = run(bytes(memory), True)
                        if native != source or stats['errors'] or stats['steps'] != 1:
                            detail = dict(variant=label, PC=hex(instruction.address), sr=sr, operand=operand,
                                          native_CPU=native['CPU'], source_CPU=source['CPU'],
                                          RAM_equal=native['RAM'] == source['RAM'], cycles=[native['cycles'], source['cycles']], stats=stats)
                            (out / 'mismatch.json').write_text(json.dumps(detail, indent=2) + '\n')
                            raise AssertionError(str(out / 'mismatch.json'))
                        count += 1
                rows.append(dict(variant=label, PC=hex(instruction.address), assembly=instruction.mnemonic + ' ' + instruction.op_str, cases=count))
        guards = []
        for label, program in variants:
            initial.sr, initial.pc = 0x2000, 0x1b0ee
            initial.registers[15], initial.registers[10] = initial.ssp, 0x71000
            memory = bytearray(0x200000)
            memory[0x1b0ee:0x1b100] = program
            memory[0x1b0ff] ^= 1
            source, stats = run(bytes(memory), True)
            assert stats['error_code'] == 96 and stats['steps'] == stats['retired'] == 0
            assert source['RAM'] == bytes(memory)
            guards.append(dict(variant=label, rejected_code=96, instruction_body_executed=False))
        report = dict(status='both_marker_variants_native_bridge_CPU_RAM_cycle_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                      directory=str(out), cases=sum(x['cases'] for x in rows), instructions=rows, whole_program_signature_guards=guards,
                      candidate=str(candidate_path), candidate_sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
                      source_sha256=candidate['source_sha256'], core_sha256=pinned['core_sha256'], whole_game_complete=False,
                      scope='Actual native owner bridge versus original opcode engine for every original/repaired marker instruction,32CCR values,user/supervisor,three declared address/data inputs. FullpublicCPU/mainRAM and returned instruction cycles match. Mutated18byte programs reject before executing a body. PrivateCPU/prefetch at isolated boundaries, complete functions and new full-route execution remain separate.')
        for path in [out / 'report.json', ROOT / 'verification/dual-marker-bridge-current.json']:
            path.write_text(json.dumps(report, indent=2) + '\n')
        print(report['status'], report['cases'], flush=True)
    finally:
        core.BIWNSetCPUExecOwner(bridge.OWNER(), 0)
        core.BIWNSetCPURetiredObserver(bridge.RETIRED())
        oracle.close()


if __name__ == '__main__':
    main()
