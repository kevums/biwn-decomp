"""Full E220/E098 CPU interface with original GPU4320 vs reconstructed GPU math."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_world_movement_pipeline as hardware
import check_biwn_rng_cpu as prior
ROOT=prior.ROOT;world=prior.world;CPU=prior.CPU;SP=prior.SP;STOP=prior.STOP
RANGES=[(0xe220,0xe26c),(0xe098,0xe0a6)]
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')

def bind(lib,full_call=False):
 fn=lib.biwn_movement_submit_cpu_call if full_call else lib.biwn_movement_submit_cpu_body;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32];fn.restype=c.c_int;return fn

def cpu_dict(cpu):
 # Direct SR reads can commit stale deferred flags. Materialize SR only after
 # taking this register/RAM snapshot; never read UC_M68K_REG_SR first.
 return {'registers':[cpu.reg_read(r)for r in world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)],'PC':cpu.reg_read(UC_M68K_REG_PC)}

def original(device,ram,case,coverage):
 device.seed(ram,0);cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,ram)
 for reg,value in zip(world.REGS,case['registers']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,case['SR']);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
 def code(engine,a,w,_):assert any(lo<=a<hi for lo,hi in RANGES),hex(a);coverage.add(a);steps.append(a)
 def read(engine,access,a,w,v,_):engine.mem_write(a,device.read(a,w).to_bytes(w,'big'))
 def write(engine,access,a,w,v,_):assert w==4;device.write(a,v&0xffffffff)
 hook=cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0xe220,STOP,count=10000,timeout=2000000);state=cpu_dict(cpu);assert state['PC']==STOP
 output=device.ram();trace=list(device.trace);stats=device.stats();mailbox=[device.read(0xf03200+off,4)for off in[0,4,12,16,20,24,28]]
 cpu.hook_del(hook);cpu.mem_write(STOP,b'\x40\xc7');cpu.emu_start(STOP,STOP+2,count=1);state['SR']=cpu.reg_read(UC_M68K_REG_D7)&65535
 return output,state,{'trace':trace,'device':stats,'mailbox':mailbox,'steps':steps}

def translated(fn,device,ram,case):
 device.seed(ram,1);errors=[]
 def read(_,a,out):
  try:out[0]=device.read(a,4);return 0
  except Exception as error:errors.append(repr(error));return 1
 def write(_,a,v):
  try:device.write(a,v);return 0
  except Exception as error:errors.append(repr(error));return 1
 r=world.R32(read);w=world.W32(write);bus=world.Bus(world.R8(),world.R16(),r,world.W16(),w,world.CALL(),None,0)
 state=CPU();state.registers[:]=case['registers'];state.sr=case['SR'];state.pc=0xe220;state.usp=SP;state.ssp=0x1d0000
 status=fn(c.byref(bus),c.byref(state),1000);assert status==0 and not errors,(status,errors)
 output=device.ram();trace=list(device.trace);stats=device.stats();mailbox=[device.read(0xf03200+off,4)for off in[0,4,12,16,20,24,28]]
 assert state.usp==SP+4 and state.ssp==0x1d0000
 return output,{'registers':list(state.registers),'PC':state.pc,'SR':state.sr},{'trace':trace,'device':stats,'mailbox':mailbox}

def guards(fn,snapshot):
 case={'registers':[0]*15+[SP],'SR':0,'initial':[[SP,4,STOP]]};rows=[]
 def attempt(missing=None,null_bus=False,null_cpu=False,entry=0xe220,sr=0,budget=1000,fail=None,busy_idle=False,busy_ack=False,corrupt=False):
  memory=prior.Memory(snapshot,case);trace=[];ack=0xffffffff
  def read(_,a,out):
   if fail=='read':return 1
   value=1 if a==0xf03200 and busy_idle else 0 if a==0xf03200 else ack if a==0xf03204 else 0 if corrupt and a==SP-4 else int.from_bytes(memory.ram[a:a+4],'big')
   out[0]=value;trace.append(['read',a,value]);return 0
  def write(_,a,v):
   nonlocal ack
   if fail=='write':return 1
   trace.append(['write',a,v])
   if a==0xf03204:ack=0x4320 if busy_ack else 0xffffffff
   elif a<0x200000:memory.put(a,4,v)
   return 0
  r=world.R32()if missing==0 else world.R32(read);w=world.W32()if missing==1 else world.W32(write);bus=world.Bus(world.R8(),world.R16(),r,world.W16(),w,world.CALL(),None,0)
  state=CPU();state.registers[:]=case['registers'];state.sr=sr;state.pc=entry;state.usp=SP;state.ssp=0x1d0000;before=bytes(state)
  status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(state),budget)
  assert bytes(state)==before;return status,trace
 for kwargs in [{'missing':0},{'missing':1},{'null_bus':True},{'null_cpu':True},{'entry':0},{'sr':0x2000}]:
  status,trace=attempt(**kwargs);assert status==1 and not trace;rows.append(kwargs)
 for fail in ['read','write']:
  status,_=attempt(fail=fail);assert status==2;rows.append({'bus_error':fail})
 for budget in [0,1,2]:
  status,_=attempt(budget=budget);assert status==3;rows.append({'read_budget':budget})
 for kwargs in [{'busy_idle':True},{'busy_ack':True}]:
  status,_=attempt(budget=4,**kwargs);assert status==3;rows.append(kwargs)
 status,_=attempt(corrupt=True);assert status==4;rows.append({'corrupt_idle_return':True})
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args();out=ROOT/'verification/biwn-movement-submit-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmovement-submit-cpu.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_movement_submit_cpu.c'),'-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=bind(c.CDLL(str(library)),full_call=True)
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0xe220);vectors=[]
 for i in range(options.limit or 128):
  regs=[rng.getrandbits(32)for _ in range(16)];regs[15]=SP;params=[rng.choice([0x80080,0x110000,0x120002]),*[0 if i%4==j else rng.getrandbits(32)for j in range(3)],rng.choice([0,1,0xffff,0x8000,0x7fff,rng.getrandbits(32)])]
  memory=prior.Memory(snapshot,{'initial':[[SP,4,STOP]]+[[SP+4+j*4,4,v]for j,v in enumerate(params)],'read_queues':[]});vectors.append(({'registers':regs,'SR':rng.randrange(32)|((i%8)<<8),'params':params},bytes(memory.ram)))
 device=hardware.Device();rows=[];coverage=set()
 try:
  for i,(case,ram)in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});left,expected,old=original(device,ram,case,coverage);right,actual,new=translated(fn,device,ram,case)
   if left!=right or expected!=actual or old['trace']!=new['trace']or old['mailbox']!=new['mailbox']:
    save(out/'mismatch.json',{'case':case,'expected':expected,'actual':actual,'original':old,'rebuilt':new,'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:60]});raise AssertionError(str(out/'mismatch.json'))
   assert old['device']['GPUExec1_calls']>0 and not new['device']['GPUExec1_calls']and not new['device']['game_frames_executed']and not new['device']['device_error']
   rows.append({'case':case,'CPU':actual,'original':old,'rebuilt':new,'RAM_sha256':hashlib.sha256(right).hexdigest(),'full_CPU_private_RAM_bus_mailbox_and_GPU_output_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:device.close()
 save(out/'fixtures.json',rows)
 if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 guard_rows=guards(fn,snapshot);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for start,end in RANGES:
  decoded,_=world.select.binary_tools.m68k_instructions(image[start-0x4000:end-0x4000],start);addresses.update(x['address']for x in decoded)
 # Busy branches are source-checked in the existing protocol proof. This
 # synchronous GPU device completes before the first acknowledgement poll.
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'full_CPU_movement_submit_with_original_GPU_vs_C_matrix_matches','directory':str(out),'cases':len(rows),
  'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'host_guards':len(guard_rows),'new_components':0,
  'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_movement_submit_cpu.c','biwn_movement_submit_cpu.h','biwn_movement_matrix.c','biwn_movement_matrix.h']},
  'bridge_sha256':hashlib.sha256((ROOT/'tools/libbiwn-movement-device.dylib').read_bytes()).hexdigest(),
  'matched':['Original E220/E098 CPU plus original GPU4320 matches C CPU interface plus reconstructed movement matrix, full CPU/SR/stack banks, completeRAM/private frames, CPU bus trace and mailbox words.',
             '128 mixed-angle/speed/base cases; C side executes no original CPU/GPU/game frames. Existing matrix1025case/353instruction proof supplies broader GPU coverage.'],
  'limits':['Synchronous dispatcher completion is a device model, not actual concurrent scheduling/timing. Original GPU uses pinned emulator, not physical hardware.','Already counted CPU submit/idle/GPU matrix gain full CPU/private stack linkage; no new components. Collision and complete actor/game integration remain pending.']}
 save(out/'guards.json',guard_rows);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-movement-submit-cpu-checks.json',report);print(json.dumps(report))

if __name__=='__main__':
 main()
