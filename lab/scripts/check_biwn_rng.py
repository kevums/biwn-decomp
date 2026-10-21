"""Nine RNG routines vs original CPU with real division/multiply kernels."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
RANGES={0x1a6e0:0x1a6f8,0x1a6f8:0x1a77c,0x1a77c:0x1a7f4,0x1a7f4:0x1a87a,0x1a87a:0x1a8c6,0x1a8c6:0x1a8e2,0x1a8e2:0x1a8f8,0x1a8f8:0x1a91e,0xe60a:0xe61c}
ENTRY_WIDTHS={0x1a77c:[2],0x1a87a:[2],0x1a8c6:[4],0x1a8f8:[4],0xe60a:[4,4]}
CALL_WIDTHS={0xe60a:[4,4],0xe588:[4,4],0xe540:[4,4],0x1a87a:[2],0x1a8c6:[4],0x1a7f4:[]}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));args=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],ENTRY_WIDTHS.get(case['entry'],[])));cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
 def code(e,a,w,_):
  assert 0x1a6e0<=a<0x1a91e or 0xe540<=a<0xe61c,hex(a)
  if a in CALL_WIDTHS and a!=case['entry']:
   stack=e.reg_read(UC_M68K_REG_A7);returned=int.from_bytes(e.mem_read(stack,4),'big')
   # E60A's internal delegation is a pure math ABI, not a second bus.call.
   if not(a==0xe588 and returned==0xe616):
    values=[];offset=4
    for width in CALL_WIDTHS[a]:values.append(int.from_bytes(e.mem_read(stack+offset,width),'big'));offset+=width
    script.trace.append(['call',a,values])
  steps.append(a);coverage.add(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=300000,timeout=10000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
 assert bytes(cpu.mem_read(SP+4,len(args)))==args
 ram=bytes(cpu.mem_read(0,0x200000));assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+16:]==script.memory[SP+16:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 specs={0x1a6e0:('biwn_rng_init',[c.c_uint32]),0x1a6f8:('biwn_rng_current',[]),0x1a77c:('biwn_rng_indexed',[c.c_uint16]),0x1a7f4:('biwn_rng_fill',[c.c_uint32]),0x1a87a:('biwn_rng_select',[c.c_uint16,c.c_uint32]),0x1a8c6:('biwn_rng_seed',[c.c_uint32]),0x1a8e2:('biwn_rng_get',[]),0x1a8f8:('biwn_rng_set',[c.c_uint32,c.c_uint32])}
 functions={}
 for entry,(name,args)in specs.items():
  fn=getattr(lib,name);fn.argtypes=[c.POINTER(world.Bus)]+args+[c.POINTER(c.c_uint32)];fn.restype=c.c_int;functions[entry]=fn
 rem=lib.biwn_rng_remainder;rem.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];rem.restype=c.c_int;functions[0xe60a]=rem
 div=lib.biwn_signed_division;div.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];div.restype=c.c_int
 mul=lib.biwn_multiply32;mul.argtypes=[c.c_uint32,c.c_uint32];mul.restype=c.c_uint32
 return functions,div,mul
def translated(bindings,script,case,budget=255,missing=None,null_out=False,null_bus=False):
 functions,div,mul=bindings
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
 def call(_,target,args,n,result):
  try:
   if script.fail_call==target:raise RuntimeError('injected dependency failure')
   values=list(args[:n]);script.trace.append(['call',target,values])
   if target==0xe60a:assert n==2;return functions[target](*values,result)
   if target==0xe588:
    assert n==2;q=c.c_uint32();r=c.c_uint32();status=div(*values,c.byref(q),c.byref(r))
    if not status:result[0]=q.value
    return status
   if target==0xe540:assert n==2;result[0]=mul(*values);return 0
   if target==0x1a87a:assert n==1;return functions[target](c.byref(bus),values[0],result[0],result)
   if target==0x1a8c6:assert n==1;return functions[target](c.byref(bus),values[0],result)
   if target==0x1a7f4:assert n==0;return functions[target](c.byref(bus),budget,result)
   raise AssertionError(hex(target))
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);ptr=None if null_out else c.byref(out);passed_bus=None if null_bus else c.byref(bus);entry=case['entry'];params=case['params'];incoming=case['incoming'][0];fn=functions[entry]
 if entry==0xe60a:status=fn(*params,ptr)
 elif entry==0x1a6e0:status=fn(passed_bus,incoming,ptr)
 elif entry==0x1a87a:status=fn(passed_bus,params[0],incoming,ptr)
 elif entry==0x1a8f8:status=fn(passed_bus,params[0],incoming,ptr)
 elif entry==0x1a7f4:status=fn(passed_bus,budget,ptr)
 else:status=fn(passed_bus,*params,ptr)
 return status,out.value
def cases():
 rng=random.Random(0x1a6e0);rows=[];selectors=[0,1,254,255,256,257,0x7fff,0x8000,0xfffe,0xffff];edge=[0,1,2,0x7ffffffe,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 counts={0x1a6e0:16,0x1a6f8:256,0x1a77c:256,0x1a7f4:64,0x1a87a:256,0x1a8c6:64,0x1a8e2:256,0x1a8f8:512,0xe60a:512}
 def sx(v):return v if v<0x8000 else v-0x10000
 for entry,count in counts.items():
  for i in range(count):
   selector=selectors[i%len(selectors)]if i<128 else rng.randrange(65536);seed=edge[i%8]if i<64 else rng.getrandbits(32);den=[1,0xffffffff,44488,93674,0xffff5238,0x80000000,0x7fffffff][i%7];coeff=[0,3399,7197,0xffffffff,0x80000000][i%5]
   params=[selector]if entry==0x1a77c else[rng.randrange(65536)]if entry==0x1a87a else[seed]if entry in[0x1a8c6,0x1a8f8]else[seed,den]if entry==0xe60a else[]
   initial=[[0x462e0,4,44488],[0x462e4,4,3399],[0x462e8,4,44488],[0x462ec,4,3399],[0x462f0,4,93674],[0x462f4,4,7197],[0x113082,4,seed],[0x113082+sx(selector)*4,4,seed],[0x113082+4,4,rng.getrandbits(32)],[0x113080,2,selector]]
   case={'entry':entry,'params':params,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'default_helper_return':0,'read_queues':[]}
   # Setters include invalid/raw positive boundaries, without fixture-side
   # normalization. Negative slot-1 overlaps selector in the original map.
   if entry==0x1a8f8:case['params']=[edge[i%8]if i<128 else rng.getrandbits(32)]
   if entry in[0x1a6f8,0x1a77c]and i%3==0:
    q=0x462e0 if entry==0x1a6f8 else 0x462e8;r=q+4;case['initial'] += [[q,4,den],[r,4,coeff]]
   if entry==0x1a6f8 and i%11==0:case['read_queues'].append({'address':0x113080,'width':2,'values':[selector,1]})
   if entry in[0x1a6f8,0x1a77c]and i%13==0:
    q=0x462e0 if entry==0x1a6f8 else 0x462e8;case['read_queues'].append({'address':q,'width':4,'values':[44488,den]})
   if entry==0x1a7f4 and i%7==0:case['initial'] += [[0x462f0,4,den],[0x462f4,4,coeff]]
   rows.append(case)
 # Named stable examples for ordinary questions, independently executed.
 for old,new,incoming in[(255,0xffff,0xabcd1234),(256,0xffff,0xabcd1234)]:
  rows.append({'entry':0x1a87a,'params':[new],'incoming':[incoming]+[0]*14,'initial':[[0x113080,2,old]],'default_helper_return':0,'read_queues':[],'named_example':True})
 return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path);opts=ap.parse_args();out=ROOT/'verification/biwn-rng'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';body=opts.source or source/'biwn_rng.c';lib=out/'librng.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source),'-include',str(source/'biwn_rng.h'),str(body),str(source/'biwn_signed_division.c'),str(source/'biwn_camera.c'),'-o',str(lib)];process=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(process.stdout+process.stderr)
 if process.returncode:save(out/'status.json',{'status':'terminal_compile_failed'});raise RuntimeError(str(out/'compile.log'))
 bindings=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(snapshot).hexdigest()=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';vectors=cases()
 if opts.limit:
  sample=[]
  for entry in RANGES:sample += [x for x in vectors if x['entry']==entry][:opts.limit]
  vectors=sample+vectors[-2:]
 rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=boundary.Script(snapshot,case);b=boundary.Script(snapshot,case);d0,steps=original(a,case,coverage);status,result=translated(bindings,b,case)
   if status or d0!=result or a.trace!=b.trace or a.memory!=b.memory:
    save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_D0':d0,'C_D0':result,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':b.trace,'visible_RAM_and_access_call_order_match':True,'state_table_sha256':hashlib.sha256(b.memory[0x113082:0x113482]).hexdigest()})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded=[]
 for lo,hi in RANGES.items():
  part,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);decoded+=part
 addresses={x['address']if isinstance(x['address'],int)else int(x['address'],16)for x in decoded};covered=addresses&coverage;missing=addresses-coverage
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(missing)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(missing)]}));return
 assert not missing
 guards=[];needed={0x1a6e0:[5],0x1a6f8:[1,2,4,5],0x1a77c:[2,4,5],0x1a7f4:[2,4,5],0x1a87a:[1,3],0x1a8c6:[4,5],0x1a8e2:[1,2],0x1a8f8:[1,4]}
 for entry,fields in needed.items():
  case=next(x for x in vectors if x['entry']==entry)
  for field in fields:
   script=boundary.Script(snapshot,case);status,result=translated(bindings,script,case,missing=field);assert status==1 and result==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':field,'rejected':True})
  for kw in[{'null_out':True},{'null_bus':True}]:
   script=boundary.Script(snapshot,case);status,result=translated(bindings,script,case,**kw);assert status==1 and result==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'arguments':kw,'rejected':True})
 fill=next(x for x in vectors if x['entry']==0x1a7f4)
 for budget in[0,1,254]:
  script=boundary.Script(snapshot,fill);status,result=translated(bindings,script,fill,budget=budget);assert status==(1 if not budget else 4)and result==0xa55aa55a;guards.append({'fill_budget':budget,'partial_effects_retained':True,'output_unchanged':True})
 case=next(x for x in vectors if x['entry']==0x1a6f8)
 for kind in['read','write','call']:
  script=boundary.Script(snapshot,case)
  if kind=='read':script.fail_read=(0x113080,2)
  elif kind=='write':script.fail_write=(0x113082,4)
  else:script.fail_call=0xe60a
  status,result=translated(bindings,script,case);assert status and result==0xa55aa55a;guards.append({'failure':kind,'output_unchanged':True})
 zero={**case,'entry':0xe60a,'params':[1,0]};status,result=translated(bindings,boundary.Script(snapshot,zero),zero);assert status==3 and result==0xa55aa55a;guards.append({'remainder_zero_divisor_host_error':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'nine_rng_routines_original_CPU_and_C_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'portable_components':9,'original_bytes':sum(hi-lo for lo,hi in RANGES.items()),'intervals':{hex(lo):hex(hi)for lo,hi in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_rng.c','biwn_rng.h','biwn_signed_division.c','biwn_signed_division.h','biwn_camera.c','biwn_camera.h']},'RAM_sha256':hashlib.sha256(snapshot).hexdigest(),'helper_kernels_execute_original_CPU':True,'nested_helper_stubs':0,'matched':['Fullninefunctions, allsourceinstructions, externalRAM/accesswidth/order/value andlogicalhelpercalls/fullD0/callees/RTS match. OriginalE540/E588/E60A execute, Cusescheckedmultiply/division plusnewremainder wrapper.','Raw/signedword selectors, mutableQ/R reads, selector/state alias, finalselector reread, nonpositiveRMWnormalization, seeded255statefill andsetter boundaries/unchangedD0.','Original selector routine tests oldselector, maywrite a temporary normalization thenalwayswrites rawnewselector; incomingD0 upperbits preserved when oldselector<=255.'],'limits':['PrivateCPUstack/caller-savedregisters exceptfullD0/CCR excluded. Finite mappedRAM, immutablecode andcontrolledrereads; not arbitraryaliasing/concurrenthardwaretiming.','Host budgets/callbackerrors andzero-divisor errors retainpartial effects andunchangedoutD0; originalexception/infinite-loop behavior not emulated. No whole-game frames/hardware proof.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-rng-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
