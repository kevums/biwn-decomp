"""Native original CPU oracle for world task plus two actual yield-only tasks."""
import ctypes as c,json
from pathlib import Path
import check_biwn_scheduler as scheduler
import check_biwn_world_cleanup_pipeline as previous
ROOT=scheduler.ROOT
MAIN=0xc2128;IDLE1=0xc5928;IDLE2=0xc5528;CONTEXTS=[MAIN,IDLE1,IDLE2]
ENTRIES=[0x1a544,0xf360,0xf880];SSP=0x1d0000
STUBS=[0xe4c0,0x191f4,0xf0fa,0xeb04,0x20820,0x1aa40,0x20f78]
LOGGED=STUBS+[0x1a188,0xe220,0x1b786,0x19f2c,0x19fda,0x1028e,0x102c4,0x1039c,0x10430,0x10652,0x20e8c,0x20f0c,0xdf60]
def private(address,width=1):
 return SSP-0x1000<=address<SSP+8 or any(a+0x26<=address<a+0x400 for a in CONTEXTS)
def fixture(case,index):
 case=dict(case);case['initial']=list(case['initial']);case['initial'] += [[0xc0920,4,MAIN],[0x80,4,0xde08]]
 # Selection publishes a region pointer at actor+0x2c (global49c78).
 # Supply the original no-index sentinel in each region's later-used word
 # so a second update has a bounded, declared layout rather than random
 # snapshot tail bytes. This is fixture data, not a helper return/stub.
 for i in range(3):case['initial'].append([0x8c000+i*24+0x16,2,0xffff])
 # The second movement can miss the first update's matching boundary key.
 # End the declared finite parent table after its populated records, using
 # the original negative-flag terminator (also returns zero on key match).
 case['initial'] += [[0x90012,2,0],[0x90014,2,0x8000],[0x90016,2,0]]
 for i,(obj,entry)in enumerate(zip(CONTEXTS,ENTRIES)):
  top=obj+0x400;warm=bool(index%2)and i>0;stack=top-48 if warm else top
  case['initial'] += [[obj,4,CONTEXTS[(i+1)%3]],[obj+4,4,CONTEXTS[(i-1)%3]],[obj+8,4,entry],[obj+12,4,stack],[obj+16,4,0xdf66 if warm else entry],[obj+20,2,0],[obj+22,4,0],[obj+26,4,0],[obj+34,4,0]]
  if warm:
   for j in range(11):case['initial'].append([stack+j*4,4,0xa0000000+i*0x100+j])
   case['initial'].append([top-4,4,entry+6])
 return case
def masked_equal(a,b):
 # Original world-update contract excludes private task stacks/CCR. Saved
 # SR low5 bits are now externally stored; these stay explicitly excluded.
 left=bytearray(a);right=bytearray(b)
 ranges=[(SSP-0x1000,SSP+8),(0x15b7a0,0x15b7aa)]+[(x+0x26,x+0x400)for x in CONTEXTS]
 for start,end in ranges:left[start:end]=bytes(end-start);right[start:end]=bytes(end-start)
 for obj in CONTEXTS:left[obj+21]&=0xe0;right[obj+21]&=0xe0
 return left==right
def initial_cpu(registers):
 cpu=scheduler.CPU();cpu.registers[:]=registers;cpu.registers[15]=MAIN+0x400;cpu.usp=cpu.registers[15];cpu.ssp=SSP;cpu.sr=0;cpu.pc=0x1a544;return cpu

class Native(scheduler.Native):
 def __init__(self):
  super().__init__();self.lib.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.lib.GPUReadLong.restype=c.c_uint32
 def run(self,script,registers,limit=1000000,world_updates=2,input_backend=None,dispatch_backend=None,animation_backend=None):
  ram=bytes(script.memory);self.device.seed(ram,0)
  stubs=[a for a in STUBS if not(input_backend is not None and a==0xe4c0)]
  logged=list(LOGGED)
  if dispatch_backend is not None:
   stubs=[a for a in stubs if a!=0x191f4 and not(getattr(dispatch_backend,'camera_linked',False)and a==0xf0fa)and not(getattr(dispatch_backend,'animation_linked',False)and a==0xeb04)and not(getattr(dispatch_backend,'targeting_linked',False)and a==0x20820)]+dispatch_backend.extra_stubs
   logged=list(dict.fromkeys(logged+dispatch_backend.logged))
  stubs=list(dict.fromkeys(stubs))
  for target in stubs:self.device.direct(target,2,0x4e75)
  if input_backend is not None:input_backend.start(script.case)
  if animation_backend is not None:animation_backend.start(script.case)
  cpu=initial_cpu(registers);self.lib.m68k_pulse_reset();self.lib.m68k_set_irq(0)
  self.lib.m68k_set_reg(17,0x2000);self.lib.m68k_set_reg(15,SSP);self.lib.m68k_set_reg(17,0)
  for i,value in enumerate(cpu.registers):self.lib.m68k_set_reg(i,value)
  self.lib.m68k_set_reg(16,cpu.pc);calls=[];handoffs=[];yields=[];steps=[];bodies=0;dispatch_states=[]
  for _ in range(limit):
   pc=self.lib.m68k_get_reg(None,16)
   if pc==0x1a550 and bodies>=world_updates:break
   assert 0x4000<=pc<0x50000,hex(pc)
   steps.append(pc)
   if pc==0x1a188:bodies+=1
   if dispatch_backend is not None and pc==0x19294:dispatch_states.append(int.from_bytes(c.string_at(self.device.pointer+0x49cb8,2),'big'))
   if pc==0xe4c0 and input_backend is not None:input_backend.begin_poll()
   if pc==0xeb04 and animation_backend is not None:animation_backend.begin_update()
   if pc in [0x1a340,0x1a3d6]and'mode_reads'in script.case:
    self.device.direct(0x49c60,2,script.read(0x49c60,2))
   extra_entry=False
   if dispatch_backend is not None and pc in dispatch_backend.logged and pc not in LOGGED:
    stack_at_entry=self.lib.m68k_get_reg(None,15)
    returned=int.from_bytes(c.string_at(self.device.pointer+stack_at_entry,4),'big')
    extra_entry=0x191f4<=returned<0x19f2c or(getattr(dispatch_backend,'camera_linked',False)and(0xf0fa<=returned<0xf35e or 0x13440<=returned<0x134dc))or(getattr(dispatch_backend,'animation_linked',False)and 0xeb04<=returned<0xec04)or(getattr(dispatch_backend,'targeting_linked',False)and 0x20820<=returned<0x20a9c)
   if pc in logged and(pc in LOGGED or extra_entry):
    stack=self.lib.m68k_get_reg(None,15)
    def arg(offset,width):return int.from_bytes(c.string_at(self.device.pointer+stack+offset,width),'big')
    if pc==0xf0fa:args=[self.lib.m68k_get_reg(None,2)&0xffff,self.lib.m68k_get_reg(None,3)&0xffff]
    elif dispatch_backend is not None and pc in dispatch_backend.widths:
     offset=4;args=[]
     for width in dispatch_backend.widths[pc]:args.append(arg(offset,width));offset+=width
    elif pc==0xe220:args=[arg(4+i*4,4)for i in range(5)]
    elif pc==0x19f2c:args=[arg(4+i*2,2)for i in range(3)]
    elif pc in [0x19fda,0x1039c,0x10652]:args=[arg(4,4),arg(8,2)]
    elif pc==0x10430:args=[arg(4,4),arg(8,2),arg(10,2)]
    elif pc in [0xeb04,0x1028e,0x102c4]:args=[arg(4,4)]
    elif pc in [0x1aa40,0x20f78]:args=[arg(4,2)]
    else:args=[]
    calls.append(['call',pc,args])
    if pc in stubs:self.lib.m68k_set_reg(0,self.device.scripted_call(script,pc,args))
    if pc==0xdf60:yields.append({'context':hex(int.from_bytes(self.device.ram()[0xc0920:0xc0924],'big')),'SP':stack,'return_PC':arg(0,4),'body_calls':bodies})
   self.lib.m68k_execute(1)
   if input_backend is not None:
    if pc in[0xe4d4,0xe4e8,0xe4fc,0xe512]:input_backend.raw_reads.append(self.lib.m68k_get_reg(None,0))
    if pc in[0xe4cc,0xe4e0,0xe4f4,0xe50a]:input_backend.selects.append({0xe4cc:0x810e,0xe4e0:0x810d,0xe4f4:0x810b,0xe50a:0x8107}[pc])
   command=self.lib.GPUReadLong(0xf03204,0)
   if command in [0x4320,0x4b00]:self.device.write(0xf03204,command)
   if pc==0xdf6a or(pc==0xde5a and self.lib.m68k_get_reg(None,16)!=0xdf66):
    handoffs.append({'context':int.from_bytes(self.device.ram()[0xc0920:0xc0924],'big'),'PC':self.lib.m68k_get_reg(None,16),'SP':self.lib.m68k_get_reg(None,15)})
  else:raise AssertionError('Original three-task run did not resume the main loop')
  for target in stubs:self.device.direct(target,2,int.from_bytes(ram[target:target+2],'big'))
  final=scheduler.CPU();final.registers[:]=[self.lib.m68k_get_reg(None,i)for i in range(16)];final.pc=self.lib.m68k_get_reg(None,16);final.sr=self.lib.m68k_get_reg(None,17);final.usp=final.registers[15];final.ssp=self.prefix[17]
  metadata={'calls':calls,'handoffs':handoffs,'yields':yields,'PCs':steps,'world_body_calls':bodies,'device':self.device.stats(),'dispatch_states':dispatch_states}
  if input_backend is not None:metadata['pad_input']={'samples':list(input_backend.samples),'raw_reads':list(input_backend.raw_reads),'selects':list(input_backend.selects)}
  if animation_backend is not None:metadata['animation_environment_events']=list(animation_backend.events)
  return self.device.ram(),self.device.registers(),final,metadata

def probe():
 old=json.loads((ROOT/'verification/biwn-world-cleanup-pipeline-checks.json').read_text());rows=json.loads((Path(old['directory'])/'fixtures.json').read_text());snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=Native();out=ROOT/'verification/task-runtime-native-probe';out.mkdir(exist_ok=True)
 try:
  results=[]
  for index in [0,12,35,56,85,150]:
   case=fixture(rows[index]['parameters'],index);script=previous.prior.previous.Script(snapshot,case);ram,regs,cpu,meta=native.run(script,[0x12340000+i for i in range(16)]);results.append({'case':index,'CPU':scheduler.cpu_dict(cpu),'metadata':meta,'parameters':case})
   print(index,len(meta['PCs']),len(meta['handoffs']),meta['yields'][:4],flush=True)
  (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 finally:native.close()
if __name__=='__main__':probe()
