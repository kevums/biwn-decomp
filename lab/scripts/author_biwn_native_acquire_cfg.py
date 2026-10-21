"""Fresh local Author with explicit coordinator CFG/ABI normalization."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,os,fcntl,re,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,assistant_chat
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 prior=ROOT/'runs/local-native-resource-acquire-20261018T105359.285475Z/prepared-author.json';prepared=json.loads(prior.read_text())
 packet=json.loads((ROOT/'verification/native-resource-acquire-preflight-current.json').read_text())
 branches=[
 [0x1af1c,'BEQ','descriptor[0] == 0',0x1affa,0x1af20],
 [0x1af32,'BNE','cacheID != requestedID',0x1af6c,0x1af34],
 [0x1af38,'BEQ','refcount == 0',0x1af6c,0x1af3a],
 [0x1af42,'BNE','ready != 0',0x1af5e,0x1af44],
 [0x1af5c,'BEQ','fresh ready == 0',0x1af4c,0x1af5e],
 [0x1af72,'BLE','signed slot counter <= 49',0x1af28,0x1af74],
 [0x1af92,'BNE','refcount != 0',0x1aff2,0x1af94],
 [0x1afa4,'BEQ','allocator handle == 0 (MOVE.L store flags)',0x1affa,0x1afa6],
 [0x1afde,'BEQ','fresh refcount == 1',0x1afec,0x1afe0],
 [0x1aff8,'BLE','signed slot counter <= 49',0x1af88,0x1affa]]
 ins={i['address']:i for i in packet['instructions']}
 rows=[]
 for pc,mn,pred,t,f in branches:
  assert ins[pc]['assembly'].startswith(mn.lower())
  rows.append(dict(pc=hex(pc),branch=mn,when_predicate_true=hex(t),when_predicate_false=hex(f),predicate=pred))
 hints='''Coordinator typed ABI normalization (extensive guidance):
1. All first-scan slot MULS values are semantic full D0 (r0), not only a private offset. The second scan computes offset in D2, leaving D0 at588 until allocation changes it. The descriptor uses SIGNED int16 ID*12, and LEA sets r8=464D0 even on failure.
2. Matched active slot performs TWO volatile refcount reads: TST then ADDQ reads again; use acquire_add1w on second read and write result. Before first wait MOVE.L D0,D2 sets N/Z from offset; use acquire_nz32. Every rejected scan iteration increments boundedcounter, so its X becomes0; both no-slot exits finally return0 with X0.
3. Supplied adapters exclusively own all stack argument pushes/cleanup and allocator/load argument READS. Do not write any r15-negative stack bytes, or duplicate descriptor/handle reads before adapters. Allocate takes DESCRIPTOR ADDRESS; load takes DESCRIPTOR ADDRESS and CACHE ENTRY ADDRESS (not handle field address). Wait/signal take just r. Child caller-saved frame outputs persist.
4. After either successful cache path, reread handle and set r0 plus acquire_nz32. Missing descriptor/failed allocation/fullcache returnr0=0 and acquire_nz32. Initial missingdescriptor preserves incomingX; failureafterallocator preserves returnedX; counters clearX. Load adapter reproduces D1=entry+8 and clearsX exactly for this boundedtable, then reads/pushes arguments in original order.
5. Do not call acquire_cmp1w for ID comparison; ordinary uint16 equality is enough there. It exists only for final CMP.W #1,refs. Ready0 waits until NONZERO. Refcount0 selects allocation; refcount!=0 skips the second-scan slot. A first-scan hit must return, never allocate. Keep every source volatile reread across callbacks.
'''
 user=prepared['user']+'\nCOORDINATOR BRANCH TABLE (true target versus false fallthrough; this is source-derived guidance, not text to copy as C):\n'+json.dumps(rows,indent=2)+'\n'+hints+'\nUse a fresh structured translation. No earlier rejected C is in this context. Return one complete C99 file in one c code fence.'
 out=ROOT/'runs'/('local-native-resource-acquire-cfg-'+lab.stamp());out.mkdir();print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),new_training=False,native_Chat=False,reasoning='off',source_accepted=False,coordinator_supplied_reference_C=False,coordinator_supplied_extensive_CFG_ABI_and_register_guidance=True,autonomous_decompilation=False,same_weights=True,prior_rejected_C_in_context=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-acquire-cfg-active.json',state)
 save(out/'branch-table.json',rows);save(out/'prepared-author.json',dict(system=prepared['system'],user=user,max_output_tokens=4000,reasoning='off'));(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+prepared['system']+'\nUSER\n'+user+'\n');mark()
 try:
  with(ROOT/'runs/.inference.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game');lab.CONFIG['models']['game']['reasoning']='off';state['status']='fresh_guided_CFG_author_running';mark();res=lab.generate('game',prepared['system'],user,4000)
  save(out/'response.json',res)
  with(out/'prompts-and-responses.txt').open('a')as f:f.write('RESPONSE\n'+res['text'])
  blocks=re.findall(r'```c\s*\n(.*?)```',res['text'],re.S);assert len(blocks)==1;source=out/'resource-acquire-native.c';source.write_text(blocks[0].strip()+'\n')
  state.update(status='terminal_fresh_guided_CFG_author_pending_native_gates',source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),raw_model_C_unchanged=True,seconds=res['seconds'],usage=res['usage'],quality_flags=res['quality_flags'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-acquire-cfg-current.json',state);print(state['status'],res['seconds'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
