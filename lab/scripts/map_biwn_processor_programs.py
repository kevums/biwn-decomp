"""Capture three next-stage GPU/DSP copy candidates with bounded original CPU runs.

These are initial-file-byte candidates: preceding BIOS/device calls are omitted
and may have changed RAM in a real run. GPU/DSP processors are not executed.
"""
from collections import Counter
import datetime
import json
from pathlib import Path
import sys

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000, UC_M68K_REG_PC, UC_M68K_REG_A0, UC_M68K_REG_A1
import extract_biwn_stage as stage

sys.path.insert(0, str(stage.ROOT))
import binary_tools


def decode_prefix(data, address, variant):
    # A fixed byte window can end inside MOVEI. Shorten by whole words rather
    # than inventing extension bytes; the omitted tail remains unclassified.
    for length in range(min(96, len(data)), max(0, min(96, len(data)) - 6), -2):
        try:
            return binary_tools.jaguar_instructions(data[:length], address, variant)
        except ValueError as exc:
            if 'truncated instruction' not in str(exc):
                raise
    raise ValueError('Could not select a complete instruction prefix')


def capture(data, spec):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(0x4000, data)
    cpu.mem_map(spec['memory_base'], spec['memory_bytes'])
    cpu.mem_write(spec['memory_base'], b'\xa5' * spec['memory_bytes'])
    addresses, writes, violations = [], [], []

    def code(engine, address, size, _):
        addresses.append(address)
        if not spec['cpu_begin'] <= address < spec['cpu_stop']:
            violations.append({'unexpected_execution': hex(address)})
            engine.emu_stop()

    def write(engine, access, address, size, value, _):
        writes.append(address)
        if size != 4 or not spec['destination'] <= address <= spec['destination'] + spec['bytes'] - 4:
            violations.append({'unexpected_write': hex(address), 'bytes': size})
            engine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(spec['cpu_begin'], spec['cpu_stop'], timeout=1_000_000, count=10000)
    if violations:
        raise ValueError(f'Copy exceeded proposed mapping: {violations}')
    assert cpu.reg_read(UC_M68K_REG_PC) == spec['cpu_stop']
    assert writes == list(range(spec['destination'], spec['destination'] + spec['bytes'], 4))
    block = bytes(cpu.mem_read(spec['destination'], spec['bytes']))
    expected = data[spec['source'] - 0x4000:spec['source'] - 0x4000 + spec['bytes']]
    assert block == expected
    whole = bytes(cpu.mem_read(spec['memory_base'], spec['memory_bytes']))
    offset = spec['destination'] - spec['memory_base']
    assert whole[:offset] == b'\xa5' * offset
    assert whole[offset + spec['bytes']:] == b'\xa5' * (spec['memory_bytes'] - offset - spec['bytes'])
    observed = {'instruction_count': len(addresses),
                'instruction_address_counts': {hex(a): count for a, count in Counter(addresses).items()},
                'longword_writes': len(writes), 'neighboring_guard_bytes_unchanged': True,
                'stop_before_executing': hex(spec['cpu_stop']),
                'A0_after_copy': hex(cpu.reg_read(UC_M68K_REG_A0)),
                'A1_after_copy': hex(cpu.reg_read(UC_M68K_REG_A1))}
    return block, observed


def main():
    root = stage.ROOT
    folder = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    data = (folder / 'nextstage-68000-candidate.bin').read_bytes()
    if stage.digest(data) != stage.STAGE_SHA:
        raise ValueError('Next-stage candidate differs from captured bytes')
    specs = [
        {'name': 'nextstage-helper-gpu', 'variant': 'gpu', 'source': 0x21ec0,
         'destination': 0xf03258, 'bytes': 0x8b0, 'cpu_begin': 0xd340, 'cpu_stop': 0xd356,
         'memory_base': 0xf03000, 'memory_bytes': 0x1000, 'entry': 0xf03258,
         'copy_basis': 'MOVE.L loop compares source A1 with0x22770; stops before subsequent startup/control logic.'},
        {'name': 'nextstage-main-gpu', 'variant': 'gpu', 'source': 0x40a8,
         'destination': 0xf03000, 'bytes': 636, 'cpu_begin': 0xe00a, 'cpu_stop': 0xe01a,
         'memory_base': 0xf03000, 'memory_bytes': 0x1000, 'entry': 0xf03224,
         'copy_basis': 'Header at0x40a0 supplies destination and DBF count158;159longword writes. Stops before BIOS CD_init.'},
        {'name': 'nextstage-dsp', 'variant': 'dsp', 'source': 0x7248,
         'destination': 0xf1b000, 'bytes': 0x1210, 'cpu_begin': 0xe96c, 'cpu_stop': 0xe980,
         'memory_base': 0xf1b000, 'memory_bytes': 0x2000, 'entry': 0xf1b126,
         'copy_basis': 'Header at0x7240 supplies destination and byte length4624; ASR2/SUBQ1/DBF gives1156longword writes. Stops before subsequent DSP writes/start.'},
    ]
    target = folder / 'processor-programs'
    target.mkdir(exist_ok=True)
    programs = []
    for spec in specs:
        block, cpu = capture(data, spec)
        path = target / (spec['name'] + '.bin')
        if path.exists():
            if path.read_bytes() != block:
                raise ValueError('Existing processor candidate differs; refusing overwrite')
        else:
            stage.publish(path, block)
        prefix, decoder = decode_prefix(block, spec['destination'], spec['variant'])
        offset = spec['entry'] - spec['destination']
        # Decode full instructions without allowing a final truncated MOVEI.
        entry_bytes = block[offset:offset + 96]
        entry_rows, _ = decode_prefix(entry_bytes, spec['entry'], spec['variant'])
        programs.append({
            'name': spec['name'], 'processor': spec['variant'],
            'source_CPU_interval': [hex(spec['source']), hex(spec['source'] + spec['bytes'])],
            'destination_interval': [hex(spec['destination']), hex(spec['destination'] + spec['bytes'])],
            'startup_PC_from_following_listing': hex(spec['entry']),
            'bytes': len(block), 'sha256': stage.digest(block), 'path': str(path),
            'basis': spec['copy_basis'], 'original_CPU_copy_check': cpu,
            'linear_prefix_decode': prefix, 'entry_prefix_decode': entry_rows,
            'decoder': decoder['name'], 'code_data_boundaries_verified': False,
        })
    report = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'three_processor_initial_file_byte_candidates_captured',
        'original_candidate_sha256': stage.STAGE_SHA,
        'programs': programs,
        'helper_table_mapping_candidate': {
            'helper_GPU_first_instruction_PC': '0xf03258',
            'static_PC_minus_0xf03000': '0x258',
            'first_table_load_if_that_delta_applies': '0xf03a5c',
            'captured_helper_copy_end': '0xf03b08',
            'finding': 'The first computed table address lies inside this2224-byte copy. Table counts, target bounds and possible self-modification need separate checking before any GPU runtime conclusion.',
            'basis': 'Static prefix and pinned MAME MOVE PC uses current instruction PC; no GPU execution observed.',
        },
        'limits': [
            'The three copy loops ran only in a Unicorn M68000 CPU model with memory-backed destinations.',
            'Preceding BIOS/device calls were omitted; real source RAM and destination RAM may differ from initial candidate bytes.',
            'GPU/DSP instruction decoding is linear and can include data. Entry values are startup writes in subsequent listing, not observed processor execution.',
            'No BIOS, CD, GPU/DSP or whole game execution and no complete restoration established.',
        ],
    }
    path = folder / 'processor-programs.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
