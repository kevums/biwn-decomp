"""Record measured source repair while retaining full objective and image failures."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    target=V/'goal-continuation-current.json';old=read(target)
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp)
    for p,h in wrapper['dependencies_sha256'].items():assert sha(p)==h,p
    packet=read(wrapper['packet']);a=packet['current_acquire_arena_stack_progress']
    assert a['primary_paired_cases']==a['pinned_CPU_paired_cases']==27 and not a['new_disc_built']
    qa=[]
    for lane in ['Root','copied']:
        path=V/f'acquire-arena-{lane}-status-cli.txt';text=path.read_text()
        assert len(text.splitlines())==12 and '786 bytes' in text and '180/224' in text and '20,188' in text and '432 cases' in text
        assert 'Not installed in a new image' in text and 'v38 stack failure' in text;qa.append(path)
    for lane in ['current','copied']:
        path=V/f'acquire-arena-delivered-{lane}-MCP-response.json';assert read(path)['status'].startswith('terminal_actual_');qa.append(path)
    out=V/'acquire-arena-goal-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'previous-goal-state.json',old)
    jobs=[('acquire-stack-gap-prototype-v2','prepare_acquire_stack_gap_v2.py'),('native-input-acquire-gap448-caller-v5','check_native_input_acquire_gap448_caller_v5.py'),('acquire-arena-prototype-v1','prepare_acquire_arena_prototype_v1.py'),('native-input-acquire-arena-caller-v1','check_native_input_acquire_arena_caller_v1.py'),('native-input-arena-admission-v6','prepare_input_arena_admission_v6.py'),('native-input-arena-admission-entry-v1','check_native_input_arena_admission_entry_v1.py'),('native-input-acquire-arena-caller-v2','check_native_input_acquire_arena_caller_v2.py'),('native-input-acquire-arena-second-CPU-v1','check_native_input_acquire_arena_second_CPU_v1.py'),('acquire-arena-identity-v1','check_acquire_arena_identity_v1.py')]
    audit=[]
    for name,script in jobs:
        receipt=read(V/(name+'-current.json'));assert receipt['status'].startswith('terminal_')
        process=subprocess.run(['ps','-p',str(receipt['pid']),'-o','pid=,command='],capture_output=True,text=True);assert script not in process.stdout,(name,process.stdout)
        audit.append(dict(job=name,pid=receipt['pid'],status=receipt['status'],matching_live_process=False))
    save(out/'own-worker-audit.json',dict(status='terminal_own_gap_arena_entry_and_CPU_workers_finished',jobs=audit,Root_and_copied_CLI_exit_zero=True,Root_and_copied_MCP_terminal=True,unrelated_jobs_inspected=False))
    frontend=V/'acquire-arena-checked-frontend-v1.json'
    save(frontend,dict(status='terminal_actual_status20_entry33_Root_and_copied_verified',renderer=str(ROOT/'scripts/show_native_status_v20.py'),portable_entry_version=33,default_lines=12,source_sha256={str(p):sha(p)for p in [*qa,ROOT/'scripts/show_native_status_v20.py',ROOT/'scripts/portable_biwn_entry_v33.py',ROOT/'scripts/check_acquire_arena_MCP_v1.py']}))
    state=dict(status='active_shared_arena_source_repair_dual_CPU27_entry20188_identity432_image_lifetime_open',recorded_at=datetime.now(timezone.utc).isoformat(),objective=old['objective'],goal_status='active',full_objective_complete=False,blocked=False,previous_goal_state=str(out/'previous-goal-state.json'),previous_goal_turn_classification=old['current_turn_classification'],
        current_turn_classification='Progress:rejected448gapafter6validpairsandactualnestedloaderparked-statecorruption. Authored676byteacquirecompiler-arenaadapterusingexistingtaskGPUslots/noadditionalprivatearena.18initialvalidcallerpairspass;inputv6raises512to768withonebyte/copiedSDKidentity.20188newentryroutespass.27fullcompiled-providercallerpairspereachCPUincludes6actualloads/copies/yields/21parkedstatechecks;guest786/fallback524/private180of224/fencesandpublicstate/finalCPUagree.432adapter-onlyidentitycasespass101slots+7invalidIDs. Root/copiedstatus20entry33/actualMCPverified. No newimage,prediction,weightsorpreviewchange.',
        current_status_manifest=str(wp),current_status_packet=wrapper['packet'],report=a['report'],current_source_component=packet['current_native_input_prototype_progress'],current_acquire_arena_stack_progress=a,
        new_predictions_this_turn=0,optimizer_updates_this_turn=0,new_training_this_turn=False,new_unique_original_functions_recovered_this_turn=0,new_disc_built=False,installed_preview_changed=False,
        current_gameplay_baseline=old['current_gameplay_baseline'],pending_candidate=old['pending_candidate'],unqualified_native_input_image=old['unqualified_native_input_image'],controlled_stream_component=old['controlled_stream_component'],
        new_game_execution_this_turn=dict(fresh_routes=0,new_discs=0,game_frames=0,rejected_gap_completed_pairs=6,rejected_gap_nested_overlap_counterexamples=1,initial_arena_valid_pairs=18,revised768_and_actual_progress_pairs_each_core=27,entry_route_cases=20188,adapter_only_identity_cases=432,identity_body_RTS_provider=True),
        current_context_limits=dict(native_guest_stack=786,original_fallback_guest_stack=524,private_arena_stack_and_context_bytes=180,private_arena_usable_bytes=224,private_arena_minimum_SP_offset=60,input_reserve=768,full_caller_entry_overhead=60,reserve_margin_over_measured_input_chain=42,global_real_helper_IRQ_bound_proven=False,arena_lifetime_alias_qualified=False,real_TRAP_RTE_with_resource_arena_qualified=False,arbitrary_IRQ_qualified=False,physical_console_qualified=False,production_error_handling_qualified=False,logical_native_error_still_fixture_ILLEGAL=True,public_comparison_excludes_current224byte_private_arena=True,private_raw_bus_differences_primary=746,private_final_RAM_differing_cases=2,runtime_RAM_normalized=False,primary_ordered_public_bus_and_parked_writes_checked=True,pinned_CPU_bus_not_observed=True,transport_progress_wait_signal_yield_boundary_controlled=True,synchronous_original_GPU=True,all_current_final_contexts_match=True,broader6945_upper_D1_differences=837,broader_differences_waived=False,old500byte_start_original_fallback_not_safe_for_all_helpers=True,new_valid_headroom_fallback_initial_offset=800),
        current_status_renderer=str(ROOT/'scripts/show_native_status_v20.py'),portable_entry_version=33,current_status_default_lines=12,current_frontend_actual_review=str(frontend),current_native_Chat_verified=False,native_Chat_observation=old['native_Chat_observation'],new_native_UI_attempt_this_turn=False,current_default_Reader_version=43,current_default_Reader_current_source_approved=False,prepared_structured_Reader=old['prepared_structured_Reader'],
        local_model_review='Allnewcode/diagnosticscoordinatorauthored. No inferenceleaseattempt,modelprediction,optimizerupdateorweighttraininginthiscontinuation. Uneditedlocalpredicateunchangedininputv6;earlierPythonwidenhelpernotrerun. DefaultReader43andpreparedstructuredReadersnapshotnotcurrentfacts/nativeChatunverified. Othermodelworkuntouched.',completed_pilot_optimizer_updates_total=old['completed_pilot_optimizer_updates_total'],existing_pilot_review=old['existing_pilot_review'],prior_Reviewer_trials=old.get('prior_Reviewer_trials',[]),
        own_finite_worker_terminal_audit=str(out/'own-worker-audit.json'),ongoing_finite_workers=[],
        remaining_requirements=dict(local_frontend='Root/copiedstatus20entry33andactualMCPdistinguishsource repairfromfailedv38imagein12lines. NativeLMStudioChatvisibleprompts/responsesandordinaryeasyinferenceusabilityremainunverified. Reader43historicalunapprovedfornewfacts;headlessoperationauthorizedwithoutunlockrequests.',training='No newweightsorproven usefultrainedgainonuntouchedgameporting/modding/restorationtasks. Earlier64updatepilotbase/adapter0of4unpromoted. Localpredicate/startuphelperareearlierbase-inferenceoutputs;thisturnresourcearena/768reserveiscoordinatorcode.',game='676byte acquire compiler stack prototype plusinputv6passes27validcompiled-providerpairsperCPU,entryroutesandadapter-onlyidentity. Needactualresourcewait/TRAPRTE/scratchlifetime,GPUalias/reentry/IRQownershipproof,productionerrorbehavior,nestedgeometryandbroaderABI. Needactualresidentrelinkwithnewadapter/finalizer/Deck/outer/heap,allstartup/copy/provider/alias/observer/freshgates. v38stackfailureandv37videofailureunpromoted. Fullsource-onlysame-consoleCPU/GPU/DSP/audio/fidelity/physicalgameunfinished.',future_hardware=old['remaining_requirements']['future_hardware']),
        next_actions=[
            'Connectnewresource-arenaadapterwithactualoriginalwait/signal/DF60/TRAPRTE/schedulerunderatleasttwodifferenttasks. Whileonewaits,letanotheruseitsGPUarenaandverifyallparkedcompilerstate/guestSP/registers/fences/resume. Existing27pairsyieldthroughcontrolledproviders,notreal taskswitches.',
            'Prove or guard scratch lifetime against same-taskGPU/resource nesting,reentryandIRQs. Adaptercurrentlyborrowsexistingper-taskGPU224byteinteriorwithoutownershiptoken. ActualresourceCcallbacksarewait/signal/allocate/load;copyusesblitterandnormalchainpassesbutnotarbitrarynestedGPU. Do notpromotewithoutownership/aliasproof;addexplicitbus-visibleerror/fallbackpolicyiflegaloverlapexists.',
            'Afterlifetimechecks,relink676byteassemblyfromfixture1F0000tofreshresidentplacementafter10580byteinputv6;allabsolute/PCrelativeaddressesmustbelinkedaudited. Fiveentryjumpstubsreplaceoldresourceacquireshim/captures. PreserveCbody160434,global191F4andactualcompiledproviders. Recomputefinalizer/Deck/outer/heap/staging/widecopy;validateactualsizesthenallfinalimagegates/copiedSDK/freshgameplay.',
            '768entryreservecoversmeasuredinput-chain726byteswith42margin,notageneralIRQbound. New20188routesinclude832boundary,27callerfixtureusesvalidtask+800fallback. Originaltask+500cannotfitallcompiled-originalhelperpathsandmustnotbecalledsafe. Keepoldv38taskguardcounterexampleand448gaploaderoverlapasregressions.',
            'ContinuefullCPU/GPU/DSPsource-onlysame-consolegame/fidelity/audioandusefultrainingonuntouchedtasks. ImproveordinarylocalChatwithvisibleprompts/responseswhenUIavailablewithoutunlockrequests;acquiresharedlease/ownershipbeforegenerationandpreserveunrelatedjobs.',
            'Do notreplayterminal27revisedcallerpairspereachCPU,20188entryroutes,432adapteridentityorcopiedv6buildforreceipts. Newtask-switch/alias/IRQ/providercombinationsorchangedcodejustifynewtests. Frozenpublishedsources/receiptsmustnotbeedited;usefreshnamespaces.'
        ],completion_audit='Not achieved. Source-level stack repair and bounded testspass,not realresource scheduling/arena ownership/IRQ,imageorfullgamequalification. v38remainsfailed/unmodified. CompleteCPU/GPU/DSP/audio/fidelity/physicalgame,trainedgain,nativeChateaseandfuturecapacityremainunfinished. Meaningful realtask/lifetime workavailable;goalactive,notblocked.',
        do_not_restart=old.get('do_not_restart',[])+[
            '448gaprebuildbyte-identicalold512then7LEAdisplacementcandidate,rejectedafter6pairsbynestedloaderPC15F4B2overwriteofparkedstate',
            '676bytecoordinatoracquirearenaadapterfixture1F0000/fiveoldentrystubs/existingGPU224byteprivateinterior;newprivatearenaallocation0;notanimage',
            'Inputv6same10580bytes/sameallELFsymbols/oneimmediatebytereserve512to768/copiedSDKidentical;20188newentryroute/fencecasespass',
            '27validcompiled-providercallerpairspereachCPU:9native/9supervisor/9task+800headroomfallback;6actualloads/copies/payloadchecks/controlledyields,21parkedsnapshotseach,guest786/fallback524/private180of224,minSPoffset60',
            'AllfinalCPU/publicstateoutsideexplicitcurrent224privatebytesmatch;746primarybusprivatevaluedifferences/2finalprivateRAMdiffcasesretained,all102slotfencespass;secondarybusunobserved',
            '432adapter-onlyRTSbodycasescoverall101validslots+7invalidIDs/usermodeandsupervisor/flagendpoints;allregisters/banks/guest-savebytes/outsideprivateRAMmatch',
            'Root/copiedstatus20entry33/12lineCLIandactualMCPverified;v34baseline,v37videoFAILandv38stackFAILpreserved;nonewimage/modelprediction/weightupdate/previewchange'
        ])
    save(out/'goal-state.json',state);assert str(target)not in wrapper['dependencies_sha256'];atomic(target,state)
    for source in [target,frontend,Path(__file__),ROOT/'scripts/check_acquire_arena_MCP_v1.py',*qa,*[p for p in out.iterdir()if p.is_file()]]:clone(source,P/'workbench'/source.relative_to(ROOT))
    print(state['status'],flush=True)


if __name__=='__main__':main()
