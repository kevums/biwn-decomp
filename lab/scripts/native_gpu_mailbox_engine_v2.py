"""Original/native CPU mailbox wrappers under explicit asynchronous bus schedules.
GPU mailbox reads are injected before their actual CPU instructions; no GPU/frame
executes. Native CPU/SR/banks and real E098 helper entries are separate checks.
"""
import copy,ctypes as c,itertools,json,random
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000,UC_M68K_REG_SR,UC_M68K_REG_A7,UC_M68K_REG_PC
from check_biwn_scheduler import Native
import check_biwn_actor_navigation as prior
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';BASE=0x180000;SP=0x1ff000;STOP=0x1ffe00
ROOTS={0xe220:(0xe26c,0x4320,5,'biwn_native_gpu_submit_4320'),0xe2b8:(0xe2f4,0x4b00,3,'biwn_native_gpu_submit_4b00')}
MMIO=list(range(0xf03200,0xf03220,4));WAIT_RANGE=(0x162708,0x162722)
PARENT_OVERRIDE=None
def read(p):return json.loads(Path(p).read_text())
def cases():
 rng=random.Random(0xe2204b00);rows=[]
 for entry,(_,command,count,_)in ROOTS.items():
  for helper in ['original','pending_repair']:
   group=[]
   for index,(pre,ack,post,ack_value)in enumerate(itertools.product(range(3),range(3),range(3),[0,0xffffffff,0x80000000,command^1])):
    incoming=[rng.getrandbits(32)for _ in range(15)];params=[rng.getrandbits(32)for _ in range(count)]
    group.append(dict(entry=entry,command=command,helper=helper,params=params,incoming=incoming,sr=rng.randrange(32)|((index%8)<<8),pre=[0x80000001]*pre+[0],ack=[command]*ack+[ack_value],post=[0xffffffff]*post+[0],pre_accept=index%3,post_accept=(index//3)%3,initial_mmio={str(a):rng.getrandbits(32)for a in MMIO}))
   for value in [0,0xffffffff,0x80000000]:
    case=copy.deepcopy(group[len(group)%108]);case['params']=[value]*count;group.append(case)
   rows+=group
   for mode in [0,0x2000]:
    for flags in range(32):
     for index in [0,1,2,3,4,5,17,26]:
      case=copy.deepcopy(group[index]);case['sr']=mode|flags;rows.append(case)
 return rows
class Script:
 def __init__(self,snapshot,case):
  self.memory=bytearray(snapshot);self.case=case;self.phase='pre';self.indices={'pre':0,'ack':0,'post':0};self.accepts={'pre':0,'post':0};self.values={int(k):v for k,v in case['initial_mmio'].items()};self.trace=[]
  self.memory[SP:SP+4]=STOP.to_bytes(4,'big')
  for i,value in enumerate(case['params']):self.memory[SP+4+4*i:SP+8+4*i]=value.to_bytes(4,'big')
 def mmio_read(self,address):
  if self.phase=='ack':
   assert address==0xf03204,(self.phase,hex(address));queue=self.case['ack'];index=self.indices['ack'];value=queue[min(index,len(queue)-1)];self.indices['ack']+=1
   if value!=self.case['command']:self.phase='post'
  elif address==0xf03204:
   assert self.case['helper']=='pending_repair';index=self.accepts[self.phase];self.accepts[self.phase]+=1;value=0x13570001 if index<self.case[self.phase+'_accept']else 0xffffffff
  else:
   assert address==0xf03200,(self.phase,hex(address));queue=self.case[self.phase];index=self.indices[self.phase];value=queue[min(index,len(queue)-1)];self.indices[self.phase]+=1
  self.values[address]=value;self.trace.append(['r',address,4,value]);return value
 def mmio_write(self,address,value):
  assert address in MMIO;self.values[address]=value;self.trace.append(['w',address,4,value])
  if address==0xf03204:assert self.phase=='pre'and value==self.case['command'];self.phase='ack'
 def complete(self):return all(self.indices[k]==len(self.case[k])for k in ['pre','ack','post'])
def seed(snapshot,case,payload,symbols,compiled):
 memory=bytearray(snapshot);memory[BASE:BASE+len(payload)]=payload
 if case['helper']=='pending_repair':
  parent=PARENT_OVERRIDE or read(ROOT/'verification/native-actor-direction-disc-build-current.json');stage=Path(parent['derived_stage']).read_bytes();resident=Path(parent['component']).read_bytes();memory[parent['resident_address']:parent['resident_address']+len(resident)]=resident;memory[0xe098:0xe09e]=stage[0xe098-0x4000:0xe09e-0x4000]
 if compiled:memory[case['entry']:case['entry']+6]=b'\x4e\xf9'+symbols[ROOTS[case['entry']][3]].to_bytes(4,'big')
 return Script(memory,case)
def normalize(memory,snapshot,length):
 result=bytearray(memory)
 for lo,hi in [(BASE,BASE+length),(SP-4096,SP),*[(a,a+6)for a in ROOTS]]:result[lo:hi]=snapshot[lo:hi]
 return bytes(result)
def execute(snapshot,case,payload,symbols,compiled):
 script=seed(snapshot,case,payload,symbols,compiled);u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_map(0xf03000,0x1000);u.mem_write(0,bytes(script.memory))
 for a,value in script.values.items():u.mem_write(a,value.to_bytes(4,'big'))
 u.reg_write(UC_M68K_REG_SR,case['sr'])
 for reg,value in zip(prior.world.REGS,case['incoming']):u.reg_write(reg,value)
 u.reg_write(UC_M68K_REG_A7,SP);machine=[];coverage=set();minimum=SP
 def private(address,width):return(SP-4096<=address and address+width<=SP)or(BASE<=address and address+width<=BASE+len(payload))
 def code(engine,pc,width,_):
  nonlocal minimum
  minimum=min(minimum,engine.reg_read(UC_M68K_REG_A7));machine.append(dict(pc=pc,injections=[]))
  helper=0xe098<=pc<0xe0a6 or(case['helper']=='pending_repair'and WAIT_RANGE[0]<=pc<WAIT_RANGE[1]);root=case['entry']<=pc<ROOTS[case['entry']][0]
  if compiled:assert pc==case['entry']or BASE<=pc<BASE+len(payload)or helper,('Original root fallback',hex(pc))
  else:assert root or helper,hex(pc)
  if root:coverage.add(pc)
  if pc==0xe098:script.trace.append(['helper_entry',[engine.reg_read(reg)for reg in prior.world.REGS],engine.reg_read(UC_M68K_REG_A7)])
 def read_hook(engine,kind,address,width,value,_):
  if 0xf03000<=address<0xf04000:
   assert width==4;actual=script.mmio_read(address);engine.mem_write(address,actual.to_bytes(4,'big'));machine[-1]['injections'].append([address,actual]);return
  if private(address,width)or address==SP:return
  actual=int.from_bytes(script.memory[address:address+width],'big');script.trace.append(['r',address,width,actual]);engine.mem_write(address,actual.to_bytes(width,'big'))
 def write_hook(engine,kind,address,width,value,_):
  value&=(1<<(width*8))-1
  if 0xf03000<=address<0xf04000:assert width==4;script.mmio_write(address,value);return
  if not private(address,width):script.trace.append(['w',address,width,value]);script.memory[address:address+width]=value.to_bytes(width,'big')
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read_hook);u.hook_add(UC_HOOK_MEM_WRITE,write_hook);u.emu_start(case['entry'],STOP,count=100000,timeout=5000000);assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4 and script.complete()
 memory=bytes(u.mem_read(0,0x200000));assert memory[BASE:BASE+len(payload)]==payload
 for entry in ROOTS:
  expected=b'\x4e\xf9'+symbols[ROOTS[entry][3]].to_bytes(4,'big')if compiled and entry==case['entry']else snapshot[entry:entry+6];assert memory[entry:entry+6]==expected
 assert memory[SP:SP+4+4*len(case['params'])]==script.memory[SP:SP+4+4*len(case['params'])]
 assert normalize(memory,snapshot,len(payload))==normalize(script.memory,snapshot,len(payload))
 return dict(ram=normalize(memory,snapshot,len(payload)),registers=[u.reg_read(reg)for reg in prior.world.REGS],trace=script.trace,mmio=script.values,machine=machine,coverage=coverage,private_depth=SP-minimum)
def replay(native,snapshot,case,payload,symbols,compiled,expected):
 script=seed(snapshot,case,payload,symbols,compiled);native.device.seed(bytes(script.memory),0);lib=native.lib;lib.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];lib.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];lib.GPUReadLong.restype=c.c_uint32
 for address,value in script.values.items():lib.GPUWriteLong(address,value,0)
 lib.m68k_pulse_reset();lib.m68k_set_irq(0)
 for sr,sp in [(0x2000,SP if case['sr']&0x2000 else 0x1fd000),(0,SP if not case['sr']&0x2000 else 0x1fc000)]:lib.m68k_set_reg(17,sr);lib.m68k_set_reg(15,sp)
 lib.m68k_set_reg(17,case['sr'])
 for i,value in enumerate(case['incoming']):lib.m68k_set_reg(i,value)
 lib.m68k_set_reg(15,SP);lib.m68k_set_reg(16,case['entry']);events=[]
 def reg(i):return lib.m68k_get_reg(None,i)
 for index,step in enumerate(expected['machine']):
  pc=reg(16);assert pc==step['pc'],(index,hex(pc),hex(step['pc']))
  for address,value in step['injections']:lib.GPUWriteLong(address,value,0)
  if pc==0xe098:events.append(dict(registers=[reg(i)for i in range(15)],SP=reg(15),SR=reg(17)))
  lib.m68k_execute(1)
 assert reg(16)==STOP and reg(15)==SP+4;ram=native.device.ram();assert normalize(ram,snapshot,len(payload))==expected['ram']and ram[BASE:BASE+len(payload)]==payload
 assert all(lib.GPUReadLong(address,0)==value for address,value in expected['mmio'].items()),'Native mailbox state'
 registers=[reg(i)for i in range(16)];assert registers[:15]==expected['registers'];sr=reg(17);return dict(registers=registers,SR=sr,USP=native.prefix[16]if sr&0x2000 else registers[15],SSP=registers[15]if sr&0x2000 else native.prefix[17],helper_entries=events)
