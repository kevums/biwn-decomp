"""Review one completed ordinary copied Reader; never regenerate its output."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def copy(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['/bin/cp','-c',str(src),str(dest)],check=True,capture_output=True)

def main():
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 queue=read(V/'portable-Reader36-queued-v1-current.json');j=queue['Reader_result'];raw=Path(j['directory'])
 assert queue['status']=='terminal_ordinary_portable_Reader_attempt_pending_review'and queue['exit_code']==0 and j['new_predictions']==1
 for p,h in j['source_sha256'].items():assert sha(p)==h,p
 result=read(raw/'response.json');text=(raw/'response.txt').read_text();e=read(raw/'evidence.json');full=read(raw/'full-MCP-evidence.json')
 assert text==result['text']and len(text.split())==156 and not j['word_limit_pass']
 assert e['display_source']['final_native_display_returns']==5243 and e['experimental_candidate']['differing_video_frames']==8375
 assert e['measured_heap_while_outer_active']['candidate']==816 and not e['whole_game_rebuild']
 assert len(j['MCP_connection']['tools'])==18 and j['model_identifier']=='portable-ailab-4f5658686590-daily'
 assert e['evidence_proof_sha256']==j['source_evidence_proof_sha256']==sha(wp)
 audit=read(P/f'path-audit-{j["pid"]}.json');assert not audit['denied']
 out=V/'display-list-copied-Reader36-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 subprocess.run(['/bin/cp','-cR',str(raw),str(out/'actual-Reader36')],check=True,capture_output=True)
 shutil.copy2(raw/'prompts-and-responses.txt',out/'prompts-and-responses.txt');save(out/'queue-terminal.json',queue);save(out/'path-audit.json',audit);save(out/'before-wrapper.json',w)
 preflights=[]
 for q in (P/'workbench/runs').glob('Deck-status-live-v36-*/protocol.json'):
  x=read(q)
  if x['status']=='terminal_current_Reader_evidence_preflight_zero_predictions':
   target=out/('preflight-'+q.parent.name);subprocess.run(['/bin/cp','-cR',str(q.parent),str(target)],check=True,capture_output=True);preflights.append(str(target))
 for src in [ROOT/'scripts/run_deck_status_live_v36.py',P/'workbench/portable_biwn.py',ROOT/'scripts/portable_biwn_entry_v8.py',V/'Reader36-launcher-preparation/portable_biwn-before-Reader36.py',Path(__file__)]:shutil.copy2(src,out/src.name)
 assert sha(P/'workbench/portable_biwn.py')==sha(ROOT/'scripts/portable_biwn_entry_v8.py')
 report=ROOT/'reports/BIWN Display List Copied Reader Review.txt'
 facts=dict(status='terminal_current_copied_Reader36_reviewed_word_limit_failed',directory=str(out),report=str(report),actual_predictions=1,seconds=j['seconds'],words=156,max_words=150,word_limit_pass=False,required_current_numeric_facts_correct=True,current_source_entry='0x185b2',current_source_reply_verified=False,current_source_factual_claims_reviewed=True,latest_source_changed_since_last_prediction=False,broader_quality_approved=False,quality_approved=False,run_speed_measured=False,new_training=False,optimizer_updates=0,trained_adapter_used=False,native_Chat_display_verified=False,raw_responses_retained=True,preflights=preflights,model_identifier=j['model_identifier'],ordinary_launcher_verified=True,path_audit_denied=[],scope='One completed ordinary moved-package Reader using copied base weights, SDK and actual 18-tool reference MCP. Two paragraphs accurately report v27,5243returns,8375intermediate video differences,final agreement,208/208stack and816sampledheap. Over150words;earlier64-update0/4pilot omitted,so not a complete training-history briefing. Capability versus quality and source authorship correctly separated. No held-out benchmark,training,model code,Native Chat or fidelity gain.')
 save(out/'facts.json',facts)
 report.write_text('BIWN copied Reader36 — actual local output review\n\nOne ordinary portable Reader prediction completed in11.58seconds using the package-owned base model and copied SDK/MCP. Its two paragraphs report the current v27 experimental source,5243native display/rotation/clear returns,8375intermediate video differences with final video agreement,208/208stack and816sampledouter-activeheap. They correctly leave whole-game rebuilding and fidelity open and separate training capability from quality and new updates.\n\nThe response is156words against a150word request. The supplied earlier64-update pilot with0/4base and0/4adapter code passes is omitted. Factual claims in this scoped response agree with saved MCP evidence;it is not approved as a fully compliant or complete training-history briefing. No weights changed and no benchmark gain is established. Native LMStudioChat rendering was not tested.\n\nThe default Reader now takes current MCP facts rather than hardcoded older input-prototype claims. The exact prompt,rawstream,response,preflight and clean origin-access audit are frozen. No prediction was replayed to produce this review.\n\n'+str(out/'prompts-and-responses.txt')+'\n')
 packet=read(w['packet']);save(out/'before-status-packet.json',packet);packet['previous_copied_Reader_progress']=packet['current_copied_Reader_progress'];packet['current_copied_Reader_progress']=facts;save(out/'current-status-packet.json',packet)
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps[str(report)]=sha(report)
 pub=V/'display-list-copied-Reader36-reviewed-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),new_predictions=1,new_training=False,dependencies_sha256=deps))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,w)
 for p,h in w['dependencies_sha256'].items():
  src=Path(p);assert src.is_relative_to(ROOT);dest=P/'workbench'/src.relative_to(ROOT)
  if not dest.is_file()or sha(dest)!=h:copy(src,dest)
 copy(wp,P/'workbench/verification'/wp.name)
 # Append independently: the moved package has its own additional historical Reader29.
 for root in [ROOT,P/'workbench']:
  index=root/'config/current-model-work-sources.json';items=read(index);items=[x for x in items if x[0]!=pub.name];items.append([pub.name,'BIWN copied Reader36 exact prompt/raw response; factual review, word limit failed']);atomic(index,items)
 print(facts['status'],str(report),flush=True)
if __name__=='__main__':main()
