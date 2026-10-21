"""Record source correction and still-unfinished full objective."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    current=V/'goal-continuation-current.json';old=read(current)
    bad=read(V/'native-input-all-states-v2-current.json');good=read(V/'native-input-all-states-v3-current.json')
    copied=read(V/'native-input-copied-build-v3-current.json');lesson=read(V/'input-helper-seeds-exposed-v1-current.json')
    assert bad['completed']==1890 and bad['original_helper_seed_mismatch_cases']==26
    assert good['completed']==2315 and good['original_helper_D0_seed_match']and good['payload_bytes']==10280
    assert copied['byte_identical']and lesson['optimizer_updates']==0
    for filename in ['input-seed-correction-delivered-current-MCP-response.json','input-seed-correction-delivered-copied-MCP-response.json']:
        assert read(V/filename)['status'].startswith('terminal_')
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp);packet=read(w['packet'])
    assert packet['latest_source_development']['profile']=='native-191f4-input-dispatch-prototype-v2'
    assert not packet['pending_native_candidate']['default_promoted']
    out=V/'input-seed-goal-continuation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old)
    audit=[]
    for job,expected in [(bad,'check_native_input_all_states_v2.py'),(good,'check_native_input_all_states_v3.py')]:
        result=subprocess.run(['ps','-p',str(job['pid']),'-o','pid=,command='],capture_output=True,text=True)
        assert expected not in result.stdout
        audit.append(dict(pid=job['pid'],status=job['status'],matching_live_worker=False))
    save(out/'own-worker-audit.json',dict(status='terminal_all_state_workers_no_matching_live_PIDs',jobs=audit,
        copied_build_terminal=True,Root_and_copied_MCP_terminal=True,unrelated_jobs_inspected=False))
    new=dict(old);new.update(status='active_native_input_all_states2315_seed_fixed_copied10280_full_goal_open',
        recorded_at=datetime.now(timezone.utc).isoformat(),previous_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification='Progress:native191F4CABIprototype10240bytes/425walkingcases/276walkingfixturestack and copiedSDKbyteidentity;read-onlyinputclockdiagnosis425connectedcases194capturedwalks. Fullgoalremainedopen.',
        current_turn_classification='Progress:unmodifiedcomponent1890allstatecases exposed26equipmenthelperD0seedmismatches despite matching outputs/bus. Correctedversionedsource preserves originalseeds at sixJSRsites;2315original/hostC/nativecases nowpasswithzero mismatches,all13statefixturepaths/18retainedhelpertargets. Correctedcomponent10280bytes,332broadfixturestack,copiedSDKbyteidentical. TwoexposedSFTlessonsprepared/copied;zeroinference/optimizerupdates. Root/copiedstatus13entry26andactualMCPdeliveryverified.',
        full_objective_complete=False,goal_status='active',ongoing_finite_workers=[],current_status_manifest=str(wp),
        new_predictions_this_turn=0,optimizer_updates_this_turn=0,new_unique_original_functions_recovered_this_turn=0,
        new_game_execution_this_turn=dict(fresh_routes=0,new_discs=0,saved_game_motion_reruns=0,
            unmodified_component_all_state_comparisons=1890,corrected_original_host_C_native_comparisons=2315,
            preflight_cases_reused_in1890=160,scripted_retained_helper_targets=18,original_E588_runs_in_reference=True),
        current_source_component=dict(profile='native-191f4-input-dispatch-prototype-v2',
            source_directory=good['source_directory'],module_bytes=10280,native_cases=2315,captured_walking_cases=194,
            C_ABI_fixture_stack_bytes=332,all13_state_fixture_paths_verified=True,original_dependency_D0_seed_mismatches=0,
            retained_helper_fixture_targets=18,copied_SDK_byte_identical=True,original_entry_caller_ABI_unqualified=True,
            task_stack_admission_unqualified=True,real_retained_helper_bodies_unqualified=True,yield_IRQ_unqualified=True,installed_in_game=False),
        source_failure_preserved=dict(review=str(V/'native-input-all-states-v2-current.json'),cases=1890,failed_equipment_D0_seed_cases=26,waived=False),
        local_model_review='Sharedinferenceleaseunavailableontwononblockingprobes;notaliveowner/verifiedwaitclaim. No newgenerationorload/unload. Reader43default/historical99wordbrief remains;newsource factsunreviewedbyfreshlocalreply. TwoexposedABIlessonsforfuturetraining,notnewweights/heldoutquality;earlierbase0/4adapter0/4pilotunchanged. NativeChatunverified;headlessallowed,nounlockasked.',
        completion_audit='Notcomplete:onlycomponentfixturesqualified. Originalentry/callerABI,realhelperbodies,actualtaskstack/yieldIRQ,imageintegration,fullCPU/GPU/DSPsource-onlysame-console rebuilding,audio/visual fidelity,usefuluntouched-tasktraininggain,nativeChat ease and future256GBhardwaremeasurements remainunfinished. Keepgoalactive.',
        next_actions=[
            'Qualify an original191F4entry/return adapter and its actualcallers,then task-stack admission and scheduler/yield/IRQ behavior. Preserve correctedcomponent10280byteprefix if appendinganentryadapter,to reuse2315bodyproofs by explicit byteidentity where justified. Noimageintegration before admission/caller/yieldgates.',
            'Realhelperbodies remain scripted dependencies except E588 in reference. NativebridgeD0seeds/stackargs/volatileclobberchecks pass18targets,but this doesnotestablish realhelperbody/CCR/otherimplicit-register contracts. Use actualhelper/caller data when qualifying.',
            'Do not rerun terminal1890unmodified/2315corrected/425priorwalking cases merelyforreceipts. Preserve26failedseedcases. SourcefixchangesD0bookkeeping at sixequipmentJSRsiteswithoutpublicmemoryorder/stackargumentchanges;no newuniqueoriginalroutineclaimed.',
            'Keepv34reviewedbaseline,v37failedpendingmatrixgate22858pixels andDesktopcheckpointpreviewunchanged. Fullsource-onlysame-console gameintegration,CPU/GPU/DSP/audiovisual/IRQfidelity,usefultrainingandlocalChat ease remain the objective.',
            'When actualshared-slotavailabilitychanges,use a freshnamespace to retrylocalanalysis/coding/training;frozenv1prompt/receipt/source mustnot beoverwritten. Newtraininglessonsareexposeddevelopmentdataandmustnotbecounteduntouchedheldout. No waitorblockedclaimfromlockalone.'
        ])
    remaining=dict(old['remaining_requirements'])
    remaining['game']='Nativeinputv2component2315cases/all13statefixturepaths/18retainedhelpertargets andoriginalD0seeds pass. Module10280bytes;332broadCABIstackbefore/afterseedfix versuspriorwalking-only276. Originalentry/callerABI,realhelperbodies,taskstackadmission/yieldIRQ andimageintegrationunqualified. v34baseline/v37failedpendingimageunchanged. FullCPU/GPU/DSPsource-onlysame-console rebuilding,audio/visual/widerfidelityremainunfinished.'
    remaining['training']='TwoexposedSFTlessonsgrounded in26failed/2315correctedcasesprepared/copied,zerooptimizerupdates. Sharedleaseunavailable;no modelinterference. Earlierbase/adapter0/4qualitypilotunchanged. Need usefulgainonuntouchedporting/modding/restorationtasks and reliablelocalcoding;nativeChat/ordinaryuse alsoopen.'
    remaining['local_frontend']='Root/copiedstatus13/entry26andactualMCPdelivercorrectedcomponent,failedv1seedgate,v34baseline andfailedpendingv37image. Reader43defaultreplyapprovalhistorical;newcomponentfactsnotfreshlygenerated. Sharedleaseunavailabledoesnotidentifyliveworker. NativeChatdisplayunverified;headlessworkallowedandnounlockneeded.'
    new['remaining_requirements']=remaining
    new['do_not_restart']=old.get('do_not_restart',[])+[
        'Completednativeinputv1preflight160reusedin1890allstatecomparisons;26dependencyD0seedfailurespreserved',
        'Completedcorrectednativeinputv2all13states2315original/hostC/nativecomparisons;0seedmismatches/332broadstack',
        'CompletedcorrectedcopiedSDK10280byteidentityandtwoexposednottrainedSFTlessons',
        'CompletedRoot/copiedstatus13entry26andactualMCP correctedcomponent/separategameimage delivery'
    ]
    save(out/'goal-state.json',new);assert str(current)not in w['dependencies_sha256'];atomic(current,new)
    for source in [current,*[p for p in out.iterdir()if p.is_file()]]:clone(source,P/'workbench'/source.relative_to(ROOT))
    print(new['status'],flush=True)


if __name__=='__main__':main()
