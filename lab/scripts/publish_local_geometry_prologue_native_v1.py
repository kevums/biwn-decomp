"""Publish a verified local-code prototype beside,not inside,the v34 gameplay image."""
import shutil
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
 delivered=read(V/'record-stride-fresh-delivery-worker-v1-current.json');assert delivered['status']=='terminal_v34_fresh_review_and_current_portable_delivery_verified'
 rp=V/'local-geometry-prologue-native-reviewed-v1-current.json';r=read(rp);assert r['native_body_cases']==512 and r['prototype_scene_cases']==772 and r['copied_prototype_module_byte_identical']
 for p,h in r['source_sha256'].items():assert sha(p)==h,p
 out=V/'local-geometry-prologue-native-current-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 packet=read(w['packet']);assert packet['latest_native_candidate']['new_fresh_gameplay_verified'];save(out/'before-packet.json',packet)
 local={k:v for k,v in r.items()if k!='source_sha256'};local['authorship']='Local copied-model identifier authored the22instruction prologue;coordinator supplied primitives and unchanged remainder. No edited model statements or weight training.';local['candidate_disc']=None
 packet['local_geometry_prologue_native_progress']=packet['local_geometry_prologue_repair_progress']=local
 packet['previous_latest_source_development_before_local_block']=packet['latest_source_development'];packet['latest_source_development']=local
 packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False)
 packet['checked_current_summary']+=' A newer v35mixed-source component contains the exact local22instruction prologue:44.56second generation,first text6.61seconds;host512+19guards,native512,scene772,copied54446bytebuild pass. It has no disc/freshqualification and is not adopted. Six full-function/block development predictions total,zero new weightupdates.'
 packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',packet)
 deps={str(Path(__file__)):sha(__file__),str(rp):sha(rp),str(Path(r['report'])):sha(r['report']),**r['source_sha256']};deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w)
 for p in deps:clone(Path(p),P/'workbench'/Path(p).relative_to(ROOT))
 clone(wp,P/'workbench/verification'/wp.name)
 save(V/'local-geometry-prologue-native-current-v1-current.json',dict(status='terminal_current_evidence_distinguishes_v34_gameplay_and_verified_local_v35_component',directory=str(out),new_predictions=0,new_training=False,model_source_installed=False))
 print('Current evidence:gameplayv34;new localv35component verified but unpromoted.',flush=True)
if __name__=='__main__':main()
