"""Current six-caller evidence for the local Chat team; no execution in lookup."""
from pathlib import Path
import re
from native_deck_source_context_v9 import matches as prior_matches,read,sha
from native_deck_status_evidence_v1 import load
ROOT=Path(__file__).resolve().parent
def matches(query):return prior_matches(query)or bool(re.search(r'\b(?:0x)?(?:110d4|1142e|10734|e03a|17f14|185b2)\b|plane[- ]layout|(?:four|five|six)[- ]helper|face[- ]builder|debug[- ]overlay',query,re.I))

def snapshot():
    p=load(ROOT)
    assert p['preview_native_Deck_callers']==6 and len(p['installed_recovered_Deck_entries'])==6
    gui=read(p['GUI_review']);g=p['gameplay_comparison'];b=p['experimental_build']
    result=dict(project=p['project'],topic='deck_readable_source',authorship=p['local_C_authorship'],
        native_experimental_disc=dict(variant='native Deck six v1',disc=b['derived_disc'],disc_sha256=b['derived_disc_sha256'],
            installed_recovered_Deck_entries=p['installed_recovered_Deck_entries'],hosted_only_recovered_Deck_entries=[],
            native_code_bytes=b['resident_bytes'],total_reservation_bytes=b['reserved_bytes'],initial_heap_bytes=b['initial_heap_bytes'],
            frames=g['candidate_frames'],native_returns=g['ordinary_native_returns'],control_returns=g['same_layout_control_returns'],
            control_original_outer_returns=g['same_layout_control_original_outer_returns'],control_restores_only_outer=True,
            differing_video_frames=g['differing_video_frames'],final_video_equal=g['final_video_equal'],cycle_identity_verified=False,
            fresh_reviewed=True,default_preview_promoted=True,review=p.get('installed_preview_report',p['report'])),
        fresh_outer_trial=dict(outer_native_returns=1,outer_original_control_returns=1,inner_five_native_in_both=True,
            geometry_returns_each_lane=18,five_original_geometry_helpers_each_return=18,other_four_returns_each_lane=19,
            observed_wait_slices=55,protected_frame_checks=222,observed_stack_margin_bytes=60,
            minimum_sampled_free_heap_while_outer_active=17968,global_heap_minimum_measured=False,
            arbitrary_suspension_reentry_IRQ_verified=False),
        separate_test_preview=dict(app=gui['app'],runtime=gui['runtime'],native_Deck_callers=6,checkpoint_restored=True,fresh_boot=False,
            actual_GUI_observed=True,live_GUI_frames=gui['frames'],live_native_returns=gui['native_returns'],
            Shift_Up_sends_C_Up_verified=True,run_speed_ratio_measured=False,Deck_expected_visual_transition_verified=False,
            audible_game_audio_verified=False,headless_nonintrusion_frames=2400,
            direct_python_command=str(Path.home()/'.lmstudio/local-ai-lab/.venv/bin/python3.12')+' '+str(Path(gui['runtime'])/'scripts/run_biwn_native_keyboard_v4.py')+' --play-audio',
            launch_and_controls=dict(launch='Double-click BIWN Test Preview.app on the Desktop; click the window and press P.',
                arrows='move/turn',run='Hold C+Up or Shift+Up. Shift alias verified to send ordinary C+Up; speed ratio not measured.',
                Z='attack/read',one_then_D='Hold1 about one second, release, then holdD. Sends ordinary selection and B+C; native calls observed but expected Deck appearance unverified.',
                zero='hold0 to exit Deck',P='start/pause',Esc='close',LM_Studio_required_for_game_window=False)),
        next_source_work='Recover deeper original helper implementations and resolve the active-route timing/video differences while preserving all six native callers. Full-game source rebuilding, arbitrary suspension/reentry/IRQ and fidelity remain incomplete.',
        restoration=dict(frames_per_group=13,original_frames_per_group=16,changes_original_behavior=True),
        whole_game_complete=False,same_console_whole_game_source_rebuild_verified=False,new_training=False,
        source_publication_sha256=p['proof_sha256'],
        scope='Six recovered callers form one Deck subsystem. Fresh/control trials and checkpoint GUI have separate input and frame scopes. Retained emulator/HLE/original-helper dependencies remain. Broad Advertising/game training quality and portable migration remain open.')

    deeper=p.get('deeper_helper_recovery')
    if deeper:
        result['deeper_helper_recovery']={k:deeper[k]for k in ['recovered_entries','authorship','component_cases','host_error_cases','connected_cases','native_object_text_bytes','native_object_executed','native_disc_changed','remaining_geometry_helpers','report']}
        result['next_source_work']='Execute relocated M68000 code for recovered helpers10968,10BA4,11384 and integrate them into geometry, preserving original110D4calls and all six existing native callers. Qualify final addresses,stack/fallback/nesting and fresh candidate/control before changing preview. Remaining helpers,whole-game source rebuilding,fidelity and accepted game/Advertising training remain incomplete.'
    candidate=p.get('native_deeper_helper_candidate')
    if candidate:
        result['native_deeper_helper_candidate']={k:candidate[k]for k in ['candidate_disc','public_native_Deck_callers','internal_helper_entries','helpers_native_inside_geometry_only','helper_global_entries_redirected','installed_preview_changed','native_code_bytes','initial_heap_bytes','native_geometry_cases_each_address','retained_four_caller_cases_each_address','full_CPU_full_RAM_fallback_cases_each_address','observed_geometry_C_stack_margin_bytes','new_outer_connected_matrix_verified','new_alias_matrix_verified','fresh_candidate_gameplay_verified','report','scope']}
        for key in ['candidate_frames','control_frames','control_restores_only_geometry','differing_video_frames','final_video_equal','compiled_helper_service_returns_each','real110D4_capture_and_return_count','alias_cases','connected_cases','protected_component_frame_checks']:
            if key in candidate:result['native_deeper_helper_candidate'][key]=candidate[key]
        if 'deeper_helper_recovery'in result:
            result['deeper_helper_recovery']['standalone_object_scope']='Earlier5194byteobject was compile-only. Later native module execution is documented in native_deeper_helper_candidate.'
        result['next_source_work']=candidate['next_action']+' Whole-game source rebuilding,fidelity,game-model training acceptance and portable migration remain incomplete.'
    plane=p.get('plane_layout_recovery')
    if plane:
        result['plane_layout_recovery']={k:plane[k]for k in ['recovered_entry','authored_source','authorship','host_CPU_RAM_cases','host_bus_error_cases','deliberate_source_defects_rejected','connected_five_body_cases','prototype_geometry_cases','prototype_retained_four_caller_cases','prototype_full_CPU_RAM_fallback_cases','prototype_internal_compiled_helper_entries','maximum_observed_geometry_C_stack_bytes','observed_C_stack_margin_bytes','native_prototype_only','final_disc_integrated','new_fresh_gameplay_verified','installed_preview_changed','base_code_tests_passed','base_code_tests_total','new_training_job','training_snapshot_at','completed_optimizer_reports_at_snapshot','training_adoption_decided','report','scope']}
        for key in ['candidate_disc','candidate_disc_sha256','native_code_bytes','total_reservation_bytes','initial_heap_bytes','candidate_frames','control_frames','compiled_helper_returns_each','differing_video_frames','recorded_state_differing_frames','final_video_equal','minimum_sampled_heap_free_while_outer_active','final_heap_free','connected_six_caller_four_helper_cases','alias_cases']:
            if key in plane:result['plane_layout_recovery'][key]=plane[key]
        if plane['new_fresh_gameplay_verified']:
            result.pop('native_deeper_helper_candidate',None)
            result['latest_unpromoted_native_candidate_section']='plane_layout_recovery'
            if 'deeper_helper_recovery'in result:
                result['deeper_helper_recovery']['standalone_object_scope']='Earlier5194byteobject was compile-only. Final linked module and fresh execution are documented in plane_layout_recovery.'
            result['latest_status_native_Chat_rendering_verified']=False
        result['new_training']=plane['completed_optimizer_reports_at_snapshot']>0
        result['new_training_scope']='Experimental game-model pilot;timestamped snapshot. Adoption remains undecided. Use the progress launcher for current worker/update status.'
        result['experimental_game_model_adopted']=False
        result['next_source_work']=plane['next_action']+' Full-game recovery,fidelity and portable migration remain incomplete.'
    faces=p.get('geometry_faces_recovery')
    if faces:
        result['geometry_faces_recovery']=faces
        result['latest_unpromoted_native_candidate_section']='geometry_faces_recovery'
        result['next_source_work']=faces['next_action']+' Full-game source rebuilding,fidelity and portable migration remain incomplete.'
        result['latest_status_native_Chat_rendering_verified']=False
    debug=p.get('debug_overlay_recovery')
    if debug:
        result['debug_overlay_recovery']=debug
        result['next_source_work']='Correct native execution overhead/timing while preserving CPU/RAM/entry contracts. Integrate the newly qualified10734caller and its real dependencies into the native module with stack/capture/fallback/nesting/fresh gates. The new10734target object remains compile-only. Whole-game rebuilding,fidelity and portable migration remain incomplete.'
    training=p.get('game_geometry_training_review')
    if training:
        result['game_geometry_training_review']=training
        result['new_training']=True
        result['new_training_scope']='The 64-update pilot completed; selected adapter passed 0/4 original code tests and remains unpromoted. Header-filename ambiguity is recorded. Separate paired clarified prompts use unchanged acceptance gates; inspect the progress launcher for their status.'
        if training.get('clarified_diagnostic_complete'):
            result['new_training_scope']='The 64-update pilot and separate filename-clarified paired diagnostic completed. Base and selected adapter each passed 0/4 tasks in both runs; all clarified outputs used the correct available headers. Adapter remains unpromoted. Further local compiler-feedback development is separate from this frozen comparison.'
        result['experimental_game_model_adopted']=False
    native_alu=p.get('native_alu_optimization')
    if native_alu:
        result['native_alu_optimization']=native_alu
        result['latest_unpromoted_native_candidate_section']='native_alu_optimization'
        result['next_source_work']=native_alu['next_action']
        result['latest_status_native_Chat_rendering_verified']=False
    latest=p.get('latest_native_candidate')
    if latest:
        result['latest_native_candidate']=latest
        result['latest_unpromoted_native_candidate_section']='latest_native_candidate'
        result['next_source_work']=latest['next_action']
        result['latest_status_native_Chat_rendering_verified']=False
    if 'latest_local_source_generation_trial'in p:result['latest_local_source_generation_trial']=p['latest_local_source_generation_trial']
    for current_key in ['game_portable_progress','current_frame_difference_analysis','native_geometry_timing_finding','native_clear_casts_performance','native_multiply_progress','native_scene_reset_progress','native_input_optimization_progress','native_input_disc_progress','native_scene_draw_progress','native_display_list_progress','native_scene_dispatch_headroom_progress','local_scene_clear_development_progress','local_scene_draw_progress','local_scene_reset_flags_progress','latest_source_development','copied_game_training_progress','current_copied_Reader_progress']:
        if current_key in p:result[current_key]=p[current_key]
    if p.get('game_portable_progress'):
        result['next_source_work']='Resolve remaining gameplay differences and finish whole-game source recovery. Current portable offline gates pass;nativeChat workspace/socket migration,new moved-package inference/training and broader model-quality verification remain incomplete. Qualify the target-tested local function for final native stack/resource/performance constraints before disc use.'
    if p.get('portable_native_Chat_progress'):
        chat=p['portable_native_Chat_progress']
        result['portable_native_Chat_progress']={key:chat[key]for key in ['status','chat_title','actual_predictions','native_Chat_transport_migrated','native_Chat_rendering_verified','copied_model_resource_inference_tested','Reviewer_words','requested_max_words','final_word_limit_pass','report']}
        result['next_source_work']='Continue original-game source recovery and resolve gameplay differences. Native Chat now renders three actual roles from copied context;enforce output limits and qualify copied-model inference/training when the shared slot is free. The target-tested local function still needs final native ABI/stack/resource/performance checks before disc use.'
    if p.get('portable_copied_reader_progress'):
        reader=p['portable_copied_reader_progress']
        result['portable_copied_reader_progress']={key:reader[key]for key in ['status','report','copied_model_resource_inference_tested','copied_model_key','new_predictions','native_Chat_copied_weight_inference_tested','broader_model_quality_approved']}
        result['next_source_work']='Copied weights now run through the repaired portable Reader. Copied training, nativeChat using copied weights and broader quality remain unverified. Continue whole-game source recovery and optimize native geometry timing;the local10968body passes shared-native component checks but costs about2.9times the optimized clear loop and remains outside the disc.'
    if p.get('native_geometry_timing_finding'):
        result['next_source_work']+=' Read-only fresh timelines show14frames accumulated delay across18native geometry calls;following resourceflags and maininputrelease shift14frames. Optimize this measured bottleneck while preservingCPU/RAM/bus-order gates;62video differences remain unapproved.'
    if p.get('native_clear_casts_performance'):
        result['next_source_work']=p['latest_native_candidate']['next_action']
    if p.get('copied_game_training_progress'):
        result['new_training_scope']='Two fresh copied-runtime LoRA updates completed with full examples and unchanged base weights. This proves training capability;no adapter was enabled or answer quality established. The earlier64updatepilot remains separate and unpromoted.'
        result['next_source_work']='Continue whole-game source recovery and resolve the latest candidate gameplay differences. Reduce the E540 native entry cost before any global game-image redirect. Copied-runtime inference and two-update training capability are verified; native Chat using copied weights and useful training quality remain open.'
        result['scope']='The installed checkpoint preview and separate experimental disc have distinct evidence. Retained emulator/HLE/original-helper dependencies, whole-game rebuilding, fidelity and future-hardware capacity remain incomplete. Copied-runtime capability checks do not establish training quality.'
    if p.get('native_scene_reset_progress'):
        reset=p['native_scene_reset_progress']
        if reset.get('experimental_disc_internal_reset_installed') and reset.get('required_reset_path_observed'):
            result['next_source_work']=p['latest_native_candidate']['next_action']
        else:
            result['next_source_work']='Qualify the new1102A scene-reset component at final image addresses,nested input/observer boundaries and fresh reset gameplay before disc adoption. Preserve the raw local Author/Repair failures and explicit coordinator SR-mask correction. Whole-game recovery,fidelity,copied-weight nativeChat and useful training quality remain open.'
    if p.get('native_input_optimization_progress'):
        result['next_source_work']=p['native_input_optimization_progress']['next_action']
    if p.get('native_scene_draw_progress'):
        result['next_source_work']=p['native_scene_draw_progress']['next_action']
    if p.get('native_display_list_progress'):result['next_source_work']=p['native_display_list_progress']['next_action']
    if p.get('native_scene_dispatch_headroom_progress'):result['next_source_work']=p['native_scene_dispatch_headroom_progress']['next_action']
    result['new_training']=False
    return result

def compact_snapshot():
    full=snapshot()
    if 'latest_native_candidate'not in full:return full
    keys=['project','topic','authorship','native_experimental_disc','separate_test_preview','latest_native_candidate','latest_unpromoted_native_candidate_section','debug_overlay_recovery','game_geometry_training_review','latest_local_source_generation_trial','experimental_game_model_adopted','whole_game_complete','same_console_whole_game_source_rebuild_verified','new_training','new_training_scope','game_portable_progress','portable_native_Chat_progress','portable_copied_reader_progress','native_geometry_timing_finding','native_clear_casts_performance','native_multiply_progress','native_scene_reset_progress','native_input_optimization_progress','native_input_disc_progress','native_scene_draw_progress','native_display_list_progress','native_scene_dispatch_headroom_progress','local_scene_clear_development_progress','local_scene_draw_progress','local_scene_reset_flags_progress','latest_source_development','copied_game_training_progress','current_copied_Reader_progress','current_frame_difference_analysis','latest_status_native_Chat_rendering_verified','source_publication_sha256','next_source_work','restoration','scope']
    return {key:full[key]for key in keys if key in full}
