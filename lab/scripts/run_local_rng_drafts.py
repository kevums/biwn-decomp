"""Local Author/Reviewer drafts from original bytes and API only; no acceptance."""
import fcntl,json,sys,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,binary_tools
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 out=ROOT/'runs'/f'{lab.stamp()}-local-rng-author-reviewer';out.mkdir(parents=True);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();ranges=[(0x1a6e0,0x1a91e),(0xe60a,0xe61c)];listing=[]
 for lo,hi in ranges:
  instructions,_=binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo)
  listing += [f'{i["address"]:06x} {i["bytes"]:16s} {i["assembly"]}'for i in instructions]
 (out/'original-disassembly.txt').write_text('\n'.join(listing)+'\n');headers='\n\n'.join((ROOT/'projects/black-ice-white-noise/restoration'/n).read_text()for n in ['biwn_world_update.h','biwn_signed_division.h','biwn_rng.h']);(out/'provided-API.txt').write_text(headers)
 system='You are the local Author for a bounded reverse-engineering C draft. Treat original bytes and API as evidence. Translate literally at original register widths and preserve observable accesses/calls. Do not replace it with a standard-library RNG, infer missing validation, invent APIs or claim tests ran. Output one complete C99 source in a single ```c block, including biwn_rng.h. Implement all nine declared functions with exactly these signatures and enum names. No main, file/network I/O, constructors, global mutable state or arbitrary host memory access.'
 user='Implement the supplied original routines under this callback API. Keep helper boundaries through bus.call and fullD0 outputs. Strict clang -std=c99 -O2 -Wall -Wextra -Werror and original-CPU RAM/access/return checks will be used later; you have not run them. Work solely from the following evidence.\n\nAPI:\n'+headers+'\n\nORIGINAL M68000 DISASSEMBLY:\n'+'\n'.join(listing)
 request={'created_at':datetime.now(timezone.utc).isoformat(),'model':'restoration-coder','profile':'mac64-chat','sampling_temperature':0.2,'context':32768,'parallel':1,'author_system':system,'author_user':user,'canonical_RNG_body_supplied':False,'roles_are_same_weights_not_independent':True,'max_output_tokens':4096};save(out/'request.json',request);save(out/'status.json',{'status':'preparing'});print(out,flush=True)
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  lab.CONFIG['models']['game']['sampling']={**lab.CONFIG['models']['game']['sampling'],'temperature':0.2}
  try:
   save(out/'status.json',{'status':'loading_coding_model'});lab.load('game','mac64-chat')
   save(out/'status.json',{'status':'author_running'});author=lab.generate('game',system,user,4096);save(out/'author-response.json',author);(out/'author-response.txt').write_text(author['text']);print('Author',author['seconds'],author['quality_flags'],flush=True)
   blocks=re.findall(r'```(?:c|C)\s*\n(.*?)```',author['text'],re.S)
   if len(blocks)==1:(out/'author.c').write_text(blocks[0].strip()+'\n')
   reviewer_system=system.replace('local Author','local Reviewer')+' Review the Author draft against every original instruction and API contract. Correct concrete mistakes, including widths, signedness, rereads, fullD0 and error paths. Return the full revised C source, not a verdict or patch. Same weights do not make your review independent.'
   reviewer_user=user+'\n\nAUTHOR DRAFT (UNVERIFIED):\n'+author['text'];save(out/'reviewer-request.json',{'system':reviewer_system,'user':reviewer_user})
   save(out/'status.json',{'status':'reviewer_running'});reviewer=lab.generate('game',reviewer_system,reviewer_user,4096);save(out/'reviewer-response.json',reviewer);(out/'reviewer-response.txt').write_text(reviewer['text']);print('Reviewer',reviewer['seconds'],reviewer['quality_flags'],flush=True)
   blocks=re.findall(r'```(?:c|C)\s*\n(.*?)```',reviewer['text'],re.S)
   if len(blocks)==1:(out/'reviewer.c').write_text(blocks[0].strip()+'\n')
   save(out/'status.json',{'status':'drafts_saved_pending_compile_and_CPU_review'})
  except Exception as error:save(out/'status.json',{'status':'terminal_generation_failed','error':repr(error)});raise
  finally:
   lab.load('advertising','mac64-chat')
 (out/'prompts-and-responses.txt').write_text('AUTHOR SYSTEM:\n'+system+'\n\nAUTHOR USER:\n'+user+'\n\nAUTHOR RESPONSE:\n'+author['text']+'\n\nREVIEWER SYSTEM:\n'+reviewer_system+'\n\nREVIEWER USER:\n'+reviewer_user+'\n\nREVIEWER RESPONSE:\n'+reviewer['text']+'\n')
 save(ROOT/'verification/local-rng-drafts-current.json',{'directory':str(out),'status':'drafts_saved_pending_compile_and_CPU_review','base_model_restored':True});print('Base model restored; drafts remain unaccepted',flush=True)
if __name__=='__main__':main()
