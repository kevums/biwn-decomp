"""Original CPU render dispatch/buffer rotation/clear submission versus portable C."""
import argparse,ctypes as c,json,random,subprocess,os,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
RANGES={0xe03a:0xe098,0x17e0e:0x17f14,0x17f14:0x17f68}
HELPERS=[0xe0a6,0xe0f2,0xe148,0xe19e,0xe202,0xe098,0x170a0,0x185b2]
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(boundary.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.mmio={};self.blit_reads=0;self.draws=0
 def read(self,a,w):
  if a==0xf02238:
   if self.fail_read==(a,w):raise RuntimeError('injected blitter read error')
   values=self.case['blitter_status'];v=values[min(self.blit_reads,len(values)-1)];self.blit_reads+=1;self.trace.append(['r',a,w,v]);return v
  return super().read(a,w)
 def write(self,a,w,v):
  if 0xf02200<=a<0xf02300:
   if self.fail_write==(a,w):raise RuntimeError('injected blitter write error')
   assert w==4;self.mmio[a]=v;self.trace.append(['w',a,w,v]);return
  super().write(a,w,v)
 def call(self,a,args,d0):
  if self.fail_call==a:raise RuntimeError('injected dependency failure')
  assert a in HELPERS;self.trace.append(['call',a,args]);self.changed=[]
  for target,address,width,value in self.case.get('helper_effects',[]):
   if target==a:self.put(address,width,value)
  if a==0x170a0:
   values=self.case['draw_counts'];self.put(0x49b88,4,values[min(self.draws,len(values)-1)]);self.draws+=1
  return self.case.get('helper_returns',{}).get(str(a),d0)&0xffffffff

def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(script.memory))
 args=b''.join(v.to_bytes(4,'big')for v in case.get('params',[]));cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 for target in HELPERS:cpu.mem_write(target,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in [0xe03a,0x17f14]and a!=case['entry']:
   stack=e.reg_read(UC_M68K_REG_A7);params=[int.from_bytes(e.mem_read(stack+4+i*4,4),'big')for i in range(2)]if a==0xe03a else[];script.trace.append(['call',a,params])
  if a in HELPERS:
   stack=e.reg_read(UC_M68K_REG_A7);params=[int.from_bytes(e.mem_read(stack+4+i*4,4),'big')for i in range(2)]if a==0x185b2 else[]
   d0=script.call(a,params,e.reg_read(UC_M68K_REG_D0))
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   e.reg_write(UC_M68K_REG_D0,d0);return
  assert any(lo<=a<hi for lo,hi in RANGES.items()),hex(a);steps.append(a);coverage.add(a)
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=100000,timeout=2000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if case['entry']==0xe03a or i not in [0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
 assert bytes(cpu.mem_read(SP+4,len(args)))==args
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 clear=lib.biwn_render_clear;clear.argtypes=[c.POINTER(world.Bus)]+[c.c_uint32]*3;clear.restype=c.c_int
 rotate=lib.biwn_render_rotate;rotate.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];rotate.restype=c.c_int
 scene=lib.biwn_render_scene;scene.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];scene.restype=c.c_int
 return clear,rotate,scene
def translated(functions,script,case,missing=None,budget=4096):
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
 def call(_,a,args,n,out):
  try:
   if script.fail_call==a:raise RuntimeError('injected dependency failure')
   values=list(args[:n])
   if a in[0xe03a,0x17f14]:
    script.trace.append(['call',a,values])
    if a==0xe03a:assert n==2;return functions[0](c.byref(bus),*values,budget)
    assert n==0;return functions[1](c.byref(bus),out[0],out)
   out[0]=script.call(a,values,out[0]);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a)
 if case['entry']==0xe03a:return functions[0](c.byref(bus),*case['params'],budget),case['incoming'][0]
 if case['entry']==0x17f14:status=functions[1](c.byref(bus),case['incoming'][0],c.byref(out))
 else:status=functions[2](c.byref(bus),budget,case['incoming'][0],c.byref(out))
 return status,out.value

def cases():
 rng=random.Random(0x17e0e);rows=[]
 for entry,n in [(0xe03a,128),(0x17f14,128),(0x17e0e,768)]:
  for i in range(n):
   case={'entry':entry,'incoming':[rng.getrandbits(32)for _ in world.REGS],'params':[rng.getrandbits(32),rng.getrandbits(32)]if entry==0xe03a else[],'initial':[],'default_helper_return':0,'blitter_status':[rng.choice([0,2,0xfffffffe])for _ in range(i%4)]+[rng.choice([1,3,0xffffffff])],'draw_counts':[i%3,0,17,0],'helper_returns':{str(0x170a0):rng.getrandbits(32),str(0x185b2):rng.getrandbits(32)},'read_queues':[]}
   for a in[0xbd830,0xbd834,0xbd838,0xbd83c,0xbd840,0xbd844,0x43daa]:case['initial'].append([a,4,rng.getrandbits(32)])
   if entry==0x17e0e:
    mode=[0,1,2,3,4,0xffff,0x8000][i%7];case['initial'] += [[0x49c60,2,mode],[0x49c76,2,[0,0x7fff,0x8000,0xffff][i%4]],[0x49b88,4,rng.getrandbits(32)],[0x10a684,4,0]]
    entries=i%5
    for j in range(entries):case['initial'] += [[0x10d688+j*8,4,rng.getrandbits(32)],[0x10d68c+j*8,4,rng.getrandbits(32)or 1]]
    case['initial'] += [[0x10d688+entries*8,4,0xffff],[0x10d68c+entries*8,4,0]]
    if i%3==0 and entries:case['initial'].append([0x10d68c+(entries-1)*8,4,0])
    if i%11==0:case['read_queues'].append({'address':0x49c60,'width':2,'values':[1,2,2]})
    if i%13==0:case['read_queues'].append({'address':0x49c60,'width':2,'values':[1,4,4,3]})
    case['read_queues'].append({'address':0x10a684,'width':4,'values':[1]*(i%4)+[0]})
   rows.append(case)
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-render-scene'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'librender-scene.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_render_scene.c'),'-o',str(library)];subprocess.run(cmd,check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});functions=bind(c.CDLL(str(library)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opts.limit:vectors=[vectors[i]for i in [0,1,127,128,255,256,257,258,259,260,261,262,267,269,270,300][:opts.limit]]
 rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});left=Script(snapshot,case);right=Script(snapshot,case);d0,instructions=original(left,case,coverage);status,result=translated(functions,right,case)
   if status or d0!=result or left.memory!=right.memory or left.trace!=right.trace or left.mmio!=right.mmio:
    save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_D0':d0,'C_D0':result,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'original_CPU_instructions':instructions,'full_D0':d0,'trace':right.trace,'whole_visible_RAM_and_MMIO_trace_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows)
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded={}
 for lo,hi in RANGES.items():
  instructions,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);decoded.update({(int(x['address'],16)if isinstance(x['address'],str)else x['address']):x for x in instructions})
 covered=set(decoded)&coverage;missing=sorted(set(decoded)-coverage)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(decoded)],'uncovered':[hex(x)for x in missing]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(decoded)],'uncovered':[hex(x)for x in missing]}));return
 assert not missing,[hex(x)for x in missing]
 guards=[]
 for entry,slots in [(0xe03a,[2,4]),(0x17f14,[2,4,5]),(0x17e0e,[1,2,4,5])]:
  case=next(x for x in vectors if x['entry']==entry)
  for slot in slots:
   script=Script(snapshot,case);status,result=translated(functions,script,case,missing=slot);assert status!=0;guards.append({'entry':hex(entry),'missing_callback':slot,'rejected':True})
 case=next(x for x in vectors if x['entry']==0xe03a);script=Script(snapshot,case);script.case={**case,'blitter_status':[0]};assert translated(functions,script,case,budget=3)[0]==4;guards.append({'bounded_blitter_busy':True})
 case=vectors[257]
 for failure in ['read','write','call']:
  script=Script(snapshot,case)
  if failure=='read':script.fail_read=(0x49c60,2)
  elif failure=='write':script.fail_write=(0x49b88,4)
  else:script.fail_call=0x17f14
  status,result=translated(functions,script,case);assert status and result==0xa55aa55a;guards.append({'failure':failure,'partial_effects_retained':True,'output_unchanged':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'render_scene_rotate_and_clear_original_CPU_match_C','directory':str(out),'CPU_cases':len(rows),'clear_cases':128,'rotate_cases':128,'scene_cases':768,'CPU_instruction_coverage':[len(covered),len(decoded)],'host_guards':len(guards),'portable_components':3,'original_bytes':sum(hi-lo for lo,hi in RANGES.items()),'intervals':{hex(lo):hex(hi)for lo,hi in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_render_scene.c','biwn_render_scene.h']},'nested_scripted_targets':[hex(a)for a in HELPERS],'matched':['Whole visible RAM, every read/write width/address/value/order, blitter MMIO writes, fullD0, callee saves, balanced stack and stack arguments.','Mode rereads, zero/one/two/three/other modes, signed region word, bounded paired-entry traversal/sentinels, draw-completion rereads and two triple-buffer rotations.','Original/C E03A clear submission and17F14rotation execute as nested real code in17E0E scene proof.'],'limits':['Eight GPU/scene/display-list dependency targets use declared scripts; no GPU, blitter rasterization, object processor, complete scene/viewport or game execution in this standalone proof.','Caller-saved registers other than fullD0, CCR, private stack, concurrency/hardware timing and arbitrary aliasing excluded. Host budgets/errors are added behavior.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-render-scene-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
