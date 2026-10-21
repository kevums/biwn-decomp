"""Publish a tested but unpromoted image;retain the failed matrix-video gate."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    names=['native-record-loop-image-disc-build-v1','record-loop-image-fresh-preflight-v1','record-loop-image-fresh-reviewed-v1','record-loop-matrix-final-difference-v1','record-loop-image-fixed-prefix-reviewed-v1','local-record-loop-Repair-reviewed-v1']
    proofs={n:read(V/(n+'-current.json'))for n in names};deps={str(Path(__file__)):sha(__file__)}
    for n,g in proofs.items():
        assert g['status'].startswith('terminal_')
        for path,h in g.get('source_sha256',{}).items():assert sha(path)==h,path
        deps.update(g.get('source_sha256',{}));p=V/(n+'-current.json');deps[str(p)]=sha(p)
    b,q,f,m,prefix,repair=[proofs[n]for n in names]
    assert len(q['gate_names'])==23 and f['candidate_frames']==25004 and f['control_frames']==24966
    assert f['native_record_returns']==4836 and f['native_scene_returns']==5835 and f['native_record_copy_returns']==8663 and not f['native_record_matrix_returns']
    assert f['all_monitors_clear_and_quiescent']and f['final_video_equal']
    assert m['native_record_matrix_returns']==201 and m['original_record_matrix_returns']==266 and m['final_differing_pixels']==22858
    assert not m['baseline_final_video_gate_pass']and not m['final_full_pose_equal']and not m['final_video_equal']
    assert prefix['current_video_differences']==449 and repair['actual_Repair_predictions']==1 and not repair['strict_compile_pass']
    assert sha(b['derived_disc'])==b['derived_disc_sha256']
    out=V/'record-loop-pending-image-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
    packet=read(w['packet']);save(out/'before-packet.json',packet)
    baseline=dict(packet['latest_native_candidate']);assert baseline['candidate_frames']==25012 and baseline['native_record_returns']==4777
    old=packet['latest_source_development'];pending=dict(old)
    report=ROOT/'reports/BIWN v37 Pending Disc and Failed Matrix Video Comparison.txt'
    pending.update(status='terminal_v37_disc_tested_matrix_final_video_gate_failed_unpromoted',artifact_type='built_experimental_disc_tested_unpromoted_fidelity_gate_failed',directory=str(out),report=str(report),variant='v37 fused record-loop experimental disc;unpromoted after matrix-video comparison failure',profile='deck-shared-v37-record-loop-advance-v2',
        candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],module_bytes=54060,native_module_bytes=54060,native_code_bytes=b['linked_component_bytes'],reservation_bytes=b['component_bytes'],boot_copy_bytes=b['copy_component_bytes'],initial_heap_bytes=b['initial_heap_bytes'],new_disc_built=True,
        component_and_readonly_observer_qualification_verified=True,qualification_gate_count=23,final_address_gate_groups=8,final_address_scene_cases=772,actual_disc_provider_body_cases=512,actual_whole_scene_provider_cases=772,copied_final_module_byte_identical=True,
        fresh_gameplay_tested=True,standard_route_pass=True,standard_route={k:v for k,v in f.items()if k!='source_sha256'},matrix_route={k:v for k,v in m.items()if k!='source_sha256'},fixed_input_prefix=prefix['comparison']['video_sha256'],fixed_input_review=str(V/'record-loop-image-fixed-prefix-reviewed-v1-current.json'),
        final_matrix_video_comparison_pass=False,final_matrix_full_pose_equal=False,fresh_gameplay_verified=False,new_fresh_gameplay_verified=False,native_disc_fidelity_verified=False,default_promoted=False,gameplay_or_fidelity_promoted=False,whole_game_complete=False,installed_preview_changed=False,
        separate_local_Repair_predictions=1,separate_local_Repair_seconds=19.48,separate_local_Repair_status=repair['status'],separate_local_Repair_compile_pass=False,model_source_installed=False,new_training=False,optimizer_updates=0,
        next_action='Investigate the failed exact final-video comparison using expanded14bitfractional player and camera observations and controlled equal-state rendering/logic diagnostics. Preserve the original mismatched frames and do not tune controller endpoints,mask state or replay until a new diagnostic question/source change justifies it. Keep v34baseline and preview unchanged. Continue remaining CPU/GPU/DSP/HLEsource,audio/IRQ/same-console rebuild,useful training and copied-weight nativeChat usability.')
    packet['previous_latest_source_before_built_v37_test']=old
    packet['pending_native_candidate']=packet['latest_source_development']=packet['native_geometry_record_loop_progress']=pending
    packet['native_scene_draw_progress']['pending_record_loop_candidate']=pending
    packet['native_scene_draw_progress']['next_action']=pending['next_action']
    packet['local_record_loop_Repair_progress']={k:v for k,v in repair.items()if k!='source_sha256'}
    if 'local_record_loop_Author_progress'in packet:packet['local_record_loop_Author_progress'].update(repair_predictions=1,repair_status=repair['status'])
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    packet['Reader40_prepared']=True;packet['Reader40_prediction_verified']=False;packet['current_status_renderer']='show_native_status_v10.py';packet['portable_entry_version']=19
    packet['checked_current_summary']='Reviewed baseline remains v34:standard25012/24966frames,5774scene/4777record-display/8567copy/0record-matrix returns,8717intermediatevideo differences,matchingfinalvideo,scene168/208,sampledouter-activeheap14320each(notglobalminimum);separatebaseline268route190native/266originalmatrixreturns andmatchingfinalvideo. Newer coordinatorv37disc is built and unpromoted:module54060bytes,linked95152,reservation263744,bootcopy121536,initialheap134144;all23component/provider/alias/observergates and copiedfinalbuildpass. v37standardfresh25004/24966frames:5835scene,4836record/display,8663copy,0matrix,8698videodifferences,matchingfinalvideo;sampledouter-activeheap14384each. v37separate268route22532/22361frames:201native/266original-record matrixreturns,monitorsclear/quiescent,BUT exactfinalvideo gatefails22858pixels inleftviewport. IntegerXZ/scene/floor/headingagree;14bitplayerfractions and camera state differ,cameraZword1696/1697. Cause notisolated,no state mask or passingfidelityclaim. v37fixed1000inputprefix449videodifferences(first378),twoheldbuttonRAMdifferences;layoutchanges prevent causal speed inference. Both audiooutputs silent. LocalAuthor16.92s and oneRepair19.48s return identicalfailedcode;no sourcefromthem adopted and zero optimizerupdates. Earlier base/adapterqualitypilot0/4each. Prior localv35block remains an older unadoptedcomponent. Preview unchanged;fullsource-onlysameconsole rebuild,broadfidelity/audio/IRQ,usefultraininggain and copiedweightnativeChat usability remainopen.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
    assert packet['latest_native_candidate']==baseline,'Do not promote the failed-output candidate'
    report.write_text('BIWN v37 — tested candidate,final matrix-video gate failed\n\n'
        'v34remains the reviewed baseline;the installed checkpoint preview is unchanged. The newer v37disc contains the coordinator fused loop-tail source. Module54060bytes,linkednative95152,reservation263744,bootcopy121536,initialheap134144. Eight exact-address/startup/heap groups plus all23provider/fallback/alias/connected/publicbus/display/copied-build/read-only-observer prerequisites pass. This is not whole-game fidelity.\n\n'
        'v37standard fresh HLECDboot:25004candidate/24966controlframes,5835native scene returns,4836record/display/rotation/clear returns,8663copy and0record-matrix. Allmonitorsclear/quiescent;8698pairedvideo differences,544frontendbuttonschedule and557latchedbutton differences. Finalvideo and selectedintegerfields agree. Scene Cstack168/208,outer164/224;sampledouter-activefreeheap14384each,notglobalminimum.\n\n'
        'Separate ordinary-control scene268route:22532/22361frames,201native/266original-record matrixreturns;static114region4anglebyte0. Allmonitorsclear/quiescent and sameindoorwaypointJSON consumed. Exactfinalvideo comparison FAILS:22858of78240pixels differ,withinrectangle[1,38,225,218). The failed reviewer and both original PNG/rawframes remain saved. Integerposition6233/35425,scene268,floor0,heading189 agree,but this is not fullpose equality. Player14bitfractionwords are[3225,0,4172]candidate/[3534,0,74]control. Camera words[88,65504,1696]/[88,65504,1697]and camera fractions also differ. The opposite finalhash never appears in either last500frames;do not dismiss this as demonstrated alternatingframephase. Different adaptiveinputs and pose states prevent isolating a rendering-code cause. No mask,statepatch,controllerretuning or passingfinal-video relabeling.\n\n'
        'v37equal-navigation1000frameprefix:449video differences,first378;CPU/GPUfirst376,DSPstatesagree,heldbuttonRAMdiffers on2frames first634. Priorv34prefix450differences;new/oldoriginal-scenecontrols differ101video frames,so this is not an isolated benefit claim. Both audiooutputs remain silent. Truncatedendpendingcalls and independentfences are retained,not complete-routeacceptance.\n\n'
        'Author16.92seconds andactualRepair19.48seconds produced byte-identical code failing strictcompilation. The actualRepairprompt matches its preparedprompt;failedcompile evidence reusedbyexactcandidateidentity,no redundantcompile. Exactprompts/responses appended to savedRoot/copiedindices. Currentlooptail code is coordinator-authored with earlier linkedhybridattribution retained. No sourcefromthesetrials adopted,no optimizerupdates or usefultrainedqualitygain. NativeLMStudioChatdisplay remainsunverified;OSreportedlocked andheadlessworkcontinued withoutaskingunlock.\n\n'
        'v37 is an unpromoted candidate. Its final-video failure is retained;completed unit/route coverage does not replace that failed requirement. FullreadableCPU/GPU/DSP/HLEsource,video/audio/IRQ/same-console rebuilding,usefultraining and frontendquality remain unfinished.\n\n'+pending['next_action']+'\n\nCandidate: '+b['derived_disc']+'\nMatrixdifference evidence: '+m['directory']+'\n')
    save(out/'pending-candidate.json',pending);save(out/'current-status-packet.json',packet)
    for name in ['show_native_status_v10.py','portable_biwn_entry_v19.py','portable_biwn_entry_v20.py','run_deck_status_live_v40.py']:
        p=ROOT/'scripts'/name;deps[str(p)]=sha(p)
    for name in ['record-loop-image-qualification-pipeline-v3-current.json','local-record-loop-advance-repair-v1-current.json']:
        p=V/name;deps[str(p)]=sha(p)
    deps[str(report)]=sha(report);deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
    normalized={}
    for path,h in deps.items():
        real=Path(path).resolve();assert real.is_relative_to(ROOT)and sha(real)==h,path;normalized[str(real)]=h
    deps=normalized
    for path in deps:clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    clone(ROOT/'scripts/portable_biwn_entry_v19.py',P/'workbench/portable_biwn.py')
    clone(ROOT/'scripts/portable_biwn_entry_v20.py',P/'workbench/portable_biwn_try_v20.py')
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    save(V/'record-loop-pending-image-reviewed-v1-current.json',dict(status=pending['status'],directory=str(out),report=str(report),pending_candidate=str(out/'pending-candidate.json'),latest_reviewed_baseline_preserved=True,new_predictions=0,new_training=False))
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    print('v37negative final-video gate published;v34baseline preserved,preview unchanged.',flush=True)

if __name__=='__main__':main()
