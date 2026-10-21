"""Persist measured source progress without redefining the full active goal."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    for name in ['record-loop-portable-delivered-current-MCP-response.json','record-loop-portable-delivered-copied-MCP-response.json']:
        result=read(V/name);assert result['status'].startswith('terminal_actual_')
    audit=read(V/'record-loop-worker-terminal-audit-v1-current.json');assert audit['all_inspected_handles_missing_now']
    wrapper=read(V/'native-Deck-current-status-v1-current.json');packet=read(wrapper['packet']);f=packet['latest_source_development']
    assert f['profile']=='deck-shared-v37-record-loop-advance-v2' and not f['new_disc_built']
    assert f['host_cases']==f['native_body_cases']==512 and f['host_guards']==19 and f['retained_caller_cases']==4992 and f['geometry_cases']==256
    author=read(V/'local-record-loop-advance-v1-current.json');repair=read(V/'local-record-loop-advance-repair-v1-current.json');assert author['new_predictions']==1 and repair['new_predictions']==0
    out=V/'record-loop-goal-continuation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    path=V/'goal-continuation-current.json';g=read(path);save(out/'previous-goal-state.json',g)
    g.update(status='active_v37_portable_loop_prototype_qualified_v34_gameplay_preserved_full_game_training_and_frontend_quality_open',recorded_at=datetime.now(timezone.utc).isoformat(),prior_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification='Progress:separate freshscene268matrix190/266coverage published,currentv34equalinput1000prefix450differences and read-only onsettrace narrowed firstscene cadence;all current transports verified.',
        current_turn_classification='Progress:two read-only first-scene histogram replicas preserve every earlierCPU/RAM/GPU/DSP/video hash and identify record-body overhead6166/706callbacks. Coordinator fused loop-tail prototype passes native512,scene772,widehelper131072,retained4992+16fallback,geometry256,copied54060bytebuild. C99label defect fixed in newsourcev2;host512+19pass and entire native module remainsbyte-identical,so native proofs transfer explicitly. Module74bytessmaller,body stack112versus120,eight fixtures save6304–6612emulatorcycles. One localAuthor16.92seconds failscompile;Repair prepared butzero predictions(sharedleasebusy). Both Root/copied currentMCP verify prototype/gameplay distinction.',
        full_objective_complete=False,blocked=False,ongoing_finite_workers=[],own_finite_worker_terminal_audit=str(V/'record-loop-worker-terminal-audit-v1-current.json'),
        new_training_this_turn=False,optimizer_updates_this_turn=0,completed_new_local_predictions_this_turn=1,
        generated_local_function_outputs_this_turn=1,new_model_authored_complete_functions_this_turn=0,new_model_authored_source_blocks_verified_this_turn=0,
        new_coordinator_authored_routines_this_turn=1,new_coordinator_native_primitives_this_turn=1,new_unique_original_functions_this_turn=0,
        new_internal_native_helper_integrations_this_turn=0,new_internal_readable_helper_integrations_this_turn=0,new_target_implementation_optimizations_this_turn=1,new_native_source_optimization_this_turn=True,
        new_full_fresh_route_runs_this_turn=0,new_fixed_input_prefix_runs_this_turn=0,new_readonly_timing_trace_replicas_this_turn=0,new_readonly_first_scene_profile_runs_this_turn=2,
        installed_preview_changed=False,experimental_game_model_adopted=False,candidate_profile='v34',candidate_native_disc_fidelity_verified=False,
        newer_source_prototype_profile='deck-shared-v37-record-loop-advance-v2',newer_source_prototype_disc_built=False,newer_source_prototype_fresh_gameplay_verified=False,
        newer_source_prototype_module_bytes=54060,newer_source_prototype_host_cases=512,newer_source_prototype_host_guards=19,newer_source_prototype_native_body_cases=512,newer_source_prototype_scene_cases=772,
        newer_source_prototype_copied_rebuild_identical=True,newer_source_prototype_body_C_stack=112,newer_source_prototype_connected_C_stack=168,newer_source_prototype_authorship=f['authorship'],
        newer_source_prototype_native_proof_transfer='Full54060byte module at identical prototype code/arena addresses and helper source identical betweenv1/v2;native proofs inherited,not rerun. NewhostC99source512+19actually executed.',
        newer_source_prototype_retained_cases=4992,newer_source_prototype_retained_fallback_cases=16,newer_source_prototype_geometry_cases=256,newer_source_prototype_wide_helper_cases=131072,
        newer_source_prototype_fixture_CPU_cycles_saved_min=6304,newer_source_prototype_fixture_CPU_cycles_saved_max=6612,
        latest_source_recovery_report=f['report'],latest_source_recovery_review=str(V/'record-loop-portability-reviewed-v2-current.json'),latest_source_delivery_review=str(V/'record-loop-portability-reviewed-v2-current.json'),
        latest_local_source_review=str(V/'local-record-loop-compile-v1-current.json'),previous_verified_local_prologue_component=str(V/'local-geometry-prologue-native-reviewed-v1-current.json'),
        last_local_loop_Author=dict(status=author['status'],compile_pass=False,seconds=author['seconds'],first_stream_message_seconds=author['first_stream_message_seconds'],output_tokens=author['output_tokens'],candidate_statement_edits=0,model_source_installed=False,transcript=str(Path(author['directory'])/'prompts-and-responses.txt')),
        prepared_local_loop_Repair=str(V/'local-record-loop-Repair-prepared-v1.json'),local_loop_Repair_actual_predictions=0,local_loop_Repair_last_observed_status=repair['status'],
        current_status_renderer=str(ROOT/'scripts/show_native_status_v9.py'),portable_entry_version=18,current_status_reader_live_generation_verified=False,current_status_reader_actual_previous_generation_verified=True,
        current_Reader_supplied_snapshot_approved=False,prior_Reader39_snapshot_approved=True,current_copied_weight_native_Chat_rendering_verified=False,
        portable_current_review=str(V/'record-loop-portability-reviewed-v2-current.json'),UI_status='No native UI attempted;headless work authorized. No copied-weight nativeChat rendering or lock-state inference this turn.',
        saved_prompt_or_transcript_records=read(V/'current-model-work-index-v4-current.json')['saved_prompt_or_transcript_records'],portable_saved_prompt_or_transcript_records=read(P/'workbench/verification/current-model-work-index-v4-current.json')['saved_prompt_or_transcript_records'])
    g['remaining_requirements']['game']='v34remains gameplay image. Portablev37v2loop-tail prototype54060bytes is74smaller/body112scene168stack. Host512+19pass,newnative-module identity carries native512/scene772/widehelper131072;retained4992+16fallback and geometry256pass,copiedSDKmatches. Need newCDI,all exact-deployed/layout/startup/heap/provider/fallback/alias/observer/copied-final and freshgates. Oldstandardroute25012/24966 and additionalmatrix190/266arev34only;currentv34prefix450video differences first378,heldbuttons/DSPequal,silentaudio. FullreadableCPU/GPU/DSP/HLEsame-console source-only rebuild,IRQ/arbitraryreentry,video/audio/physical fidelity incomplete.'
    g['remaining_requirements']['local_frontend']='Root/copied statusv9/entry18 and actualMCP preservev34gameplay versus newer portablev37prototype. ExactlocalAuthorprompt/response16.92second compilefailure appended to frozen savedindices;Repairpreparedbutzeroactualpredictionsduesharedleasebusy. PriorReader39provided-snapshotapproval remainshistorical,currentfactsnotgenerated/reviewed. Need reliable useful localcoding,inferenceease and copiedweightnativeChat display/end-to-endlatency. No model source adopted thisturn.'
    g['remaining_requirements']['training']='Zero newoptimizerupdates. Copied2updatecapability/unchangedbasehash previouslyverified;earlier64updatepilotbase0/4adapter0/4unpromoted. NewAuthorcompilefailure is scaffoldeddevelopmentdata,notheldoutquality or traininggain. Need useful gain on untouchedporting/modding/restorationtasks;preserve otherlocaljobs under sharedlease.'
    g['next_actions']=[f['next_action'],
        'Prepare v37v2candidate builder fromv34builder using completedhost512+19/native512/scene772/retained4992/geometry256/copied54060proofs. Explicitly verify native-module identity forv1qualifiedbytes andv2source. Preserve originalmapnames and biwn_v33_records markers;isolate all new proof families.',
        'After newCDI,qualify eight exact-address/startup/heap groups,actualinherited-provider body512/scene772,fallback/reentry/aliases/connected/bus/display/copied-final and read-only observer controls before freshboot routes. Do not reusev34positive matrix orprefix results asv37proof.',
        'Continue full readableCPU/GPU/DSP/HLEsource recovery,same-console source-only rebuilding,video/audio/IRQ/physical fidelity and useful training evaluation. Retry preparedlocalRepair only after actual sharedslotavailability changes;do not replay completed failedAuthor or interfere with unrelatedjobs. NativeChat usability remainsopen;do not askunlock.']
    g['do_not_restart']+=['Completed twofirstsceneprofile replicas;23929/14359callbacks and record6166/706overhead classified,all earlier1000framehashes preserved.',
        'Completed coordinatorloopnative512,scene772,widehelper131072;v1wide-probe executionboundfailure retained,correctedv2complete. C99labelv1failure correctedbyv2nullstatements withfullnativebyteidentity. Host512+19,retained4992+16,geometry256,copiedv2build54060pass;do not replay.',
        'Completed onelocalrecordloopAuthor16.92second compilefailure. Repair launchattempts bothzero whileleasebusy;exactpreparedprompt retained. No Author replay,no silent editing into passing coordinatorhelper.']
    atomic(path,g);clone(path,P/'workbench/verification'/path.name)
    save(out/'delivery.json',dict(status=g['status'],goal_remains_active=True,current_proof_sha256=sha(V/'native-Deck-current-status-v1-current.json'),new_predictions=1,new_training=False,source_sha256=sha(__file__)))
    print('Full goal remains active;portable sourceprototype advanced,no newdisc/model adoption.',flush=True)

if __name__=='__main__':main()
