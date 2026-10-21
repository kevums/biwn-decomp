"""Scene CPU fixture with real original GPU-command helpers and declared mailboxes.
Only170A0 remains an adversarial geometry-record service. No GPU program runs.
"""
import ctypes as c,re
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
import scene17_host_runtime_v1 as old
base=old.base
GPU_ENTRIES={0xe098:0xe0a4,0xe0a6:0xe0f0,0xe0f2:0xe146,0xe148:0xe19c,0xe19e:0xe200,0xe202:0xe21e}
POLL={0xe0de,0xe134,0xe18a,0xe1ee,0xe212}
WRITES={0xe0d4,0xe12a,0xe180,0xe1e4,0xe208}
base.queue.ENTRIES.update(GPU_ENTRIES);base.queue.RETURNS.update(GPU_ENTRIES.values());base.queue.SCRIPTS.difference_update(GPU_ENTRIES)

def native_sites(payload,address):
 reads={};writes={}
 for ins in Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(payload,address):
  if ins.mnemonic!='move.l':continue
  m=re.fullmatch(r'\(a([0-7])\), d[0-7]',ins.op_str)
  if m:reads[ins.address]=8+int(m.group(1))
  m=re.fullmatch(r'd([0-7]), \(a([0-7])\)',ins.op_str)
  if m:writes[ins.address]=(int(m.group(1)),8+int(m.group(2)))
 assert reads and writes
 return reads,writes

class Runtime(old.Runtime):
 def __init__(self,library,rows):
  snapshot=(base.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();gpu,_=base.cd.gen.base.binary_tools.m68k_instructions(snapshot[0xe098:0xe220],0xe098)
  super().__init__(library,rows+gpu);self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32;self.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
 def reset(self,*args):
  super().reset(*args);self.idle_reads=0;self.ack_reads=0;self.command=0xffffffff;self.core.GPUWriteLong(0xf03200,0,0);self.core.GPUWriteLong(0xf03204,0xffffffff,0)
 def command_written(self,value):self.command=value&0xffffffff;self.ack_reads=0
 def inject(self,address,width):
  if address==0xf03200:
   assert width==4;self.core.GPUWriteLong(address,1 if self.idle_reads%2==0 else 0,0);self.idle_reads+=1;return
  if address==0xf03204:
   assert width==4;self.core.GPUWriteLong(address,self.command if self.ack_reads==0 else 0xffffffff,0);self.ack_reads+=1;return
  return super().inject(address,width)
 def write(self,address,width,value):
  if address==0xf03204:
   assert width==4;self.trace.append(['w',address,width,value]);self.core.GPUWriteLong(address,value,0);self.command_written(value);return
  return super().write(address,width,value)
 def native(self,*args):
  execute=self.core.m68k_execute
  def step(count):
   pc=self.core.m68k_get_reg(None,16)
   if pc==0xe098:self.inject(0xf03200,4)
   if pc in POLL:self.inject(0xf03204,4)
   value=execute(count)
   if pc in WRITES:self.command_written(self.core.GPUReadLong(0xf03204,0))
   return value
  self.core.m68k_execute=step
  try:return super().native(*args)
  finally:self.core.m68k_execute=execute
