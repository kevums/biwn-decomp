"""Native F4D8 actor plus two idle tasks versus C caller/actual scheduler."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_actor_task as actor
import check_biwn_actor_navigation as navigation
import check_biwn_rng_cpu as rng_cpu
import check_biwn_actor_movement_collision as motion
import check_biwn_render_display_runtime as prior
ROOT=actor.ROOT;world=actor.world;CPU=actor.CPU;SSP=0x1d0000
CONTEXTS=[0xc1528,0xc5928,0xc5528];ENTRIES=[0xf4d8,0xf360,0xf880];MAIN=CONTEXTS[0]
NAV={0xf368,0x13f12,0x13f7c,0x13fea,0x1a77c,0x13c9a};STUBS=[x for x in actor.WIDTHS if x not in NAV];save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def get(r,a,w=4):return int.from_bytes(r[a:a+w],'big')
class Plan:
 def __init__(self,case,device):self.case=case;self.device=device;self.calls=[];self.movements=[]
 def observe(self,target,args,incoming):
  self.calls.append(['call',target,args,incoming])
  if target==0x13c9a:
   obj=args[0];ram=self.device.ram();self.movements.append({'iteration':len(self.movements),'object':obj,'heading':get(ram,obj+110,1),'target_heading':get(ram,obj+111,1),'vertical_velocity':get(ram,obj+116),'speed':get(ram,obj+120),'X':get(ram,obj+4),'Y':get(ram,obj+8,2),'Z':get(ram,obj+10),'collision':get(ram,obj+196,2),'mode':get(ram,obj+20,2)})
class Device(motion.submit_cpu.hardware.Device):
 def __init__(self,library=None,core=None):
  super().__init__(library,core=core);self.errors=[];self.address_aliases=[]
  def reader(width):
   def cb(_,a,out):
    try:out[0]=self.read(a,width);return 0
    except Exception as error:self.errors.append(repr(error));return 1
   return cb
  def writer(width):
   def cb(_,a,v):
    try:
     if width==1:self.direct(a,width,v)
     elif width==2:self.write16(a,v)
     else:self.write(a,v)
     return 0
    except Exception as error:self.errors.append(repr(error));return 1
   return cb
  self.r8=world.R8(reader(1));self.r16=world.R16(reader(2));self.r32=world.R32(reader(4));self.w16=world.W16(writer(2));self.w32=world.W32(writer(4));self.write8=actor.W8(writer(1))
 def physical(self,address,width,write):
  physical=address&0xffffff
  if physical!=address:self.address_aliases.append({'logical':address,'physical':physical,'width':width,'write':write})
  return physical
 def read(self,address,width):return super().read(self.physical(address,width,False),width)
 def write(self,address,value):return super().write(self.physical(address,4,True),value)
 def write16(self,address,value):return super().write16(self.physical(address,2,True),value)
 def direct(self,address,width,value):return super().direct(self.physical(address,width,True),width,value)
 def seed(self,ram,mode):
  super().seed(ram,mode);self.address_aliases=[]
  if hasattr(self.lib,'lab_render_geometry_reset'):self.lib.lab_render_geometry_reset()
 def stats(self):
  d=super().stats();d['original_GPUExec1_calls']=d['GPUExec1_calls']
  if hasattr(self.lib,'lab_render_geometry_stat'):d.update(original_GPU_geometry_calls=self.lib.lab_render_geometry_stat(0),C_GPU_geometry_calls=self.lib.lab_render_geometry_stat(1))
  if hasattr(self.lib,'lab_integer_division_control'):d['GPU_division_control']=self.lib.lab_integer_division_control()
  d['CPU_bus_high_byte_aliases']=len(self.address_aliases)
  return d
class Runtime:
 def __init__(self,library,device_library=None):
  self.device=Device(device_library);self.core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));self.lib=c.CDLL(str(library));self.actor=actor.bind(self.lib);self.navigation=navigation.bind(self.lib);self.rng_cpu=rng_cpu.bind(self.lib);self.movement=motion.bind(self.lib);self.direction=motion.direction.bind(self.lib);self.submit=motion.submit_cpu.bind(self.lib);self.collision=motion.collision.bind(self.lib)
  self.core.m68k_set_reg.argtypes=[c.c_int,c.c_uint32];self.core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];self.core.m68k_get_reg.restype=c.c_uint32;self.core.m68k_execute.argtypes=[c.c_int];self.core.m68k_execute.restype=c.c_int;self.core.m68k_set_irq.argtypes=[c.c_uint32];self.prefix=(c.c_uint32*18).in_dll(self.core,'regs');self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32
  self.yield_fn=self.lib.biwn_scheduler_yield;self.yield_fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32];self.yield_fn.restype=c.c_int
  self.remove_fn=self.lib.biwn_scheduler_remove;self.remove_fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32];self.remove_fn.restype=c.c_int
  self.idle=self.lib.biwn_task_loop_step;self.idle.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),prior.BODY,c.c_void_p,c.c_uint32];self.idle.restype=c.c_int
 def current(self):return get(self.device.ram(),0xc0920)
 def cpu(self):
  state=CPU();state.registers[:]=[self.core.m68k_get_reg(None,i)for i in range(16)];state.pc=self.core.m68k_get_reg(None,16);state.sr=self.core.m68k_get_reg(None,17);state.usp=state.registers[15];state.ssp=self.prefix[17];return state
 def event(self,state):return {'context':self.current(),'PC':state.pc,'SP':state.registers[15],'SR':state.sr}
 def native(self,ram,case,iterations,remove=False):
  self.device.seed(ram,0);plan=Plan(case,self.device)
  for target in STUBS:self.device.direct(target,2,0x4e75)
  self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000);self.core.m68k_set_reg(15,SSP);self.core.m68k_set_reg(17,0)
  for i,v in enumerate(case['registers']):self.core.m68k_set_reg(i,v)
  self.core.m68k_set_reg(15,MAIN+0x400);self.core.m68k_set_reg(17,case['SR']);self.core.m68k_set_reg(16,0xf4d8);handoffs=[];yields=[];steps=[];navreturns=[];navtarget=None;removals=[]
  for _ in range(500000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==0xf70c and len(plan.movements)>=iterations:
    if not remove:break
    self.device.direct(0x49d6c+case['registers'][7]*206+2,2,case.get('kill_word',1))
   assert any(lo<=pc<hi for lo,hi in[(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xdf7a,0xdf7c),(0xdeb6,0xdee2),(0xf360,0xf368),(0xf880,0xf888)])or pc in STUBS or any(lo<=pc<hi for lo,hi in navigation.RANGES+rng_cpu.RANGES+motion.direction.RANGES+motion.submit_cpu.RANGES+motion.collision.RANGES+[(0x13c9a,0x13f12)]),hex(pc);steps.append(pc)
   if pc in NAV:
    navtarget=pc;sp=self.core.m68k_get_reg(None,15);offset=4;args=[]
    for width in actor.WIDTHS[pc]:args.append(get(self.device.ram(),sp+offset,width));offset+=width
    plan.observe(pc,args,self.core.m68k_get_reg(None,0))
   if pc in navigation.RETURNS|{0x1a7f2,0x13f10}:
    navreturns.append({'target':navtarget,'CPU':prior.scheduler.cpu_dict(self.cpu())});navtarget=None
   if pc in STUBS:
    sp=self.core.m68k_get_reg(None,15);args=[];offset=4
    for width in actor.WIDTHS[pc]:args.append(get(self.device.ram(),sp+offset,width));offset+=width
    self.core.m68k_set_reg(0,plan.call(pc,args,self.core.m68k_get_reg(None,0)))
   if pc==0xdf60:
    sp=self.core.m68k_get_reg(None,15);yields.append({'context':self.current(),'SP':sp,'return_PC':get(self.device.ram(),sp)})
   if pc==0xdf7a:
    state=self.cpu();removals.append({'CPU':prior.scheduler.cpu_dict(state),'context_header':self.device.ram()[MAIN:MAIN+38].hex(),'return_PC':get(self.device.ram(),state.registers[15])})
   self.core.m68k_execute(1)
   if self.core.GPUReadLong(0xf03204,0)==0x4320:self.device.write(0xf03204,0x4320)
   if pc==0xdf6a or(pc==0xde5a and self.core.m68k_get_reg(None,16)!=0xdf66):
    handoffs.append(self.event(self.cpu()))
    if remove and get(self.device.ram(),0xc0924)==MAIN:break
  else:raise AssertionError('Native actor task did not resume')
  for target in STUBS:self.device.direct(target,2,get(ram,target,2))
  return self.device.ram(),self.cpu(),{'calls':plan.calls,'movements':plan.movements,'handoffs':handoffs,'yields':yields,'steps':steps,'navigation_returns':navreturns,'removals':removals,'device':self.device.stats()}
 def translated(self,ram,case,iterations,remove=False):
  self.device.seed(ram,1);plan=Plan(case,self.device);cpu=CPU();cpu.registers[:]=case['registers'];cpu.registers[15]=MAIN+0x400;cpu.pc=0xf4d8;cpu.sr=case['SR'];cpu.usp=cpu.registers[15];cpu.ssp=SSP;handoffs=[];yields=[];errors=[];navreturns=[];removals=[]
  def movement_service(_,bus,state,target):
   try:
    if target==0x13440:return self.direction(bus,state)
    if target==0xe220:return self.submit(bus,state,1000)
    assert target in[0x13b5a,0x13bb0];return self.collision(bus,state,2048)
   except Exception as error:errors.append(repr(error));return 1
  movement_cb=motion.SERVICE(movement_service)
  def service(_,bus,state,target):
   try:
    assert target in NAV;stack=state.contents.registers[15];offset=4;args=[]
    for width in actor.WIDTHS[target]:args.append(get(self.device.ram(),stack+offset,width));offset+=width
    plan.observe(target,args,state.contents.registers[0])
    if target==0x1a77c:status=self.rng_cpu(bus,state)
    elif target==0x13c9a:status=self.movement(bus,state,movement_cb,None)
    else:status=self.navigation(bus,state)
    assert status==0,status;navreturns.append({'target':target,'CPU':prior.scheduler.cpu_dict(state.contents)});return 0
   except Exception as error:errors.append(repr(error));return 1
  cb=actor.SERVICE(service);bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,world.CALL(),None,0)
  for _ in range(1000):
   if cpu.pc==0xf70c and len(plan.movements)>=iterations:
    if not remove:break
    self.device.direct(0x49d6c+case['registers'][7]*206+2,2,case.get('kill_word',1))
   if self.current()==MAIN:
    status=self.actor(c.byref(bus),c.byref(cpu),self.device.write8,cb,None,64)
    if remove and status==6:
     assert cpu.pc==0xdf7a;removals.append({'CPU':prior.scheduler.cpu_dict(cpu),'context_header':self.device.ram()[MAIN:MAIN+38].hex(),'return_PC':get(self.device.ram(),cpu.registers[15])})
     status=self.remove_fn(c.byref(bus),c.byref(cpu),64);assert status==0;handoffs.append(self.event(cpu));break
    assert status==0,(status,errors);assert cpu.pc==0xdf60
    yields.append({'context':self.current(),'SP':cpu.registers[15],'return_PC':get(self.device.ram(),cpu.registers[15])});status=self.yield_fn(c.byref(bus),c.byref(cpu),64);assert status==0;handoffs.append(self.event(cpu))
   else:
    yielding=cpu.pc in[0xf360,0xf880]
    if yielding:yields.append({'context':self.current(),'SP':cpu.registers[15]-4,'return_PC':cpu.pc+6})
    status=self.idle(c.byref(bus),c.byref(cpu),prior.BODY(),None,64);assert status==0
    if yielding:handoffs.append(self.event(cpu))
  else:raise AssertionError('C actor task did not resume')
  assert not errors
  return self.device.ram(),cpu,{'calls':plan.calls,'movements':plan.movements,'handoffs':handoffs,'yields':yields,'navigation_returns':navreturns,'removals':removals,'device':self.device.stats()}
 def close(self):self.device.close()
def fixture(snapshot,case):
 script=actor.Script(snapshot,case);ram=bytearray(script.memory);obj=0x49d6c+case['registers'][7]*206
 def put(a,w,v):ram[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
 container=0x82000;tiles=0x90000;scene=0x84000;scan=0x100000;regions=0x110000;indoor=0x121000
 put(container,2,16);put(container+8,4,tiles)
 for room in range(-6,7):put(0x49bb4+room*4,4,container)
 for z in range(4):
  for x in range(4):
   index=z*4+x;record=tiles+index*20
   for off,v in[(0,2),(2,index+4 if z<3 else 0xffff),(4,index-4 if z else 0xffff),(6,index+1 if x<3 else 0xffff),(8,index-1 if x else 0xffff),(10,x*4),(14,z*4),(16,4),(18,4)]:put(record+off,2,v)
 put(0x49c18,4,scene);put(scene,2,2);put(scene+4,4,regions);put(scene+8,4,scan)
 for n in range(2):
  for off,v in[(2,0),(4,0),(6,16),(8,16)]:put(regions+n*24+off,2,v)
 for n,key in enumerate(range(-512,544)):
  put(scan+n*6,2,key);put(scan+n*6+2,2,0xf000 if n==1055 else 0x7000);put(scan+n*6+4,2,0)
 put(indoor+6,2,0);put(indoor+8,2,16);put(indoor+22,2,0)
 slot=case['registers'][7];x=0x2400+slot*4;z=0x9800+slot*4;ix=(x>>8)&3;iz=(z>>8)&3;tile=iz*4+ix
 for off,w,v in[(2,2,0),(4,4,x),(10,4,z),(14,2,slot*31),(16,2,slot*47),(18,2,slot*59),(20,2,1),(22,2,0),(26,4,0x10000),(30,4,0xffff0000),(34,4,0x10000),(38,4,0xffff0000),(44,4,indoor),(48,4,0x10000),(52,4,0xffff0000),(56,4,0x10000),(60,4,0xffff0000),(64,2,0),(66,2,tile),(68,4,tiles+tile*20),(72,4,(x&0xfffffc00)+ix*256+256),(76,4,(x&0xfffffc00)+ix*256),(80,4,(z&0xfffffc00)+iz*256+256),(84,4,(z&0xfffffc00)+iz*256),(112,4,0),(192,2,0)]:put(obj+off,w,v)
 put(0x49b9f,1,0);put(0x47b88+18,2,0);put(0x47b88+22,2,0)
 put(0x462e8,4,44488);put(0x462ec,4,3399);put(0x113082+slot*4,4,slot+1)
 put(0xc0920,4,MAIN);put(0x80,4,0xde08);put(0x778cc,4,0)
 for i,(ctx,entry)in enumerate(zip(CONTEXTS,ENTRIES)):
  for off,w,v in[(0,4,CONTEXTS[(i+1)%3]),(4,4,CONTEXTS[(i-1)%3]),(8,4,entry),(12,4,ctx+0x400),(16,4,entry),(20,2,0),(22,4,0),(26,4,0),(30,4,case['registers'][7]if i==0 else 0),(34,4,0)]:put(ctx+off,w,v)
 return bytes(ram)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-actor-full-movement-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_actor_task.c','biwn_actor_navigation.c','biwn_actor_movement.c','biwn_actor_direction.c','biwn_movement_submit_cpu.c','biwn_actor_collision.c','biwn_geometry_cpu.c','biwn_rng_cpu.c','biwn_signed_division.c','biwn_camera.c','biwn_scheduler.c','biwn_task_loops.c'];lib=out/'libactor-runtime.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});runtime=Runtime(lib);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=[x for x in actor.cases()if x['PC']==0xf4d8][:opt.limit or 128];rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});ram=fixture(snapshot,case);left,expected,old=runtime.native(ram,case,8);right,actual,new=runtime.translated(ram,case,8);coverage.update(old['steps'])
   if left!=right or bytes(expected)!=bytes(actual)or any(old[k]!=new[k]for k in ['calls','movements','handoffs','yields','navigation_returns']):
    save(out/'mismatch.json',{'case':case,'CPU_original':prior.scheduler.cpu_dict(expected),'CPU_C':prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(left,right))if x!=y][:100],'original':old,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
   assert len(new['movements'])==8 and len(new['handoffs'])==24 and not new['device']['original_GPUExec1_calls']and not new['device']['game_frames_executed'];rows.append({'case':i,'parameters':case,'final_CPU':prior.scheduler.cpu_dict(actual),'original':old,'rebuilt':new,'whole2MBRAM_fullCPU_SSP_USP_CCR_headers_privateframes_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:runtime.close()
 save(out/'fixtures.json',rows)
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'actor_with_real_navigation_RNG_movement_GPU_collision_geometry_scheduler_matches_original','directory':str(out),'cases':len(rows),'actor_iterations':len(rows)*8,'task_handoffs':len(rows)*24,'task_contexts':CONTEXTS,'task_entries':ENTRIES,'whole2MBRAM_including_private_stacks_compared':True,'fullCPU_SR_SSP_USP_compared':True,'public_context_header_bytes_compared':38,'scheduler_yields_real':True,'scripted_helpers':[hex(x)for x in STUBS],'navigation_helper_bodies_real':4,'indexed_RNG_body_real':True,'math_kernels_full_CPU_real':True,'movement_and_collision_real':True,'GPU_output_words_scripted':False,'synthetic_scene_geometry':True,'synchronous_GPU_dispatch_model':True,'navigation_helper_return_CPU_compared':True,'removal_TRAP2_executed':False,'startup21context_fixture_linked':False,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'matched':['Native originalCPU executesF4D8actor, twoidle loops, actualDF60/TRAP0/DE08/RTE andsavedcontinuations. Ccaller andscheduler produceidenticalwholeRAM/fullCPU/stackbanks/calls/fields/handoffs underexplicithelperfixtures.','Eightactoriterations and24actualhandoffs percase preserve8liveargumentbytes acrossyields and40byteinitialcallee-saveframe. SavedCCR andall38publiccontextbytes compare withno masks.'],'limits':['No actor helper bodies are scripted in this bounded outdoor actor test. RNG, navigation, movement, direction, GPU math, collision and geometry execute original/C code. Scene geometry and clock are seeded fixtures; GPU completion is synchronous, not reconstructed dispatcher concurrency. DFA6 getter, navigation helpers, caller, scheduler and idle bodies are real here.','Three-context test isseparatefrom21-contextstartup/world/renderpipeline. Removaltrap2,realcalleeeffects/assetlifecycles/fullscene/game/hardware remainunfinished. No originalCPU/GPU/gameframes executeontheCside.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-actor-full-movement-runtime-checks.json',report);print(json.dumps(report))
if __name__=='__main__':main()
