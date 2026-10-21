"""F4D8 caller against original CPU at yield/removal boundaries, explicit callees."""
import ctypes as c,json,random,subprocess,os,hashlib,argparse
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_actor_creation as prior
import check_biwn_scheduler as scheduler
ROOT=prior.ROOT;world=prior.world;SP=prior.SP;STOP=prior.STOP;CPU=scheduler.CPU;W8=prior.W8
SERVICE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32)
WIDTHS={0x1a77c:[2],0xf368:[4],0x13f12:[4,4],0x13f7c:[4,4],0x13fea:[4],0x13c9a:[4,4]}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(prior.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.counts={}
 def read(self,a,w):
  if SP-0x1000<=a<SP+64:return int.from_bytes(self.memory[a:a+w],'big')
  return super().read(a,w)
 def write(self,a,w,v):
  if SP-0x1000<=a<SP+64:self.put(a,w,v);return
  return super().write(a,w,v)
 def call(self,target,args,incoming):
  self.trace.append(['call',target,args,incoming]);n=self.counts.get(target,0);self.counts[target]=n+1;values=self.case['returns'].get(str(target),[self.case['default_helper_return']]);return values[min(n,len(values)-1)]
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory))
 for r,v in zip(world.REGS,case['registers']):cpu.reg_write(r,v)
 cpu.reg_write(UC_M68K_REG_SR,case['SR']);cpu.reg_write(UC_M68K_REG_A7,SP)
 for a in WIDTHS:cpu.mem_write(a,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in[0xdf60,0xdf7a]:e.emu_stop();return
  if a in WIDTHS:
   stack=e.reg_read(UC_M68K_REG_A7);args=[];off=4
   for width in WIDTHS[a]:args.append(int.from_bytes(e.mem_read(stack+off,width),'big'));off+=width
   e.reg_write(UC_M68K_REG_D0,script.call(a,args,e.reg_read(UC_M68K_REG_D0)));return
  assert 0xf4d8<=a<0xf712 or 0xdfa6<=a<0xdfb2,hex(a);coverage.add(a);steps.append(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+64:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):script.write(a,w,v&((1<<(w*8))-1))
 code_hook=cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['PC'],STOP,count=20000,timeout=2000000);pc=cpu.reg_read(UC_M68K_REG_PC);assert pc in[0xdf60,0xdf7a]
 ram=bytearray(cpu.mem_read(0,0x200000))
 for a in WIDTHS:ram[a:a+2]=script.memory[a:a+2]
 assert ram==script.memory
 registers=[cpu.reg_read(r)for r in world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)];cpu.hook_del(code_hook);cpu.mem_write(STOP,b'\x40\xc7');cpu.emu_start(STOP,STOP+2,count=1);sr=cpu.reg_read(UC_M68K_REG_D7)&65535
 return {'registers':registers,'SR':sr,'PC':pc},len(steps)
def bind(lib):
 fn=lib.biwn_actor_task_run;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),W8,SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int;return fn
def translated(fn,script,case,budget=64,missing=None,null_bus=False,null_cpu=False,null_service=False,service_error=False,bad_return=False):
 def reader(w):
  def cb(_,a,v):
   try:v[0]=script.read(a,w);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def writer(w):
  def cb(_,a,v):
   try:script.write(a,w,v);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def service(_,bus,state,target):
  try:
   if service_error:return 1
   if bad_return:state.contents.registers[15]+=2;return 0
   args=[];off=state.contents.registers[15]+4
   for width in WIDTHS[target]:args.append(int.from_bytes(script.memory[off:off+width],'big'));off+=width
   state.contents.registers[0]=script.call(target,args,state.contents.registers[0]);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4))];
 if missing is not None and missing<5:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,world.CALL(),None,0);w8=W8()if missing==5 else W8(writer(1));cb=SERVICE()if null_service else SERVICE(service);cpu=CPU();cpu.registers[:]=case['registers'];cpu.registers[15]=SP;cpu.usp=SP;cpu.ssp=0x1d0000;cpu.sr=case['SR'];cpu.pc=case['PC'];status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(cpu),w8,cb,None,budget)
 return status,{'registers':list(cpu.registers),'SR':cpu.sr,'PC':cpu.pc},cpu

def cases():
 rng=random.Random(0xf4d8);rows=[]
 for i in range(512):
  slot=i%40;obj=0x49d6c+slot*206;record=0x120000;pc=[0xf4d8,0xf56e,0xf70c][i%3];kind=(i//3)%8;registers=[rng.getrandbits(32)for _ in range(16)];registers[10]=obj;registers[11]=0x13f7c;registers[12]=0x13f12;registers[7]=slot;registers[6]=(registers[6]&0xffff0000)|(1 if kind==7 else 0);registers[5]&=0xffff0000;registers[15]=SP
  initial=[[SP,4,STOP],[0xc0920,4,0xc1528],[0xc1528+30,4,slot],[obj+2,2,1 if i%17==0 else 0],[obj+44 if False else obj+68,4,record],[record,2,81 if kind==1 else 2],[obj+196,2,0 if kind in[0,7]else 1],[obj+110,1,rng.getrandbits(8)],[obj+111,1,[0,64,128,192,1,255][i%6]],[obj+8,2,[0,1,0xffff,0x7fff,0x8000][i%5]],[obj+4,4,rng.getrandbits(32)],[obj+10,4,rng.getrandbits(32)],[0x4c24c,4,[0,1,8,0xffffffff,0x80000000][i%5]]]
  left=[1]if kind==2 else [0,1,1]if kind==6 else [0];right=[1]if kind==3 else[0];front=[1]if kind in[5,6]else[0]
  if kind==7 and i%2==0:initial.append([obj+110,1,[0,64,128,192,1,255][i%6]])
  returns={str(0x1a77c):[i%4,0x12345678],str(0xf368):[rng.getrandbits(32),rng.getrandbits(32)],str(0x13f12):left,str(0x13f7c):right,str(0x13fea):front,str(0x13c9a):[rng.getrandbits(32)]}
  rows.append({'PC':pc,'SR':rng.randrange(32)|((i%8)<<8),'registers':registers,'initial':initial,'returns':returns,'default_helper_return':0,'helper_returns':{},'read_queues':[]})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-actor-task'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libactor-task.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_actor_task.c'),'-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases();vectors=vectors[:opt.limit]if opt.limit else vectors;coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});a=Script(snapshot,case);b=Script(snapshot,case);expected,steps=original(a,case,coverage);status,actual,cpu=translated(fn,b,case)
   if status!=(6 if expected['PC']==0xdf7a else 0)or expected!=actual or a.memory!=b.memory or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors,'RAM_diff':[hex(j)for j,(x,y)in enumerate(zip(a.memory,b.memory))if x!=y][:32]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'boundary':actual,'CPU_instructions':steps,'trace':b.trace,'full_registers_CCR_PC_stack_and_RAM_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','case':i,'error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);data=(session/'nextstage-68000-candidate.bin').read_bytes();decoded,_=world.select.binary_tools.m68k_instructions(data[0xf4d8-0x4000:0xf712-0x4000],0xf4d8);addresses={x['address']for x in decoded};unreachable={0xf528,0xf536};reachable=addresses-unreachable
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(coverage&addresses),len(addresses)]});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
 assert reachable<=coverage,[hex(x)for x in sorted(reachable-coverage)];guards=[]
 for case in[vectors[1],vectors[7]]:
  script=Script(snapshot,case);status,actual,cpu=translated(fn,script,case,budget=0);assert status==4;guards.append({'work_limit':True,'PC':hex(case['PC'])})
 for field in range(6):
  case=vectors[1];script=Script(snapshot,case);status,actual,cpu=translated(fn,script,case,missing=field);assert status==1 and not script.trace;assert actual=={'registers':case['registers'],'SR':case['SR'],'PC':case['PC']};guards.append({'missing_callback':field,'CPU_unchanged':True})
 for kw in[{'null_bus':True},{'null_cpu':True},{'null_service':True}]:
  case=vectors[1];script=Script(snapshot,case);status,actual,cpu=translated(fn,script,case,**kw);assert status==1 and not script.trace;assert actual=={'registers':case['registers'],'SR':case['SR'],'PC':case['PC']};guards.append({'arguments':kw,'CPU_unchanged':True})
 for kw,expected_status in[({'service_error':True},3),({'bad_return':True},5)]:
  case=vectors[3];script=Script(snapshot,case);status,actual,cpu=translated(fn,script,case,**kw);assert status==expected_status;assert actual=={'registers':case['registers'],'SR':case['SR'],'PC':case['PC']};guards.append({'arguments':kw,'CPU_unchanged':True,'partial_RAM_retained':True})
 for case in[{**vectors[1],'PC':0},{**vectors[1],'SR':0x2000}]:
  script=Script(snapshot,case);status,actual,cpu=translated(fn,script,case);assert status==1 and not script.trace;guards.append({'unsupported_entry_or_supervisor':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'actor_task_caller_matches_original_CPU_at_pending_yield_exit_boundaries','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'reachable_instruction_coverage':[len(reachable&coverage),len(reachable)],'unreachable_instructions':[hex(x)for x in sorted(unreachable)],'unreachable_reason':'After AND.L3,D0 the selector is0..3. The two default BRA instructionsF528/F536 cannot be reached; their conditional predecessors cover everypossible value.','original_interval':'[0xf4d8,0xf712)','getter_DFA6_locally_implemented':True,'host_guard_checks':len(guards),'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_actor_task.c','biwn_actor_task.h']},'pending_yield_cases':sum(r['boundary']['PC']==0xdf60 for r in rows),'pending_removal_cases':sum(r['boundary']['PC']==0xdf7a for r in rows),'helper_targets_scripted':[hex(a)for a in WIDTHS],'CPU_flags_observation':'Unicorn directSRread retained deferred flags. After taking the boundarysnapshot, MOVE.W SR,D7 (40c7) materializes CCR; capturedregisters/RAM precede the diagnostic instruction. Probe decode verified asM68000MOVE.WSR,D7.','matched':['All16registers, materializedfullSR/CCR, boundaryPC/SP, complete2MBRAM includingprivatecallee-save/argument/return frames, logicalhelpercalls/incomingD0 andexternalaccessorder match.','Initial entry, loop andpost-yield resumption; persistentturning/waypoint/retry/clamp state, invalidheading staleD3, allfourRNGvariants, turncompletion andpendingremoval covered.'],'limits':['SchedulerDF60 andremovalTRAP2 are pending boundaries, not executed in thisproof. Steering, waypoint, RNG andmovement helper bodies are scripted; onlyDFA6getter runsrealbody. No live actor behavior,task-ring integration orwholegame established.','Service contracts inthisproof setD0only andpreserve othercaller-savedregisters/SR. RealhelperCPUeffects andsourcehelperbodies needintegrationbeforea nativefullactor runtime claim.','Work bounds/errors arehostbehavior, not originalexceptions. No newcomponent addedtothepublic96checkpoint until task-ring and realhelper integration.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass_boundary_comparisons_integration_pending'});save(ROOT/'verification/biwn-actor-task-boundary-checks.json',report);print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':report['CPU_instruction_coverage'],'reachable':report['reachable_instruction_coverage'],'integration':'pending'}))
if __name__=='__main__':main()
