"""Separate inherited prototype notes from current deployed-image evidence."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
    out=V/'record-loop-pending-scope-aligned-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    p=read(w['packet']);save(out/'before-packet.json',p);n=dict(p['pending_native_candidate'])
    oldkeys=['native_qualifications_inherited_by_full_module_byte_identity','native_case_count_inherited_by_byte_identity','scene_case_count_inherited_by_byte_identity','helper_wide_cases_inherited_by_identical_source_and_native_module','native_module_byte_identical_to_v1','v1_host_C99_compile_failed','v2_host_C99_compile_pass']
    n['prototype_only_qualification_notes']={key:n.pop(key)for key in oldkeys if key in n}
    n['scope']='Actual built v37experimental image:deployed-address/provider/alias/observer gates and standard fresh route pass. Additional matrix path is observed but exact finalvideo gate fails22858pixels;fractional player/camera state differs. This is an unpromoted candidate,not a fidelity pass. Historical prototype byte-identity notes are nested separately and do not replace actual deployed-image checks.'
    p['pending_native_candidate']=p['latest_source_development']=p['native_geometry_record_loop_progress']=n;p['native_scene_draw_progress']['pending_record_loop_candidate']=n
    save(out/'current-status-packet.json',p)
    deps={str(Path(__file__)):sha(__file__),**{str(x):sha(x)for x in out.iterdir()if x.is_file()}}
    for name in ['run_deck_status_live_v41.py','portable_biwn_entry_v21.py']:
        source=ROOT/'scripts'/name;deps[str(source)]=sha(source)
    for path in deps:clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    save(V/'record-loop-pending-scope-aligned-v1-current.json',dict(status='terminal_current_image_scope_separated_from_historical_prototype_notes',directory=str(out),new_predictions=0,new_training=False))
    print('Pending image scope aligned;failed visual gate and v34baseline preserved.',flush=True)

if __name__=='__main__':main()
