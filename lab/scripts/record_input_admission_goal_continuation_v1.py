"""Record authoritative progress without carrying stale current-state aliases."""
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    target = V/'goal-continuation-current.json'
    old = read(target)
    receipt_names = ['local-input-task-admission-author-v1','local-input-task-admission-reviewed-v1',
        'native-input-admission-entry-v1','native-input-full-caller-v3','native-input-copied-build-v5']
    receipts = {name:read(V/(name+'-current.json')) for name in receipt_names}
    author,predicate,guard,caller,copied = [receipts[name] for name in receipt_names]
    assert author['new_predictions']==1 and predicate['host_cases']==1440596 and predicate['native_cases']==16280
    assert guard['completed']==20188 and caller['completed']==6945 and copied['bytes']==10580 and copied['byte_identical']
    for name in ['input-admission-delivered-current-MCP-response.json','input-admission-delivered-copied-MCP-response.json']:
        assert read(V/name)['status'].startswith('terminal_actual_')
    wp = V/'native-Deck-current-status-v1-current.json'
    wrapper = read(wp)
    packet = read(wrapper['packet'])
    component = packet['current_native_input_prototype_progress']
    assert component == packet['latest_source_development'] and component['module_bytes']==10580
    assert packet['latest_native_candidate']['native_record_returns']==4777
    assert not packet['pending_native_candidate']['default_promoted']
    out = V/'input-admission-goal-continuation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old)
    audit = []
    for name,script in [(receipt_names[0],'run_local_input_task_admission_author_v1.py'),
                        (receipt_names[1],'check_local_input_task_admission_v1.py'),
                        (receipt_names[2],'check_native_input_admission_entry_v1.py'),
                        (receipt_names[3],'check_native_input_full_caller_v3.py')]:
        job = receipts[name]
        result = subprocess.run(['ps','-p',str(job['pid']),'-o','pid=,command='],capture_output=True,text=True)
        assert script not in result.stdout,(name,result.stdout)
        audit.append(dict(job=name,pid=job['pid'],status=job['status'],matching_live_process=False))
    save(out/'own-worker-audit.json',dict(status='terminal_own_author_and_diagnostics_no_matching_live_PIDs',
        jobs=audit,Root_and_copied_MCP_terminal=True,Root_and_copied_status_CLI_exit_zero=True,
        copied_build_terminal=True,unrelated_jobs_inspected=False))
    save(out/'native-Chat-observation.json',dict(status='observation_timeout_no_UI_state_returned',
        requested_app='LM Studio',reported_wall_seconds=120.7094,screen_lock_state_known=False,
        inference_launched_through_UI=False,unlock_requested=False,native_Chat_verified=False,
        next_action='Continue permitted headless work;do not infer locked screen or a live model process from observation timeout.'))
    state = dict(
        status='active_local_C_admission20188_full_caller6945_copied10580_full_goal_open',
        recorded_at=datetime.now(timezone.utc).isoformat(),objective=old['objective'],
        goal_status='active',full_objective_complete=False,blocked=False,
        previous_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification='Progress:10304byteinputentry,4630entry/4630callerprefixand16pairedrealTRAP/RTEyieldtests104switches. Widercaller/admission remainedopen.',
        previous_user_support_turn_classification='Informational launcher assistance;no new source/model progress. Revalidated authoritative worktree and inference catalog before this continuation.',
        current_turn_classification='Progress:one actual localCoder response19.7s,unedited120bytepredicate passes1440596host/16280actual68000cases. Coordinator stack-firstpreflight adds156bytes;20188route/fencecasespass. Fulloriginalworldcaller6945fixturespass:1264native/2528originalfallback/3153skips,837upperD1differencesretained. Copied10580bytebuildidentical. Root/copiedstatus15/entry28andactualMCPverified. No newdisc/preview/optimizerupdate.',
        current_status_manifest=str(wp),current_status_packet=wrapper['packet'],
        report=component['report'],transcript=packet['current_input_admission_progress']['transcript'],
        new_predictions_this_turn=1,optimizer_updates_this_turn=0,new_training_this_turn=False,
        model_candidate_statement_edits=0,local_model_code_integrated_in_prototype=True,
        local_model_code_installed_in_game=False,new_unique_original_functions_recovered_this_turn=0,
        ongoing_finite_workers=[],own_finite_worker_terminal_audit=str(out/'own-worker-audit.json'),
        current_source_component=dict(profile=component['profile'],module_bytes=10580,
            prior_component_prefix_bytes=10304,prefix_byte_identical=True,
            inherited_all_state_body_cases=2315,inherited_entry_cases=4630,inherited_caller_prefix_cases=4630,
            new_admission_route_cases=20188,new_full_caller_cases=6945,
            admitted_native_calls=1264,original_fallback_calls=2528,caller_input_skips=3153,
            preflight_stack_bytes=36,preflight_reserved_bytes=40,native_admission_reserve_bytes=512,
            full_caller_native_fixture_stack_bytes=356,full_caller_fallback_fixture_stack_bytes=102,
            inherited_real_two_task_stack_bytes=392,fenced_task_stack_capacity=960,
            local_C_predicate_bytes=120,coordinator_assembly_guard_bytes=156,
            no_stack_access_before_preflight_verified=True,full_caller_scripted_dependencies_verified=True,
            universal_raw_ABI_qualified=False,full_real_helper_bound_proven=False,
            real_helper_bodies_qualified=False,arbitrary_IRQ_qualified=False,installed_in_game=False),
        current_context_limits=dict(raw_original_entry_CCR_differing_cases=2706,
            original_entry_volatile_differing_cases=4630,prior_prefix_upper_D1_differing_cases=1480,
            new_full_caller_upper_D1_differing_cases=837,new_full_caller_D1_low_word_equal=True,
            full_caller_final_SR_equal=True,extra_guard_current_task_read_explicit=True,
            resource_animation_collision_camera_entity_helpers_scripted=True,
            GPU_results_scripted_and_mailbox_ack_only=True,
            invalid_original_stack_execution_safe_claim=False,
            logical_native_error_still_fixture_ILLEGAL=True,
            runtime_admission_scope='No-stack-access preflight/routing through exact known1A266caller fixture;not arbitraryIRQ,universalrawABI or a proven reserve for all realhelpers.'),
        current_gameplay_baseline='v34signedrecordstrides;standard25012/24966frames,4777record/displayreturns,8717video differences/finalvideoagrees. Additionalmatrix190/266returns/finalvideoagrees. Desktoppreview remains earlier six-calleroutdoorcheckpoint.',
        pending_candidate='v37loop-tail54060bytemodule;prerequisite/exact-addressgatespass. Standard25004/24966finalvideoagrees,butadditionalmatrix201/266returns/finalvideoFAIL22858pixelswithfractionalpose differences. Fixedprefix449/1000differences;unpromoted,causeunresolved.',
        new_game_execution_this_turn=dict(fresh_routes=0,new_discs=0,entry_admission_route_trials=20188,
            full_caller_paired_fixtures=6945,new_original_task_switch_trials=0),
        current_status_renderer=str(ROOT/'scripts/show_native_status_v15.py'),portable_entry_version=28,
        copied_build_identical=True,current_native_Chat_verified=False,
        native_Chat_observation=str(out/'native-Chat-observation.json'),
        local_model_review='One real copied27B6bit Coder output19.7s;firststream/fullprompt/rawresponse saved. StrictC99and68000compile pass withzero statementedits;120bytes integrated in separate guarded prototype. Not an untouched-task benchmark or weight training. NativeChatapp observationtimedout beforestate;headless permitted. PriorReader43historicalapproval,notnewfacts. Priorbase0/4adapter0/4qualitypilotunchanged.',
        completed_pilot_optimizer_updates_total=old.get('completed_pilot_optimizer_updates_total',64),
        existing_pilot_review=old['existing_pilot_review'],
        current_default_Reader_version=43,current_default_Reader_current_source_approved=False,
        remaining_requirements=dict(
            local_frontend='CurrentRoot/copiedstatus15andentry28/actualMCPwork. ExactCoderprompts/rawresponse linked. NativeLMStudioChatrendering/usabilityoncurrentcopiedmodelunverified;UIobservationtimeoutdoesnotconfirm lock. No unlockneeded/requested.',
            training='Actualuneditedlocalcodingtaskpasses,butno newoptimizerupdates/usefuluntouched-tasktrainedgain. TwoearlierexposedSFTlessonsnottrained;earlierbase/adapter0/4qualitypilotunpromoted. Need representativeuntouchedevaluation and demonstrablegain.',
            game='Guarded10580byteprototype preservesprior10304bytes;20188admission/6945fullcallerfixturespassunderdeclaredscripts. NeedrealhelperCPUcontracts,837upperD1contextresolution,provenreservewithrealnesting,cooperative/IRQ/reentrycoverage,logicalerrorhandling,allocatedimage/startup/heap/alias/observerandfreshqualification. Fullsource-onlysame-consolegame,CPU/GPU/DSP,audio/videoandphysicalconsoleunfinished;v37failedgatepreserved.',
            future_hardware='CopiedSDK/runtime/modeltrainingcapabilitymeasuredon64GBMac.256GBcapacity/concurrency/performanceunmeasured;futureprofileverificationremainsopen.'),
        next_actions=[
            'Execute actual retained resource/animation/collision/camera helper bodies under both original and guarded nativecaller. Inspect fullD1reads/consumption rather than waiving837upperD1differences from scriptedproviders. Keeporiginal191F4globalentryintact.',
            'Qualifytrue stackboundwithrealhelpernesting andknowncooperative/IRQpaths;512reserveisprovisional,not productionevidence. Guard itself36/40bytes and no-stack-accesspreflightpass;native logicalfailurestillILLEGALfixture,not productionfallbackafterpartialsides.',
            'Beforeanyimagepatch,inspectactualplacement/startupcopywidth/heap/alias/observercontracts. Prototype1C0000isfixtureonly. Preservev34baseline,v37failedmatrixgate,andinstalledpreview. Do notnormalizeposes/timers or retunelivecontrols toforceequality.',
            'ContinuefullCPU/GPU/DSPsource-onlysame-consolebuilding,audiovisualfidelity,usefulgame-onlytrainingonuntouchedtasks andnativeChat ease. Preserve unrelatedmodeljobs;acquireleaseandinspectcatalogbeforeinference.',
            'Do notreplayterminalpredicate1440596host/16280native,guard20188,fullcaller6945,copied10580oractualMCPchecksjustforreceipts. Versionsv1/v2failedfullcallerharnessarepreserved;v3explicitlyseparatesnativecalls,fallbacksandskips.'
        ],
        completion_audit='Not achieved. Usefullocalinferenceandnewguardedsourceprototypeprogressareverified,butfullsame-console source-onlygame,realhelpers/IRQ/imagequalification,fidelity,audio,untouched-tasktraininggain,nativeChat ease andfuturecapacityremainincomplete. Goal staysactive.',
        do_not_restart=old.get('do_not_restart',[])+[
            'CompletedoneactuallocalCoder19.7s/uneditedpredicate1440596hostand16280M68000oraclecases',
            'Completed10580byteguardedprototypepreserving10304byteprefix;20188stack-firstadmissionroutes/fences,36bytepreflight',
            'Completed6945fulloriginalcallerfixtures:1264native,2528fallback,3153skips;837upperD1differencespreserved',
            'CompletedcopiedSDK10580byteidentity,Root/copiedstatus15/entry28andactualMCPdelivery'
        ])
    save(out/'goal-state.json',state)
    assert str(target) not in wrapper['dependencies_sha256']
    atomic(target,state)
    for source in [target,*[p for p in out.iterdir() if p.is_file()]]:
        clone(source,P/'workbench'/source.relative_to(ROOT))
    print(state['status'],flush=True)


if __name__=='__main__':
    main()
