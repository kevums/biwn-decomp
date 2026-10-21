"""Publish the verified ordinary Reader39 and nullable-comparison fix."""
import shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
 rp=V/'copied-Reader39-reviewed-v1-current.json';r=read(rp);assert r['complete_requested_briefing_approved']and r['actual_predictions']==1 and r['words']==138
 for p,h in r['source_sha256'].items():assert sha(p)==h,p
 out=V/'Reader39-current-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 packet=read(w['packet']);save(out/'before-packet.json',packet)
 packet['previous_copied_Reader_before_pending_comparison_fix']=packet['current_copied_Reader_progress'];packet['previous_default_Reader_before39']=packet['current_default_Reader_progress']
 packet['current_copied_Reader_progress']=dict(status=r['status'],directory=r['directory'],report=r['report'],review=str(rp),actual_predictions=1,seconds=11.92,words=138,max_words=150,word_limit_pass=True,required_current_numeric_facts_correct=True,supplied_snapshot_factual_claims_approved=True,artifact_type_error=False,artifact_type_pass=True,code_authorship_statement_present=True,complete_requested_briefing_approved=True,current_source_reply_verified=True,current_source_factual_claims_reviewed=True,provided_candidate_profile='v34',provided_source_prototype_profile='v35',latest_source_changed_since_last_prediction=False,broader_quality_approved=False,quality_approved=False,new_training=False,optimizer_updates=0,trained_adapter_used=False,native_Chat_display_verified=False,model_identifier=r['model_identifier'],ordinary_launcher_verified=True,default_reader_version=39,default_reader_prepared=True,default_reader_generation_verified=True,scope='One actual ordinary copied-model briefing on unchanged current v34gameplay/v35prototype facts.138words/twoparagraphs,facts/artifact/authorship and requestedformat pass. Notheldout/general quality or traininggain. Generation11.92seconds excludes earlier setup/evidence/queue;totalclicklatencyuninstrumented. Currentpublicationchanges only Readerdelivery metadata.')
 packet['current_default_Reader_progress']=dict(status=r['status'],version=39,prepared=True,current_evidence_preflight_verified=True,Root_and_copied_evidence_preflight_verified=True,actual_prediction_verified=True,new_predictions=1,new_training=False,native_Chat_verified=False,entry=str(P/'workbench/portable_biwn.py'),script=str(P/'workbench/scripts/run_deck_status_live_v39.py'),scope=packet['current_copied_Reader_progress']['scope'])
 packet['checked_current_summary']+=' Ordinary copied Reader39 now returns a138word/twoparagraph current-snapshot briefing in11.92seconds;facts,artifacttype and requestedauthorship pass. This is a single supplied-facts result,not broadquality or weighttraining. Reader39handles nullable pendingcomparisons and preserves other loadedmodels.'
 packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',packet)
 deps={str(Path(__file__)):sha(__file__),str(rp):sha(rp),str(Path(r['report'])):sha(r['report']),**r['source_sha256']}
 for name in ['run_deck_status_live_v39.py','portable_biwn_entry_v16.py']:
  p=ROOT/'scripts'/name;deps[str(p)]=sha(p);clone(p,P/'workbench/scripts'/name)
 assert sha(P/'workbench/portable_biwn.py')==sha(ROOT/'scripts/portable_biwn_entry_v16.py')
 deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()});w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w)
 for p in deps:clone(Path(p),P/'workbench'/Path(p).relative_to(ROOT))
 clone(wp,P/'workbench/verification'/wp.name)
 for label,command in [('Root',[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_native_status_v7.py'),'--brief']),('copied',[str(P/'runtime/python/bin/python3.12'),str(P/'workbench/portable_biwn.py'),'status'])]:
  q=subprocess.run(command,cwd='/',capture_output=True,text=True,timeout=180);(out/(label+'-status.txt')).write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  assert all(x in q.stdout for x in ['25,012/24,966','8,717','14,320/14,320','11.92','138','version: 39','44.56','not adopted'])
 save(V/'Reader39-current-delivery-v1-current.json',dict(status='terminal_Reader39_and_Root_copied_status_launchers_current_facts_verified',directory=str(out),new_predictions_in_delivery=0,new_training=False,native_Chat_verified=False))
 print('Root/copied status and ordinary Reader39 verified;no source or preview promotion.',flush=True)
if __name__=='__main__':main()
