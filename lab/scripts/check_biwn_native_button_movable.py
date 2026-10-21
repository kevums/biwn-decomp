"""Movable native C component: real checkpoint allocation, compaction, ABI.
Coordinator wrote this harness, relative-call adaptation and trampoline.
The reference remains original BIWN; no game frames or disc writes here.
"""
from datetime import datetime,timezone
from pathlib import Path
import itertools,json,os,subprocess,ctypes as c
from check_biwn_native_button_digit import ROOT,SP,STOP,sha,save
from check_biwn_native_button_full_ABI import NativeCPU

ENTRY=0x1b718
class CPU(NativeCPU):
 def execute_ranges(self,image,entry,regions,mask,incoming,sr):
  n=self.native;l=n.lib;n.device.seed(image,0);l.m68k_pulse_reset();l.m68k_set_irq(0)
  l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP);l.m68k_set_reg(17,sr);l.m68k_set_reg(15,SP)
  regs=[0]*16;regs[0]=incoming;regs[1]=0x11223344;regs[8]=0x33445566;regs[9]=0x55667788;regs[15]=SP
  for i,reg in enumerate([2,3,4,5,6,7,10,11,12,13,14]):regs[reg]=(0x12345678+i*0x11111111)&0xffffffff
  for reg,value in enumerate(regs):l.m68k_set_reg(reg,value)
  n.device.direct(SP,4,STOP);n.device.direct(SP+4,4,mask);expected=bytearray(image);expected[SP:SP+8]=STOP.to_bytes(4,'big')+mask.to_bytes(4,'big')
  l.m68k_set_reg(16,entry);steps=[]
  for _ in range(10000):
   pc=l.m68k_get_reg(None,16)
   if pc==STOP:break
   assert any(a<=pc<b for a,b in regions),('escaped',hex(pc));steps.append(pc);l.m68k_execute(1)
  else:raise AssertionError('No return')
  returned=n.device.ram();assert returned[:SP-0x1000]==expected[:SP-0x1000]and returned[SP:]==expected[SP:]
  return dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17)),steps
 def memory_call(self,image,entry,args):
  n=self.native;l=n.lib;n.device.seed(image,1);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2700)
  for reg in range(16):l.m68k_set_reg(reg,0)
  l.m68k_set_reg(15,SP);l.m68k_set_reg(16,entry);n.device.direct(SP,4,STOP)
  for i,value in enumerate(args):n.device.direct(SP+4+i*4,4,value)
  steps=0
  for _ in range(2000000):
   pc=l.m68k_get_reg(None,16)
   if pc==STOP:break
   assert 0x15200<=pc<0x1545c or 0xe3e0<=pc<0xe4aa,('memory escaped',hex(pc))
   l.m68k_execute(1);steps+=1
  else:raise AssertionError('Memory call failed to return')
  returned=bytearray(n.device.ram());returned[SP-0x1000:SP+32]=image[SP-0x1000:SP+32]
  return returned,l.m68k_get_reg(None,0),steps

def main():
 out=ROOT/'verification/native-button-movable'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),whole_game_complete=False,game_frames=0,disc_modified=False,coordinator_modified_relative_shim=True,raw_model_source_unchanged=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-button-movable-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  n=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
  bins=[]
  for base in [0x10000,0x1975a0]:
   build=out/f'build-{base:x}';command=['make','-f','Makefile.movable','movable','BUILD='+str(build),'COMPONENT_BASE='+hex(base)]
   p=subprocess.run(command,cwd=n,capture_output=True,text=True);(out/f'make-{base:x}.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
   bins.append((build/'button-digit-movable.bin').read_bytes())
   (build/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/'button-digit-movable.elf')],text=True))
  code=bins[0];assert code==bins[1], 'Component is not position independent'
  natural=json.loads((ROOT/'verification/natural-coordinate-gameplay-current.json').read_text());confirm=next(row for row in natural['cases']if row['case']=='confirm');baseline=Path(confirm['source_trace']).parent.parent
  snapshot_path=baseline/'C/warm-RAM.bin';original=snapshot_path.read_bytes();assert len(original)==0x200000
  prior=json.loads((ROOT/'verification/native-button-full-ABI-current.json').read_text());assert original[ENTRY:0x1b780]==Path(prior['directory'],'original-disc-stage-button-digit.bin').read_bytes()
  cpu=CPU();allocated,handle,allocation_steps=cpu.memory_call(original,0x152a2,[len(code)])
  assert 0x112960<=handle<0x112d60 and handle%4==0
  read32=lambda ram,a:int.from_bytes(ram[a:a+4],'big')
  address=read32(allocated,handle);assert 0x15edc8<=address<=0x1c0000-len(code)
  assert read32(allocated,address-4)==handle and read32(allocated,address-8)>=len(code)+8
  allocated[address:address+len(code)]=code
  # Reserve target slot, preserve A0, resolve handle, tail-return into blob.
  source=out/'handle-trampoline.S';source.write_text('.text\n.globl trampoline\ntrampoline:\nsubq.l #4,%sp\nmove.l %a0,-(%sp)\nmovea.l '+hex(handle)+',%a0\nmove.l %a0,4(%sp)\nmovea.l (%sp)+,%a0\nrts\n')
  subprocess.run([prefix+'as','-m68000','-o',str(out/'trampoline.o'),str(source)],check=True)
  subprocess.run([prefix+'objcopy','-O','binary',str(out/'trampoline.o'),str(out/'trampoline.bin')],check=True)
  trampoline=(out/'trampoline.bin').read_bytes();assert len(trampoline)<=104
  allocated[ENTRY:ENTRY+len(trampoline)]=trampoline
  (out/'allocated-RAM.bin').write_bytes(allocated)
  compacted,_,compaction_steps=cpu.memory_call(bytes(allocated),0x15200,[]);new_address=read32(compacted,handle)
  assert new_address!=address and compacted[new_address:new_address+len(code)]==code
  (out/'compacted-RAM.bin').write_bytes(compacted)
  state.update(status='checking_relocated_ABI',payload_bytes=len(code),trampoline_bytes=len(trampoline),handle=handle,allocated_address=address,compacted_address=new_address,allocation_steps=allocation_steps,compaction_steps=compaction_steps);checkpoint();print(json.dumps(state),flush=True)
  bits=[19,18,17,7,6,5,4,3,2,1];incoming=[0,0x8000ffff,0xdeadbeef]
  cases=list(dict.fromkeys([(sum(1<<b for b,f in zip(bits,flags)if f),d,0x2000)for flags in itertools.product([0,1],repeat=10)for d in incoming]+[(m,d,mode|ccr)for m in [0]+[1<<b for b in bits]for d in incoming for mode in [0,0x2000]for ccr in range(32)]))
  rows=[]
  for i,(mask,d,sr)in enumerate(cases):
   expected,_=cpu.execute_ranges(original,ENTRY,[(ENTRY,0x1b780)],mask,d,sr)
   counts=[]
   for ram,addr in [(allocated,address),(compacted,new_address)]:
    actual,steps=cpu.execute_ranges(bytes(ram),ENTRY,[(ENTRY,ENTRY+len(trampoline)),(addr,addr+len(code))],mask,d,sr)
    assert actual==expected,('ABI',i,hex(addr),expected,actual)
    assert any(addr<=pc<addr+len(code)for pc in steps)
    counts.append(len(steps))
   rows.append(dict(mask=mask,incoming_D0=d,incoming_SR=sr,native_steps=counts,matched=True))
   if i%512==0:state['completed_cases']=i;checkpoint();print('movable',i,'/',len(cases),flush=True)
  cpu.close();save(out/'cases.json',rows)
  patches=[]
  # Explicit setup overlay; allocator executed above, not automatically in game loader.
  raw=bytes(allocated);start=None
  for a in range(len(original)+1):
   changed=a<len(original)and original[a]!=raw[a]
   if changed and start is None:start=a
   if not changed and start is not None:
    patches.append(dict(address=hex(start),original=original[start:a].hex(),replacement=raw[start:a].hex()));start=None
  save(out/'allocated-overlay.json',dict(patches=patches,scope='Explicit checkpoint setup from native original allocator; no cold-loader installation.'))
  paths=[n/x for x in ['Makefile','Makefile.movable','movable.ld','button-digit-movable-shim.S']]+[n.parent/'biwn_inventory_select.c',Path(__file__).resolve()]
  state.update(status='terminal_native_movable_component_ABI_matches',cases=len(cases),native_candidate_comparisons=2*len(cases),all16registers_PC_SR=True,nonprivate_final_RAM_unchanged_per_call=True,original_allocator_executed=True,original_compactor_and_pinned_blitter_executed=True,position_independent_link_binaries_equal=True,source_sha256={str(p):sha(p)for p in paths},snapshot=str(snapshot_path),snapshot_sha256=sha(snapshot_path),compiled_binary=str(out/'build-10000/button-digit-movable.bin'),compiled_binary_sha256=sha(out/'build-10000/button-digit-movable.bin'),overlay=str(out/'allocated-overlay.json'),scope='Original native game allocator reserves component in actual source-checkpoint heap. Native compactor moves it and updates its handle. Original entry trampoline resolves current handle on each call. 5151 full-register/flags cases match before and after actual compaction. Private stack excluded; no game frames, cold-loader install, native image, timing or hardware proof. Coordinator changed accepted guided local shim to a relative call and wrote trampoline/harness.')
  checkpoint();save(ROOT/'verification/native-button-movable-current.json',state);print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
