"""Compiled native arithmetic versus original complete return ABI.
Native DIVU-by-zero path uses a declared test RTE handler; normalized saved
fault PC reflects code relocation. No original arithmetic code in candidate.
"""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,random,subprocess,os
from check_biwn_native_button_digit import ROOT,SP,STOP,sha,save
from check_biwn_scheduler import Native

BASE=0x15edc0;HANDLER=0x1f1000;SSP=0x1ff000
class Runner:
 def __init__(self):self.n=Native()
 def run(self,image,entry,regions,a,b,sr,d2,d1):
  n=self.n;l=n.lib;n.device.seed(image,0);l.m68k_pulse_reset();l.m68k_set_irq(0)
  l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SSP);l.m68k_set_reg(17,sr);l.m68k_set_reg(15,SP)
  regs=[(0x10203040+i*0x091a2b3c)&0xffffffff for i in range(16)];regs[1]=d1;regs[2]=d2;regs[15]=SP
  for i,v in enumerate(regs):l.m68k_set_reg(i,v)
  n.device.direct(20,4,HANDLER);n.device.direct(HANDLER,2,0x4e73)
  for address,value in [(SP,STOP),(SP+4,a),(SP+8,b)]:n.device.direct(address,4,value)
  expected=bytearray(image);expected[20:24]=HANDLER.to_bytes(4,'big');expected[HANDLER:HANDLER+2]=bytes.fromhex('4e73');expected[SP:SP+12]=STOP.to_bytes(4,'big')+a.to_bytes(4,'big')+b.to_bytes(4,'big')
  l.m68k_set_reg(16,entry);steps=0;faults=[]
  for _ in range(20000):
   pc=l.m68k_get_reg(None,16)
   if pc==STOP:break
   assert pc==HANDLER or any(lo<=pc<hi for lo,hi in regions),('escaped',hex(pc),hex(entry))
   if pc==HANDLER:
    stack=l.m68k_get_reg(None,15);ram=n.device.ram();faults.append(dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],SR=l.m68k_get_reg(None,17),frame_SR=int.from_bytes(ram[stack:stack+2],'big'),frame_PC=int.from_bytes(ram[stack+2:stack+6],'big')))
   l.m68k_execute(1);steps+=1
  else:raise AssertionError(('no return',hex(entry),hex(a),hex(b)))
  returned=n.device.ram();spans=sorted([(SP-0x2000,SP),(SSP-256,SSP)])
  last=0
  for lo,hi in spans:
   assert returned[last:lo]==expected[last:lo],('nonprivate RAM changed',hex(last),hex(lo));last=hi
  assert returned[last:]==expected[last:]
  result=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17),USP=n.prefix[16]if sr&0x2000 else l.m68k_get_reg(None,15),SSP=l.m68k_get_reg(None,15)if sr&0x2000 else n.prefix[17])
  assert result['registers'][15]==SP+4
  return result,faults,steps

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args();out=ROOT/'verification/native-math'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),whole_game_complete=False,game_frames=0,new_training=False,coordinator_authored_glue=True)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-math-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');command=['make','-f','Makefile.math','math','BUILD='+str(out/'build')];p=subprocess.run(command,cwd=native,capture_output=True,text=True);(out/'make.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  elf=out/'build/native-math.elf';binary=out/'build/native-math.bin';code=binary.read_bytes();symbols={}
  nm=subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True)
  for line in nm.splitlines():
   parts=line.split()
   if len(parts)==3:symbols[parts[2]]=int(parts[0],16)
  save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True));(out/'ELF-header.txt').write_text(subprocess.check_output([prefix+'readelf','-h',str(elf)],text=True))
  original=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();candidate=bytearray(original);candidate[BASE:BASE+len(code)]=code;candidate=bytes(candidate)
  names={0xe540:'biwn_native_multiply',0xe588:'biwn_native_division',0xe60a:'biwn_native_remainder'};r=Runner();rng=random.Random(0xe588);values=[0,1,2,0x7fff,0x8000,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff,0xffff0000,0x8000ffff]
  base=[(a,b,0x2000,0x12345678,0xdeadbeef)for a in values for b in values]+[(rng.getrandbits(32),rng.getrandbits(32),0x2000,rng.getrandbits(32),rng.getrandbits(32))for _ in range(512)]
  matrix=[(a,b,mode|ccr,d2,0xdeadbeef)for a,b in [(0,1),(1,1),(0x80000000,1),(0x80000000,0xffffffff),(0x12345678,0x8000),(0xffffffff,0x10000),(0xffffffff,3),(0x7fffffff,0xffff0001)]for mode in [0,0x2000]for ccr in range(32)for d2 in [0,0x80000000,0xffffffff]]
  cases=list(dict.fromkeys(base+matrix));rows=[];state.update(status='checking_native_math',binary_bytes=len(code),compile_command=command);checkpoint()
  for original_entry,name in names.items():
   selected=[x for x in cases if original_entry==0xe540 or x[1]]
   if args.limit:selected=selected[:args.limit]
   for i,(a,b,sr,d2,d1)in enumerate(selected):
    expected,oldfaults,oldsteps=r.run(original,original_entry,[(0xe540,0xe61c)],a,b,sr,d2,d1)
    actual,faults,steps=r.run(candidate,symbols[name],[(BASE,BASE+len(code))],a,b,sr,d2,d1)
    assert actual==expected,('ABI',hex(original_entry),i,hex(a),hex(b),hex(sr),hex(d2),expected,actual)
    assert not faults and not oldfaults
    rows.append(dict(entry=hex(original_entry),a=a,b=b,SR=sr,D2=d2,D1=d1,original_steps=oldsteps,compiled_steps=steps,matched=True))
    if i%256==0:state.update(current_entry=hex(original_entry),completed_normal_cases=len(rows));checkpoint();print('math',hex(original_entry),i,'/',len(selected),flush=True)
  save(out/'normal-cases.json',rows);zero_rows=[]
  for original_entry in [0xe588,0xe60a]:
   zeros=[(a,mode|ccr,[0,0x80000000,0xffffffff][ccr%3],0xdeadbeef)for a in [0,1,0x80000000,0xffffffff]for mode in [0,0x2000]for ccr in range(32)]
   if args.limit:zeros=zeros[:args.limit]
   for i,(a,sr,d2,d1)in enumerate(zeros):
    expected,oldfaults,_=r.run(original,original_entry,[(0xe540,0xe61c)],a,0,sr,d2,d1)
    actual,faults,_=r.run(candidate,symbols[names[original_entry]],[(BASE,BASE+len(code))],a,0,sr,d2,d1)
    assert actual==expected,('zero return ABI',hex(original_entry),i,expected,actual)
    assert len(faults)==len(oldfaults)==1
    ref=oldfaults[0].copy();new=faults[0].copy();refpc=ref.pop('frame_PC');newpc=new.pop('frame_PC');assert ref==new,('zero trap state',ref,new)
    delta=refpc-0xe606;assert delta in [0,2]and newpc==symbols['biwn_native_division_fault']+delta,('relocated fault',hex(refpc),hex(newpc),symbols)
    zero_rows.append(dict(entry=hex(original_entry),numerator=a,SR=sr,D2=d2,full_return_CPU_match=True,trap_registers_frame_SR_match=True,original_saved_fault_PC=refpc,native_saved_fault_PC=newpc,saved_PC_relocation_delta=delta))
   print('zero exception',hex(original_entry),len(zeros),flush=True)
  save(out/'zero-exception-cases.json',zero_rows);r.n.close()
  if args.limit:state.update(status='terminal_native_math_preflight_pass',normal_cases=len(rows),zero_exception_cases=len(zero_rows));checkpoint();print(state['status'],flush=True);return
  paths=[native/name for name in ['Makefile','Makefile.movable','Makefile.math','math.ld','math-results.c','math-shims.S','button-digit-movable-shim.S']]+[native.parent/name for name in ['biwn_camera.c','biwn_signed_division.c','biwn_inventory_select.c']]+[Path(__file__)]
  libgcc=ROOT/'tools/m68k-elf/m68000-soft/libgcc.a';core=ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib';device=ROOT/'tools/libbiwn-movement-device.dylib'
  state.update(status='terminal_native_arithmetic_full_ABI_and_zero_exception_pass',normal_cases=len(rows),zero_exception_cases=len(zero_rows),entry_case_counts={hex(entry):sum(row['entry']==hex(entry)for row in rows)for entry in names},all16registers_PC_SR_and_stack_banks_match=True,zero_divisor_new_native_exception=True,no_original_arithmetic_instructions_on_candidate=True,no_nonprivate_final_RAM_changes=True,compiled_binary=str(binary),compiled_binary_sha256=sha(binary),compiled_ELF=str(elf),compiled_ELF_sha256=sha(elf),symbols=symbols,source_sha256={str(p):sha(p)for p in paths},execution_dependencies_sha256={str(p):sha(p)for p in [libgcc,core,device]},scope='Compiled recovered C multiplication/division plus coordinator flag/ABI glue. Three original entry contracts include quotient, remainder, multiply,D1,A0/A1,CCR,both modes and stack banks. New native zero path executes DIVU processor exception; declared inert RTE test handler returns.512zero cases compare trap/return registers and savedSR, with expected faultPC relocation. Nativecode is not yet installed into a disc or game frames; arbitrary handler mutation, full aliasing, interrupt timing and physical console remain unproved.')
  checkpoint();save(ROOT/'verification/native-math-current.json',state);print(json.dumps({k:state[k]for k in ['status','binary_bytes','normal_cases','zero_exception_cases']}),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise
if __name__=='__main__':main()
