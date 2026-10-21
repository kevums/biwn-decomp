"""10734 full CPU/RAM against original68000 with actual pinned blitter MMIO.

Formatter/text bodies are explicit fixtures. They do not supply blitter pixels.
An independent Unicorn lane checks ordered public RAM/MMIO accesses and calls.
"""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;CPU=h.CPU;Bus=h.Bus;SERVICE=h.SERVICE;SP=h.SP;STOP=h.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-debug-overlay-v1'
save=h.save;sha=h.sha;cpu_dict=h.cpu_dict
WIDTHS={0x1b45a:[4,4,4],0x149ae:[2,2,4,4,4,4,2,2]}
REGS=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
class Engine(h.Engine):
 def arguments(self,state,target):
  at=state.registers[15]+4;values=[]
  for width in WIDTHS[target]:values.append(self.native.device.read(at,width));at+=width
  return values
 def effect(self,state,target,case,index):
  args=self.arguments(state,target);device=self.native.device
  if target==0x1b45a:
   scratch=args[0];text=('fixture-'+str(index)+'-'+str(case['variant'])).encode()+b'\0'
   for n,value in enumerate(text):device.direct(scratch+n,1,value)
  else:device.direct(0x70000+index*4,4,0x149ae000|index)
  for reg in [0,1,8,9]:state.registers[reg]=(0xa17b2931*(reg+1)+case['variant']*71+index*997)&0xffffffff
  state.sr=(state.sr&0xffe0)|((case['variant']*11+index*7)&31)
  if case['mutate_globals']:
   if index==0:device.direct(0x400f0,4,0x80000001)
   if index==9:device.direct(0x403d0,2,0x8001)
   if index==11:device.direct(0x403ca,2,0xffff)
   device.direct(0x403cc,2,0)
  state.pc=0x1b476 if target==0x1b45a else 0x14ca8
 def original(self,ram,initial,case):
  device=self.native.device;device.seed(ram,0);self.set_cpu(initial,True);entries=[];seen=set()
  for steps in range(1000):
   state=self.cpu();pc=state.pc
   if pc==STOP:break
   if pc in WIDTHS:
    entries.append(self.entry(device.ram(),state));self.effect(state,pc,case,len(entries)-1)
    state.pc=device.read(state.registers[15],4);state.registers[15]+=4
    if state.sr&0x2000:state.ssp=state.registers[15]
    else:state.usp=state.registers[15]
    self.set_cpu(state);continue
   assert 0x10734<=pc<0x10968,hex(pc);seen.add(pc);self.core.m68k_execute(1)
  else:raise AssertionError('original debug work bound')
  return device.ram(),self.cpu(),entries,seen,device.registers(),steps
 def translated(self,fn,ram,initial,case,fail=None,service_fault=None,budget=16):
  device=self.native.device;device.seed(ram,0);events=[];errors=[];entries=[];public=[]
  def reader(width):
   def cb(_,a,out):
    if fail==len(events):return 1
    try:
     out[0]=device.read(a,width);events.append(['r',a,width,out[0]])
     if not SP-256<=a<SP+4:public.append(['r',a,width,out[0]])
     return 0
    except BaseException as error:errors.append(repr(error));return 1
   return cb
  def writer(width):
   def cb(_,a,value):
    if fail==len(events):return 1
    try:
     if width==2:device.write16(a,value)
     else:device.write(a,value)
     events.append(['w',a,width,value])
     if not SP-256<=a<SP+4:public.append(['w',a,width,value])
     return 0
    except BaseException as error:errors.append(repr(error));return 1
   return cb
  def service(_,bus,pointer,target):
   try:
    assert target in WIDTHS,hex(target);state=pointer.contents;entries.append(self.entry(device.ram(),state));public.append(['call',target,self.arguments(state,target)])
    if service_fault=='error':return 1
    self.effect(state,target,case,len(entries)-1)
    if service_fault=='stack':state.registers[15]+=4
    if service_fault=='return':device.direct(state.registers[15],4,0)
    return 0
   except BaseException as error:errors.append(repr(error));return 1
  w=h.base.scheduler.cleanup.world;callbacks=[w.R16(reader(2)),w.R32(reader(4)),w.W16(writer(2)),w.W32(writer(4)),SERVICE(service)]
  bus=Bus(w.R8(),*callbacks[:4],w.CALL(),None,0);state=CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(state),callbacks[4],None,budget)
  return status,device.ram(),state,entries,device.registers(),events,errors,public
 def ordered_original(self,ram,initial,case):
  device=self.native.device;device.seed(ram,0);u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_map(0xf02000,0x1000);u.mem_write(0,ram)
  u.reg_write(UC_M68K_REG_SR,initial.sr)
  for reg,value in zip(REGS,initial.registers):u.reg_write(reg,value)
  events=[];number=0
  def code(engine,pc,width,_):
   nonlocal number
   if pc in WIDTHS:
    state=CPU.from_buffer_copy(bytes(initial));state.registers[:]=[u.reg_read(reg)for reg in REGS];state.sr=u.reg_read(UC_M68K_REG_SR);state.pc=pc
    events.append(['call',pc,self.arguments(state,pc)]);self.effect(state,pc,case,number);number+=1;state.pc=device.read(state.registers[15],4);state.registers[15]+=4
    u.reg_write(UC_M68K_REG_SR,state.sr)
    for reg,value in zip(REGS,state.registers):u.reg_write(reg,value)
    u.reg_write(UC_M68K_REG_PC,state.pc);return
   assert 0x10734<=pc<0x10968,hex(pc)
  def read(engine,access,a,width,value,_):
   value=device.read(a,width);u.mem_write(a,value.to_bytes(width,'big'))
   if not SP-256<=a<SP+4:events.append(['r',a,width,value])
  def write(engine,access,a,width,value,_):
   value&=(1<<(width*8))-1
   if width==2:device.write16(a,value)
   else:assert width==4;device.write(a,value)
   if not SP-256<=a<SP+4:events.append(['w',a,width,value])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x10734,STOP,count=1000,timeout=3000000)
  assert u.reg_read(UC_M68K_REG_PC)==STOP
  return events
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1073410968)
 for i in range(256):
  memory=bytearray(baseline);state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];state.pc=0x10734;state.sr=(0x2000 if i&1 else 0)|((i//2)%32)|((i//64)<<8);state.usp=0x1d8000 if i&1 else SP;state.ssp=SP if i&1 else 0x1ff000
  memory[SP-256:SP+16]=rng.randbytes(272);memory[SP:SP+4]=STOP.to_bytes(4,'big');flag=[0,1,0x8000,0xffff][i//64];memory[0x403cc:0x403ce]=flag.to_bytes(2,'big')
  for n,a in enumerate([0x400ec,0x400f0,0x400f4,0x400fc,0x400f8,0x40100]):memory[a:a+4]=[0,1,0x7fffffff,0x80000000,0xffffffff,0x12345678][(i+n)%6].to_bytes(4,'big')
  for n,a in enumerate([0x403d0,0x403ca]):memory[a:a+2]=[0,1,2,31,0x7fff,0x8000,0xffff][(i+n)%7].to_bytes(2,'big')
  memory[0xb29d0:0xb5130]=bytes([0xa5])*(0xb5130-0xb29d0)
  yield bytes(memory),state,dict(variant=i,flag=flag,mutate_globals=i%3==0)
def compile_source(source,out,label):
 library=out/(label+'.dylib');p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(source),str(SRC/'debug-adapter.c'),'-o',str(library)],capture_output=True,text=True);(out/(label+'-compiler.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(library)).biwn_debug_overlay_cpu_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int;return fn,library
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=SRC/'coordinator-reference.c');args=ap.parse_args()
 out=ROOT/'verification/deck-debug-overlay-cpu-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);state=dict(status='compiling',directory=str(out),pid=os.getpid(),native_disc_changed=False,new_training=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/deck-debug-overlay-cpu-v1-current.json',state)
 mark()
 try:
  fn,library=compile_source(args.source,out,'debug');e=Engine();rows=[];coverage=set();samples={};guards=[]
  try:
   for ram,initial,case in fixtures():
    if args.limit and case['variant']%64>=args.limit:continue
    expected,cpu,entries,seen,hardware,steps=e.original(ram,initial,case);status,actual,got,observed,registers,events,errors,public=e.translated(fn,ram,initial,case)
    if status or errors or actual!=expected or cpu_dict(cpu)!=cpu_dict(got)or observed!=entries or hardware!=registers:
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,original_hardware=hardware,C_hardware=registers,RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:40]));raise AssertionError(out/'counterexample.json')
    assert actual[0xb29d0:0xb5130]==bytes(0xb5130-0xb29d0),'Actual blitter did not regenerate the poisoned buffer'
    original_trace=e.ordered_original(ram,initial,case);assert original_trace==public,(case,original_trace,public)
    coverage|=seen;rows.append(dict(case=case,CPU_RAM_hardware_entries_and_public_bus_match=True,helper_calls=len(entries),cleared_blitter_bytes=0xb5130-0xb29d0,original_instructions=steps))
    if case['variant']in [0,64]:samples[case['variant']]=(ram,initial,case,events)
    if len(rows)%32==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
   if not args.limit:
    for ram,initial,case,events in samples.values():
     for index in range(len(events)):
      status,_,got,_,_,_,errors,_=e.translated(fn,ram,initial,case,fail=index);assert status==2 and not errors and cpu_dict(got)==cpu_dict(initial),(case,index,status);guards.append(dict(variant=case['variant'],bus_failure=index))
    ram,initial,case,_=samples[64]
    for fault,want in [('error',3),('stack',5),('return',5)]:
     status,_,got,_,_,_,errors,_=e.translated(fn,ram,initial,case,service_fault=fault);assert status==want and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(service_fault=fault))
    for budget in [0,1,15]:
     status,_,got,_,_,_,errors,_=e.translated(fn,ram,initial,case,budget=budget);assert status==(1 if budget==0 else 4)and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(budget=budget))
  finally:e.native.close()
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();d=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);expected={x.address for x in d.disasm(baseline[0x10734:0x10968],0x10734)};assert args.limit or coverage==expected
  save(out/'cases.json',rows);save(out/'guards.json',guards);paths=[Path(__file__),args.source,SRC/'debug-contract.h',SRC/'debug-adapter.c',Path(h.__file__),out/'cases.json',out/'guards.json',library]
  state.update(status='terminal_debug_preflight_pass'if args.limit else'terminal_debug_full_CPU_RAM_real_blitter_public_order_match',completed=len(rows),instruction_locations=[len(coverage),len(expected)],host_error_cases=len(guards),formatter_text_fixture_calls=sum(x['helper_calls']for x in rows),regenerated_blitter_bytes_each_case=0xb5130-0xb29d0,source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' Both stack banks/allCCR for each debug flag group;private56byte frame and all RAM compared. Real MMIO/blitter clears10,080poisonedbytes;helperfixtures do not fill pixels. Full formatter/text bodies,timing,IRQ,native compiled integration and whole-game rebuilding remain unverified.');mark();print(state['status'],len(rows),flush=True)
 except BaseException as error:state.update(status='terminal_debug_checker_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
