"""Freeze v26 clear/fresh/fixed-input and rejected local trial evidence."""
import shutil, subprocess
from pathlib import Path
from datetime import datetime, timezone
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic


def main():
    wp = V/'native-Deck-current-status-v1-current.json'
    wrapper = read(wp)
    for path, digest in wrapper['dependencies_sha256'].items():
        assert sha(path) == digest, path
    stems = ['native-scene17-clear-disc-build-v1', 'native-Deck-scene17-clear-final-v1',
             'scene17-clear-final-bridge-v1', 'scene17-clear-final-fallback-v1',
             'scene17-clear-final-reentry-v1', 'scene17-clear-final-public-bus-v1',
             'scene17-clear-input-face-alias-v1', 'native-deck-alias-nesting-scene17-clear-final-v1',
             'native-scene17-clear-geometry-alias-v1', 'native-Deck-outer-connected-scene17-clear-v1',
             'scene17-clear-geometry-observer-qualified-v1', 'outer-scene17-clear-geometry-observer-qualified-v1',
             'shared-Deck-region-check-scene17-clear-v1', 'scene17-clear-shared-observer-qualified-v1',
             'scene17-clear-shared-observer-actual-CPU-v2', 'scene17-clear-reset-observer-qualified-v1',
             'scene17-clear-observer-actual-CPU-v1', 'scene17-clear-copied-rebuild-v1',
             'scene17-clear-fixed-prefix-review-v1','scene-clear-structured-host-v1','scene17-clear-commit-observer-v1','scene17-clear-rotation-commit-observer-v1']
    proofs = {name: read(V/(name+'-current.json')) for name in stems}
    for name, proof in proofs.items():
        assert proof['status'].startswith('terminal_') and 'failed' not in proof['status'], name
        for key in ['source_sha256', 'copied_source_sha256', 'files_sha256']:
            for path, digest in proof.get(key, {}).items():
                assert sha(path) == digest, (name, path)
    b = proofs[stems[0]]
    assert sha(b['derived_disc']) == b['derived_disc_sha256']
    scene_proof = proofs[stems[2]]
    assert scene_proof['completed'] == 772 and scene_proof['maximum_C_stack_bytes'] == 156
    assert scene_proof['deployed_module_byte_identity'] and scene_proof['actual_completion_read_counts_match']
    assert scene_proof['original_rotation_instructions_executed']==0 and scene_proof['native_rotation_calls']>0
    assert scene_proof['original_clear_instructions_executed']==0 and scene_proof['native_clear_calls']>0
    assert scene_proof['actual_clear_read_counts_match'] and scene_proof['ordered_MMIO_matches']
    assert [proofs[name]['completed'] for name in stems[3:10]] == [384, 64, 14, 256, 256, 128, 128]
    jobs = {lane: read(V/f'native-scene17-clear-fresh-v2-{lane}-current.json') for lane in ['candidate', 'control']}
    reports = {}
    for lane, job in jobs.items():
        assert job['status'] == 'terminal_fresh_scene17_route_pending_review', (lane, job['status'])
        assert job['snapshot_restores'] == job['host_guest_RAM_writes'] == job['host_CPU_or_task_seeds'] == 0
        for path, digest in job['source_sha256'].items():
            assert sha(path) == digest, (lane, path)
        assert sha(job['report']) == job['report_sha256']
        reports[lane] = read(job['report'])
        for name in ['shared', 'face', 'geometry', 'outer', 'reset', 'rotation', 'clear']:
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
    samples = read(sample_dir/'cases.json')[-4:-2]
    clear_samples = read(sample_dir/'cases.json')[-2:]
    assert [x['long_clear_polls'] for x in clear_samples] == [512,1024]
    clear_slope=(clear_samples[1]['native_instructions']-clear_samples[0]['native_instructions'])/512
    assert clear_slope==3
    assert [x['long_completion_polls'] for x in samples] == [512, 1024]
    slope = (samples[1]['native_instructions']-samples[0]['native_instructions'])/512
    assert slope == 2
    out = V/'native-scene17-clear-fresh-reviewed-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
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
    fixed = proofs['scene17-clear-fixed-prefix-review-v1']
    scene_returns = jobs['candidate']['shared_observation']['native_returns'][5]
    helper_returns = jobs['candidate']['shared_observation']['helper_returns'][5]
    control_calls = jobs['control']['shared_observation']['public_entries'][5]
    rotation = jobs['candidate']['rotation_observation']
    assert rotation['entries']==rotation['returns']==rotation['helper_entries']==rotation['helper_returns']>0
    clear=jobs['candidate']['clear_observation']
    assert clear['entries']==clear['returns']==rotation['returns']>0
    assert jobs['control']['clear_observation']['entries']==jobs['control']['rotation_observation']['entries']==0
    assert jobs['candidate']['retained_observation']['errors']==jobs['control']['retained_observation']['errors']==0
    fixed_video = fixed['comparisons']['clear']['video_sha256']
    fixed_control = fixed['new_control_versus_prior_layout']['video_sha256']
    report_path = ROOT/'reports/BIWN Native Clear Submission and Gameplay Review.txt'
    report_path.write_text(
        'BIWN — structured native clear submission, v26\n\n'
        f'Candidate/control complete {len(a):,}/{len(c):,} fresh frames. All {scene_returns:,} native scene and {helper_returns:,} captured-helper calls return. '
        f'Native clear and rotation each complete {clear["returns"]:,} calls. Rotation retains original185B2. All shared, face, geometry, outer, reset, clear and rotation monitors finish clear and quiescent. No snapshots or host RAM/CPU/task repair.\n\n'
        f'The feedback-navigation routes differ on {counts["video_sha256"]:,} paired video frames and {counts["held_buttons"]:,} held-input samples. '
        f'Final video equal:{comparison["final_video_equal"]}; final selected game fields equal:{final_selected_equal}. '
        'Different feedback inputs prevent attributing later differences solely to the helper or timing. Both audio captures contain zero nonzero samples: sound fidelity remains unproved.\n\n'
        f'Identical frontend input schedule over1,000frames: {fixed_video["count"]} differing video frames, first{fixed_video["first_frame"]}. '
        f'The v26 original-scene control differs from the prior v25control on{fixed_control["count"]}video frames, first{fixed_control["first_frame"]}. '
        'Earlier v23/v24/v25pairs had189/194/444differences in their own layouts. Boot-copy size and heap layout change; these cross-build counts do not isolate speed or fidelity improvements. Prefix cutoffs retain raw pending/end-arena observations and independent fences; they are not whole-route acceptance.\n\n'
        'E03A clear now executes structured native code inside the scene caller. Original unbounded MOVE.L/LSR.W/BCC blitter-ready polling preserves the successful X=1. '
        'Eight ordered MOVE.L MMIO stores include an explicit MOVE for zero to avoid the compiler introducing a CLR dummy read. MOVEM-style savedD0and logical flags/stack/argument effects are preserved. '
        f'The global originalE03Aentry remains intact and ran{clear['original_global_returns']}times from other callers in this route. Global17F14also remains intact. '
        'This is coordinator integration of an already recovered reference: zero new unique original routines, one additional structured native helper. Original185B2, geometry/projection/draw and other game code plus GPU/DSP/device/HLE dependencies remain.\n\n'
        'Host proof:256original pinned68000/Unicorn/fullCPU/2MBRAM/private-stack/ordered-access comparisons plus14guards. Exact deployed module:772scene cases,384fallback,64nested-scene and14public-bus checks; peak scene C stack156of208bytes. '
        'Controlled busy values are injected only into the destination register after an actual native clear MOVE read; actual MMIO read addresses/counts/order and write values compare. Read values are not recorded by the native trace. '
        'Completion polling adds2instructions per additional busy read; clear polling adds3in controlled512/1024samples. These are instruction deltas, not physical cycles or a game speedup. '
        'Retained4992plus16fallbacks, geometry256, all8final-image gates, aliases256+256+128 and connected128pass. Shared observer512actual lanes, geometry64, reset64pairs, clear55calls/19corruptions and rotation55calls/20corruptions pass. '
        'Finite normal-call proofs do not establish arbitrary IRQ/intermediate logical-state or physical-console fidelity.\n\n'
        'Shared module46,578bytes; linked native code87,408bytes; initial heap122,496bytes; reservation275,392bytes; boot copy113,792bytes. Existing arenas are reused. Copied source/SDK rebuild is byte-identical.\n\n'
        'Local model:3actual predictions using the copied27B6bit daily model, Author/Repair/advisory Reviewer. Author13.84s failed compilation; Repair14.52s compiled but failed CPU/stack/RAM/order. '
        'Neither body is in the image; no native model-body execution followed the failed host gate. Reviewer pass/training/promotion booleans agree, but prose claims no provided results despite explicit failed gates and remains unapproved. '
        'Exact prompts, raw responses and first counterexample are preserved in the separate local review. This supplied-primitive development trial is not an untouched benchmark, training or useful quality gain. No optimizer updates. Native Chat using these copied weights remains unverified. Desktop preview unchanged.\n\n'
        'Next: diagnose fixed-input execution/video differences and remove more original scene dependencies; improve verifier feedback and primitive/addressing scaffolding for a new local development trial. Whole-game readable source, a complete same-console rebuild, audio/IRQ fidelity, useful training quality and physical Jaguar CD boot remain unfinished.\n\n'
        'Experimental disc: '+b['derived_disc']+'\nFull route comparison: '+str(out/'fresh-comparison.json')+'\n')
    previous_scene = dict(packet['native_scene_draw_progress'])
    scene = dict(previous_scene)
    scene.pop('previous_wait_profile',None)
    scene.update(status='terminal_scene17_clear_fresh_pass_fidelity_open', profile='deck-shared-v26-scene-clear',
                 previous_scene_review=str(V/'native-scene17-rotation-fresh-reviewed-v1-current.json'), latest_fresh_result_is_passing_route=True,
                 experimental_disc=b['derived_disc'], experimental_disc_sha256=b['derived_disc_sha256'],
                 prototype_module_bytes=46578, final_module_bytes=46578, native_code_bytes=87408,initial_heap_bytes=122496,shared_bridge_C_stack_bytes=156,shared_bridge_cases=772,native_clear_integrated=True,native_clear_returns=clear['returns'],native_rotation_integrated=True,native_rotation_returns=rotation['returns'],original185B2_retained=True,
                 fresh_scene_native_entries=scene_returns, fresh_scene_native_returns=scene_returns,
                 fresh_scene_helper_returns=helper_returns, fresh_scene_original_control_calls=control_calls,
                 candidate_frames=len(a), control_frames=len(c), fresh_differing_video_frames=counts['video_sha256'],
                 held_input_differing_frames=counts['held_buttons'], final_video_equal=comparison['final_video_equal'],
                 final_selected_game_fields_equal=final_selected_equal, identical_frontend_inputs=False,
                 source_semantic_vs_timing_cause_proven=False, new_disc_fresh_gameplay_tested=True,
                 new_disc_fresh_route_completed=True, new_disc_fidelity_verified=False, cost_approved=False,
                 clear_poll_instructions_per_extra_busy_read=clear_slope,direct_poll_instructions_per_extra_busy_read=slope, fixed_input_comparison=fixed['comparisons'],
                 fixed_input_fidelity_resolved=False,fixed_input_control_layout_changes=fixed['new_control_versus_prior_layout'], installed_preview_changed=False, report=str(report_path),
                 next_action='Diagnose fixed-input/video execution differences and reconstruct more original scene dependencies; improve local model primitive/addressing scaffolding and detailed verifier feedback. Whole-game source rebuilding, useful training quality, audio/IRQ fidelity and physical-console validation remain incomplete.')
    packet['native_scene_draw_progress'] = packet['latest_source_development'] = scene
    local=read(V/'local-scene-clear-worker-reviewed-v1-current.json')
    assert local['new_predictions']==3 and local['accepted_complete_functions']==0
    packet['local_scene_clear_development_progress']=local
    scene['local_development_review']=local['review_file']
    candidate = dict(packet['latest_native_candidate'])
    packet['previous_native_candidate_before_clear'] = dict(candidate)
    candidate.update(status=scene['status'], variant='readable scene, clear submission and buffer rotation plus retained native callers, v26',
                     directory=str(out), candidate_disc=b['derived_disc'], candidate_disc_sha256=b['derived_disc_sha256'],
                     native_module=scene_proof['payload'], native_module_sha256=scene_proof['payload_sha256'],
                     native_module_bytes=46578, native_code_bytes=87408,candidate_initial_heap_bytes=122496,native_scene_prototype_C_stack_bytes=156,native_scene_internal_helpers=['0x17f14','0xe03a'],total_internal_compiled_helpers=9,native_clear_returns=clear['returns'],native_rotation_returns=rotation['returns'], total_reservation_bytes=b['component_bytes'],
                     candidate_frames=len(a), control_frames=len(c), differing_video_frames=counts['video_sha256'],
                     held_button_differing_frames=counts['held_buttons'], final_video_equal=comparison['final_video_equal'],
                     final_selected_game_fields_equal=final_selected_equal, native_scene_returns=scene_returns,
                     native_scene_helper_returns=helper_returns, new_fresh_gameplay_verified=True,
                     fresh_route_completed=True, native_disc_qualified=False, native_disc_fidelity_verified=False,
                     scene_C_stack_low_offset=jobs['candidate']['shared_observation']['C_stack_low_offsets'][5],
                     installed_preview_changed=False, report=str(report_path), scope=comparison['scope'], next_action=scene['next_action'])
    tracked=[key for key in fields if key not in ['video_sha256','navigation']]
    candidate.update(candidate_trial_frames=len(reports['candidate']['ordinary_Deck_input_trial']['inputs']),
                     control_trial_frames=len(reports['control']['ordinary_Deck_input_trial']['inputs']),
                     recorded_state_fields=tracked,recorded_state_differing_frames=len(set().union(*(set(compared[key]['differing_frames'])for key in tracked))),
                     C_range_legal_controls=proofs['scene17-clear-shared-observer-qualified-v1']['C_floor_legal_controls'],
                     C_range_outside_fault_controls=proofs['scene17-clear-shared-observer-qualified-v1']['C_floor_rejected_controls'])
    packet['latest_native_candidate'] = packet['latest_fresh_reviewed_candidate'] = candidate
    packet['current_frame_difference_analysis'] = dict(status='terminal_clear_fixed_input_and_feedback_route_reviewed',
                                                      fresh_comparison=str(out/'fresh-comparison.json'), fixed_prefix=fixed,
                                                      differing_video_frames=counts['video_sha256'], same_input_stream=False,
                                                      scope=comparison['scope'])
    packet['installed_preview_report']=packet.get('installed_preview_report',packet['report'])
    packet['report']=str(report_path)
    summary=(f'V26native clear and rotation completes {len(a):,}/{len(c):,}fresh candidate/control frames; {rotation["returns"]:,}native clear and rotation returns each. All monitors clear. {counts["video_sha256"]:,}paired video differences remain; final video equal:{comparison["final_video_equal"]}. Identical-input1000frame prefix differs{fixed_video["count"]}frames, with{fixed_control["count"]}control-layout differences versus the earlier image. Fidelity remains open. Original185B2and other dependencies remain; preview unchanged, full game and useful trained-model quality incomplete.')
    for key in ['checked_current_summary','checked_answer','current_verified_route_summary']:packet[key]=summary
    packet['milestone']='Partial native clear and rotation integrated; whole game and fidelity remain open'
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True, current_source_reply_verified=False)
    save(out/'current-status-packet.json', packet)
    shutil.copy2(__file__, out/'publisher-source.py')
    shutil.copy2(report_path, out/report_path.name)
    viewer = ROOT/'scripts/show_native_status_v2.py'
    shutil.copy2(viewer, out/viewer.name)
    for lane in ['candidate','control']:
        prefix=read(V/f'scene17-clear-fixed-prefix-v4-{lane}-current.json')
        subprocess.run(['/bin/cp','-cR',prefix['directory'],str(out/('fixed-prefix-'+lane))],check=True,capture_output=True)
    local_dir=Path(local['directory'])
    subprocess.run(['/bin/cp','-cR',str(local_dir),str(out/'local-model-trial')],check=True,capture_output=True)
    save(out/'local-model-review.json',local)
    shutil.copy2(local['report'],out/Path(local['report']).name)
    deps = {str(p):sha(p) for p in out.rglob('*') if p.is_file()}
    deps[str(report_path)] = sha(report_path)
    for name in ['derived_disc', 'component', 'derived_stage', 'patch_manifest']:
        deps[b[name]] = sha(b[name])
    pub = V/'native-scene17-clear-fresh-reviewed-v2-current.json'
    atomic(pub, dict(status=scene['status'], directory=str(out), report=str(report_path), new_predictions=3,
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
        path.write_text('CURRENT — v26 native clear and rotation complete fresh route; fidelity remains open\n'
                        f'{scene_returns:,}scene returns; {counts["video_sha256"]:,}paired video differences. Fixed-input prefix differs{fixed_video["count"]}frames; control layouts also differ. Preview unchanged.\n'
                        'Report: '+str(report_path)+'\n\nEarlier notes:\n'+path.read_text())
    print(scene['status'], str(report_path), flush=True)


if __name__ == '__main__':
    main()
