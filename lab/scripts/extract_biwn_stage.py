"""Reproduce the static second-stage candidate from the preserved BIWN#23 CDI.

This is an image-specific extraction, not a general Jaguar executable loader.
The nominal CD_read buffer can contain code, data, padding and mastering data.
No BIOS, GPU, MMIO or game code is executed by this command.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import struct

import cdi_layout

ROOT = Path(__file__).resolve().parent.parent
IMAGE_SHA = '0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
TRACK_SHA = '44f0e6412d05a91fd7cd3b1f298faeddc91b22b0a8c8619c1fd929d84fee9ef6'
BOOT_SHA = '235b342638e4face19e82b68d1fdd6592e58dbf689792ee41d572db465cfc8a4'
STAGE_SHA = '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
READ_BLOCK = bytes.fromhex(
    '207c00004000227c00100000223c5354554274004eb8303c4eb8304e'
    'b1fc001000006ff44eb8304223fc0000000100f03800203900f02114'
    'c07c000166f44ef84000')
TOC_BLOCK = bytes.fromhex(
    '207c00002c0043e8000812280003923c00014881363c0064923c0001'
    '6700001ed1fc0000000810280004b03c000166e81010b6006de21600224860dc'
    '207c00002c00d1fc0000000810280004b03c000166f01010b00366ea2010'
    'c0bc00ffffff903c000664000018d03c004b907c01006400000cd07c3c0090bc00010000')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def swap16(data):
    if len(data) % 2:
        raise ValueError('Word-swapped input must contain complete 16-bit words')
    result = bytearray(len(data))
    result[::2], result[1::2] = data[1::2], data[::2]
    return bytes(result)


def marker_runs(data, marker):
    """Return maximal, word-aligned runs; isolated instruction constants survive."""
    runs = []
    position = 0
    while True:
        start = data.find(marker, position)
        if start < 0:
            return runs
        if start % 2:
            position = start + 1
            continue
        end = start + len(marker)
        while data[end:end + len(marker)] == marker:
            end += len(marker)
        runs.append({'start': start, 'end': end, 'count': (end - start) // len(marker)})
        position = end


def derive(raw):
    if digest(raw) != TRACK_SHA:
        raise ValueError('Raw track differs from the preserved BIWN#23 track')
    normalized = swap16(raw)
    magic = b'ATARI APPROVED DATA HEADER ATRI '
    header = normalized.find(magic)
    if header < 0 or normalized.find(magic, header + 1) >= 0:
        raise ValueError('Expected exactly one Atari boot header')
    base, size = struct.unpack_from('>II', normalized, header + 32)
    boot_start = header + 40
    boot = normalized[boot_start:boot_start + size]
    if base != 0x180000 or size != 60000 or digest(boot) != BOOT_SHA:
        raise ValueError('Boot header or payload differs from the captured candidate')
    if boot[0x146:0x188] != READ_BLOCK or boot[0xc8:0x146] != TOC_BLOCK:
        raise ValueError('Loader instruction bytes differ from the audited listing')
    # The complete guarded block fixes these instruction forms and register writes.
    low = int.from_bytes(boot[0x148:0x14c], 'big')
    high = int.from_bytes(boot[0x14e:0x152], 'big')
    marker = boot[0x154:0x158]
    runs = marker_runs(normalized, marker)
    repeated = [r for r in runs if r['count'] > 1]
    if len(repeated) != 1 or repeated[0]['count'] != 16:
        raise ValueError('Expected one maximal run of sixteen partition markers')
    run = repeated[0]
    start = run['end']
    length = high - low
    if length <= 0 or start + length > len(normalized):
        raise ValueError('Nominal loader buffer extends beyond the captured raw track')
    candidate = normalized[start:start + length]
    if digest(candidate) != STAGE_SHA:
        raise ValueError('Derived candidate differs from the captured stage')
    overlap_start = start - boot_start
    overlap = len(boot) - overlap_start
    if overlap < 0 or boot[overlap_start:] != candidate[:overlap]:
        raise ValueError('Initial boot payload overlap no longer agrees')
    return candidate, {
        'boot_header_raw_track_offset': header,
        'boot_payload_raw_track_offset': boot_start,
        'boot_load_address': hex(base), 'boot_bytes': size,
        'boot_sha256': digest(boot), 'marker_hex': marker.hex(),
        'marker_runs': runs, 'selected_marker_run': run,
        'candidate_raw_track_offset': start, 'candidate_bytes': length,
        'candidate_sha256': digest(candidate), 'load_address': hex(low),
        'nominal_end_address': hex(high),
        'boot_overlap': {'boot_offset': hex(overlap_start), 'bytes': overlap},
    }


def msf(frames):
    minute, remainder = divmod(frames, 75 * 60)
    second, frame = divmod(remainder, 75)
    if not 0 <= minute <= 255:
        raise ValueError('MSF minute is outside a byte')
    return [minute, second, frame]


def subtract_six(packed):
    """Literal byte/word arithmetic at 0x180128..0x180140; binary MSF, not BCD."""
    old_byte = packed & 255
    packed = (packed & ~255) | ((old_byte - 6) & 255)
    if old_byte < 6:
        packed = (packed & ~255) | (((packed & 255) + 75) & 255)
        old_word = packed & 65535
        packed = (packed & ~65535) | ((old_word - 0x100) & 65535)
        if old_word < 0x100:
            packed = (packed & ~65535) | (((packed & 65535) + 0x3c00) & 65535)
            packed = (packed - 0x10000) & 0xffffffff
    return packed


def conditional_toc_trace(layout, facts):
    """Evaluate the audited scanner under the pinned emulator's TOC conventions.

    This deliberately exposes that the first loop omits the last two entries.
    It is not a measurement of a real BIOS TOC or CD seek.
    """
    tracks = layout['tracks']
    entries = {}
    for t in tracks:
        number = t['track']
        # Assumption from CDIntfGetTrackInfo: LBA at INDEX 01 plus 150 lead-in.
        frames = t['declared_start_lba'] + t['pregap_sectors'] + 150
        entries[number] = bytes([number, *msf(frames), t['session'] - 1,
                                 *msf(t['program_sectors'])])
    max_track = max(entries)
    if sorted(entries) != list(range(1, max_track + 1)) or not 3 <= max_track <= 99:
        raise ValueError('Conditional scanner requires contiguous tracks 1..99, at least three')
    counter = (max_track - 1) & 255
    d3 = 100
    current = 0
    trace = []
    while True:
        counter = (counter - 1) & 255
        if counter == 0:
            break
        current += 1
        entry = entries[current]
        eligible = entry[4] == 1
        # CMP.B D0,D3 / BLT uses signed bytes. Track numbers <=99 are positive.
        selected = eligible and d3 >= entry[0]
        if selected:
            d3 = entry[0]
        trace.append({'entry': current, 'bytes_hex': entry.hex(),
                      'counter_after_decrement': counter, 'selected': selected})
    selected_entry = next((n for n in sorted(entries)
                           if entries[n][4] == 1 and entries[n][0] == d3), None)
    if selected_entry is None:
        raise ValueError('The second scan would fail to find a matching entry')
    entry = entries[selected_entry]
    track = next(t for t in tracks if t['track'] == selected_entry)
    packed = int.from_bytes(entry[:4], 'big') & 0xffffff
    seek = subtract_six(packed)
    seek_msf = [(seek >> 16) & 255, (seek >> 8) & 255, seek & 255]
    absolute_frames = (seek_msf[0] * 60 + seek_msf[1]) * 75 + seek_msf[2]
    seek_lba = absolute_frames - 150
    raw_sector = seek_lba - track['declared_start_lba']
    marker_distance = facts['selected_marker_run']['start'] - raw_sector * track['sector_bytes']
    return {
        'status': 'conditional_static_arithmetic_only',
        'assumptions': [
            'TOC entries are track-indexed, eight bytes each, with zero-based session byte 4.',
            'Header byte 3 is maximum track. INDEX 01 LBA is CDI start LBA plus stored pregap.',
            'TOC MSF is binary absolute LBA plus 150 lead-in frames, matching the pinned emulator reference.',
            'No hardware, BIOS binary, CD seek or GPU behavior was executed or observed.',
        ],
        'first_scan': trace,
        'entries_omitted_by_first_scan': list(range(current + 1, max_track + 1)),
        'selected_track': selected_entry, 'selected_entry_hex': entry.hex(),
        'track_start_msf': list(entry[1:4]), 'seek_msf': seek_msf,
        'packed_seek_hex': f'0x{seek:06x}', 'seek_lba': seek_lba,
        'seek_raw_track_sector': raw_sector,
        'marker_bytes_after_assumed_seek': marker_distance,
        'marker_sector_and_byte_after_assumed_seek': list(divmod(marker_distance, track['sector_bytes'])),
    }


def publish(target, data):
    # Never silently overwrite an existing result, even with identical bytes.
    with target.open('xb') as stream:
        stream.write(data)
    if target.read_bytes() != data:
        raise ValueError('Output readback differs')


def reproduce(session, destination):
    session = session.resolve()
    mapping = json.loads((session / 'boot-mapping.json').read_text())
    source = Path(json.loads((session / 'cdi-layout.json').read_text())['source'])
    layout = cdi_layout.parse(source)
    if layout['source_sha256'] != IMAGE_SHA:
        raise ValueError('Source CDI differs from the preserved image')
    track = next(t for t in layout['tracks'] if t['track'] == 2)
    raw_path = session / 'raw-tracks/track-02-raw.bin'
    raw = raw_path.read_bytes()
    with source.open('rb') as stream:
        stream.seek(track['raw_file_offset'])
        original_range = stream.read(track['raw_bytes'])
    if raw != original_range:
        raise ValueError('Captured raw track differs from the current source CDI range')
    candidate, facts = derive(raw)
    if mapping['source_cdi_sha256'] != IMAGE_SHA or mapping['normalized_payload_sha256'] != BOOT_SHA:
        raise ValueError('Recorded boot provenance disagrees with current input')
    trace = conditional_toc_trace(layout, facts)
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    binary = destination / 'nextstage-68000-candidate.bin'
    report_path = destination / 'reproduction.json'
    if binary.exists() or report_path.exists():
        raise ValueError('Use a fresh destination; existing results are not overwritten')
    report = {
        'schema': 'biwn-static-stage-reproduction/v1',
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'reproduced_static_candidate_runtime_unverified',
        'source': str(source), 'source_sha256': layout['source_sha256'],
        'raw_track': str(raw_path), 'raw_track_sha256': digest(raw),
        'raw_track_matches_current_cdi_range': True,
        'candidate_raw_cdi_offset': track['raw_file_offset'] + facts['candidate_raw_track_offset'],
        'facts': facts, 'conditional_toc_trace': trace,
        'output': str(binary), 'implementation_sha256': cdi_layout.sha(Path(__file__)),
        'limits': [
            'Nominal buffer length is not an executable/file extent or a code coverage measurement.',
            'The repeated marker run boundary follows a pinned emulator reference and static plausibility.',
            'CD_read can write up to 64 bytes beyond A1 per the Atari manual; overshoot is not imported.',
            'Actual BIOS TOC, seek, marker synchronization and game execution remain unverified.',
        ],
    }
    publish(binary, candidate)
    if cdi_layout.sha(source) != IMAGE_SHA or digest(raw_path.read_bytes()) != TRACK_SHA:
        raise ValueError('Input changed during reproduction; result must not be promoted')
    report['inputs_unchanged_after_readback'] = True
    publish(report_path, (json.dumps(report, indent=2) + '\n').encode())
    return report_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    session = args.session or Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    destination = args.output or session / f'stage-rebuild-{stamp}'
    print(reproduce(session, destination))


if __name__ == '__main__':
    main()
