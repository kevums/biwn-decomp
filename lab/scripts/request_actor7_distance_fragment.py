"""Local code author/reviewer on a bounded source decision; outputs unedited."""
import fcntl,json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');out=ROOT/'verification/actor7-local-distance-fragment'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
live=json.loads((ROOT/'verification/natural-actor8-task-current.json').read_text());ram=(Path(live['directory'])/'native-RAM.bin').read_bytes()
import generate_biwn_entry_setup_cpu as gen
rows=gen.loader.base.binary_tools.m68k_instructions(ram[0x14d7c:0x14dba],0x14d7c)[0]
evidence='\n'.join(f'{r["address"]:06X}: {r["assembly"]}'for r in rows)
user='Translate only the output decision of this original M68000 sequence, stopping at14DBA. D0 initially holds int32_t distance; previous is the uint16_t word at actor+0x6C. If source calls207CC, record its pushed16bit message number; the helper returns normally and does not change actor+6C. No call means messageFFFF. CMP.W sets16bit flags, CMP.L sets32bit flags; BGT and BLE are signed comparisons, BEQ is equality. Ignore other registers, stack and flags in the exported output. Return only bare complete C99 source including stdint.h, no fences or commentary. Export uint32_t biwn_actor7_distance_decision(uint16_t previous, int32_t distance). Pack final actor+6C word in low16 and message number in high16. No other functions, I/O, allocation, pointers or memory reads. Derive the decision from the listing; do not claim verification.\n\n'+evidence
record=dict(status='running',directory=str(out),model=lab.CONFIG['models']['game'],source_instructions=rows,source_generation_manifest_sha256=hashlib.sha256(ram[0x14d7c:0x14dba]).hexdigest(),task=user,results=[],new_weight_training=False,interface='LM Studio localhost REST; not native Chat',coordinator_supplied='Output-only function ABI and exact instruction semantics; code will not replace the full CPU task; both signed ISA comparisons and output ABI are supplied',independent_model_verification=False);save(out/'protocol.json',record);print(out,flush=True)
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for role in ['author','reviewer']:
  task=user if role=='author'else user+'\n\nReview the earlier draft against the listing. Return a corrected bare complete C function in the same format. A same-weight review is not independent verification.\n<draft>\n'+record['results'][0]['text']+'\n</draft>'
  result=lab.generate('game',lab.COMMON+'\nYour role is '+role+'. Recover only the declared source effect.',task,600)
  result['role']=role;record['results'].append(result);save(out/f'{role}.json',result);(out/f'{role}.c').write_text(result['text']);save(out/'protocol.json',record);print(role,result['seconds'],result['quality_flags'],flush=True)
record['status']='raw_code_outputs_pending_native_check';save(out/'protocol.json',record);save(ROOT/'verification/actor7-local-distance-fragment-current.json',dict(directory=str(out),status=record['status']));(out/'prompts-and-responses.txt').write_text('\n\n'.join('ROLE '+x['role']+'\nREQUEST\n'+json.dumps(x['request'],indent=2,ensure_ascii=False)+'\nRAW RESPONSE\n'+x['text']for x in record['results']))
