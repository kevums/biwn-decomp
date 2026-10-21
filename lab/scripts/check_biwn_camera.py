"""Camera, signed multiply and table direction versus unchanged original CPU."""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
import check_biwn_input_dispatch as dispatch
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
RANGES={0xe540:0xe588,0x13440:0x134dc,0xf0fa:0xf35e,0xe588:0xe60a};WIDTHS={0xe540:[4,4],0x13440:[2,2],0xe588:[4,4],0xe220:[4]*5}
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
class Script(boundary.Script):
 def call(self,a,args):
  if self.fail_call==a:raise RuntimeError('injected dependency failure')
  self.trace.append(['call',a,args]);assert a==0xe220
  for target,address,width,value in self.case.get('helper_effects',[]):
   if target==a:self.put(address,width,value)
  return 0

def original(script,case,coverage,instruction_limit=10000):
 entry=case['entry'];cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(0xe220,b'\x4e\x75')
 args=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],WIDTHS.get(entry,[])));cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,v in zip(world.REGS,case['incoming']):cpu.reg_write(reg,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
 def code(e,a,w,_):
  if a in WIDTHS and a!=entry:
   stack=e.reg_read(UC_M68K_REG_A7);offset=4;values=[]
   for width in WIDTHS[a]:values.append(int.from_bytes(e.mem_read(stack+offset,width),'big'));offset+=width
   if a==0xe220:
    script.changed=[];value=script.call(a,values)
    for address,width,value2 in script.changed:e.mem_write(address,value2.to_bytes(width,'big'))
    e.reg_write(UC_M68K_REG_D0,value);return
   script.trace.append(['call',a,values])
  assert any(start<=a<end for start,end in RANGES.items()),hex(a);steps.append(a);coverage.add(a)
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(entry,STOP,count=instruction_limit,timeout=2000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
 assert bytes(cpu.mem_read(SP+4,len(args)))==args
 ram=bytearray(cpu.mem_read(0,0x200000));ram[0xe220:0xe222]=script.memory[0xe220:0xe222];assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+16:]==script.memory[SP+16:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)

def bind(lib):
 mul=lib.biwn_multiply32;mul.argtypes=[c.c_uint32,c.c_uint32];mul.restype=c.c_uint32
 direction=lib.biwn_camera_direction;direction.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];direction.restype=c.c_int
 camera=lib.biwn_camera_update;camera.argtypes=[c.POINTER(world.Bus),dispatch.W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];camera.restype=c.c_int
 return {0xe540:mul,0x13440:direction,0xf0fa:camera}
def translated(functions,division,script,case,missing=None):
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
   values=list(args[:n])
   if script.fail_call==a:raise RuntimeError('injected dependency failure')
   if a==0xe220:result[0]=script.call(a,values);return 0
   script.trace.append(['call',a,values])
   if a==0xe540:result[0]=functions[a](*values);return 0
   if a==0xe588:remainder=c.c_uint32();return division(*values,result,c.byref(remainder))
   if a==0x13440:return functions[a](c.byref(bus),*values,result[0],result)
   raise AssertionError(hex(a))
  except Exception as error:script.errors.append(str(error));return 1
 types=[world.R8,world.R16,world.R32,world.W16,world.W32,world.CALL,dispatch.W8];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](call),types[6](writer(1))]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=world.Bus(*callbacks[:6],None,0);out=c.c_uint32(0xa55aa55a);entry=case['entry']
 if entry==0xe540:return 0,functions[entry](*case['params'])
 if entry==0x13440:status=functions[entry](c.byref(bus),*case['params'],case['incoming'][0],c.byref(out))
 else:status=functions[entry](c.byref(bus),callbacks[6],case['incoming'][2],case['incoming'][3],c.byref(out))
 return status,out.value

def cases():
 rng=random.Random(0xf0fa);rows=[];longs=[0,1,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffffff,0x80000000,0x80000001,0xffff0000,0xffffffff];words=[0,1,2,59,60,61,119,120,121,255,256,0x3fff,0x4000,0x7fff,0x8000,0x8001,0xfffe,0xffff]
 def make(entry,params,kind):return{'entry':entry,'params':params,'kind':kind,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[],'default_helper_return':0}
 for i in range(2048):rows.append(make(0xe540,[longs[i//len(longs)]if i<len(longs)**2 else rng.getrandbits(32),longs[i%len(longs)]if i<len(longs)**2 else rng.getrandbits(32)],'multiply'))
 for i in range(1024):rows.append(make(0x13440,[words[i//len(words)]if i<len(words)**2 else rng.randrange(65536),words[i%len(words)]if i<len(words)**2 else rng.randrange(65536)],'direction'))
 for i in range(768):
  case=make(0xf0fa,[],'camera_debug'if i<256 else'camera_normal');held=(0x80|((i&255)<<16)|(i%16))if i<256 else rng.getrandbits(32)&0xffffff7f
  case['initial']=[[0x49ba4,4,held],[0x49cba,1,i%256],[0x3c840,2,words[i%len(words)]],[0x3c842,4,rng.choice(longs)],[0x3c846,4,rng.choice(longs)],[0x49b98,4,rng.choice(longs)],[0x49b9c,4,rng.choice(longs)],[0x49ba0,4,rng.choice(longs)],[0x49cc0,4,rng.choice(longs)]]
  for a in[0x49cd8,0x49cdc,0x49cde,0x49ce0,0x49ce2,0x47b9c,0x49b8e]:case['initial'].append([a,2,rng.choice(words)])
  if i%17==0:case['helper_effects']=[[0xe220,0x3c846,4,0x80000000+i]]
  if i%19==0:case['read_queues']=[{'address':0x3c842,'width':4,'values':[1,0xffffffff]},{'address':0x49cba,'width':1,'values':[i%256,(255-i)%256]}]
  rows.append(case)
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-camera'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcamera.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_camera.c'),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 functions=bind(c.CDLL(str(library)));dr=json.loads((ROOT/'verification/biwn-signed-division-checks.json').read_text());division=c.CDLL(str(Path(dr['directory'])/'libdivision.dylib')).biwn_signed_division;division.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];division.restype=c.c_int
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA
 for a,b in RANGES.items():assert snapshot[a:b]==image[a-0x4000:b-0x4000]
 vectors=cases()
 if opts.limit:vectors=[x for x in vectors if x['entry']==0xf0fa][:opts.limit]+[x for x in vectors if x['entry']==0x13440][:opts.limit]+[x for x in vectors if x['entry']==0xe540][:opts.limit]
 coverage=set();rows=[]
 for i,case in enumerate(vectors):
  save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);d0,steps=original(a,case,coverage);status,result=translated(functions,division,b,case)
  if status or result!=d0 or a.trace!=b.trace or a.memory!=b.memory:
   save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':result,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
  rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':a.trace,'whole_RAM_trace_stack_and_callee_save_match':True})
 save(out/'fixtures.json',rows);decoded=[]
 for a,b in RANGES.items():
  if a==0xe588:continue
  part,_=world.select.binary_tools.m68k_instructions(snapshot[a:b],a);decoded+=part
 missing=[x for x in decoded if x['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing})
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'covered':len(decoded)-len(missing),'total':len(decoded),'directory':str(out)}));return
 assert[hex(x['address'])for x in missing]==['0x134be']
 # D3 is assigned quadrant1..4 on all source paths; the checked E588
 # helper preserves D3. The final unmatched-quadrant BRA is unreachable
 # under the routine's own contract. Do not fabricate a register clobber.
 guards=[]
 dummy=world.Bus();out_d0=c.c_uint32(0xa55aa55a)
 assert functions[0x13440](None,0,0,0,c.byref(out_d0))==1 and out_d0.value==0xa55aa55a
 assert functions[0x13440](c.byref(dummy),0,0,0,None)==1
 assert functions[0xf0fa](None,dispatch.W8(),0,0,c.byref(out_d0))==1 and out_d0.value==0xa55aa55a
 assert functions[0xf0fa](c.byref(dummy),dispatch.W8(),0,0,None)==1
 guards += [{'null_bus_or_output':kind,'status':1}for kind in['direction_bus','direction_output','camera_bus','camera_output']]
 for entry,required in[(0x13440,[2,5]),(0xf0fa,list(range(7)))]:
  case=next(x for x in vectors if x['entry']==entry)
  for callback in required:
   script=Script(snapshot,case);status,d0=translated(functions,division,script,case,missing=callback);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':callback,'status':1})
 for target in WIDTHS:
  case=next(row['parameters']for row in rows if any(t[:2]==['call',target]for t in row['trace']));script=Script(snapshot,case);script.fail_call=target;status,d0=translated(functions,division,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'failed_dependency':hex(target),'status':3})
 for action in['r','w']:
  for width in[1,2,4]:
   row=next(x for x in rows if any(t[0]==action and t[2]==width for t in x['trace']));entry=next(t for t in row['trace']if t[0]==action and t[2]==width);case=row['parameters'];script=Script(snapshot,case);setattr(script,'fail_read'if action=='r'else'fail_write',(entry[1],width));status,d0=translated(functions,division,script,case);assert status==2 and d0==0xa55aa55a;guards.append({'failed_bus':[action,entry[1],width],'status':2})
 save(out/'guards.json',guards)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'camera_multiply_direction_match_original_CPU','directory':str(out),'CPU_cases':len(rows),'multiply_cases':2048,'direction_cases':1024,'camera_cases':768,'CPU_instruction_coverage':[len(decoded)-len(missing),len(decoded)],'reachable_instruction_coverage':[len(decoded)-len(missing),len(decoded)-len(missing)],'unreachable_instructions':['0x134be'],'unreachable_basis':'D3 is assigned exactly1..4 on all quadrant paths; original division preserves D3; each allowed quadrant branches before the unmatched-quadrant fallback BRA134BE.','host_guards':len(guards),'portable_components':3,'intervals':{hex(a):hex(b)for a,b in RANGES.items()if a!=0xe588},'original_bytes':72+156+612,'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in['biwn_camera.c','biwn_camera.h']},'stage_sha256':world.select.stage.STAGE_SHA,'compiler':command,'matched':['All reachable instructions in complete multiply, table-direction and camera routines; fullD0, callee-saved registers, balanced stack/untouched args and whole visible RAM.','Every external read/write address/width/value/order and nested call target/stack args/order. Original multiply/direction/signed-division execute, C counterparts are linked; E220 mailbox submit remains scripted in this standalone run.','Raw32multiply overflow; signed/unsigned direction scan/quadrants including signedword extremes and zeroZ upperD0 preservation; camera debug control wrap, signed counters, both averaging branches and changing rereads/helper effects.'],'limits':['F0FA is an analyst-labelled camera update, correcting the older terrain label. Shared final3C846read is its return; normalpath writes27, helper effects/debugpath may change that.','Camera debugpath uses lowword incomingD2/D3. Fullcaller-saved register/CCR ABI, asynchronous aliases and hardware timing excluded.','E220 is an explicit scripted dependency here; GPU movement and world runtime integration not proved by this standalone check. No complete game frames.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-camera-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
