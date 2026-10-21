"""Record concrete image progress and its confirmed failure; keep full goal active."""
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    target = V/'goal-continuation-current.json'
    old = read(target)
    wp = V/'native-Deck-current-status-v1-current.json'
    wrapper = read(wp)
    for path,digest in wrapper['dependencies_sha256'].items():
        assert sha(path) == digest,path
    packet = read(wrapper['packet'])
    image = packet['unqualified_native_input_image']
    stream = packet['current_input_stream_rebase_progress']
    assert image['stack_failure_confirmed_two_CPUs'] and not image['admission_reserve_sufficient']
    assert not image['default_promoted'] and image['completed_image_provider_pairs'] == 0
    qa = []
    for lane in ['Root','copied']:
        path = V/f'input-image-stack-{lane}-status-cli.txt'
        text = path.read_text()
        assert len(text.splitlines()) == 12 and '958 stack bytes' in text and '512-byte admission reserve is insufficient' in text
        assert '192 heap checks' in text and '123,520' in text and 'zero predictions' in text
        qa.append(path)
    for lane in ['current','copied']:
        path = V/f'input-image-stack-delivered-{lane}-MCP-response.json'
        assert read(path)['status'].startswith('terminal_actual_')
        qa.append(path)
    out = V/'input-image-stack-goal-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old)
    jobs = [
        ('native-input-rebase-v1','check_native_input_rebase_v1.py'),
        ('native-input-real-stream-caller-v2','check_native_input_real_stream_caller_v2.py'),
        ('native-input-real-stream-second-CPU-v1','check_native_input_real_stream_second_CPU_v1.py'),
        ('stream-rebase-structured-reader-v1','run_stream_rebase_structured_reader_v1.py'),
        ('native-input-callsite-disc-build-v1','build_native_input_callsite_disc_v1.py'),
        ('native-input-image-startup-heap-v1','check_native_input_image_startup_heap_v1.py'),
        ('native-input-image-inherited-providers-v1','check_native_input_image_inherited_providers_v1.py'),
        ('native-input-image-provider-stack-diagnostic-v1','check_native_input_image_provider_stack_diagnostic_v1.py'),
        ('native-input-image-stack-second-CPU-v1','check_native_input_image_stack_second_CPU_v1.py')]
    audit = []
    for name,script in jobs:
        r = read(V/(name+'-current.json'))
        assert r['status'].startswith('terminal_')
        process = subprocess.run(['ps','-p',str(r['pid']),'-o','pid=,command='],capture_output=True,text=True)
        assert script not in process.stdout,(name,process.stdout)
        audit.append(dict(job=name,pid=r['pid'],status=r['status'],matching_live_process=False))
    save(out/'own-worker-audit.json',dict(status='terminal_own_rebase_stream_image_and_diagnostic_workers_finished',jobs=audit,Root_and_copied_CLI_exit_zero=True,Root_and_copied_MCP_terminal=True,unrelated_jobs_inspected=False))
    frontend = V/'input-image-stack-checked-frontend-v1.json'
    save(frontend,dict(status='terminal_actual_status19_entry32_Root_and_copied_verified',renderer=str(ROOT/'scripts/show_native_status_v19.py'),portable_entry_version=32,default_lines=12,source_sha256={str(p):sha(p) for p in [*qa,ROOT/'scripts/show_native_status_v19.py',ROOT/'scripts/portable_biwn_entry_v32.py',ROOT/'scripts/check_input_image_stack_MCP_v1.py']}))
    state = dict(status='active_rebased_input_v38_startup_pass_dual_CPU_task_stack_failure_full_goal_open',recorded_at=datetime.now(timezone.utc).isoformat(),objective=old['objective'],goal_status='active',full_objective_complete=False,blocked=False,
        previous_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification='No progress on decompilation implementation in the immediately preceding how-to reply: existing preview launch paths were verified and explained. The next safe implementation action remained available and was resumed here.',
        current_turn_classification='Progress:revalidated10580bytev5rebase/48relocations/144changedbytesand27originalstreamloaderpairspereachCPU. Builta separateactualv34-derivedv38CDIwithwidebootstrap,relinkedarenasandheap.6startupcasesperCPUand192heapcomparisons pass. Firstactualimageprovider nativecase violatesprotectedtaskbytesat958stackbytes;secondCPUconfirmsidenticalPC/SP/alllowevents. Failurepreservedandunpromoted. Root/copied12lineCLIandactualMCPverified.0newpredictions/optimizerupdates;previewunchanged.',
        current_status_manifest=str(wp),current_status_packet=wrapper['packet'],report=image['report'],current_source_component=packet['current_native_input_prototype_progress'],controlled_stream_component=stream,unqualified_native_input_image=image,
        new_predictions_this_turn=0,optimizer_updates_this_turn=0,new_training_this_turn=False,new_unique_original_functions_recovered_this_turn=0,
        new_disc_built=True,installed_preview_changed=False,current_gameplay_baseline=old['current_gameplay_baseline'],pending_candidate=old['pending_candidate'],
        new_game_execution_this_turn=dict(fresh_routes=0,new_discs=1,actual_image_startup_cases_each_core=6,heap_initialize_cases=192,controlled_original_provider_pairs_each_core=27,completed_actual_image_provider_pairs=0,expected_negative_image_stack_case_confirmed_on_each_core=1,game_frames=0,original400A_executed=False),
        current_context_limits=dict(original_provider_controlled_native_stack=458,original_provider_controlled_fallback_stack=196,image_first_violation_stack_bytes=958,image_full_path_maximum_known=False,failing_fixture_stack_capacity_above_guard=956,generic_fenced_task_stack_capacity=960,admission_reserve=512,admission_sufficient_for_actual_image=False,protected_bytes_changed=[62,63],arbitrary_IRQ_qualified=False,physical_console_qualified=False,production_error_handling_qualified=False,logical_native_error_still_fixture_ILLEGAL=True,broader6945_upper_D1_differences=837,broader_differences_waived=False,synchronous_original_GPU=True,transport_progress_wait_signal_yield_boundary_still_controlled=True,primary_ordered_bus_checked=True,pinned_core_ordered_bus_unobserved=True),
        current_status_renderer=str(ROOT/'scripts/show_native_status_v19.py'),portable_entry_version=32,current_status_default_lines=12,current_frontend_actual_review=str(frontend),
        current_native_Chat_verified=False,native_Chat_observation=old['native_Chat_observation'],new_native_UI_attempt_this_turn=False,current_default_Reader_version=43,current_default_Reader_current_source_approved=False,
        prepared_structured_Reader=packet['prepared_structured_stream_Reader'],
        local_model_review='No newgenerationoroptimizerupdates. StructuredReaderprompt/schemapreparedbutnonblockingsharedleaseunavailablebeforecatalog/generation;0predictions,loadedmodelstructuredgenerationuntested. No liveownerinferredfromlock. UneditedpriorlocalCoder16.34swidecopyhelpernowconsumedbythenewexperimentalbuilder,butimagefailsstackintegration;nottrainedgain. DefaultReader43historicalunapprovedforthesefacts;NativeChatvisibilityunverified.',
        completed_pilot_optimizer_updates_total=old['completed_pilot_optimizer_updates_total'],existing_pilot_review=old['existing_pilot_review'],prior_Reviewer_trials=old.get('prior_Reviewer_trials',[]),
        own_finite_worker_terminal_audit=str(out/'own-worker-audit.json'),ongoing_finite_workers=[],
        remaining_requirements=dict(local_frontend='Root/copiedstatus19entry32andactualMCPshownewimagefailurein12lines. DefaultReader43notnewfacts;structuredReaderpromptpreparedbutgeneration/schemafunctionalityuntested. NativeLMStudioChatprompts/responsesandordinaryeasyinferenceusabilityremainunverified;headlessauthorizedwithoutunlockrequests.',training='No newweightsorprovenusefultrainedgainonuntouchedgameporting/modding/restorationtasks. Earlier64updatepilotbase/adapter0of4unpromoted. PrioruneditedlocalCpredicateandPythonwidenhelperareusefulbaseinferenceoutputs;notproof of modeltraininggain.',game='Actualv38inputimagebuilt/startupheapverifiedbutfirstactualresourceconnectionfailsprotectedtaskstackattask+62. Fixprivatecompiler/gueststackplacementandproveadmissionagainstactualcompiledresourcechain,nestedgeometry/scheduler/IRQ/errors,allprovider/alias/observerandfreshimagegates. Fullsource-onlysame-consoleCPU/GPU/DSP/audio/fidelity/physicalgameunfinished. Reviewedv34andfailedv37remainseparate;previewoldercheckpoint.',future_hardware=old['remaining_requirements']['future_hardware']),
        next_actions=[
            'Use preserved actual-image PC0x1603FE/SP0xC0966/task0xC0928 counterexample and matched pinned-core low-event trace to repair stack ownership. The inheritedresource-acquire-shim.S reserves512bytes belowguestpublicsaves;nativeinputaddsitsownC/physical-callframes. PreserveoriginalhelperSP/context,schedulerstateand64byteguard. Do not merelyraiseharnessboundsorclaima completed-path958maximum.',
            'Evaluate a task-owned compiler stack or bounded-stack source/bridge design for the complete actual compiled resource/helper chain,includingrelease/free,acquire/allocate/load/wait/signal,animation/Deckyield. Do notsilentlyreplaceactualproviderswithoriginalstomaketheimagepass. Keeporiginal1A266referenceandv38failureasregressions.',
            'For any changedprofilebuildnewnamespaceandrerunneededactual-address/admission/helper/dualCPUregressions. Preserveallfrozenreceipt/sourceSHAclosures. v5runtimeunchangedrelocationauditisnotnewbyte-prefixidentityorafresh4630/20188ABIproof.',
            'Afterstackrepair,qualifyimageproviders,nestedcollisiongeometry,alias/reentry,read-onlyobservers,IRQ/errorpathsandfreshgameplaybeforepromotion. Preserveglobal191F4andinstalledpreview. Do notwaivefailedv37matrixvideogateorcomparecurrentdifferentfixturecountsasbroadABIimprovement.',
            'ContinuefullCPU/GPU/DSPsource-onlysame-consolegame/fidelity/audioandusefultrainingonuntouchedtasks. ImproveordinarylocalChatwithvisibleprompts/responseswhenUIavailablewithoutunlockrequests;acquiresharedlease/ownershipbeforegenerationandpreserveunrelatedjobs.',
            'Do notreplayterminal27streamcomparisonsperCPU,6actualstartupinputsperCPU,192heapcasesorconfirmednegativecaseforreceipts. A changedsource/providercombinationornewtechnicalquestionmustjustifynewruns.'
        ],
        completion_audit='Not achieved. Newdiscstartupandcontrolledstreamtestsarenotcompletegameplay. Actual-image taskguardviolationisconfirmedandunfixed;completehelper/scheduler/IRQ/error/freshfidelity/audio/source-onlyGPU/DSP/physical-console,trainedgain,nativeChateaseandfuturecapacityremainunfinished. Meaningfulstackrepairworkisavailable;goalremainsactive,notblocked.',
        do_not_restart=old.get('do_not_restart',[])+[
            'v5rebase10580bytesat17C724/48ELFrelocations/144changedbytes/0runtimechanges/copiedSDKidentical;no literalprefixidentity',
            '27controlledoriginalstreamloader/copy/resource/heap/target/camera/animation/GPUcomparisonsoneachCPU,6loads/copies/payloadchecks,458native/196fallback;CPUbusorderprimaryonly',
            'StructuredReaderpreparedonce;leaseunavailablebeforegeneration,0predictions;not a verified livewaitorowneridentification',
            'Separatev38inputCDIbuiltfromv34;copy132160/clear132224/resident274368/initialheap123520;no promotion',
            'Actualv38startup6dirtyRAMcasesperCPU/full2MBoracleincludingsavedstack/arenas/input,192heapcasespass;no400A/gameframes',
            'Actualv38firstnativeequipment/resourcecaseFAILtaskguardPC1603FE/SPC0966/958observedstack/bytes62and63changed;pinnedCPUconfirmsalllowevents;0imageproviderpairspass',
            'Root/copiedstatus19entry32/12lineCLIandactualMCPretainreviewedv34,failedv37andfailedv38,separated'
        ])
    save(out/'goal-state.json',state)
    assert str(target) not in wrapper['dependencies_sha256']
    atomic(target,state)
    for source in [target,frontend,Path(__file__),ROOT/'scripts/check_input_image_stack_MCP_v1.py',*qa,*[p for p in out.iterdir()if p.is_file()]]:
        clone(source,P/'workbench'/source.relative_to(ROOT))
    print(state['status'],flush=True)


if __name__ == '__main__':
    main()
