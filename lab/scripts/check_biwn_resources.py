"""Resource/cache/stream/texture caller bodies vs original CPU, explicit helpers."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP;SCRATCH=SP-8
RANGES={0x1af04:0x1b002,0x1b002:0x1b044,0x1b044:0x1b154,0x1aa40:0x1aade}
WIDTHS={0x152a2:[4],0x1b044:[4]*5,0xdf8c:[4],0xdf9c:[4],0x1545c:[4],0xdf60:[],0xd206:[4,4],0xd2f0:[4]*3,0xd306:[],0xe3e0:[4]*3}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(boundary.Script):
 def __init__(self,snapshot,case):
  super().__init__(snapshot,case);self.bulk=[];self.attempts=0;self.progress_reads=0;self.waits=0
 def read(self,a,w):
  if SP-0x1000<=a<SP+32:return int.from_bytes(self.memory[a:a+w],'big')
  if self.case['entry']==0x1b044 and a==0xbd848 and w==4:
   end=0x1c8000+self.case['params'][3];values=([end]if self.case['progress_kind']==0 else[0,end]if self.case['progress_kind']==1 else[0,end-4,end]);self.put(a,w,values[min(self.progress_reads,len(values)-1)]);self.progress_reads+=1
  return super().read(a,w)
 def write(self,a,w,v):
  if SP-0x1000<=a<SP+32:self.put(a,w,v);return
  return super().write(a,w,v)
 def call(self,target,args):
  if self.fail_call==target:raise RuntimeError('injected dependency failure')
  self.trace.append(['call',target,args]);case=self.case
  if target==0x152a2:return 0 if case.get('allocation_fails')else case['allocated_handle']
  if target==0x1b044:
   if args[4]:self.put(args[4],2,1)
   if case.get('raise_ref'):self.put(args[4]-2,2,2)
   if case.get('reread_handle'):self.put(args[4]-6,4,0xabcdef10)
  elif target==0xdf8c:
   self.waits+=1
   if self.waits>=case['waits_until_ready']:self.put(case['ready_address'],2,1)
  elif target==0x1545c:
   if args[0]:self.put(args[0],4,0)
  elif target==0xd2f0:
   start,end,_=args;assert start==0x1c0000 and end==0x1c8000+case['params'][3];size=end-start;payload=bytearray(b'\xa5'*size);spec=case['stream_specs'][min(self.attempts,len(case['stream_specs'])-1)];tag=case['params'][1].to_bytes(4,'big')
   for position,count in spec:payload[position:position+count*4]=tag*count
   self.memory[start:start+len(payload)]=payload;self.bulk.append((start,bytes(payload)));self.attempts+=1;self.progress_reads=0
  elif target==0xe3e0:
   source,destination,size=args;payload=bytes(self.memory[source:source+size]);self.memory[destination:destination+size]=payload;self.bulk.append((destination,payload))
  return case['default_helper_return']
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));widths=[2]if case['entry']in[0x1af04,0x1b002,0x1aa40]else[4]*5;args=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],widths));cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);stubs=[a for a in WIDTHS if a!=case['entry']]
 for a in stubs:cpu.mem_write(a,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in stubs:
   stack=e.reg_read(UC_M68K_REG_A7);offset=4;values=[]
   for width in WIDTHS[a]:values.append(int.from_bytes(e.mem_read(stack+offset,width),'big'));offset+=width
   script.changed=[];script.bulk=[];d0=script.call(a,values)
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   for address,payload in script.bulk:e.mem_write(address,payload)
   e.reg_write(UC_M68K_REG_D0,d0);return
  assert any(lo<=a<hi for lo,hi in RANGES.items()),hex(a);coverage.add(a);steps.append(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+32:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=250000,timeout=5000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 assert all(cpu.reg_read(r)==case['incoming'][i]for i,r in enumerate(world.REGS)if i not in[0,1,8,9])
 assert bytes(cpu.mem_read(SP+4,len(args)))==args
 ram=bytearray(cpu.mem_read(0,0x200000))
 for a in stubs:ram[a:a+2]=script.memory[a:a+2]
 assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+32:]==script.memory[SP+32:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 signatures={0x1af04:('biwn_resource_get',[c.c_uint16,c.c_uint32]),0x1b002:('biwn_resource_release',[c.c_uint16,c.c_uint32]),0x1b044:('biwn_resource_load',[c.c_uint32]*6),0x1aa40:('biwn_resource_textures',[c.c_uint16,c.c_uint32])};functions={}
 for entry,(name,args)in signatures.items():fn=getattr(lib,name);fn.argtypes=[c.POINTER(world.Bus)]+args+[c.POINTER(c.c_uint32)];fn.restype=c.c_int;functions[entry]=fn
 return functions
def translated(functions,script,case,budget=32768,missing=None,null_bus=False,null_out=False,scratch=SCRATCH):
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
  try:assert n==len(WIDTHS[target]);out[0]=script.call(target,list(args[:n]));return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);ptr=None if null_out else c.byref(out);passed=None if null_bus else c.byref(bus);entry=case['entry'];params=case['params']
 status=functions[entry](passed,*params,scratch if entry==0x1aa40 else budget,ptr)
 return status,out.value

def cases():
 rng=random.Random(0x1af04);rows=[]
 for i in range(1024):
  kind=i%8;id=[0,1,27,52,128,0x7fff,0xfff0,0xffff][(i//8)%8];offset=(id if id<32768 else id-65536)*12;slot=(i//8)%50;entry=0x15b534+slot*12;handle=0x110000+(i%64)*4;initial=[[0x464d0+offset,4,0 if kind==0 else 0x123456],[0x464d4+offset,4,0x4d455350],[0x464d8+offset,4,128]]
  for j in range(50):initial += [[0x15b534+j*12,2,(id+1)&65535],[0x15b53a+j*12,2,1],[0x15b53c+j*12,2,1]]
  if kind in[1,2]:initial += [[entry,2,id],[entry+6,2,[1,2,0x7fff,0xffff][(i//64)%4]],[entry+8,2,0 if kind==2 else 1],[entry+2,4,rng.getrandbits(32)]]
  elif kind in[3,4,6,7]:initial += [[entry+6,2,0]]
  if kind==6:initial += [[entry,2,id]]
  rows.append({'entry':0x1af04,'params':[id],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'default_helper_return':rng.getrandbits(32),'allocated_handle':handle,'allocation_fails':kind==4,'raise_ref':kind==7,'reread_handle':kind==3 and i%16==3,'ready_address':entry+8,'waits_until_ready':1+i%3,'read_queues':[],'kind':kind})
 for i in range(512):
  id=[0,1,27,0xffff][i%4];initial=[]
  for j in range(50):
   match=j%7==i%7;entry=0x15b534+j*12;handle=0x110000+j*4;initial += [[entry,2,id if match else(id+1)&65535],[entry+6,2,[0,1,2,0xffff][(i+j)%4]],[entry+2,4,handle],[handle,4,0x170008+j*16]]
  rows.append({'entry':0x1b002,'params':[id],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'default_helper_return':rng.getrandbits(32),'read_queues':[]})
 for i in range(256):
  kind=i%8;tag=[0x4d455350,0,0xffffabcd,0x52545854][(i//8)%4];size=128+(i%8)*16;handle=0 if kind==6 else 0x110000;completion=0 if kind==7 else 0x110004;stream=[[(0,16)]]if kind==0 else[[(256,16)]]if kind==1 else[[(0,2),(128,16)]]if kind==2 else[[(0,15),(128,16)]]if kind==3 else[[(32708,16)],[(128,16)]]if kind==4 else[[],[(64,16)]]if kind==5 and i%32==5 else[[(32704,16)]]if kind==5 else[[(128,16)]]
  queues=[{'address':0x47b82,'width':2,'values':[1,1,0]if i%3==0 else[0]},{'address':0x47b80,'width':2,'values':[1,0]if i%5==0 else[0]}]
  rows.append({'entry':0x1b044,'params':[0x123456,tag,handle,size,completion],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[[0x110000,4,0x170000],[0x110004,2,0xa55a]],'default_helper_return':rng.getrandbits(32),'read_queues':queues,'progress_kind':i%3,'stream_specs':stream,'kind':kind})
 for i in range(128):rows.append({'entry':0x1aa40,'params':[[0,1,2,0xffff][i%4]],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[],'default_helper_return':rng.getrandbits(32),'read_queues':[]})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-resources'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libresources.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_resources.c'),'-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr)
 if p.returncode:save(out/'status.json',{'status':'terminal_compile_failed'});raise RuntimeError(str(out/'compile.log'))
 functions=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opts.limit:vectors=[case for entry in RANGES for case in[x for x in vectors if x['entry']==entry][:opts.limit]]
 coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);expected,steps=original(a,case,coverage);status,d0=translated(functions,b,case)
   left=bytes(a.memory[:SP-0x1000]+a.memory[SP+32:]);right=bytes(b.memory[:SP-0x1000]+b.memory[SP+32:])
   if status or d0!=expected or left!=right or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_D0':expected,'C_D0':d0,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':b.trace,'RAM_accesses_calls_and_return_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for lo,hi in RANGES.items():
  decoded,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);addresses.update(x['address']for x in decoded)
 covered=coverage&addresses
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(addresses-coverage)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)]}));return
 if not addresses<=coverage:save(out/'status.json',{'status':'terminal_coverage_incomplete','matched_cases':len(rows),'uncovered':[hex(a)for a in sorted(addresses-coverage)]});raise AssertionError(str(addresses-coverage))
 guards=[]
 for entry,fields in [(0x1af04,[1,2,3,4,5]),(0x1b002,[1,2,3,5]),(0x1b044,[1,2,3,4,5]),(0x1aa40,[2,3,4,5])]:
  case=next(x for x in vectors if x['entry']==entry)
  for field in fields:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,missing=field);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':field})
  for kwargs in[{'null_bus':True},{'null_out':True}]+([]if entry==0x1aa40 else[{'budget':0}]):
   script=Script(snapshot,case);status,d0=translated(functions,script,case,**kwargs);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'arguments':kwargs})
 for entry in[0x1af04,0x1b002,0x1b044]:
  case=next(x for x in vectors if x['entry']==entry);script=Script(snapshot,case);status,d0=translated(functions,script,case,budget=1)
  if entry==0x1af04:case=next(x for x in vectors if x['entry']==entry and x['kind']==5);script=Script(snapshot,case);status,d0=translated(functions,script,case,budget=1)
  assert status==4 and d0==0xa55aa55a;guards.append({'entry':hex(entry),'work_limit':True})
 texture=next(x for x in vectors if x['entry']==0x1aa40 and x['params']==[1]);script=Script(snapshot,texture);status,d0=translated(functions,script,texture,scratch=0);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'texture_missing_private_scratch':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'four_resource_callers_original_CPU_and_C_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'new_components':4,'original_bytes':sum(b-a for a,b in RANGES.items()),'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_resources.c','biwn_resources.h']},'nested_dependencies_scripted':list(hex(a)for a in WIDTHS),'matched':['Full resource acquire/release, marker-stream loading and texture setup bodies; external RAM/access width/order, logical helper args, full D0, callee saves and return stack match original CPU.','50-slot scans, raw signed ID lookup, reference wrap/zero/duplicate matches, ready waits, allocation failure, completion/wake/rereads, semaphore waits, sixteen-tag marker retries/boundary and direct-buffer-return lock semantics, 36 texture descriptors.'],'limits':['Nested allocator/free/copy/CD/BIOS/yield/signal boundaries are explicit scripts in this standalone proof. Actual source-disc data and native allocator/copy integration are separate.','Private CPU stack and supplied texture scratch, CCR and other caller-saved registers are excluded. Host limits/errors retain partial effects and unchanged output; no full scheduler, BIOS/CD timing, resource lifecycle or game proof.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-resources-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
