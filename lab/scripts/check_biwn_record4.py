"""Compare bounded record translation against actual candidate M68000 bytes."""
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import (UC_CPU_M68K_M68000, UC_M68K_REG_A7,
                               UC_M68K_REG_D0, UC_M68K_REG_PC)
import unicorn
import extract_biwn_stage as stage

BASE, COUNT, SP, STOP = 0x1126c0, 0x112940, 0x1ff000, 0x1ffe00
ROUTINE_HEX = '0c790027001129406e3230390011294048c0e98041f9001126c021af0008080421af0004080021af000c080821af0010080c52790011294070014e7542404e75'


def original(image, count, args, incoming):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(0x4000, image)
    cpu.mem_write(BASE - 16, bytes([0xa5]) * 688)
    cpu.mem_write(COUNT, count.to_bytes(2, 'big'))
    cpu.mem_write(SP, b''.join(x.to_bytes(4, 'big') for x in [STOP, *args]))
    cpu.reg_write(UC_M68K_REG_A7, SP)
    cpu.reg_write(UC_M68K_REG_D0, incoming)
    before = bytes(cpu.mem_read(0, 0x200000))
    trace, writes = [], []

    def code(engine, address, size, _):
        if not 0xeac4 <= address < 0xeb04:
            raise AssertionError(('unexpected execution', hex(address)))
        trace.append(address)

    def write(engine, access, address, size, value, _):
        writes.append({'address': hex(address), 'bytes': size, 'value': value})

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(0xeac4, STOP, count=32, timeout=1_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC) == STOP
    assert cpu.reg_read(UC_M68K_REG_A7) == SP + 4
    signed_count = count if count < 0x8000 else count - 0x10000
    expected = bytearray(before)
    if signed_count <= 39:
        offset = BASE + signed_count * 16
        expected[offset:offset + 16] = b''.join(x.to_bytes(4, 'big') for x in args)
        expected[COUNT:COUNT + 2] = ((count + 1) & 0xffff).to_bytes(2, 'big')
        assert [int(w['address'], 16) for w in writes] == [offset + 4, offset, offset + 8, offset + 12, COUNT]
    else:
        assert not writes
    assert bytes(cpu.mem_read(0, 0x200000)) == bytes(expected), 'unexpected memory mutation'
    return {'D0': cpu.reg_read(UC_M68K_REG_D0),
            'count': int.from_bytes(cpu.mem_read(COUNT, 2), 'big'),
            'records': bytes(cpu.mem_read(BASE, 640)), 'writes': writes,
            'instructions': len(trace)}


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    assert stage.digest(image) == stage.STAGE_SHA
    assert image[0xeac4 - 0x4000:0xeb04 - 0x4000].hex() == ROUTINE_HEX
    source = root / 'projects/black-ice-white-noise/restoration'
    folder = root / 'verification/biwn-record4' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    folder.mkdir(parents=True)
    library = folder / 'libbiwn_record4.dylib'
    command = ['clang', '-dynamiclib', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O2',
               str(source / 'biwn_record4.c'), '-o', str(library)]
    subprocess.run(command, check=True, capture_output=True,
                   env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    lib = ctypes.CDLL(str(library))
    fn = lib.biwn_record4_append
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
                   ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint32),
                   ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    fn.restype = ctypes.c_int
    rng = random.Random(0xeac4)
    fixtures = [(count, [rng.getrandbits(32) for _ in range(4)], rng.getrandbits(32))
                for count in list(range(40)) * 4 + [40, 41, 127, 32767] * 8]
    passed = []
    for count, args, incoming in fixtures:
        cpu = original(image, count, args, incoming)
        buffer = (ctypes.c_uint8 * 672)(*([0xa5] * 672))
        ptr = ctypes.cast(ctypes.byref(buffer, 16), ctypes.POINTER(ctypes.c_uint8))
        count_word, result = ctypes.c_uint16(count), ctypes.c_uint32(0xdeadbeef)
        assert fn(ptr, 640, ctypes.byref(count_word), (ctypes.c_uint32 * 4)(*args), incoming, ctypes.byref(result)) == 0
        assert bytes(buffer)[16:656] == cpu['records']
        assert bytes(buffer)[:16] == bytes(buffer)[656:] == bytes([0xa5]) * 16
        assert count_word.value == cpu['count']
        assert result.value == cpu['D0']
        passed.append({'count_before': count, 'args': args, 'D0_before': incoming,
                       'D0_after': result.value, 'count_after': count_word.value,
                       'original_writes': cpu['writes'], 'instructions': cpu['instructions']})
    guards = []
    for count, size, expected_error in [(0x8000, 640, 1), (0xffff, 640, 1), (39, 639, 2), (0, 15, 2)]:
        buffer = (ctypes.c_uint8 * 640)(*([0xa5] * 640))
        count_word, result = ctypes.c_uint16(count), ctypes.c_uint32(0xdeadbeef)
        args = (ctypes.c_uint32 * 4)(1, 2, 3, 4)
        assert fn(buffer, size, ctypes.byref(count_word), args, 0x12345678, ctypes.byref(result)) == expected_error
        assert bytes(buffer) == bytes([0xa5]) * 640
        assert count_word.value == count and result.value == 0xdeadbeef
        entry = {'count': count, 'size': size, 'host_error': expected_error, 'host_unchanged': True}
        if count >= 0x8000:
            cpu = original(image, count, list(args), 0x12345678)
            entry['original_first_write'] = cpu['writes'][0]['address']
            entry['original_D0'] = cpu['D0']
        guards.append(entry)
    report = {'time': datetime.now(timezone.utc).isoformat(),
              'status': 'portable_record_component_matched_original_CPU_fixtures',
              'original_candidate_sha256': stage.STAGE_SHA,
              'original_interval': '[0xeac4,0xeb04)', 'routine_bytes_hex': ROUTINE_HEX,
              'CPU_model': 'Unicorn ' + unicorn.__version__ + ' M68000',
              'compiler_command': command, 'cases': len(passed), 'fixtures': passed,
              'host_guards': guards, 'whole_2MiB_original_memory_mutation_checked': True,
              'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [source / 'biwn_record4.c', source / 'biwn_record4.h']},
              'limits': ['Analyst-assigned name; original purpose and symbols unknown.',
                         'Host translation rejects negative count and short buffers; original has no bounds checks.',
                         'D0 result, count, stack return and final writes checked; condition codes/A0 not modeled.',
                         'Ordinary non-overlapping host memory only; original intermediate store order not modeled.',
                         'Isolated original CPU bytes, not a rebuilt full game or hardware validation.']}
    (folder / 'checks.json').write_text(json.dumps(report, indent=2) + '\n')
    (root / 'verification/biwn-record4-checks.json').write_text(json.dumps({'latest': str(folder / 'checks.json'), **report}, indent=2) + '\n')
    print(json.dumps({'report': str(folder / 'checks.json'), 'cases': len(passed), 'host_guards': len(guards)}))


if __name__ == '__main__':
    main()
