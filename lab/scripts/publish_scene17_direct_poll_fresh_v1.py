"""Freeze v24 component/fresh/fixed-input evidence without promoting fidelity."""
import shutil, subprocess
from pathlib import Path
from datetime import datetime, timezone
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic


def main():
    wp = V/'native-Deck-current-status-v1-current.json'
    wrapper = read(wp)
    for path, digest in wrapper['dependencies_sha256'].items():
        assert sha(path) == digest, path
    stems = ['native-scene17-direct-poll-disc-build-v1', 'native-Deck-scene17-direct-poll-final-v1',
             'scene17-direct-poll-final-bridge-v1', 'scene17-direct-poll-final-fallback-v1',
             'scene17-direct-poll-final-reentry-v1', 'scene17-direct-poll-final-public-bus-v1',
             'scene17-direct-poll-input-face-alias-v1', 'native-deck-alias-nesting-scene17-direct-poll-final-v1',
             'native-scene17-direct-poll-geometry-alias-v1', 'native-Deck-outer-connected-scene17-direct-poll-v1',
             'scene17-direct-poll-geometry-observer-qualified-v1', 'outer-scene17-direct-poll-geometry-observer-qualified-v1',
             'shared-Deck-region-check-scene17-direct-poll-v1', 'scene17-direct-poll-shared-observer-qualified-v1',
             'scene17-direct-poll-shared-observer-actual-CPU-v2', 'scene17-direct-poll-reset-observer-qualified-v1',
             'scene17-direct-poll-observer-actual-CPU-v1', 'scene17-direct-poll-copied-rebuild-v1',
             'scene17-fixed-prefix-review-v1', 'game-quickstart-refresh-v1',
             'local-scene-poll-review-v1', 'scene17-local-feedback-wire-audit-v1']
    proofs = {name: read(V/(name+'-current.json')) for name in stems}
    for name, proof in proofs.items():
        assert proof['status'].startswith('terminal_') and 'failed' not in proof['status'], name
        for key in ['source_sha256', 'copied_source_sha256', 'files_sha256']:
            for path, digest in proof.get(key, {}).items():
                assert sha(path) == digest, (name, path)
    b = proofs[stems[0]]
    assert sha(b['derived_disc']) == b['derived_disc_sha256']
    scene_proof = proofs[stems[2]]
    assert scene_proof['completed'] == 770 and scene_proof['maximum_C_stack_bytes'] == 108
    assert scene_proof['deployed_module_byte_identity'] and scene_proof['actual_completion_read_counts_match']
    assert [proofs[name]['completed'] for name in stems[3:10]] == [384, 64, 14, 256, 256, 128, 128]
    jobs = {lane: read(V/f'native-scene17-direct-poll-fresh-v2-{lane}-current.json') for lane in ['candidate', 'control']}
    reports = {}
    for lane, job in jobs.items():
        assert job['status'] == 'terminal_fresh_scene17_route_pending_review', (lane, job['status'])
        assert job['snapshot_restores'] == job['host_guest_RAM_writes'] == job['host_CPU_or_task_seeds'] == 0
        for path, digest in job['source_sha256'].items():
            assert sha(path) == digest, (lane, path)
        assert sha(job['report']) == job['report_sha256']
        reports[lane] = read(job['report'])
        for name in ['shared', 'geometry', 'outer', 'reset']:
            obs = job[name+'_observation']
            assert obs['errors'] == obs['pending'] == 0, (lane, name)
        assert job['shared_observation']['native_entries'] == job['shared_observation']['native_returns']
        assert job['shared_observation']['helper_entries'] == job['shared_observation']['helper_returns']
    a, c = [reports[lane]['frames'] for lane in ['candidate', 'control']]
    fields = ['video_sha256', 'raw_player_X', 'raw_player_Z', 'scene_word', 'player_mode_word',
              'tile_word', 'equipped_word', 'movie_flag_words', 'movie_controller_state_word',
              'navigation', 'floor_word', 'raw_word_49c5c', 'locomotion_state', 'held_buttons']
    compared = {key: dict(differing_frames=[x['frame'] for x, y in zip(a, c) if x.get(key) != y.get(key)],
                          candidate_final=a[-1].get(key), control_final=c[-1].get(key),
                          final_equal=a[-1].get(key) == c[-1].get(key)) for key in fields}
    counts = {key: len(value['differing_frames']) for key, value in compared.items()}
    final_selected_equal = all(value['final_equal'] for key, value in compared.items() if key != 'navigation')
    comparison = dict(candidate_frames=len(a), control_frames=len(c), paired_frames=min(len(a), len(c)),
                      fields=compared, counts=counts, final_video_equal=compared['video_sha256']['final_equal'],
                      final_selected_game_fields_equal=final_selected_equal,
                      identical_per_frame_frontend_inputs=False, same_feedback_navigation_policy=True,
                      audio={lane: report['audio'] for lane, report in reports.items()},
                      control_scope='Only the original ten bytes at17E0E are restored; all other compiled callers/helpers and memory layout are shared.',
                      scope='Finite fresh ordinary feedback-navigation route. Different frontend inputs prevent assigning all later differences to source logic or timing. No whole-game or arbitrary IRQ, audio or console equivalence.')
    sample_dir = Path(scene_proof['directory'])
    samples = read(sample_dir/'cases.json')[-2:]
    assert [x['long_completion_polls'] for x in samples] == [512, 1024]
    slope = (samples[1]['native_instructions']-samples[0]['native_instructions'])/512
    assert slope == 2
    out = V/'native-scene17-direct-poll-fresh-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out/'previous-wrapper.json', wrapper)
    packet = read(wrapper['packet'])
    save(out/'previous-status-packet.json', packet)
    for name, proof in proofs.items():
        save(out/(name+'.json'), proof)
        if name != stems[0]:
            subprocess.run(['/bin/cp', '-cR', proof['directory'], str(out/name)], check=True, capture_output=True)
        if 'files_sha256' in proof:
            for i, path in enumerate(proof['files_sha256']):
                shutil.copy2(path, out/name/(str(i)+'-'+Path(path).name))
    for lane, job in jobs.items():
        save(out/(lane+'-job.json'), job)
        subprocess.run(['/bin/cp', '-cR', job['directory'], str(out/lane)], check=True, capture_output=True)
    save(out/'fresh-comparison.json', comparison)
    fixed = proofs['scene17-fixed-prefix-review-v1']
    scene_returns = jobs['candidate']['shared_observation']['native_returns'][5]
    helper_returns = jobs['candidate']['shared_observation']['helper_returns'][5]
    control_calls = jobs['control']['shared_observation']['public_entries'][5]
    report_path = ROOT/'reports/BIWN Direct Polling and Fixed Input Review.txt'
    report_path.write_text(
        'BIWN — direct GPU completion polling, v24\n\n'
        f'The candidate completes {len(a):,} fresh frames and the same-layout original-scene control completes {len(c):,}. '
        f'All {scene_returns:,} native scene calls and {helper_returns:,} helper calls return; the control records {control_calls:,} original scene calls. '
        'Shared, geometry, outer and reset monitors finish clear and quiescent. No checkpoint restore or host RAM/CPU/task repair.\n\n'
        f'There are {counts["video_sha256"]:,} differing paired video frames and {counts["held_buttons"]:,} differing held-input samples. '
        f'Final video equal: {comparison["final_video_equal"]}. Final selected game fields equal: {final_selected_equal}. '
        'Navigation uses feedback, so these full routes do not receive identical frame-by-frame input. Raw differences remain preserved.\n\n'
        'The separate equal-input comparison replays the exact original control buttons for1,000frames. V23 has189video differences and v24 has194; both first differ at549, before the held-input sample difference600. '
        'Controls match video, selected gameplay fields and GPU/DSP states across the two builds. One control CPU N-flag difference at frame181 is preserved; full CPU identity is not claimed. '
        'The v23 control replay also matches the prior CPU/video/full-RAM capture. This experiment shows that direct polling alone does not resolve the early presentation differences. '
        'Live GPU calls at the fixed cutoff are recorded, with all102slot fences independently checked; this is a prefix measurement, not route completion.\n\n'
        'V24 replaces the native callback polling path with physical TST.L $10A684/BNE instructions. The two long-wait cases add two target instructions per extra busy read versus28previously. '
        'This is not a14times game speedup or a hardware-cycle result. Logical flags commit on completion; intermediate logical flags and arbitrary interrupt equivalence remain unproven. '
        'The44,108-byte module occupies the previous44,226-byte reservation using118NOPpadding. Staging/copy sizes, arena addresses and124,864initial heap bytes are retained. Linked native code totals84,938bytes.\n\n'
        'The deployed module passes770CPU/RAM/helper cases and all eight final image gates, plus384fallback,64nested-scene,14bus-order,256scene/input/face alias,256cross-root alias,128geometry alias and128connected cases. '
        'Read-only monitors pass512actual scene/fallback/reentry lanes,64geometry lanes and64reset input pairs plus corruption controls. Copied SDK/source rebuilding is byte-identical. '
        'These are finite emulator/component results; full game, audio, arbitrary IRQ and physical-console fidelity are incomplete.\n\n'
        'Codex authored this target glue. Earlier local Scene Author/Repair outputs remain rejected; this turn performs no optimizer updates or new local predictions. The local poll-review attempt was busy and generated no responses. '
        'LM Studio UI inspection timed out. The installed game preview remains unchanged. Its launcher menu now selects the current v4 GUI; launch validation passes and saved controls include Shift+Up.\n\n'
        'Next: diagnose the original/native scene boundary differences under fixed inputs; remove remaining original helper dependencies with readable source and real native checks. Continue useful model training/evaluation when the shared model runtime is available. '
        'Do not promote this image as fidelity-approved.\n\nExperimental disc: '+b['derived_disc']+'\nDetailed full-route comparison: '+str(out/'fresh-comparison.json')+'\n')
    previous_scene = dict(packet['native_scene_draw_progress'])
    scene = dict(previous_scene)
    scene.update(status='terminal_scene17_direct_poll_fresh_pass_fidelity_open', profile='deck-shared-v24-scene-direct-poll',
                 previous_wait_profile=previous_scene, latest_fresh_result_is_passing_route=True,
                 experimental_disc=b['derived_disc'], experimental_disc_sha256=b['derived_disc_sha256'],
                 prototype_module_bytes=44108, final_module_bytes=44108, native_code_bytes=84938,
                 fresh_scene_native_entries=scene_returns, fresh_scene_native_returns=scene_returns,
                 fresh_scene_helper_returns=helper_returns, fresh_scene_original_control_calls=control_calls,
                 candidate_frames=len(a), control_frames=len(c), fresh_differing_video_frames=counts['video_sha256'],
                 held_input_differing_frames=counts['held_buttons'], final_video_equal=comparison['final_video_equal'],
                 final_selected_game_fields_equal=final_selected_equal, identical_frontend_inputs=False,
                 source_semantic_vs_timing_cause_proven=False, new_disc_fresh_gameplay_tested=True,
                 new_disc_fresh_route_completed=True, new_disc_fidelity_verified=False, cost_approved=False,
                 direct_poll_instructions_per_extra_busy_read=slope, fixed_input_comparison=fixed['comparisons'],
                 fixed_input_fidelity_resolved=False, installed_preview_changed=False, report=str(report_path),
                 next_action='Diagnose persistent fixed-input scene/presentation differences and remove original helper dependencies; retain all finite CPU/RAM/bus/stack gates. Whole-game rebuilding, same-console validation, arbitrary IRQ/audio fidelity and useful trained-model quality remain incomplete.')
    packet['native_scene_draw_progress'] = packet['latest_source_development'] = scene
    candidate = dict(packet['latest_native_candidate'])
    packet['previous_native_candidate_before_direct_poll'] = dict(candidate)
    candidate.update(status=scene['status'], variant='readable scene17 direct physical GPU polling plus retained native callers, v24',
                     directory=str(out), candidate_disc=b['derived_disc'], candidate_disc_sha256=b['derived_disc_sha256'],
                     native_module=scene_proof['payload'], native_module_sha256=scene_proof['payload_sha256'],
                     native_module_bytes=44108, native_code_bytes=84938, total_reservation_bytes=b['component_bytes'],
                     candidate_frames=len(a), control_frames=len(c), differing_video_frames=counts['video_sha256'],
                     held_button_differing_frames=counts['held_buttons'], final_video_equal=comparison['final_video_equal'],
                     final_selected_game_fields_equal=final_selected_equal, native_scene_returns=scene_returns,
                     native_scene_helper_returns=helper_returns, new_fresh_gameplay_verified=True,
                     fresh_route_completed=True, native_disc_qualified=False, native_disc_fidelity_verified=False,
                     scene_C_stack_low_offset=jobs['candidate']['shared_observation']['C_stack_low_offsets'][5],
                     installed_preview_changed=False, report=str(report_path), scope=comparison['scope'], next_action=scene['next_action'])
    packet['latest_native_candidate'] = packet['latest_fresh_reviewed_candidate'] = candidate
    packet['current_frame_difference_analysis'] = dict(status='terminal_direct_poll_fixed_input_and_feedback_route_reviewed',
                                                      fresh_comparison=str(out/'fresh-comparison.json'), fixed_prefix=fixed,
                                                      differing_video_frames=counts['video_sha256'], same_input_stream=False,
                                                      scope=comparison['scope'])
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True, current_source_reply_verified=False)
    save(out/'current-status-packet.json', packet)
    shutil.copy2(__file__, out/'publisher-source.py')
    shutil.copy2(report_path, out/report_path.name)
    viewer = ROOT/'scripts/show_native_status_v2.py'
    shutil.copy2(viewer, out/viewer.name)
    deps = {str(p):sha(p) for p in out.rglob('*') if p.is_file()}
    deps[str(report_path)] = sha(report_path)
    for name in ['derived_disc', 'component', 'derived_stage', 'patch_manifest']:
        deps[b[name]] = sha(b[name])
    pub = V/'native-scene17-direct-poll-fresh-reviewed-v1-current.json'
    atomic(pub, dict(status=scene['status'], directory=str(out), report=str(report_path), new_predictions=0,
                     new_training=False, whole_objective_complete=False, dependencies_sha256=deps))
    wrapper.update(packet=str(out/'current-status-packet.json'), dependencies_sha256={**wrapper['dependencies_sha256'], **deps, str(pub):sha(pub)})
    atomic(wp, wrapper)
    for path, digest in wrapper['dependencies_sha256'].items():
        source = Path(path)
        assert source.is_relative_to(ROOT)
        dest = P/'workbench'/source.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.is_file() or sha(dest) != digest:
            subprocess.run(['/bin/cp', '-c', str(source), str(dest)], check=True, capture_output=True)
    shutil.copy2(wp, P/'workbench'/wp.relative_to(ROOT))
    shutil.copy2(viewer, P/'workbench'/viewer.relative_to(ROOT))
    for path in [ROOT/'CURRENT DECOMPILATION.txt', P/'CURRENT DECOMPILATION.txt', P/'workbench/CURRENT DECOMPILATION.txt']:
        path.write_text('CURRENT — v24 direct-poll scene completes fresh route; fidelity remains open\n'
                        f'{scene_returns:,}scene returns; {counts["video_sha256"]:,}paired video differences. Fixed-input prefix still differs194frames versus189previously. Preview unchanged.\n'
                        'Report: '+str(report_path)+'\n\nEarlier notes:\n'+path.read_text())
    print(scene['status'], str(report_path), flush=True)


if __name__ == '__main__':
    main()
