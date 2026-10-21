"""Record v40 source progress and failed gameplay without promoting the image."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    timings = {}
    for lane in ['Root', 'copied']:
        timing = read(V / f'frame-phased-image-{lane}-status-timing.json')
        text = (V / f'frame-phased-image-{lane}-status-cli.txt').read_text()
        assert timing['exit_code'] == 0 and timing['lines'] == 12
        assert len(text.splitlines()) == 12
        assert all(s in text for s in ['75/75', '34,619', '25,015', '2/6/26', '184'])
        timings[lane] = timing
    for lane in ['current', 'copied']:
        result = read(V / f'frame-phased-image-delivered-{lane}-MCP-response.json')
        assert result['status'].startswith('terminal_actual_')
    manifest = V / 'native-Deck-current-status-v1-current.json'
    wrapper = read(manifest)
    packet = read(wrapper['packet'])
    progress = packet['current_frame_phased_image_progress']
    assert not progress['default_promoted'] and not progress['fresh_route_qualified']
    assert progress['candidate_Frame_calls'] == progress['candidate_Frame_returns'] == 75
    assert progress['candidate_Frame_errors'] == progress['candidate_Frame_stack_outside'] == 0
    header_path = V / 'v40-actor-init-header-fault-reviewed-v1-current.json'
    header = read(header_path)
    assert not header['fix_implemented']
    jobs = []
    for name, script in [
        ('frame-phased-image-qualification-pipeline-v3', 'run_frame_phased_image_qualification_pipeline_v3.py'),
        ('native-frame-phased-image-fresh-input-v1-candidate', 'run_frame_phased_image_input_route_v1.py'),
        ('native-frame-phased-image-fresh-input-v1-control', 'run_frame_phased_image_input_route_v1.py'),
        ('v40-input-transition-fault-trace-v1', 'trace_v40_input_transition_fault_v1.py'),
        ('v40-input-transition-fault-trace-v2', 'trace_v40_input_transition_fault_v2.py'),
        ('frame-phased-local-reviewer-v1', 'run_frame_phased_local_reviewer_v1.py'),
    ]:
        receipt = read(V / (name + '-current.json'))
        assert receipt['status'].startswith('terminal_') and not receipt.get('child_pid')
        command = subprocess.run(['ps', '-p', str(receipt['pid']), '-o', 'command='], capture_output=True, text=True).stdout
        assert script not in command, (name, command)
        jobs.append(dict(name=name, pid=receipt['pid'], status=receipt['status'], matching_live_process=False))
    target = V / 'goal-continuation-current.json'
    old = read(target)
    out = V / 'frame-phased-image-goal-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out / 'previous-goal-state.json', old)
    save(out / 'own-worker-audit.json', dict(jobs=jobs, unrelated_jobs_inspected=False, all_recorded_own_workers_terminal=True))
    frontend = V / 'frame-phased-image-checked-frontend-v1.json'
    save(frontend, dict(status='terminal_status23_entry36_Root_copied_CLI_and_actual_MCP_verified', default_lines=12, CLI_timings=timings, concurrent_status_QA_not_inference_latency=True, new_predictions=0, new_training=False))
    next_action = ('Phase actor dispatch and actor initialization so their C frames are released before original geometry/task/helper calls. '
        'Preserve original arguments, flags, public save frames, volatile memory order and task-create behavior. '
        'Reproduce the captured actor task+520 entry and 2/6/26-byte header corruption counterexample, qualify the complete nested chain and copied rebuild, '
        'then build a separate candidate and rerun changed-code fresh routes. Preserve reviewed v34, failed v37/v38/v39/v40 and the Desktop preview. '
        'Continue full source-only CPU/GPU/DSP/firmware/audio/fidelity/console recovery, useful trained gain, native Chat/easy inference and future 256GB qualification.')
    state = dict(old)
    state.update(
        status='active_v40_frame_phased_fix_qualified_fresh_actor_init_header_defect_identified',
        recorded_at=datetime.now(timezone.utc).isoformat(), goal_status='active', full_objective_complete=False, blocked=False,
        previous_goal_state=str(out / 'previous-goal-state.json'),
        current_turn_classification='Progress: phased frame source and actual v40 integration pass finite component/provider/startup/copied/observer checks. Fresh candidate fails; all 75 Frame calls return with zero Frame errors. Actor-init header corruption independently reproduced; not fixed. Status23/entry36 CLI and actual MCP verified. Zero predictions/weights; preview unchanged.',
        current_status_manifest=str(manifest), current_status_packet=wrapper['packet'], report=progress['report'],
        current_source_component=packet['current_native_input_prototype_progress'],
        current_frame_phased_image_progress=progress, unqualified_frame_phased_image=progress,
        new_disc_built=True, new_predictions_this_turn=0, optimizer_updates_this_turn=0, new_training_this_turn=False,
        new_unique_original_functions_recovered_this_turn=0, installed_preview_changed=False,
        current_status_renderer=str(ROOT / 'scripts/show_native_status_v23.py'), portable_entry_version=36,
        current_status_default_lines=12, current_frontend_actual_review=str(frontend), concurrent_CLI_QA_timings=timings,
        current_native_Chat_verified=False, new_native_UI_attempt_this_turn=False,
        current_default_Reader_version=43, current_default_Reader_current_source_approved=False,
        current_actor_initialize_header_fault=header,
        current_local_reviewer=read(V / 'frame-phased-local-reviewer-v1-current.json'),
        own_worker_audit=str(out / 'own-worker-audit.json'),
        new_game_execution_this_turn=dict(new_discs=1, fresh_routes=2, fresh_candidate_frames=34619, fresh_control_frames=25015,
            candidate_fresh_route_qualified=False, control_fresh_route_completed=True, diagnostic_fresh_replays=2,
            diagnostic_stop_frames=[9279, 8978], isolated_actor_header_instruction_steps=3, unique_full_game_paths_added=False),
        current_context_limits=dict(observer_qualified=True, finite_final_address_gates_qualified=True,
            fresh_gameplay_qualified=False, fresh_native_input_transition_failed=True,
            frame_acquire_header_defect_fixed_in_v40=True, frame_candidate_calls_returned=75,
            frame_candidate_stack_errors=0, frame_C_phase_static_bound=184, static_bound_excludes_helpers_and_IRQ=True,
            all_global_stack_paths_proven=False, actor_init_entry_SP_above_task=520, actor_init_gap_bytes=448,
            actor_init_context_above_task=40, isolated_actor_header_bytes_overwritten_cumulative=[2, 6, 26],
            actor_init_header_defect_fixed=False, all_failure_causes_resolved=False,
            first_actor_stack_fault_frame=8978, diagnostic_first_odd_PC=0x19, candidate_end_exception_loop_PC=0x23),
        local_model_review='Exact local Reviewer prompt/schema/source evidence saved. Shared lease unavailable before catalog/generation; zero predictions or optimizer updates. Coordinator authored source and checks; no independent review or current native Chat verification.',
        user_facing_completion_estimate=dict(range_percent=[20, 30], confidence='low', measured_code_coverage=False,
            scope='Complete readable decompilation with same-console source rebuild',
            basis='Qualitative planning judgment only; no verified whole-game coverage denominator. Preview playability is a separate milestone.'),
        next_action=next_action, next_actions=[next_action],
    )
    state['do_not_repeat_completed_work'] = list(old.get('do_not_repeat_completed_work', [])) + [
        'v40 finite component/image/task/copied/31-gate preflight and read-only observer checks are terminal; reuse unchanged proof scopes by exact identity.',
        'v40 fresh candidate34619 fails/control25015 completes. Diagnostics9279/8978 and isolated actor-init stores expose the next defect; require changed code or a new unresolved question before replay.',
        'Frame75/75 returns with zero Frame errors; do not repeat the failed old512-gap wrapper or reduce actor gaps without proving nested lifetimes.',
        'Status23/entry36 Root/copied CLI and actual MCP pass. Reviewer lease unavailable: zero predictions; no unrelated job inspection.',
    ]
    atomic(target, state)
    clone(target, P / 'workbench/verification' / target.name)
    save(out / 'record.json', dict(status='terminal_progress_recorded_goal_active', new_predictions=0, new_training=False,
        dependencies_sha256={str(p): sha(p) for p in [Path(__file__), manifest, Path(wrapper['packet']), header_path, frontend,
            *[V / f'frame-phased-image-{lane}-status-timing.json' for lane in ['Root', 'copied']],
            *[V / f'frame-phased-image-delivered-{lane}-MCP-response.json' for lane in ['current', 'copied']]]}))
    print(state['status'], flush=True)


if __name__ == '__main__':
    main()
