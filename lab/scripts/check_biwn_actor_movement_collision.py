"""13C9A caller versus original CPU with explicit direction/GPU/collision services."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_rng_cpu as prior
import check_biwn_actor_direction as direction
import check_biwn_movement_submit_cpu as submit_cpu
import check_biwn_actor_collision as collision
ROOT=prior.ROOT;world=prior.world;CPU=prior.CPU;SP=prior.SP;STOP=prior.STOP
SERVICE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32)
WIDTHS={0x13440:[2,2],0xe220:[4,4,4,4,4],0x13b5a:[4,2,2,2],0x13bb0:[4,4,2]}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')

class Memory(prior.Memory):
 def __init__(self,snapshot,case,device=None,Cside=1):
  super().__init__(snapshot,case);self.case=case;self.device=device
  obj=0x80000;container=0x82000;scene=0x84000;tiles=0x90000;scan=0x100000;regions=0x110000;record=0x121000
  self.put(0x49c18,4,scene);self.put(scene,2,2);self.put(scene+4,4,regions);self.put(scene+8,4,scan)
  self.put(container,2,2);self.put(container+8,4,tiles)
  for room in range(-6,7):self.put(0x49bb4+room*4,4,container)
  for n in range(2):
   for off,v in [(2,0),(4,1),(6,0xffff),(8,0x1000),(10,0),(14,0),(16,16),(18,16)]:self.put(tiles+n*20+off,2,v)
   for off,v in [(2,0),(4,0),(6,16),(8,16)]:self.put(regions+n*24+off,2,v)
  layout=case['collision_layout'];self.put(obj+64,2,[0,1,0xffff][layout%3]);self.put(obj+22,2,0)
  for off,v in [(26,0x10000),(30,0xffff0000),(34,0x10000),(38,0xffff0000)]:self.put(obj+off,4,v)
  for off in [2,4,6,8]:self.put(0x120000+off,2,[0,1,0xffff,0x1000][(layout+off//2)%4])
  self.put(record+6,2,0);self.put(record+8,2,16);self.put(record+22,2,0xffff if layout==0 else 0)
  target=0 if layout==2 else 3 if layout==3 else 0xffff;flags=0 if layout==1 else 0x7000
  for n,key in enumerate(range(-512,544)):
   self.put(scan+n*6,2,key);self.put(scan+n*6+2,2,flags|0x8000 if n==1055 else flags);self.put(scan+n*6+4,2,target)
  if device is not None:device.seed(bytes(self.ram),Cside)
 def read(self,a,w):
  if self.device is None:return super().read(a,w)
  queue=self.queues.get((a,w))
  if queue:self.device.direct(a,w,queue.pop(0))
  value=self.device.read(a,w);self.trace.append(['read',a,w,value])
  if a<0x200000:self.put(a,w,value)
  return value
 def write(self,a,w,v):
  if self.device is None:return super().write(a,w,v)
  self.trace.append(['write',a,w,v])
  if w==2:self.device.write16(a,v)
  else:assert w==4;self.device.write(a,v)
  if a<0x200000:self.put(a,w,v)

def original(memory,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,bytes(memory.ram))
 for reg,value in zip(world.REGS,case['registers']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,case['SR']);cpu.reg_write(UC_M68K_REG_A7,SP)

 steps=[]
 def code(engine,a,w,_):
  if a in WIDTHS:
   stack=engine.reg_read(UC_M68K_REG_A7);offset=4;args=[]
   for width in WIDTHS[a]:args.append(int.from_bytes(engine.mem_read(stack+offset,width),'big'));offset+=width
   memory.trace.append(['call',a,args,engine.reg_read(UC_M68K_REG_D0)])
  assert 0x13c9a<=a<0x13f12 or any(lo<=a<hi for lo,hi in direction.RANGES+submit_cpu.RANGES+collision.RANGES),hex(a);steps.append(a);coverage.add(a)
 def read(engine,access,a,w,v,_):engine.mem_write(a,memory.read(a,w).to_bytes(w,'big'))
 def write(engine,access,a,w,v,_):memory.write(a,w,v&((1<<(8*w))-1))
 hook=cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x13c9a,STOP,count=10000,timeout=2000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP
 registers=[cpu.reg_read(r)for r in world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)];ram=bytearray(cpu.mem_read(0,0x200000))

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
   memory.trace.append(['call',target,args,state.contents.registers[0]])
   if target==0x13440:return DIRECTION(bus,state)
   if target==0xe220:return SUBMIT(bus,state,1000)
   assert target in[0x13b5a,0x13bb0];return COLLISION(bus,state,2048)

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
               'collision_layout':i%5,'returns':{str(0x13440):rng.getrandbits(32),str(0xe220):rng.getrandbits(32),str(0x13b5a):[0,1,2,0xffff,0x8000,0x10000,0x80000000][i%7],str(0x13bb0):[0,1,2,0xffff,0x8000,0x10000,0x80000000][i%7]},'read_queues':queues})
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args();out=ROOT/'verification/biwn-actor-movement-collision'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libactor-movement.dylib';names=['biwn_actor_movement.c','biwn_actor_direction.c','biwn_movement_submit_cpu.c','biwn_actor_collision.c','biwn_geometry_cpu.c','biwn_rng_cpu.c','biwn_signed_division.c','biwn_camera.c']
 process=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(source/name)for name in names],'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(process.stdout+process.stderr)
 if process.returncode:save(out/'status.json',{'status':'terminal_compile_failed'});raise RuntimeError(str(out/'compile.log'))
 global DIRECTION,SUBMIT,COLLISION
 lib=c.CDLL(str(library));DIRECTION=direction.bind(lib);SUBMIT=submit_cpu.bind(lib);COLLISION=collision.bind(lib);fn=bind(lib,full_call=True);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()[::8];vectors=vectors[:options.limit]if options.limit else vectors;rows=[];coverage=set();device=submit_cpu.hardware.Device()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});left=Memory(snapshot,case,device,0);expected,steps=original(left,case,coverage);original_RAM=device.ram();original_stats=device.stats();right=Memory(snapshot,case,device,1);status,actual,_=translated(fn,right,case);C_RAM=device.ram();C_stats=device.stats()
   if status or expected!=actual or original_RAM!=C_RAM or left.trace!=right.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors,'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(original_RAM,C_RAM))if a!=b][:50]});raise AssertionError(str(out/'mismatch.json'))
   assert original_stats['GPUExec1_calls']>0 and not C_stats['GPUExec1_calls']and not C_stats['game_frames_executed']and not C_stats['device_error']
   rows.append({'original_device':original_stats,'C_device':C_stats,'GPU_output_RAM_sha256':hashlib.sha256(C_RAM).hexdigest(),'case':i,'parameters':case,'CPU':actual,'instructions':steps,'trace':right.trace,'full_CPU_flags_RAM_private_frames_RTS_bus_and_calls_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:device.close()
 save(out/'fixtures.json',rows)
 if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded,_=world.select.binary_tools.m68k_instructions(image[0x13c9a-0x4000:0x13f12-0x4000],0x13c9a);addresses={x['address']for x in decoded}
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
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'actor_movement_with_real_direction_GPU_collision_and_geometry_matches_original','directory':str(out),
  'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'host_guards':len(guards),'original_interval':'[0x13c9a,0x13f12)',
  'code_bytes':0x13f12-0x13c9a,'pending_components':1,'published_new_components':0,'scripted_services':[],'collision_helpers_real':True,'nested_geometry_scripts':0,'direction13440_and_division_real':True,'GPU4320_original_vs_C_matrix_linked':True,'GPU_output_words_scripted':False,'synchronous_dispatch_completion_model':True,
  'source_sha256':{name:hashlib.sha256((source/name).read_bytes()).hexdigest()for name in names+[name.replace('.c','.h')for name in names]},
  'matched':['All registers, materialized SR/CCR, full call/RTS, private save and argument frames, complete2MBRAM and ordered data/helper calls with incomingD0 match.',
             'All four animation quadrants, signed view indices, fraction carries and coordinate wraps, outdoor/indoor edge priorities, low-word collision returns, invalid mode rollback and mutable mode rereads covered.'],
  'limits':['13440 direction and division plusE220/E098 and GPU4320 original/C matrix are real. Both13B5A/13BB0 collision helpers and their four geometry routines now execute real code. Geometry and scene records are bounded fixtures; GPU output words and collision effects are computed. Synchronous completion is a device model, not dispatcher concurrency. The movement call is complete under these fixtures, but not yet linked to the actor task ring or complete game.',
            'Host service/bus/argument errors preserve prior RAM effects and unchanged caller CPU. Original exceptions, arbitrary code/stack aliases, interrupts/tracing/timing and fullgame/hardware are not emulated.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass_services_pending'});save(ROOT/'verification/biwn-actor-movement-collision-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
