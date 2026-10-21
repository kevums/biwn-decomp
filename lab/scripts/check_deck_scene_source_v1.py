"""Original 68000 vs two complete structured Deck callers with ABI fixtures."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_deck_coordinate_source_v1 as coordinate
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
ROOT=coordinate.ROOT;SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-scene-source'
CPU=coordinate.CPU;Bus=coordinate.Bus;SERVICE=coordinate.SERVICE;SP=coordinate.SP;STOP=coordinate.STOP
ROOTS={0x11828:0x1186a,0x11ad4:0x11b4c}
HELPERS={0x11b4c,0x1186a,0x11d1a,0x10968,0x11384,0x10ba4,0x1142e,0x10734}
save=coordinate.save;sha=coordinate.sha;cpu_dict=coordinate.cpu_dict
class Engine(coordinate.Engine):
 def helper(self,memory,state,target,case,number):
  assert target in HELPERS
  # Declared callee ABI: preserve D2-D7/A2-A7, vary all four caller-saved
  # registers and CCR. No instruction in a dependency is claimed recovered.
  for n in [0,1,8,9]:state.registers[n]=(target*0x10203+number*0x1234567+case['variant']*71+n*0x123abcd)&0xffffffff
  state.sr=(state.sr&0xffe0)|((case['variant']+number*13)&31);state.pc=target+2
  a=0x70000+number*4;memory[a:a+4]=((target<<8|number)&0xffffffff).to_bytes(4,'big')
  if target==0x11b4c:
   value=[0,1,0xffffffff,0x7fffffff,0x80000000][(case['variant']+number)%5]
   memory[0x40104:0x40108]=value.to_bytes(4,'big')
  if case['mutate_later_tag']and number==0:
   memory[0x400ea+8*46:0x400ec+8*46]=b'\0\1'
 def original(self,ram,initial,case):
  self.native.device.seed(ram,0);self.set_cpu(initial,True);covered=set();entries=[]
  for _ in range(10000):
   s=self.cpu();pc=s.pc
   if pc==STOP:break
   if pc in HELPERS:
    memory=bytearray(self.native.device.ram());entries.append(self.entry(memory,s));self.helper(memory,s,pc,case,len(entries)-1)
    self.native.device.seed(bytes(memory),0);s.pc=int.from_bytes(memory[s.registers[15]:s.registers[15]+4],'big');s.registers[15]+=4
    if s.sr&0x2000:s.ssp=s.registers[15]
    else:s.usp=s.registers[15]
    self.set_cpu(s);continue
   assert initial.pc<=pc<ROOTS[initial.pc],hex(pc)
   covered.add(pc);self.core.m68k_execute(1)
  else:raise AssertionError('original caller bound')
  return self.native.device.ram(),self.cpu(),entries,covered
 def translated(self,fn,ram,initial,case,fail=None,budget=128,service_fault=None):
  memory=bytearray(ram);entries=[];events=[];errors=[]
  def read(w):
   def callback(_,a,out):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['bad_read',a,w]);return 1
    out[0]=int.from_bytes(memory[a:a+w],'big');events.append(['r',a,w,out[0]]);return 0
   return callback
  def write(w):
   def callback(_,a,v):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['bad_write',a,w]);return 1
    memory[a:a+w]=v.to_bytes(w,'big');events.append(['w',a,w,v]);return 0
   return callback
  def service(_,bus,pointer,target):
   try:
    state=pointer.contents;entries.append(self.entry(memory,state))
    if service_fault=='error':return 1
    self.helper(memory,state,target,case,len(entries)-1)
    if service_fault=='stack':state.registers[15]+=4
    if service_fault=='return':memory[state.registers[15]:state.registers[15]+4]=bytes(4)
    return 0
   except Exception as e:errors.append(repr(e));return 1
  w=coordinate.scheduler.cleanup.world
  callbacks=[w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),SERVICE(service)]
  bus=Bus(w.R8(),*callbacks[:4],w.CALL(),None,0);state=CPU.from_buffer_copy(bytes(initial))
  status=fn(c.byref(bus),c.byref(state),callbacks[4],None,budget)
  return status,bytes(memory),state,entries,events,errors
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1182811ad4);cases=[]
 for root in ROOTS:
  for i in range(256):
   state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];state.pc=root;state.sr=(0x2000 if i&1 else 0)|((i//2)%32)|((i//64)<<8)
   state.usp=0x1d8000 if i&1 else SP;state.ssp=SP if i&1 else 0x1ff000
   ram=bytearray(baseline);ram[SP-256:SP+32]=rng.randbytes(288);ram[SP:SP+4]=STOP.to_bytes(4,'big')
   def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
   mask=[0,0xffff,0x5555,1<<(i//4%16)][i%4]
   for slot in range(16):put(0x400ea+46*slot,2,1 if mask&(1<<slot)else[0,2,0xffff][(i+slot)%3])
   for n,a in enumerate([0x40100,0x400f8,0x400fc]):
    angle=((i>>(2*n))&3)*64-32
    # All64 rounded orientations plus exact low-word/32bit wrap inputs.
    put(a,4,angle+(0xffffff00 if i&64 else 0))
   for slot in range(64):put(0x3d7a2+slot*2,2,(slot*991+i*17)&65535)
   cases.append((bytes(ram),state,dict(root=root,variant=i,active_mask=mask,mutate_later_tag=i%7==0)))
 return cases
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=SRC/'deck-scene-source.c');ap.add_argument('--output',type=Path);args=ap.parse_args()
 out=args.output or ROOT/'verification/deck-scene-source'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True,exist_ok=True);print(out,flush=True)
 state=dict(status='compiling',pid=os.getpid(),directory=str(out),source=str(args.source),whole_game_complete=False,new_training=False,authorship='Coordinator recovered structured C; helper implementations are separate dependencies.')
 def mark():save(out/'protocol.json',state)
 mark();library=out/'libdeck-scene.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(args.source),'-o',str(library)]
 try:
  p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  fn=c.CDLL(str(library)).biwn_deck_scene_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int
  engine=Engine();selected=[x for x in fixtures()if not args.limit or x[2]['variant']<args.limit];rows=[];coverage=set()
  try:
   for i,(ram,initial,case)in enumerate(selected):
    expected,cpu,entries,covered=engine.original(ram,initial,case);status,actual,got,observed,events,errors=engine.translated(fn,ram,initial,case)
    if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(j),a,b]for j,(a,b)in enumerate(zip(expected,actual))if a!=b][:32]));raise AssertionError(out/'counterexample.json')
    coverage|=covered;rows.append(dict(case=case,CPU=cpu_dict(cpu),RAM=sha(expected),helper_entries=len(entries),C_events=len(events),full_CPU_RAM_helper_entry_match=True))
    if i%64==0:state.update(status='checking',completed=i+1,total=len(selected));mark();print('case',i+1,'/',len(selected),flush=True)
   guards=[]
   if not args.limit:
    for root in ROOTS:
     ram,initial,case=next(x for x in selected if x[1].pc==root and x[2]['variant']==1)
     status,_,_,_,events,_=engine.translated(fn,ram,initial,case);assert status==0
     for fail in range(len(events)):
      status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,fail=fail);assert status==2 and not errors and cpu_dict(got)==cpu_dict(initial),(hex(root),fail,status);guards.append(dict(root=hex(root),data_failure=fail))
     for fault,expect in [('error',3),('stack',5),('return',5)]:
      status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,service_fault=fault);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(root=hex(root),service_fault=fault))
     for budget,expect in [(0,1),(1,4)]:
      status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,budget=budget);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(root=hex(root),helper_budget=budget))
  finally:engine.native.close()
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);addresses={x.address for a,b in ROOTS.items()for x in decoder.disasm(baseline[a:b],a)}
  assert args.limit or coverage==addresses,sorted(addresses-coverage)
  save(out/'cases.json',rows);save(out/'guards.json',guards)
  core=ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib';device=ROOT/'tools/libbiwn-movement-device.dylib'
  sources=[args.source,SRC/'deck-scene-contract.h',SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h',Path(__file__),Path(coordinate.__file__)]
  state.update(status='terminal_preflight_pass'if args.limit else'terminal_two_readable_Deck_scene_callers_native_match',completed=len(rows),instruction_locations=[len(coverage),len(addresses)],host_error_cases=len(guards),entries={hex(a):sum(x['case']['root']==a for x in rows)for a in ROOTS},source_sha256={str(p.resolve()):sha(p.read_bytes())for p in sources},native_dependencies_sha256={str(p):sha(p.read_bytes())for p in [core,device,ROOT/'render-assets/biwn-inventory-baseline.bin']},scope='Two complete caller bodies inclRTS,finitefixtures,bothstackbanks/all32CCR,16recordscan,positive/zero/negativeupdatevalues,64orientationindicesandanglewrap,calleeclobbersandRAMmutation. FullCPU/2MBRAM/privateframesandcalleeentryCPU/RAMmatch. Allhelperbodies declaredfixtures; notGPU/device/IRQ/timing/naturalgameplay/fullgamerecovery.');mark()
  if not args.limit:save(ROOT/'verification/Deck-scene-source-current.json',state)
  print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
