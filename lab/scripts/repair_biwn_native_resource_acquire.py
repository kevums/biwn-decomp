"""One explicitly guided local repair; no reference C supplied or acceptance implied."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,sys,re,fcntl,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 prior=json.loads((ROOT/'verification/local-native-resource-acquire-current.json').read_text());pd=Path(prior['directory']);prepared=json.loads((pd/'prepared-author.json').read_text())
 failure=ROOT/'verification/native-resource-acquire/20261018T105555.007605Z/mismatch.json';m=json.loads(failure.read_text())
 guidance='''Coordinator instruction/ABI defect review (extensive guidance; not an autonomous second attempt):
- The ID WORD at r15+4 is signed for MULS.W #12. Use (int32_t)(int16_t)id*12 for descriptor offset. LEA464D0,A0 changes semantic r8 to464D0 even if the descriptor is absent.
- Semantic r0 is the full MULS result on descriptor calculation and each first scan slot, not merely a private C local. The second scan uses D2 and leaves D0 at the last first-scan offset until allocation changes it.
- CMP.W (entry),D5 tests equality of cache ID and ID. acquire_cmp1w is ONLY for CMP.W #1,refs after load. Use ordinary id equality for the first scan. BNE after CMP skips this slot when unequal; BEQ after TST refs skips when zero.
- ADDQ.W #1,refs is a second volatile read and write after the TST.W read. Use acquire_add1w on that second read so X/carry/overflow are exact. TST/MOVE preserve X. The unsuccessful slot-counter increments reset X (bounded0..50).
- TST.W ready followed by BNE goes directly to return when ready is NONZERO. Zero ready enters wait. MOVE.L D0,D2 before the first wait sets N/Z from offset while preserving X; capture wait seeds/captures caller outputs. Repeat until the fresh ready read is NONZERO, then reread handle and return. Do not fall through into other slots after waiting.
- In second scan BNE after TST refs skips occupied slots. Zero refs selects allocation. Call allocate_capture(r,descriptor_address), not the descriptor size; it itself reads descriptor+8 exactly once at that point. Set semantic frame inputs/flags from the listing, including r0 and r8.
- Both PEA and all argument pushes/cleanup are owned by the capture adapters. NO AW32(r15-negative,..) for arguments, no manual clearing of these stack words, and no extra AR32 reads to prepare arguments. These writes corrupt original public MOVEM saves.
- After successful allocation the source stores handle, clears ready, writes ID and refs1, then load_capture(r,descriptor_address,entry_address). Pass addresses, not loaded values or ready-pointer. This adapter computes r1/flags and performs all5 source argument reads. It rereads descriptor and handle after allocation.
- After load, reread refs and use acquire_cmp1w; signal_capture only when refs!=1. Load/signal/wait may replace r0/r1/r8/r9/CCR; do not restore stale inputs afterward. Every successful return reads handle fresh after callbacks and applies acquire_nz32 to its full returned D0. Every zero-result return applies acquire_nz32(0). Full-cache/final unsuccessful scans have X0 due to original counter ADDQ. Preserve r16 upper bits.
No coordinator reference C is provided. Derive the remaining behavior from the complete original assembly/header above. Return one complete corrected C file, no invented guards.'''
 user=prepared['user']+'\nREJECTED DRAFT:\n'+Path(prior['source']).read_text()+'\n'+guidance+'\nFIRST NATIVE FAILURE:\n'+json.dumps({k:v for k,v in m.items()if k!='parameters'})
 system=prepared['system'].replace('local native C Author','local guided Repair Author')
 out=ROOT/'runs'/('local-native-resource-acquire-repair-'+lab.stamp());out.mkdir();print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),previous=str(pd),failure=str(failure),reasoning='off',source_accepted=False,new_training=False,native_Chat=False,coordinator_supplied_reference_C=False,coordinator_supplied_extensive_instruction_ABI_and_control_flow_guidance=True,autonomous_decompilation=False,independent_model_validation=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-resource-acquire-repair-active.json',state)
 mark();save(out/'prepared-author.json',dict(system=system,user=user,max_output_tokens=4000,reasoning='off'));(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\n')
 try:
  with(ROOT/'runs/.inference.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game');lab.CONFIG['models']['game']['reasoning']='off';state['status']='guided_repair_running';mark();a=lab.generate('game',system,user,4000)
  save(out/'response.json',a)
  with(out/'prompts-and-responses.txt').open('a')as f:f.write('RESPONSE\n'+a['text'])
  blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1;p=out/'resource-acquire-native.c';p.write_text(blocks[0].strip()+'\n')
  state.update(status='terminal_guided_acquire_repair_pending_native_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_model_C_unchanged=True,reported_seconds=a['seconds'],usage=a['usage'],quality_flags=a['quality_flags'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-resource-acquire-current.json',state);print(state['status'],a['seconds'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
