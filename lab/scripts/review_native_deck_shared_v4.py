"""Review five final-address callers and fresh eight-byte original-geometry control."""
from datetime import datetime, timezone
import json
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save
import check_native_deck_shared_v4 as kernel

V = ROOT / 'verification'


def read(path):
    return json.loads(Path(path).read_text())


def main():
    out = V / 'native-Deck-shared-review-v4' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out, flush=True)
    bp = V / 'native-Deck-shared-disc-build-v4-current.json'
    build = read(bp)
    bound = [Path(__file__), bp, Path(kernel.__file__)]
    for key in ['derived_disc', 'derived_stage', 'component']:
        assert sha(build[key]) == build[key + '_sha256']
        bound.append(Path(build[key]))
    component = Path(build['component']).read_bytes()
    matrices = [
        ('native-deck-shared-v4-current.json', 5248),
        ('native-deck-shared-final-v4-current.json', 5248),
        ('native-deck-shared-connected-v4-current.json', 128),
        ('native-deck-shared-connected-final-v4-current.json', 128),
        ('native-deck-alias-nesting-v4-current.json', 128),
        ('native-deck-alias-nesting-final-v4-current.json', 128),
        ('native-deck-geometry-alias-v4-current.json', 128),
        ('native-deck-geometry-alias-final-v4-current.json', 128),
        ('shared-Deck-fallback-ABI-v4-current.json', 1280),
    ]
    def bind_proof(path):
        proof = read(path)
        for p, digest in proof['source_sha256'].items():
            assert sha(p) == digest, p
            bound.append(Path(p))
        bound.append(path)
        return proof
    for name, count in matrices:
        proof = bind_proof(V / name)
        assert proof['completed'] == count
        bound.append(Path(proof['directory']) / 'cases.json')
        if name == 'native-deck-shared-final-v4-current.json':
            assert proof['deployed_module_byte_identity']
    startup = bind_proof(V / 'native-Deck-shared-startup-heap-v4-current.json')
    capacity = bind_proof(V / 'native-Deck-shared-capacity-v4-current.json')
    regions = bind_proof(V / 'shared-Deck-region-check-v4-current.json')
    watcher = bind_proof(V / 'geometry-observer-qualified-v1-current.json')
    assert startup['startup_cases'] == 6 and startup['heap_initialize_cases'] == 192
    assert capacity['cases'] == 36 and len(regions['negative_controls']) == 58
    assert watcher['legal_controls'] == 2 and watcher['rejected_fault_controls'] == 8
    jobs, reports, shared, geometries, faces, retained, used = {}, {}, {}, {}, {}, {}, {}
    for lane in ['candidate', 'control']:
        path = V / ('native-Deck-five-caller-geometry-v1-' + lane + '-current.json')
        job = bind_proof(path)
        assert job['status'] == 'terminal_fresh_geometry_route_pending_review'
        assert sha(job['build']) == job['build_sha256'] == sha(bp)
        jobs[lane] = job
        folder = Path(job['report']).parent
        report = read(job['report'])
        assert sha(job['report']) == job['report_sha256']
        assert not report['captured_state_input'] and not report['host_CPU_or_GPU_register_seed']
        trial = report['ordinary_Deck_input_trial']
        assert 400 <= len(trial['inputs']) <= 912 and trial['start_frame'] > 20000
        assert len(report['frames']) == trial['start_frame'] + len(trial['inputs'])
        reports[lane] = report
        retained[lane] = obs = read(folder / 'gameplay-observation.json')
        shared[lane] = s = read(folder / 'shared-observation.json')
        faces[lane] = face = read(folder / 'face-observation.json')
        geometries[lane] = geometry = read(folder / 'geometry-observation.json')
        errors = {k: x for k, x in obs.items() if isinstance(x, (int, float)) and
                  any(word in k for word in ['error', 'pending', 'outside', 'corruption', 'collision'])}
        assert errors and not any(errors.values()), errors
        assert not any(s[k] for k in ['errors', 'pending', 'C_stack_outside'])
        assert s['native_entries'] == s['native_returns'] and s['helper_entries'] == s['helper_returns']
        assert s['fallback_entries'] == [0] * 5
        assert obs['mb_entries'] == obs['mb_native'] == obs['mb_returns'] and min(obs['mb_returns']) > 0
        assert obs['acquire_entries'] == obs['acquire_returns'] and obs['acquire_pending'] == 0
        assert obs['deck_entries'] == obs['deck_native_entries'] == obs['deck_native_returns'] > 0
        assert obs['deck_source_steps'] == obs['deck_invalid_entries'] == 0
        assert face['entries'] == face['returns'] == face['positive_speed_entries'] > 0
        assert face['errors'] == face['pending'] == face['original_parent_returns'] == 0
        assert face['native_parent_returns'] == face['suspended_native_parent_checks'] == face['returns']
        assert geometry['entries'] == geometry['returns'] == geometry['original_outer_parent_returns'] > 0
        assert geometry['errors'] == geometry['pending'] == 0
        assert geometry['helper_entries'] == geometry['helper_returns'] == [geometry['entries']] * 5
        if lane == 'candidate':
            assert s['public_entries'] == s['native_entries'] == s['native_returns']
            assert min(s['native_returns']) > 0 and s['original_body_steps'] == [0] * 5
            assert geometry['original_body_steps'] == 0 and s['native_returns'][4] == geometry['returns']
        else:
            assert s['native_returns'][4] == 0 and s['original_body_steps'][4] > 0
            assert all(s['native_returns'][i] > 0 for i in range(4))
            assert geometry['original_body_steps'] > 0
        final = report['frames'][-1]
        assert final['scene_word'] == 312 and final['player_mode_word'] == 1 and final['movie_flag_words'] == [0, 0]
        ram_path = folder / 'RAM-final.bin'
        ram = ram_path.read_bytes()
        assert sha(ram_path) == report['final_RAM_sha256']
        base = build['resident_address']
        for lo, hi in [(base, build['arena_address']), (build['arena_end'], build['deck_arena_address'])]:
            assert ram[lo:hi] == component[lo-base:hi-base]
        used[lane] = []
        for slot in range(101):
            at = build['deck_arena_address'] + slot * 1024
            for lo, hi in kernel.FENCES:
                assert ram[at+lo:at+hi] == component[at-base+lo:at-base+hi]
            for _, offset, _, _ in kernel.LAYOUT.values():
                assert ram[at+offset+114:at+offset+118] == bytes(4)
            if ram[at:at+1024] != component[at-base:at-base+1024]:
                used[lane].append(slot)
        for slot in range(102):
            at = build['arena_address'] + slot * 256
            for lo in [0, 240]:
                assert ram[at+lo:at+lo+16] == component[at-base+lo:at-base+lo+16]
        for file in ['report.json', 'gameplay-observation.json', 'shared-observation.json',
                     'geometry-observation.json', 'face-observation.json', 'RAM-final.bin',
                     'state-final.bin', 'original-emulator-final-frame.png']:
            bound.append(folder / file)
    a, b = reports['candidate'], reports['control']
    start = a['ordinary_Deck_input_trial']['start_frame']
    assert start == b['ordinary_Deck_input_trial']['start_frame']
    ignored = {'full_RAM_sha256', 'stage_sha256'}
    for left, right in zip(a['frames'][:start], b['frames'][:start]):
        assert {k: x for k, x in left.items() if k not in ignored} == {k: x for k, x in right.items() if k not in ignored}, left['frame']
    assert a['frames'][-1]['video_sha256'] == b['frames'][-1]['video_sha256']
    matching_video = sum(x['video_sha256'] == y['video_sha256'] for x, y in zip(a['frames'], b['frames']))
    assert len(a['frames']) == len(b['frames'])
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = session / 'nextstage-mapping.json'
    offset = read(mapping)['payload_raw_cdi_offset'] + 0x11ad4 - 0x4000
    command = jobs['control']['command']
    control_disc = Path(command[command.index('--disc') + 1])
    changed = position = 0
    with Path(build['derived_disc']).open('rb') as left_file, control_disc.open('rb') as right_file:
        while True:
            left, right = left_file.read(1048576), right_file.read(1048576)
            assert len(left) == len(right)
            if not left:
                break
            if left != right:
                for i, (x, y) in enumerate(zip(left, right)):
                    if x != y:
                        assert offset <= position + i < offset + 8
                        changed += 1
            position += len(left)
    assert 0 < changed <= 8
    prior = read(V / 'native-Deck-shared-reviewed-v3-current.json')
    assert sha(prior['build']) == prior['build_sha256']
    assert sha(prior['disc']) == prior['disc_sha256']
    for path, digest in build['source_sha256'].items():
        assert sha(path) == digest, path
        bound.append(Path(path))
    bound.extend([mapping, control_disc, V / 'native-Deck-shared-reviewed-v3-current.json'])
    proof = dict(status='terminal_fresh_five_native_Deck_callers_reviewed',
                 recorded_at=datetime.now(timezone.utc).isoformat(), directory=str(out),
                 build=str(bp), build_sha256=sha(bp), disc=build['derived_disc'],
                 disc_sha256=build['derived_disc_sha256'], native_code_bytes=build['linked_component_bytes'],
                 shared_module_bytes=build['shared_Deck_code_bytes'], total_reservation_bytes=build['component_bytes'],
                 initial_heap_bytes=0x1c0000-build['heap_start'],
                 installed_recovered_Deck_entries=build['installed_Deck_entries'],
                 remaining_hosted_only_Deck_entries=build['remaining_hosted_Deck_entries'],
                 candidate_frames=len(a['frames']), control_frames=len(b['frames']),
                 candidate_trial_frames=len(a['ordinary_Deck_input_trial']['inputs']),
                 control_trial_frames=len(b['ordinary_Deck_input_trial']['inputs']),
                 ordinary_native_returns=dict(zip(kernel.LAYOUT, shared['candidate']['native_returns'])),
                 ordinary_native_helper_returns=dict(zip(kernel.LAYOUT, shared['candidate']['helper_returns'])),
                 same_layout_control_returns=dict(zip(kernel.LAYOUT, shared['control']['native_returns'])),
                 same_layout_control_original_geometry_calls=geometries['control']['returns'],
                 geometry_observations=geometries, natural_face_observations=faces,
                 native_GPU_returns={lane: retained[lane]['mb_returns'] for lane in retained},
                 all_observed_monitor_errors_pending_outside_zero=True,
                 all101_Deck_seven_fences_pass=True, all102_GPU_fences_pass=True,
                 Deck_used_slots=used, immutable_code_unchanged=True,
                 pre_input_recorded_fields_equal_frames=start,
                 pre_input_RAM_and_stage_hashes_excluded_for_static_redirect=True,
                 control_declared_redirect_bytes=8, control_changed_disc_bytes=changed,
                 matching_video_frames=matching_video,
                 differing_video_frames=len(a['frames'])-matching_video,
                 final_video_equal=True, timing_cycle_identity_verified=False,
                 component_cases=5248, final_address_cases=5248,
                 nested_retained_four_cases_each_address=128,
                 nested_geometry_entries_in_that_matrix=0,
                 alias_cases_each_pair_each_address=128, fallback_ABI_cases=1280,
                 startup_cases=6, heap_initialize_cases=192, capacity_cases=36,
                 native_region_fault_controls=58, geometry_watcher_legal_controls=2,
                 geometry_watcher_fault_controls=8, prior_four_caller_disc_preserved=True,
                 selector13_restoration_retained=True, restoration_changes_original_behavior=True,
                 native_keyboard_default_updated=False, new_training=False,
                 whole_game_complete=False, physical_console_verified=False,
                 authorship=build['geometry_algorithm_authorship'] + ' ' + build['face_algorithm_authorship'],
                 scope='Separate five-caller image and fresh same-layout eight-byte original-geometry control. '
                 'Ordinary directional input; five actual original geometry helpers return on every geometry call. '
                 'No checkpoint restore or host guest-state injection in these runs. '
                 'Only pre-trial recorded fields excluding declared static RAM/stage hashes match exactly. '
                 'Some active-trial video frames differ; final video equality and equal call counts do not prove cycle identity. '
                 'Original helpers, busy fallbacks, HLE assists, arbitrary suspension/reentry/IRQ, audio/physical fidelity '
                 'and full-game same-console source rebuilding remain incomplete. Preview remains the older three-caller build.',
                 source_sha256={str(p): sha(p) for p in set(bound)})
    save(out / 'review.json', proof)
    save(V / 'native-Deck-shared-reviewed-v4-current.json', proof)
    print(proof['status'], proof['ordinary_native_returns'], 'unequal video frames', proof['differing_video_frames'])


if __name__ == '__main__':
    main()
