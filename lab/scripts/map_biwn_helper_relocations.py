"""Static evaluation of the captured GPU helper's two relocation-table loops.

No GPU instruction execution is performed. The transform follows the decoded
loop arithmetic and independently checks each MOVEI's semantic immediate.
"""
import datetime
import json
from pathlib import Path
import sys
import extract_biwn_stage as stage
sys.path.insert(0, str(stage.ROOT))
import binary_tools

HELPER_SHA = '2a6ad91e2d3262d495a3349f72701862670e778633df9e61c65e397ace64106d'
COMPILED_BASE = 0xf03000
LOAD_BASE = 0xf03258
DELTA = LOAD_BASE - COMPILED_BASE


def u32(data, offset):
    return int.from_bytes(data[offset:offset + 4], 'big')


def movei_value(data, offset):
    opcode = int.from_bytes(data[offset:offset + 2], 'big')
    if opcode >> 10 != 38 or offset < 0 or offset + 6 > len(data):
        raise ValueError('Table target is not a complete captured MOVEI')
    return int.from_bytes(data[offset + 2:offset + 4], 'big') | (int.from_bytes(data[offset + 4:offset + 6], 'big') << 16)


def relocate(data):
    if stage.digest(data) != HELPER_SHA:
        raise ValueError('GPU helper differs from captured initial bytes')
    result = bytearray(data)
    immediate, pointers = [], []
    count = u32(data, 0x804)
    if count != 33 or 0x808 + count * 4 != 0x88c:
        raise ValueError('Unexpected first table extent')
    for index in range(count):
        address = u32(data, 0x808 + index * 4)
        offset = address - COMPILED_BASE
        old_immediate = movei_value(data, offset)
        # The loop tests target bit1, aligns a longword access, and uses either
        # delta or ROR(delta,16). MOVEI extension words store low-half first.
        write_offset = offset + (2 if address & 2 else 0)
        increment = ((DELTA >> 16) | ((DELTA << 16) & 0xffffffff)) if address & 2 else DELTA
        if write_offset < 0 or write_offset + 4 > len(result) or (LOAD_BASE + write_offset) % 4:
            raise ValueError('First relocation write exceeds its aligned candidate range')
        old_word = u32(result, write_offset)
        new_word = (old_word + increment) & 0xffffffff
        result[write_offset:write_offset + 4] = new_word.to_bytes(4, 'big')
        actual_immediate = movei_value(result, offset)
        expected_immediate = (old_immediate + DELTA) & 0xffffffff
        if actual_immediate != expected_immediate:
            raise ValueError('Literal loop transform disagrees with independent MOVEI immediate addition')
        if result[offset:offset + 2] != data[offset:offset + 2]:
            raise ValueError('Relocation changed an opcode rather than only its immediate')
        immediate.append({'table_index': index, 'compiled_target': hex(address),
                          'loaded_target': hex(address + DELTA),
                          'aligned_write': hex(LOAD_BASE + write_offset),
                          'increment': hex(increment), 'old_immediate': hex(old_immediate),
                          'new_immediate': hex(actual_immediate)})
    count = u32(data, 0x88c)
    if count != 8 or 0x890 + count * 4 != len(data):
        raise ValueError('Unexpected second table extent')
    for index in range(count):
        address = u32(data, 0x890 + index * 4)
        offset = address - COMPILED_BASE
        if offset < 0 or offset + 4 > len(result) or (LOAD_BASE + offset) % 4:
            raise ValueError('Second relocation write exceeds its aligned candidate range')
        old = u32(result, offset)
        new = (old + DELTA) & 0xffffffff
        result[offset:offset + 4] = new.to_bytes(4, 'big')
        pointers.append({'table_index': index, 'compiled_target': hex(address),
                         'loaded_target': hex(address + DELTA), 'old_word': hex(old), 'new_word': hex(new)})
    # CPU D340 later waits on F03794+0x258. The transformed GPU MOVEI must agree.
    assert movei_value(result, 0x66) == 0xf039ec
    rows, _ = binary_tools.jaguar_instructions(bytes(result[0x66:0x6c]), 0xf032be, 'gpu')
    return bytes(result), {
        'delta': hex(DELTA), 'compiled_base': hex(COMPILED_BASE), 'load_base': hex(LOAD_BASE),
        'movei_relocations': immediate, 'longword_relocations': pointers,
        'both_first_loop_alignment_paths': {'bit1_clear': sum((int(x['compiled_target'], 16) & 2) == 0 for x in immediate),
                                           'bit1_set': sum((int(x['compiled_target'], 16) & 2) != 0 for x in immediate)},
        'GPU_completion_flag_instruction_after_static_transform': rows,
        'GPU_flag_operand_matches_CPU_wait_address': True,
        'all_writes_inside_captured_helper': True,
        'all_movei_opcodes_preserved': True,
        'all_movei_immediates_match_independent_addition': True,
    }


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    source = session / 'processor-programs/nextstage-helper-gpu.bin'
    data = source.read_bytes()
    transformed, facts = relocate(data)
    output = source.with_name('nextstage-helper-gpu-static-relocated.bin')
    if output.exists():
        if output.read_bytes() != transformed:
            raise ValueError('Existing transformed snapshot differs; refusing overwrite')
    else:
        stage.publish(output, transformed)
    report = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'static_relocation_transform_checked_GPU_execution_unverified',
        'source': str(source), 'source_sha256': stage.digest(data),
        'output': str(output), 'output_sha256': stage.digest(transformed),
        'facts': facts,
        'implementation_sha256': stage.cdi_layout.sha(Path(__file__)),
        'limits': [
            'A static evaluation of decoded loops, not an executed GPU or hardware trace.',
            'MOVE PC/current-instruction-PC behavior comes from the pinned MAME reference.',
            'Preceding BIOS calls, initial processor state, code/data classification, delay slots and later commands are not validated.',
            'The transformed file is a derived hypothesis; original candidate bytes remain unchanged.',
        ],
    }
    path = session / 'helper-gpu-relocations.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
