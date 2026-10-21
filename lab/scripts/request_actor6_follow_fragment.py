"""Local code author/reviewer on a bounded source decision; outputs unedited."""
import fcntl,json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');out=ROOT/'verification/actor6-local-follow-fragment'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
live=json.loads((ROOT/'verification/natural-actor6-task-current.json').read_text());ram=(Path(live['directory'])/'native-RAM.bin').read_bytes()
import generate_biwn_entry_setup_cpu as gen
rows=gen.loader.base.binary_tools.m68k_instructions(ram[0x1585c:0x15896],0x1585c)[0]
evidence='\n'.join(f'{r["address"]:06X}: {r["assembly"]}'for r in rows)
user='Translate only the output effect on actor+78 and actor+7C from this original M68000 listing. Initial long at4C24C is ticks, initial actor+7C long is fraction. Stop before15896. E588 is the original signed32 division helper, numerator from first pushedlong, denominator300 from earlier PEA; quotient truncates towardzero. ADD.L and data registers wrap32bits. ASL.W modifiesonly low16 and leaves high16unchanged; SWAP exchangeslow/high16; CLR.W clearslow16 only; MOVEA.W signextends16bits; MOVE.L stores32bits. Return only bare complete C99 source including stdint.h. No Markdown, fences, commentary. Your first characters must be #include. Export uint64_t biwn_actor6_follow_step(uint32_t ticks,uint32_t fraction). Pack final actor+78 long in low32 and final actor+7C long in high32. Ignore registers/stack/CCR except necessary output computations; no other functions, pointers, I/O or allocation. Derivefromlisting, do not claim verification.\n\n'+evidence
record=dict(status='running',directory=str(out),model=lab.CONFIG['models']['game'],source_instructions=rows,source_generation_manifest_sha256=hashlib.sha256(ram[0x1585c:0x15896]).hexdigest(),task=user,results=[],new_weight_training=False,interface='LM Studio localhost REST; not native Chat',coordinator_supplied='Output-only function ABI and exact instruction semantics; code will not replace the full CPU task; both signed ISA comparisons and output ABI are supplied',independent_model_verification=False);save(out/'protocol.json',record);print(out,flush=True)
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for role in ['author','reviewer']:
  task=user if role=='author'else user+'\n\nReview the earlier draft against the listing. Return a corrected bare complete C function in the same format. A same-weight review is not independent verification.\n<draft>\n'+record['results'][0]['text']+'\n</draft>'
  result=lab.generate('game','Your role is '+role+'. Recover only the declared source effect. Return bare C source, starting with #include. No Markdown fences.',task,600)
  result['role']=role;record['results'].append(result);save(out/f'{role}.json',result);(out/f'{role}.c').write_text(result['text']);save(out/'protocol.json',record);print(role,result['seconds'],result['quality_flags'],flush=True)
record['status']='raw_code_outputs_pending_native_check';save(out/'protocol.json',record);save(ROOT/'verification/actor6-local-follow-fragment-current.json',dict(directory=str(out),status=record['status']));(out/'prompts-and-responses.txt').write_text('\n\n'.join('ROLE '+x['role']+'\nREQUEST\n'+json.dumps(x['request'],indent=2,ensure_ascii=False)+'\nRAW RESPONSE\n'+x['text']for x in record['results']))
