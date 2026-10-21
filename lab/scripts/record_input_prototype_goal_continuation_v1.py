"""Preserve full goal scope and exact terminal progress,without status changes."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    target=V/'goal-continuation-current.json';old=read(target)
    r=read(V/'native-input-prototype-v1-current.json');copied=read(V/'native-input-copied-build-v2-current.json')
    timing=read(V/'input-timing-connected-v1-current.json')
    assert r['cases']==425 and r['payload_bytes']==10240 and r['C_stack_bytes']==276
    assert copied['byte_identical'] and timing['captured_walking_cases']==194
    for filename in ['native-input-component-delivered-current-MCP-response.json','native-input-component-delivered-copied-MCP-response.json']:
        result=read(V/filename);assert result['status'].startswith('terminal_')
    w=read(V/'native-Deck-current-status-v1-current.json');p=read(w['packet'])
    assert p['latest_source_development']['profile']=='native-191f4-input-dispatch-prototype-v1'
    assert p['latest_native_candidate']['native_record_returns']==4777 and not p['pending_native_candidate']['default_promoted']
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=V/'input-prototype-goal-continuation-v1'/stamp;out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old)
    jobs=[]
    for origin in ['candidate','control']:
        for lane in ['native','original']:
            pointer=V/f'record-loop-input-timing-{origin}-{lane}-v3-current.json';job=read(pointer)
            assert job['status']=='terminal_saved_state_equal_origin_diagnostic_pending_review'
            process=subprocess.run(['ps','-p',str(job['pid']),'-o','pid=,command='],capture_output=True,text=True)
            assert 'run_record_loop_input_timing_v3.py'not in process.stdout
            jobs.append(dict(origin=origin,lane=lane,pid=job['pid'],recorded_status=job['status'],matching_live_worker=False))
    save(out/'own-worker-audit.json',dict(status='terminal_four_diagnostic_workers_no_matching_live_PIDs',jobs=jobs,
        connected425_and_native425_tools_reported_exit0=True,copied_build_terminal=True,actual_MCP_delivery_terminal=True,
        unrelated_jobs_inspected=False))
    analyst=read(V/'local-input-timing-analyst-v1-current.json');assert analyst['new_predictions']==0
    n=dict(old);n.update(status='active_native191F4_component425_copied10240_clock_diagnosed_full_game_and_training_open',
        recorded_at=datetime.now(timezone.utc).isoformat(),
        previous_goal_turn_classification='Progress:twelveequalstate stationary/motionlanes,fourreplicacontrols,627actualCtransitions,and reviewed existingReader43defaultdelivery established newevidence. No fullgoalcompletion claimed.',
        current_turn_classification='Progress:fourread-only inputboundarylanes preserveeverypriorCPU/RAM/GPU/DSP/videorow and explain controlled22/23movementsteps via287/290admittedclockticks.425connected original191F4/E588cases pass,including194capturedwalkcalls. Newnative68000C-ABIinputcomponent10240bytes passes425native walking/backward/run cases,276bytefixturestack. CopiedSDKbuildbyteidentical;relative recipefixespathspaces. Root/copiedstatus12/entry25andactualMCPdeliver separatecomponent/pendingimage. PreparedTraceAnalystzero predictions(sharedleaseunavailable).',
        full_objective_complete=False,goal_status='active',previous_goal_state=str(out/'previous-goal-state.json'),ongoing_finite_workers=[],
        current_status_manifest=str(V/'native-Deck-current-status-v1-current.json'),
        new_game_execution_this_turn=dict(readonly_saved_snapshot_motion_lanes=4,frames_each=180,fresh_routes=0,new_discs=0,
            host_pose_timer_or_input_normalization=False,connected_original_CPU_cases=425,native_component_CPU_cases=425),
        new_predictions_this_turn=0,optimizer_updates_this_turn=0,new_unique_original_functions_recovered_this_turn=0,
        current_source_component=dict(profile='native-191f4-input-dispatch-prototype-v1',module_bytes=10240,native_cases=425,captured_walking_cases=194,
            C_ABI_fixture_stack_bytes=276,copied_SDK_byte_identical=True,remaining_input_states_unqualified=True,
            original_entry_caller_ABI_unqualified=True,task_stack_admission_unqualified=True,yield_IRQ_unqualified=True,
            installed_in_game=False),
        current_gameplay_baseline=old['current_gameplay_baseline'],pending_candidate=old['pending_candidate'],
        local_model_review='Reader43remainsdefaultwithhistorical99word/8.27generationsecond/18.94firsttext/25.18warmCLItotalprovidedfactspass. Newestsourceisnowseparatenativeinputcomponent,so current-source replyapprovalisfalse. PreparedTraceAnalystexactprompt is saved butzeroactualpredictionsdue unavailablelease;noownedmodelwasloaded/unloaded. NativeChatunverified;noUIattempt orunlockrequest thisturn.',
        completion_audit='Unproven:whole-game source-only same-console rebuilding,remainingnativecomponentstates/entryABI/taskstack/yieldIRQ,imageintegration/fidelity,audio and usefuluntouched-tasktraininggain,copiedweightnativeChat ease and future256GBhardwaremeasurements. Do not mark complete,blocked orpaused.',
        remaining_requirements=dict(
            local_frontend='Root/copiedstatus12/entry25andactualMCPdistinguishv34reviewedbaseline,v37failedpendingimage,andnew10240byteinputsourcecomponent. Reader43defaultreplyapprovalhistoricalafternewsourcefacts. TraceAnalystpreparedzeropredictions;sharedleaseunavailabledoesnotidentifyliveownerorjustifyverifiedwait. NativeChatdisplaystillunverified;headlessallowedandnounlockneeded.',
            training='Zerooptimizerupdates/newinferences thisturn. Priorcopied2updatecapabilityverified;earlier64updatequalitypilotbase0/4adapter0/4unpromoted. Need usefulgainonuntouchedporting/modding/restorationtasks and reliablelocalcoding. Preserveunrelatedmodels/jobs;newrunnamespace is required before retryingfrozenAnalystv1receipt.',
            game='Native191F4componentcodecompiledcompleteexistingdispatcher,butonlywalking/backward/runstates5/7/8qualified425caseswithsourceCdivision. Otherstates/physicalhelperbridge/originalcallerABI/stackadmission/yieldIRQunqualified;notgameimage. Fullsource-onlysame-console rebuilding,CPU/GPU/DSPintegration,audio/IRQ/widerfidelityremainunfinished. v37freshmatrixfail22858pixelsretained;controlledclockthresholdcauseisnotproofearlierfreshcauseisolated.',
            future_hardware=old['remaining_requirements']['future_hardware']),
        next_actions=[
            'Qualifyremaining13-state dispatcher paths and generic physicalhelperbridge with explicitscripteddependencies and strictglobalbus/argument/ABIchecks.425native/425connected terminal cases shouldnotbe rerunmerelyforreceipts. Then qualifyoriginal191F4callerABI,taskstackadmission and yielding/IRQ beforeanyimageintegration.',
            'Keepv34reviewedbaseline,v37pendingfailedmatrixgate,andinstalledsixcallercheckpointpreviewunchanged. Newsourcecomponent276bytefixturestackbelongs toCABItest,not the unrelated208byteDeckscenestack. No sourceuniqueroutine recoveredthisturn.',
            'Continuewhole-game CPU/GPU/DSPsource-onlysame-console reconstruction,audio/IRQ/fidelity and usefuluntouched-tasktrainingevaluation. RetrypreparedTraceAnalystonlyafteractualslotavailabilitychanges,andusefreshv2namespace since v1prompt/receipt/sourceare frozenin deliveryclosure. Do not callblockedwhileindependentprogressavailable.',
            'Copiedcomponentrebuild commandis make -f Makefile.portable;itsrelativeSDK/buildpaths handlepackagepathspaces. Preserveoriginalfailedcopiedbuildlogandstrict-GCCbraces/memcpyrepairs. Do notoverwritebyteguardedsourceorprototypebuildfiles.'
        ])
    n['do_not_restart']=old.get('do_not_restart',[])+[
        'Completed4readonly191F4entry/1A26Creturn/1A2C2worldinputtiminglanes;allprior180framerowsmatch',
        'Completed425connectedoriginaldispatcher/E588vsCcasesincluding194capturedwalkingspeed/remainders',
        'Completednative191F4CABIcomponent425walking/backward/runfixtures,10240bytes,276bytefixturestack',
        'CompletedcopiedSDKbuildv2byteidentitywithMakefile.portablepathspacesfix;v1failedlogretained',
        'PreparedTraceAnalystv1busyattemptzero generations;receipt/sourcefrozen,usefreshnamespaceonactualavailabilitychange',
        'CompletedRoot/copiedstatus12entry25andactualMCPnativecomponent/pendingimage/baseline/historicalReaderseparation'
    ]
    save(out/'goal-state.json',n);assert str(target)not in w['dependencies_sha256'];atomic(target,n)
    for source in [target,*[x for x in out.iterdir()if x.is_file()]]:clone(source,P/'workbench'/source.relative_to(ROOT))
    print(n['status'],flush=True)


if __name__=='__main__':main()
