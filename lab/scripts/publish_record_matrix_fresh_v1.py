"""Publish terminal fresh matrix coverage without combining independent routes."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    rp=V/'record-matrix-268-fresh-reviewed-v1-current.json';r=read(rp)
    assert r['fresh_record_matrix_path_verified'] and r['all_monitors_clear_and_quiescent']
    assert r['native_record_matrix_entries']==r['native_record_matrix_returns']==190
    assert r['original_record_matrix_entries']==r['original_record_matrix_returns']==266
    assert r['static_angle']==0 and r['host_guest_RAM_writes']==r['snapshot_restores']==0
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in {**w['dependencies_sha256'],**r['source_sha256']}.items():assert sha(path)==h,path
    out=V/'record-matrix-fresh-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    packet=read(w['packet']);save(out/'before-packet.json',packet)
    standard=dict(packet['latest_native_candidate'])
    assert standard['candidate_frames']==25012 and standard['native_record_matrix_returns']==0
    facts={k:v for k,v in r.items()if k!='source_sha256'}
    facts.update(profile='deck-shared-v34-record-strides-v1',artifact_type='additional_fresh_route_same_experimental_disc',
        standard_route_native_matrix_returns=0,standard_route_counters_replaced=False,
        control_scope='Same-layout v34 image with only the ten original scene-entry bytes restored; global native copy/matrix/wait redirects retained. Not a pristine original disc.',
        fresh_coverage_scope='Ordinary controls from fresh HLE CD boot, static type114 in indoor scene268 region4, actual angle byte0. One natural matrix path; not every model/angle or arbitrary IRQ.',
        final_render_batch_regions={'candidate':3,'control':4},
        matched_final_video_is_not_full_game_fidelity=True,
        authorship='Existing coordinator-authored v34 record source and stride adaptation; prior linked hybrid attribution retained. Read-only watcher and route controller are coordinator work. No new model prediction or weight update.')
    report=ROOT/'reports/BIWN Fresh Record Matrix Route Review.txt';facts['report']=str(report)
    packet['record_matrix_fresh_progress']=facts
    packet['native_scene_draw_progress']['record_matrix_fresh_coverage']=facts
    records=packet['native_geometry_records_progress']
    records['record_matrix_fresh_coverage']=facts
    records['standard_route_native_record_matrix_fresh_path_verified']=False
    records['native_record_matrix_fresh_path_verified']=True
    records['native_record_matrix_fresh_path_scope']='Additional scene268 fresh route:190 native matrix returns. Standard route remains zero.'
    records['fresh_scene_native_returns']=records['native_scene_returns']
    records['final_disc_providers']='Inherited global native E3E0/E220/E098. Body512 and scene772 checks use the same inherited providers. Standard route has8567copy/0record-matrix returns; separate scene268 route has22566copy/190record-matrix returns.'
    action='Measure the current v34 identical-input prefix and investigate intermediate video/input timing and silent audio; continue remaining readable CPU/GPU/DSP/HLE recovery and same-console source-only rebuilding. Preserve qualified v34 and separate unpromoted v35 local component. Useful untouched-task training and copied-weight LM Studio Chat usability remain open.'
    for key in ['native_geometry_records_progress','native_scene_draw_progress','latest_native_candidate']:
        packet[key]['next_action']=action
    reader=packet['current_copied_Reader_progress']
    reader.update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,
                  current_source_factual_claims_reviewed=False,
                  prior_snapshot_reply_approval_retained=True,
                  new_matrix_route_facts_in_prior_prediction=False)
    packet['checked_current_summary']='Latest gameplay-tested image remains v34, shared module54134bytes. Standard route25012/24966frames:5774scene,4777record/display,8567copy and0record-matrix native returns;8717intermediate video differences,finalvideo agrees,scene stack168/208,sampled outer-active free heap14320each(not a global minimum). Additional ordinary-control fresh scene268 route22536/22363frames now witnesses190native/266original-record matrix returns,all monitors clear,finalvideo and playerXZ/scene/floor/heading agree. Its21803paired video differences and different final render-batch regions remain;outer-task stack/active heap unmeasured on that route. Actual static114angle byte0,not catalogue word4. This is one path,not whole-game fidelity. Local v35prologue remains an unpromoted54446byte component,not a disc:44.56second generation,host512+19guards,native512,scene772,copiedbyteidentity. Coordinator disc source and prior linked hybrid attribution remain. No new predictions or optimizer updates. Earlier base/adapter quality pilot0/4each. Reader39prior snapshot response138words/11.92seconds remains historically approved;new matrix facts have not been generated/reviewed. Preview unchanged;complete same-console source rebuild,audio/IRQ/physical fidelity,useful training gain and copied-weight native Chat usability remain open.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
    packet['current_status_renderer']='show_native_status_v8.py';packet['portable_entry_version']=17
    report.write_text('BIWN — fresh record-matrix path\n\n'
        'The existing v34 experimental image reached indoor scene268 using ordinary movement controls from a fresh HLE CD boot. Candidate22536frames:190native matrix entries/returns,12705native scene returns,12700record returns,22566copy returns. Same-layout control22363frames:266original-record matrix entries/returns. All qualified observers end clear and quiescent. No checkpoint restore,host guestRAM writes or CPU/task seeds. Read-only matrix watcher qualification:1152synthetic controls and128actual original/native CPU lanes.\n\n'
        'Both lanes consumed the same archived indoor waypoint JSON and finish with identical video,playerXZ,scene,floor and heading. Adaptive controller schedules differ on1247pairedframes;game-latched buttons differ on1230;video differs on21803. Final render-batch region is3candidate/4control although playerregion is4in both. This is not cycle/fullRAM/whole-game fidelity. Control restores only10original scene-entry bytes;global native copy/matrix/wait providers remain. Actual descriptor angle byte is0;raw catalogue last word4 is not treated as angle. One static114path does not cover every model/angle.\n\n'
        'Scene Cstack168/208bytes. The outer task was not exercised:outer-active heap and outer stack are unmeasured,notFFFFFFFFfree bytes. Final free-heap word is21056each,a final sample,not a minimum. The older standard route remains25012/24966frames,5774native scene returns,4777record/display,8567copy and zero record-matrix;its14320sampled outer-active heap belongs to that route alone.\n\n'
        'The first scene784 controller attempt used inconsistent movement thresholds and was intentionally stopped;the corrected route reaches784 and instantiates static116inregion13 but remains inregion0 with no matrix calls. Both attempts and the reviewer correction from assumed angle4 to measured0 are retained. No failing attempt was relabeled as passing.\n\n'
        'Existing v34 source and watcher/controller are coordinator work with prior linked hybrid attribution retained. No new local predictions or weight updates. Local v35block remains a separately verified component,not installed in the disc. The Desktop checkpoint preview is unchanged. Full source-only same-console rebuilding,broad video/audio/IRQ/console fidelity,useful training quality and copied-weight native Chat remain open.\n\nReview: '+r['directory']+'\n\n'+action+'\n')
    save(out/'facts.json',facts);save(out/'current-status-packet.json',packet)
    deps={str(rp):sha(rp),**r['source_sha256'],str(report):sha(report),str(Path(__file__)):sha(__file__)}
    for name in ['record-matrix-784-reviewed-v1-current.json','record-matrix-route-watch-qualified-v1-current.json']:
        p=V/name;g=read(p)
        for path,h in g.get('source_sha256',{}).items():assert sha(path)==h,path
        deps[str(p)]=sha(p);deps.update(g.get('source_sha256',{}))
    for name in ['show_native_status_v8.py','portable_biwn_entry_v17.py']:
        p=ROOT/'scripts'/name;deps[str(p)]=sha(p)
    deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
    for path,h in deps.items():
        assert Path(path).is_relative_to(ROOT) and sha(path)==h,path
        clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    clone(ROOT/'scripts/portable_biwn_entry_v17.py',P/'workbench/portable_biwn.py')
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for label,cmd in [('Root',[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_native_status_v8.py'),'--brief']),('copied',[str(P/'runtime/python/bin/python3.12'),str(P/'workbench/portable_biwn.py'),'status'])]:
        q=subprocess.run(cmd,cwd='/',capture_output=True,text=True,timeout=180);(out/(label+'-status.txt')).write_text(q.stdout+q.stderr)
        assert q.returncode==0,q.stderr
        assert all(x in q.stdout for x in ['25,012/24,966','190 native / 266 original','22,536/22,363','21,803','angle 0','unmeasured','44.56'])
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
        (root/'WATCH LOCAL AGENTS.txt').write_text(report.read_text())
    save(V/'record-matrix-fresh-delivery-v1-current.json',dict(status='terminal_fresh_matrix_path_published_Root_and_copied_status_verified',directory=str(out),new_predictions=0,new_training=False,installed_preview_changed=False))
    print('Published separate matrix route;Root and portable saved status verified.',flush=True)

if __name__=='__main__':main()
