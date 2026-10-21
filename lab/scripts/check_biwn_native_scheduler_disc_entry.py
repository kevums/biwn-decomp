"""Original native core checks new entry, heap boundary and component ABI."""
from pathlib import Path
from datetime import datetime,timezone
import json,random,os,itertools
from check_biwn_native_button_digit import ROOT,sha,save,SP,STOP
from check_biwn_native_button_movable import CPU

def main():
 out=ROOT/'verification/native-scheduler-disc-entry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 build_path=ROOT/'verification/native-scheduler-disc-build-current.json';b=json.loads(build_path.read_text())
 assert b['status']=='terminal_partial_native_scheduler_disc_built_pending_execution'
 for path,digest in b['source_sha256'].items():assert sha(path)==digest
 original=bytearray(0x200000);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);original[0x4000:0x100000]=(session/'nextstage-68000-candidate.bin').read_bytes()
 candidate=bytearray(original);candidate[0x4000:0x100000]=Path(b['derived_stage']).read_bytes();payload=Path(b['component']).read_bytes();cpu=CPU();rng=random.Random(0x4000)
 state=dict(status='checking_entry',directory=str(out),pid=os.getpid(),build_proof=str(build_path),build_proof_sha256=sha(build_path),whole_game_complete=False,game_frames=0)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-scheduler-disc-entry-active.json',state)
 def entry(image,regs,sr,new):
  n=cpu.native;l=n.lib;n.device.seed(bytes(image),0);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,sr)
  for i,v in enumerate(regs):l.m68k_set_reg(i,v)
  l.m68k_set_reg(16,0x4000);pcs=[];cycles=0
  for _ in range(10000):
   pc=l.m68k_get_reg(None,16)
   if pc==0x400a:break
   assert pc in [0x4000,0x4004]or(new and (b['staging_address']<=pc<b['staging_address']+b['native_entry_bytes']or b['resident_address']<=pc<b['resident_address']+b['component_bytes']))
   pcs.append(pc);cycles+=l.m68k_execute(1)
  else:raise AssertionError('Entry failed')
  return dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17)),n.device.ram(),pcs,cycles
 checkpoint();print(out,flush=True)
 try:
  rows=[]
  for i,(variant,ccr)in enumerate(itertools.product(range(3),range(32))):
   regs=[rng.randrange(0x100000000)for _ in range(16)];regs[15]=0x180000
   a,_,_,original_cycles=entry(original,regs,0x2000|ccr,False);actual,ram,steps,entry_cycles=entry(candidate,regs,0x2000|ccr,True)
   assert actual==a and ram[b['resident_address']:b['resident_address']+len(payload)]==payload
   # Outside source-stage changes, explicit resident payload and private
   # new supervisor scratch stack, entry adds no persistent writes.
   expected=bytearray(candidate);expected[b['resident_address']:b['resident_address']+len(payload)]=payload;expected[0xff000:0x100000]=bytes(4096)
   assert ram[:0x1fffc4]==expected[:0x1fffc4]and ram[0x200000:]==expected[0x200000:]
   rows.append(dict(variant=variant,CCR=ccr,full_CPU=a,new_instruction_count=len(steps),original_cycles=original_cycles,new_entry_cycles=entry_cycles))
  save(out/'entry-cases.json',rows);installed=ram
  # Execute patched original heap initialization, then allocations/compaction.
  l=cpu.native.lib;n=cpu.native;n.device.seed(installed,1);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2700);l.m68k_set_reg(15,SP);l.m68k_set_reg(16,0x1557a);n.device.direct(SP,4,STOP)
  for i in range(3000):
   pc=l.m68k_get_reg(None,16)
   if pc==STOP:break
   assert 0x1557a<=pc<0x155c2;l.m68k_execute(1)
  else:raise AssertionError('Heap init failed')
  heap_image=n.device.ram();u=lambda image,a:int.from_bytes(image[a:a+4],'big');assert u(heap_image,0x112d60)==b['heap_start']
  assert u(heap_image,b['heap_start'])==0x1c0000-b['heap_start'] and u(heap_image,0x112d64)==0x1c0000-b['heap_start']
  assert heap_image[0x112960:0x112d60]==bytes(1024) and heap_image[b['resident_address']:b['resident_address']+len(payload)]==payload
  allocated,h1,_=cpu.memory_call(heap_image,0x152a2,[137]);allocated,h2,_=cpu.memory_call(bytes(allocated),0x152a2,[260]);compacted,_,_=cpu.memory_call(bytes(allocated),0x15200,[])
  assert h1 and h2 and all(u(compacted,h)>=b['heap_start']+8 for h in [h1,h2]);assert compacted[b['resident_address']:b['resident_address']+len(payload)]==payload
  (out/'installed-and-heap-initialized-RAM.bin').write_bytes(heap_image)
  bits=[19,18,17,7,6,5,4,3,2,1];incoming=[0,0x8000ffff,0xdeadbeef]
  cases=list(dict.fromkeys([(sum(1<<bit for bit,f in zip(bits,flags)if f),d,0x2000)for flags in itertools.product([0,1],repeat=10)for d in incoming]+[(m,d,mode|ccr)for m in [0]+[1<<bit for bit in bits]for d in incoming for mode in [0,0x2000]for ccr in range(32)]))
  state.update(status='checking_installed_native_ABI',entry_cases=len(rows),heap_initialize_instructions=i);checkpoint();results=[]
  for i,(mask,d,sr)in enumerate(cases):
   expected,_=cpu.execute_ranges(bytes(original),0x1b718,[(0x1b718,0x1b780)],mask,d,sr)
   actual,pcs=cpu.execute_ranges(heap_image,0x1b718,[(0x1b718,0x1b71e),(b['resident_address'],b['resident_address']+len(payload))],mask,d,sr)
   assert actual==expected
   results.append(dict(mask=mask,incoming_D0=d,incoming_SR=sr,matched=True))
   if i%512==0:state['completed_component_cases']=i;checkpoint();print('resident ABI',i,'/',len(cases),flush=True)
  save(out/'component-cases.json',results);cpu.close()
  state.update(status='terminal_native_entry_heap_and_component_pass',entry_cases=len(rows),component_cases=len(cases),all16registers_PC_SR_match=True,heap_reserved_bytes=b['heap_bytes_reserved'],staging_window_4096_bytes_cleared=True,payload_unchanged_after_heap_init_allocation_compaction=True,new_compiled_loader_runs=True,source_sha256={str(Path(__file__)):sha(__file__)},scope='Native new mainstage entry copies native bundle, clears4096temporary staging bytes from resident code, preserves original entry registers/SR/SP and resumes400A in96CCR/register cases. Patched original heap init excludes the full new native bundle; actual allocator/compactor preserve resident code.5151fullABIcases pass through new disc-stage JMP. No game frames or physical console in this checker.')
  checkpoint();save(ROOT/'verification/native-scheduler-disc-entry-current.json',state);print(json.dumps({k:state[k]for k in ['status','entry_cases','component_cases','heap_reserved_bytes']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
