"""Preserve the verified v41 checkpoint and the human-requested paused state."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    timings = {}
    for lane in ['Root', 'copied']:
        timing = read(V / f'actor-phased-image-{lane}-status-timing.json')
        text = (V / f'actor-phased-image-{lane}-status-cli.txt').read_text()
        assert timing['exit_code'] == 0 and timing['lines'] == len(text.splitlines()) == 12
        assert all(s in text for s in ['25,024', '25,011', '6,950', '15/15', '13/13', '124/124'])
        timings[lane] = timing
    for lane in ['current', 'copied']:
        result = read(V / f'actor-phased-image-delivered-{lane}-MCP-response.json')
        assert result['status'].startswith('terminal_actual_')
    manifest = V / 'native-Deck-current-status-v1-current.json'
    wrapper = read(manifest)
    packet = read(wrapper['packet'])
    progress = packet['current_actor_phased_image_progress']
    assert progress['fresh_route_qualified'] and not progress['game_fidelity_verified'] and not progress['default_promoted']
    preservation_path = V / 'game-preservation-v2-current.json'
    preservation = read(preservation_path)
    assert preservation['status'].startswith('terminal_')
    assert all(r['all_recorded_files_match'] and not r['second_complete_copy_proven'] for r in preservation['unique_trained_exports'])
    jobs = []
    for name, script in [
        ('actor-phased-v1', 'check_actor_phased_v1.py'), ('actor-phased-fixed-v2', 'check_actor_phased_fixed_v2.py'),
        ('actor-phased-image-startup-heap-v1', 'check_actor_phased_image_startup_heap_v1.py'),
        ('actor-phased-watch-v1', 'qualify_actor_phased_watch_v1.py'),
        ('native-actor-phased-image-fresh-input-v1-candidate', 'run_actor_phased_image_input_route_v1.py'),
        ('native-actor-phased-image-fresh-input-v1-control', 'run_actor_phased_image_input_route_v1.py'),
        ('actor-phased-local-reviewer-v1', 'run_actor_phased_local_reviewer_v1.py'),
        ('game-preservation-v2', 'preserve_game_model_retention_v2.py'),
    ]:
        r = read(V / (name + '-current.json'))
        assert r['status'].startswith('terminal_') and not r.get('child_pid')
        command = subprocess.run(['ps', '-p', str(r['pid']), '-o', 'command='], capture_output=True, text=True).stdout
        assert script not in command, (name, command)
        jobs.append(dict(name=name, pid=r['pid'], status=r['status'], matching_live_process=False))
    target = V / 'goal-continuation-current.json'
    old = read(target)
    out = V / 'v41-preservation-checkpoint-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out / 'previous-goal-state.json', old)
    save(out / 'own-worker-audit.json', dict(jobs=jobs, unrelated_worker_processes_inspected=False, all_recorded_own_workers_terminal=True,
        CLI_and_MCP_QA_sessions_collected=True, live_game_inference_or_training_workers=0))
    frontend = out / 'checked-frontend.json'
    save(frontend, dict(status='terminal_status24_entry37_Root_copied_CLI_and_actual_MCP_verified', default_lines=12, CLI_timings=timings,
        concurrent_status_QA_not_inference_latency=True, new_predictions=0, new_training=False))
    next_action = ('Do not advance while paused. Preserve all work until the dedicated local-model machine is ready. '
        'Any space cleanup requires exact content/configuration in a verified retained copy; do not delete trained exports or rely on recipes/re-downloads. '
        'After explicit resume, verify latest v41 and copied-package evidence on the new machine. Update the historical Reader43 prompt before relying on generated current status; '
        'test easy native Chat/inference under the owned lease, useful local authorship/training, fixed-input and broader indoor/device/audio routes, '
        'then continue full readable CPU/GPU/DSP/firmware source-only console recovery and actual256GBhardware qualification.')
    state = dict(old)
    state.update(status='paused_preserved_v41_actor_route_pass_fidelity_and_full_goal_open', goal_status='paused', blocked=False,
        recorded_at=datetime.now(timezone.utc).isoformat(), full_objective_complete=False,
        pause_authorization=dict(thread_id='01a159fa-426f-73f3-bbfa-026d3fd27e99', user_message_id='01a15f04-b224-7402-b1f2-9195fc8b7ff4',
            request='Preserve all work from both chats and store until dedicated local-model machine is ready; verified through read_thread. Goal tool already reports paused.'),
        previous_goal_state=str(out / 'previous-goal-state.json'),
        previous_goal_turn_classification='Progress: verified and saved v40 checkpoint; completion percentage was explicitly an unmeasured low-confidence planning judgment.',
        current_turn_classification='Progress before preservation pause: coordinator phased actor dispatch/initialization,qualified prototype/fixed/task/startup/copied/observer cases,builtv41and completed/reviewed fresh25024/25011routes. All monitors clear;6950video differences/final equal/audio silent,fidelity open. Publishedstatus24/entry37Root/copiedCLIandactualMCP. LocalReviewer0predictions. Then human requested preservation;three unique game exports hash-match saved manifests,all work remains in place,and no further advancement/training/inference started.',
        current_status_manifest=str(manifest), current_status_packet=wrapper['packet'], report=progress['report'],
        current_source_component=packet['latest_source_development'], current_actor_phased_image_progress=progress,
        unqualified_actor_phased_image=progress, current_status_renderer=str(ROOT / 'scripts/show_native_status_v24.py'),
        portable_entry_version=37, current_status_default_lines=12, current_frontend_actual_review=str(frontend),
        concurrent_CLI_QA_timings=timings, current_default_Reader_version=43, current_default_Reader_current_source_approved=False,
        current_native_Chat_verified=False, new_native_UI_attempt_this_turn=False,
        current_local_reviewer=packet['current_actor_phased_local_Reviewer_progress'],
        new_disc_built=True, new_unique_original_functions_recovered_this_turn=0, new_predictions_this_turn=0,
        optimizer_updates_this_turn=0, new_training_this_turn=False, installed_preview_changed=False,
        current_context_limits=dict(fresh_route_qualified=True, whole_game_input_qualified=False, all_monitors_clear_and_quiescent=True,
            frame_acquire_header_defect_fixed_in_v40=True, actor_initialize_header_defect_fixed_in_v41=True,
            actor_C_frames_parked_across_helpers=0, static_actor_C_phase_bounds=dict(dispatch=136, initialize=156),
            static_bounds_exclude_helpers_IRQ_and_exceptions=True, all_global_stack_paths_proven=False,
            physical_console_verified=False, whole_source_only_game_rebuild=False, game_fidelity_verified=False,
            silent_audio_unresolved=True, fixed_identical_input_v41_not_yet_run=True),
        new_game_execution_this_turn=dict(new_discs=1, fresh_routes=2, candidate_frames=25024, control_frames=25011,
            both_finite_routes_completed=True, snapshot_restores=0, host_guest_RAM_writes=0, host_CPU_or_task_seeds=0,
            video_differences=6950, final_video_equal=True, final_selected_fields_equal=True, audio_silent_both=True),
        own_worker_audit=str(out / 'own-worker-audit.json'), preservation_receipt=str(preservation_path),
        preservation_resume_handoff=preservation['resume_handoff'], independent_backup_created=False,
        preservation_state='Retained in place on this Mac,including current copied package;no deletion/move. Inventory/hash verification is not an independent backup. Originating advertising chat owns destination question and duplicate archive audit.',
        space_cleanup_audit_policy='Earlier game-model-space-audit-v1 public-download candidates superseded by game-preservation-v2. Preserve every model unless exact content/configuration is verified in another retained copy;no theoretical reconstruction deletions.',
        next_action=next_action, next_actions=[next_action])
    state['do_not_repeat_completed_work'] = list(old.get('do_not_repeat_completed_work', [])) + [
        'V41 actors:1024initializer+856joint comparisons at prototype and actual linked addresses;232taskpairs/101slots,48off-on/7faultcontrols,2copiedbuilds,6startup/core+192heap pass.',
        'V41freshcandidate25024/control25011bothcomplete. AD15/15,AI13/13,Frame124/124perlane;allmonitorsclear.6950video differences/final equal,audio silent:do not promote or claim fidelity.',
        'No additional advancement/training/inference while paused. Preserve unique trained exports and all native/public models until exact retained-copy verification.',
    ]
    atomic(target, state)
    clone(target, P / 'workbench/verification' / target.name)
    for path in [*Path(preservation['directory']).rglob('*'), preservation_path, Path(__file__)]:
        if path.is_file() and '__pycache__' not in path.parts:
            clone(path, P / 'workbench' / path.relative_to(ROOT))
    save(out / 'record.json', dict(status='terminal_v41_preservation_checkpoint_recorded_goal_paused', new_predictions=0, new_training=False,
        source_sha256={str(p):sha(p) for p in [Path(__file__), manifest, Path(wrapper['packet']), preservation_path, frontend,
            *[V / f'actor-phased-image-{lane}-status-timing.json' for lane in ['Root', 'copied']],
            *[V / f'actor-phased-image-delivered-{lane}-MCP-response.json' for lane in ['current', 'copied']]]}))
    for path in out.iterdir():
        if path.is_file():
            clone(path, P / 'workbench' / path.relative_to(ROOT))
    print(state['status'], flush=True)


if __name__ == '__main__':
    main()
