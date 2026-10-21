"""Seven startup bodies vs original CPU; nested resource/scene calls explicit."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
RANGES={0xe2f4:0xe300,0x18160:0x181da,0x21242:0x212e8,0x18ba8:0x18df2,0xdfc0:0xdff4,0x1aeda:0x1af04,0xf0c0:0xf0fa}
WIDTHS={0x1aa40:[2],0x1af04:[2],0x152a2:[4],0xdf6c:[4,4],0x1b786:[],0x18888:[],0x20f78:[2],0x11e6c:[],0x1aeda:[],0xea20:[],0xf0c0:[],0xe4c0:[]}
STUBS=[0x1aa40,0x1af04,0x152a2,0xdf6c,0x1b786,0x18888,0x20f78,0x11e6c]
W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(boundary.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.MMIO={};self.padrow=0
 def read(self,a,w):
  if a<0x200000:return super().read(a,w)
  if self.fail_read==(a,w):raise RuntimeError('injected MMIO read failure')
  assert a==0xf14000 and w==4;v=self.case['pad_rows'][self.padrow];self.padrow+=1;self.trace.append(['r',a,w,v]);return v
 def write(self,a,w,v):
  if a<0x200000:return super().write(a,w,v)
  if self.fail_write==(a,w):raise RuntimeError('injected MMIO write failure')
  assert 0xf00000<=a<0xf20000
  for i,b in enumerate(v.to_bytes(w,'big')):self.MMIO[a+i]=b
  self.trace.append(['w',a,w,v])
 def call(self,target,args):
  assert target in STUBS
  if self.fail_call==target:raise RuntimeError('injected dependency failure')
  self.trace.append(['call',target,args])
  for a,w,v in self.case.get('helper_effects',{}).get(str(target),[]):self.put(a,w,v)
  return self.case['helper_returns'].get(str(target),self.case['default_helper_return'])
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf00000,0x20000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
 for r,v in zip(world.REGS,case['incoming']):cpu.reg_write(r,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 for a in STUBS:cpu.mem_write(a,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in WIDTHS and a!=case['entry']:
   stack=e.reg_read(UC_M68K_REG_A7);args=[];offset=4
   for width in WIDTHS[a]:args.append(int.from_bytes(e.mem_read(stack+offset,width),'big'));offset+=width
   if a in STUBS:
    script.changed=[];d0=script.call(a,args)
    for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
    e.reg_write(UC_M68K_REG_D0,d0);return
   script.trace.append(['call',a,args])
  assert any(lo<=a<hi for lo,hi in RANGES.items())or 0xe4c0<=a<0xe53c or 0xea20<=a<0xea28,hex(a)
  coverage.add(a);steps.append(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  script.write(a,w,v&((1<<(w*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=20000,timeout=3000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 assert all(cpu.reg_read(r)==case['incoming'][i]for i,r in enumerate(world.REGS)if i not in[0,1,8,9])
 ram=bytearray(cpu.mem_read(0,0x200000))
 for target in STUBS:ram[target:target+2]=script.memory[target:target+2]
 assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+16:]==script.memory[SP+16:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 fn=lib.biwn_startup_service;fn.argtypes=[c.POINTER(world.Bus),W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
 poll=lib.biwn_input_poll;poll.argtypes=[c.POINTER(world.Bus)];poll.restype=c.c_int
 reset=lib.biwn_animation_images_reset;reset.argtypes=[c.POINTER(world.Bus)];reset.restype=c.c_int
 return fn,poll,reset
def translated(bindings,script,case,missing=None,null_bus=False,null_out=False):
 fn,poll,reset=bindings
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
 def call(_,target,args,n,out):
  try:
   values=list(args[:n]);assert n==len(WIDTHS[target])
   if script.fail_call==target:raise RuntimeError('injected dependency failure')
   if target in STUBS:out[0]=script.call(target,values);return 0
   script.trace.append(['call',target,values])
   if target==0xe4c0:return poll(c.byref(bus))
   if target==0xea20:return reset(c.byref(bus))
   assert target in [0x1aeda,0xf0c0];return fn(c.byref(bus),w8,target,out[0],out)
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)];w8=W8(writer(1))
 if missing==6:w8=W8()
 elif missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);status=fn(None if null_bus else c.byref(bus),w8,case['entry'],case['incoming'][0],None if null_out else c.byref(out))
 return status,out.value

def cases():
 rng=random.Random(0x18ba8);rows=[]
 for entry in RANGES:
  for i in range(256 if entry in[0x18ba8,0xdfc0]else 128):
   model_handle=0x110000+(i%64)*4;model=0x160000+(i%64)*0x100;out_handle=0x111000+(i%64)*4;output=0x170000+(i%64)*0x100;position=(i%21)-10;item=(i%15)-7;maxpixels=rng.randrange(1,16000)
   initial=[[model_handle,4,model],[model+8,4,maxpixels],[out_handle,4,output],[0x45d9a,2,rng.randrange(65536)],[0x49ba4,4,rng.getrandbits(32)],[0x45e30+position*20+item*4,4,rng.getrandbits(32)]]
   rows.append({'entry':entry,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'default_helper_return':rng.getrandbits(32),'helper_returns':{str(0x1af04):model_handle,str(0x152a2):out_handle},'helper_effects':{str(0x152a2):[[0x49c4c,2,position&65535],[0x49d5a,2,item&65535]]},'read_queues':([{'address':0x49c4c,'width':2,'values':[position&65535,((position+1)%11)&65535]}]if i%7==0 and entry==0x18ba8 else[]),'pad_rows':([0xffffffff]*4 if i%2 else [rng.getrandbits(32)for _ in range(4)])})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-startup-services'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_startup_services.c','biwn_input_poll.c','biwn_animation_images.c'];lib=out/'libstartup-services.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr)
 if p.returncode:save(out/'status.json',{'status':'terminal_compile_failed'});raise RuntimeError(str(out/'compile.log'))
 functions=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opts.limit:vectors=[case for entry in RANGES for case in [x for x in vectors if x['entry']==entry][:opts.limit]]
 coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);original_d0,steps=original(a,case,coverage);status,d0=translated(functions,b,case)
   if status or original_d0!=d0 or a.memory!=b.memory or a.MMIO!=b.MMIO or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'original_D0':original_d0,'C_D0':d0,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':b.trace,'visible_RAM_MMIO_writes_and_bus_order_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for lo,hi in RANGES.items():
  decoded,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);addresses.update(x['address']for x in decoded)
 covered=coverage&addresses
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(x)for x in sorted(addresses-coverage)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)]}));return
 assert addresses<=coverage
 needed={0xe2f4:[4],0x18160:[3,4],0x21242:[3,4,5],0x18ba8:[1,2,3,4,5,6],0xdfc0:[2,3,5],0x1aeda:[3],0xf0c0:[3,4]};guards=[]
 for entry,fields in needed.items():
  case=next(x for x in vectors if x['entry']==entry)
  for field in fields:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,missing=field);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':field})
  for kwargs in [{'null_bus':True},{'null_out':True}]:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,**kwargs);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'arguments':kwargs})
 for target in [0x1af04,0x152a2,0xdf6c,0x1b786,0x18888,0x1aa40,0x20f78]:
  case=next(x for x in vectors if x['entry']==0x18ba8);script=Script(snapshot,case);script.fail_call=target;status,d0=translated(functions,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'dependency_failure':hex(target),'partial_effects_retained':True})
 for entry,a,w in [(0xe2f4,0x10a680,4),(0x18160,0xf00402,2),(0x18ba8,0x49cbb,1)]:
  case=next(x for x in vectors if x['entry']==entry);script=Script(snapshot,case);script.fail_write=(a,w);status,d0=translated(functions,script,case);assert status==2 and d0==0xa55aa55a;guards.append({'write_failure':[hex(a),w]})
 case={**vectors[0],'entry':0};script=Script(snapshot,case);status,d0=translated(functions,script,case);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'unsupported_entry':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'seven_startup_services_original_CPU_and_C_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'portable_components':7,'original_bytes':sum(b-a for a,b in RANGES.items()),'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'nested_scripted_targets':[hex(a)for a in STUBS],'real_nested_helpers':['0x1aeda','0xf0c0','0xea20','0xe4c0'],'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'RAM_sha256':hashlib.sha256(snapshot).hexdigest(),'matched':['Seven complete source bodies; visible RAM, MMIO write width/address/value/order, logical helper calls, full D0, callee saves and return stack match original CPU.','25 object pointers, two 40-entry resets, 50 resource records, player globals and model/output handle rereads, actual nested reset/input-poll bodies; 18BA8 task creation request is [18B86,1388].'],'limits':['Eight nested resource/allocator/task/scene services are explicitly scripted in this standalone proof, including DF6C (already checked separately). Not whole startup, resource loading or game execution.','MMIO is a declared trace fixture without actual hardware side effects. Original private stack, caller-saved registers except D0 and CCR are excluded. Connected native hardware/CPU integration is a separate proof.','Host callback errors retain prior effects and leave output unchanged. Finite valid RAM/handles; no arbitrary aliasing or concurrency claim.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-startup-services-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
