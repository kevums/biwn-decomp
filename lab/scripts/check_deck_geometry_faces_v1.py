"""Complete1142Eface builder vs original68000;E26C is an explicit GPU fixture."""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;CPU=h.CPU;Bus=h.Bus;SERVICE=h.SERVICE;SP=h.SP;STOP=h.STOP;save=h.save;sha=h.sha;cpu_dict=h.cpu_dict
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-geometry-faces-v1'
class Engine(h.Engine):
 def effect(self,memory,state,case,number):
  v=case['variant'];sp=state.registers[15];assert int.from_bytes(memory[sp+20:sp+22],'big')==0
  for n in [0,1,8,9]:state.registers[n]=(0x91ab1237*(n+1)+v*71+number*137)&0xffffffff
  state.sr=(state.sr&0xffe0)|((v*13+number*7)&31)
  def put(a,w,value):memory[a:a+w]=(value&((1<<(8*w))-1)).to_bytes(w,'big')
  put(0x70000+number*4,4,0xe26c0000|v<<8|number)
  if case['mutate_counter']:put(0x49b88,4,[0,1,7,0x4000000,0xffffffff][(v+number)%5])
  if case['flip_descriptor']and number==0:put(0x400e6,4,0x90000)
  for n in range(3):put(0x49b8c+n*2,2,[0,1,0x7fff,0x8000,0xffff][(v+n+number)%5])
  for n in range(12):put(0x3d75a+n*2,2,(v*997+number*71+n*317)&65535)
  state.pc=0xe2b6
 def original(self,ram,initial,case):
  self.native.device.seed(ram,0);self.set_cpu(initial,True);entries=[];seen=set()
  for steps in range(20000):
   state=self.cpu();pc=state.pc
   if pc==STOP:break
   if pc==0xe26c:
    memory=bytearray(self.native.device.ram());entries.append(self.entry(memory,state));self.effect(memory,state,case,len(entries)-1)
    self.native.device.seed(bytes(memory),0);state.pc=int.from_bytes(memory[state.registers[15]:state.registers[15]+4],'big');state.registers[15]+=4
    if state.sr&0x2000:state.ssp=state.registers[15]
    else:state.usp=state.registers[15]
    self.set_cpu(state);continue
   assert 0x1142e<=pc<0x114c0 or 0x114cc<=pc<0x11762,hex(pc);seen.add(pc);self.core.m68k_execute(1)
  else:raise AssertionError(('original face work bound',case))
  return self.native.device.ram(),self.cpu(),entries,seen,steps
 def translated(self,fn,ram,initial,case,fail=None,service_fault=None,iteration_budget=64,helper_budget=64):
  memory=bytearray(ram);events=[];errors=[];entries=[]
  def reader(w):
   def cb(_,a,out):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['read',a,w]);return 1
    out[0]=int.from_bytes(memory[a:a+w],'big');events.append(['r',a,w]);return 0
   return cb
  def writer(w):
   def cb(_,a,value):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['write',a,w]);return 1
    memory[a:a+w]=(value&((1<<(8*w))-1)).to_bytes(w,'big');events.append(['w',a,w]);return 0
   return cb
  def service(_,bus,pointer,target):
   try:
    assert target==0xe26c;state=pointer.contents;entries.append(self.entry(memory,state))
    if service_fault=='error':return 1
    self.effect(memory,state,case,len(entries)-1)
    if service_fault=='stack':state.registers[15]+=4
    if service_fault=='return':memory[state.registers[15]:state.registers[15]+4]=bytes(4)
    return 0
   except BaseException as e:errors.append(repr(e));return 1
  w=h.base.scheduler.cleanup.world;callbacks=[w.R16(reader(2)),w.R32(reader(4)),w.W16(writer(2)),w.W32(writer(4)),SERVICE(service)]
  bus=Bus(w.R8(),*callbacks[:4],w.CALL(),None,0);state=CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(state),callbacks[4],None,helper_budget,iteration_budget)
  return status,bytes(memory),state,entries,events,errors
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1142e11762)
 for count in [0,1,2,6,8]:
  for i in range(128):
   memory=bytearray(baseline);state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];state.pc=0x1142e;state.sr=(0x2000 if i&1 else 0)|((i//2)%32)|(0x100 if i>=64 else 0);state.usp=0x1d8000 if i&1 else SP;state.ssp=SP if i&1 else 0x1ff000
   def put(a,w,value):memory[a:a+w]=(value&((1<<(8*w))-1)).to_bytes(w,'big')
   memory[SP-256:SP+64]=rng.randbytes(320);put(SP,4,STOP)
   for descriptor in [0x80000,0x90000]:
    index=[0,1,7,63][(i//8)%4];put(descriptor,2,index)
    for n in range(16):put(0x400c4+index*32+n*2,2,[0,1,0x7fff,0x8000,0xffff,0xfffe][(i+n)%6])
    for f in range(8):
     put(descriptor+0x10+f*20,2,[0,1,2,3,4,5,6,0xffff][(i+f)%8]);texture=[0,1,7,0x8000,0xffff][(i+f)%5];put(descriptor+0x14+f*20,2,texture);put(0x3d772+texture*8,4,rng.getrandbits(32))
    put(descriptor+0x88,2,count if descriptor==0x80000 else [0,1,3,6,8][(i//3)%5])
   put(0x400e6,4,0x80000);put(0x49b88,4,[0,1,7,0xffffffff,0x4000000][i%5])
   for n in range(36):put(0x3d6ca+n*4,4,[0,1,0x7fffffff,0x80000000,0xffffffff,0x7ffffffe][(i+n)%6])
   for n in range(12):put(0x3d75a+n*2,2,rng.getrandbits(16))
   assert len(memory)==0x200000
   yield bytes(memory),state,dict(count=count,variant=i,mutate_counter=i%2==0,flip_descriptor=i%3==0)
def compile_source(source,out,name):
 lib=out/(name+'.dylib');p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(source),str(SRC/'faces-adapter.c'),'-o',str(lib)],capture_output=True,text=True);(out/(name+'-compiler.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(lib)).biwn_geometry_faces_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int;return fn,lib
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=SRC/'coordinator-reference.c');args=ap.parse_args()
 out=ROOT/'verification/deck-geometry-faces-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);s=dict(status='compiling',directory=str(out),pid=os.getpid(),whole_game_complete=False,new_training=False,native_disc_changed=False)
 def mark():save(out/'protocol.json',s);save(ROOT/'verification/deck-geometry-faces-v1-current.json',s)
 mark()
 try:
  fn,lib=compile_source(args.source,out,'faces');e=Engine();rows=[];covered=set();samples={};guards=[]
  try:
   for ram,initial,case in fixtures():
    if args.limit and case['variant']>=args.limit:continue
    expected,cpu,entries,seen,steps=e.original(ram,initial,case);status,actual,got,observed,events,errors=e.translated(fn,ram,initial,case)
    if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:40]));raise AssertionError(out/'counterexample.json')
    covered|=seen;rows.append(dict(case=case,original_steps=steps,GPU_calls=len(entries),full_CPU_RAM_entries_match=True))
    if case['variant']==1 and case['count']in[0,1,2]:samples[case['count']]=(ram,initial,case,events)
    if len(rows)%32==0:s.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
   if not args.limit:
    for count,(ram,initial,case,events)in samples.items():
     for index in range(len(events)):
      status,_,cpu,_,_,errors=e.translated(fn,ram,initial,case,fail=index);assert status==2 and not errors and cpu_dict(cpu)==cpu_dict(initial),(count,index,status);guards.append(dict(count=count,bus_failure=index))
    ram,initial,case,_=samples[2]
    for fault,want in [('error',3),('stack',5),('return',5)]:
     status,_,cpu,_,_,errors=e.translated(fn,ram,initial,case,service_fault=fault);assert status==want and not errors and cpu_dict(cpu)==cpu_dict(initial);guards.append(dict(service_fault=fault))
    for budgets in [dict(iteration_budget=0),dict(iteration_budget=1),dict(helper_budget=1)]:
     status,_,cpu,_,_,errors=e.translated(fn,ram,initial,case,**budgets);assert status==4 and not errors and cpu_dict(cpu)==cpu_dict(initial);guards.append(budgets)
  finally:e.native.close()
  b=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();d=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);addresses={x.address for a,z in[(0x1142e,0x114c0),(0x114cc,0x11762)]for x in d.disasm(b[a:z],a)};assert args.limit or covered==addresses,[hex(a)for a in addresses-covered]
  save(out/'cases.json',rows);save(out/'guards.json',guards);paths=[Path(__file__),args.source,SRC/'faces-contract.h',SRC/'faces-adapter.c',Path(h.__file__),out/'cases.json',out/'guards.json',lib]
  s.update(status='terminal_faces_preflight_pass'if args.limit else'terminal_complete_geometry_faces_CPU_RAM_match',completed=len(rows),instruction_locations=[len(covered),len(addresses)],host_error_cases=len(guards),GPU_fixture_calls=sum(x['GPU_calls']for x in rows),source=str(args.source),source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' FullCPU/banks,2MBRAM and ordered GPU entry snapshots. Counts0,1,2,6,8,partial registers,wraps,arithmetic averages,invalid face selectors,texture extremes and helper mutations. E26Cdevice/firmware body,timing,MMIO,IRQ,native relocation and full-game fidelity are not established here.');mark();print(s['status'],len(rows),s['instruction_locations'],flush=True)
 except BaseException as error:s.update(status='terminal_faces_checker_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
