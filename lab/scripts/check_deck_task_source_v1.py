"""Original 68000 vs structured outer Deck task and explicit dependency fixtures.

No native CPU helper body is claimed recovered here. Full 2MB RAM, CPU,
private frame and dependency-entry comparisons; genuine connected test separate.
"""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_deck_scene_source_v1 as scene
ROOT=scene.ROOT;CPU=scene.CPU;Bus=scene.Bus;SERVICE=scene.SERVICE;SP=scene.SP;STOP=scene.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-task-source'
HELPERS={0x10990,0x11828,0xe03a,0x10c6e,0x1102a,0x11ad4,0x16bf4,0x10e72,0x11d1a,0xe19e,0xe202,0xe098,0x17f14}
RETURNS=[0x11e8c,0x11ec4,0x11ed6,0x11edc,0x11ee4,0x11f12,0x11f1a,0x11f32,0x11f38,0x11f4a,0x11f50,0x11f58,0x11f5e,0x11f64,0x11f6a]
save=scene.save;sha=scene.sha;cpu_dict=scene.cpu_dict
class Engine(scene.coordinate.Engine):
 def helper(self,memory,state,target,case,number):
  assert target in HELPERS
  for n in [0,1,8,9]:state.registers[n]=(target*0x10203+number*0x1234567+case['variant']*71+n*0x123abcd)&0xffffffff
  state.sr=(state.sr&0xffe0)|((case['variant']+number*13)&31);state.pc=target+2
  a=0x70000+number*4;memory[a:a+4]=((target<<8|number)&0xffffffff).to_bytes(4,'big')
  def put(a,w,v):memory[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
  if target==0x11828:put(0x403d6,2,case['mode'])
  if target==0xe03a:put(0x40400,2,case['dirty'])
  if target==0x10c6e:
   put(0x403dc,4,case['variant']%8)
   if case['variant']%3==0:put(0x400e6,4,0x90000)
  if target==0x10990 and case.get('suspend'):
   # Explicit dependency suspension fixture with a live private frame and
   # outstanding original return address. No simulated scheduler progress.
   state.registers[15]-=12
   if state.sr&0x2000:state.ssp=state.registers[15]
   else:state.usp=state.registers[15]
   put(state.registers[15],4,0x1b0da);put(state.registers[15]+4,4,number)
   state.pc=case['suspend'];return 6
  return 0
 def original(self,ram,initial,case):
  self.native.device.seed(ram,0);self.set_cpu(initial,True);covered=set();entries=[]
  for step in range(2000):
   state=self.cpu();pc=state.pc
   if pc==STOP or(step and pc==0x11e86):return (0 if pc==STOP else 6),self.native.device.ram(),state,entries,covered
   if pc in HELPERS:
    memory=bytearray(self.native.device.ram());entries.append(self.entry(memory,state));status=self.helper(memory,state,pc,case,len(entries)-1)
    self.native.device.seed(bytes(memory),0)
    if status==6:self.set_cpu(state);return 6,bytes(memory),state,entries,covered
    state.pc=int.from_bytes(memory[state.registers[15]:state.registers[15]+4],'big');state.registers[15]+=4
    if state.sr&0x2000:state.ssp=state.registers[15]
    else:state.usp=state.registers[15]
    self.set_cpu(state);continue
   assert 0x11e6c<=pc<0x11f6c,hex(pc)
   covered.add(pc);self.core.m68k_execute(1)
  raise AssertionError('original work bound')
 def translated(self,fn,ram,initial,case,fail=None,budget=64,service_fault=None,poll_budget=64,wait_reads=0):
  memory=bytearray(ram);entries=[];events=[];errors=[];polls=0
  def read(w):
   def callback(_,a,out):
    nonlocal polls
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['bad_read',a,w]);return 1
    if a==0x10a684 and w==4:
     out[0]=1 if polls<wait_reads else int.from_bytes(memory[a:a+w],'big');polls+=1
    else:out[0]=int.from_bytes(memory[a:a+w],'big')
    events.append(['r',a,w,out[0]]);return 0
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
    status=self.helper(memory,state,target,case,len(entries)-1)
    if service_fault=='stack':state.registers[15]+=4
    if service_fault=='return':memory[state.registers[15]:state.registers[15]+4]=bytes(4)
    if service_fault=='invalid_yield':state.pc=0x123456;return 6
    return status
   except Exception as e:errors.append(repr(e));return 1
  w=scene.coordinate.scheduler.cleanup.world
  callbacks=[w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),SERVICE(service)]
  bus=Bus(w.R8(),*callbacks[:4],w.CALL(),None,0);state=CPU.from_buffer_copy(bytes(initial))
  status=fn(c.byref(bus),c.byref(state),callbacks[4],None,budget,poll_budget)
  return status,bytes(memory),state,entries,events,errors
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x11e6c)
 modes=[0,1,2,3,4,0x7fff,0x8000,0xffff];roots=[0x11e6c,0x11e86,*RETURNS]
 for root in roots:
  count=256 if root==0x11e86 else 64
  for i in range(count):
   state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP]
   state.pc=root;state.sr=(0x2000 if i&1 else 0)|((i//2)%32)|((i//64)%8)<<8
   state.usp=0x1d8000 if state.sr&0x2000 else SP;state.ssp=SP if state.sr&0x2000 else 0x1ff000
   memory=bytearray(baseline);memory[SP-512:SP+128]=rng.randbytes(640)
   def put(a,w,v):memory[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
   # A valid existing LINK frame for iteration/return continuations; entry
   # creates a fresh frame. Source calls may have outstanding arguments.
   frame=SP+64;state.registers[14]=frame;put(frame,4,rng.getrandbits(32));put(frame+4,4,STOP);put(SP,4,STOP)
   if root==0x11f6a:put(SP,4,STOP)
   mode=modes[(i//2)%8];dirty=[0,1,0x8000,0xffff][i%4]
   for a,w,v in [(0x403d6,2,mode),(0x40400,2,dirty),(0x400e6,4,0x80000),(0x8008e,4,rng.getrandbits(32)),(0x9008e,4,rng.getrandbits(32)),(0x403dc,4,i%8),(0x49b88,4,[0,1,0x7fffffff,0x80000000,0xffffffff][i%5]),(0x10a684,4,0),(0xbd830,4,rng.getrandbits(32)),(0xbd83c,4,rng.getrandbits(32))]:put(a,w,v)
   for j in range(8):put(0x403e0+2*j,2,rng.getrandbits(16))
   yield bytes(memory),state,dict(root=root,variant=i,mode=mode,dirty=dirty)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=SRC/'deck-task-source.c');ap.add_argument('--output',type=Path);args=ap.parse_args()
 out=args.output or ROOT/'verification/deck-task-source'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True,exist_ok=True);print(out,flush=True)
 state=dict(status='compiling',pid=os.getpid(),directory=str(out),source=str(args.source),whole_game_complete=False,new_training=False,authorship='Coordinator structured recovery; dependency bodies explicit fixtures.')
 def mark():save(out/'protocol.json',state)
 mark();library=out/'libdeck-task.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(args.source),'-o',str(library)]
 try:
  p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  lib=c.CDLL(str(library));fn=lib.biwn_deck_task_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int
  engine=Engine();rows=[];coverage=set();guards=[];suspensions=[]
  try:
   for i,(ram,initial,case)in enumerate(fixtures()):
    if args.limit and i>=args.limit:break
    original_status,expected,cpu,entries,covered=engine.original(ram,initial,case)
    status,actual,got,observed,events,errors=engine.translated(fn,ram,initial,case)
    if status!=original_status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
     save(out/'counterexample.json',dict(case=case,status=status,original_status=original_status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(j),a,b]for j,(a,b)in enumerate(zip(expected,actual))if a!=b][:32]));raise AssertionError(out/'counterexample.json')
    coverage|=covered;rows.append(dict(case=case,status=status,CPU=cpu_dict(cpu),RAM=sha(expected),helper_entries=len(entries),C_events=len(events),full_CPU_RAM_helper_entry_match=True))
    if i%64==0:state.update(status='checking',completed=i+1);mark();print('case',i+1,flush=True)
   if not args.limit:
    # The two permitted deep-scheduler continuation states retain all frames.
    ram,initial,base=next(fixtures())
    for pc in [0xdf60,0xdf8c]:
     case={**base,'suspend':pc};expected=engine.original(ram,initial,case);got=engine.translated(fn,ram,initial,case)
     assert expected[0]==got[0]==6 and expected[1]==got[1]and cpu_dict(expected[2])==cpu_dict(got[2])and expected[3]==got[3]and not got[5]
     suspensions.append(dict(PC=hex(pc),full_CPU_RAM_private_frame_match=True))
    # All bus failures in mode3, plus service/budget/return failures, must
    # preserve the input CPU. These are intentional host error tests.
    ram,initial,case=next(x for x in fixtures()if x[1].pc==0x11e86 and x[2]['mode']==3 and x[2]['variant']%2)
    status,_,_,_,events,_=engine.translated(fn,ram,initial,case);assert status==6
    for fail in range(len(events)):
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,fail=fail);assert status==2 and not errors and cpu_dict(got)==cpu_dict(initial),(fail,status);guards.append(dict(data_failure=fail))
    for fault,expect in [('error',3),('stack',5),('return',5),('invalid_yield',3)]:
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,service_fault=fault);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(service_fault=fault))
    for budget,expect in [(0,1),(1,4)]:
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,budget=budget);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(helper_budget=budget))
    # Host wait slicing is an added explicit continuation, not hardware time.
    initial.pc=0x11f50
    status,_,got,_,events,errors=engine.translated(fn,ram,initial,case,poll_budget=3,wait_reads=10)
    assert status==6 and got.pc==0x11f50 and len(events)==3 and not errors
    resumed=engine.translated(fn,ram,got,case,poll_budget=64)
    direct=engine.translated(fn,ram,initial,case,poll_budget=64,wait_reads=3)
    assert resumed[0]==direct[0]==6 and resumed[1]==direct[1]and cpu_dict(resumed[2])==cpu_dict(direct[2])and not resumed[5]and not direct[5]
    suspensions.append(dict(display_wait_sliced_at='0x11f50',resumed_same_CPU_and_RAM_as_unsliced=True,no_clock_or_IRQ_invented=True))
  finally:engine.native.close()
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=scene.Cs(scene.CS_ARCH_M68K,scene.CS_MODE_BIG_ENDIAN|scene.CS_MODE_M68K_000);addresses={x.address for x in decoder.disasm(baseline[0x11e6c:0x11f6c],0x11e6c)}
  assert args.limit or coverage==addresses,sorted(addresses-coverage)
  save(out/'cases.json',rows);save(out/'guards.json',guards);save(out/'continuations.json',suspensions)
  paths=[args.source,SRC/'deck-task-source.h',SRC.parent/'deck-scene-source/deck-scene-contract.h',SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h',Path(__file__),Path(scene.__file__),Path(scene.coordinate.__file__)]
  deps=[ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']
  state.update(status='terminal_preflight_pass'if args.limit else'terminal_complete_readable_Deck_outer_task_original_CPU_match',completed=len(rows),instruction_locations=[len(coverage),len(addresses)],host_error_checks_passed=len(guards),continuation_checks_passed=len(suspensions),source_sha256={str(p.resolve()):sha(p.read_bytes())for p in paths},native_dependencies_sha256={str(p):sha(p.read_bytes())for p in deps},scope='Complete256byte11E6C..11F6C outertask includingRTSviaadapter. All8modevalues inclsignedunknowns,bothstackbanks/allCCR,allJSRreturncontinuations,dirtyoverlay,mailargumentstack,positive/zero/negative49B88,calleeclobbers/globalchanges,constructorfixtureyieldDF60/DF8C,explicitboundedpollresume. FullCPU/2MBRAM/privateframes/helper-entry comparison. Dependencies arefixtures;noorderedbus/IRQ/timing/naturalgameplay/physicalhardware/fullgamerebuildproof.');mark()
  if not args.limit:save(ROOT/'verification/Deck-task-source-current.json',state)
  print(state['status'],len(rows),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
