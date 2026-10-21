"""Record provider and startup progress; leave the full goal active."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    target=V/'goal-continuation-current.json';old=read(target)
    jobs=[('native-input-real-targeting-caller-v1','check_native_input_real_targeting_caller_v1.py'),
        ('native-input-real-boundary-caller-v1','check_native_input_real_boundary_caller_v1.py'),
        ('native-input-real-resources-caller-v1','check_native_input_real_resources_caller_v1.py'),
        ('native-input-real-combined-caller-v1','check_native_input_real_combined_caller_v1.py'),
        ('local-wide-bootstrap-author-v1','run_local_wide_bootstrap_author_v1.py'),
        ('local-wide-bootstrap-reviewed-v1','check_local_wide_bootstrap_v1.py'),
        ('wide-bootstrap-second-CPU-v1','check_wide_bootstrap_second_CPU_v1.py')]
    receipts={name:read(V/(name+'-current.json'))for name,_ in jobs}
    assert [receipts[name]['completed']for name,_ in jobs[:4]]==[78,78,27,27]
    assert receipts['local-wide-bootstrap-author-v1']['new_predictions']==1
    assert receipts['wide-bootstrap-second-CPU-v1']['completed']==3
    mcp=[];cli=[]
    for lane in ['current','copied']:
        path=V/f'input-provider-startup-delivered-{lane}-MCP-response.json'
        assert read(path)['status'].startswith('terminal_actual_');mcp.append(path)
    for lane in ['Root','copied']:
        path=V/f'input-provider-startup-{lane}-status-cli.txt';text=path.read_text()
        assert len(text.splitlines())==12 and 'targeting 78, boundary 78, resources 27, combined 27' in text
        assert '16.34s' in text and '432 measured' in text and '512-byte entry reserve remains provisional' in text
        assert 'response unapproved' in text and 'Complete source-only Jaguar rebuild remains unfinished' in text
        cli.append(path)
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp);packet=read(wrapper['packet'])
    n=packet['current_input_remaining_helpers_progress'];w=packet['current_input_wide_startup_progress']
    assert packet['current_native_input_prototype_progress']==packet['latest_source_development']
    assert not packet['pending_native_candidate']['default_promoted'] and not w['game_image_qualified']
    out=V/'input-provider-startup-goal-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old);audit=[]
    for name,script in jobs:
        receipt=receipts[name];q=subprocess.run(['ps','-p',str(receipt['pid']),'-o','pid=,command='],capture_output=True,text=True)
        assert script not in q.stdout,(name,q.stdout)
        audit.append(dict(job=name,pid=receipt['pid'],status=receipt['status'],matching_live_process=False))
    save(out/'own-worker-audit.json',dict(status='terminal_own_provider_Coder_and_startup_workers_finished',jobs=audit,
        Root_and_copied_CLI_exit_zero=True,Root_and_copied_MCP_terminal=True,unrelated_jobs_inspected=False))
    frontend=V/'input-provider-startup-checked-frontend-v1.json'
    save(frontend,dict(status='terminal_actual_status18_entry31_Root_and_copied_verified',renderer=str(ROOT/'scripts/show_native_status_v18.py'),
        portable_entry_version=31,default_lines=12,CLI_logs=[str(p)for p in cli],MCP_reviews=[str(p)for p in mcp],
        source_sha256={str(p):sha(p)for p in [*cli,*mcp,ROOT/'scripts/show_native_status_v18.py',ROOT/'scripts/portable_biwn_entry_v31.py']}))
    baseline=w['planned_layouts']['native-record-strides-disc-build-v1']
    pending=w['planned_layouts']['native-record-loop-image-disc-build-v1']
    state=dict(status='active_target78_boundary78_resource27_combined27_wide_startup_dualCPU_full_goal_open',
        recorded_at=datetime.now(timezone.utc).isoformat(),objective=old['objective'],goal_status='active',
        full_objective_complete=False,blocked=False,previous_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification=old['current_turn_classification'],
        current_turn_classification='Progress:actualtarget78/boundary78/resource27/combined27callercomparisonsmatchpublicstate/finalCPUunderexplicitbackendlimits. OneactualuneditedlocalCoder16.34swidebootstraphelperpasses65536valid/9716invalid,56copy/18clearrestoreand3secondCPUtrials. Feasiblev34/v37layoutplansproveword-loopcapacitychangeisneeded;prototypepasses,builderunchanged. Root/copiedstatus18entry31andactualMCPverified. No weights/disc/previewchange.',
        current_status_manifest=str(wp),current_status_packet=wrapper['packet'],report=n['report'],
        new_predictions_this_turn=1,optimizer_updates_this_turn=0,new_training_this_turn=False,
        new_unique_original_functions_recovered_this_turn=0,new_local_model_source_helpers_used_in_prototype=1,
        new_disc_built=False,installed_preview_changed=False,ongoing_finite_workers=[],
        own_finite_worker_terminal_audit=str(out/'own-worker-audit.json'),
        current_source_component=dict(profile='native-191f4-input-admission-prototype-v4',module_bytes=10580,
            component_bytes_changed=False,installed_in_game=False,
            inherited_admission_routes=20188,inherited_broad_scripted_full_caller_cases=6945,
            inherited_animation_cases=318,inherited_camera_original_GPU_cases=78,
            new_targeting_cases=78,new_target_selected_cases=42,new_target_rejected_cases=36,
            new_boundary_cases=78,outdoor_calls=39,indoor_calls=39,boundary_directions=[0,1,2,3],
            new_resource_cases=27,resource_scenarios=n['resource_scenarios'],
            actual_get_calls=27,actual_release_calls=27,actual_allocate_calls=33,actual_free_calls=30,
            new_combined_cases=27,combined_outdoor_calls=15,combined_indoor_calls=12,
            provider_loader_calls=6,provider_wait_calls=6,provider_signal_calls=3,
            combined_nested_boundary_scripts=24,
            all_recorded_targeting_incoming_registers_equal=True,current_matrices_raw_final_differences=0,
            maximum_connected_caller_stack=432,maximum_original_fallback_stack=150,
            entry_reserve=512,entry_reserve_global_bound_proven=False,fenced_task_stack_capacity=960,
            inherited_real_task_yield_stack=392,arbitrary_IRQ_qualified=False,
            complete_geometry_or_loading_qualified=False,source_only_GPU_claim=False),
        current_context_limits=dict(broader6945_upper_D1_differences=837,broader_differences_waived=False,
            actual_boundary_entry_upper_D1_differing_calls=9,new_sets_final_context_differences=0,
            new_fixture_sets_not_a_broad_improvement_metric=True,original_GPU_both_lanes=True,
            synchronous_GPU_completion=True,nested_geometry_cleanup_setup_yield_still_scripted=True,
            resource_loader_wait_signal_still_scripted=True,
            colliding_fixture_code_address=0x1c0000,original_stream_loader_staging_address=0x1c0000,
            logical_native_error_still_fixture_ILLEGAL=True,physical_console_qualified=False),
        wide_startup_prototype=dict(source_profile=w['source_profile'],local_Coder_seconds=16.34,
            local_statement_edits=0,transcript=w['transcript'],host_valid_cases=65536,host_invalid_cases=9716,
            native_copy_fragment_cases=56,native_integrated_clear_restore_cases=18,native_negative_controls=1,
            pinned_native_CPU_and_Unicorn_cases=3,full_RAM_GPR_SR_SSP_USP_match=True,
            legacy_word_loop_capacity=131072,wide_long_loop_capacity=262144,
            actual_blank_staging_and_header_clear_limits_still_apply=True,
            v34_planned_layout=baseline,v37_reference_plan=pending,
            copied_clear_routine_build_identical=True,installed_builders_changed=False,
            arena_heap_relink_qualified=False,new_game_image_written=False,full_boot_qualified=False),
        new_game_execution_this_turn=dict(fresh_routes=0,new_discs=0,
            targeting_paired_comparisons=78,boundary_paired_comparisons=78,resource_paired_comparisons=27,
            combined_paired_comparisons=27,changed_provider_matrix_paired_comparisons=210,
            matrices_have_overlapping_input_cases=True,
            startup_copy_cases=56,startup_clear_restore_cases=18,second_CPU_startup_cases=3,
            naive_wrapped_word_counter_negative_controls=1,original400A_executed_in_startup_prototypes=False),
        current_gameplay_baseline=old['current_gameplay_baseline'],pending_candidate=old['pending_candidate'],
        current_status_renderer=str(ROOT/'scripts/show_native_status_v18.py'),portable_entry_version=31,
        current_status_default_lines=12,current_frontend_actual_review=str(frontend),
        current_native_Chat_verified=False,native_Chat_observation=old['native_Chat_observation'],
        new_native_UI_attempt_this_turn=False,current_default_Reader_version=43,
        current_default_Reader_current_source_approved=False,
        local_model_review='Oneactualownedcopied27B6bitCoderresponse16.34s/334outputtokensproducedpurePythonwiden_loaderhelperwithouteditsorfenceremoval. Exacttypes/template/countguardsanddualCPUstartupchecks pass;adoptedinseparateprototypeonly,nocurrentbuilderchange. PriorReviewer15.88s213words/5.05s63wordsremainunapproved/defaultunchanged. No newoptimizerupdatesorweights;usefuluntouched-tasktrainedgainunproven. NativeChatvisibilityunverified/headlessauthorized.',
        prior_Reviewer_trials=old['local_Reviewer_trials'],completed_pilot_optimizer_updates_total=old['completed_pilot_optimizer_updates_total'],
        existing_pilot_review=old['existing_pilot_review'],
        remaining_requirements=dict(
            local_frontend='Root/copiedstatus18entry31/actualMCPverified,12linecheckedviewandnewCodertranscriptlinked. DefaultReader43notnewfacts;priorRevieweroutputsremainunapproved. Currentcopied-modelnativeLMStudioChatdisplay/usabilityunverified;headlessauthorized/no unlockneeded.',
            training='ActualuneditedlocalCoderCpredicateandPythonstartuphelperareusefulbase-inferenceoutputs,butno newoptimizerupdatesorproven gainonuntouchedgameporting/modding/restorationtasks. Priorbase/adapter0/4qualitypilotunpromoted;exposedlessonsnotheldout.',
            game='Unchanged10580byteguardedinputnowconnectedwithactualtargeting,boundaryrouting,cache/heap,camera/animation/originalGPUunderdeclaredproviders. Neednestedcollisiongeometry,realstreamloading/wait/signal/scheduler,provenstack/IRQ/errorhandlingandbroaderABI. Diagnostic1C0000conflictswithloaderstaging. Widecopy/clearprototypepassesdualCPUandv34layoutfeasible,butrebase/modulearenaheaprelink/finalprovideraliasobserverstartupandfreshimagequalificationremainopen. Fullsource-onlysame-consoleCPU/GPU/DSP/audiovisual/physicalgameunfinished;v37matrixgatefailed.',
            future_hardware=old['remaining_requirements']['future_hardware']),
        next_actions=[
            'Rebaseunchangedinputsourceintoafreshprofileatplannedv34inputaddress0x17C724,insteadofcollidingfixture1C0000. Newfinalizer0x17F078,Deckarena0x17F200,heap0x1A1D80,copy132160/clear132224/stagingDDD80/initialheap123520areplansonly. Checkactuallinkedsizeandrelocations,notnaivebytepatching. Keepv37failedcandidateunpromoted.',
            'Atnoncollidingprototypeaddress,connectoriginal1B044streamloaderandE3E0copywithexplicittransportD206/D2F0/D306andprogressinputs. Resourceget/release/heapareactualalready;loader/wait/signalprovidersremaincontrolled. SupportactualblitterRAMcoherenceandrecordstagewrites. No stagepayloadmustoverwriteinputcode.',
            'Connectnestedcollisiongeometry/cleanup/scene setupandactualscheduler/IRQ/errorpaths. ExistingboundaryentryD1differences9andoldbroad837mustremainrecorded;current210pairedmatrixzero-final-contextisnotuniversalABI.512entryreserveisprovisionaldespite432boundedpeak.',
            'Derivenewexperimentalimagefromreviewedv34onlyafterprovider/placementchecks. Useverifiedwiden_loaderandlongclear,butrelinkallaffectedarenas/heapconstantsandpassallfinal-address/startup/heap/alias/observer/freshgates. Currentbuildersstillenforce131072word-looplimit;do notwaivethatguard. Preserveoriginal191F4globalentryandinstalledpreview.',
            'ContinuefullCPU/GPU/DSPsource-onlygame/fidelity/audioandusefultrainingqualityonrepresentativeuntouchedtasks. Newcodegenerationisnotweighttraining. ImproveordinarylocalChatwhenUIavailablewithoutunlockrequests;acquiresharedlease/ownershipbeforeinferenceandpreserveunrelatedjobs.',
            'Do notreplayterminaltarget78/boundary78/resource27/combined27,65536valid/9716invalidwidehelper,56copy/18clear/3dualCPUandcopiedclearchecksforreceipts. Newquestions/providercombinationsorchangedsourceare requiredforadditionalruns.'
        ],
        completion_audit='Notachieved. Usefulnewproviderconnectionsandlocallyauthoredstartuphelperarenotcompletegameorimagequalification. Rebase/loader/geometry/IRQ/error/relink/freshgates,fidelity/audio,source-onlyGPU/DSP,trainedgain,nativeChat easeandfuturecapacityremainunfinished. Goal remainsactive.',
        do_not_restart=old.get('do_not_restart',[])+[
            'Completed78actualtargeting/camera/animation/originalGPUcallercontexts;42targetselection/36rejection,allincomingtargetregisters/publicstate/finalCPUagree',
            'Completed78actualboundarycontexts39outdoor/39indoor/all4directions;81nestedprovider scripts,9entryD1differencesrecorded,finalCPUagree',
            'Completed27realresourceget/release/heapcontexts9scenarios;get27/release27/alloc33/free30,backendloader6/wait6/signal3controlled',
            'Completed27combinedresource/boundary/target/camera/animation/GPUcontexts;15outdoor/12indoor/24nestedboundaryscripts,432stack,finalCPUagree',
            'CompletedoneactualuneditedlocalCoder16.34swiden_loader;65536valid/9716invalid,56M68000copy/18clearrestore/1wrappedcounternegative,3secondCPUwholeRAM/GPR/bankschecks;copiedclearbinaryidentical',
            'Verifiedv34planned10580byteinputinsertionneeds132160copy/132224clearand123520heap;actualoldbuildersunchanged/capped;notanimage',
            'CompletedRoot/copiedstatus18entry31/12lineCLIandactualMCP;oldbaselineandfailedv37preserved'
        ])
    save(out/'goal-state.json',state);assert str(target)not in wrapper['dependencies_sha256'];atomic(target,state)
    for source in [target,frontend,*mcp,*cli,*[p for p in out.iterdir()if p.is_file()]]:
        clone(source,P/'workbench'/source.relative_to(ROOT))
    print(state['status'],flush=True)


if __name__=='__main__':main()
