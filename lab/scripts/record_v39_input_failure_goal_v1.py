"""Record fresh failure, concrete header defect and unfinished full objective."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    timings={}
    for lane in ['Root','copied']:
        timing=read(V/f'v39-input-failure-{lane}-status-timing.json')
        text=(V/f'v39-input-failure-{lane}-status-cli.txt').read_text()
        assert timing['exit_code']==0 and timing['lines']==12 and len(text.splitlines())==12
        assert '34619'not in text and '34,619'in text and '25,009'in text and 'failed'in text and '878'in text
        timings[lane]=timing
    for lane in ['current','copied']:
        r=read(V/f'v39-input-failure-delivered-{lane}-MCP-response.json')
        assert r['status'].startswith('terminal_actual_')
    manifest=V/'native-Deck-current-status-v1-current.json';wrapper=read(manifest);packet=read(wrapper['packet'])
    progress=packet['current_resource_arena_image_progress'];assert not progress['default_promoted']
    header_path=V/'v39-frame-acquire-header-fault-reviewed-v1-current.json';header=read(header_path)
    assert header['metadata_bytes_overwritten_each_case']==38 and header['isolated_native_entry_cases']==2 and not header['fix_implemented']
    target=V/'goal-continuation-current.json';old=read(target)
    out=V/'v39-input-failure-goal-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old)
    jobs=[]
    for name,script in [('input-arena-image-qualification-pipeline-v2','run_input_arena_image_qualification_pipeline_v2.py'),('native-input-arena-image-fresh-input-v1-candidate','run_native_input_arena_image_input_route_v1.py'),('native-input-arena-image-fresh-input-v1-control','run_native_input_arena_image_input_route_v1.py'),('v39-input-transition-fault-trace-v1','trace_v39_input_transition_fault_v1.py'),('v39-input-transition-fault-trace-v2','trace_v39_input_transition_fault_v2.py'),('v39-input-structured-reader-v1','run_v39_input_structured_reader_v1.py')]:
        r=read(V/(name+'-current.json'));assert r['status'].startswith('terminal_') and not r.get('child_pid')
        command=subprocess.run(['ps','-p',str(r['pid']),'-o','command='],capture_output=True,text=True).stdout
        assert script not in command,(name,command)
        jobs.append(dict(name=name,pid=r['pid'],status=r['status'],matching_live_process=False))
    save(out/'own-worker-audit.json',dict(jobs=jobs,unrelated_jobs_inspected=False,all_recorded_own_workers_terminal=True))
    frontend=V/'v39-input-failure-checked-frontend-v1.json'
    save(frontend,dict(status='terminal_status22_entry35_Root_copied_CLI_and_actual_MCP_verified',default_lines=12,CLI_timings=timings,concurrent_status_QA_not_inference_latency=True,new_predictions=0,new_training=False))
    state=dict(old)
    state.update(status='active_v39_finite_checks_pass_fresh_input_failed_frame_acquire_header_defect_identified',recorded_at=datetime.now(timezone.utc).isoformat(),goal_status='active',full_objective_complete=False,blocked=False,previous_goal_state=str(out/'previous-goal-state.json'),previous_goal_turn_classification='No progress on decomp: the immediately preceding user turn received verified preview launch instructions; pending qualification was revalidated at continuation start and found terminal.',current_turn_classification='Progress: completed finite final-address/alias/read-only monitor gates and27-gatepreflight;ran freshcandidate34619/control25009. Nativeinputtransitionfailed,controlcompleted. TwofreshdiagnosticscapturefirstoddPC4F13/frame8959andtwoisolatedpinnedCPUentryreplaysprove1AC68wrappercontextstartstask-26andwritesall38metadata bytes. Defectidentified,notfixed. Status22entry35Root/copiedCLIandactualMCPverified;oneReaderleaseattempt0predictions;no weightsorpreviewchange.',current_status_manifest=str(manifest),current_status_packet=wrapper['packet'],report=progress['report'],current_source_component=packet['current_native_input_prototype_progress'],current_resource_arena_image_progress=progress,unqualified_resource_arena_image=progress,new_disc_built=False,new_predictions_this_turn=0,optimizer_updates_this_turn=0,new_training_this_turn=False,new_unique_original_functions_recovered_this_turn=0,installed_preview_changed=False,current_status_renderer=str(ROOT/'scripts/show_native_status_v22.py'),portable_entry_version=35,current_status_default_lines=12,current_frontend_actual_review=str(frontend),concurrent_CLI_QA_timings=timings,current_native_Chat_verified=False,new_native_UI_attempt_this_turn=False,current_default_Reader_version=43,current_default_Reader_current_source_approved=False,current_structured_input_Reader=read(V/'v39-input-structured-reader-v1-current.json'),current_frame_acquire_header_fault=header,own_worker_audit=str(out/'own-worker-audit.json'),new_game_execution_this_turn=dict(new_discs=0,fresh_routes=2,fresh_candidate_frames=34619,fresh_control_frames=25009,candidate_fresh_route_qualified=False,control_fresh_route_completed=True,diagnostic_fresh_replays=2,diagnostic_stop_frame_each=8959,isolated_captured_frame_acquire_entry_cases=2,unique_full_game_paths_added=False),local_model_review='Prepared exact current structured Reader prompt/schema/evidence. Copied interpreter refused root-script access by design;rootSDKlaunch stopped at unavailable sharedlease beforemodelcatalog/generation. Zero newpredictions/optimizerupdates;no localAuthor/Repairor nativeChatattempt. Coordinatorauthoredthiscontinuation.',next_action='Replace lower-level1AC68compiledframe-acquire guest-stack context/Cstack with bounded private storage and explicit ownership/nesting policy;preserve its full original control flow/helper boundary semantics. Qualify captured header-counterexample,CPU/RAM/provider/alias/IRQ and copied rebuild,then build a separate candidate and rerun changed-code fresh outdoor/indoor/fixed-input routes. Preservev34baseline,failedv37/v38/v39andDesktoppreview. Continue fullsource-onlyCPU/GPU/DSP/audio/firmware/fidelity/console,usefultrainedgain,nativeChat/easyinferenceandfuture256GBhardware profile.')
    state['current_context_limits']=dict(old['current_context_limits'],observer_qualified=True,all_final_address_gates_qualified=True,fresh_gameplay_qualified=False,fresh_native_input_transition_failed=True,lower_level_frame_acquire_context_before_task_bytes=26,actual_original_task_metadata_clobbered_bytes=38,observed_user_stack_below_task_bytes=138,first_odd_PC=0x4f13,frame_end_exception_loop_PC=0xca2d,frame_acquire_header_defect_reproduced_cases=2,frame_acquire_header_defect_fixed=False)
    state['do_not_repeat_completed_work']=list(old.get('do_not_repeat_completed_work',[]))+['v39retained8groups/772bridge/finitealiasobserver27preflightgates complete;do not replay for receipts.','Freshv39nativeinputcandidate34619failsbeforeDeck/control25009completes. Two diagnosticreplays8959andtwoisolatedentry-storecases prove38byte1AC68taskmetadataoverwrite. Replaysnowrequirechangedcodeornewunresolvedquestion.','Readercurrentstructuredprompt prepared;sharedleaseunavailable0predictions. No model ownership inferred.','Root/copiedstatus22entry35/12lineCLI/actualMCPverified;oldbaselineandfailedimages/previewpreserved.']
    atomic(target,state);clone(target,P/'workbench/verification'/target.name)
    save(out/'record.json',dict(status='terminal_progress_recorded_goal_active',new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in [Path(__file__),manifest,header_path,frontend,*[V/f'v39-input-failure-{lane}-status-timing.json'for lane in ['Root','copied']],*[V/f'v39-input-failure-delivered-{lane}-MCP-response.json'for lane in ['current','copied']]]}))
    print(state['status'],flush=True)


if __name__=='__main__':main()
