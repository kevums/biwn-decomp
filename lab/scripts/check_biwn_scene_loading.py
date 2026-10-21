"""Six scene loader/parsing bodies vs original CPU; explicit helper boundaries."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_startup_services as prior
world=prior.world;ROOT=prior.ROOT;SP=prior.SP;STOP=prior.STOP
RANGES={0x20aa0:0x20b2a,0x20b2a:0x20c16,0x20c16:0x20cc4,0x20cf8:0x20d7c,0x20d7c:0x20e40,0x20f78:0x21242}
WIDTHS={0x20aa0:[],0x20b2a:[4,4,2],0x20c16:[],0x20cf8:[4,4,2],0x20d7c:[],0x20f78:[2],0xe3e0:[4]*3,0x1ac68:[2],0x1ac3c:[2],0x13ae0:[2,4,2,4,2],0xe60a:[4,4],0xe588:[4,4],0x1b044:[4]*5,0x102c4:[4],0x10520:[4]}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(prior.Script):
 def call(self,target,args,incoming_D0):
  if self.fail_call==target:raise RuntimeError('injected dependency failure')
  self.trace.append(['call',target,args,incoming_D0])
  if target==0xe3e0 and args[2]<=256:
   for i in range(args[2]):self.put(args[1]+i,1,self.memory[args[0]+i])
  for a,w,v in self.case.get('helper_effects',{}).get(str(target),[]):self.put(a,w,v)
  if target==0x1ac3c:return 0xcafe0000|((args[0]+17)&65535)
  return self.case['helper_returns'].get(str(target),self.case['default_helper_return'])
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],WIDTHS[case['entry']]));cpu.mem_write(SP,STOP.to_bytes(4,'big')+params)
 for r,v in zip(world.REGS,case['incoming']):cpu.reg_write(r,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);stubs=[a for a in WIDTHS if a!=case['entry']]
 for a in stubs:cpu.mem_write(a,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in stubs:
   stack=e.reg_read(UC_M68K_REG_A7);args=[];offset=4
   for width in WIDTHS[a]:args.append(int.from_bytes(e.mem_read(stack+offset,width),'big'));offset+=width
   script.changed=[];d0=script.call(a,args,e.reg_read(UC_M68K_REG_D0))
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   e.reg_write(UC_M68K_REG_D0,d0);return
  assert any(lo<=a<hi for lo,hi in RANGES.items()),hex(a);coverage.add(a);steps.append(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+32:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+32:return
  script.write(a,w,v&((1<<(w*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=100000,timeout=5000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4,(hex(cpu.reg_read(UC_M68K_REG_PC)),hex(cpu.reg_read(UC_M68K_REG_A7)),len(steps),script.trace[-6:])
 assert all(cpu.reg_read(r)==case['incoming'][i]for i,r in enumerate(world.REGS)if i not in[0,1,8,9]);assert bytes(cpu.mem_read(SP+4,len(params)))==params
 ram=bytearray(cpu.mem_read(0,0x200000))
 for a in stubs:ram[a:a+2]=script.memory[a:a+2]
 assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+32:]==script.memory[SP+32:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 fn=lib.biwn_scene_loading;fn.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def translated(fn,script,case,budget=4096,missing=None,null_bus=False,null_out=False):
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
  try:assert n==len(WIDTHS[target]);out[0]=script.call(target,list(args[:n]),out[0]);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);args=(case['params']+[0]*3)[:3];status=fn(None if null_bus else c.byref(bus),case['entry'],*args,case['incoming'][0],budget,None if null_out else c.byref(out));return status,out.value
def cases():
 rng=random.Random(0x20f78);rows=[]
 for entry in RANGES:
  for i in range(256):
   src=0x110000;dst=0x120000;payload=0x170000;initial=[]
   def put(a,w,v):initial.append([a,w,v&((1<<(w*8))-1)])
   def block(a,n):
    for off in range(0,n,2):put(a+off,2,rng.getrandbits(16))
   block(src,256);block(dst,256);block(payload-32,256)
   for a in[0x15ece0,0x15ed46,0x15edac]:put(a,2,[0,1,2,3,0xffff,0x8000][i%6])
   for j in range(4):
    put(0x15ec7c+j*2,2,rng.getrandbits(16));put(0x15ed48+j*4,4,dst+j*256);put(dst+j*256+2,2,[0,1,2,0xffff][(i+j)%4]);put(dst+j*256+12,4,0x130000+j*256)
    for k in range(64):put(0x130000+j*256+k*2,2,rng.getrandbits(16))
    actor=0x140000+j*128;put(0x15ece2+j*4,4,actor);put(actor,2,[0,1,2,0xffff][(i+j)%4]);block(actor+2,96)
   put(0x49c18,4,dst);put(dst,2,[0,1,2,0xffff][i%4]);put(dst+4,4,0x130000)
   for j in range(25):put(0x49bb4+j*4,4,0x150000+j*540)
   for a in[0x49c50,0x49c56,0x49c6a,0x49c72]:put(a,4,rng.getrandbits(32))
   for a in[0x49c54,0x49c64,0x49c6c,0x49c74]:put(a,2,rng.getrandbits(16))
   put(0x49c60,2,[0,1,2,3,0xffff][i%5]);put(0x47b80,2,1)
   if entry==0x20b2a:
    put(src+6,2,[0,1,3,6,0xffff][i%5]);
    for j in range(4):put(src+8+j*2,2,[16,32,48,64][j])
   if entry==0x20cf8:
    put(src+4,4,32);put(src+8,4,64);put(src+2,2,[0,1,2,0xffff][i%4]);put(src+64+([0,1,2,-1][i%4])*6,2,[0,1,2,3,0xffff][i%5]);put(dst+64+([0,1,2,-1][i%4])*6,2,[0,1,2,3,0xffff][i%5])
   params=[src,dst,[16,32,96,128,0,15,0x8000][i%7]]if entry in[0x20b2a,0x20cf8]else[[0,1,2,3,0xffff][i%5]]if entry==0x20f78 else[]
   helper_returns={str(0x1b044):payload,str(0xe60a):i%5,str(0xe588):rng.getrandbits(32)}
   queues=[]
   if i%9==0 and entry in[0x20b2a,0x20cf8]:queues=[{'address':0x15ed46,'width':2,'values':[0xffff,2]}]
   rows.append({'entry':entry,'incoming':[rng.getrandbits(32)for _ in world.REGS],'params':params,'initial':initial,'default_helper_return':rng.getrandbits(32),'helper_returns':helper_returns,'read_queues':queues})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-scene-loading'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libscene-loading.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_scene_loading.c'),'-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opt.limit:vectors=[case for entry in RANGES for case in [x for x in vectors if x['entry']==entry][:opt.limit]]
 coverage=set();rows=[]
 try:
  for ordinal,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':ordinal,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);expected,steps=original(a,case,coverage);status,d0=translated(fn,b,case)
   if status or expected!=d0 or a.memory!=b.memory or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected_D0':expected,'C_D0':d0,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':ordinal,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':b.trace,'visible_RAM_access_order_calls_full_D0_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','case':ordinal,'entry':hex(case['entry']),'error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for lo,hi in RANGES.items():
  decoded,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);addresses.update(r['address']for r in decoded)
 covered=coverage&addresses
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(x)for x in sorted(addresses-coverage)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)]}));return
 assert addresses<=coverage, [hex(a)for a in sorted(addresses-coverage)];guards=[]
 for entry in RANGES:
  case=next(x for x in vectors if x['entry']==entry)
  for field in[1,2,3,4,5]:
   script=Script(snapshot,case);status,d0=translated(fn,script,case,missing=field);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':field})
  for kw in[{'null_bus':True},{'null_out':True}]:
   script=Script(snapshot,case);status,d0=translated(fn,script,case,**kw);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'arguments':kw})
 for entry in RANGES:
  case=next(x for x in vectors if x['entry']==entry and any(r[0]=='call'for r in rows[vectors.index(x)]['trace']))
  trace=rows[vectors.index(case)]['trace'];target=next(r[1]for r in trace if r[0]=='call');script=Script(snapshot,case);script.fail_call=target;status,d0=translated(fn,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'entry':hex(entry),'dependency_failure':hex(target),'partial_effects_retained':True})
  looping=next(x for x in vectors if x['entry']==entry and translated(fn,Script(snapshot,x),x,budget=0)[0]==4);script=Script(snapshot,looping);status,d0=translated(fn,script,looping,budget=0);assert status==4 and d0==0xa55aa55a;guards.append({'entry':hex(entry),'work_limit':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'six_scene_loading_bodies_original_CPU_and_C_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'new_components':6,'original_bytes':sum(b-a for a,b in RANGES.items()),'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in['biwn_scene_loading.c','biwn_scene_loading.h']},'nested_scripted_targets':[hex(a)for a in WIDTHS if a!=0x20f78],'RAM_sha256':hashlib.sha256(snapshot).hexdigest(),'matched':['Six complete scene caller/parsing bodies: raw signed-word loops and offsets, copied segment headers and pointer relocation, texture-reference lists/fixups, two actor record formats, both scene modes and full D0. Visible RAM, read/write width/order and logical helper arguments match original CPU.'],'limits':['Each source body is checked independently; all nested helper bodies are explicit scripts in this proof, including other members of this group. No actual disc/texture/actor creation or full startup is established here.','Private stack, CCR and caller-saved registers except D0 are excluded. Finite valid RAM fixtures and selected controlled rereads, not arbitrary aliasing/concurrency. Huge signed copy counts use helper-call contracts, not complete copies.','Host work bounds and errors retain prior effects and leave out_D0 unchanged; no original exception emulation.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-scene-loading-checks.json',report);print(json.dumps(report))
if __name__=='__main__':main()
