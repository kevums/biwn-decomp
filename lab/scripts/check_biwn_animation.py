"""Original animation advance and request queue versus linked portable C."""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
RANGES={0xeac4:0xeb04,0xeb04:0xec04};OBJECT=0x80000;CURRENT=0x84000;PENDING=0x90000
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(boundary.Script):pass

def bind(lib):
 queue=lib.biwn_animation_enqueue;queue.argtypes=[c.POINTER(world.Bus)]+[c.c_uint32]*5+[c.POINTER(c.c_uint32)];queue.restype=c.c_int
 update=lib.biwn_animation_update;update.argtypes=[c.POINTER(world.Bus)]+[c.c_uint32]*3+[c.POINTER(c.c_uint32)];update.restype=c.c_int
 return {0xeac4:queue,0xeb04:update}

def original(script,case,coverage):
 entry=case['entry'];cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));args=b''.join(v.to_bytes(4,'big')for v in case['params']);cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
 def code(e,a,w,_):
  assert any(start<=a<end for start,end in RANGES.items()),hex(a)
  if a==0xeac4 and entry!=a:
   stack=e.reg_read(UC_M68K_REG_A7);values=[int.from_bytes(e.mem_read(stack+4+i*4,4),'big')for i in range(4)];script.trace.append(['call',a,values])
  coverage.add(a);steps.append(a)
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+24:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+24:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(entry,STOP,count=200000,timeout=2000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4,{'PC':hex(cpu.reg_read(UC_M68K_REG_PC)),'SP':hex(cpu.reg_read(UC_M68K_REG_A7)),'timer':int.from_bytes(script.memory[OBJECT+0x62:OBJECT+0x64],'big')}
 for i,reg in enumerate(world.REGS):
  if i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
 assert bytes(cpu.mem_read(SP+4,len(args)))==args
 ram=bytes(cpu.mem_read(0,0x200000));assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+24:]==script.memory[SP+24:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)

def translated(functions,script,case,missing=None,budget=512):
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
 def call(_,a,args,n,result):
  try:
   if script.fail_call==a:raise RuntimeError('injected dependency failure')
   assert a==0xeac4 and n==4;values=list(args[:n]);script.trace.append(['call',a,values]);return functions[a](c.byref(bus),*values,result[0],result)
  except Exception as error:script.errors.append(str(error));return 1
 types=[world.R8,world.R16,world.R32,world.W16,world.W32,world.CALL];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](call)]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);entry=case['entry']
 if entry==0xeac4:status=functions[entry](c.byref(bus),*case['params'],case['incoming'][0],c.byref(out))
 else:status=functions[entry](c.byref(bus),*case['params'],case['incoming'][0],budget,c.byref(out))
 return status,out.value

def cases():
 rng=random.Random(0xeb04);rows=[]
 def make(entry,kind):return{'entry':entry,'kind':kind,'params':[],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[],'default_helper_return':0}
 counts=[0,1,38,39,40,41,0x7fff,0x8000,0xfffe,0xffff]
 for i in range(512):
  case=make(0xeac4,'queue');case['params']=[rng.getrandbits(32)for _ in range(4)];case['initial']=[[0x112940,2,counts[i%len(counts)]]]
  if i%19==0:case['read_queues']=[{'address':0x112940,'width':2,'values':[39,40,0xffff]}]
  rows.append(case)
 words=[0,1,2,3,127,128,255,0x7fff,0x8000,0x8001,0xfffe,0xffff];steps=[0,1,0xff,127,128]
 for i in range(1024):
  case=make(0xeb04,'new_sequence'if i%3==0 else'advance');case['params']=[OBJECT];index=rng.choice([0,1,2,3,0x7fff,0x8000,0xfffe,0xffff]);new=i%3==0;step=steps[i%len(steps)];offset=(step if step<128 else step-256)*4;target=CURRENT+offset;pending_index=(index if index<0x8000 else(-index)&0xffff);signed_index=pending_index if pending_index<0x8000 else pending_index-65536;new_pointer=PENDING+signed_index*4-4
  case['initial']=[[OBJECT+0x68,4,PENDING if new else 0],[OBJECT+0x64,4,CURRENT],[OBJECT+0xca,2,index],[OBJECT+0x62,2,rng.choice(words)],[OBJECT+0xcc,2,rng.choice([0,1,0xffff])],[OBJECT+0x58,4,rng.getrandbits(32)],[OBJECT+0x5e,4,rng.getrandbits(32)],[0x4c24e,2,rng.choice(words)],[0x112940,2,rng.choice(counts)]]
  frame=rng.choice([0,1,0x7f,0x80,0xff]);next_frame=frame if i%2 else(frame+1)&255;duration=127
  rng.choice([1,2,127]) # Retain deterministic later samples from the first fixture set.
  case['initial'] += [[CURRENT,1,frame],[CURRENT+1,1,127],[CURRENT+3,1,step],[target,1,next_frame],[target+1,1,duration],[target+3,1,0]]
  # For nonzero steps, restore the first record's relative step, then
  # optionally traverse a negative-duration record before a finite terminal.
  if offset:case['initial'].append([CURRENT+3,1,step])
  if offset and i%5==0:
   terminal=target+508;case['initial'] += [[target+1,1,128],[target+3,1,127],[terminal,1,0x80],[terminal+1,1,127],[terminal+3,1,0]]
  if new:case['initial'] += [[new_pointer,1,frame],[new_pointer+1,1,rng.choice([0,1,127,128,255])],[new_pointer+3,1,0]]
  if i%17==0:case['read_queues']=[{'address':OBJECT+0xca,'width':1,'values':[0xff,0]},{'address':OBJECT+0x58,'width':4,'values':[0xabcdef01,0x12345678]}]
  rows.append(case)
 # Exact checked contract examples independent of C implementation.
 case=make(0xeac4,'checked_full_queue');case['params']=[1,2,3,4];case['incoming'][0]=0xabcd1234;case['initial']=[[0x112940,2,40]];rows.append(case)
 case=make(0xeb04,'checked_noop_countdown');case['params']=[OBJECT];case['incoming'][0]=0xabcd0063;case['initial']=[[OBJECT+0x68,4,0],[OBJECT+0x62,2,10],[OBJECT+0xcc,2,0],[0x4c24e,2,3]];rows.append(case)
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-animation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libanimation.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_animation.c'),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 functions=bind(c.CDLL(str(library)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA
 for a,b in RANGES.items():assert snapshot[a:b]==image[a-0x4000:b-0x4000]
 vectors=cases()
 if opts.limit:vectors=[x for x in vectors if x['entry']==0xeb04][:opts.limit]+[x for x in vectors if x['entry']==0xeac4][:opts.limit]
 coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});a=Script(snapshot,case);b=Script(snapshot,case);d0,steps=original(a,case,coverage);status,result=translated(functions,b,case)
   if status or result!=d0 or a.trace!=b.trace or a.memory!=b.memory:
    save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':result,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':a.trace,'whole_RAM_trace_stack_and_callee_save_match':True})
 except Exception as error:save(out/'error-case.json',case);save(out/'status.json',{'status':'terminal_failed','case':i,'error':repr(error)});raise
 save(out/'fixtures.json',rows);decoded=[]
 for a,b in RANGES.items():part,_=world.select.binary_tools.m68k_instructions(snapshot[a:b],a);decoded+=part
 missing=[x for x in decoded if x['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing})
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'covered':len(decoded)-len(missing),'total':len(decoded),'directory':str(out)}));return
 assert not missing,[hex(x['address'])for x in missing]
 guards=[];dummy=world.Bus();out_d0=c.c_uint32(0xa55aa55a)
 for entry in functions:
  args=[1,2,3,4,0]if entry==0xeac4 else[OBJECT,0,1]
  assert functions[entry](None,*args,c.byref(out_d0))==1 and out_d0.value==0xa55aa55a
  assert functions[entry](c.byref(dummy),*args,None)==1;guards += [{'null_argument':hex(entry),'kind':kind,'status':1}for kind in['bus','output']]
  case=next(x for x in vectors if x['entry']==entry)
  for callback in([1,3,4]if entry==0xeac4 else range(6)):
   script=Script(snapshot,case);status,d0=translated(functions,script,case,missing=callback);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':callback,'status':1})
 for action,width,entry in[('r',1,0xeb04),('r',2,0xeac4),('r',4,0xeb04),('w',2,0xeac4),('w',4,0xeac4)]:
  row=next(x for x in rows if x['parameters']['entry']==entry and any(t[0]==action and t[2]==width for t in x['trace']));event=next(t for t in row['trace']if t[0]==action and t[2]==width);case=row['parameters'];script=Script(snapshot,case);setattr(script,'fail_read'if action=='r'else'fail_write',(event[1],width));status,d0=translated(functions,script,case);assert status==2 and d0==0xa55aa55a;guards.append({'bus_failure':[action,event[1],width],'status':2})
 row=next(x for x in rows if any(t[:2]==['call',0xeac4]for t in x['trace']));case=row['parameters'];script=Script(snapshot,case);script.fail_call=0xeac4;status,d0=translated(functions,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'queue_dependency_error':True,'status':3})
 case=next(x for x in vectors if x['entry']==0xeb04);script=Script(snapshot,case);status,d0=translated(functions,script,case,budget=0);assert status==1 and not script.trace;guards.append({'zero_work_budget':True,'status':1})
 case={'entry':0xeb04,'params':[OBJECT],'incoming':[0]*len(world.REGS),'initial':[[OBJECT+0x68,4,0],[OBJECT+0x64,4,CURRENT],[OBJECT+0x62,2,0],[OBJECT+0xcc,2,0],[0x4c24e,2,0],[CURRENT,1,0],[CURRENT+1,1,0],[CURRENT+3,1,0]]};script=Script(snapshot,case);status,d0=translated(functions,script,case,budget=2);assert status==4 and d0==0xa55aa55a and script.trace;guards.append({'nonprogressing_sequence_budget':2,'status':4,'partial_effects_retained':script.trace})
 save(out/'guards.json',guards);examples=[{'kind':row['parameters']['kind'],'full_D0':hex(row['full_D0']),'trace':row['trace']}for row in rows if row['parameters']['kind'].startswith('checked_')];assert[x['full_D0']for x in examples]==['0xabcd0000','0xabcd0007'];save(ROOT/'verification/animation-checked-examples.json',examples)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'complete_animation_update_and_queue_match_original_CPU','directory':str(out),'CPU_cases':len(rows),'queue_cases':sum(x['parameters']['entry']==0xeac4 for x in rows),'update_cases':sum(x['parameters']['entry']==0xeb04 for x in rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'portable_components':2,'original_bytes':320,'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'stage_sha256':world.select.stage.STAGE_SHA,'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in['biwn_animation.c','biwn_animation.h']},'compiler':command,'matched':['Both complete original CPU functions, full D0, preserved callee registers, private RTS stack/arguments and whole visible RAM.','Every external memory read/write width/address/value/order and actual nested EAC4 call arguments/order; queue implementation linked on both original/C paths.','Signed byte frame/duration/relative steps, word-wrap countdown catch-up, same-frame suppression, dirty retry after rejected queue, signed queue counts and rereads; CLR.W rejection preserves upperD0.'],'limits':['Queue consumer, model/pose processing, full actor lifecycle, main loop, physicalhardware and complete game are outside this standalone proof.','Added host callback errors/work budget retain prior effects and preserve output on failure. Original infinite animation loops are not assigned a completed result.','Finite supplied record/data layouts and controlled rereads; arbitrary aliases/asynchronous updates and fullCCR/caller-saved register ABI excluded.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-animation-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
