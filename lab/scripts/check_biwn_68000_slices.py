"""Execute two bounded original boot routines in an isolated M68000 CPU model.

The TOC is supplied test data. No Jaguar BIOS, CD subsystem, GPU processor,
MMIO device, interrupt or complete game is emulated by these checks.
"""
from collections import Counter
import datetime
import json
from pathlib import Path

import unicorn
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68000, UC_M68K_REG_PC, UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D3,
    UC_M68K_REG_D2, UC_M68K_REG_A0, UC_M68K_REG_A1,
)
import extract_biwn_stage as stage


def run_slice(boot, start, end, toc=None, copy=False, budget=4096):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(0x180000, boot)
    if toc is not None:
        cpu.mem_write(0x2c00, toc)
    if copy:
        cpu.mem_map(0xf03000, 0x1000)
        cpu.mem_write(0xf03000, b'\xa5' * 0x1000)
    trace, writes, violations = [], [], []

    def code_hook(engine, address, size, _):
        trace.append(address)
        if not start <= address < end:
            violations.append({'unexpected_execution': hex(address)})
            engine.emu_stop()

    def write_hook(engine, access, address, size, value, _):
        writes.append({'address': hex(address), 'bytes': size, 'value': hex(value)})
        if not copy or size != 4 or not 0xf03200 <= address <= 0xf039d0:
            violations.append({'unexpected_write': hex(address), 'bytes': size})
            engine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, code_hook)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    cpu.emu_start(start, end, timeout=1_000_000, count=budget)
    registers = {name: hex(cpu.reg_read(reg)) for name, reg in [
        ('PC', UC_M68K_REG_PC), ('D0', UC_M68K_REG_D0), ('D1', UC_M68K_REG_D1),
        ('D2', UC_M68K_REG_D2), ('D3', UC_M68K_REG_D3), ('A0', UC_M68K_REG_A0), ('A1', UC_M68K_REG_A1),
    ]}
    if violations:
        raise ValueError(f'CPU slice violated its execution/write bounds: {violations}')
    if cpu.reg_read(UC_M68K_REG_PC) != end:
        raise ValueError('CPU slice did not reach the stop address within its instruction/time budget')
    result = {'range': [hex(start), hex(end)], 'stop_before_executing': hex(end),
              'registers': registers, 'instruction_count': len(trace),
              'executed_addresses': {hex(k): v for k, v in Counter(trace).items()},
              'writes': writes, 'bounds_violations': violations}
    if copy:
        memory = bytes(cpu.mem_read(0xf03000, 0x1000))
        expected = boot[0x188:0x95c]
        assert memory[0x200:0x9d4] == expected
        assert memory[:0x200] == b'\xa5' * 0x200
        assert memory[0x9d4:] == b'\xa5' * (0x1000 - 0x9d4)
        assert len(writes) == 501
        assert [int(w['address'], 16) for w in writes] == list(range(0xf03200, 0xf039d4, 4))
        assert registers['A0'] == '0x18095c' and registers['A1'] == '0xf039d4'
        result['destination_sha256'] = stage.digest(memory[0x200:0x9d4])
        result['source_sha256'] = stage.digest(expected)
        result['neighboring_guard_bytes_unchanged'] = True
    return result


def make_toc(layout):
    toc = bytearray(0x400)
    toc[2:4] = bytes([1, max(t['track'] for t in layout['tracks'])])
    for track in layout['tracks']:
        number = track['track']
        start = track['declared_start_lba'] + track['pregap_sectors'] + 150
        toc[number * 8:number * 8 + 8] = bytes([
            number, *stage.msf(start), track['session'] - 1, *stage.msf(track['program_sectors'])])
    return toc


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    boot = (session / 'boot-payload-68000-candidate.bin').read_bytes()
    if stage.digest(boot) != stage.BOOT_SHA or boot[0xc8:0x146] != stage.TOC_BLOCK:
        raise ValueError('Original boot bytes no longer match audited input')
    layout = json.loads((session / 'cdi-layout.json').read_text())
    _, facts = stage.derive((session / 'raw-tracks/track-02-raw.bin').read_bytes())
    conditional = stage.conditional_toc_trace(layout, facts)
    toc = make_toc(layout)
    actual = run_slice(boot, 0x1800c8, 0x18015a, bytes(toc))
    expected_seek = int(conditional['packed_seek_hex'], 16)
    assert int(actual['registers']['D0'], 16) == expected_seek
    for register, expected in [('D1', 0x53545542), ('D2', 0), ('A0', 0x4000), ('A1', 0x100000)]:
        assert int(actual['registers'][register], 16) == expected

    cases = {'cdi_derived_toc_under_reference_conventions': actual}
    # Independent linear frame subtraction checks against actual instruction execution.
    for name, frames in [('frame_borrow', 12750), ('second_and_minute_borrow', 4502),
                         ('exact_six', 6), ('minute_99', 99 * 4500 + 4)]:
        fixture = bytearray(toc)
        fixture[2 * 8 + 1:2 * 8 + 4] = bytes(stage.msf(frames))
        result = run_slice(boot, 0x1800c8, 0x18015a, bytes(fixture))
        m, s, f = stage.msf(frames - 6)
        expected = (m << 16) | (s << 8) | f
        assert int(result['registers']['D0'], 16) == expected
        result['synthetic_toc_track2_msf'] = stage.msf(frames)
        result['expected_seek_msf'] = [m, s, f]
        cases[name] = result
    # No matching entry: a finite budget must stop the unbounded second scanner.
    invalid = bytearray(toc)
    for number in range(1, 6):
        invalid[number * 8 + 4] = 0
    try:
        run_slice(boot, 0x1800c8, 0x18015a, bytes(invalid), budget=128)
    except ValueError as exc:
        assert 'instruction/time budget' in str(exc)
        cases['missing_session2'] = {'status': 'bounded stop; CD_read was not reached', 'instruction_limit': 128}
    else:
        raise AssertionError('Missing session should not reach the CD_read boundary')
    copy = run_slice(boot, 0x18007e, 0x180094, copy=True)
    report = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'selected_original_cpu_routines_passed_in_isolation',
        'emulator': {'package': 'unicorn', 'version': unicorn.__version__, 'cpu_model': 'UC_CPU_M68K_M68000',
                     'source': 'https://www.unicorn-engine.org/docs/'},
        'input_sha256': stage.BOOT_SHA,
        'implementation_sha256': stage.cdi_layout.sha(Path(__file__)),
        'toc_cases': cases, 'gpu_ram_copy_cpu_routine': copy,
        'limits': [
            'TOC bytes are supplied fixtures, not read from a Jaguar BIOS or physical CD.',
            'The track-selection slice stops before JSR CD_read at 0x18015a.',
            'The copy slice writes a memory buffer representing GPU RAM; the GPU is not executed.',
            'No BIOS, interrupt, MMIO device, streamed stage or full game was executed.',
            'This establishes these instructions under this CPU model and fixtures, not whole-game correctness.',
        ],
    }
    target = root / 'verification/biwn-68000-slice-checks.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(target)


if __name__ == '__main__':
    main()
