"""Add native-checked executable targets and a borrow/zero correction to v3."""
import ctypes as c,json,hashlib,shutil,subprocess,os,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();previous=Path(json.loads((ROOT/'verification/game-source-v3-dataset.json').read_text())['directory']);old=json.loads((previous/'split-manifest.json').read_text());records=[json.loads(x)for x in Path(old['input_path']).read_text().splitlines()];assert len(records)==57
out=ROOT/'training/game'/('source-v4-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);snap=out/'source-snapshots';snap.mkdir()
moveq='#include <stdint.h>\n\nvoid biwn_moveq_effect(uint8_t immediate, uint32_t *d, uint16_t *sr) {\n    uint32_t value = (uint32_t)(int32_t)(int8_t)immediate;\n    *d = value;\n    *sr = (uint16_t)((*sr & 0xFFF0u) | (value == 0 ? 4u : 0u) | ((value & 0x80000000u) ? 8u : 0u));\n}\n'
(snap/'moveq-ground-truth.c').write_text(moveq)
# Reuse the independent original-CPU comparison, with a separate pointer.
for phase in ['base','adapter']:save(snap/f'{phase}-m68k-C-effect.json',dict(response=moveq))
save(snap/'evaluation-pointer.json',dict(directory=str(snap)))
run=subprocess.run([sys.executable,str(ROOT/'scripts/check_game_v2_generated_moveq_C.py'),'--evaluation-pointer',str(snap/'evaluation-pointer.json'),'--report-pointer',str(snap/'moveq-native-check.json')],cwd=ROOT,capture_output=True,text=True);(snap/'moveq-native-check.log').write_text(run.stdout+run.stderr);assert run.returncode==0
proof=json.loads((snap/'moveq-native-check.json').read_text());assert all(x['cases']==512 and x['accepted']for x in proof['results']);assert (snap/'base-moveq.c').read_bytes()==(snap/'adapter-moveq.c').read_bytes()
voice=json.loads((ROOT/'verification/actor14-local-voice-fragment-reviewed.json').read_text());assert voice['accepted']and voice['cases']==65557;voice_code=(Path(voice['directory'])/'author-extracted.c').read_text();shutil.copy2(Path(voice['directory'])/'native-check.json',snap/'voice-native-check.json');shutil.copy2(Path(voice['directory'])/'author-extracted.c',snap/'voice-code.c')
# Capture the actual native flags before BLS, not just a derived answer.
sys.path.insert(0,str(ROOT/'scripts'));import check_biwn_media_setup_cpu as media
entry=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(entry['directory'])/'libentry-helpers.dylib',[]);live=json.loads((ROOT/'verification/natural-actor14-task-current.json').read_text());ram=(Path(live['directory'])/'native-RAM.bin').read_bytes();runtime.reset(ram,0);traces=[]
try:
 for word in [0,1,2,3,4,0xffff]:
  cpu=media.CPU();cpu.pc=0x1a674;cpu.registers[0]=word;cpu.registers[15]=cpu.usp=0x1ff000;cpu.ssp=0x200000;runtime.seed_cpu(cpu)
  for _ in range(16):
   if runtime.cpu().pc==0x1a680:break
   runtime.core.m68k_execute(1)
  else:raise AssertionError('CMP flag capture bound')
  actual=runtime.cpu();traces.append(dict(voice=word,D0_low=actual.registers[0]&65535,SR=actual.sr,C=actual.sr&1,Z=bool(actual.sr&4),BLS=bool(actual.sr&5)))
 assert [x['BLS']for x in traces]==[False,True,True,False,False,False];save(snap/'original-BLS-flags.json',traces)
finally:runtime.oracle.close()
system=records[0]['messages'][0]['content'];new=[]
def add(user,target,evidence):
 row=dict(source_id='m68k-native-isa',review='source_checked_coordinator_target',messages=[dict(role='system',content=system),dict(role='user',content=user),dict(role='assistant',content=target)],review_evidence=evidence);records.append(row);new.append(row)
add('Return only bare complete C99 source including stdint.h. Export void biwn_moveq_effect(uint8_t immediate, uint32_t *d, uint16_t *sr). Implement M68000 MOVEQ effect only: sign extend8bits into32bit D, preserve upper SR and X16, N8 follows sign, Z4 follows zero, V2/C1 clear. Pointers valid; no RTS, I/O or other functions.',moveq,str(snap/'moveq-native-check.json'))
add('Return only bare complete C99 source including stdint.h. Export uint16_t biwn_actor14_voice_flag(uint16_t voice,uint16_t previous). Original word sequence: D1=voice;D0=(voice-1)mod65536;CMP.W#1,D0;BLS sets flag word to1;otherwise CMP.W#4,D1;BNE preserves prior word, equality sets1. Extract only that flag output. No full CPU/register/stack claim.',voice_code,str(snap/'voice-native-check.json'))
add('Original M68000 trace before BLS after SUBQ.W#1,D0;CMP.W#1,D0: '+json.dumps(traces)+'\nWhy is testing the wrapped subtraction result unsigned<=0 incorrect?', 'CMP establishes an unsigned relation between its operands through borrow C and equality Z. BLS branches when C or Z is set, not when the wrapped result is <=0. Voice1 gives decremented D0=0; CMP0-1 wraps toFFFF but sets C, so BLS is taken. Voice2 gives D0=1 and CMP equality sets Z. Voice0 gives D0=FFFF, no borrow/equality, so BLS is not taken. Keep 16bit word subtraction and flags separate from an unsigned comparison of the wrapped result.',str(snap/'original-BLS-flags.json'))
add('A local Author emitted fenced C for the source voice-flag output; the C body passed65557original CPU output comparisons after fence removal. Reviewer emitted truncated prose and misread BLS. Is this a full task recovery, independent review, or a format pass?', 'No. This is an accepted output-only flag decision with an explicit coordinator ABI and instruction semantics. Only Markdown fences were removed; the code body was unchanged. The raw answer failed the requested bare-source format. It does not reproduce full CPU, private RAM, stack or flags and is not linked live. The same-weight Reviewer failed and is not independent verification. Keep the raw failed review, scoped machine check and original full-task source proof separate.',str(snap/'voice-native-check.json'))
assert len(records)==61;input_path=out/'reviewed-source-examples.jsonl';input_path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n'for x in records))
for split in ['valid','test']:shutil.copy2(previous/(split+'.jsonl'),out/(split+'.jsonl'));assert sha(out/(split+'.jsonl'))==old['split_sha256'][split]
train=[dict(messages=x['messages'])for x in records if x['source_id']in old['source_groups']['train']];assert len(train)==55;(out/'train.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n'for x in train))
from mlx_lm.tokenizer_utils import load as load_tokenizer
tokenizer=load_tokenizer(Path.home()/'.lmstudio/models'/old['base_repository'],{});lengths=[]
for i,row in enumerate(records):
 full=tokenizer.apply_chat_template(row['messages'],tokenize=True,add_generation_prompt=False,enable_thinking=False);prefix=tokenizer.apply_chat_template(row['messages'][:-1],tokenize=True,add_generation_prompt=True,enable_thinking=False);assert full[:len(prefix)]==prefix and len(full)>len(prefix)and len(full)<=2048;lengths.append(dict(record=i,tokens=len(full),target_tokens=len(full)-len(prefix)))
manifest={**old,'input_path':str(input_path),'input_sha256':sha(input_path),'records':61,'unique_records':61,'previous_dataset':str(previous),'split_sha256':{k:sha(out/(k+'.jsonl'))for k in ['train','valid','test']},'scope':'55train/3valid/3test. Added machine-checked pure C effects and original native BLS flags. Prior project validation/test groups unchanged and previously inspected; adaptive diagnostic, not independent generalization.'};save(out/'split-manifest.json',manifest);save(out/'token-preflight.json',lengths);save(out/'source-provenance.json',dict(new_records=list(range(57,61)),reviewer='Codex coordinator/source-native crosscheck, not human labels',proofs=[str(snap/'moveq-native-check.json'),str(snap/'voice-native-check.json'),str(snap/'original-BLS-flags.json')],MOVEQ_target_coordinator_authored=True,voice_target_local_authored_with_coordinator_ABI_semantics=True,code_fence_removal_declared=True));report=dict(status='game_source_v4_reviewed_prepared_untrained',directory=str(out),records=61,train=55,valid=3,test=3,max_tokens=max(x['tokens']for x in lengths));save(ROOT/'verification/game-source-v4-dataset.json',report);print(json.dumps(report))
