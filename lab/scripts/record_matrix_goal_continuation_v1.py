"""Record active full-scope goal progress after current transport verification."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    for name in ['record-matrix-final-v34-delivered-current-MCP-response.json','record-matrix-final-v34-delivered-copied-MCP-response.json']:
        g=read(V/name);assert g['status'].startswith('terminal_actual_')
    audit=read(V/'record-matrix-prefix-worker-terminal-audit-v1-current.json');assert audit['all_inspected_job_handles_missing_now']
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp);packet=read(wrapper['packet'])
    assert packet['latest_native_candidate']['native_record_matrix_returns']==0
    assert packet['record_matrix_fresh_progress']['native_record_matrix_returns']==190
    assert packet['native_geometry_records_progress']['current_fixed_input_video_comparison']['count']==450
    out=V/'record-matrix-goal-continuation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    path=V/'goal-continuation-current.json';g=read(path);save(out/'previous-goal-state.json',g)
    g.update(status='active_v34_fresh_matrix_path_and_identical_input_timing_onset_verified_full_game_and_useful_training_open',
        recorded_at=datetime.now(timezone.utc).isoformat(),prior_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification='Progress:read-only matrix watcher1152synthetic controls/128actualCPUlanes;corrected scene784negative and scene268fresh positive candidate190/control266matrix returns. Terminal review recovered and checked this continuation.',
        previous_user_support_turn_classification='Informational launcher assistance;no new game build/model training in that support reply.',
        current_turn_classification='Progress:published distinct matrix/standard scenarios to Root and copied workbench,statusv8/entry17. Two new1000frame equal-input prefixes show450video differences first378,CPU/GPU first376,heldbuttons/DSPequal. Two read-only trace replicas preserve all recorded CPU/RAM/GPU/DSP/video hashes and localize onset after identical first scene entry376;secondentry379candidate/378control. Both actual current MCP transports verified. No model generations or weight updates.',
        full_objective_complete=False,blocked=False,new_training_this_turn=False,optimizer_updates_this_turn=0,
        completed_new_local_predictions_this_turn=0,new_coordinator_authored_routines_this_turn=0,
        new_internal_native_helper_integrations_this_turn=0,new_internal_readable_helper_integrations_this_turn=0,
        new_target_implementation_optimizations_this_turn=0,new_native_source_optimization_this_turn=False,
        new_model_authored_complete_functions_this_turn=0,new_model_authored_source_blocks_verified_this_turn=0,
        new_full_fresh_route_runs_this_turn=0,new_fixed_input_prefix_runs_this_turn=2,new_readonly_timing_trace_replicas_this_turn=2,
        installed_preview_changed=False,experimental_game_model_adopted=False,ongoing_finite_workers=[],
        own_finite_worker_terminal_audit=str(V/'record-matrix-prefix-worker-terminal-audit-v1-current.json'),
        latest_matrix_coverage_gap_review=str(V/'record-matrix-268-fresh-reviewed-v1-current.json'),
        latest_matrix_fresh_coverage_verified=True,additional_matrix_route_native_returns=190,additional_matrix_route_original_returns=266,
        additional_matrix_route_candidate_frames=22536,additional_matrix_route_control_frames=22363,
        candidate_native_record_matrix_returns=0,candidate_native_record_matrix_returns_scope='Standard25012frame route only;additional268route190native calls is stored separately.',
        latest_frame_difference_analysis=str(V/'record-strides-fixed-prefix-reviewed-v1-current.json'),
        latest_scene_timing_trace_review=str(V/'record-strides-timing-reviewed-v1-current.json'),
        current_image_equal_input_prefix_verified=True,current_image_equal_input_prefix_video_differences=450,
        current_image_equal_input_prefix_frames=1000,current_image_equal_input_prefix_first_video_difference=378,
        current_image_equal_input_prefix_first_CPU_GPU_difference=376,current_image_equal_input_prefix_held_buttons_identical=True,
        current_image_timing_cause_resolved=False,current_image_audio_fidelity_verified=False,
        current_status_renderer=str(ROOT/'scripts/show_native_status_v8.py'),portable_entry_version=17,
        current_status_reader_live_generation_verified=False,current_status_reader_actual_previous_generation_verified=True,
        current_Reader_supplied_snapshot_approved=False,prior_Reader39_snapshot_approved=True,
        current_copied_weight_native_Chat_rendering_verified=False,
        UI_status='No native UI attempted this continuation. Headless work is authorized. Prior OS check reported locked;do not request unlock. No current copied-weight native Chat display claim.',
        last_live_model_slot_check_scope='Historical check retained;no model slot/inference operation performed this continuation.',
        portable_current_review=str(V/'record-matrix-current-finalization-v1-current.json'))
    g['remaining_requirements']['game']='Current v34standardroute25012/24966frames,5774scene/4777records/8567copy/0matrix;separate freshscene268route22536/22363frames,190native/266original-record matrix returns,allmonitorsclear. Finalvideo/playerfields agree on matrixroute but21803pairedvideo differences and render-batch region3/4remain. Current identical-input1000frameprefix has450video differences first378,CPU/GPU first376,heldbuttons/DSPequal,silentaudio. Tracepreservesallpriorhashes and firstsceneentryidentical376;secondscene379/378,causeunresolved. FullreadableCPU/GPU/DSP/HLEsameconsolesource-onlyrebuild,IRQ/arbitraryreentry/consolefidelity incomplete. Localv35block remains unpromotedcomponent.'
    g['remaining_requirements']['local_frontend']='Root/copied savedstatusv8/entry17 and actualMCP convey separate matrix/standard/prefix/trace scenarios. OrdinaryReader39prior138word/11.92second snapshot remains historically approved;newfacts not generated/reviewed. Currentcopiedweight nativeChat ease/display and end-to-end clicklatency remain unverified. No new localprediction or model source adoption.'
    g['remaining_requirements']['training']='Copied2updatecapability and unchangedbasehash previouslyverified;earlier64updatepilotbase0/4adapter0/4unpromoted. Zero updates thiscontinuation. Need useful training gain on untouchedtasks;promptfeedback and single supplied-facts briefings are not weighttraining/heldoutquality.'
    g['next_actions']=[packet['native_scene_draw_progress']['next_action'],
        'Use source and read-only instruction profiling to separate clear/records/rotation/display/wait costs in the first scene call. Do not guess delay compensation,mask mismatches,or equate callback ordinals with cycles.',
        'Continue remaining originalCPU/GPU/DSP/HLEreadable source and whole-game same-console source-only rebuilding,audio/IRQ/physical fidelity. v35localprologue component is separately verified but larger/unpromoted;qualify all integration gates before any adoption.',
        'Finish easy local inference and useful training evaluation:preserve unrelated loaded/busy models under sharedlease,maintain exact prompts/responses,do not repeat completed failed pilots. Copiedweight nativeChat currentrendering remainsopen;locked/headless work authorized.']
    g['do_not_restart']+=['Completed matrixwatch1152synthetic controls/128actualCPUlanes and scene784controllerfailure/correctednegative/scene268candidate190control266fresh routes;preserve receipts,no coverage replay.',
        'Completed v34fixedinput1000candidate/control prefixes and read-only timing replicas;all prior recorded hashes preserved. Additional traces/runs require a new unresolved question or changed implementation.']
    atomic(path,g);clone(path,P/'workbench/verification'/path.name)
    save(out/'delivery.json',dict(status=g['status'],goal_remains_active=True,new_predictions=0,new_training=False,proof=str(wp),proof_sha256=sha(wp),source=str(Path(__file__)),source_sha256=sha(__file__)))
    print('Active full-scope goal state saved;finite game workers terminal.',flush=True)

if __name__=='__main__':main()
