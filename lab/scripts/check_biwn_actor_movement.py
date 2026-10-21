"""13C9A caller versus original CPU with explicit direction/GPU/collision services."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_rng_cpu as prior
ROOT=prior.ROOT;world=prior.world;CPU=prior.CPU;SP=prior.SP;STOP=prior.STOP
SERVICE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32)
WIDTHS={0x13440:[2,2],0xe220:[4,4,4,4,4],0x13b5a:[4,2,2,2],0x13bb0:[4,4,2]}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')

class Memory(prior.Memory):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.case=case
 def service(self,target,args,incoming):
  self.trace.append(['call',target,args,incoming])
  effects=self.case['GPU_effects']if target==0xe220 else self.case['collision_effects']if target in[0x13b5a,0x13bb0]else[]
  for a,w,v in effects:self.write(a,w,v)
  return self.case['returns'][str(target)]

def original(memory,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(memory.ram))
 for reg,value in zip(world.REGS,case['registers']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,case['SR']);cpu.reg_write(UC_M68K_REG_A7,SP)
 for address in WIDTHS:cpu.mem_write(address,b'\x4e\x75')
 steps=[]
 def code(engine,a,w,_):
  if a in WIDTHS:
   stack=engine.reg_read(UC_M68K_REG_A7);offset=4;args=[]
   for width in WIDTHS[a]:args.append(int.from_bytes(engine.mem_read(stack+offset,width),'big'));offset+=width
   value=memory.service(a,args,engine.reg_read(UC_M68K_REG_D0))
   for address,width,v in (case['GPU_effects']if a==0xe220 else case['collision_effects']if a in[0x13b5a,0x13bb0]else[]):engine.mem_write(address,(v&((1<<(8*width))-1)).to_bytes(width,'big'))
   engine.reg_write(UC_M68K_REG_D0,value);return
  assert 0x13c9a<=a<0x13f12,hex(a);steps.append(a);coverage.add(a)
 def read(engine,access,a,w,v,_):engine.mem_write(a,memory.read(a,w).to_bytes(w,'big'))
 def write(engine,access,a,w,v,_):memory.write(a,w,v&((1<<(8*w))-1))
 hook=cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x13c9a,STOP,count=10000,timeout=2000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP
 registers=[cpu.reg_read(r)for r in world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)];ram=bytearray(cpu.mem_read(0,0x200000))
 for a in WIDTHS:ram[a:a+2]=memory.ram[a:a+2]
 assert ram==memory.ram
 cpu.hook_del(hook);cpu.mem_write(STOP,b'\x40\xc7');cpu.emu_start(STOP,STOP+2,count=1);sr=cpu.reg_read(UC_M68K_REG_D7)&65535
 return {'registers':registers,'PC':STOP,'SR':sr,'USP':SP+4,'SSP':0x1d0000},len(steps)

def bind(lib,full_call=False):
 fn=lib.biwn_actor_movement_call if full_call else lib.biwn_actor_movement_body;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),SERVICE,c.c_void_p];fn.restype=c.c_int;return fn

def translated(fn,memory,case,missing=None,fail=None,null_bus=False,null_cpu=False,null_service=False,service_error=False,bad_return=False):
 def reader(width):
  def cb(_,a,out):
   if fail==('read',width):return 1
   try:out[0]=memory.read(a,width);return 0
   except Exception as error:memory.errors.append(repr(error));return 1
  return cb
 def writer(width):
  def cb(_,a,v):
   if fail==('write',width):return 1
   try:memory.write(a,width,v);return 0
   except Exception as error:memory.errors.append(repr(error));return 1
  return cb
 def service(_,bus,state,target):
  if service_error:return 1
  if bad_return:state.contents.registers[15]+=2;return 0
  try:
   stack=state.contents.registers[15];offset=4;args=[]
   for width in WIDTHS[target]:args.append(int.from_bytes(memory.ram[stack+offset:stack+offset+width],'big'));offset+=width
   state.contents.registers[0]=memory.service(target,args,state.contents.registers[0]);return 0
  except Exception as error:memory.errors.append(repr(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4))]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,world.CALL(),None,0);cb=SERVICE()if null_service else SERVICE(service)
 state=CPU();state.registers[:]=case['registers'];state.pc=case.get('entry',0x13c9a);state.sr=case['SR'];state.usp=SP;state.ssp=0x1d0000;before=bytes(state)
 status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(state),cb,None)
 return status,{'registers':list(state.registers),'PC':state.pc,'SR':state.sr,'USP':state.usp,'SSP':state.ssp},before==bytes(state)

def cases():
 rng=random.Random(0x13c9a);rows=[];obj=0x80000;table=0x81000;outdoor=0x120000;indoor=0x121000
 words=[0,1,0x3fff,0x4000,0x7fff,0x8000,0xffff];longs=[0,1,0x7fffffff,0x80000000,0xffffffff,0xfffffffe]
 for i in range(2048):
  registers=[rng.getrandbits(32)for _ in range(16)];registers[15]=SP;mode=[0,1,2,3,0xffff][(i//16)%5];view=[0,1,2,0xffff,0xfffe][i%5];signedview=view if view<32768 else view-65536
  direction=[0,1,63,64,127,128,191,192,255][(i//8)%9];kind=(i//80)%5;x=0x2400;z=0x9800
  if i%19==0:x=rng.choice(longs)
  if i%23==0:z=rng.choice(longs)
  if i==0:x=0x7fffffff;z=0xffffffff
  initial=[[SP,4,STOP],[SP+4,4,obj],[SP+8,4,table],[obj+192,2,view],[obj+110,1,direction],[0x49b9f,1,rng.randrange(256)],
           [0x47b88+signedview*64+18,2,rng.choice(words)],[0x47b88+signedview*64+22,2,rng.choice(words)],
           [obj+4,4,x],[obj+8,2,rng.choice(words)],[obj+10,4,z],[obj+14,2,rng.choice(words)],[obj+16,2,rng.choice(words)],[obj+18,2,rng.choice(words)],
           [obj+20,2,mode],[obj+68,4,outdoor],[obj+44,4,indoor],[obj+112,4,rng.getrandbits(32)],[obj+116,4,rng.getrandbits(32)],[obj+120,4,rng.getrandbits(32)],
           [obj+196,2,rng.randrange(65536)]]
  # Finite limits are chosen far enough apart that each named edge is reached
  # even with the signed16 GPU integer fixture. Kind4 stays inside.
  bounds=[0x10000,0xffff0000,0x20000,0xfffe0000]
  if kind==0:bounds[2]=0x80000000
  elif kind==1:bounds[3]=0x7fffffff
  elif kind==2:bounds[0]=0x80000000
  elif kind==3:bounds[1]=0x7fffffff
  for off,v in zip([72,76,80,84],bounds):initial.append([obj+off,4,v])
  for off,v in zip([48,52,56,60],bounds):initial.append([obj+off,4,v])
  for off in [2,4,6,8]:initial.append([outdoor+off,2,rng.choice(words)])
  for n in range(24):initial.append([table+n*4,4,rng.getrandbits(32)])
  gpu=[[obj+off,2,rng.choice(words)]for off in [146,148,150,154,156,158]]
  if i==0:
   gpu=[[obj+146,2,1],[obj+148,2,1],[obj+150,2,1],[obj+154,2,0],[obj+156,2,0],[obj+158,2,0]];initial += [[obj+14,2,0],[obj+18,2,0]]
  effects=[[obj+64,2,rng.randrange(65536)],[obj+20,2,2 if mode==1 else 1]]if i%7==0 else[]
  queues=[]
  if i%31==0:queues=[{'address':obj+20,'width':2,'values':[0,2]}]
  rows.append({'registers':registers,'SR':rng.randrange(32)|((i%8)<<8),'initial':initial,'GPU_effects':gpu,'collision_effects':effects,
               'returns':{str(0x13440):rng.getrandbits(32),str(0xe220):rng.getrandbits(32),str(0x13b5a):[0,1,2,0xffff,0x8000,0x10000,0x80000000][i%7],str(0x13bb0):[0,1,2,0xffff,0x8000,0x10000,0x80000000][i%7]},'read_queues':queues})
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args();out=ROOT/'verification/biwn-actor-movement'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libactor-movement.dylib'
 process=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_actor_movement.c'),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(process.stdout+process.stderr)
 if process.returncode:save(out/'status.json',{'status':'terminal_compile_failed'});raise RuntimeError(str(out/'compile.log'))
 fn=bind(c.CDLL(str(library)),full_call=True);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases();vectors=vectors[:options.limit]if options.limit else vectors;rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});left=Memory(snapshot,case);right=Memory(snapshot,case);expected,steps=original(left,case,coverage);status,actual,_=translated(fn,right,case)
   if status or expected!=actual or left.ram!=right.ram or left.trace!=right.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors,'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(left.ram,right.ram))if a!=b][:50]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'CPU':actual,'instructions':steps,'trace':right.trace,'full_CPU_flags_RAM_private_frames_RTS_bus_and_calls_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows)
 if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded,_=world.select.binary_tools.m68k_instructions(image[0x13c9a-0x4000:0x13f12-0x4000],0x13c9a);addresses={x['address']for x in decoded};assert addresses<=coverage,[hex(x)for x in sorted(addresses-coverage)]
 guards=[]
 for index in range(5):
  memory=Memory(snapshot,vectors[0]);status,_,same=translated(fn,memory,vectors[0],missing=index);assert status==1 and same and not memory.trace;guards.append({'missing_callback':index})
 for kwargs in [{'null_bus':True},{'null_cpu':True},{'null_service':True}]:
  memory=Memory(snapshot,vectors[0]);status,_,same=translated(fn,memory,vectors[0],**kwargs);assert status==1 and same and not memory.trace;guards.append(kwargs)
 for case in [{**vectors[0],'entry':0},{**vectors[0],'SR':0x2000}]:
  memory=Memory(snapshot,case);status,_,same=translated(fn,memory,case);assert status==1 and same and not memory.trace;guards.append({'unsupported_entry_or_supervisor':True})
 for fail in [('read',1),('read',2),('read',4),('write',2),('write',4)]:
  memory=Memory(snapshot,vectors[0]);status,_,same=translated(fn,memory,vectors[0],fail=fail);assert status==2 and same;guards.append({'bus_error':fail})
 for kwargs,expected_status in [({'service_error':True},3),({'bad_return':True},4)]:
  memory=Memory(snapshot,vectors[0]);status,_,same=translated(fn,memory,vectors[0],**kwargs);assert status==expected_status and same;guards.append(kwargs)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'actor_movement_caller_matches_original_CPU_with_scripted_services','directory':str(out),
  'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'host_guards':len(guards),'original_interval':'[0x13c9a,0x13f12)',
  'code_bytes':0x13f12-0x13c9a,'pending_components':1,'published_new_components':0,'scripted_services':[hex(x)for x in WIDTHS],
  'source_sha256':{name:hashlib.sha256((source/name).read_bytes()).hexdigest()for name in ['biwn_actor_movement.c','biwn_actor_movement.h']},
  'matched':['All registers, materialized SR/CCR, full call/RTS, private save and argument frames, complete2MBRAM and ordered data/helper calls with incomingD0 match.',
             'All four animation quadrants, signed view indices, fraction carries and coordinate wraps, outdoor/indoor edge priorities, low-word collision returns, invalid mode rollback and mutable mode rereads covered.'],
  'limits':['13440 direction, E220 GPU movement and13B5A/13BB0 collision helpers are explicit scripts. GPU output words and collision effects are fixtures. This is a caller proof, not real physics or complete actor integration.',
            'Host service/bus/argument errors preserve prior RAM effects and unchanged caller CPU. Original exceptions, arbitrary code/stack aliases, interrupts/tracing/timing and fullgame/hardware are not emulated.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass_services_pending'});save(ROOT/'verification/biwn-actor-movement-boundary-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
