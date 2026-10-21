"""Compare portable byte copying and register-command planning with original CPU bytes.

Device writes are captured in ordinary mapped memory, without device behavior.
"""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess

import unicorn
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import extract_biwn_stage as stage

SP, STOP = 0x1ff000, 0x1ffe00


class Command(c.Structure):
    _fields_ = [('address', c.c_uint32), ('value', c.c_uint32)]


def original(image, entry, source, destination, count, seed):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_map(0xf02000, 0x1000)
    cpu.mem_write(0x4000, image)
    cpu.mem_write(0x110000, seed)
    args = [STOP, source, destination, count] if entry == 0xe3e0 else [STOP, destination, source, count]
    cpu.mem_write(SP, b''.join(x.to_bytes(4, 'big') for x in args))
    cpu.reg_write(UC_M68K_REG_A7, SP)
    saved = [(UC_M68K_REG_D2, 0x12345678), (UC_M68K_REG_D3, 0x76543210), (UC_M68K_REG_D4, 0x89abcdef)]
    for reg, value in saved: cpu.reg_write(reg, value)
    before = bytes(cpu.mem_read(0, 0x200000))
    writes, commands, trace = [], [], []
    def code(engine, address, size, _):
        assert 0xe3e0 <= address < 0xe4aa
        trace.append(address)
    def write(engine, access, address, size, value, _):
        value &= (1 << (size * 8)) - 1
        row = {'address': address, 'bytes': size, 'value': value}
        if 0xf02000 <= address < 0xf03000:
            assert size == 4
            commands.append((address, value))
        else: writes.append(row)
    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(entry, STOP, count=5000, timeout=1_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC) == STOP
    assert cpu.reg_read(UC_M68K_REG_A7) == SP + 4
    for reg, value in saved: assert cpu.reg_read(reg) == value
    expected = bytearray(before)
    for row in writes:
        address, size = row['address'], row['bytes']
        expected[address:address + size] = row['value'].to_bytes(size, 'big')
    assert bytes(cpu.mem_read(0, 0x200000)) == bytes(expected), 'Uncaptured RAM mutation'
    if count < 128:
        assert len(writes) == count and not commands
        assert [row['address'] for row in writes] == list(range(destination, destination + count))
    else:
        assert [row['address'] for row in writes] == [SP - 4, SP - 8, SP - 12]
        assert [row['value'] for row in writes] == [value for _, value in saved]
    assert cpu.reg_read(UC_M68K_REG_A0) == (destination + count) & 0xffffffff
    assert cpu.reg_read(UC_M68K_REG_A1) == (source + count) & 0xffffffff
    assert cpu.reg_read(UC_M68K_REG_D1) == 0
    return {'commands': commands, 'RAM': bytes(cpu.mem_read(0x110000, len(seed))),
            'D0': cpu.reg_read(UC_M68K_REG_D0), 'instructions': len(trace)}


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    assert stage.digest(image) == stage.STAGE_SHA
    source_dir = root / 'projects/black-ice-white-noise/restoration'
    folder = root / 'verification/biwn-copy' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    folder.mkdir(parents=True)
    library = folder / 'libbiwn_copy.dylib'
    compiler = ['clang', '-dynamiclib', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O2', str(source_dir / 'biwn_copy.c'), '-o', str(library)]
    subprocess.run(compiler, check=True, capture_output=True, env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    lib = c.CDLL(str(library))
    small = lib.biwn_copy_cpu_bytes
    small.argtypes = [c.POINTER(c.c_uint8), c.c_size_t, c.c_uint32, c.c_uint32, c.c_uint32]
    small.restype = c.c_int
    plan = lib.biwn_copy_device_commands
    plan.argtypes = [c.c_uint32, c.c_uint32, c.c_uint32, c.POINTER(Command), c.c_size_t,
                     c.POINTER(c.c_size_t), c.POINTER(c.c_uint32), c.POINTER(c.c_uint32)]
    plan.restype = c.c_int
    rng = random.Random(0xe3e0)
    seed = rng.randbytes(512)
    rows = []
    # Exact forward-overlap semantics, with every supported nonzero count.
    for entry in [0xe3e0, 0xe3ee]:
        for count in range(128):
            for delta in [-1, 0, 1, 200]:
                source, destination = 0x110080, 0x110080 + delta
                cpu = original(image, entry, source, destination, count, seed)
                buffer = (c.c_uint8 * len(seed)).from_buffer_copy(seed)
                assert small(buffer, len(seed), source - 0x110000, destination - 0x110000, count) == 0
                assert bytes(buffer) == cpu['RAM']
                rows.append({'entry': hex(entry), 'count': count, 'destination_delta': delta,
                             'instructions': cpu['instructions'], 'path': 'CPU_bytes'})
    small_count = len(rows)
    # All phrase-offset combinations, odd counts, and single/multiple chunks.
    for entry in [0xe3e0, 0xe3ee]:
        for count in [128, 129, 65535, 65536, 65537, 131071, 131072, 131073]:
            for source_offset in range(8):
                for destination_offset in range(8):
                    # One wrapped-address case per combination: no actual source/dest memory accesses on this path.
                    source = (0xffff0000 if count == 131073 else 0x110000) + source_offset
                    destination = 0x120000 + destination_offset
                    cpu = original(image, entry, source, destination, count, seed)
                    commands = (Command * 32)()
                    used, end_source, end_destination = c.c_size_t(), c.c_uint32(), c.c_uint32()
                    assert plan(source, destination, count, commands, 32, c.byref(used), c.byref(end_source), c.byref(end_destination)) == 0
                    actual = [(commands[i].address, commands[i].value) for i in range(used.value)]
                    assert actual == cpu['commands']
                    assert end_source.value == (source + count) & 0xffffffff
                    assert end_destination.value == (destination + count) & 0xffffffff
                    assert cpu['D0'] == actual[-1][1]
                    rows.append({'entry': hex(entry), 'count': count, 'source': hex(source), 'destination': hex(destination),
                                 'commands': actual, 'instructions': cpu['instructions'], 'path': 'device_command_trace'})
    guards = []
    for count, capacity, expected in [(127, 32, 1), (0x80000000, 32, 1), (0xffffffff, 32, 1), (128, 7, 2)]:
        commands = (Command * 32)(*[Command(0xdeadbeef, 0xdeadbeef) for _ in range(32)])
        used, end_source, end_destination = c.c_size_t(0xaaaa), c.c_uint32(0xbbbb), c.c_uint32(0xcccc)
        before = bytes(commands)
        assert plan(0, 0, count, commands, capacity, c.byref(used), c.byref(end_source), c.byref(end_destination)) == expected
        assert bytes(commands) == before and (used.value, end_source.value, end_destination.value) == (0xaaaa, 0xbbbb, 0xcccc)
        guards.append({'function': 'device_commands', 'count': count, 'capacity': capacity, 'error': expected})
    for count, source, destination, expected in [(128, 0, 0, 1), (2, 511, 0, 2), (2, 0, 511, 2)]:
        buffer = (c.c_uint8 * len(seed)).from_buffer_copy(seed)
        assert small(buffer, len(seed), source, destination, count) == expected and bytes(buffer) == seed
        guards.append({'function': 'CPU_bytes', 'count': count, 'source': source, 'destination': destination, 'error': expected})
    report = {'time': datetime.now(timezone.utc).isoformat(), 'status': 'copy_bytes_and_device_command_plan_matched_original_CPU',
              'stage_sha256': stage.STAGE_SHA, 'original_interval': '[0xe3e0,0xe4aa)',
              'routine_bytes_hex': image[0xe3e0 - 0x4000:0xe4aa - 0x4000].hex(),
              'CPU_model': 'Unicorn ' + unicorn.__version__ + ' M68000', 'compiler_command': compiler,
              'CPU_byte_copy_cases': small_count, 'device_command_trace_cases': len(rows) - small_count,
              'host_guard_cases': len(guards), 'fixtures': rows, 'host_guards': guards,
              'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [source_dir / 'biwn_copy.c', source_dir / 'biwn_copy.h']},
              'limits': ['Ordinary mapped memory captures register writes without implementing any device behavior.',
                         'Large-path source/destination data are never copied in this test or planner.',
                         'Original device completion, resulting bytes, odd-count and alignment effects remain unverified.',
                         'Host guards reject high-bit counts whose original BMI overflow behavior is unsafe.',
                         'Observed A0/A1/D1, preserved D2-D4, stack return and RAM mutations checked; full condition-code ABI excluded.',
                         'Isolated original CPU bytes, not a rebuilt game, hardware validation or confirmed original function name.']}
    (folder / 'checks.json').write_text(json.dumps(report, indent=2) + '\n')
    (root / 'verification/biwn-copy-checks.json').write_text(json.dumps({'latest': str(folder / 'checks.json'), **report}, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'CPU_byte_copy_cases', 'device_command_trace_cases', 'host_guard_cases']}), flush=True)


if __name__ == '__main__': main()
