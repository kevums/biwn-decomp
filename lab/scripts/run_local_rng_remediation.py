"""One bounded local correction, still requiring compilation/CPU acceptance."""
import fcntl,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 prior=Path(json.loads((ROOT/'verification/local-rng-drafts-current.json').read_text())['directory']);out=prior/'one-guided-correction';out.mkdir(exist_ok=True);headers='\n\n'.join((ROOT/'projects/black-ice-white-noise/restoration'/n).read_text()for n in ['biwn_world_update.h','biwn_signed_division.h','biwn_rng.h'])
 system='You are the local Remediator. Return one complete C99 source in one closed ```c block. First line must be #include "biwn_rng.h". Do not copy header contents, add main/I/O/constructors/global mutable state, fake stack arrays or unused register-save variables. Implement all nine exact API functions mapped to the stated source entries. Preserve widths, signedness, external accesses and logical helper-call order. Use uint32_t for wrapped arithmetic; signed-word ASR must be exact. You have not run tests. Do not claim correctness.'
 feedback='The prior Author and Reviewer output is identical, truncated and rejected. Correct from the original source, not by completing that wrong template. Function-address mapping is now explicit in the header. Read long values at constant addresses before passing helper args; source pushes denominator then numerator, so logical args are [numerator,denominator_value]. Do not pass the constant address as denominator. Follow the unsigned word comparison in select at1A87A; that routine is not the generator. A BGT after a long store tests signed positivity; its fallthrough normalization is a memory read-modify-write, not replacing a value with a constant. Preserve rereads and fullD0, including incomingD0 on paths that do not change it. Do not replace this with a standard RNG or bake mutable constants. Strict -Wall -Wextra -Werror rejects unused fake registers/args. Existing signed division returns raw quotient and remainder; E60A delegates to it. Bus.call failures map to DEPENDENCY_ERROR, while local callback failures map to BUS_ERROR. No canonical RNG body is supplied.'
 user=feedback+'\n\nAPI WITH EXACT ENTRY MAPPING:\n'+headers+'\n\nORIGINAL DISASSEMBLY:\n'+(prior/'original-disassembly.txt').read_text()+'\n\nPRIOR COMPILER FEEDBACK:\n'+(prior/'initial-compile.log').read_text()[-6500:]
 save(out/'request.json',{'created_at':datetime.now(timezone.utc).isoformat(),'system':system,'user':user,'model':'restoration-coder','temperature':0.2,'max_output_tokens':8192,'canonical_body_supplied':False,'prior_failed_directory':str(prior)});print(out,flush=True)
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);lab.CONFIG['models']['game']['sampling']={**lab.CONFIG['models']['game']['sampling'],'temperature':0.2}
  try:
   save(out/'status.json',{'status':'loading_coding_model'});lab.load('game','mac64-chat');save(out/'status.json',{'status':'remediator_running'});result=lab.generate('game',system,user,8192);save(out/'response.json',result);(out/'response.txt').write_text(result['text']);blocks=re.findall(r'```(?:c|C)\s*\n(.*?)```',result['text'],re.S)
   if len(blocks)==1:(out/'candidate.c').write_text(blocks[0].strip()+'\n')
   save(out/'status.json',{'status':'response_saved_pending_review','seconds':result['seconds'],'quality_flags':result['quality_flags']});print(result['seconds'],result['quality_flags'],flush=True)
  except Exception as error:save(out/'status.json',{'status':'terminal_generation_failed','error':repr(error)});raise
  finally:lab.load('advertising','mac64-chat')
 (out/'prompts-and-response.txt').write_text('SYSTEM:\n'+system+'\n\nUSER:\n'+user+'\n\nRESPONSE:\n'+result['text']+'\n');save(ROOT/'verification/local-rng-remediation-current.json',{'directory':str(out),'status':'response_saved_pending_review','base_restored':True})
if __name__=='__main__':main()
