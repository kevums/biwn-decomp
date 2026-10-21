"""Full181F8 overlay: original CPU bus trace/calls/fullD0 versus C."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_render_scene as scene
world=scene.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP;SCRATCH=SP-54
WIDTHS={0x1b45a:[4,4,2,2,2],0x149ae:[2,2,4,4,4,4,2,2]}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(scene.Script):
 def call(self,a,args,d0):
  if self.fail_call==a:raise RuntimeError('injected dependency failure')
  assert a in WIDTHS;self.trace.append(['call',a,args]);self.changed=[]
  if a==0x1b45a:
   for i,v in enumerate(b' fixture\x00'):self.put(args[0]+i,1,v)
  return self.case['helper_returns'][str(a)]
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
 for reg,v in zip(world.REGS,case['incoming']):cpu.reg_write(reg,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 for a in WIDTHS:cpu.mem_write(a,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in WIDTHS:
   sp=e.reg_read(UC_M68K_REG_A7);offset=4;args=[]
   for width in WIDTHS[a]:args.append(int.from_bytes(e.mem_read(sp+offset,width),'big'));offset+=width
   d0=script.call(a,args,e.reg_read(UC_M68K_REG_D0))
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   e.reg_write(UC_M68K_REG_D0,d0);return
  assert 0x181f8<=a<0x18554,hex(a);coverage.add(a);steps.append(a)
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x181f8,STOP,count=2000,timeout=1000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 f=lib.biwn_overlay;f.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];f.restype=c.c_int;return f
def translated(fn,script,case,missing=None,null_out=False):
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
  try:out[0]=script.call(a,list(args[:n]),out[0]);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);status=fn(c.byref(bus),SCRATCH,case['incoming'][0],None if null_out else c.byref(out));return status,out.value

def cases():
 rng=random.Random(0x181f8);rows=[];edge16=[0,1,7,8,15,16,0x7fff,0x8000,0xffff];edge32=[0,63,64,0x7fffffff,0x80000000,0xffffffff,0x12345678,0xfedcba98]
 for i in range(1024):
  x=edge32[i%8]if i<64 else rng.getrandbits(32);z=edge32[i//8%8]if i<64 else rng.getrandbits(32);sector=[0,1,0x7fff,0x8000,0xffff][i%5];cx=(x>>6)&0xffff;cz=(z>>6)&0xffff;cache_sector=sector
  if i%4==1:cx^=1
  elif i%4==2:cz^=1
  elif i%4==3:cache_sector^=1
  case={'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[[0x4451c,2,i%2],[0x44518,2,edge16[i%9]],[0x4451a,2,edge16[i//9%9]],[0x49d6a,2,edge16[i//3%9]],[0x49d68,2,edge16[i//7%9]],[0x49d5c,2,(i//2)%2],[0x49d5e,2,(i//4)%2],[0x113060,2,(i//8)%2],[0x49cba,1,i%256],[0x49c50,4,x],[0x49c56,4,z],[0x49c62,2,sector],[0x4451e,2,cx],[0x44520,2,cz],[0x44522,2,cache_sector]],'default_helper_return':0,'blitter_status':[1],'draw_counts':[0],'helper_returns':{str(a):rng.getrandbits(32)for a in WIDTHS},'read_queues':[]}
  if i%17==0:case['read_queues'].append({'address':0x49d6a,'width':2,'values':[0x7fff,0x8000]})
  if i%19==0:case['read_queues'].append({'address':0x49d68,'width':2,'values':[0x10,0xffff]})
  if i%23==0:case['read_queues'].append({'address':0x49c50,'width':4,'values':[x,x^0x80000000]})
  if i%29==0:case['read_queues'].append({'address':0x49c56,'width':4,'values':[z,z^0x80000000]})
  if i%31==0:case['read_queues'].append({'address':0x49c62,'width':2,'values':[sector,sector^0x8000]})
  if i%37==0:case['read_queues'].append({'address':0x44522,'width':2,'values':[cache_sector,0xffff]})
  rows.append(case)
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-overlay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'liboverlay.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_overlay.c'),'-o',str(library)];subprocess.run(cmd,check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=bind(c.CDLL(str(library)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases();vectors=vectors[:opts.limit]if opts.limit else vectors;coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});a=Script(snapshot,case);b=Script(snapshot,case);d0,steps=original(a,case,coverage);status,result=translated(fn,b,case)
   if status or result!=d0 or a.trace!=b.trace or a.memory!=b.memory or a.mmio!=b.mmio:
    save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_D0':d0,'C_D0':result,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':b.trace,'whole_visible_RAM_MMIO_and_dependency_calls_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded,_=world.select.binary_tools.m68k_instructions(image[0x181f8-0x4000:0x18554-0x4000],0x181f8);addresses={x['address']if isinstance(x['address'],int)else int(x['address'],16)for x in decoded};covered=addresses&coverage;missing=addresses-coverage
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(missing)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(missing)]}));return
 assert not missing
 guards=[];case=vectors[1]
 for missing_callback in range(6):
  status,result=translated(fn,Script(snapshot,case),case,missing=missing_callback);assert status==1 and result==0xa55aa55a;guards.append({'missing_callback':missing_callback,'rejected':True})
 assert translated(fn,Script(snapshot,case),case,null_out=True)[0]==1;guards.append({'null_output':True})
 for failure in ['read8','read16','read32','write16','write32','formatter','text']:
  script=Script(snapshot,case)
  if failure.startswith('read'):script.fail_read={'read8':(0x49cba,1),'read16':(0x4451c,2),'read32':(0x49c50,4)}[failure]
  elif failure.startswith('write'):script.fail_write={'write16':(0x44518,2),'write32':(0xf02200,4)}[failure]
  else:script.fail_call=0x1b45a if failure=='formatter'else 0x149ae
  status,result=translated(fn,script,case);assert status and result==0xa55aa55a;guards.append({'failure':failure,'output_unchanged':True,'partial_effects_retained':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'full_overlay_original_CPU_matches_C','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'portable_components':1,'original_bytes':0x18554-0x181f8,'original_interval':'[0x181f8,0x18554)','source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_overlay.c','biwn_overlay.h']},'nested_scripted_targets':['0x1b45a','0x149ae'],'matched':['Full function, every RAM/MMIOread/write width/address/value/order, exact logical formatter/text args, fullD0/callee saves/balanced stack.','Old marker clearing/new marker placement with packedY plus signed doubledX and original rereads, colorselector, staticlabelonce, lowbyte gauge offset.','Signed32ASR6 coordinates/lowword cache comparison, changed-coordinate rereads, signed sector format choice and later sector reread, unchanged-coordinate return and text result.'],'limits':['Standalone device submissions only; blitter rasterization, formatter/text implementation and GPU/OP/hardware timing not executed here. Both nested dependencies use declared scripts.','Scratch buffer explicitly maps original entrySP-54; source private stack/CCR/caller-saved registers exceptfullD0 and arbitrary aliases/concurrency excluded. Added host errors retain earlier effects.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-overlay-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
