"""Record entry/caller/yield progress without shrinking the active objective."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    target=V/'goal-continuation-current.json';old=read(target)
    entry=read(V/'native-input-entry-ABI-v2-current.json');caller=read(V/'native-input-caller-prefix-v1-current.json')
    yielded=read(V/'native-input-real-task-yield-v2-current.json');copied=read(V/'native-input-copied-build-v4-current.json')
    assert entry['completed']==caller['completed']==4630 and yielded['completed']==16 and copied['byte_identical']
    for name in ['input-entry-yield-delivered-current-MCP-response.json','input-entry-yield-delivered-copied-MCP-response.json']:
        assert read(V/name)['status'].startswith('terminal_')
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp);p=read(w['packet'])
    assert p['latest_source_development']['profile']=='native-191f4-input-entry-prototype-v3'
    assert not p['pending_native_candidate']['default_promoted']and p['latest_native_candidate']['native_record_returns']==4777
    out=V/'input-entry-goal-continuation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old);audit=[]
    for job,name in [(entry,'check_native_input_entry_ABI_v2.py'),(caller,'check_native_input_caller_prefix_v1.py'),(yielded,'check_native_input_real_task_yield_v2.py')]:
        q=subprocess.run(['ps','-p',str(job['pid']),'-o','pid=,command='],capture_output=True,text=True);assert name not in q.stdout
        audit.append(dict(pid=job['pid'],status=job['status'],matching_live_worker=False))
    save(out/'own-worker-audit.json',dict(status='terminal_entry_caller_yield_workers_no_matching_live_PIDs',jobs=audit,
        copied_build_terminal=True,Root_and_copied_MCP_terminal=True,unrelated_jobs_inspected=False))
    n=dict(old);n.update(status='active_input_entry4630_caller4630_real_yield16_copied10304_full_goal_open',
        recorded_at=datetime.now(timezone.utc).isoformat(),previous_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification='Progress:26equipmentD0seedcounterexamples corrected in versionednativeinputv2;2315allstate/capturedregressioncomparisons and copied10280bytebuildpass. TwoexposedSFTlessonsprepared,zerooptimizerupdates;fullgoalopen.',
        current_turn_classification='Progress:24byteentryadapterappendedtopreserved10280bytecomponent.4630entryD0/callee-save/SP/bankcontracts pass,but2706CCR/allcaller-save differences retained. Actualcaller1A266..1A340/E220/E098publicRAM,bus,args,frames,flagsmatch4630;upperD1differs1480. Sixteenactualtwo-taskTRAP/RTEpairedtrials/104switchesresumeCframes within392/960fencedbytes. Copied10304bytebuildidentical. Root/copiedstatus14entry27andactualMCPverified. No gameimage/inference/weightupdate.',
        full_objective_complete=False,goal_status='active',ongoing_finite_workers=[],current_status_manifest=str(wp),
        new_predictions_this_turn=0,optimizer_updates_this_turn=0,new_unique_original_functions_recovered_this_turn=0,
        new_game_execution_this_turn=dict(fresh_routes=0,new_discs=0,entry_pair_cases=4630,caller_prefix_pair_cases=4630,
            original_two_task_paired_trials=16,actual_original_task_switches=104),
        current_source_component=dict(profile='native-191f4-input-entry-prototype-v3',module_bytes=10304,
            inherited_component_bytes=10280,appended_entry_bytes=24,component_prefix_byte_identical=True,
            inherited_body_cases=2315,entry_cases=4630,caller_prefix_cases=4630,
            body_C_ABI_stack=332,entry_fixture_stack=348,caller_prefix_stack=352,actual_two_task_stack=392,
            fenced_task_stack_capacity=960,bounded_two_task_yield_verified=True,
            universal_raw_context_ABI_unqualified=True,remaining_caller_unqualified=True,real_helper_bodies_unqualified=True,
            runtime_task_stack_admission_unqualified=True,arbitrary_IRQ_unqualified=True,installed_in_game=False),
        current_entry_context_limits=dict(raw_entry_CCR_differing_cases=2706,raw_entry_volatile_differing_cases=4630,
            caller_prefix_final_SR_equal=True,caller_prefix_upper_D1_differing_cases=1480,
            GPU_provider_ack_only=True,task_A_saved_SR_equal_pairs=12,total_task_pairs=16,
            private_first_task_and_exception_frame_layout_dependent=True),
        local_model_review='No newlocalpredictionoroptimizerupdates. Sharedleaseunavailableatturnstart;notliveowner/verifiedwaitclaim. Reader43defaultapprovalhistoricalafternewsourcefacts. Earlierbase0/4adapter0/4pilotunchanged;twoexposedlessonsfrompriorgoalworknottrained. NativeChatunverified/headlessallowed/no unlockrequest.',
        completion_audit='Unproven:entryadapterisnotuniversalrawABIequivalent. Testedcallerprefixandboundedrealcooperativeyieldsstrengthencomponentreadiness,butremainingcaller/realhelpers/runtimeadmission/arbitraryIRQ andimageintegrationopen. Fullsource-onlysame-console game,CPU/GPU/DSP/audiovisualfidelity,usefuluntouched-tasktraininggain,nativeChat ease and futureprofilelimits remainunfinished. Keepgoalactive.',
        next_actions=[
            'Qualifyremainingactualworldcallerafter1A340andrealretainedhelperbodies. Do not treat caller-prefix publicstate/SRmatch aswholecaller or universalentryABIproof;upperD1differences and2706entryCCRdifferencesstayrecorded. Prefercallsite-specificintegrationonlyafteractualcallercontractisproved;original191F4globalentrymustnotbeblindlyredirected.',
            'Implement/test runtimeadmission for original1024bytetasks and fallback before publiceffects,using actualtaskidentity/mode/SP/fencelimits. Boundedtwotask392/960stackand104actualTRAP/RTEswitchespass,butdo notprovealltaskpaths,realhelpernesting,arbitraryIRQs or invalidtaskadmission.',
            'Inspect actualimageplacement/startupcopy/heap/alias/observerrequirements beforeanycandidatebuild;currentfixturecodeaddress1C0000isnot an allocatedgameimage reservation. Preservev34reviewedbaseline,v37failedmatriximage andDesktoppreview. Do not maskposes/timers or retunecontroller toforceequalimages.',
            'Do notreplayterminal4630entry/4630callerprefix/16pairedyieldcasesorcopied10304buildforreceipts. Sourceprofileinput-dispatch-native-v3-entryisbyteguarded;usefreshnamespace/profileforchanges. Earlierentryv1serializationfailure32caseprefixwasreviewed/reused;yieldv1linkfailurewasclassifiedterminalbeforeexecution.',
            'ContinuefullCPU/GPU/DSPsource-onlysame-console rebuilding,audio/IRQ/fidelity andusefultraining/localChatworkflow. Retrylocalmodelworkonlyafteractualslotavailabilitychanges,preservingunrelatedjobs. No verifiedwaitfromlockalone;no blockerstatuswhileindependentworkavailable.'
        ])
    remaining=dict(old['remaining_requirements'])
    remaining['game']='Entryprototype10304bytes preservescorrected10280bytebody.4630basicentrycasespassbutrawcontextdiffers. Callerprefixpublicstate/flagsmatch4630withupperD1diff1480. SixteenactualtwotaskTRAP/RTEtrials104switchesfit392/960fencedstack. Remainingcaller/realhelperbodies/runtimeadmission/arbitraryIRQ/imageplacementandfreshqualificationopen. Fullsource-onlysame-console game,audio/visual/CPU/GPU/DSPfidelityunfinished;v34baseline/v37failedpendingimageunchanged.'
    remaining['local_frontend']='Root/copiedstatus14/entry27andactualMCPexposeentry/contextlimits/callerprefixandboundedreal-yieldevidence separatelyfromgameimage. Reader43remainsdefaultwithhistoricalapproval;newfactsnotfreshlygenerated. NativeLMStudioChatdisplayunverified;headlessallowed/no unlockneeded. Sharedmodelleaseunavailabilitydoesnotidentifyalivejob.'
    n['remaining_requirements']=remaining
    n['do_not_restart']=old.get('do_not_restart',[])+[
        'Completed24byteoriginal-styleentryadapterand10280byteprefixidentity;module10304bytes',
        'Completed4630user/supervisorentrycontracts;2706rawCCR/allcaller-save differencespreserved',
        'Completed4630actualcallerprefix/E220/E098CPU/mailboxackcomparisons;fullSR/publicstatepass,1480upperD1diffsretained',
        'Completed16pairedactualTRAP/RTEtwo-tasktests104switches;native392/B52/SSP6stack,fencespass',
        'CompletedcopiedSDK10304byteidentityandRoot/copiedstatus14entry27/actualMCPdelivery'
    ]
    save(out/'goal-state.json',n);assert str(target)not in w['dependencies_sha256'];atomic(target,n)
    for source in [target,*[x for x in out.iterdir()if x.is_file()]]:clone(source,P/'workbench'/source.relative_to(ROOT))
    print(n['status'],flush=True)


if __name__=='__main__':main()
