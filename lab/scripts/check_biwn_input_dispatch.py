"""Complete 13-state CPU dispatcher versus logical C, explicit helper boundaries."""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
HELPERS=[0x190bc,0xe4c0,0x1a0f8,0xeb04,0xdf60,0x1b002,0x1af04,0x1545c,0x152a2,0x1aade,0xdf22,0x11e6c,0x18160,0x1aa40,0x1ab2a,0xdf3e,0x18e92,0x18df2,0xe588]
WIDTHS={0xeb04:[4],0x1b002:[2],0x1af04:[2],0x1545c:[4],0x152a2:[4],0x1aa40:[2],0x1ab2a:[4],0xe588:[4,4]}
W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
class Script(boundary.Script):
 def __init__(self,snapshot,case):
  super().__init__(snapshot,case);self.calls={}
 def call(self,address,args):
  if self.fail_call==address:raise RuntimeError('injected dependency error')
  assert address in HELPERS;self.trace.append(['call',address,args]);n=self.calls.get(address,0);self.calls[address]=n+1
  if address==0xe4c0:
   values=self.case.get('poll_values',[0x10000000]);self.put(0x49ba4,4,values[min(n,len(values)-1)])
  if address==0xeb04:
   values=self.case.get('animation_flags',[1]);self.put(0x90002,1,values[min(n,len(values)-1)])
  for target,a,w,v in self.case.get('helper_effects',[]):
   if target==address:self.put(a,w,v)
  return self.case['helper_returns'][str(address)]
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
 for reg,v in zip(world.REGS,case['incoming']):cpu.reg_write(reg,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 for target in HELPERS:cpu.mem_write(target,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in HELPERS:
   stack=e.reg_read(UC_M68K_REG_A7);offset=4;args=[]
   for width in WIDTHS.get(a,[]):args.append(int.from_bytes(e.mem_read(stack+offset,width),'big'));offset+=width
   script.changed=[];result=script.call(a,args)
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   e.reg_write(UC_M68K_REG_D0,result);return
  assert 0x191f4<=a<0x19f2c,hex(a);coverage.add(a);steps.append(a)
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
 cpu.emu_start(0x191f4,STOP,count=20000,timeout=1000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i],i
 ram=bytearray(cpu.mem_read(0,0x200000))
 for target in HELPERS:ram[target:target+2]=script.memory[target:target+2]
 assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+8:]==script.memory[SP+8:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def translated(fn,script,case,missing=None,budget=64):
 def reader(width):
  def cb(_,a,v):
   try:v[0]=script.read(a,width);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def writer(width):
  def cb(_,a,v):
   try:script.write(a,width,v);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def call(_,a,args,count,result):
  try:result[0]=script.call(a,list(args[:count]));return 0
  except Exception as error:script.errors.append(str(error));return 1
 types=[world.R8,world.R16,world.R32,world.W16,world.W32,world.CALL,W8]
 callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](call),types[6](writer(1))]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=world.Bus(*callbacks[:6],None,0);out=c.c_uint32(0xa5a55a5a)
 status=fn(c.byref(bus),callbacks[6],budget,case['incoming'][0],c.byref(out));return status,out.value

def cases(snapshot):
 rng=random.Random(0x191f4);rows=[]
 def make(state,held,kind):
  counter=rng.choice([0,1,6,7,8,255,256,0x7fff,0x8000,0xffff]);actor=rng.choice([0,1,2,0xffff]);slot=rng.choice([0,1,2,4,0xffff]);index=rng.choice([0,1,9,0xffff]);item=rng.choice([0x41,0x42,0x43,0x44,0x45,0x46,0x66,0,0xffff])
  case={'kind':kind,'state':state,'held':held,'incoming':[rng.getrandbits(32)for _ in world.REGS],
   'initial':[[0x4624a,2,rng.choice([0,1])],[0x4624c,2,counter],[0x4624e,2,counter],[0x46250,2,rng.choice([0,1,2,300,0x7fff,0x8000,0xffff])],[0x49d62,2,rng.choice([0,1,0x7fff,0x8000,0xffff])],[0x4c24c,4,rng.choice([0,1,30,0x10000,0x1ffff,0x7fffffff,0x80000000,0xffffffff,rng.getrandbits(32)])],[0x49c4c,2,actor],[0x49c4e,2,0],[0x49d5a,2,slot],[0x49cb8,2,state],[0x49ba4,4,held],[0x49c60,2,0],[0x49c78,4,0x90100],[0x90100,2,0xffff],[0x49cb0,4,0x90000],[0x90002,1,rng.choice([0,1,2,3,0xff])],[0x49cc4,4,rng.getrandbits(32)],[0x49cc8,4,rng.getrandbits(32)],[0x49cba,1,rng.randrange(256)],[0x49d54,2,index],[0x49d2c+(index if index<0x8000 else index-65536)*2,2,item],[0x461be+(item if item<0x8000 else item-65536),1,rng.choice([0,0,1,2,4,0xff])],[0x49ca4,4,0x91000],[0x91000,4,0x92000],[0x92008,4,0x80],[0x49caa,4,0x93000],[0x93000,4,0x94000]],
   'helper_returns':{str(a):rng.getrandbits(32)for a in HELPERS},'animation_flags':[0,0,1],
   'default_helper_return':0}
  case['helper_returns'].update({str(0x1af04):0x91000,str(0x152a2):0x93000,str(0x1aade):0x95000})
  for a in[0x49ccc,0x49cce,0x49cd0,0x49cde,0x49ce0,0x49ce2,0x49d14]:case['initial'].append([a,2,rng.choice([0,1,0x3fff,0x4000,0x7fff,0x8000,0xbfff,0xc000,0xffff])])
  return case
 # Cross every state with individual raw bits and mixed combinations.
 for state in range(13):
  for held in[0,0xffffffff]+[1<<bit for bit in range(32)]+[rng.getrandbits(32)for _ in range(94)]:rows.append(make(state,held,'state_bit_matrix'))
 for state in[13,0x7fff,0x8000,0xffff]:
  for _ in range(16):rows.append(make(state,rng.getrandbits(32),'out_of_range_state'))
 # Force every equipment path; no expectation is computed from the C logic.
 for item in[0,0x41,0x42,0x43,0x44,0x45,0x46,0x66,0xffff]:
  for mode in[1,2]:
   case=make(1,0x02002000,'equipment_item');case['initial'] += [[0x49d5a,2,0],[0x49d54,2,0],[0x49d2c,2,item],[0x461be+(item if item<0x8000 else item-65536),1,0],[0x49c60,2,mode]]
   rows.append(case)
 for slot in[0,1,2,4,0xffff]:
  for byte in[0,1,2,4,0xff]:
   case=make(1,0x02002000,'equipment_slot');case['initial'] += [[0x49d5a,2,slot],[0x49d54,2,0],[0x49d2c,2,0x70],[0x4622e,1,byte]];rows.append(case)
 for timer in[0,1,0x7fff,0x8000,0xffff]:
  case=make(1,0,'idle_poll_wait');case['initial'] += [[0x49c60,2,2],[0x90100,2,0x8000],[0x46250,2,timer]];case['poll_values']=[0,0x00100000,0,0x10000000];rows.append(case)
 # Explicit acceleration boundaries: add before signed clamp, including wrap.
 for state in[1,5,7,8,10]:
  for right in[False,True]:
   for counter in[0,6,7,8,255,256,0x7fff,0x8000,0xffff]:
    held=(0x00400000 if right else 0x00800000)|{1:0,5:0x00100000,7:0x00200000,8:0x00102000,10:0x02200000}[state]
    case=make(state,held,'turn_boundary');case['initial'] += [[0x4624a,2,1],[0x4624c,2,counter],[0x4624e,2,counter]];rows.append(case)
 # Rereads deliberately change after the first access, identically in both paths.
 for address,width,values in[(0x49d62,2,[1,0x8000]),(0x49c4e,2,[1,0xffff]),(0x49ba5,1,[0x10,0x40,0x80]),(0x49d5a,2,[1,2]),(0x49d2c,2,[0x41,0x44,0x45,0x46])]:
  case=make(1,0x02002000,'changing_reread');case['initial'] += [[0x49d5a,2,0],[0x49d54,2,0],[0x49d2c,2,0x41],[0x461ff,1,0]]
  case['read_queues']=[{'address':address,'width':width,'values':values}];rows.append(case)
 for slot in[0,1]:
  case=make(1,0x02002000,'helper_mutated_equipment');case['initial'] += [[0x49d5a,2,slot],[0x49d54,2,0],[0x49d2c,2,0x70],[0x4622e,1,2]]
  case['helper_effects']=[[0x1b002,0x49c4c,2,2],[0x1af04,0x49caa,4,0x93000]];rows.append(case)
 for counter in[7,0xffff]:
  case=make(1,0x00400000,'checked_turn_example');case['initial'] += [[0x4624a,2,1],[0x4624e,2,counter],[0x49cba,1,250]];rows.append(case)
 case=make(5,0x00100000,'checked_fraction_argument');case['initial'] += [[0x4c24c,4,0x1ffff],[0x49cc8,4,0]];case['helper_returns'][str(0xe588)]=0;rows.append(case)
 case=make(5,0x00100000,'fraction_post_helper_reread');case['helper_effects']=[[0xe588,0x49cc8,4,0x89abcdef]];rows.append(case)
 # Explicit interrupted-motion reset and changing reread values.
 for state in range(13):
  case=make(state,rng.getrandbits(32),'pending_motion');case['initial'].append([0x49c4e,2,rng.choice([1,0xffff,0x8000])]);rows.append(case)
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();out=ROOT/'verification/biwn-input-dispatch'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libdispatch.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_input_dispatch.c'),'-o',str(library)]
 run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 fn=c.CDLL(str(library)).biwn_input_dispatch;fn.argtypes=[c.POINTER(world.Bus),W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
 session=__import__('pathlib').Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes()
 assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA
 assert snapshot[0x191f4:0x19f2c]==image[0x191f4-0x4000:0x19f2c-0x4000]
 vectors=cases(snapshot)
 if args.limit:vectors=vectors[:args.limit]
 coverage=set();rows=[]
 for i,case in enumerate(vectors):
  save(out/'status.json',{'status':'running','case':i});a=Script(snapshot,case);b=Script(snapshot,case);d0,steps=original(a,case,coverage);status,result=translated(fn,b,case)
  if status or result!=d0 or a.trace!=b.trace or a.memory!=b.memory:
   save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':result,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
  rows.append({'case':i,'parameters':case,'full_D0':d0,'original_steps':steps,'trace':a.trace,'whole_RAM_trace_and_callee_save_match':True})
 save(out/'fixtures.json',rows)
 decoded=[]
 for start,end in[(0x191f4,0x192a2),(0x192bc,0x19f2c)]:part,_=world.select.binary_tools.m68k_instructions(snapshot[start:end],start);decoded+=part
 missing=[x for x in decoded if x['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing})
 if args.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'covered':len(coverage),'total':len(decoded),'directory':str(out)}));return
 guards=[];assert fn(None,W8(),1,0,c.byref(c.c_uint32()))==1;guards.append({'null_bus':True,'status':1})
 dummy=world.Bus();assert fn(c.byref(dummy),W8(lambda *args:0),1,0,None)==1;guards.append({'null_output':True,'status':1})
 case=vectors[0];s=Script(snapshot,case);s.put(0x192a2,2,0xffff);status,d0=translated(fn,s,case);assert status==5 and d0==0xa5a55a5a;guards.append({'unsupported_jump_table':True,'status':5,'partial_effects':s.trace})
 for missing_callback in range(7):
  s=Script(snapshot,vectors[0]);status,d0=translated(fn,s,vectors[0],missing=missing_callback);assert status==1 and d0==0xa5a55a5a and not s.trace;guards.append({'missing_callback':missing_callback,'status':status})
 s=Script(snapshot,vectors[0]);status,d0=translated(fn,s,vectors[0],budget=0);assert status==1 and not s.trace;guards.append({'zero_budget':True,'status':1})
 for target in HELPERS:
  hit=next((x for x in rows if any(t[0]=='call'and t[1]==target for t in x['trace'])),None)
  assert hit is not None,hex(target)
  case=hit['parameters'];s=Script(snapshot,case);s.fail_call=target;status,d0=translated(fn,s,case);assert status==3 and d0==0xa5a55a5a;guards.append({'helper_failure':hex(target),'status':status,'partial_effects':s.trace})
 for width in[1,2,4]:
  for action in['r','w']:
   hit=next(x for x in rows if any(t[0]==action and t[2]==width for t in x['trace']));entry=next(t for t in hit['trace']if t[0]==action and t[2]==width);case=hit['parameters'];s=Script(snapshot,case);setattr(s,'fail_read'if action=='r'else'fail_write',(entry[1],width));status,d0=translated(fn,s,case);assert status==2 and d0==0xa5a55a5a;guards.append({'bus_failure':[action,hex(entry[1]),width],'status':status,'partial_effects':s.trace})
 for kind in['idle_poll_wait','equipment_slot']:
  hit=next(x for x in rows if x['parameters']['kind']==kind and any(t[0]=='call'and t[1]in[0xe4c0,0xeb04]for t in x['trace']));case=hit['parameters'];s=Script(snapshot,case);status,d0=translated(fn,s,case,budget=1);assert status==4 and d0==0xa5a55a5a;guards.append({'loop_budget':kind,'status':4,'partial_effects':s.trace})
 save(out/'guards.json',guards);assert not missing,[hex(x['address'])for x in missing]
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'complete_original_CPU_input_dispatch_matches_C','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage),len(decoded)],'host_guards':len(guards),'portable_components':1,'interval':'[0x191f4,0x19f2c)','original_bytes':0x19f2c-0x191f4,'jump_table_bytes':26,'stage_sha256':world.select.stage.STAGE_SHA,'state_count':13,'helper_targets':[hex(x)for x in HELPERS],'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in['biwn_input_dispatch.c','biwn_input_dispatch.h']},'compiler':command,'matched':['Complete original caller with all 13 states, full D0, original callee-saved registers and balanced private stack.','Every external RAM read/write width/address/value/order, all helper target/stack arguments/order and full visible RAM.','Signed countdowns, pre-clamp turn byte, signed animation/equipment indices, equipment/transition dependency calls, word-truncated fractional movement, repeated polling/animation waits.'],'limits':['All 19 nested helper targets are identical scripted RTS dependencies in this standalone proof; helpers themselves not proved by this run.','Original immutable jump table only. No arbitrary alias/asynchronous changes, full CCR or other caller-saved registers, hardware timing or physical controller proof.','Added host loop budgets/callback errors preserve prior effects and leave output D0 unchanged.','Not yet connected to the existing three-task runtime; no complete rebuilt game frames executed.']}
 examples=[]
 for row in rows:
  if row['parameters']['kind']not in['checked_turn_example','checked_fraction_argument']:continue
  a=Script(snapshot,row['parameters']);d0,steps=original(a,row['parameters'],set());b=Script(snapshot,row['parameters']);status,result=translated(fn,b,row['parameters']);assert not status and d0==result and a.trace==b.trace
  if row['parameters']['kind']=='checked_turn_example':
   counter=next(v for address,w,v in row['parameters']['initial'][::-1]if address==0x4624e)
   expected=(2,7)if counter==7 else(250,0)
   angle=a.memory[0x49cba];after=int.from_bytes(a.memory[0x4624e:0x46250],'big');assert(angle,after)==expected
   examples.append({'kind':'turn_before_clamp','previous_counter':counter,'previous_angle_byte':250,'new_angle_byte':angle,'stored_counter':after,'previous_turn_flag':1,'original_and_C_match':True})
  else:
   call=next(t for t in a.trace if t[:2]==['call',0xe588]);assert call[2]==[0xffe80000,300]
   examples.append({'kind':'fraction_argument','clock_long':'0x0001ffff','state':5,'scale':3,'division_numerator':'0xffe80000','division_denominator':300,'division_result_is_scripted_in_this_standalone_check':True,'original_and_C_match':True})
 save(out/'checked-examples.json',examples);save(ROOT/'verification/input-dispatch-checked-examples.json',examples)
 report['checked_examples']=str(out/'checked-examples.json')
 save(out/'status.json',{'status':'terminal_pass'});save(out/'report.json',report);save(ROOT/'verification/biwn-input-dispatch-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
