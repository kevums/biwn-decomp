"""Deliver current v33 saved status and compact-Author evidence to both workbenches."""
import shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
 out=V/'geometry-records-frontend-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
 packet=read(w['packet']);save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet)
 rp=V/'local-geometry-records-reviewed-v2-current.json';r=read(rp);assert r['actual_predictions']==1 and r['truncation_correctly_classified'] and not r['repair_run']
 deps={str(Path(__file__)):sha(__file__),str(rp):sha(rp),**r['source_sha256']}
 for path,h in deps.items():assert sha(path)==h,path
 compact={k:v for k,v in r.items()if k!='source_sha256'};packet['local_geometry_records_compact_progress']=compact
 for key in ['native_geometry_records_progress','latest_source_development']:
  packet[key]['local_generation_snapshot']={k:r[k]for k in ['status','actual_predictions','seconds','output_tokens','accepted_complete_functions','compiled_candidates','new_training','optimizer_updates','model_source_installed']}
  packet[key]['actual_local_predictions_v1_v2_total']=3
 packet['checked_current_summary']+=' Compact local Author v2 also truncated after320.05seconds;correctly classified,Repair skipped,neither compiled nor installed. Three actual v1/v2predictions total,zero new optimizer updates.'
 packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
 save(out/'current-status-packet.json',packet);deps[str(out/'current-status-packet.json')]=sha(out/'current-status-packet.json')
 for name in ['show_native_status_v5.py','portable_biwn_entry_v13.py']:
  p=ROOT/'scripts'/name;deps[str(p)]=sha(p);clone(p,P/'workbench/scripts'/name)
 target=P/'workbench/portable_biwn.py';backup=out/'previous-portable-entry.py';shutil.copy2(target,backup);shutil.copy2(ROOT/'scripts/portable_biwn_entry_v13.py',target)
 deps[str(backup)]=sha(backup);deps[str(out/'before-wrapper.json')]=sha(out/'before-wrapper.json');deps[str(out/'before-packet.json')]=sha(out/'before-packet.json')
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w)
 for path in deps:clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
 clone(wp,P/'workbench/verification'/wp.name)
 checks=[]
 for key,command in [('Root',[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_native_status_v5.py'),'--brief']),('copied',[str(P/'runtime/python/bin/python3.12'),str(target),'status'])]:
  result=subprocess.run(command,cwd='/',capture_output=True,text=True,timeout=180);(out/(key+'-status.txt')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
  assert all(x in result.stdout for x in ['25,020/24,965','5,668','8,764','14,256/14,256','4,666','8,381','matrix 0','448','320.05']),result.stdout
  checks.append(dict(root=key,exit_code=0,stdout=str(out/(key+'-status.txt'))))
 save(V/'geometry-records-frontend-delivery-v1-current.json',dict(status='terminal_Root_and_copied_v33_saved_status_launchers_verified',directory=str(out),checks=checks,new_predictions=0,new_training=False,native_Chat_verified=False,installed_preview_changed=False))
 print('Both saved status launchers verified on v33facts;compact Author review included.',flush=True)
if __name__=='__main__':main()
