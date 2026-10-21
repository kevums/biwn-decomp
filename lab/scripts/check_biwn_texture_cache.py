"""Texture lookup/acquisition vs original CPU, with loader call boundary."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_resources as prior
world=prior.world;ROOT=prior.ROOT;SP=prior.SP;STOP=prior.STOP;SCRATCH=prior.SCRATCH
RANGES={0x1ac3c:0x1ac68,0x1ac68:0x1ae56};WIDTHS={0x1b044:[4]*5}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(prior.boundary.Script):
 def read(self,a,w):
  if SP-0x1000<=a<SP+32:return int.from_bytes(self.memory[a:a+w],'big')
  return super().read(a,w)
 def write(self,a,w,v):
  if SP-0x1000<=a<SP+32:self.put(a,w,v);return
  return super().write(a,w,v)
 def call(self,target,args,incoming_D0):
  if self.fail_call==target:raise RuntimeError('injected loader failure')
  assert target==0x1b044;self.trace.append(['call',target,args,incoming_D0]);assert args[2]==SCRATCH
  for a,w,v in self.case.get('helper_effects',[]):self.put(a,w,v)
  return self.case['default_helper_return']
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big')+case['id'].to_bytes(2,'big'))
 for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);cpu.mem_write(0x1b044,b'\x4e\x75');steps=[]
 def code(e,a,w,_):
  if a==0x1b044:
   stack=e.reg_read(UC_M68K_REG_A7);values=[int.from_bytes(e.mem_read(stack+4+i*4,4),'big')for i in range(5)];script.changed=[];d0=script.call(a,values,e.reg_read(UC_M68K_REG_D0))
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   e.reg_write(UC_M68K_REG_D0,d0);return
  assert any(lo<=a<hi for lo,hi in RANGES.items()),hex(a);coverage.add(a);steps.append(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+32:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=100000,timeout=5000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4,(hex(cpu.reg_read(UC_M68K_REG_PC)),len(steps))
 assert all(cpu.reg_read(r)==case['incoming'][i]for i,r in enumerate(world.REGS)if i not in[0,1,8,9]);assert bytes(cpu.mem_read(SP+4,2))==case['id'].to_bytes(2,'big')
 ram=bytearray(cpu.mem_read(0,0x200000));ram[0x1b044:0x1b046]=script.memory[0x1b044:0x1b046]
 assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+32:]==script.memory[SP+32:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 lookup=lib.biwn_texture_lookup;lookup.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];lookup.restype=c.c_int
 acquire=lib.biwn_texture_acquire;acquire.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];acquire.restype=c.c_int;return {0x1ac3c:lookup,0x1ac68:acquire}
def translated(functions,script,case,budget=4096,missing=None,null_bus=False,null_out=False,scratch=SCRATCH):
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
  try:assert n==5;out[0]=script.call(target,list(args[:n]),out[0]);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);passed=None if null_bus else c.byref(bus);pointer=None if null_out else c.byref(out)
 if case['entry']==0x1ac3c:status=functions[case['entry']](passed,case['id'],budget,pointer)
 else:status=functions[case['entry']](passed,case['id'],scratch,case['incoming'][0],budget,pointer)
 return status,out.value
def cases():
 rng=random.Random(0x1ac68);rows=[]
 for i in range(512):
  id=[0,1,35,0xffff,0x8000][i%5];slot=i%36;initial=[]
  for j in range(36):initial +=[[0x15b4a0+j*4,2,(id+1)&65535],[0x15b4a2+j*4,2,rng.getrandbits(16)]]
  if i%3!=0:initial +=[[0x15b4a0+slot*4,2,id]]
  if i%7==0:initial +=[[0x15b4a0,2,id],[0x15b4a2,2,0]]
  rows.append({'entry':0x1ac3c,'id':id,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'read_queues':[],'default_helper_return':rng.getrandbits(32)})
 for i in range(1536):
  kind=i%12;mode=1+(i//12)%3;group=[1,2,3,6,16][(i//36)%5];start=[0,3,15,0xfffe,0xffff][(i//180)%5];relative=[0,1,18,75,0x7fff][(i//900)%5];id=(relative+123)&65535;initial=[]
  def put(a,w,v):initial.append([a,w,v&((1<<(w*8))-1)])
  if kind==0:mode=[0,4,0x8000,0xffff][(i//12)%4]
  if kind==1:relative=0x8000;id=(relative+123)&65535
  if kind==7:start=36-group
  put(0x15b530,2,mode);put(0x15b532,2,start)
  for m in range(1,4):put(0x464c8+m*2,2,123);put(0x464a0+m*2,2,group);put(0x464a8+m*4,4,0x345678);put(0x464b8+m*4,4,0x72000000)
  for j in range(-3,36):
   put(0x15b4a0+j*4,2,(id+137)&65535);put(0x15b4a2+j*4,2,1);put(0x4674c+j*8,4,0x130000+j*8192)
  signed_start=start if start<32768 else start-65536;slot=signed_start+(group if kind in[4,8,11]else 0)
  if kind in[2,4,9,10]:
   put(0x15b4a0+slot*4,2,id)
   for j in range(group):put(0x15b4a2+(slot+j)*4,2,0 if kind==9 else 0xffff if kind==10 else rng.getrandbits(16))
  elif kind in[3,8,11]:put(0x15b4a0+slot*4,2,0xffff)
  elif kind==5:put(0x15b4a2+slot*4,2,0)
  elif kind==6:pass
  queues=[]
  if kind==11:queues=[{'address':0x15b532,'width':2,'values':[start,(start+group)&65535,(start+2*group)&65535]}]
  rows.append({'entry':0x1ac68,'id':id,'kind':kind,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'read_queues':queues,'default_helper_return':rng.getrandbits(32)})
 # Negative group and zero group reuse are finite without executing DIVS#0.
 for group in[0xffff,0x8000,0]:
  base=next(r for r in rows if r['entry']==0x1ac68 and r.get('kind')==2);initial=base['initial']+[[0x464a2,2,group],[0x15b530,2,1],[0x15b532,2,0],[0x15b4a0,2,base['id']]];rows.append({**base,'initial':initial,'raw_group':group})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-texture-cache'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libtexture-cache.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_texture_cache.c'),'-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});functions=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opt.limit:vectors=[r for entry in RANGES for r in [x for x in vectors if x['entry']==entry][:opt.limit]]
 rows=[];coverage=set()
 try:
  for ordinal,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':ordinal,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);expected,steps=original(a,case,coverage);status,d0=translated(functions,b,case)
   if status or expected!=d0 or a.memory[:SP-0x1000]!=b.memory[:SP-0x1000]or a.memory[SP+32:]!=b.memory[SP+32:]or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected_D0':expected,'C_D0':d0,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':ordinal,'parameters':case,'full_D0':d0,'instructions':steps,'trace':b.trace,'external_RAM_calls_incoming_D0_and_return_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','case':ordinal,'error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for lo,hi in RANGES.items():
  decoded,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);addresses.update(r['address']for r in decoded)
 covered=addresses&coverage
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(addresses-coverage)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)]}));return
 assert addresses<=coverage,[hex(a)for a in sorted(addresses-coverage)];guards=[]
 for entry,fields in[(0x1ac3c,[1]),(0x1ac68,[1,2,3,4,5])]:
  case=next(r for r in vectors if r['entry']==entry)
  for field in fields:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,missing=field);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':field})
  for kw in[{'null_bus':True},{'null_out':True}]:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,**kw);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'arguments':kw})
  looping=next(r for r in vectors if r['entry']==entry and translated(functions,Script(snapshot,r),r,budget=0)[0]==4);script=Script(snapshot,looping);status,d0=translated(functions,script,looping,budget=0);assert status==4 and d0==0xa55aa55a;guards.append({'entry':hex(entry),'work_limit':True})
 case=next(r for r in vectors if r['entry']==0x1ac68 and r.get('kind')==3)
 for kw in[{'scratch':0}]:
  script=Script(snapshot,case);status,d0=translated(functions,script,case,**kw);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'zero_scratch':True})
 script=Script(snapshot,case);script.fail_call=0x1b044;status,d0=translated(functions,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'loader_failure':True,'partial_effects_retained':True})
 for attr,address,width in[('fail_read',0x15b530,2),('fail_write',0x15b4a0,2)]:
  script=Script(snapshot,case);setattr(script,attr,(address,width));status,d0=translated(functions,script,case);assert status==2 and d0==0xa55aa55a;guards.append({attr:[hex(address),width]})
 zero={**case,'initial':case['initial']+[[0x464a2,2,0],[0x15b532,2,36]]};script=Script(snapshot,zero);status,d0=translated(functions,script,zero);assert status==5 and d0==0xa55aa55a;guards.append({'zero_divisor_host_error':'Original exception frame not emulated'})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'texture_lookup_and_acquire_original_CPU_C_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'new_components':2,'original_bytes':sum(b-a for a,b in RANGES.items()),'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_texture_cache.c','biwn_texture_cache.h']},'helper_incoming_D0_compared':True,'nested_scripted_targets':['0x1b044'],'matched':['Lookup scans36slots andreturns firstmatching index regardless ofreference count; missreturns0. Acquisition respects signedmode/relativeID/group bounds, strict slot<36-group limit, group reuse/increment/refcountwrap, empty-ID allocation beforezero-ref eviction, source offsets/tags/private-handle scratch and fullD0.','External RAM access width/order, logical loader args/incomingD0, fullreturnD0, callee saves andRTS stack match original CPU. Loaded-prefix rereads, raw negative starts, negative/zero group reuse covered.'],'limits':['Loader is an explicit script in this standalone proof; no real disc bytes, texture residency or full scene is established here.','Private stack/scratch, CCR andothercaller-saved registers excluded. Negative group loader sizes are not fully copied here; zero divisor is a host error, not original exception emulation. Raw nonterminating searches are bounded by hostworkbudget. Finite validRAM fixtures, not arbitraryaliasing/concurrency.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-texture-cache-checks.json',report);print(json.dumps(report))
if __name__=='__main__':main()
