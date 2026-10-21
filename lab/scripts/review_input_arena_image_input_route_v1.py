"""Review v39 fresh input-only comparison without normalizing game state."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    out = V/'input-arena-image-fresh-input-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    deps = {str(Path(__file__)): sha(__file__)}
    jobs, reports = {}, {}
    for lane in ['candidate', 'control']:
        path = V/f'native-input-arena-image-fresh-input-v1-{lane}-current.json'
        job = read(path)
        assert job['status'] == 'terminal_fresh_scene17_route_pending_review', (lane, job['status'])
        assert job['input_only_control'] and job['scene_native_in_both_lanes']
        assert job['snapshot_restores'] == job['host_guest_RAM_writes'] == job['host_CPU_or_task_seeds'] == 0
        for source, digest in job['source_sha256'].items():
            assert sha(source) == digest, source
        deps.update(job['source_sha256'])
        deps[str(path)] = sha(path)
        report = Path(job['report'])
        assert sha(report) == job['report_sha256']
        deps[str(report)] = sha(report)
        for observation in (Path(job['directory'])/'candidate').glob('*-observation.json'):
            deps[str(observation)] = sha(observation)
        for name in ['shared_observation', 'face_observation', 'geometry_observation', 'outer_observation', 'reset_observation', 'rotation_observation', 'clear_observation', 'display_observation', 'records_observation', 'resource_input_observation']:
            obs = job[name]
            bad = {k: v for k, v in obs.items() if isinstance(v, (int, float)) and any(tag in k for tag in ['errors', 'pending', 'outside'])}
            assert not any(bad.values()), (lane, name, bad)
        scene = job['shared_observation']
        assert scene['native_entries'][5] == scene['native_returns'][5] > 0
        assert scene['original_body_steps'][5] == 0
        inp = job['resource_input_observation']
        assert inp['input_calls'] == inp['input_returns'] > 0
        assert inp['resource_public'] == inp['resource_native_entries'] == inp['resource_returns'] > 0
        if lane == 'control':
            assert inp['input_native'] == 0 and inp['input_original'] == inp['input_calls']
        else:
            assert inp['input_native'] > 0
        jobs[lane], reports[lane] = job, read(report)
        save(out/(lane+'-job.json'), job)

    # Prove the actual control disc differs only by the declared six-byte JSR.
    build_path = Path(jobs['candidate']['build'])
    assert jobs['candidate']['build_sha256'] == jobs['control']['build_sha256'] == sha(build_path)
    build = read(build_path)
    control_dir = Path(jobs['control']['directory'])
    delta_path = control_dir/'control-delta.json'
    delta = read(delta_path)
    assert delta['declared_bytes'] == 6 and delta['only_input_callsite_restored']
    disc, control = Path(build['derived_disc']), control_dir/'same-layout-original-input.cdi'
    assert sha(disc) == build['derived_disc_sha256'] == delta['parent_sha256']
    assert sha(control) == delta['control_sha256']
    changed = []
    offset = 0
    with disc.open('rb') as left, control.open('rb') as right:
        while True:
            a, b = left.read(1024*1024), right.read(1024*1024)
            assert len(a) == len(b)
            if not a:
                break
            if a != b:
                changed.extend(offset+i for i, (x, y) in enumerate(zip(a, b)) if x != y)
                assert len(changed) <= 6
            offset += len(a)
    session_pointer = ROOT/'projects/black-ice-white-noise/analysis/current-session.json'
    mapping_path = Path(read(session_pointer)['directory'])/'nextstage-mapping.json'
    at = read(mapping_path)['payload_raw_cdi_offset']+0x1a266-0x4000
    assert changed and all(at <= x < at+6 for x in changed), changed
    for path in [build_path, delta_path, disc, control, session_pointer, mapping_path]:
        deps[str(path)] = sha(path)
    save(out/'disc-delta-verified.json', dict(declared_patch_bytes=6, actual_changed_bytes=len(changed), offsets=changed, checked_entire_disc=True, original_input_callsite='0x1A266', scene_native_in_both_lanes=True))

    a, b = reports['candidate']['frames'], reports['control']['frames']
    assert a and b and all(x['frame'] == y['frame'] for x, y in zip(a, b))
    fields = {}
    for key in ['video_sha256', 'held_buttons', 'raw_player_X', 'raw_player_Z', 'scene_word', 'player_mode_word', 'tile_word', 'floor_word', 'locomotion_state']:
        different = [x['frame'] for x, y in zip(a, b) if x[key] != y[key]]
        fields[key] = dict(count=len(different), first_frame=different[0] if different else None, final_equal=a[-1][key] == b[-1][key])
    frontend = sum((x.get('navigation') or {}).get('buttons', []) != (y.get('navigation') or {}).get('buttons', []) for x, y in zip(a, b))
    heap = {lane: j['outer_observation']['minimum_heap_free_while_outer_active'] for lane, j in jobs.items()}
    counts = {lane: dict(input=j['resource_input_observation'], native_scene_returns=j['shared_observation']['native_returns'][5], record_returns=j['records_observation']['returns'], record_matrix_returns=j['records_observation']['matrix_returns'], record_copy_returns=j['records_observation']['copy_returns']) for lane, j in jobs.items()}
    comparison = dict(frames=dict(candidate=len(a), control=len(b)), paired_frames=min(len(a), len(b)), unpaired_tail_frames=abs(len(a)-len(b)), fields=fields, frontend_button_schedule_differences=frontend, final_video_equal=fields['video_sha256']['final_equal'], final_selected_fields_equal=all(x['final_equal'] for x in fields.values()), audio={lane: report['audio'] for lane, report in reports.items()}, minimum_sampled_heap_while_outer_active=heap, global_heap_minimum_measured=False, call_counts=counts, input_only_control=True, scene_native_in_both_lanes=True, snapshot_restores=0, host_guest_RAM_writes=0, host_CPU_or_task_seeds=0, scope='Frame-index comparison of fresh boots with only the input callsite changed. Both lanes retain compiled scene/resource code and use the same feedback policy. Unequal schedules or durations do not establish causal speed or original-game fidelity. Raw video, pose and controller values remain unmodified. This finite outdoor route does not establish indoor/full-game/console qualification.')
    save(out/'comparison.json', comparison)
    facts = dict(status='terminal_v39_fresh_input_only_route_reviewed_fidelity_open', directory=str(out), comparison=str(out/'comparison.json'), candidate_frames=len(a), control_frames=len(b), video_differences=fields['video_sha256']['count'], frontend_button_schedule_differences=frontend, game_latched_button_RAM_differences=fields['held_buttons']['count'], final_video_equal=comparison['final_video_equal'], final_selected_fields_equal=comparison['final_selected_fields_equal'], all_monitors_clear_and_quiescent=True, fresh_gameplay_executed=True, full_game_input_qualified=False, game_fidelity_verified=False, default_promoted=False, installed_preview_changed=False, new_predictions=0, new_training=False, call_counts=counts, minimum_sampled_heap_while_outer_active=heap, source_sha256=deps)
    save(out/'review.json', facts)
    save(V/'input-arena-image-fresh-input-reviewed-v1-current.json', facts)
    print({k: facts[k] for k in ['status', 'candidate_frames', 'control_frames', 'video_differences', 'final_video_equal', 'final_selected_fields_equal']}, flush=True)


if __name__ == '__main__':
    main()
