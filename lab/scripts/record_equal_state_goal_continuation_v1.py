"""Record completed work and the full unfinished objective; no goal status change."""
import os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    current=V/'goal-continuation-current.json';old=read(current)
    w=read(V/'native-Deck-current-status-v1-current.json')
    assert str(current)not in w['dependencies_sha256']
    packet=read(w['packet']);r=read(V/'record-loop-equal-state-reviewed-v3-current.json')
    assert r['actual_recovered_C_integrator_transitions']==627
    assert not packet['pending_native_candidate']['default_promoted']
    assert packet['current_copied_Reader_progress']['default_reader_version']==43
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out=V/'equal-state-goal-continuation-v1'/stamp;out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old)
    # Inspect only PIDs recorded by these twelve finite diagnostic jobs.
    jobs=[]
    for origin in ['candidate','control']:
        for lane in ['native','original','replica']:
            for mode in ['stationary','motion']:
                pointer=V/(f'record-loop-equal-state-{origin}-{lane}-v1-current.json'if mode=='stationary'else f'record-loop-equal-state-motion-{origin}-{lane}-v2-current.json')
                j=read(pointer);assert j['status']=='terminal_saved_state_equal_origin_diagnostic_pending_review'
                result=subprocess.run(['ps','-p',str(j['pid']),'-o','pid=,command='],capture_output=True,text=True)
                expected='run_record_loop_equal_state_diagnostic_v1.py'if mode=='stationary'else'run_record_loop_equal_state_motion_v2.py'
                assert expected not in result.stdout,(j['pid'],result.stdout)
                jobs.append(dict(origin=origin,lane=lane,mode=mode,pid=j['pid'],recorded_status=j['status'],matching_live_worker=False))
    save(out/'own-worker-audit.json',dict(status='terminal_all_twelve_recorded_workers_terminal_no_matching_live_PIDs',jobs=jobs,unrelated_jobs_inspected=False))
    save(out/'native-Chat-attempt.json',dict(status='observation_timeout_no_Chat_display_verification',tool='cua.getApp(LM Studio)',
         result='Sky Computer Use request timed out',elapsed_seconds=120.7549,new_predictions=0,unlock_requested=False,
         scope='A native-window read timed out;this does not establish lock state or a stopped external process. No native-Chat inference was launched.'))
    n=dict(old)
    n.update(status='active_v37_equal_state_diagnosed_Reader43_default_full_game_training_and_Chat_quality_open',
         recorded_at=datetime.now(timezone.utc).isoformat(),
         previous_goal_turn_classification='Progress:verified saved Desktop app/Python GUI entry and keyboard controls for requested ease of use. Earlier goal work also built v37 and recorded standard pass/matrix final-video failure;those terminal results are preserved rather than replayed.',
         current_turn_classification='Progress:twelve exact-snapshot stationary/motion lanes plus four unchanged replay controls narrow scene timing. Stationary pixels agree at both saved poses;fixed Up input yields22/23nonzero movement steps at one origin. Existing recovered C integrator matches627captured transitions. Reviewed existing Reader43and installed it as copied default;Root/copied status and actualMCP delivery verified separately. Exact three Readertrials appended to frozen indices;no new model predictions or weight updates this turn.',
         full_objective_complete=False,goal_status='active',previous_goal_state=str(out/'previous-goal-state.json'),ongoing_finite_workers=[],
         current_status_manifest=str(V/'native-Deck-current-status-v1-current.json'),
         current_gameplay_baseline='v34 signed record strides;standard25012/24966frames,4777record/displayreturns,8717video differences,finalvideoagrees. Additionalmatrix190/266returns/finalvideoagrees. Preview remains older six-caller outdoor checkpoint.',
         pending_candidate='v37loop-tail image54060bytes,23prerequisite gates/eightfinaladdressgroups pass;standard25004/24966finalvideoagrees. Additionalmatrix201/266returns but finalvideo differs22858pixels and expandedpose differs. Fixedprefix449/1000differs;no isolated improvement overv34. Candidate unpromoted;failed exact gate retained.',
         new_game_execution_this_turn=dict(saved_snapshot_diagnostic_lanes=12,frames_each=180,unchanged_replica_pairs=4,fresh_routes=0,new_discs=0,host_pose_or_timer_writes=0,scene_entry_code_interventions=4,code_bytes_per_intervention=10),
         new_predictions_this_turn=0,optimizer_updates_this_turn=0,new_unique_original_functions_recovered_this_turn=0,
         local_model_review='Reader43prediction was generated in prior goal work and reviewed this turn:99words,two paragraphs,8.27generationseconds,18.94seconds warmCLI firsttext/25.18complete including setup/evidence. Supplied facts/units/causal scope pass;default copied Reader43/status11/entry24installed. Reader41/42remain rejected;199Root/200copied frozen prompt/transcript records. Not heldoutquality/traininggain/nativeChat proof.',
         completion_audit='Unproven:source-only whole-game same-console rebuild,full CPU/GPU/DSP/HLEcoverage,audio/IRQ/wider fidelity,useful untouched-task training gain,copied-weight nativeChat ease and future256GBhardware measurements remain incomplete. No completion,blocked or pause status requested.',
         remaining_requirements=dict(
             local_frontend='Current copied Reader43 CLI approved for one supplied snapshot,firsttext18.94s/complete25.18s warm. Root/copied savedstatus and actualMCP delivery expose baseline/pendingfailure/diagnostic scopes. Native LM Studio window inspection timed out;no Chat display verified and no unlock requested. Need ordinary copied-weight Chat ease and useful coding task success.',
             training='Zero optimizerupdates this turn. Prior copied2update training capability verified;earlier64update quality pilot base0/4adapter0/4unpromoted. Actual loop Author/Repair outputs failed and no sourcefromthose adopted. Need measured useful gain on untouched porting/modding/restoration tasks;preserve unrelated models/jobs under shared lease.',
             game='v37remains unpromoted after exactfreshmatrixvideo failure. New exactstate diagnostic supports stationary renderer equivalence at two poses;worldcadence differs under same fixedUp input. Existing C integration matches627actualcaptured transitions;no newfunctions claimed. Need attribute191F4dt/remainder/held-input transitions and scene timing,then resolve full CPU/GPU/DSP/HLEsource-only rebuilding,audio/IRQ/arbitraryreentry/physical and broader visual fidelity.',
             future_hardware='CopiedSDK/runtime/model registration/inference and training capability measured on this64GBMac. Future256GBcapacity,concurrency and performance unmeasured;do not infer futurehardware verification from this machine.'),
         next_actions=[
             'Do not rerun the completed12saved-state lanes or627actual-C checks. Add read-only191F4entry/1A26Cexit timing,held-button,speed/remainder observations to a separately versioned controlled motion diagnostic to attribute the22versus23step effect. Event49BAC is raw edge/input data,not a verified held-button label.',
             'Preserve the failed v37freshmatrixexactvideo gate,v34baseline and unchangedpreview. Do not tunecontrollerendpoints or normalizeposes/timers merely to obtain matching images. Fixed180-frame diagnostics can leave one native scene call active;do not label them quiescent/full-guardfreshproofs.',
             'Continue complete readableCPU/GPU/DSP/HLEsource-only same-console game rebuilding and audio/IRQ/fidelity. Improve useful localcoding and untouched-task training quality,plus copied-weight nativeChat usability when the UI tool is available;no unlock request is needed.'
         ])
    n['do_not_restart']=old.get('do_not_restart',[])+[
        'Completedv37discbuild/eightfinaladdressgroups/23componentprovideraliasobservercopiedgates',
        'Completedv37standardfresh25004/24966andmatrix22532/22361;matrixfinalvideoFAIL22858pixels remains failed',
        'Completedv37fixed1000prefix449differences andfourendpoint expandedpose/crossversionofflineanalysis',
        'CompletedactualRepair19.48s identical failedAuthor;no redundantcompile/adoption',
        'CompletedactualReader41/42/43predictions;41counter/lengthfailure,42units/causalfailure,43providedfacts99wordpass',
        'Completed12stationary/motion restored-state lanes and4unchangedreplicas;627actualrecovered-C transitionchecks',
        'Reviewerharnessv1wrongquiescentcount andv2Ctokenization failures preserved;v3fixes reviewer withoutgame replay',
        'CompletedRoot/copiedReader43default/status11/entry24andactualMCP delivery;do notreplayinference for statusmetadata'
    ]
    save(out/'goal-state.json',n);atomic(current,n)
    for source in [current,*[p for p in out.iterdir()if p.is_file()]]:
        clone(source,P/'workbench'/source.relative_to(ROOT))
    print(n['status'],flush=True)


if __name__=='__main__':main()
