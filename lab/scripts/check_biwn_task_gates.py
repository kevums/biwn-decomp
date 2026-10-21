"""Compare readable peer-task gates with actual original DF22/DF3E bodies."""
import argparse
import copy
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000, UC_M68K_REG_D0, UC_M68K_REG_A7, UC_M68K_REG_PC, UC_M68K_REG_SR
import check_biwn_media_setup_cpu as media

ROOT = Path(__file__).resolve().parents[1]
RESTORE = ROOT / 'projects/black-ice-white-noise/restoration'
SP, STOP, CURRENT = 0x1ef800, 0x1f0000, 0xc0920
ENTRIES = {'pause': 0xdf22, 'resume': 0xdf3e}
SENTINEL = 0xa5a55a5a

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value): Path(path).write_text(json.dumps(value, indent=2) + '\n')

class Bus:
    def __init__(self, raw, queues=None, failure=None):
        self.memory = bytearray(raw)
        self.memory[SP:SP + 4] = STOP.to_bytes(4, 'big')
        self.trace, self.errors = [], []
        self.queues = copy.deepcopy(queues or {})
        self.failure = failure
    def access(self, kind, address, value=None):
        if self.failure == len(self.trace): raise RuntimeError('injected callback failure')
        if not 0 <= address <= len(self.memory) - 4: raise RuntimeError('outside supplied RAM')
        if kind == 'r':
            queue = self.queues.get(address)
            value = queue.pop(0) if queue else int.from_bytes(self.memory[address:address + 4], 'big')
        else:
            self.memory[address:address + 4] = value.to_bytes(4, 'big')
        self.trace.append([kind, address, value])
        return value

def original(bus, mode, incoming, coverage):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000); cpu.mem_write(0, bytes(bus.memory))
    cpu.reg_write(UC_M68K_REG_SR, 0x2000); cpu.reg_write(UC_M68K_REG_A7, SP); cpu.reg_write(UC_M68K_REG_D0, incoming)
    def code(engine, address, size, opaque):
        assert ENTRIES[mode] <= address < (0xdf3e if mode == 'pause' else 0xdf60), hex(address)
        coverage.add(address)
    def read(engine, access, address, width, value, opaque):
        if address == SP: assert width == 4; return
        assert width == 4
        engine.mem_write(address, bus.access('r', address).to_bytes(4, 'big'))
    def write(engine, access, address, width, value, opaque):
        assert width == 4
        bus.access('w', address, value & 0xffffffff)
    cpu.hook_add(UC_HOOK_CODE, code); cpu.hook_add(UC_HOOK_MEM_READ, read); cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(ENTRIES[mode], STOP, count=20000)
    assert cpu.reg_read(UC_M68K_REG_PC) == STOP and cpu.reg_read(UC_M68K_REG_A7) == SP + 4
    assert cpu.reg_read(UC_M68K_REG_D0) == incoming
    return incoming

def translated(function, bus, incoming, budget=1024, missing=None):
    world = media.scheduler.cleanup.world
    def read(_, address, result):
        if _ != 0x51475231: bus.errors.append('wrong read callback context'); return 1
        try: result[0] = bus.access('r', address); return 0
        except RuntimeError as error: bus.errors.append(str(error)); return 1
    def write(_, address, value):
        if _ != 0x51475231: bus.errors.append('wrong write callback context'); return 1
        try: bus.access('w', address, value); return 0
        except RuntimeError as error: bus.errors.append(str(error)); return 1
    rd, wr = world.R32(read), world.W32(write)
    interface = media.Bus(world.R8(), world.R16(), rd if missing != 'read32' else world.R32(),
                          world.W16(), wr if missing != 'write32' else world.W32(), world.CALL(), 0x51475231, 0)
    result = c.c_uint32(SENTINEL)
    code = function(None if missing == 'bus' else c.byref(interface), budget, incoming,
                    None if missing == 'out' else c.byref(result))
    return code, result.value

def fixtures(snapshot):
    counters = [0, 1, 2, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff]
    for count in [1, 2, 3, 8]:
        for offset in range(len(counters)):
            memory = bytearray(snapshot)
            nodes = [0x170000 + i * 0x100 for i in range(count)]
            current = nodes[offset % count]
            memory[CURRENT:CURRENT + 4] = current.to_bytes(4, 'big')
            for i, address in enumerate(nodes):
                memory[address:address + 4] = nodes[(i + 1) % count].to_bytes(4, 'big')
                memory[address + 34:address + 38] = counters[(i + offset) % len(counters)].to_bytes(4, 'big')
            for mode in ENTRIES:
                yield dict(name=f'{mode}_{count}_nodes_{offset}', mode=mode, RAM=bytes(memory),
                    incoming=(0x89ab0000 + offset * 31) & 0xffffffff, nodes=count,
                    budget=max(count - 1, 1), queues={})
    # The second SUBQ read is independent of TST, even when it changes to0.
    seed = next(x for x in fixtures_without_queues(snapshot) if x['nodes'] == 3)
    current = int.from_bytes(seed['RAM'][CURRENT:CURRENT + 4], 'big')
    peer = int.from_bytes(seed['RAM'][current:current + 4], 'big')
    for first, second in [(1, 0), (1, 0xffffffff), (0xffffffff, 0x80000000), (0, 99)]:
        yield dict(seed, name=f'resume_changing_read_{first}_{second}', mode='resume', queues={peer + 34: [first, second]})

def fixtures_without_queues(snapshot):
    # Small seed independent of the generator above.
    raw = bytearray(snapshot); nodes = [0x170000, 0x170100, 0x170200]
    raw[CURRENT:CURRENT + 4] = nodes[0].to_bytes(4, 'big')
    for i, address in enumerate(nodes):
        raw[address:address + 4] = nodes[(i + 1) % 3].to_bytes(4, 'big')
        raw[address + 34:address + 38] = (i + 1).to_bytes(4, 'big')
    yield dict(name='three_nodes', mode='pause', RAM=bytes(raw), incoming=0x12345678, nodes=3, budget=2, queues={})

def native(runtime, case, coverage):
    bus = Bus(case['RAM'])
    runtime.device.seed(bytes(bus.memory), 0)
    cpu = media.CPU(); cpu.registers[:] = [case['incoming']] + [i * 0x11111111 for i in range(1, 15)] + [SP]
    cpu.pc, cpu.sr, cpu.usp, cpu.ssp = ENTRIES[case['mode']], 0x2000, 0x180800, SP
    runtime.seed_cpu(cpu)
    for steps in range(20000):
        pc = runtime.core.m68k_get_reg(None, 16)
        if pc == STOP: break
        assert ENTRIES[case['mode']] <= pc < (0xdf3e if case['mode'] == 'pause' else 0xdf60), hex(pc)
        coverage.add(pc); runtime.core.m68k_execute(1)
    else: raise AssertionError('Native task ring work bound')
    result = runtime.cpu()
    assert result.registers[0] == case['incoming'] and result.registers[15] == SP + 4
    for i in list(range(2, 8)) + list(range(10, 15)): assert result.registers[i] == cpu.registers[i]
    return runtime.device.ram(), steps

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--source', type=Path, required=True); args = ap.parse_args()
    out = ROOT / 'verification/task-gates' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True); print(out, flush=True)
    source = out / 'biwn_task_gates.c'; source.write_bytes(args.source.read_bytes())
    assert '#include "biwn_task_gates.h"' in source.read_text()
    library = out / 'libtask-gates.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(RESTORE), str(source), '-o', str(library)]
    compiled = subprocess.run(command, capture_output=True, text=True, env={**os.environ, 'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out / 'compiler.log').write_text(compiled.stdout + compiled.stderr); assert compiled.returncode == 0, compiled.stderr
    lib = c.CDLL(str(library))
    functions = {mode: getattr(lib, 'biwn_task_' + mode + '_others') for mode in ENTRIES}
    for fn in functions.values(): fn.argtypes = [c.POINTER(media.Bus), c.c_uint32, c.c_uint32, c.POINTER(c.c_uint32)]; fn.restype = c.c_int
    snapshot = (ROOT / 'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    rows = list(fixtures(snapshot)); real_sources = []
    natural = json.loads((ROOT / 'verification/natural-coordinate-gameplay-current.json').read_text())
    for row in natural['cases']:
        proof_path = Path(row['proof']); assert sha(proof_path) == row['proof_sha256']
        proof = json.loads(proof_path.read_text()); ram_path = Path(proof['directory']) / 'C/final-RAM.bin'
        raw = ram_path.read_bytes(); node = start = int.from_bytes(raw[CURRENT:CURRENT + 4], 'big'); seen = set()
        while node not in seen:
            assert 0 <= node < len(raw) - 38 and len(seen) < 512
            seen.add(node); node = int.from_bytes(raw[node:node + 4], 'big')
        assert node == start
        real_sources.append(dict(case=row['case'], path=str(ram_path), sha256=sha(ram_path), task_nodes=len(seen), inherited_repair_bytes=18))
        for mode in ENTRIES:
            # As-captured ring, plus a paused version computed by readable C.
            rows.append(dict(name='captured_' + row['case'] + '_' + mode, mode=mode, RAM=raw, incoming=0xfedcba98,
                nodes=len(seen), budget=len(seen) - 1, queues={}))
        paused = Bus(raw); status, _ = translated(functions['pause'], paused, 0, len(seen) - 1); assert status == 0
        rows.append(dict(name='captured_' + row['case'] + '_pause_then_resume', mode='resume', RAM=bytes(paused.memory),
            incoming=0xfedcba98, nodes=len(seen), budget=len(seen) - 1, queues={}))
    coverage, native_coverage, results, guards = set(), set(), [], []
    core = Path(json.loads((ROOT / 'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    oracle = media.scheduler.Native(diagnostic_core=core)
    runtime = media.Runtime.__new__(media.Runtime); runtime.oracle, runtime.device, runtime.core = oracle, oracle.device, oracle.lib
    try:
        for case in rows:
            left, right = Bus(case['RAM'], case['queues']), Bus(case['RAM'], case['queues'])
            expected = original(left, case['mode'], case['incoming'], coverage)
            status, result = translated(functions[case['mode']], right, case['incoming'], case['budget'])
            assert status == 0 and result == expected and right.trace == left.trace and right.memory == left.memory, case['name']
            native_steps = None
            if not case['queues']:
                memory, native_steps = native(runtime, case, native_coverage)
                assert memory == right.memory, case['name']
            results.append(dict(name=case['name'], mode=case['mode'], peer_nodes=case['nodes'] - 1,
                callback_count=len(right.trace), trace_sha256=hashlib.sha256(json.dumps(right.trace).encode()).hexdigest(),
                final_RAM_sha256=hashlib.sha256(right.memory).hexdigest(), native_steps=native_steps,
                original_full_D0=True, all_RAM_matches=True))
        seed = next(fixtures_without_queues(snapshot))
        for mode in ENTRIES:
            baseline = Bus(seed['RAM']); assert translated(functions[mode], baseline, seed['incoming'], 2)[0] == 0
            for index in range(len(baseline.trace)):
                failed = Bus(seed['RAM'], failure=index)
                status, result = translated(functions[mode], failed, seed['incoming'], 2)
                prefix = Bus(seed['RAM'])
                for kind, address, value in baseline.trace[:index]:
                    assert prefix.access(kind, address, value) == value
                assert status == 2 and result == SENTINEL and failed.trace == baseline.trace[:index] and failed.memory == prefix.memory
                guards.append(dict(mode=mode, failure_at_callback=index, earlier_effects_retained=True, output_unchanged=True))
            for missing in ['bus', 'out', 'read32', 'write32', 'budget']:
                bus = Bus(seed['RAM']); status, result = translated(functions[mode], bus, 0, 0 if missing == 'budget' else 2, missing)
                assert status == 1 and result == SENTINEL and not bus.trace
                guards.append(dict(mode=mode, missing=missing, no_effects=True))
            limited = Bus(seed['RAM']); status, result = translated(functions[mode], limited, 0, 1)
            # Initial two reads, one peer, next pointer read; then stop.
            stop = next(i + 1 for i, event in enumerate(baseline.trace) if event[:2] == ['r', 0x170100])
            assert status == 4 and result == SENTINEL and limited.trace == baseline.trace[:stop]
            guards.append(dict(mode=mode, limit_after_one_peer=True, no_callback_for_next_peer=True))
            malformed = bytearray(seed['RAM']); malformed[0x170100:0x170104] = (0x170100).to_bytes(4, 'big')
            bus = Bus(malformed); status, result = translated(functions[mode], bus, 0, 3)
            assert status == 4 and result == SENTINEL
            guards.append(dict(mode=mode, malformed_cycle_bounded=True, original_timeout_inferred=False))
    finally: oracle.close()
    import capstone
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
    addresses = {instruction.address for instruction in decoder.disasm(snapshot[0xdf22:0xdf60], 0xdf22)}
    assert coverage == native_coverage == addresses
    save(out / 'cases.json', results); save(out / 'guards.json', guards)
    report = dict(status='task_pause_resume_original_and_native_match', recorded_at=datetime.now(timezone.utc).isoformat(),
        directory=str(out), source=str(source), source_sha256=sha(source), header=str(RESTORE / 'biwn_task_gates.h'),
        header_sha256=sha(RESTORE / 'biwn_task_gates.h'), library=str(library), library_sha256=sha(library),
        original_cases=len(results), native_cases=sum(x['native_steps'] is not None for x in results),
        changing_read_cases=sum(bool(x['queues']) for x in rows), instruction_locations=[len(coverage), len(addresses)],
        guards=len(guards), captured_game_task_rings=real_sources, core=str(core), core_sha256=sha(core), compiler=command,
        full_D0=True, all_public_RAM=True, ordered_data_accesses=True, live_frame_runtime_changed=False,
        original_program_modified=False, whole_game_complete=False,
        scope='Actual original DF22/DF3E versus readable traversal, including empty peer ring,1/2/7peers, unsigned counter boundaries, changing TST/SUBQ reads, and three real18-task rings captured from accepted source gameplay. Native lane excludes four queued-read cases; all native cases compare full RAM/D0/callee-save registers. This is function-level task-gate logic, not asynchronous scheduling, live-frame integration or physical timing. Host limits/errors are added behavior.')
    save(out / 'report.json', report); save(ROOT / 'verification/task-gates-current.json', report)
    print(json.dumps(dict(status=report['status'], cases=len(results), native=report['native_cases'], guards=len(guards))), flush=True)

if __name__ == '__main__': main()
