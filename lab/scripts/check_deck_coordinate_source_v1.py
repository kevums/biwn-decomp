"""Native 68000 vs readable C for complete Deck/C-Space caller 11D1A.

E26C is an explicit result fixture; E540 executes its original CPU body on
both lanes. Finite component proof, not natural gameplay or GPU integration.
"""
import argparse,ctypes as c,hashlib,json,os,random,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_scheduler as scheduler
ROOT=scheduler.ROOT;CPU=scheduler.CPU;Bus=scheduler.cleanup.world.Bus
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-coordinate-update'
SP=0x1e8000;STOP=0x192000
SERVICE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(Bus),c.POINTER(CPU),c.c_uint32)
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def cpu_dict(s):return scheduler.cpu_dict(s)
class Engine:
 def __init__(self):self.native=scheduler.Native();self.core=self.native.lib
 def set_cpu(self,s,reset=False):
  l=self.core
  if reset:l.m68k_pulse_reset();l.m68k_set_irq(0)
  l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,s.ssp)
  l.m68k_set_reg(17,0);l.m68k_set_reg(15,s.usp);l.m68k_set_reg(17,s.sr)
  for i,v in enumerate(s.registers):l.m68k_set_reg(i,v)
  l.m68k_set_reg(16,s.pc)
 def cpu(self):
  l=self.core;s=CPU();s.registers[:]=[l.m68k_get_reg(None,i)for i in range(16)]
  s.pc=l.m68k_get_reg(None,16);s.sr=l.m68k_get_reg(None,17)
  s.usp=self.native.prefix[16]if s.sr&0x2000 else s.registers[15]
  s.ssp=s.registers[15]if s.sr&0x2000 else self.native.prefix[17];return s
 def gpu_fixture(self,memory,state,case):
  sp=state.registers[15];args=[int.from_bytes(memory[sp+4+4*i:sp+8+4*i],'big')for i in range(5)]
  assert args[0]==0x47b88
  for a,w,v in case['gpu_effects']:memory[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
  state.sr=(state.sr&0xfff0)|4;state.pc=0xe2b6
 def entry(self,memory,state):
  sp=state.registers[15]
  return dict(CPU=cpu_dict(state),RAM=sha(memory),arguments=bytes(memory[sp+4:sp+24]).hex())
 def original(self,ram,initial,case):
  self.native.device.seed(ram,0);self.set_cpu(initial,True);coverage=set();entries=[];steps=0
  for _ in range(2000):
   s=self.cpu();pc=s.pc
   if pc==STOP:break
   if pc in [0xe26c,0xe540]:entries.append(self.entry(self.native.device.ram(),s))
   if pc==0xe26c:
    memory=bytearray(self.native.device.ram());self.gpu_fixture(memory,s,case)
    self.native.device.seed(bytes(memory),0)
    s.pc=int.from_bytes(memory[s.registers[15]:s.registers[15]+4],'big');s.registers[15]+=4
    if s.sr&0x2000:s.ssp=s.registers[15]
    else:s.usp=s.registers[15]
    self.set_cpu(s);continue
   assert 0x11d1a<=pc<0x11e64 or 0xe540<=pc<0xe588,hex(pc)
   if 0x11d1a<=pc<0x11e64:coverage.add(pc)
   self.core.m68k_execute(1);steps+=1
  else:raise AssertionError('original work bound')
  assert len(entries)==4
  return self.native.device.ram(),self.cpu(),entries,coverage,steps
 def math_body(self,memory,state):
  self.native.device.seed(bytes(memory),0);self.set_cpu(state,True)
  for _ in range(100):
   pc=self.core.m68k_get_reg(None,16)
   if pc==0xe586:break
   assert 0xe540<=pc<0xe588,hex(pc);self.core.m68k_execute(1)
  else:raise AssertionError('math body bound')
  memory[:]=self.native.device.ram();c.memmove(c.byref(state),c.byref(self.cpu()),c.sizeof(CPU))
 def translated(self,fn,ram,initial,case,fail=None,budget=4,bad_return=False):
  memory=bytearray(ram);entries=[];events=[];errors=[]
  def read(w):
   def cb(_,a,out):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['bad_read',a,w]);return 1
    out[0]=int.from_bytes(memory[a:a+w],'big');events.append(['r',a,w,out[0]]);return 0
   return cb
  def write(w):
   def cb(_,a,v):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['bad_write',a,w]);return 1
    memory[a:a+w]=v.to_bytes(w,'big');events.append(['w',a,w,v]);return 0
   return cb
  def service(_,bus,state,target):
   try:
    s=state.contents;entries.append(self.entry(memory,s))
    if target==0xe26c:self.gpu_fixture(memory,s,case)
    elif target==0xe540:self.math_body(memory,s)
    else:raise AssertionError(hex(target))
    if bad_return:memory[s.registers[15]:s.registers[15]+4]=bytes(4)
    return 0
   except Exception as e:errors.append(repr(e));return 1
  w=scheduler.cleanup.world;callbacks=[w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),SERVICE(service)]
  bus=Bus(w.R8(),*callbacks[:4],w.CALL(),None,0);s=CPU.from_buffer_copy(bytes(initial))
  status=fn(c.byref(bus),c.byref(s),callbacks[4],None,budget)
  return status,bytes(memory),s,entries,events,errors
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x11d1a)
 rows=[];extremes=[0,1,0x7fff,0x8000,0xffff,0x7fffffff,0x80000000,0xffffffff]
 for i in range(576):
  sr=(0x2000 if i&1 else 0)|((i//2)%32)|(((i//64)%8)<<8)
  s=CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP]
  s.pc=0x11d1a;s.sr=sr;s.usp=0x1d8000 if sr&0x2000 else SP;s.ssp=SP if sr&0x2000 else 0x1ff000
  mem=bytearray(baseline);mem[SP-256:SP+32]=rng.randbytes(288);mem[SP:SP+4]=STOP.to_bytes(4,'big')
  def put(a,w,v):mem[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
  descriptor=0x80000;index=(i//8)%16
  put(0x400e6,4,descriptor);put(descriptor,2,index)
  for n,a in enumerate([0x400f8,0x400fc,0x40100,0x40402,0x40406,0x4040a,0x40104]):
   put(a,4,extremes[(i+n)%len(extremes)]if i<128 else rng.getrandbits(32))
  for a in [0x400ec,0x400f0,0x400f4,descriptor+4,descriptor+8,descriptor+12]:
   put(a,4,rng.getrandbits(32))
  # Far/near/equal threshold paths plus mixed unsigned-wrap results.
  threshold=[0,1,0xffffffff,0x80000000,0x7fffffff][i%5]
  put(0x400c4+(index<<5)+0x1c,4,threshold)
  effects=[[0x47b9a+n*2,2,extremes[(i+n*3)%8]]for n in range(3)]
  if i%9==0:
   descriptor=0x90000;put(descriptor,2,index);effects.append([0x400e6,4,descriptor])
   for a in [descriptor+4,descriptor+8,descriptor+12]:put(a,4,rng.getrandbits(32))
  if i%11==0:effects.append([0x40104,4,rng.getrandbits(32)])
  rows.append((bytes(mem),s,dict(index=i,gpu_effects=effects,threshold=threshold)))
 return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=args.output;out.mkdir(parents=True,exist_ok=True);print(out,flush=True)
 state=dict(status='compiling',pid=os.getpid(),source=str(args.source),source_sha256=sha(args.source.read_bytes()),whole_game_complete=False)
 def mark():save(out/'protocol.json',state)
 mark();library=out/'libdeck-coordinate.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(args.source),str(SRC/'deck-coordinate-adapter.c'),'-o',str(library)]
 try:
  p=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr)
  state['compiler_exit_code']=p.returncode;assert p.returncode==0,p.stderr
  lib=c.CDLL(str(library));fn=lib.biwn_deck_coordinate_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int
  engine=Engine();vectors=fixtures();selected=vectors[:args.limit]if args.limit else vectors;rows=[];covered=set()
  try:
   for i,(ram,initial,case)in enumerate(selected):
    expected,cpu,entries,coverage,steps=engine.original(ram,initial,case)
    status,actual,got,observed,events,errors=engine.translated(fn,ram,initial,case)
    ok=not status and not errors and actual==expected and cpu_dict(got)==cpu_dict(cpu)and entries==observed
    if not ok:
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,initial_CPU=cpu_dict(initial),original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(j),a,b]for j,(a,b)in enumerate(zip(expected,actual))if a!=b][:64],C_events=events))
     state.update(status='terminal_component_rejected',completed=i,counterexample=str(out/'counterexample.json'));mark();return 1
    covered|=coverage;rows.append(dict(case=i,CPU=cpu_dict(cpu),RAM=sha(expected),helper_entries=entries,original_instructions=steps,C_data_events=len(events)))
    if i%64==0:state.update(status='checking',completed=i+1,total=len(selected));mark();print('case',i+1,'/',len(selected),flush=True)
   guards=[]
   if not args.limit:
    ram,initial,case=vectors[0];status,_,_,_,events,_=engine.translated(fn,ram,initial,case);assert status==0
    for failure in range(len(events)):
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,fail=failure)
     assert status==2 and cpu_dict(got)==cpu_dict(initial)and not errors,('failure',failure,status)
     guards.append(dict(data_failure=failure,status=status))
    for budget in [0,1,2,3]:
     status,_,got,_,_,_=engine.translated(fn,ram,initial,case,budget=budget)
     assert status==(1 if budget==0 else 4)and cpu_dict(got)==cpu_dict(initial)
     guards.append(dict(helper_budget=budget,status=status))
    status,_,got,_,_,_=engine.translated(fn,ram,initial,case,bad_return=True)
    assert status==5 and cpu_dict(got)==cpu_dict(initial);guards.append(dict(bad_return=True,status=status))
  finally:engine.native.close()
  from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(baseline[0x11d1a:0x11e64],0x11d1a));addresses={x.address for x in decoded}
  assert args.limit or covered==addresses,sorted(addresses-covered)
  save(out/'cases.json',rows);save(out/'guards.json',guards)
  state.update(status='terminal_component_preflight_pass'if args.limit else'terminal_readable_Deck_coordinate_full_CPU_component_pass',completed=len(rows),instruction_coverage=[len(covered),len(addresses)],host_error_cases=len(guards),all_2MB_RAM_and_full_CPU_match=True,helper_entry_full_CPU_and_RAM_match=True,helper_dependencies={'E26C':'Declared result fixture,not real GPU execution','E540':'Original native CPU body on both paths;not new source recovery'},source_bindings={str(p):sha(p.read_bytes())for p in [args.source,SRC/'deck-coordinate-contract.h',SRC/'deck-coordinate-adapter.c',Path(__file__)]},scope='Complete11D1A..11E64 structured C caller compared to original pinnedCPU in576finitecases. Bothbanks,all32CCR,signedwordGPUresults,anglewrap,unsignedboundaries and declaredcalleeRAMmutations. Original full16regs/SR/PC/USP/SSP,complete2MBRAM includingprivateframes,andfourhelperentryCPU/RAMsnapshots match. No orderedbus/IRQ/timing/physicalhardware/naturalgameplay/fullGPUclaim. Hosterror contracts separately checked.');mark();print(state['status'],flush=True);return 0
 except BaseException as e:state.update(status='terminal_checker_failed',error=repr(e));mark();raise
if __name__=='__main__':sys.exit(main())
