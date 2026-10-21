"""Native F4D8 actor plus two idle tasks versus C caller/actual scheduler."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_actor_task as actor
import check_biwn_render_display_runtime as prior
ROOT=actor.ROOT;world=actor.world;CPU=actor.CPU;SSP=0x1d0000
CONTEXTS=[0xc1528,0xc5928,0xc5528];ENTRIES=[0xf4d8,0xf360,0xf880];MAIN=CONTEXTS[0]
STUBS=list(actor.WIDTHS);save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def get(r,a,w=4):return int.from_bytes(r[a:a+w],'big')
class Plan:
 def __init__(self,case,device):self.case=case;self.device=device;self.counts={};self.calls=[];self.movements=[]
 def call(self,target,args,incoming):
  n=self.counts.get(target,0);self.counts[target]=n+1;self.calls.append(['call',target,args,incoming]);values=self.case['returns'].get(str(target),[self.case['default_helper_return']]);result=values[min(n,len(values)-1)]
  if target==0x13c9a:
   obj=args[0];ram=self.device.ram();self.movements.append({'iteration':n,'object':obj,'heading':get(ram,obj+110,1),'target_heading':get(ram,obj+111,1),'vertical_velocity':get(ram,obj+116),'speed':get(ram,obj+120)})
   # Explicit external movement fixture, identical on both paths; no physics claim.
   self.device.direct(obj+4,4,0x2400+64*n);self.device.direct(obj+10,4,0x9800+32*n);self.device.direct(obj+8,2,[0,1,0xffff][n%3]);self.device.direct(obj+196,2,1 if n%3 else 0)
   if n%4==3:self.device.direct(obj+110,1,get(ram,obj+111,1))
  return result
class Runtime:
 def __init__(self,library):
  self.device=prior.render.Runtime();self.core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));self.lib=c.CDLL(str(library));self.actor=actor.bind(self.lib)
  self.core.m68k_set_reg.argtypes=[c.c_int,c.c_uint32];self.core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];self.core.m68k_get_reg.restype=c.c_uint32;self.core.m68k_execute.argtypes=[c.c_int];self.core.m68k_execute.restype=c.c_int;self.core.m68k_set_irq.argtypes=[c.c_uint32];self.prefix=(c.c_uint32*18).in_dll(self.core,'regs')
  self.yield_fn=self.lib.biwn_scheduler_yield;self.yield_fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32];self.yield_fn.restype=c.c_int
  self.idle=self.lib.biwn_task_loop_step;self.idle.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),prior.BODY,c.c_void_p,c.c_uint32];self.idle.restype=c.c_int
 def current(self):return get(self.device.ram(),0xc0920)
 def cpu(self):
  state=CPU();state.registers[:]=[self.core.m68k_get_reg(None,i)for i in range(16)];state.pc=self.core.m68k_get_reg(None,16);state.sr=self.core.m68k_get_reg(None,17);state.usp=state.registers[15];state.ssp=self.prefix[17];return state
 def event(self,state):return {'context':self.current(),'PC':state.pc,'SP':state.registers[15],'SR':state.sr}
 def native(self,ram,case,iterations):
  self.device.seed(ram,0);plan=Plan(case,self.device)
  for target in STUBS:self.device.direct(target,2,0x4e75)
  self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000);self.core.m68k_set_reg(15,SSP);self.core.m68k_set_reg(17,0)
  for i,v in enumerate(case['registers']):self.core.m68k_set_reg(i,v)
  self.core.m68k_set_reg(15,MAIN+0x400);self.core.m68k_set_reg(17,case['SR']);self.core.m68k_set_reg(16,0xf4d8);handoffs=[];yields=[];steps=[]
  for _ in range(500000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==0xf70c and len(plan.movements)>=iterations:break
   assert any(lo<=pc<hi for lo,hi in[(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xf360,0xf368),(0xf880,0xf888)])or pc in STUBS,hex(pc);steps.append(pc)
   if pc in STUBS:
    sp=self.core.m68k_get_reg(None,15);args=[];offset=4
    for width in actor.WIDTHS[pc]:args.append(get(self.device.ram(),sp+offset,width));offset+=width
    self.core.m68k_set_reg(0,plan.call(pc,args,self.core.m68k_get_reg(None,0)))
   if pc==0xdf60:
    sp=self.core.m68k_get_reg(None,15);yields.append({'context':self.current(),'SP':sp,'return_PC':get(self.device.ram(),sp)})
   self.core.m68k_execute(1)
   if pc==0xdf6a or(pc==0xde5a and self.core.m68k_get_reg(None,16)!=0xdf66):handoffs.append(self.event(self.cpu()))
  else:raise AssertionError('Native actor task did not resume')
  for target in STUBS:self.device.direct(target,2,get(ram,target,2))
  return self.device.ram(),self.cpu(),{'calls':plan.calls,'movements':plan.movements,'handoffs':handoffs,'yields':yields,'steps':steps,'device':self.device.stats()}
 def translated(self,ram,case,iterations):
  self.device.seed(ram,1);plan=Plan(case,self.device);cpu=CPU();cpu.registers[:]=case['registers'];cpu.registers[15]=MAIN+0x400;cpu.pc=0xf4d8;cpu.sr=case['SR'];cpu.usp=cpu.registers[15];cpu.ssp=SSP;handoffs=[];yields=[];errors=[]
  def service(_,bus,state,target):
   try:
    stack=state.contents.registers[15];offset=4;args=[]
    for width in actor.WIDTHS[target]:args.append(get(self.device.ram(),stack+offset,width));offset+=width
    state.contents.registers[0]=plan.call(target,args,state.contents.registers[0]);return 0
   except Exception as error:errors.append(repr(error));return 1
  cb=actor.SERVICE(service);bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,world.CALL(),None,0)
  for _ in range(1000):
   if cpu.pc==0xf70c and len(plan.movements)>=iterations:break
   if self.current()==MAIN:
    status=self.actor(c.byref(bus),c.byref(cpu),self.device.write8,cb,None,64);assert status==0,(status,errors);assert cpu.pc==0xdf60
    yields.append({'context':self.current(),'SP':cpu.registers[15],'return_PC':get(self.device.ram(),cpu.registers[15])});status=self.yield_fn(c.byref(bus),c.byref(cpu),64);assert status==0;handoffs.append(self.event(cpu))
   else:
    yielding=cpu.pc in[0xf360,0xf880]
    if yielding:yields.append({'context':self.current(),'SP':cpu.registers[15]-4,'return_PC':cpu.pc+6})
    status=self.idle(c.byref(bus),c.byref(cpu),prior.BODY(),None,64);assert status==0
    if yielding:handoffs.append(self.event(cpu))
  else:raise AssertionError('C actor task did not resume')
  assert not errors
  return self.device.ram(),cpu,{'calls':plan.calls,'movements':plan.movements,'handoffs':handoffs,'yields':yields,'device':self.device.stats()}
 def close(self):self.device.close()
def fixture(snapshot,case):
 script=actor.Script(snapshot,case);ram=bytearray(script.memory);obj=0x49d6c+case['registers'][7]*206
 def put(a,w,v):ram[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
 put(obj+2,2,0);put(0xc0920,4,MAIN);put(0x80,4,0xde08);put(0x778cc,4,0)
 for i,(ctx,entry)in enumerate(zip(CONTEXTS,ENTRIES)):
  for off,w,v in[(0,4,CONTEXTS[(i+1)%3]),(4,4,CONTEXTS[(i-1)%3]),(8,4,entry),(12,4,ctx+0x400),(16,4,entry),(20,2,0),(22,4,0),(26,4,0),(30,4,case['registers'][7]if i==0 else 0),(34,4,0)]:put(ctx+off,w,v)
 return bytes(ram)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-actor-task-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_actor_task.c','biwn_scheduler.c','biwn_task_loops.c'];lib=out/'libactor-runtime.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});runtime=Runtime(lib);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=[x for x in actor.cases()if x['PC']==0xf4d8][:opt.limit or 128];rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});ram=fixture(snapshot,case);left,expected,old=runtime.native(ram,case,8);right,actual,new=runtime.translated(ram,case,8);coverage.update(old['steps'])
   if left!=right or bytes(expected)!=bytes(actual)or any(old[k]!=new[k]for k in ['calls','movements','handoffs','yields']):
    save(out/'mismatch.json',{'case':case,'CPU_original':prior.scheduler.cpu_dict(expected),'CPU_C':prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(left,right))if x!=y][:100],'original':old,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
   assert len(new['movements'])==8 and len(new['handoffs'])==24 and not new['device']['original_GPUExec1_calls']and not new['device']['game_frames_executed'];rows.append({'case':i,'parameters':case,'final_CPU':prior.scheduler.cpu_dict(actual),'original':old,'rebuilt':new,'whole2MBRAM_fullCPU_SSP_USP_CCR_headers_privateframes_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:runtime.close()
 save(out/'fixtures.json',rows)
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'actor_caller_two_idle_tasks_real_scheduler_match_native_CPU_C','directory':str(out),'cases':len(rows),'actor_iterations':len(rows)*8,'task_handoffs':len(rows)*24,'task_contexts':CONTEXTS,'task_entries':ENTRIES,'whole2MBRAM_including_private_stacks_compared':True,'fullCPU_SR_SSP_USP_compared':True,'public_context_header_bytes_compared':38,'scheduler_yields_real':True,'scripted_helpers':[hex(x)for x in STUBS],'removal_TRAP2_executed':False,'startup21context_fixture_linked':False,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'matched':['Native originalCPU executesF4D8actor, twoidle loops, actualDF60/TRAP0/DE08/RTE andsavedcontinuations. Ccaller andscheduler produceidenticalwholeRAM/fullCPU/stackbanks/calls/fields/handoffs underexplicithelperfixtures.','Eightactoriterations and24actualhandoffs percase preserve8liveargumentbytes acrossyields and40byteinitialcallee-saveframe. SavedCCR andall38publiccontextbytes compare withno masks.'],'limits':['Sixactorhelpers areexplicit scripts: RNG, waypoint, steering predicates andmovement. Movementfieldupdates are externaltestfixtures, not actualphysics/actorAIbehavior. OnlyDFA6getter andcaller/scheduler/idle bodies are realhere.','Three-context test isseparatefrom21-contextstartup/world/renderpipeline. Removaltrap2,realcalleeeffects/assetlifecycles/fullscene/game/hardware remainunfinished. No originalCPU/GPU/gameframes executeontheCside.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-actor-task-runtime-checks.json',report);print(json.dumps(report))
if __name__=='__main__':main()
