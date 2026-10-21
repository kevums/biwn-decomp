"""Read-only entrance inventory from actual normalized outdoor CD payloads.

This is data reconnaissance, not proof of reachability or a transition test.
Source 20F78 selects nine-segment files; source 10430 reads 28-byte gates.
"""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from biwn_disc_backend import Disc, ROOT


def inspect():
    disc = Disc()
    data = disc.data
    payloads, gates, invalid = [], [], []
    seen = set()
    u16 = lambda b, n: int.from_bytes(b[n:n + 2], 'big')
    for high in range(0x20, 0x23):
        prefix = bytes([0, 0, high])
        cursor = 0
        while True:
            marker = data.find(prefix, cursor)
            if marker < 0:
                break
            cursor = marker + 3
            word = data[marker:marker + 4]
            if len(word) != 4 or data[marker:marker + 64] != word * 16:
                continue
            tag = int.from_bytes(word, 'big')
            payload = data[marker + 64:marker + 64 + 4704]
            offsets = [u16(payload, i * 2) for i in range(10)]
            if offsets[0] != 20 or offsets != sorted(offsets) or not all(20 <= x <= 4704 for x in offsets):
                invalid.append({'tag': hex(tag), 'marker': marker, 'reason': 'segment_offsets'})
                continue
            payloads.append({'tag': hex(tag), 'marker': marker, 'offsets': offsets,
                             'sha256': hashlib.sha256(payload).hexdigest()})
            for segment in range(9):
                raw = payload[offsets[segment]:offsets[segment + 1]]
                if len(raw) < 16:
                    invalid.append({'tag': hex(tag), 'segment': segment, 'reason': 'short_header'})
                    continue
                count, pos = u16(raw, 2), u16(raw, 10)
                if pos + count * 28 > len(raw):
                    invalid.append({'tag': hex(tag), 'segment': segment, 'reason': 'gate_bounds',
                                    'count': count, 'offset': pos, 'segment_bytes': len(raw)})
                    continue
                for index in range(count):
                    cell = ((tag - 0x2000) // 13, ((tag - 0x2000) % 13) * 5 + segment, index)
                    if cell in seen:
                        continue
                    seen.add(cell)
                    record = raw[pos + index * 28:pos + (index + 1) * 28]
                    gates.append({'cell': cell, 'tag': hex(tag), 'segment': segment,
                                  'record_offset': marker + 64 + offsets[segment] + pos + index * 28,
                                  'target': u16(record, 26), 'record_hex': record.hex()})
    active = [row for row in gates if row['target'] != 0xffff]
    enabled = []
    for row in active:
        record = bytes.fromhex(row['record_hex'])
        directions = [i for i, offset in enumerate([11, 13, 15, 17]) if record[offset] < 16]
        if directions:
            enabled.append({**row, 'directions': directions})
    targets = sorted(set(row['target'] for row in active))
    # Independently anchor the raw record interpretation to the captured 25-tile
    # startup world. Texture words at +2/+4/+6 are deliberately not compared:
    # source 20C16 resolves them to runtime cache handles.
    ram = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    u32 = lambda b, n: int.from_bytes(b[n:n + 4], 'big')
    x, z = u32(ram, 0x49c50), u32(ram, 0x49c56)
    sx = (x - 1) // 1024 - 2
    sz = (0xbc01 - z) // 1024 + 2
    tag0 = 0x2000 + sz * 13 + sx // 5
    witness = []
    lookup = {int(row['tag'], 16): row for row in payloads}
    for slot in range(25):
        tag = tag0 - (slot // 5) * 13
        meta = lookup[tag]
        segment = sx % 5 + slot % 5
        start = meta['marker'] + 64 + meta['offsets'][segment]
        end = meta['marker'] + 64 + meta['offsets'][segment + 1]
        raw = data[start:end]
        tile_pointer = u32(ram, 0x49bb4 + slot * 4)
        tile = tile_pointer & 0x1fffff
        count, pointer = u16(ram, tile + 2), u32(ram, tile + 12) & 0x1fffff
        assert count == u16(raw, 2), ('count', slot)
        record_offset = u16(raw, 10)
        for index in range(count):
            left = raw[record_offset + index * 28:record_offset + (index + 1) * 28]
            right = ram[pointer + index * 28:pointer + (index + 1) * 28]
            assert len(left) == len(right) == 28 and left[8:] == right[8:], ('record', slot, index)
        witness.append({'slot': slot, 'tag': hex(tag), 'segment': segment,
                        'tile_pointer': hex(tile_pointer),
                        'gate_count': count, 'non_texture_gate_bytes_match': True})
    return {'recorded_at': datetime.now(timezone.utc).isoformat(),
            'status': 'read_only_disc_gate_inventory', 'payloads': payloads, 'gates': gates,
            'non_FFFF_gates': active, 'invalid_segments': invalid,
            'directionally_enabled_gates': enabled,
            'startup_25_tile_record_witness': witness,
            'startup_RAM_sha256': hashlib.sha256(ram).hexdigest(),
            'target_distribution': dict(Counter(str(row['target']) for row in gates)),
            'target_marker_offsets': {str(target): data.find((0x6000 + target).to_bytes(4, 'big') * 16)
                                      for target in targets},
            'normalized_track_sha256': disc.manifest['normalized_track_sha256'],
            'source_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'limits': ['Gate records are inferred using source parser offsets; no source transition executed.',
                       'Directionally enabled means the source byte check can match a 0..15 position nibble; it does not prove a reachable doorway.',
                       '329 short/empty segment spans are retained as unresolved parser inputs; no full outdoor loader coverage claim.',
                       'Repeated overlapping cells are deduplicated by row/column/gate index.',
                       'No RAM, source code, disc image, models or native Chat state changed.']}


if __name__ == '__main__':
    result = inspect()
    path = ROOT / 'verification/biwn-disc-gate-target-inventory.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'path': str(path), 'payloads': len(result['payloads']),
                      'gates': len(result['gates']), 'non_FFFF_gates': len(result['non_FFFF_gates']),
                      'invalid_segments': len(result['invalid_segments']),
                      'directionally_enabled_gates': len(result['directionally_enabled_gates']),
                      'startup_witness_tiles': len(result['startup_25_tile_record_witness']),
                      'sample': result['directionally_enabled_gates'][:3]}))
