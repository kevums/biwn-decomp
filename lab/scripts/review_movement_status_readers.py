"""Review actual current-menu and scoped-author Reader; retain semantic failures."""
import json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';runs=[read(v/f'current-biwn-status-v{n}-reader-current.json')for n in [12,16]];assert all(x['status']=='terminal_local_current_status_v'+str(n)+'_pending_semantic_review'for x,n in zip(runs,[12,16]));assert all(x['rounds']==2 and len(x['tool_calls'])==1 and not x['automatic_format_flags']and not x.get('Editor')and x['tool_calls'][0]['experimental_build']['resident_bytes']==26220 for x in runs)
 assert runs[0]['word_count']==143 and '14 actor successes'in runs[0]['answer']and'all current disc code is coordinator work'in runs[0]['answer'];assert runs[1]['word_count']==157 and'12 actor successes'in runs[1]['answer']and'new movement and creation routines'in runs[1]['answer']
 for x in runs:
  assert all(y in x['answer']for y in ['26,220','2,624','192','96','5,248','13,898','31,745','Video, audio, and state differ'])
 launcher=ROOT/'BIWN Current Status.command';assert'ask_biwn_current_status_v12.py'in launcher.read_text();out=v/'movement-status-readers-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);paths=[Path(__file__),launcher];summary=[]
 for n,x in zip([12,16],runs):
  p=out/f'v{n}-reader-as-reviewed.json';save(p,x);paths.append(p);folder=Path(x['directory']);paths.extend(folder/name for name in ['runner-as-run.py','protocol.json','answer.txt','prompts-and-responses.txt']);summary.append(dict(version=n,seconds=x['seconds'],words=x['word_count'],predictions=2,evidence_calls=1,installed_default=n==12))
 report=out/'review.txt';report.write_text(f'''Actual local status delivery for the26,220movement disc

Existing main-menuS(v12):143words,{runs[0]['seconds']:.2f}seconds,two localprediction rounds/one actualconfiguredMCPcall. New movement/component/startup/context/real-helper counts and14actor/0fail/0sprite-success/1skipped-failure limits are copied correctly. It says all current disc code is coordinator work: too broad. Only new movement/creation routines are coordinator implementations; previously accepted localhelpers and originalgamecode remain. Omits retainedprocessors, explicit routeframecompletion, nativeChat/Advertising/completefuture scope. No silent correction made.

One bounded scoped-author clarification(v16):157words,{runs[1]['seconds']:.2f}seconds,two rounds/one toolcall. It correctly limits coordinator authorship to new movement/creation, preserves nativeCPU/GPU/DSP/IRQandfullsameconsole/Advertising/Chat/migrationlimits, but changes14actorselector successes to12by confusing dispatcher actor routes with selector successes. All other listed new component/movement counts copy correctly. Format checks pass despite the factual error. Candidate rejected/notinstalled; no further prompt retries this turn. DefaultSstillv12.

New published evidence now has typed selector_outcomes and dispatcher_routing_counts, sourced from the actual checked observation:14selector successes versus12actor routes are separate. This data separation is preparation for stronger automatic fact checks; it does not establish better model output. Both raw answers/prompts/tool payloads/stats remain saved. Four predictions,no new code/weights/training or nativeChatdisplayclaim. Same local27Bbase; no independentReviewer.
''');paths.append(report);state=dict(status='terminal_movement_status_readers_semantic_limits_reviewed',directory=str(out),report=str(report),runs=summary,actual_predictions=4,actual_evidence_calls=2,default_Reader='v12',candidate_v16_installed=False,v12_numeric_counts_correct=True,v12_authorship_scope_overbroad=True,v16_actor_selector_count_wrong=True,typed_source_fields_added=True,output_improvement_proved=False,native_Chat_verified=False,new_training=False,source_sha256={str(p):sha(p)for p in paths});save(out/'protocol.json',state);save(v/'movement-status-readers-reviewed-current.json',state);print(json.dumps({k:state[k]for k in ['status','actual_predictions','candidate_v16_installed','typed_source_fields_added']}))
if __name__=='__main__':main()
