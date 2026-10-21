"""Keep current v34 summary aliases consistent; preserve route-specific counts."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
    out=V/'record-matrix-current-finalization-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    p=read(w['packet']);save(out/'before-packet.json',p)
    n=p['native_geometry_records_progress'];c=p['latest_native_candidate']
    assert n['native_record_matrix_returns']==c['native_record_matrix_returns']==0
    assert n['record_matrix_fresh_coverage']['native_record_matrix_returns']==190
    c['standard_route_native_record_matrix_fresh_path_verified']=False
    c['native_record_matrix_fresh_path_verified']=True
    c['native_record_matrix_fresh_path_scope']=n['native_record_matrix_fresh_path_scope']
    c['record_matrix_fresh_coverage']=n['record_matrix_fresh_coverage']
    n['next_action']=c['next_action']=p['native_scene_draw_progress']['next_action']
    p['native_geometry_record_stride_progress']=dict(n)
    p['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',p)
    deps={str(Path(__file__)):sha(__file__),**{str(x):sha(x)for x in out.iterdir()if x.is_file()}}
    for path in deps:clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    save(V/'record-matrix-current-finalization-v1-current.json',dict(status='terminal_current_v34_aliases_preserve_separate_matrix_and_standard_counts',directory=str(out),new_predictions=0,new_training=False))
    print('Current v34 aliases agree;standard route matrix0,separate route190.',flush=True)

if __name__=='__main__':main()
