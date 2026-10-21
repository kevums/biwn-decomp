"""Full CPU/stack RNG and math calls versus original M68000 execution."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_actor_navigation as navigation
ROOT=navigation.ROOT;world=navigation.world;CPU=navigation.CPU;SP=navigation.SP;STOP=navigation.STOP
RANGES=[(0x1a77c,0x1a7f4),(0xe540,0xe61c)]
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')

class Memory(navigation.Memory):
 def __init__(self,snapshot,case):
  super().__init__(snapshot,case);self.queues={(q['address'],q['width']):list(q['values'])for q in case.get('read_queues',[])}
 def read(self,a,w):
  queue=self.queues.get((a,w))
  if queue:self.put(a,w,queue.pop(0))
  return super().read(a,w)

def original(memory,case,coverage,allowed_ranges=None):
 ranges=RANGES if allowed_ranges is None else allowed_ranges
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(memory.ram))
 for reg,value in zip(world.REGS,case['registers']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,case['SR']);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
 def code(engine,a,w,_):assert any(lo<=a<hi for lo,hi in ranges),hex(a);coverage.add(a);steps.append(a)
 def read(engine,access,a,w,v,_):engine.mem_write(a,memory.read(a,w).to_bytes(w,'big'))
 def write(engine,access,a,w,v,_):memory.write(a,w,v&((1<<(w*8))-1))
 hook=cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=10000,timeout=2000000)
 pc=cpu.reg_read(UC_M68K_REG_PC);assert pc==STOP;registers=[cpu.reg_read(r)for r in world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)]
 assert bytearray(cpu.mem_read(0,0x200000))==memory.ram
 cpu.hook_del(hook);cpu.mem_write(STOP,b'\x40\xc7');cpu.emu_start(STOP,STOP+2,count=1);sr=cpu.reg_read(UC_M68K_REG_D7)&65535
 return {'registers':registers,'PC':pc,'SR':sr,'USP':SP+4,'SSP':0x1d0000},len(steps)

def bind(lib,full_call=False):
 fn=lib.biwn_rng_cpu_call if full_call else lib.biwn_rng_cpu_body;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU)];fn.restype=c.c_int;return fn

def translated(fn,memory,case,missing=None,fail=None,null_bus=False,null_cpu=False):
 def reader(w):
  def cb(_,a,out):
   if fail==('read',w):return 1
   try:out[0]=memory.read(a,w);return 0
   except Exception as error:memory.errors.append(repr(error));return 1
  return cb
 def writer(w):
  def cb(_,a,value):
   if fail==('write',w):return 1
   try:memory.write(a,w,value);return 0
   except Exception as error:memory.errors.append(repr(error));return 1
  return cb
 callbacks=[world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4))]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(world.R8(),callbacks[0],callbacks[1],callbacks[2],callbacks[3],world.CALL(),None,0)
 state=CPU();state.registers[:]=case['registers'];state.sr=case['SR'];state.pc=case['entry'];state.usp=SP;state.ssp=0x1d0000;before=bytes(state)
 status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(state))
 return status,{'registers':list(state.registers),'PC':state.pc,'SR':state.sr,'USP':state.usp,'SSP':state.ssp},before==bytes(state)

def cases():
 rng=random.Random(0x1a77ce588);rows=[];edge=[0,1,2,32767,32768,65535,65536,0x7ffffffe,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 denominators=[1,2,32767,32768,65535,65536,44488,93674,0x7fffffff,0x80000000,0xffff5238,0xffffffff]
 selectors=[0,1,254,255,256,257,32767,32768,65534,65535]
 for entry,count in [(0x1a77c,1024),(0xe588,2048),(0xe60a,1024),(0xe540,2048)]:
  for i in range(count):
   a=edge[i%len(edge)]if i<512 else rng.getrandbits(32);b=denominators[(i//len(edge))%len(denominators)]if i<512 else rng.getrandbits(32)or 1
   registers=[rng.getrandbits(32)for _ in range(16)];registers[15]=SP;initial=[[SP,4,STOP]];queues=[]
   if entry==0x1a77c:
    selector=selectors[i%len(selectors)]if i<512 else rng.randrange(65536);signed=selector if selector<32768 else selector-65536
    initial+=[[SP+4,2,selector],[0x113082+signed*4,4,a],[0x462e8,4,b],[0x462ec,4,rng.choice(edge)]]
    if i%13==0:queues=[{'address':0x462e8,'width':4,'values':[b,denominators[(i+3)%len(denominators)]]}]
   else:initial+=[[SP+4,4,a],[SP+8,4,b]]
   rows.append({'entry':entry,'registers':registers,'SR':rng.randrange(32)|((i%8)<<8),'initial':initial,'read_queues':queues})
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args();out=ROOT/'verification/biwn-rng-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_rng_cpu.c','biwn_signed_division.c','biwn_camera.c'];library=out/'librng-cpu.dylib'
 subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 fn=bind(c.CDLL(str(library)),full_call=True);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if options.limit:vectors=sum([[x for x in vectors if x['entry']==entry][:options.limit]for entry in [0x1a77c,0xe588,0xe60a,0xe540]],[])
 rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});left=Memory(snapshot,case);right=Memory(snapshot,case)
   expected,steps=original(left,case,coverage);status,actual,_=translated(fn,right,case)
   if status or expected!=actual or left.ram!=right.ram or left.trace!=right.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors,'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(left.ram,right.ram))if a!=b][:50]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'CPU':actual,'instructions':steps,'trace':right.trace,'full_CPU_RAM_and_ordered_bus_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows)
 if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for start,end in RANGES:
  decoded,_=world.select.binary_tools.m68k_instructions(image[start-0x4000:end-0x4000],start);addresses.update(x['address']for x in decoded)
 excluded={0xe606,0xe608};assert addresses-excluded<=coverage,[hex(x)for x in sorted(addresses-excluded-coverage)]
 guards=[]
 for index in range(4):
  memory=Memory(snapshot,vectors[0]);status,_,unchanged=translated(fn,memory,vectors[0],missing=index);assert status==1 and unchanged and not memory.trace;guards.append({'missing_callback':index})
 for kwargs in [{'null_bus':True},{'null_cpu':True}]:
  memory=Memory(snapshot,vectors[0]);status,_,unchanged=translated(fn,memory,vectors[0],**kwargs);assert status==1 and unchanged and not memory.trace;guards.append(kwargs)
 for case in [{**vectors[0],'entry':0},{**vectors[0],'SR':0x2000}]:
  memory=Memory(snapshot,case);status,_,unchanged=translated(fn,memory,case);assert status==1 and unchanged and not memory.trace;guards.append({'unsupported_entry_or_supervisor':True})
 for fail in [('read',2),('read',4),('write',2),('write',4)]:
  memory=Memory(snapshot,vectors[0]);status,_,unchanged=translated(fn,memory,vectors[0],fail=fail);assert status==2 and unchanged;guards.append({'bus_error':fail,'CPU_unchanged':True})
 for entry in [0x1a77c,0xe588,0xe60a]:
  case=next(x for x in vectors if x['entry']==entry);memory=Memory(snapshot,case)
  if entry==0x1a77c:memory.put(0x462e8,4,0);memory.queues={}
  else:memory.put(SP+8,4,0)
  status,_,unchanged=translated(fn,memory,case);assert status==3 and unchanged;guards.append({'zero_divisor_host_error':hex(entry),'CPU_unchanged':True})
 for address,values in [(SP-40,[0]),(SP-28,[0]),(SP-28,[0x1a7a2,0]),(SP-28,[0x1a7a2,0x1a7c8,0])]:
  case=vectors[0];memory=Memory(snapshot,case);memory.queues={(address,4):values.copy()}
  status,_,unchanged=translated(fn,memory,case);assert status==4 and unchanged
  guards.append({'corrupt_nested_return':hex(address),'return_sequence':values,'CPU_unchanged':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'indexed_RNG_and_math_full_CPU_RAM_bus_match_original','directory':str(out),
  'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'reachable_nonexception_instruction_coverage':[len((addresses-excluded)&coverage),len(addresses-excluded)],
  'exception_only_instructions_excluded':[hex(x)for x in sorted(excluded)],'host_guards':len(guards),'new_components':0,
  'entries':['0x1a77c','0xe60a','0xe588','0xe540'],'full_CPU_SR_USP_SSP_private_frames_RAM_RTS_and_bus_compared':True,
  'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},
  'matched':['Full functions including nested original math calls and RTS match complete CPU/flags/stack banks, full2MBRAM/private frames and ordered data reads/writes.',
             'Raw signed selectors, edge/random seeds and operands, mutable Q rereads, nonpositive RNG normalization, divide/multiply signs and word/long division paths covered.'],
  'limits':['Already counted RNG/remainder/division/multiply bodies gain a full CPU interface; component count does not increase. No movement, actor startup, GPU, game or hardware completion is implied.',
            'Zero division returns a host error with earlier RAM effects and unchanged CPU; original exception frames are not emulated. No arbitrary code/stack aliases, interrupts, tracing or cycle timing.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-rng-cpu-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
