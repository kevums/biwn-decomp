"""Original CPU E220 mailbox helper vs C, with scripted device replies."""
import ctypes as c,itertools,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_gpu_commands as gpu
ROOT=gpu.stage.ROOT;SP=gpu.SP;STOP=gpu.STOP
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def original(image,script,params,incoming):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf03000,0x1000);cpu.mem_write(0x4000,image);cpu.mem_write(SP,STOP.to_bytes(4,'big')+b''.join(x.to_bytes(4,'big')for x in params))
 for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[];stack=[]
 def code(engine,a,w,_):assert 0xe220<=a<0xe26c or 0xe098<=a<0xe0a6;steps.append(a)
 def read(engine,access,a,w,v,_):
  if 0xf03000<=a<0xf04000:assert w==4;engine.mem_write(a,script.read(a).to_bytes(4,'big'))
  else:assert SP-4<=a<SP+24
 def write(engine,access,a,w,v,_):
  v&=(1<<(w*8))-1
  if 0xf03000<=a<0xf04000:assert w==4;script.write(a,v)
  else:assert a==SP-4 and w==4;stack.append((a,w,v))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0xe220,STOP,count=512,timeout=500000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 assert stack==[(SP-4,4,0xe226),(SP-4,4,0xe26a)]
 for reg,value in zip(REGS,incoming):assert cpu.reg_read(reg)==value
 assert bytes(cpu.mem_read(SP+4,20))==b''.join(x.to_bytes(4,'big')for x in params)
 return len(steps)
def main():
 s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(s/'nextstage-68000-candidate.bin').read_bytes();assert gpu.stage.digest(image)==gpu.stage.STAGE_SHA
 out=ROOT/'verification/biwn-movement-submit'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmovement-submit.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_movement_submit.c'),str(source/'biwn_gpu_commands.c'),'-o',str(library)];v=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});assert v.returncode==0,v.stderr
 lib=c.CDLL(str(library));fn=lib.biwn_movement_submit;fn.argtypes=[c.POINTER(gpu.Bus)]+[c.c_uint32]*5;fn.restype=c.c_int;rng=random.Random(0xe220);rows=[]
 for pre_n,ack_n,post_n,ack in itertools.product(range(4),range(4),range(4),[0,0xffffffff,0x80000000,0x4321]):
  params=[rng.getrandbits(32)for _ in range(5)];pre=[1]*pre_n+[0];pending=[0x4320]*ack_n+[ack];post=[0xffffffff]*post_n+[0]
  a=gpu.Script(0x4320,pre,pending,post,[]);steps=original(image,a,params,[rng.getrandbits(32)for _ in REGS]);b=gpu.Script(0x4320,pre,pending,post,[]);status,remaining=gpu.translated(lambda bus:fn(bus,*params),b)
  assert status==0 and a.complete() and b.complete() and a.trace==b.trace and a.memory==b.memory
  assert [x for x in b.trace if x[0]=='w']==[('w',0xf0320c+i*4,params[i])for i in range(5)]+[('w',0xf03204,0x4320)]
  rows.append({'parameters':params,'pre_busy_reads':pre_n,'pending_ack_reads':ack_n,'post_busy_reads':post_n,'ack_value':ack,'CPU_instructions':steps,'trace':b.trace,'remaining_budget':remaining})
 guards=[];params=[0x49ccc,0,17,0,0xffffffff];call=lambda bus:fn(bus,*params)
 assert call(None)==1;guards.append({'null_bus':True,'status':1})
 for name,budget in [('missing_read',128),('missing_write',128),('zero_budget',0),('ack_budget',1),('post_budget',3),('write_failure',128),('ack_failure',128),('post_failure',128)]:
  a=gpu.Script(0x4320,[0],[0x4320,1],[0],[])
  if name=='write_failure':a.fail_write=0xf03214
  if name=='ack_failure':a.fail_read=0xf03204
  if name=='post_failure':a.fail_read=0xf03200;a.fail_read_phase='post'
  status,remaining=gpu.translated(call,a,budget,missing_read=name=='missing_read',missing_write=name=='missing_write')
  expected=1 if name.startswith('missing') else 3 if 'failure' in name else 2;assert status==expected,(name,status)
  guards.append({'case':name,'status':status,'remaining_budget':remaining,'partial_trace':a.trace})
 save(out/'fixtures.json',rows);save(out/'guards.json',guards)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'original_CPU_movement_submit_matches_C','directory':str(out),'CPU_cases':len(rows),'host_guards':len(guards),'interval':'[0xe220,0xe26c)','bytes':76,'portable_components':1,'source_sha256':{name:gpu.binary_tools.sha(source/name)for name in ['biwn_movement_submit.c','biwn_movement_submit.h']},'matched':['Every ordered32bit data/command write and poll read/value; all256busy/ack/post combinations.','OriginalD0-D7/A0-A6 unchanged, private arguments unchanged and RTS stack balanced.','Any acknowledgement unequal to4320 is accepted, including nonzero; final idle must be zero.'],'limits':['Scripted device replies only, not GPU execution or scheduling.','Host return enum/limits/errors are added; not originalD0 or condition-code ABI.']}
 save(out/'report.json',report);save(ROOT/'verification/biwn-movement-submit-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
