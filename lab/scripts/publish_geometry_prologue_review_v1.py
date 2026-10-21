"""Reconcile completed block-agent results without changing game/source candidates."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
 rp=V/'local-geometry-prologue-reviewed-v2-current.json';r=read(rp);assert r['actual_predictions']==2 and r['compiled_attempts']==2 and r['compiled_successes']==0
 for p,h in r['source_sha256'].items():assert sha(p)==h,p
 out=V/'geometry-prologue-current-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 packet=read(w['packet']);save(out/'before-packet.json',packet)
 facts={k:v for k,v in r.items()if k!='source_sha256'};packet['local_geometry_prologue_progress']=facts
 packet['latest_source_development']['latest_local_block_trial']=facts
 packet['latest_source_development']['geometry_full_and_block_local_predictions_total']=5
 packet['checked_current_summary']+=' Bounded22instruction local Author/Repair completed50.23/34.62seconds,915/650tokens;both complete,but both strict C builds fail unusedlocalu. Zero semantic machinecases,no sourceadoption or optimizerupdates. No local block worker remains live.'
 packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
 save(out/'current-status-packet.json',packet)
 deps={str(Path(__file__)):sha(__file__),str(rp):sha(rp),**r['source_sha256'],str(Path(r['report'])):sha(r['report'])}
 deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w)
 for p in deps:clone(Path(p),P/'workbench'/Path(p).relative_to(ROOT))
 clone(wp,P/'workbench/verification'/wp.name)
 save(V/'geometry-prologue-current-delivery-v1-current.json',dict(status='terminal_complete_block_agent_results_reconciled_into_current_evidence',directory=str(out),new_predictions=0,new_training=False,game_disc_changed=False))
 print('Completed block results reconciled;no worker still queued.',flush=True)
if __name__=='__main__':main()
