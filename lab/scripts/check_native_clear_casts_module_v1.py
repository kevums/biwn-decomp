"""Exact shared-module cast clear across260originalCPU/order boundary cases.
The production internal callee is specialized by LTO to a constant65536budget;
dynamic budget failures are qualified in the separate standalone35case gate.
"""
import ctypes as c,json,os,struct
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;V=ROOT/'verification';CODE=0x180000;ARENA=0x160000;SLOTS=101;STRIDE=1024
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return h.sha(Path(p).read_bytes())
def pack(s):return struct.pack('>19IH',*s.registers,s.pc,s.usp,s.ssp,s.sr)
def unpack(raw):
 v=struct.unpack('>19IH',raw);s=h.CPU();s.registers[:]=v[:16];s.pc,s.usp,s.ssp,s.sr=v[16:];return s
def main():
 gp=V/'native-Deck-clear-casts-v1-current.json';g=read(gp);assert g['completed']==256
 for p,digest in g['source_sha256'].items():assert sha(p)==digest,p
 out=V/'native-clear-casts-module-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='checking',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,disc_changed=False)
 def mark():save(out/'protocol.json',state);save(V/'native-clear-casts-module-v1-current.json',state)
 mark();payload=Path(g['payload']).read_bytes();matches=[(n,a)for n,a in g['symbols'].items()if n.startswith('native_clear_records')];assert len(matches)==1 and 'constprop'in matches[0][0];symbol,entry=matches[0];engine=h.Engine();rows=[]
 def ordered(memory,initial,start,stop):
  u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,memory);u.reg_write(UC_M68K_REG_SR,initial.sr)
  for reg,value in zip(REGS,initial.registers):u.reg_write(reg,value)
  events=[]
  def public(a,w):return not(ARENA<=a and a+w<=ARENA+SLOTS*STRIDE)
  def rd(uc,access,a,w,value,data):
   if public(a,w):events.append(['r',a,w,int.from_bytes(u.mem_read(a,w),'big')])
  def wr(uc,access,a,w,value,data):
   if public(a,w):events.append(['w',a,w,value&((1<<(8*w))-1)])
  u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start(start,stop,count=4000000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==stop;return events
 try:
  for ram,initial,case in h.fixtures():
   if case['root']!=0x10968:continue
   i=case['variant'];memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE);memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');base=ARENA+(i%SLOTS)*STRIDE;frame=base+16;csp=base+992
   memory[frame:frame+98]=struct.pack('>I',0)+pack(initial)+struct.pack('>4I',0x12345678,frame,7,0);memory[csp:csp+8]=struct.pack('>2I',h.STOP,frame);memory=bytes(memory)
   physical=h.CPU();physical.registers[:]=[(0x1234567*(n+1))&0xffffffff for n in range(15)]+[csp];physical.pc=entry;physical.sr=initial.sr&0x2000;physical.usp=0x1d8000 if physical.sr else csp;physical.ssp=csp if physical.sr else 0x1ff000
   expected,cpu,_,_,_=engine.original(memory,initial,case);cpu.pc=0x1098e;cpu.registers[15]=initial.registers[15]
   if cpu.sr&0x2000:cpu.ssp=initial.registers[15]
   else:cpu.usp=initial.registers[15]
   engine.native.device.seed(memory,0);engine.set_cpu(physical,True)
   for chunk in range(5000):
    engine.core.m68k_execute(10000)
    if engine.cpu().pc==h.STOP:break
   else:raise AssertionError('Shared clear work limit')
   actual=engine.native.device.ram();done=engine.cpu();assert done.registers[15]==csp+4
   for index in [*range(2,8),*range(10,15)]:assert done.registers[index]==physical.registers[index],('C ABI',i,index)
   got=unpack(actual[frame+4:frame+82]);assert h.cpu_dict(got)==h.cpu_dict(cpu),('raw CPU',i);assert actual[frame+82:frame+98]==memory[frame+82:frame+98]
   assert actual[CODE:CODE+len(payload)]==payload
   assert actual[ARENA:base]==memory[ARENA:base]and actual[base+STRIDE:ARENA+SLOTS*STRIDE]==memory[base+STRIDE:ARENA+SLOTS*STRIDE]
   for lo,hi in [(0,16),(134,832),(1000,1024)]:assert actual[base+lo:base+hi]==memory[base+lo:base+hi],('private fence',i,lo)
   def normalize(raw):
    b=bytearray(raw);b[ARENA:ARENA+SLOTS*STRIDE]=memory[ARENA:ARENA+SLOTS*STRIDE];return bytes(b)
   assert normalize(actual)==normalize(expected),('public RAM',i)
   events=ordered(memory,physical,entry,h.STOP);original_events=ordered(memory,initial,0x10968,0x1098e);assert events==original_events,('ordered original accesses',i)
   rows.append(dict(case=i,events=len(events),CPU_RAM_order_C_ABI_and_private_fences_match=True))
   if len(rows)%16==0:state['completed']=len(rows);mark();print('completed',len(rows),flush=True)
 finally:engine.native.close()
 assert len(rows)==260;save(out/'cases.json',rows);paths=[Path(__file__),gp,Path(g['payload']),out/'cases.json'];state.update(status='terminal_exact_shared_cast_clear_260_original_CPU_RAM_order_ABI_match',completed=len(rows),symbol=symbol,module_bytes=g['code_bytes'],payload_sha256=g['payload_sha256'],source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Actual pinned68000 plus independentUnicorn runs of exact new function and originalhelper;allCCR/bothbanks/large signedboundaries. Only privatearena normalized;logical originalRTSpop reversed. No arbitrary aliases,IRQ,finaldisc orfreshfidelity claim.');mark();print(state['status'],flush=True)
if __name__=='__main__':main()
