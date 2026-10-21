"""Input preservation, output refusal and independent MSF arithmetic checks."""
import copy
import datetime
import json
from pathlib import Path
import tempfile

import extract_biwn_stage as stage

ROOT = stage.ROOT
session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
checks = {}
raw = (session / 'raw-tracks/track-02-raw.bin').read_bytes()
candidate, facts = stage.derive(raw)
assert candidate == (session / 'nextstage-68000-candidate.bin').read_bytes()
checks['reproduced_candidate_matches_previous_capture'] = True

for name, corrupted in [
    ('truncated_track', raw[:-2]),
    ('marker_bit_changed', raw[:376994] + bytes([raw[376994] ^ 1]) + raw[376995:]),
    ('payload_bit_changed', raw[:377058] + bytes([raw[377058] ^ 1]) + raw[377059:]),
]:
    try:
        stage.derive(corrupted)
    except ValueError as exc:
        assert 'differs from the preserved' in str(exc)
        checks[name] = 'rejected before publication'
    else:
        raise AssertionError(name)

try:
    stage.swap16(b'123')
except ValueError:
    checks['partial_word'] = 'rejected'
else:
    raise AssertionError('Odd word-swap input accepted')

# Independently compare the loader's byte/word borrow sequence with a frame clock.
# This includes second and minute boundaries, but does not establish a real TOC.
count = 0
for frames in range(6, 100 * 60 * 75):
    minute, remainder = divmod(frames, 4500)
    second, frame = divmod(remainder, 75)
    packed = (minute << 16) | (second << 8) | frame
    result = stage.subtract_six(packed)
    actual_frames = (((result >> 16) & 255) * 60 + ((result >> 8) & 255)) * 75 + (result & 255)
    assert actual_frames == frames - 6
    count += 1
checks['binary_msf_borrow_matches_frame_clock'] = {'cases': count, 'range': '00:00:06 through 99:59:74'}

layout = json.loads((session / 'cdi-layout.json').read_text())
trace = stage.conditional_toc_trace(layout, facts)
assert trace['selected_track'] == 2
assert trace['seek_msf'] == [2, 50, 23]
assert trace['marker_sector_and_byte_after_assumed_seek'] == [16, 674]
assert trace['entries_omitted_by_first_scan'] == [4, 5]
checks['conditional_toc'] = trace
tail_only = copy.deepcopy(layout)
for t in tail_only['tracks']:
    t['session'] = 1 if t['track'] < 4 else 2
try:
    stage.conditional_toc_trace(tail_only, facts)
except ValueError as exc:
    assert 'fail to find a matching entry' in str(exc)
    checks['tail_only_session2'] = 'correctly rejects: the audited first loop omits entries 4 and 5'
else:
    raise AssertionError('Incorrectly generalized the scanner to all track entries')

with tempfile.TemporaryDirectory(prefix='biwn-publication-') as folder:
    target = Path(folder) / 'keep.bin'
    original = b'Existing user output must survive unchanged.'
    target.write_bytes(original)
    try:
        stage.publish(target, candidate)
    except FileExistsError:
        assert target.read_bytes() == original
        checks['existing_output'] = 'refused; original bytes unchanged'
    else:
        raise AssertionError('Existing output overwritten')
    fresh = Path(folder) / 'fresh.bin'
    stage.publish(fresh, candidate)
    assert stage.digest(fresh.read_bytes()) == stage.STAGE_SHA
    checks['new_output'] = 'exclusive creation and readback passed'

report = {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'Image-specific byte extraction guards, selected track-scanner edge case and independent binary MSF arithmetic; no game/BIOS execution.',
          'implementation_sha256': stage.cdi_layout.sha(Path(stage.__file__)),
          'checks': checks}
path = ROOT / 'verification/biwn-stage-reproduction-checks.json'
path.write_text(json.dumps(report, indent=2) + '\n')
print(path)
