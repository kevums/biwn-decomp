"""Publish bounded checks and fresh failure without promoting the candidate."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    names=['input-arena-image-fresh-preflight-v1','v39-input-route-failure-reviewed-v1','v39-input-transition-fault-trace-v1','v39-input-transition-fault-trace-v2','v39-input-structured-reader-v1','v39-frame-acquire-header-fault-reviewed-v1']
    receipts={n:read(V/(n+'-current.json'))for n in names}
    pre,failure,trace1,trace2,reader,header=[receipts[n]for n in names]
    assert pre['status']=='terminal_v39_exact_component_alias_and_readonly_observers_qualified_for_fresh'
    assert failure['status']=='terminal_v39_fresh_native_input_route_failed_control_completed_cause_open'
    assert trace1['status']==trace2['status']=='terminal_transition_diagnostic_fault_recorded'
    assert reader['status']=='terminal_shared_slot_busy_zero_predictions' and reader['new_predictions']==0
    assert header['source_defect_identified'] and header['isolated_native_entry_cases']==2 and header['metadata_bytes_overwritten_each_case']==38
    candidate,control=failure['candidate'],failure['control']
    assert candidate['exact_executed_frames']==34619 and control['exact_executed_frames']==25009
    assert candidate['observations']['resource-input-observation']['input_pending']==1
    assert candidate['observations']['gameplay-observation']['acquire_user_stack_outside']==878
    assert not failure['comparison']['final_video_equal'] and failure['comparison']['final_differing_pixels']==45249
    deps={str(Path(__file__)):sha(__file__)}
    for name,r in receipts.items():
        assert r['status'].startswith('terminal_')
        for path,digest in r.get('source_sha256',{}).items():assert sha(path)==digest,(name,path)
        deps.update(r.get('source_sha256',{}));path=V/(name+'-current.json');deps[str(path)]=sha(path)
        for p in Path(r['directory']).rglob('*'):
            if p.is_file()and'__pycache__'not in p.parts:deps[str(p)]=sha(p)
    manifest=V/'native-Deck-current-status-v1-current.json';wrapper=read(manifest)
    for path,digest in wrapper['dependencies_sha256'].items():assert sha(path)==digest,path
    packet=read(wrapper['packet']);previous=packet['current_resource_arena_image_progress']
    out=V/'v39-input-failure-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'before-packet.json',packet)
    report=ROOT/'reports/BIWN v39 Fresh Input Failure.txt'
    detail=dict(candidate_frames=34619,control_frames=25009,candidate_route_pass=False,control_route_pass=True,candidate_input_calls=4375,candidate_input_returns=4374,candidate_input_pending=1,lower_level_acquire_pending=1,lower_level_acquire_stack_outside_observations=878,candidate_resource_returns=4,control_resource_returns=11,control_input_returns=4777,control_sampled_outer_active_heap_bytes=3056,candidate_sampled_outer_active_heap_available=False,final_video_equal=False,final_differing_pixels=45249,endpoints_have_different_durations=True,cause_resolved=False,trace_first_odd_frame=trace2['fault']['frame'],trace_first_odd_PC=header['first_odd_PC'],trace_frame_end_loop_PC=trace2['fault']['pc'],trace_task=trace2['fault']['task'],frame_acquire_context_before_task_bytes=26,original_task_metadata_bytes_overwritten=38,minimum_observed_SP_below_task_bytes=138,header_defect_reproduced_cases=2,fix_implemented=False)
    report.write_text(
        'BIWN — v39 fresh input comparison\n\n'
        'The new native-input v39 image is rejected for promotion. Its original-input control completed25,009frames and the400-frame Deck trial. Candidate executed34,619frames but never reached that trial. One of4,375input calls did not return; a lower-level1AC68asset acquire remains pending with878stack-outside observations. This is a fresh transition failure,not a completed game or a passing native-input route.\n\n'
        'Both lanes retain the same v39scene/resource layout and algorithms;control restores the six-byte inputJSR at1A266. Candidate resource acquisition itself records4entries/returns;control11,with no resource ownership,private-C-stack or input-C-stack errors reported by the new monitor. Those clean counters do not waive the pending input/acquire or stack-outside evidence. The candidate never exercised the later Deck/outer route,so itsFFFFFFFFunsampled heap sentinel is not a measured free-heap value. Control sampled3,056bytes while outer-active,not a global minimum.\n\n'
        'The endpoints have45,249different pixels and different selected RAM fields,at unequal durations. That is not an isolated rendering-cause test. Raw video,RAM,CPU samples,audio,observer counters and failed protocol are preserved.\n\n'
        'A diagnostic fresh replay finds the oddPC0xCA2Dexception loop at frame8,959,task0xC2128. The first ring was overwritten within the frame;the second freezes at its first oddPC. The frozen ring first enters oddPC0x4F13before the0xCA2Dloop. It captures two1AC68compiled frame-acquire entries whose logical context starts26bytes before task0xC2128. MOVEMoverwrites the first34metadata bytes and its logical-SP store the last4. Two isolated pinnedCPUentry-store replays reproduce all38metadata overwrites and match an independent full2MBRAM oracle. The ring observes userSP138bytes below the task base. This is a concrete header-clobber defect in the lower-level512-gap wrapper;it does not establish that all failure causes are resolved,and no fix is implemented. No source/image,guest RAM,CPU/task state or pose/timer/controller normalization was applied.\n\n'
        'The prior final-address retained modules,eight component/startup groups,772scene bridge cases,finite provider/fallback/alias gates and read-only observers pass. The new resource/input observer has73fault controls/314CPU-and-RAM-readonly calls,16isolated ownership-order controls(8same-task rejected/8different-task accepted),32actual direct-wait observer-off/on pairs(42,912calls/408whole-RAMboundary checks)and27actual controlled input pairs(182,893calls;9native/18original). These are finite checks;production same-task reentry guards were not added. The startup/caller/wait/selectedIRQ/copied-piece results in the previous report remain scoped evidence,not a waiver of this gameplay failure.\n\n'
        'WHO DID WHAT\nCoordinator prepared final-address gates,authored the resource/input observer and its checks,ran the two fresh boots,reviewed raw failure artifacts and wrote the targeted diagnostics. No cloud subagents or new local model generations ran. The exact current local Reader prompt/schema/evidence are saved in '+reader['directory']+'. A copied-interpreter attempt to open the root script was refused by its origin guard;the root SDK launch then stopped before model inspection/generation because the shared lease was unavailable. No unrelated job was inspected or interrupted,no optimizer update or new weights. Reader43remains earlier evidence;the new structuredReader is unvalidated.\n\n'
        'RUN THE PLAYABLE TEST\nOpen Desktop BIWN Test Preview.app,click the window,Pstarts/pauses,arrowsmove,Shift+UporC+Upruns,Zattacks/reads,1thenDopensDeck,Esccloses. This is the earlier outdoor checkpoint,not v39or a fullgame.\n\n'
        'NEXT\nMove the lower-level1AC68frame-acquire saved context and Cstack off the original task stack,qualify ownership/nesting and helper returns,and fix the transition failure,qualify changed code and rerun relevant fresh outdoor/indoor/fixed-input routes. Continue source-onlyCPU/GPU/DSP/audio/firmware/IRQ/fidelity and physical-console work,useful trained gain,native LMStudioChat ease,and eventual256GBhardware qualification. Reviewedv34,failedv37/v38and Desktop preview remain unchanged.\n')
    progress=dict(previous,status='v39_finite_gates_pass_fresh_native_input_transition_failed_unpromoted',report=str(report),observer_qualified=True,all_final_address_gates_verified=True,fresh_gameplay_verified=False,fresh_gameplay_executed=True,fresh_native_input_route_qualified=False,fresh_input_failure=detail,resource_input_observer_fault_controls=73,resource_input_observer_owner_order_controls=16,resource_input_actual_wait_observer_pairs=32,resource_input_actual_fullcaller_observer_pairs=27,production_reentry_guards_added=False,same_task_alias_reentry_qualified=False,game_frames=34619+25009,new_predictions=0,optimizer_updates=0,new_training=False,default_promoted=False,installed_preview_changed=False)
    component=dict(packet['current_native_input_prototype_progress'],status=progress['status'],report=str(report),fresh_gameplay_verified=False,image_partial_qualification=progress,scope='v39finite final-address component/alias/read-only observer checks pass,but actual native-input fresh transition fails;control completes. Lower-level acquire stack/return cause unresolved. Unpromoted;no preview or model weight change.')
    packet['current_resource_arena_image_progress']=packet['unqualified_resource_arena_image']=progress
    packet['current_native_input_prototype_progress']=packet['latest_source_development']=component
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    packet['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v35.py')
    packet['current_status_frontend_progress']=dict(status='status22_entry35_prepared_actual_checks_pending',renderer=str(ROOT/'scripts/show_native_status_v22.py'),portable_entry_version=35,default_brief_lines=12,new_predictions=0,detailed_report=str(report))
    packet['current_structured_input_Reader_progress']=reader
    packet['checked_current_summary']='Reviewedv34andDesktoppreviewunchanged. v39final-address component/alias/readonlyobserverspass,butnativeinputfreshtransitionFAIL:34619frames,noDecktrial,1input/1low-levelacquirepending,878acquirestack-outsideobservations;originalinputcontrolcompletes25009frames. Endpointvideo45249pixelsdifferentatunequaldurations,causeopen. DiagnosticoddPCatframe8959. No promotion/newpredictions/weights. Source-onlyfullgame,fidelity/console,usefultraining/nativeChat/futurehardwareunfinished.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
    save(out/'current-status-packet.json',packet);save(out/'facts.json',detail)
    for name in ['show_native_status_v22.py','portable_biwn_entry_v35.py','run_v39_input_structured_reader_v1.py']:
        p=ROOT/'scripts'/name;deps[str(p)]=sha(p)
    deps[str(report)]=sha(report);deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
    for path,digest in deps.items():
        p=Path(path);assert p.is_relative_to(ROOT)and sha(p)==digest,path
        clone(p,P/'workbench'/p.relative_to(ROOT))
    clone(ROOT/'scripts/portable_biwn_entry_v35.py',P/'workbench/portable_biwn.py')
    wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps})
    atomic(manifest,wrapper);clone(manifest,P/'workbench/verification'/manifest.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    atomic(V/'v39-input-failure-delivered-v1-current.json',dict(status='terminal_v39_fresh_failure_published_unpromoted',directory=str(out),report=str(report),source_sha256=deps,new_predictions=0,new_training=False))
    print('Published v39 fresh native-input failure; baseline and preview preserved.',flush=True)


if __name__=='__main__':main()
