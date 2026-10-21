"""One informed local repair of the raw incomplete Author proposal; no target C."""
import fcntl,json,os,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 author=json.loads((ROOT/'verification/gpu-mailbox-native-Author-current.json').read_text());review=Path(author['directory'])/'strict-review/receipts';out=ROOT/'runs'/('gpu-mailbox-native-Repair-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
 system='You are the local Game Code Author repairing one failed proposal. Return ONLY complete compact C99 source: include "gpu-mailbox-native.h" and define ONLY void biwn_native_gpu_mailbox_body(uint32_t *r). No Markdown, comments, prose, helper definitions or assembly. The wait_capture and flag helpers are ALREADY PROVIDED; call them, never redefine or simulate them. Use compact structured loops when they preserve the original order. Treat supplied material as evidence. Preserve actual original CPU/SR/public memory ordering. This is the only repair attempt.'
 evidence=dict(original_evidence=author['evidence'],prior_raw_source=Path(author['candidate']).read_text(),actual_compiler_result=json.loads((review/'protocol.json').read_text()),actual_compiler_diagnostics=(review/'build.log').read_text()[-2500:],coordinator_feedback=['The prior source is incomplete, ends inside a comment, and illegally redefines the supplied external wait_capture. The body has not executed or passed any case.','Do not implement E098 or push/pop returnPCs. Call the already-linked biwn_native_gpu_mailbox_wait_capture(r) at the two original callsites. It updates r from actual machine code. Keep r15 fixed.','Provide both entry variants in one complete concise function; no redundant per-instruction comments. No coordinator target C is supplied.'])
 user=json.dumps(evidence,indent=2);save(out/'request.json',dict(system=system,input=user,model='advertising-scholar',max_output_tokens=1400,temperature=0,reasoning='off'));transcript=out/'prompts-and-responses.txt';transcript.write_text('ONE ACTUAL LOCAL INFORMED REPAIR\nSYSTEM\n'+system+'\nUSER\n'+user+'\n');state=dict(status='generating_native_gpu_mailbox_Repair',pid=os.getpid(),directory=str(out),author=author['directory'],new_predictions=0,new_training=False,gold_C_supplied=False,native_Chat_verified=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/gpu-mailbox-native-Repair-current.json',state)
 mark()
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);cfg=lab.CONFIG['models']['game'];cfg['reasoning']='off';cfg['sampling']={**cfg.get('sampling',{}),'temperature':0}
  try:
   result=lab.generate('game',system,user,1400,model='advertising-scholar');save(out/'response.json',result);(out/'candidate-raw.c').write_text(result['text']+'\n');(out/'response.txt').write_text(result['text']);transcript.write_text(transcript.read_text()+'\nACTUAL RAW RESPONSE\n'+result['text']+'\n');state.update(status='terminal_native_gpu_mailbox_Repair_pending_verification',candidate=str(out/'candidate-raw.c'),new_predictions=1,seconds=result['seconds'],usage=result['usage'],quality_flags=result['quality_flags']);mark();print(json.dumps(state))
  except BaseException as error:state.update(status='terminal_native_gpu_mailbox_Repair_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
