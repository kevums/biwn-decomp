"""Local code author/reviewer on a bounded source decision; outputs unedited."""
import fcntl,json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');out=ROOT/'verification/actor14-local-voice-fragment'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
source=json.loads((ROOT/'verification/actor14-task-generation.json').read_text());rows=[r for r in source['instructions_decoded']if 0x1a674<=r['address']<0x1a690]
evidence='\n'.join(f'{r["address"]:06X}: {r["assembly"]}'for r in rows)
user='Translate only the effect on the word at 0x462C2 of this original M68000 sequence. D0 low16 initially holds a sound helper return; previous is the initial word at462C2. Stop before1A690. MOVE.W copies low16, SUBQ.W subtracts1 modulo65536, CMP.W sets flags for destination minus immediate, BLS is unsigned <=, BNE is !=. Stack/register/flags are outside this output-only extraction; do not implement them. Return only bare complete C99 source including stdint.h, no fences or commentary. Export uint16_t biwn_actor14_voice_flag(uint16_t voice, uint16_t previous). No other functions, I/O, allocation or memory reads. Derive the decision from the listing; do not claim verification.\n\n'+evidence
record=dict(status='running',directory=str(out),model=lab.CONFIG['models']['game'],source_instructions=rows,source_generation_manifest_sha256=hashlib.sha256((ROOT/'verification/actor14-task-generation.json').read_bytes()).hexdigest(),task=user,results=[],new_weight_training=False,interface='LM Studio localhost REST; not native Chat',coordinator_supplied='Output-only function ABI and exact instruction semantics; code will not replace the full CPU task',independent_model_verification=False);save(out/'protocol.json',record);print(out,flush=True)
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for role in ['author','reviewer']:
  task=user if role=='author'else user+'\n\nReview the earlier draft against the listing. Return a corrected bare complete C function in the same format. A same-weight review is not independent verification.\n<draft>\n'+record['results'][0]['text']+'\n</draft>'
  result=lab.generate('game',lab.COMMON+'\nYour role is '+role+'. Recover only the declared source effect.',task,600)
  result['role']=role;record['results'].append(result);save(out/f'{role}.json',result);(out/f'{role}.c').write_text(result['text']);save(out/'protocol.json',record);print(role,result['seconds'],result['quality_flags'],flush=True)
record['status']='raw_code_outputs_pending_native_check';save(out/'protocol.json',record);save(ROOT/'verification/actor14-local-voice-fragment-current.json',dict(directory=str(out),status=record['status']));(out/'prompts-and-responses.txt').write_text('\n\n'.join('ROLE '+x['role']+'\nREQUEST\n'+json.dumps(x['request'],indent=2,ensure_ascii=False)+'\nRAW RESPONSE\n'+x['text']for x in record['results']))
