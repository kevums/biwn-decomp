"""Check the recorded plan and reject damaged/out-of-domain snapshot inputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import biwn_indoor_exit_planner as planner


def main():
    source_manifest = json.loads((ROOT / 'verified-previews/indoor-exit-planning-scene.json').read_text())
    original = (ROOT / source_manifest['relative_RAM']).read_bytes()
    proof = json.loads((ROOT / 'verification/building570-exit-route-current.json').read_text())
    actual = planner.plan(ROOT)
    assert len(actual['candidates']) == 1 and actual['candidates'][0]['plan'] == proof['controller_plan']
    assert actual['source_RAM_sha256'] == proof['source_RAM_sha256']
    assert actual['memory_written'] is actual['buttons_executed'] is actual['live_game_state'] is False
    cases = ['exact_recorded_source_matched_plan']
    with tempfile.TemporaryDirectory(prefix='biwn-indoor-plan-') as temporary:
        root = Path(temporary)
        preview = root / 'verified-previews'
        preview.mkdir()
        snapshot = preview / 'building570-RAM.bin'
        manifest_path = preview / 'indoor-exit-planning-scene.json'

        def seed(raw=original):
            snapshot.write_bytes(raw)
            manifest = dict(source_manifest, RAM_sha256=hashlib.sha256(raw).hexdigest())
            manifest_path.write_text(json.dumps(manifest))
            return manifest

        def reject(name):
            try:
                planner.plan(root)
            except ValueError:
                cases.append(name)
            else:
                raise AssertionError(name)

        seed()
        damaged = bytearray(original)
        damaged[-1] ^= 1
        snapshot.write_bytes(damaged)
        reject('corrupt_RAM_hash_rejected')
        manifest = seed()
        manifest['relative_RAM'] = '../outside.bin'
        manifest_path.write_text(json.dumps(manifest))
        reject('path_escape_rejected_before_file_open')
        raw = bytearray(original)
        raw[0x49c62:0x49c64] = (1).to_bytes(2, 'big')
        seed(raw)
        assert planner.plan(root)['candidates'] == []
        cases.append('upper_floor_no_outdoor_exit')
        get = lambda a, w=2: int.from_bytes(original[a:a + w], 'big')
        container = get(0x49c18, 4)
        record = get(0x49c78, 4)
        groups = get(container + 8, 4)
        index = get(record + 22)
        entry = groups + index * 6
        raw = bytearray(original)
        raw[entry + 2:entry + 4] = (0x8400).to_bytes(2, 'big')
        seed(raw)
        assert planner.plan(root)['candidates'] == []
        cases.append('no_source_exit_permission_no_plan')
        raw = bytearray(original)
        raw[entry + 4:entry + 6] = (0).to_bytes(2, 'big')
        seed(raw)
        assert planner.plan(root)['candidates'] == []
        cases.append('internal_region_target_is_not_outdoor_exit')
        raw = bytearray(original)
        raw[entry + 2:entry + 4] = (0x0400).to_bytes(2, 'big')
        raw[entry + 6:entry + 8] = get(entry).to_bytes(2, 'big')
        seed(raw)
        assert planner.plan(root)['candidates'] == []
        cases.append('later_duplicate_key_cannot_override_first_match')
        raw = bytearray(original)
        raw[0x49c18:0x49c1c] = (container | 0x80000000).to_bytes(4, 'big')
        seed(raw)
        assert planner.plan(root)['candidates'] == actual['candidates']
        cases.append('tagged_pointer_24bit_address_equivalence')
        raw = bytearray(original)
        raw[container + 8:container + 12] = (0x200000).to_bytes(4, 'big')
        seed(raw)
        reject('outside_main_RAM_table_rejected')
        raw = bytearray(original)
        for slot in range(index, get(container + 2)):
            offset = groups + slot * 6 + 2
            raw[offset:offset + 2] = (get(offset) & 0x7fff).to_bytes(2, 'big')
        seed(raw)
        reject('unterminated_bounded_list_rejected')
    report = dict(status='checked_indoor_plan_matches_recorded_exit_and_guards_pass',
                  recorded_at=datetime.now(timezone.utc).isoformat(), cases=cases,
                  source_plan=proof['controller_plan'], execution_proof=str(ROOT / 'verification/building570-exit-route-current.json'),
                  synthetic_mutations_written_to_game=False, native_Chat_verified=False,
                  scope='Exact positive plan equals the source-matched600frame recorded exit. Remaining cases mutate private temporary snapshot copies only and exercise lookup guards, not additional game execution or general navigation.')
    (ROOT / 'verification/indoor-exit-planner-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], len(cases), flush=True)


if __name__ == '__main__':
    main()
