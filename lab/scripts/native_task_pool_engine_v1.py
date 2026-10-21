"""Whole DD40..DDCC initialization: ordered RAM/USP effects and native mode switch.
Supervisor entry, no asynchronous IRQ/GPU/frame execution. Private SSP frame,
installed code and the8byte entry patch are the only RAM exclusions.
"""
import copy,random
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_scheduler import Native
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';BASE=0x180000;ENTRY=0xdd40;PRE_END=0xddc4;END=0xddcc
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
def cases():
 rng=random.Random(0xdd40);rows=[]
 for variant in range(2):
  for priority in range(8):
   for flags in range(32):rows.append(dict(variant=variant,ssp=0x1ff000-variant*0x1000,usp=rng.getrandbits(32),sr=0x2000|(priority<<8)|flags,incoming=[rng.getrandbits(32)for _ in range(15)]))
 return rows
def seed(snapshot,case,payload,symbols,compiled):
 m=bytearray(snapshot);m[BASE:BASE+len(payload)]=payload
 if case['variant']:
  lo,hi=0xc0920,0xd9d28;m[lo:hi]=bytes((i*53+case['sr']+11)&255 for i in range(hi-lo))
 if compiled:m[ENTRY:ENTRY+8]=b'\x4e\xf9'+symbols['biwn_native_task_pool_initialize'].to_bytes(4,'big')+b'\x4e\x71'
 return m
def normalize(memory,snapshot,case,length):
 m=bytearray(memory)
 for lo,hi in [(BASE,BASE+length),(case['ssp']-4096,case['ssp']),(ENTRY,ENTRY+8)]:m[lo:hi]=snapshot[lo:hi]
 return bytes(m)
def execute(snapshot,case,payload,symbols,compiled):
 m=seed(snapshot,case,payload,symbols,compiled);u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(m));u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,case['ssp']);u.reg_write(UC_M68K_REG_CR_USP,case['usp'])
 for reg,value in zip(REGS,case['incoming']):u.reg_write(reg,value)
 trace=[];steps=[];coverage=set();minimum=case['ssp'];stop=symbols['biwn_native_task_pool_switch']if compiled else PRE_END
 def private(a,w):return(case['ssp']-4096<=a and a+w<=case['ssp'])or(BASE<=a and a+w<=BASE+len(payload))
 def code(cpu,pc,width,_):
  nonlocal minimum
  minimum=min(minimum,cpu.reg_read(UC_M68K_REG_A7));steps.append(pc)
  if compiled:assert pc==ENTRY or BASE<=pc<BASE+len(payload),('Original initializer fallback',hex(pc))
  else:assert ENTRY<=pc<PRE_END;coverage.add(pc)
  if pc==(symbols['biwn_native_task_pool_set_usp_instruction']if compiled else 0xddaa):trace.append(['USP',cpu.reg_read(UC_M68K_REG_A0 if compiled else UC_M68K_REG_A1)])
 def read(cpu,kind,a,w,v,_):
  if not private(a,w):trace.append(['r',a,w,int.from_bytes(cpu.mem_read(a,w),'big')])
 def write(cpu,kind,a,w,v,_):
  if not private(a,w):trace.append(['w',a,w,v&((1<<(8*w))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(ENTRY,stop,count=100000,timeout=5000000);assert u.reg_read(UC_M68K_REG_PC)==stop and u.reg_read(UC_M68K_REG_A7)==case['ssp'];ram=bytes(u.mem_read(0,0x200000));assert ram[BASE:BASE+len(payload)]==payload
 return dict(ram=normalize(ram,snapshot,case,len(payload)),registers=[u.reg_read(reg)for reg in REGS],USP=u.reg_read(UC_M68K_REG_CR_USP),trace=trace,machine=steps,coverage=coverage,private_depth=case['ssp']-minimum)
def replay(native,snapshot,case,payload,symbols,compiled,expected):
 m=seed(snapshot,case,payload,symbols,compiled);native.device.seed(bytes(m),0);l=native.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0);l.m68k_set_reg(15,case['usp']);l.m68k_set_reg(17,case['sr']);l.m68k_set_reg(15,case['ssp'])
 for i,value in enumerate(case['incoming']):l.m68k_set_reg(i,value)
 l.m68k_set_reg(16,ENTRY)
 def reg(i):return l.m68k_get_reg(None,i)
 for index,pc in enumerate(expected['machine']):assert reg(16)==pc,(index,hex(reg(16)),hex(pc));l.m68k_execute(1)
 assert reg(16)==(symbols['biwn_native_task_pool_switch']if compiled else PRE_END);assert normalize(native.device.ram(),snapshot,case,len(payload))==expected['ram'];assert[reg(i)for i in range(15)]==expected['registers'];pre=dict(registers=[reg(i)for i in range(16)],SR=reg(17),USP=native.prefix[16],SSP=reg(15));assert pre['USP']==0xc0d28
 tail=[]
 for _ in range(8):
  pc=reg(16)
  if pc==END:break
  assert(BASE<=pc<BASE+len(payload))if compiled else PRE_END<=pc<END;tail.append(pc);l.m68k_execute(1)
 else:raise AssertionError('Native mode transition did not reach DDCC')
 assert reg(16)==END;sr=reg(17);final=dict(registers=[reg(i)for i in range(16)],PC=reg(16),SR=sr,USP=reg(15)if not sr&0x2000 else native.prefix[16],SSP=native.prefix[17]if not sr&0x2000 else reg(15));assert normalize(native.device.ram(),snapshot,case,len(payload))==expected['ram'];return dict(pre=pre,final=final,tail_steps=tail)
