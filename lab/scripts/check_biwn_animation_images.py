"""Queue reset/consumer plus real CPU4B00 protocol on opaque MMIO replies."""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
import check_biwn_input_dispatch as dispatch
import check_biwn_gpu_commands as gpu
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
RANGES={0xea20:0xea28,0xea28:0xeac4}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(boundary.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.phase='pre';self.indices={};self.mmio={};self.calls=[]
 def begin(self,args):
  self.trace.append(['call',0xe2b8,args]);self.calls.append(args);self.phase='pre';self.indices={'pre':0,'ack':0,'post':0}
 def read(self,a,w):
  if a in[0xf03200,0xf03204]:
   if self.fail_read==(a,w):raise RuntimeError('injected MMIO read failure')
   assert w==4 and a==(0xf03204 if self.phase=='ack'else 0xf03200)
   values={'pre':[2,0],'ack':[0x4b00,0x4b00,self.case.get('ack',0xffffffff)],'post':[1,0]}[self.phase];n=self.indices[self.phase];v=values[n];self.indices[self.phase]+=1
   if self.phase=='ack'and v!=0x4b00:self.phase='post'
   self.trace.append(['r',a,w,v]);return v
  return super().read(a,w)
 def write(self,a,w,v):
  if 0xf03200<=a<0xf04000:
   if self.fail_write==(a,w):raise RuntimeError('injected MMIO write failure')
   assert w==4 and a in[0xf0320c,0xf03210,0xf03214,0xf03204];self.mmio[a]=v;self.trace.append(['w',a,w,v])
   if a==0xf03204:assert v==0x4b00 and self.phase=='pre';self.phase='ack'
  else:super().write(a,w,v)

def bind(lib):
 reset=lib.biwn_animation_images_reset;reset.argtypes=[c.POINTER(world.Bus)];reset.restype=c.c_int
 consume=lib.biwn_animation_images_consume;consume.argtypes=[c.POINTER(world.Bus),dispatch.W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];consume.restype=c.c_int
 return {0xea20:reset,0xea28:consume}
def protocol_function():
 report=json.loads((ROOT/'verification/biwn-gpu-commands-checks.json').read_text());fn=c.CDLL(str(Path(report['directory'])/'libbiwn_gpu_commands.dylib')).biwn_gpu_submit_4b00;fn.argtypes=[c.POINTER(gpu.Bus),c.c_uint32,c.c_uint32,c.c_uint32];fn.restype=c.c_int;return fn

def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
 for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[];sprite_d0=None
 def code(e,a,w,_):
  nonlocal sprite_d0
  assert 0xea20<=a<0xeac4 or 0xe2b8<=a<0xe2f4 or 0xe098<=a<0xe0a6,hex(a)
  if a==0xe2b8:
   stack=e.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(e.mem_read(stack+4+i*4,4),'big')for i in range(3)];script.begin(args);sprite_d0=e.reg_read(UC_M68K_REG_D0)
  if a==0xeaaa:assert e.reg_read(UC_M68K_REG_D0)==sprite_d0
  coverage.add(a);steps.append(a)
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=200000,timeout=2000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if case['entry']==0xea20 or i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
 ram=bytes(cpu.mem_read(0,0x200000));assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+8:]==script.memory[SP+8:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)

def translated(functions,protocol,script,case,missing=None,budget=64):
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
   assert a==0xe2b8 and n==3;values=list(args[:n]);script.begin(values)
   device=gpu.Bus(gpu.READ(cast_read),gpu.WRITE(cast_write),None,1000)
   return protocol(c.byref(device),*values)
  except Exception as error:script.errors.append(str(error));return 1
 def cast_read(_,a,v):
  try:v[0]=script.read(a,4);return 0
  except Exception as error:script.errors.append(str(error));return 1
 def cast_write(_,a,v):
  try:script.write(a,4,v);return 0
  except Exception as error:script.errors.append(str(error));return 1
 types=[world.R8,world.R16,world.R32,world.W16,world.W32,world.CALL,dispatch.W8];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](call),types[6](writer(1))]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=world.Bus(*callbacks[:6],None,0);out=c.c_uint32(0xa55aa55a)
 if case['entry']==0xea20:status=functions[0xea20](c.byref(bus));return status,case['incoming'][0]
 status=functions[0xea28](c.byref(bus),callbacks[6],budget,case['incoming'][0],c.byref(out));return status,out.value

def cases():
 rng=random.Random(0xea28);rows=[]
 for i in range(64):rows.append({'entry':0xea20,'kind':'reset','incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[[0x112940,2,rng.randrange(65536)]],'default_helper_return':0})
 for i in range(256):
  count=[0,1,2,3,39,40,0x7fff,0x8000,0xffff][i%9]
  # A positive extreme count is stopped by a controlled live reread after
  # one record. All source offsets remain finite declared memory fixtures.
  case={'entry':0xea28,'kind':'consume','incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[[0x112940,2,count]],'default_helper_return':0,'ack':[0,1,0xffffffff,0xdeadbeef][i%4]}
  if count==0x7fff:case['read_queues']=[{'address':0x112940,'width':2,'values':[0x7fff,1]}]
  for width in range(256):case['initial'].append([0x3bd20+width*4,4,rng.getrandbits(32)])
  for j in range(40):
   row=0x1126c0+j*16;model_handle=0x150000+j*4;output_handle=0x151000+j*4;model=0x130000+(j%4)*0x1000;output=0x90000+j*0x2000;frame=[0,1,2,0xffffffff,0x80000000,0x40000000,0x7fffffff][(i+j)%7];offset=0x100+(j%3)*0x100
   case['initial'] += [[row,4,model_handle],[row+4,4,frame],[row+8,4,output_handle],[row+12,4,[0,1,0x80000000,0xffffffff][(i+j)%4]],[model_handle,4,model],[output_handle,4,output],[(model+12+((frame<<2)&0xffffffff))&0xffffffff,4,offset],[model+offset,1,(i+j)%256],[model+offset+1,1,(255-i+j)%256]]
  if i%17==0:case['read_queues']=[{'address':0x112940,'width':2,'values':[1,3,3,3]}]
  if i%19==0:
   case.setdefault('read_queues',[]).append({'address':0x151000,'width':4,'values':[0x90000,0x92000]})
  rows.append(case)
 rows.append({'entry':0xea28,'kind':'checked_empty_preserves_D0','incoming':[0xabcd1234]+[0]*14,'initial':[[0x112940,2,0]],'default_helper_return':0})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-animation-images'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libanimation-images.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_animation_images.c'),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 functions=bind(c.CDLL(str(library)));protocol=protocol_function();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA
 for a,b in RANGES.items():assert snapshot[a:b]==image[a-0x4000:b-0x4000]
 vectors=cases();vectors=([x for x in vectors if x['entry']==0xea28][:opts.limit]+[x for x in vectors if x['entry']==0xea20][:opts.limit])if opts.limit else vectors;rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});a=Script(snapshot,case);b=Script(snapshot,case);d0,steps=original(a,case,coverage);status,result=translated(functions,protocol,b,case)
   if status or result!=d0 or a.trace!=b.trace or a.memory!=b.memory:
    save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':result,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':a.trace,'requests_consumed':len(a.calls),'whole_RAM_trace_and_register_contract_match':True})
 except Exception as error:save(out/'error-case.json',case);save(out/'status.json',{'status':'terminal_failed','case':i,'error':repr(error)});raise
 save(out/'fixtures.json',rows);decoded=[]
 for a,b in RANGES.items():part,_=world.select.binary_tools.m68k_instructions(snapshot[a:b],a);decoded+=part
 missing=[x for x in decoded if x['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing})
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'covered':len(decoded)-len(missing),'total':len(decoded),'directory':str(out)}));return
 assert not missing,[hex(x['address'])for x in missing]
 guards=[];dummy=world.Bus();output=c.c_uint32(0xa55aa55a);assert functions[0xea20](None)==1;assert functions[0xea28](None,dispatch.W8(),1,0,c.byref(output))==1 and output.value==0xa55aa55a;assert functions[0xea28](c.byref(dummy),dispatch.W8(),1,0,None)==1;guards += [{'null_argument':kind,'status':1}for kind in['reset_bus','consumer_bus','consumer_output']]
 reset_case=next(x for x in vectors if x['entry']==0xea20);script=Script(snapshot,reset_case);status,d0=translated(functions,protocol,script,reset_case,missing=3);assert status==1 and not script.trace;guards.append({'reset_missing_write':True,'status':1})
 case=next(row['parameters']for row in rows if row['requests_consumed']>=2)
 for missing_callback in range(7):
  script=Script(snapshot,case);status,d0=translated(functions,protocol,script,case,missing=missing_callback);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'missing_callback':missing_callback,'status':1})
 for budget,expected in[(0,1),(1,4)]:
  script=Script(snapshot,case);status,d0=translated(functions,protocol,script,case,budget=budget);assert status==expected and d0==0xa55aa55a;guards.append({'work_budget':budget,'status':status,'partial_effects':script.trace})
 for action,width in[('r',1),('r',2),('r',4),('w',1),('w',2),('w',4)]:
  row=next(x for x in rows if x['parameters']['entry']==0xea28 and any(t[0]==action and t[2]==width and t[1]<0x200000 for t in x['trace']));event=next(t for t in row['trace']if t[0]==action and t[2]==width and t[1]<0x200000);script=Script(snapshot,row['parameters']);setattr(script,'fail_read'if action=='r'else'fail_write',(event[1],width));status,d0=translated(functions,protocol,script,row['parameters']);assert status==2 and d0==0xa55aa55a;guards.append({'bus_error':[action,event[1],width],'status':2})
 script=Script(snapshot,case);script.fail_call=0xe2b8;status,d0=translated(functions,protocol,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'sprite_dependency_error':True,'status':3})
 script=Script(snapshot,case);script.fail_read=(0xf03200,4);status,d0=translated(functions,protocol,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'sprite_MMIO_failure':True,'status':3})
 save(out/'guards.json',guards);assert rows[-1]['full_D0']==0xabcd1234
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'queue_reset_consumer_and_CPU_sprite_protocol_match_C','directory':str(out),'CPU_cases':len(rows),'reset_cases':64,'consumer_cases':257,'CPU_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'portable_components':2,'original_bytes':164,'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'stage_sha256':world.select.stage.STAGE_SHA,'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in['biwn_animation_images.c','biwn_animation_images.h']},'compiler':command,'matched':['Complete reset/consumer functions, full consumerD0 and resetallregisterpreservation, callee-saved registers, balanced RTSstack andwholevisibleRAM.','Every external read/write width/address/value/order plus actual E2B8/E098 CPUmailbox protocol, orderedparameters andD0preservation on both original/C paths.','Signed livequeuecount, index/handle/width rereads, packedwidth/height, nonzero flipbit31, pitchtablelookup, dynamic queue growth/shrink and finalqueue reset.'],'limits':['Opaque scripted MMIO responses, not GPU decoding or full animation rendering in this standalone proof.','Finite supplied model/frame/outputhandle data and controlled rereads. Arbitrary aliases/concurrency, fullCCR/caller-savedregisterABI, hardwaretiming and complete game excluded.','Added hostworkbudget/callbackerrors retain partialwrites and preserve outputD0 on failure.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-animation-images-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
