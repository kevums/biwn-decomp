"""Differential checks: next-stage original 68000 arithmetic versus portable C."""
from collections import Counter
import ctypes
import datetime
import json
from pathlib import Path
import random
import subprocess

from unicorn import (Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE,
                     UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE)
from unicorn.m68k_const import (
    UC_CPU_M68K_M68000, UC_M68K_REG_PC, UC_M68K_REG_D0, UC_M68K_REG_D1,
    UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_A0, UC_M68K_REG_A7,
)
import unicorn
import extract_biwn_stage as stage
from check_biwn_68000_slices import make_toc


class Position(ctypes.Structure):
    _fields_ = [('packed_binary_msf', ctypes.c_uint32), ('toc_entry_offset', ctypes.c_uint32)]


def original(data, entry, toc=b'', selector=0, byte_offset=0, numerator=0, divisor=1):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(0x4000, data)
    cpu.mem_write(0x2c00, toc)
    cpu.reg_write(UC_M68K_REG_A7, 0x1ff000)
    cpu.mem_write(0x1ff000, b''.join(x.to_bytes(4, 'big') for x in [0x1ffe00, selector, byte_offset]))
    cpu.reg_write(UC_M68K_REG_D0, 0xa5a50000 | divisor)
    cpu.reg_write(UC_M68K_REG_D1, numerator)
    cpu.reg_write(UC_M68K_REG_D2, 0x12345678)
    cpu.reg_write(UC_M68K_REG_D3, 0x9abcdef0)
    trace, violations = [], []

    def code(engine, address, size, _):
        trace.append(address)
        if not 0xd1e0 <= address < 0xd2a0:
            violations.append({'execution': hex(address)})
            engine.emu_stop()

    def read(engine, access, address, size, value, _):
        if not (0x1fef00 <= address and address + size <= 0x1ff010) and not (
                0x2c00 <= address and address + size <= 0x2c00 + len(toc)):
            violations.append({'data_read': hex(address), 'bytes': size})
            engine.emu_stop()

    def write(engine, access, address, size, value, _):
        if not 0x1fef00 <= address or address + size > 0x1ff000:
            violations.append({'write': hex(address), 'bytes': size})
            engine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_READ, read)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(entry, 0x1ffe00, timeout=1_000_000, count=4096)
    if violations:
        raise ValueError(f'Isolated original CPU run exceeded its supplied data/code bounds: {violations}')
    assert cpu.reg_read(UC_M68K_REG_PC) == 0x1ffe00
    assert cpu.reg_read(UC_M68K_REG_A7) == 0x1ff004
    assert cpu.reg_read(UC_M68K_REG_D2) == 0x12345678
    assert cpu.reg_read(UC_M68K_REG_D3) == 0x9abcdef0
    return {
        'D0': cpu.reg_read(UC_M68K_REG_D0), 'D1': cpu.reg_read(UC_M68K_REG_D1),
        'A0': cpu.reg_read(UC_M68K_REG_A0), 'instructions': len(trace),
        'path_counts': {hex(k): v for k, v in Counter(trace).items()},
        'D2_D3_preserved': True, 'stack_restored_after_RTS': True,
        'bounds_violations': violations,
    }


def as_buffer(data):
    return (ctypes.c_uint8 * len(data)).from_buffer_copy(data)


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    data = (session / 'nextstage-68000-candidate.bin').read_bytes()
    if stage.digest(data) != stage.STAGE_SHA:
        raise ValueError('Candidate bytes differ from the captured next-stage image')
    source = root / 'projects/black-ice-white-noise/restoration'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    folder = root / 'verification/biwn-cd-math' / stamp
    folder.mkdir(parents=True)
    library = folder / 'libbiwn_cd_math.dylib'
    command = ['clang', '-dynamiclib', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O2',
               str(source / 'biwn_cd_math.c'), '-o', str(library)]
    subprocess.run(command, capture_output=True, check=True, text=True)
    lib = ctypes.CDLL(str(library))
    lib.biwn_divide_u32_u16.argtypes = [ctypes.c_uint32, ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint32)]
    lib.biwn_divide_u32_u16.restype = ctypes.c_int
    lib.biwn_cd_offset_msf.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                                     ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
                                     ctypes.POINTER(Position)]
    lib.biwn_cd_offset_msf.restype = ctypes.c_int
    generator = random.Random(20261012)
    division_cases = [(n, d) for d in [1, 2, 3, 75, 2352, 65535]
                      for n in sorted({0, 1, 65535, 65536, 0xffffffff,
                                       min(0xffffffff, d * 65535), min(0xffffffff, d * 65536)})]
    division_cases += [(generator.getrandbits(32), generator.randrange(1, 65536)) for _ in range(256)]
    division = []
    for numerator, divisor in division_cases:
        cpu = original(data, 0xd1e0, numerator=numerator, divisor=divisor)
        result = ctypes.c_uint32(0xa5a5a5a5)
        assert lib.biwn_divide_u32_u16(numerator, divisor, ctypes.byref(result)) == 0
        assert result.value == cpu['D1'] == numerator // divisor
        assert cpu['D0'] == 0xa5a50000 | divisor
        division.append({'numerator': numerator, 'divisor': divisor, 'quotient': result.value,
                         'overflow_fallback_executed': '0xd1ec' in cpu['path_counts']})

    layout = json.loads((session / 'cdi-layout.json').read_text())
    toc = bytes(make_toc(layout))
    positions = []
    offsets = [0, 1, 2351, 2352, 2353, 74 * 2352, 75 * 2352,
               4500 * 2352, 641054064, 0xffffffff]
    fixtures = []
    for selector in range(5):
        for offset in offsets:
            fixtures.append((f'captured-layout-selector{selector}-offset{offset}', selector, offset, toc))
    for frames in [6, 75, 4500, 4502, 12779, 99 * 4500 + 4]:
        modified = bytearray(toc)
        modified[17:20] = bytes(stage.msf(frames))
        for offset in offsets:
            fixtures.append((f'borrow-frames{frames}-offset{offset}', 1, offset, bytes(modified)))
    # Byte widths and BMI conditions are retained even for noncanonical TOC bytes.
    for _ in range(64):
        modified = bytearray(toc)
        modified[17:20] = bytes(generator.randrange(256) for _ in range(3))
        fixtures.append(('noncanonical-supplied-time', 1, generator.getrandbits(32), bytes(modified)))
    for name, selector, offset, fixture in fixtures:
        cpu = original(data, 0xd206, toc=fixture, selector=selector, byte_offset=offset)
        result = Position()
        assert lib.biwn_cd_offset_msf(selector, offset, as_buffer(fixture), len(fixture), ctypes.byref(result)) == 0
        assert result.packed_binary_msf == cpu['D0'], (name, hex(result.packed_binary_msf), hex(cpu['D0']))
        # Original A0 advanced four bytes after reading the selected entry's MSF.
        assert result.toc_entry_offset == cpu['A0'] - 0x2c00 - 4
        positions.append({'fixture': name, 'selector': selector, 'byte_offset': offset,
                          'toc_sha256': stage.digest(fixture), 'packed_binary_msf': hex(result.packed_binary_msf),
                          'selected_toc_entry_offset': result.toc_entry_offset,
                          'original_instructions': cpu['instructions']})
    guards = {}
    result = ctypes.c_uint32(0xa5a5a5a5)
    assert lib.biwn_divide_u32_u16(123, 0, ctypes.byref(result)) == 1
    assert result.value == 0xa5a5a5a5
    guards['divide_by_zero'] = 'host error without output mutation; original trap behavior not tested'
    position = Position(0xa5a5a5a5, 0xa5a5a5a5)
    assert lib.biwn_cd_offset_msf(1, 0, as_buffer(toc), 16, ctypes.byref(position)) == 3
    assert position.packed_binary_msf == position.toc_entry_offset == 0xa5a5a5a5
    guards['short_toc'] = 'bounded host error; output unchanged'
    report = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'two_nextstage_arithmetic_components_compiled_and_matched_original_CPU_fixtures',
        'original_candidate_sha256': stage.STAGE_SHA,
        'original_addresses': {'division': '0xd1e0..0xd206', 'cd_offset': '0xd206..0xd2a0'},
        'CPU_model': 'Unicorn ' + unicorn.__version__ + ' M68000',
        'compiler_command': command,
        'source_sha256': {p.name: stage.cdi_layout.sha(p) for p in [source / 'biwn_cd_math.c', source / 'biwn_cd_math.h']},
        'division_cases': division, 'cd_position_cases': positions, 'host_input_guards': guards,
        'both_division_paths_exercised': {str(flag): sum(x['overflow_fallback_executed'] == flag for x in division) for flag in [False, True]},
        'limits': [
            'Analyst-written source and names; no original source, compiler ABI or symbol recovery claimed.',
            'Selected CPU routines execute against supplied TOC bytes and a host memory buffer only.',
            'Function return registers and preserved D2/D3/stack were checked; full condition-code ABI not reconstructed.',
            'Input bounds/zero-divisor errors are deliberate host behavior, not original hardware trap/scanner equivalence.',
            'No BIOS/CD/GPU/DSP or whole-game execution and no working full reconstruction established.',
        ],
    }
    path = folder / 'checks.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    (root / 'verification/biwn-cd-math-checks.json').write_text(json.dumps({'latest': str(path), **report}, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
