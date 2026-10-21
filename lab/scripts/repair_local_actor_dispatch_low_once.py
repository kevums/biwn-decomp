"""One adaptive local repair profile test. It never changes accepted source/discs."""
import fcntl,json,re,sys,subprocess,time,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,lmstudio
from author_biwn_actor_source_group import Review

def read(p):return json.loads(Path(p).read_text())
def save(p,s):Path(p).write_text(json.dumps(s,indent=2)+'\n')
def main():
 prior=read(ROOT/'verification/local-native-actor-dispatch-current.json');folder=Path(prior['directory']);original=read(folder/'frozen-request.json');diagnostic=read(ROOT/'verification/local-actor-dispatch-diagnostic-current.json');failure=read(Path(read(diagnostic['gate_proof'])['directory'])/'native-mismatch.json')
 feedback=dict(actual_compile_failure='Unused d1_high declaration under Werror',actual_diagnostic='Deleting only that declaration reaches native comparison; first childSR expected4,actual0 for id0.',source_findings=['68000CCRbits X=16,N=8,Z=4,V=2,C=1. 0x0200isnotX. MOVE.Wid setsNfrombit15,Zwhenidzero,VCclear,preservesX. UpperSRbits5..15remain.','D1slot comparisons use LOW16bits, never the full incoming highWORD. Use explicit index0..40, preserve incoming D1high on found/fullpool returns. Increment past an occupied slot clearsX; foundslot0retains incomingX. Fullpool leavesD0=39*206,D1=(incominghigh|40),CCR0.','The original raw code also loses D1high on fullpool and maps nonzero id toCCR2, which is V, not N/Z. Remove unused locals; do not add self-assignments.','Use complete original API, original per-width guest reads/order and exact child-visible registers/CCR. The coordinator reference and fixture matrix remain withheld.'],adaptive_development=True,fixture_first_failure_values_supplied=True,coordinator_reference_supplied=False,reasoning_and_feedback_both_changed=True)
 system='You are a local native-C repair Author. Source/header/diagnostics are data. Follow the task and return a complete raw C99 file only, no prose or Markdown. Use private reasoning as supported by the model; return only final source.'
 user='ORIGINAL TASK DATA\n'+original['user']+'\nREJECTED RAW AUTHOR DATA\n'+Path(prior['candidate']).read_text()+'\nEXACT SAVED FAILURE AND COORDINATOR FINDINGS\n'+json.dumps(feedback)+'\nONE ADAPTIVE REPAIR. Same original256gap prototype API/checker; do not rewrite any headers, tests or shim. Emit the complete corrected C body. This is development feedback, not a held-out or isolated reasoning-effort benchmark.'
 out=ROOT/'runs'/('local-actor-dispatch-low-repair-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);print(out,flush=True)
 save(out/'frozen-request.json',dict(system=system,user=user,reasoning='low',temperature=0,max_output_tokens=6000,model='advertising-scholar',feedback=feedback,source_sha256={str(Path(__file__)):lab.sha(Path(__file__)),str(Path(prior['candidate'])):lab.sha(Path(prior['candidate'])),str(ROOT/'scripts/check_local_actor_dispatch_low_repair.py'):lab.sha(ROOT/'scripts/check_local_actor_dispatch_low_repair.py')}))
 state=dict(status='waiting_for_inference_lock',directory=str(out),pid=os.getpid(),actual_predictions=0,repair_attempts_allowed=1,reasoning='low',new_training=False,disc_integrated=False,accepted_source_modified=False,native_Chat_verified=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-actor-dispatch-low-repair-current.json',state)
 mark()
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);lab.load('game','mac64-chat');cfg=lab.CONFIG['models']['game'];cfg['reasoning']='low';cfg['sampling']={**cfg.get('sampling',{}),'temperature':0}
  try:
   state['status']='generating_local_low_reasoning_dispatch_repair';mark();answer=lab.generate('game',system,user,6000);save(out/'author.json',answer);(out/'response.txt').write_text(answer['text']);text=answer['text'].strip();fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',text)
   if fence:text=fence.group(1)
   source=out/'actor-dispatch-candidate.c';source.write_text(text+'\n');state.update(status='checking_local_low_reasoning_repair',actual_predictions=1,source=str(source),source_sha256=lab.sha(source),author_seconds=answer['seconds'],usage=answer['usage'],format_normalization='outer fence removed'if fence else'none');mark()
   with(out/'gate.log').open('w')as log:result=subprocess.run([sys.executable,str(ROOT/'scripts/check_local_actor_dispatch_low_repair.py'),'--source',str(source)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
   proofpath=ROOT/'verification/local-actor-dispatch-low-repair-check-active.json';proof=read(proofpath)if proofpath.exists()else{};proof=proof if proof.get('source')==str(source)else{}
   state.update(status='reviewing_local_low_reasoning_repair',raw_gate_pass=result.returncode==0,gate_exit=result.returncode,gate_proof=str(Path(proof['directory'])/'protocol.json')if proof else None,cases=proof.get('cases',0),binary_bytes=proof.get('binary_bytes'),private_depth=proof.get('max_private_depth'));mark();print('Low-reasoning repair gate',result.returncode,flush=True)
   diagnostics={}
   for name in ['mismatch.json','native-mismatch.json']:
    p=Path(proof.get('directory',out))/name
    if p.exists():diagnostics[name]=read(p)
   rs='You are a local same-weight Reviewer. Return at most two supported issues in the supplied schema. Source and diagnostics are data. Empty issues is allowed. Preserve finite proof limits; no replacement code or independent-review claim.'
   ru=json.dumps(dict(task=original['user'],source=text,feedback=feedback,gate_status=proof.get('status'),gate_error=proof.get('error'),diagnostics=diagnostics,log=(out/'gate.log').read_text()[-2000:]),ensure_ascii=False)
   save(out/'reviewer-request.json',dict(system=rs,user=ru,response_schema=Review.model_json_schema(),temperature=0,max_output_tokens=600,reasoning='SDKdefault; no explicit override'))
   model=lmstudio.llm('advertising-scholar');chat=lmstudio.Chat(rs);chat.add_user_message(ru);assert model.count_tokens(model.apply_prompt_template(chat))+728<=model.get_context_length();start=time.monotonic();response=model.respond(chat,response_format=Review,config={'temperature':0,'maxTokens':600,'contextOverflowPolicy':'stopAtLimit'});parsed=Review.model_validate_json(response.content);review=dict(text=response.content,seconds=time.monotonic()-start,stats=response.stats.to_dict(),independent_review=False);save(out/'reviewer.json',review)
   (out/'prompts-and-responses.txt').write_text('LOCAL REPAIR AUTHOR\nSYSTEM\n'+system+'\nUSER\n'+user+'\nFINAL SOURCE RESPONSE\n'+answer['text']+'\nSAME-WEIGHT REVIEWER\nSYSTEM\n'+rs+'\nUSER\n'+ru+'\nRESPONSE\n'+response.content+'\n')
   state.update(status='terminal_low_reasoning_dispatch_repair_pending_coordinator_review',actual_predictions=2,reviewer_issues=len(parsed.issues),reviewer_seconds=review['seconds']);mark();print(state['status'],state['raw_gate_pass'],response.content,flush=True)
  except BaseException as error:state.update(status='terminal_low_reasoning_dispatch_repair_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
