"""Allocator/compactor/full copy source vs CPU; copy dependency effects explicit."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
RANGES={0x15200:0x152a2,0x152a2:0x1545c,0xe3e0:0xe4aa}
W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(boundary.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.MMIO={}
 def write(self,a,w,v):
  if a<0x200000:return super().write(a,w,v)
  if self.fail_write==(a,w):raise RuntimeError('injected MMIO failure')
  assert 0xf02200<=a<=0xf0223c and w==4
  self.MMIO[a]=v;self.trace.append(['w',a,w,v])
 def call_copy(self,args,incoming):
  if self.fail_call==0xe3e0:raise RuntimeError('injected copy dependency failure')
  self.trace.append(['call',0xe3e0,args]);source,destination,count=args;assert count<=0x2000
  # Scripted dependency copies supplied blocks; this is NOT blitter validation.
  payload=bytes(self.memory[source:source+count]);assert len(payload)==count
  for i,b in enumerate(payload):self.put(destination+i,1,b)
  return self.case['helper_D0']
def original(script,case,coverage,prefix_budget=None):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(script.memory));args=b''.join(x.to_bytes(4,'big')for x in case['params']);cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for r,v in zip(world.REGS,case['incoming']):cpu.reg_write(r,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 is_copy=case['entry']in[0xe3e0,0xe3ee]
 if not is_copy:cpu.mem_write(0xe3e0,b'\x4e\x75')
 steps=[];units=0
 def code(e,a,w,_):
  nonlocal units
  if prefix_budget is not None and a in[0xe420,0xe4a2]:
   if units==prefix_budget:e.emu_stop();return
   units+=1
  if not is_copy and a==0xe3e0:
   stack=e.reg_read(UC_M68K_REG_A7);values=[int.from_bytes(e.mem_read(stack+4+i*4,4),'big')for i in range(3)];script.changed=[];d0=script.call_copy(values,e.reg_read(UC_M68K_REG_D0))
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   e.reg_write(UC_M68K_REG_D0,d0);return
  if a==0x15200 and case['entry']!=a:script.trace.append(['call',a,[]])
  assert any(lo<=a<hi for lo,hi in RANGES.items()),hex(a);steps.append(a);coverage.add(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+20:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+20:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=100000,timeout=3000000)
 if prefix_budget is None:
  assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
  assert all(cpu.reg_read(r)==case['incoming'][i]for i,r in enumerate(world.REGS)if i not in[0,1,8,9])
  assert bytes(cpu.mem_read(SP+4,len(args)))==args
 else:assert cpu.reg_read(UC_M68K_REG_PC)in[0xe420,0xe4a2]and units==prefix_budget
 ram=bytearray(cpu.mem_read(0,0x200000))
 if not is_copy:ram[0xe3e0:0xe3e2]=script.memory[0xe3e0:0xe3e2]
 assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+20:]==script.memory[SP+20:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 alloc=lib.biwn_memory_allocate;compact=lib.biwn_memory_compact;copy=lib.biwn_memory_copy
 alloc.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];compact.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];copy.argtypes=[c.POINTER(world.Bus),W8]+[c.c_uint32]*6+[c.POINTER(c.c_uint32)]
 for f in[alloc,compact,copy]:f.restype=c.c_int
 return alloc,compact,copy
def translated(bindings,script,case,budget=4096,missing=None,null_bus=False,null_out=False):
 alloc,compact,copy=bindings
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
   if script.fail_call==target:raise RuntimeError('injected dependency failure')
   if target==0x15200:assert n==0;script.trace.append(['call',target,[]]);return compact(c.byref(bus),4096,out)
   assert target==0xe3e0 and n==3;out[0]=script.call_copy(list(args[:n]),out[0]);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(),world.R32(reader(4)),world.W16(),world.W32(writer(4)),world.CALL(call)];w8=W8(writer(1))
 if missing==6:w8=W8()
 elif missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);ptr=None if null_out else c.byref(out);passed=None if null_bus else c.byref(bus)
 if case['entry']==0x152a2:status=alloc(passed,case['params'][0],budget,ptr)
 elif case['entry']==0x15200:status=compact(passed,budget,ptr)
 else:status=copy(passed,w8,case['entry'],*case['params'],case['incoming'][0],budget,ptr)
 return status,out.value

def allocation_initial(kind,requested,free_index):
 base=0x1bf000;need=(requested+15)&0xfffffff8;initial=[[0x112d60,4,base],[0x112d64,4,0x1000]]
 initial += [[0x112960+i*4,4,0x100000+i*4]for i in range(256)]
 if free_index is not None:initial.append([0x112960+free_index*4,4,0])
 def block(address,size,next=0,prev=0):initial.extend([[address,4,size],[address+4,4,next],[address+8,4,prev]])
 if kind in[5,6,7,12,13]:
  block(base,64,base+192);block(base+64,128,0x112b60);block(base+192,64,base+384,base);block(base+256,128,0x112b64);block(base+384,0x1000-384,0,base+192)
  initial += [[0x112b60,4,base+72],[0x112b64,4,base+264]]
 elif kind in[0,8]:block(base,0x1000)
 elif kind in[1,9]:block(base,need+8,base+0x800);block(base+0x800,0x800)
 elif kind in[2,3,10,11]:block(base,16,base+0x200);block(base+0x200,need+8 if kind in[3,10]else need+64)
 elif kind==4:block(base,16,base+0x100);block(base+0x100,24,base+0x300);block(base+0x300,need+64)
 return initial

def cases():
 rng=random.Random(0x152a2);vectors=[]
 for i in range(1536):
  kind=i%14;requested=0xeb0 if kind in[5,12] else 0xef8 if kind in[6,13] else 4000 if kind==7 else (0,1,8,16,0xfffffff1,0xffffffff,127)[(i//11)%7]if kind==0 else rng.randrange(33,192)
  free=None if kind in[8,9,10,11,12,13]else [0,1,127,130,254,255][(i//11)%6]
  vectors.append({'entry':0x152a2,'params':[requested],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':allocation_initial(kind,requested,free),'default_helper_return':0,'helper_D0':rng.getrandbits(32),'read_queues':[],'kind':kind})
 for i in range(256):
  base=0x1bfa00;kind=i%5;segments=[(0x600,0)]if kind==0 else[(64,0),(64,0x112960),(64,0x112964),(0x600-192,0)]if kind==1 else[(64,0),(64,0x112960),(16,0),(16,0),(96,0x112964),(0x600-256,0)]if kind==2 else[(64,0),(128,0x112960),(64,0x15edc0),(64,0),(128,0x112964),(0x600-448,0)]if kind==3 else[(64,0),(128,0x112960),(16,0),(64,0x112964),(0x600-272,0)]
  initial=[[0x112d60,4,base]];a=base
  for size,handle in segments:
   initial += [[a,4,size],[a+4,4,handle],[a+8,4,rng.getrandbits(32)]]
   if 0x112960<=handle<0x112d60:initial += [[handle,4,a+8]]
   a+=size
  queues=[]
  if kind==4:queues=[{'address':base+192+4,'width':4,'values':[0,0x112968]}];initial += [[0x112968,4,base+200]]
  vectors.append({'entry':0x15200,'params':[],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'default_helper_return':0,'helper_D0':rng.getrandbits(32),'read_queues':queues,'kind':kind})
 lengths=[0,1,2,3,7,8,15,16,31,63,64,127,128,129,130,255,256,257,65535,65536,65537,65538,131071,131072,131073]
 for i in range(1024):
  entry=0xe3e0 if i%2 else 0xe3ee;length=lengths[(i//2)%len(lengths)];source=0x140000+(i%8);destination=source+((i//8)%9-4)*2 if length<128 else 0x170000+((i//8)%8)
  vectors.append({'entry':entry,'params':[source,destination,length]if entry==0xe3e0 else[destination,source,length],'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[],'default_helper_return':0,'helper_D0':0,'read_queues':[]})
 return vectors

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-memory'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libmemory.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_memory.c'),'-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr)
 if p.returncode:save(out/'status.json',{'status':'terminal_compile_failed'});raise RuntimeError(str(out/'compile.log'))
 functions=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opts.limit:vectors=[case for entry in[0x152a2,0x15200,0xe3e0,0xe3ee]for case in[x for x in vectors if x['entry']==entry][:opts.limit]]
 coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);expected,steps=original(a,case,coverage);status,d0=translated(functions,b,case)
   if status or d0!=expected or a.memory!=b.memory or a.MMIO!=b.MMIO or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_D0':expected,'C_D0':d0,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':b.trace,'RAM_MMIO_width_order_and_calls_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for lo,hi in RANGES.items():
  decoded,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);addresses.update(x['address']for x in decoded)
 covered=coverage&addresses
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(x)for x in sorted(addresses-coverage)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)]}));return
 if not addresses<=coverage:
  missing=sorted(hex(a)for a in addresses-coverage);save(out/'status.json',{'status':'terminal_coverage_incomplete','matched_cases':len(rows),'uncovered':missing});raise AssertionError(missing)
 guards=[]
 for entry,required in [(0x152a2,[2,4,5]),(0x15200,[2,4,5]),(0xe3e0,[0,4,6]),(0xe3ee,[0,4,6])]:
  case=next(x for x in vectors if x['entry']==entry)
  for missing in required:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,missing=missing);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing':missing})
  for kwargs in[{'null_bus':True},{'null_out':True},{'budget':0}]:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,**kwargs);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'arguments':kwargs})
 prefixes=[]
 for entry in [0xe3e0,0xe3ee]:
  for length in[0x7fffffff,0x80000000,0x8000007f,0x80000080,0xffffff80,0xffffffff]:
   case={**vectors[-1],'entry':entry,'params':[0x140000,0x170000,length]};a=Script(snapshot,case);b=Script(snapshot,case);original(a,case,set(),prefix_budget=3);status,d0=translated(functions,b,case,budget=3);assert status==4 and d0==0xa55aa55a and a.trace==b.trace and a.memory==b.memory and a.MMIO==b.MMIO;prefixes.append({'entry':hex(entry),'count':hex(length),'units':3,'original_execution_stopped_before_return':True,'C_work_limit_prefix_match':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'allocator_compactor_full_copy_original_CPU_and_C_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'raw_large_count_prefix_cases':len(prefixes),'new_components':2,'upgraded_existing_copy_components':2,'source_entry_points':['0x152a2','0x15200','0xe3e0','0xe3ee'],'original_bytes':sum(b-a for a,b in RANGES.items()),'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_memory.c','biwn_memory.h']},'copy_dependency_scripted_for_allocator_compactor':True,'matched':['Full allocator/compactor/copy caller control flow, full D0, callee saves, RAM, access widths/order and logical call boundaries vs original CPU.','Head/middle split and whole consumption, 256-slot handle search/exhaustion, compaction retry/success/failure, handle relocation, raw wrapped allocation requests, byte overlaps, 128/65536 thresholds, odd lengths and signed-BMI count prefixes.'],'limits':['Compactor E3E0 copy dependency is scripted with declared memory effects in this standalone proof. Large-copy MMIO trace has no hardware effects here; connected native-blitter proof is separate.','Private stack/CCR and other caller-saved registers excluded. Finite valid RAM/block fixtures; no physical timing, interrupts, complete resource or game lifecycle. Work limits preserve partial effects and leave output unchanged.','Two earlier partial CPU-copy/command-planner components are upgraded here, not counted again. Raw huge/negative counts have three-unit prefix checks, not successful full-copy returns.']}
 save(out/'guards.json',guards);save(out/'prefixes.json',prefixes);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-memory-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
