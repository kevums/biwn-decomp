"""Compare CPU GPU-mailbox routines with portable callback C on scripted bus replies.

The original instructions execute in Unicorn M68000; no GPU is emulated here.
Only CPU-visible ordering, values, register preservation and return are checked.
"""
import ctypes as c
from datetime import datetime,timezone
import hashlib,itertools,json,os,random,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import unicorn
import extract_biwn_stage as stage
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import binary_tools
SP,STOP=0x1ff000,0x1ffe00
READ=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32))
WRITE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32)
class Bus(c.Structure):_fields_=[('read32',READ),('write32',WRITE),('context',c.c_void_p),('read_budget',c.c_uint32)]

class Script:
 def __init__(self,command,pre,ack,post,source):
  self.command=command;self.queues={'pre':list(pre),'ack':list(ack),'post':list(post)};self.indices={k:0 for k in self.queues};self.phase='pre';self.source=source;self.trace=[];self.memory={};self.errors=[];self.fail_read=None;self.fail_read_phase=None;self.fail_write=None
 def read(self,address):
  if address==self.fail_read and (self.fail_read_phase is None or self.phase==self.fail_read_phase):raise RuntimeError('scripted read failure')
  if address in (0x49c18,0x49c1c):
   assert self.command==0x6ae0 and self.phase=='pre'
   value=self.source[0 if address==0x49c18 else 1]
  else:
   assert address==(0xf03204 if self.phase=='ack' else 0xf03200),(hex(address),self.phase)
   index=self.indices[self.phase];value=self.queues[self.phase][index];self.indices[self.phase]+=1
   if self.phase=='ack' and value!=self.command:self.phase='post'
  self.trace.append(('r',address,value));self.memory[address]=value;return value
 def write(self,address,value):
  if address==self.fail_write:raise RuntimeError('scripted write failure')
  assert address in (0xf03204,0xf0320c,0xf03210,0xf03214,0xf03218,0xf0321c)
  self.trace.append(('w',address,value));self.memory[address]=value
  if address==0xf03204:
   assert self.phase=='pre' and value==self.command
   self.phase='ack'
 def complete(self):return all(self.indices[k]==len(q) for k,q in self.queues.items())


def original(image,entry,script,incoming,instruction_budget=512):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
 cpu.mem_map(0,0x200000);cpu.mem_map(0xf03000,0x1000);cpu.mem_write(0x4000,image);cpu.mem_write(SP,STOP.to_bytes(4,'big'));cpu.reg_write(UC_M68K_REG_A7,SP)
 regs=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
 for reg,value in zip(regs,incoming):cpu.reg_write(reg,value)
 trace=[];stack_writes=[]
 def code(engine,address,size,_):
  assert 0xe098<=address<0xe148,(hex(address),size)
  trace.append(address)
 def read(engine,access,address,size,value,_):
  if 0xf03000<=address<0xf04000 or address in (0x49c18,0x49c1c):
   assert size==4
   engine.mem_write(address,script.read(address).to_bytes(4,'big'))
 def write(engine,access,address,size,value,_):
  value&=(1<<(size*8))-1
  if 0xf03000<=address<0xf04000:
   assert size==4;script.write(address,value)
  else:
   assert address==SP-4 and size==4,(hex(address),size)
   stack_writes.append((address,size,value))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
 cpu.emu_start(entry,STOP,count=instruction_budget,timeout=1_000_000)
 returned=cpu.reg_read(UC_M68K_REG_PC)==STOP
 for reg,value in zip(regs,incoming):assert cpu.reg_read(reg)==value
 if returned:
  assert cpu.reg_read(UC_M68K_REG_A7)==SP+4
  expected=[] if entry==0xe098 else [(SP-4,4,entry+6),(SP-4,4,0xe0f0 if entry==0xe0a6 else 0xe146)]
  assert stack_writes==expected,(stack_writes,expected)
 for address,value in script.memory.items():assert int.from_bytes(cpu.mem_read(address,4),'big')==value
 return {'returned':returned,'PC':hex(cpu.reg_read(UC_M68K_REG_PC)),'instructions':len(trace),'stack_writes':stack_writes,'D0':hex(cpu.reg_read(UC_M68K_REG_D0))}


def translated(fn,script,budget=128,missing_read=False,missing_write=False):
 def read(_,address,out):
  try:out[0]=script.read(address);return 0
  except Exception as e:script.errors.append(repr(e));return 1
 def write(_,address,value):
  try:script.write(address,value);return 0
  except Exception as e:script.errors.append(repr(e));return 1
 reader,writer=READ(read),WRITE(write);bus=Bus(READ() if missing_read else reader,WRITE() if missing_write else writer,None,budget)
 status=fn(c.byref(bus));return status,bus.read_budget


def main():
 root=stage.ROOT;s=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);p=s/'nextstage-68000-candidate.bin';image=p.read_bytes();assert stage.digest(image)==stage.STAGE_SHA
 code=image[0xe098-0x4000:0xe148-0x4000];assert len(code)==176
 decoded,decoder=binary_tools.m68k_instructions(code,0xe098)
 folder=root/'verification/biwn-gpu-commands'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');folder.mkdir(parents=True)
 source=root/'projects/black-ice-white-noise/restoration';library=folder/'libbiwn_gpu_commands.dylib'
 command=['clang','-dynamiclib','-std=c11','-Wall','-Wextra','-Werror','-O2',str(source/'biwn_gpu_commands.c'),'-o',str(library)]
 subprocess.run(command,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 lib=c.CDLL(str(library));functions={entry:getattr(lib,name) for entry,name in [(0xe098,'biwn_gpu_wait_idle'),(0xe0a6,'biwn_gpu_submit_4d80'),(0xe0f2,'biwn_gpu_submit_6ae0')]}
 for fn in functions.values():fn.argtypes=[c.POINTER(Bus)];fn.restype=c.c_int
 rng=random.Random(0xe098);rows=[]
 for entry,word in [(0xe0a6,0x4d80),(0xe0f2,0x6ae0)]:
  for pre_n,ack_n,post_n,ack_value in itertools.product(range(4),range(4),range(4),[0,0xffffffff,0x80000000,word^1]):
   pre=[rng.choice([1,0xffffffff,0x80000000]) for _ in range(pre_n)]+[0];ack=[word]*ack_n+[ack_value];post=[rng.choice([1,0xffffffff,0x80000000]) for _ in range(post_n)]+[0];values=[rng.getrandbits(32),rng.getrandbits(32)];incoming=[rng.getrandbits(32) for _ in range(15)]
   a=Script(word,pre,ack,post,values);observed=original(image,entry,a,incoming);assert observed['returned'] and a.complete()
   b=Script(word,pre,ack,post,values);status,remaining=translated(functions[entry],b);assert status==0 and b.complete() and not b.errors
   assert a.trace==b.trace and a.memory==b.memory
   expected_writes=[(0xf0320c,0x47b88),(0xf03210,0x49b8c),(0xf03214,0x49bb4 if word==0x4d80 else values[0]),(0xf03218,0x49b88 if word==0x4d80 else values[1])]
   if word==0x6ae0:expected_writes.append((0xf0321c,0x10d688))
   expected_writes.append((0xf03204,word));assert [(addr,v) for kind,addr,v in a.trace if kind=='w']==expected_writes
   rows.append({'entry':hex(entry),'pre_busy_reads':pre_n,'pending_ack_reads':ack_n,'post_busy_reads':post_n,'ack_value':hex(ack_value),'source_values':[hex(v) for v in values],'CPU':observed,'trace':a.trace,'remaining_host_read_budget':remaining})
 for busy_n in range(16):
  pre=[rng.getrandbits(32) or 1 for _ in range(busy_n)]+[0];a=Script(None,pre,[],[],[]);obs=original(image,0xe098,a,[rng.getrandbits(32) for _ in range(15)]);b=Script(None,pre,[],[],[]);status,_=translated(functions[0xe098],b);assert obs['returned'] and status==0 and a.trace==b.trace
  rows.append({'entry':'0xe098','busy_reads':busy_n,'CPU':obs,'trace':a.trace})
 guards=[]
 for entry in functions:
  assert functions[entry](None)==1;guards.append({'case':'null_bus','entry':hex(entry),'status':1})
 tests=[('missing_read',0xe098,0,None,None),('missing_write',0xe0a6,0,None,None),('zero_budget',0xe098,0,None,None),('ack_budget',0xe0a6,1,None,None),('source_budget',0xe0f2,1,None,None),('source_failure',0xe0f2,128,0x49c18,None),('write_failure',0xe0a6,128,None,0xf03214),('ack_failure',0xe0a6,128,0xf03204,None),('post_failure',0xe0a6,128,0xf03200,None)]
 for name,entry,budget,fail_r,fail_w in tests:
  word=0x6ae0 if entry==0xe0f2 else 0x4d80 if entry==0xe0a6 else None;x=Script(word,[0],[0] if word else [],[0] if word else [],[0x12345678,0xabcdef01]);x.fail_read=fail_r;x.fail_write=fail_w
  if name=='post_failure':x.fail_read_phase='post'
  status,remaining=translated(functions[entry],x,budget,missing_read=name=='missing_read',missing_write=name=='missing_write')
  expected=1 if name.startswith('missing') else 3 if 'failure' in name else 2;assert status==expected,(name,status,expected)
  if name=='post_failure':assert x.phase=='post' and x.indices['ack']==1 and len([t for t in x.trace if t[0]=='w'])==5
  guards.append({'case':name,'status':status,'trace':x.trace,'remaining_budget':remaining,'callback_errors':x.errors})
 x=Script(None,[1]*100,[],[],[]);obs=original(image,0xe098,x,[0]*15,instruction_budget=32);assert not obs['returned'] and obs['PC']=='0xe098' and len(x.trace)==16
 y=Script(None,[1]*100,[],[],[]);status,remaining=translated(functions[0xe098],y,budget=16);assert status==2 and y.trace==x.trace
 guards.append({'case':'script_never_zero_under_observation_budget','CPU':obs,'host_status':status,'read_trace_matches':True,'scope':'Original remains in the poll loop under32instruction observation; added C guard returns after16reads. Not proof of a real device hang.'})
 (folder/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');(folder/'guards.json').write_text(json.dumps(guards,indent=2)+'\n');(folder/'original-decode.json').write_text(json.dumps({'bytes_hex':code.hex(),'instructions':decoded,'decoder':decoder},indent=2)+'\n')
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'CPU_protocol_and_portable_C_match_scripted_bus','directory':str(folder),'stage_sha256':stage.STAGE_SHA,'original_interval':'[0xe098,0xe148)','original_bytes':176,'original_bytes_sha256':hashlib.sha256(code).hexdigest(),'portable_components':3,'entry_cases':{hex(e):sum(x['entry']==hex(e) for x in rows) for e in functions},'completed_CPU_cases':len(rows),'host_guard_cases':len(guards),'CPU_model':'Unicorn'+unicorn.__version__+' M68000','matched':['Every scripted bus read/write address,value,and ordering, including dynamic source reads.','Nonzero unequal command acknowledgements accepted.','Final bus-visible memory values.','OriginalCPU RTS/private-stack balance; D0-D7 and A0-A6 unchanged.'],'excluded':['GPU/DSP execution and real device scheduling, command purpose, races not represented by fixtures.','CPU condition codes and full-game integration.','No original timeout: read budget and callback failure handling are added guards, with partial writes retained.','Host status enum is not an originalD0 ABI return.'],'compiler':command,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ['biwn_gpu_commands.c','biwn_gpu_commands.h']}}
 (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n');(root/'verification/biwn-gpu-commands-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
