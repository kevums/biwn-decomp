"""One guided local revision after native CPU counterexamples; no hidden edits."""
import fcntl,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat,lmstudio
from author_GPU_wait_runtime_C import SYSTEM,Source
from run_biwn_native_fast_gameplay_route import sha,save
def main():
 ap=ROOT/'verification/GPU-wait-Code-Author-current.json';author=json.loads(ap.read_text());cp=ROOT/'verification/GPU-wait-local-C-check-current.json';check=json.loads(cp.read_text());assert check['failed_cases']==832 and check['author_proof_sha256']==sha(ap)
 first=Path(author['directory']);request=json.loads((first/'request.json').read_text());failures=json.loads((Path(check['directory'])/'first-mismatches.json').read_text())
 feedback=('The native oracle rejects832of1024cases. Correct the SR bit layout: '
 'C=0x0001,V=0x0002,Z=0x0004,N=0x0008,X=0x0010,S=0x2000. '
 'For CMP preserve existing SR&0xfff0, then OR only new NZVC low4bits. '
 'Subtraction overflow is bit31 of((destination^source)&(destination^result)); '
 'parenthesize the entire bit expression before extracting its sign. '
 'CMP must preserve all upper SR bits and X. A7 is ALWAYS registers[15], '
 'including usermode; registers[14] is A6. RTS increments A7 by4 and updates '
 'the active bank (SSPwhen SR&S,otherwiseUSP), preserving the inactive bank. '
 'Keep the same6instruction PCs and all7hosterror contracts. '
 'Return the complete corrected C unit, not a patch. Do not claim tests passed.')
 user=json.dumps(dict(original_request=json.loads(request['user']),rejected_C=Path(author['source']).read_text(),native_counterexamples=failures[:3],coordinator_feedback=feedback,final_task='Implement exactlyoneinstruction percall using the specified bitpositions and A7bank rules. Return complete C99 source.'),ensure_ascii=False)
 out=ROOT/'runs'/('GPU-wait-Code-Author-revision-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);save(out/'request.json',dict(system=SYSTEM,user=user,tools=[]));(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Code Author guided revision',same_weights=True,independent_review=False,native_Chat_verified=False,new_training=False,parent_author=str(ap),parent_author_sha256=sha(ap),native_failure_check=str(cp),native_failure_check_sha256=sha(cp),source_sha256={str(p):sha(p)for p in [Path(__file__),ap,cp,first/'request.json',Path(author['source']),out/'request.json']})
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/GPU-wait-Code-Author-revision-current.json',state)
 mark();print(out,flush=True)
 try:
  with(ROOT/'runs/.inference.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);identifier=assistant_chat.ensure_model('game');model=lmstudio.llm(identifier);chat=lmstudio.Chat(SYSTEM);chat.add_user_message(user);tokens=model.count_tokens(model.apply_prompt_template(chat));assert tokens+2600+128<=model.get_context_length();state.update(status='local_Code_Author_revision_generating',model_identifier=identifier,input_tokens=tokens);mark();start=time.monotonic();response=model.respond(chat,response_format=Source,config={'temperature':0,'maxTokens':2600,'contextOverflowPolicy':'stopAtLimit'});elapsed=time.monotonic()-start
  save(out/'response.json',dict(text=response.content,stats=response.stats.to_dict(),seconds=elapsed));parsed=Source.model_validate_json(response.content).model_dump();code=out/'biwn_GPU_wait_repair.c';code.write_text(parsed['source']);state.update(status='terminal_local_C_revision_pending_review',source=str(code),source_text_sha256=sha(code),assumptions=parsed['assumptions'],seconds=elapsed,compiled=False,accepted=False);mark();print(parsed['source'],flush=True);print('seconds',elapsed,flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
 finally:(out/'prompts-and-responses.txt').write_text('GUIDED LOCAL CODE AUTHOR REVISION; NOT INDEPENDENT\nSYSTEM\n'+SYSTEM+'\nUSER\n'+user+'\nOUTPUT\n'+(Path(state['source']).read_text()if state.get('source')else''))
if __name__=='__main__':main()
