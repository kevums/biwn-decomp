"""Eight complete per-task arena CPU mailbox wrappers under explicit asynchronous bus schedules.
One fixed shader identity read is ABI bookkeeping; all other public accesses compare.
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
ROOTS={0xe0a6:(0xe0f2,0x4d80,0,'biwn_native_gpu_submit_4d80'),0xe0f2:(0xe148,0x6ae0,0,'biwn_native_gpu_submit_6ae0'),0xe148:(0xe19e,0x6da0,0,'biwn_native_gpu_submit_6da0'),0xe19e:(0xe202,0x52e0,0,'biwn_native_gpu_submit_52e0'),0xe202:(0xe220,0x57a0,0,'biwn_native_gpu_submit_57a0'),0xe220:(0xe26c,0x4320,5,'biwn_native_gpu_submit_4320'),0xe26c:(0xe2b8,0x4720,5,'biwn_native_gpu_submit_4720'),0xe2b8:(0xe2f4,0x4b00,3,'biwn_native_gpu_submit_4b00')}
MMIO=list(range(0xf03200,0xf03220,4));WAIT_RANGE=(0x162708,0x162722)
PARENT_OVERRIDE=None
ARENA=0x168000;SLOT_SIZE=256;SLOTS=102;POOL=0xc0928
def slot_bounds(case):
 base=ARENA+case['slot']*SLOT_SIZE;return base,base+16,base+240,base+256
def arena_cases():
 rows=cases()
 for index,row in enumerate(rows):
  if row['entry']==0xe202:row['post']=[]
  row['ram_values']={str(a):((index*0x9e3779b9+a)&0xffffffff)for a in[0x49c18,0x49c1c,0x49b88,0x10a684]}
  owner=index%102;row['slot']=owner;row['task']=POOL+owner*1024 if owner<101 else 0;row['sp']=row['task']+[0x3c0,0x3be,0x30][index%3] if owner<101 else 0x1ff000
 import copy
 for task in [POOL-1024,POOL+101*1024,POOL+4,POOL+100*1024+2,0xffffffff]:
  for entry in ROOTS:
   for helper in ['original','pending_repair']:
    row=copy.deepcopy(next(c for c in rows if c['entry']==entry and c['helper']==helper));row.update(task=task,slot=101,sp=0x1ff000);rows.append(row)
 return rows
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
 global SP
 SP=case['sp'];memory=bytearray(snapshot);memory[BASE:BASE+len(payload)]=payload
 memory[0xc0920:0xc0924]=case['task'].to_bytes(4,'big')
 for a,value in case['ram_values'].items():memory[int(a):int(a)+4]=value.to_bytes(4,'big')
 if case['helper']=='pending_repair':
  parent=PARENT_OVERRIDE or read(ROOT/'verification/native-actor-direction-disc-build-current.json');stage=Path(parent['derived_stage']).read_bytes();resident=Path(parent['component']).read_bytes();memory[parent['resident_address']:parent['resident_address']+len(resident)]=resident;memory[0xe098:0xe09e]=stage[0xe098-0x4000:0xe09e-0x4000]
 memory[BASE:BASE+len(payload)]=payload
 memory[ARENA:ARENA+SLOT_SIZE*SLOTS]=bytes((i*47+23)&255 for i in range(SLOT_SIZE*SLOTS))
 if compiled:memory[case['entry']:case['entry']+6]=b'\x4e\xf9'+symbols[ROOTS[case['entry']][3]].to_bytes(4,'big')
 return Script(memory,case)
def normalize(memory,snapshot,length,case):
 result=bytearray(memory)
 for lo,hi in [(BASE,BASE+length),(SP-10,SP),(slot_bounds(case)[1],slot_bounds(case)[2]),*[(a,a+6)for a in ROOTS]]:result[lo:hi]=snapshot[lo:hi]
 return bytes(result)
def execute(snapshot,case,payload,symbols,compiled):
 script=seed(snapshot,case,payload,symbols,compiled);arena_initial=bytes(script.memory[ARENA:ARENA+SLOT_SIZE*SLOTS]);header_initial=bytes(script.memory[case['task']:case['task']+38])if case['slot']<101 else None;u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_map(0xf03000,0x1000);u.mem_write(0,bytes(script.memory))
 for a,value in script.values.items():u.mem_write(a,value.to_bytes(4,'big'))
 u.reg_write(UC_M68K_REG_SR,case['sr'])
 for reg,value in zip(prior.world.REGS,case['incoming']):u.reg_write(reg,value)
 u.reg_write(UC_M68K_REG_A7,SP);machine=[];coverage=set();minimum=SP;arena_minimum=slot_bounds(case)[2];abi_reads=[]
 def private(address,width):return(SP-10<=address and address+width<=SP)or(slot_bounds(case)[1]<=address and address+width<=slot_bounds(case)[2])or(BASE<=address and address+width<=BASE+len(payload))
 def code(engine,pc,width,_):
  nonlocal minimum,arena_minimum
  sp=engine.reg_read(UC_M68K_REG_A7)
  if SP-10<=sp<=SP:minimum=min(minimum,sp)
  else:assert slot_bounds(case)[1]<=sp<=slot_bounds(case)[2],('Stackoutsideownedregions',hex(sp),case['slot']);arena_minimum=min(arena_minimum,sp)
  machine.append(dict(pc=pc,injections=[]))
  helper=0xe098<=pc<0xe0a6 or(case['helper']=='pending_repair'and WAIT_RANGE[0]<=pc<WAIT_RANGE[1]);root=case['entry']<=pc<ROOTS[case['entry']][0]
  if compiled:assert pc==case['entry']or BASE<=pc<BASE+len(payload)or helper,('Original root fallback',hex(pc))
  else:assert root or helper,hex(pc)
  if root:coverage.add(pc)
  if pc==0xe098:script.trace.append(['helper_entry',[engine.reg_read(reg)for reg in prior.world.REGS],engine.reg_read(UC_M68K_REG_A7)])
 def read_hook(engine,kind,address,width,value,_):
  if 0xf03000<=address<0xf04000:
   assert width==4;actual=script.mmio_read(address);engine.mem_write(address,actual.to_bytes(4,'big'));machine[-1]['injections'].append([address,actual]);return
  if address==0xc0920 and machine[-1]['pc']in [v for k,v in symbols.items()if k.startswith('biwn_native_gpu_arena_identity_')]:
   value=int.from_bytes(engine.mem_read(address,width),'big');assert width==4 and value==case['task'];abi_reads.append([address,value]);return
  if private(address,width)or address==SP:return
  actual=int.from_bytes(script.memory[address:address+width],'big');script.trace.append(['r',address,width,actual]);engine.mem_write(address,actual.to_bytes(width,'big'))
 def write_hook(engine,kind,address,width,value,_):
  value&=(1<<(width*8))-1
  if ARENA<=address<ARENA+SLOT_SIZE*SLOTS:assert slot_bounds(case)[1]<=address and address+width<=slot_bounds(case)[2],('Writeoutsideownedarena',hex(address),case['slot'])
  if 0xf03000<=address<0xf04000:assert width==4;script.mmio_write(address,value);return
  if not private(address,width):script.trace.append(['w',address,width,value]);script.memory[address:address+width]=value.to_bytes(width,'big')
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read_hook);u.hook_add(UC_HOOK_MEM_WRITE,write_hook);u.emu_start(case['entry'],STOP,count=100000,timeout=5000000);assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4 and script.complete()
 memory=bytes(u.mem_read(0,0x200000));assert memory[BASE:BASE+len(payload)]==payload
 base,low,high,end=slot_bounds(case);assert memory[ARENA:low]==arena_initial[:low-ARENA]and memory[high:ARENA+SLOT_SIZE*SLOTS]==arena_initial[high-ARENA:], 'Otherarenasorguardsmodified'
 assert abi_reads==([[0xc0920,case['task']]]if compiled else[])
 if header_initial is not None:assert memory[case['task']:case['task']+38]==header_initial,'Taskheaderchanged'
 for entry in ROOTS:
  expected=b'\x4e\xf9'+symbols[ROOTS[entry][3]].to_bytes(4,'big')if compiled and entry==case['entry']else snapshot[entry:entry+6];assert memory[entry:entry+6]==expected
 assert memory[SP:SP+4+4*len(case['params'])]==script.memory[SP:SP+4+4*len(case['params'])]
 assert normalize(memory,snapshot,len(payload),case)==normalize(script.memory,snapshot,len(payload),case)
 return dict(ram=normalize(memory,snapshot,len(payload),case),registers=[u.reg_read(reg)for reg in prior.world.REGS],trace=script.trace,mmio=script.values,machine=machine,coverage=coverage,private_depth=SP-minimum,arena_depth=slot_bounds(case)[2]-arena_minimum,abi_reads=abi_reads)
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
 assert reg(16)==STOP and reg(15)==SP+4;ram=native.device.ram();assert normalize(ram,snapshot,len(payload),case)==expected['ram']and ram[BASE:BASE+len(payload)]==payload
 assert all(lib.GPUReadLong(address,0)==value for address,value in expected['mmio'].items()),'Native mailbox state'
 registers=[reg(i)for i in range(16)];assert registers[:15]==expected['registers'];sr=reg(17);return dict(registers=registers,SR=sr,USP=native.prefix[16]if sr&0x2000 else registers[15],SSP=registers[15]if sr&0x2000 else native.prefix[17],helper_entries=events)
