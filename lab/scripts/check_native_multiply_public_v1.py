"""E540 public native-entry prototype with the existing guarded task arena.
Compare full original return/publicRAM and exact guest bus order, declaring
only the bridge's single task-pointer lookup as extra runtime metadata read.
No disc/global redirection, arbitrary aliases, IRQ or gameplay proof.
"""
import ctypes as c,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_native_multiply_context_v1 as contract
h=contract.h;ROOT=h.ROOT;V=ROOT/'verification';SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v14-public-multiply';CODE=0x180000;ARENA=0x160000;POOL=0xc0928;SLOTS=101;STRIDE=1024
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return h.sha(Path(p).read_bytes())
def main():
 out=V/'native-multiply-public-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,fallbacks=0,new_predictions=0,new_training=False,disc_changed=False)
 def mark():save(out/'protocol.json',state);save(V/'native-multiply-public-v1-current.json',state)
 mark();build=out/'build';compiled=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
 payload=(build/'native-shared.bin').read_bytes();symbols={line.split()[-1]:int(line.split()[0],16)for line in (build/'symbols.txt').read_text().splitlines()if len(line.split())==3};entry=symbols['biwn_v14_multiply'];h.RANGES[0xe540]=0xe588;e=h.Engine();rows=[];guards=[]
 def ordered(memory,initial,start):
  u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,memory);u.reg_write(UC_M68K_REG_SR,initial.sr)
  for reg,value in zip(contract.REGS,initial.registers):u.reg_write(reg,value)
  events=[];lookup=[]
  def private(a,w):return ARENA<=a and a+w<=ARENA+SLOTS*STRIDE
  def rd(uc,access,a,w,value,data):
   if not private(a,w):
    event=['r',a,w,int.from_bytes(u.mem_read(a,w),'big')]
    if start==entry and a==0xc0920 and w==4:lookup.append(event)
    else:events.append(event)
  def wr(uc,access,a,w,value,data):
   if not private(a,w):events.append(['w',a,w,value&((1<<(8*w))-1)])
  u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start(start,h.STOP,count=10000,timeout=1000000);assert u.reg_read(UC_M68K_REG_PC)==h.STOP;assert len(lookup)==(1 if start==entry else 0);return events
 try:
  for ram,initial,case in contract.fixtures():
   i=case['variant'];task=POOL+(i%SLOTS)*STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3];s=h.CPU.from_buffer_copy(bytes(initial));s.registers[15]=sp
   if s.sr&0x2000:s.ssp=sp
   else:s.usp=sp
   modes=['native']+(['busy','low','unaligned','high','allbits']if i<64 else[])
   for mode in modes:
    memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE);memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');memory[sp-64:sp+32]=ram[contract.GSP-64:contract.GSP+32]
    for slot in range(SLOTS):memory[ARENA+slot*STRIDE+16+114:ARENA+slot*STRIDE+16+118]=bytes(4)
    selected={'native':task,'busy':task,'low':POOL-4,'unaligned':task+2,'high':POOL+SLOTS*STRIDE,'allbits':0xffffffff}[mode];memory[0xc0920:0xc0924]=selected.to_bytes(4,'big');base=ARENA+(i%SLOTS)*STRIDE
    if mode=='busy':memory[base+16+114:base+16+118]=(1).to_bytes(4,'big')
    memory=bytes(memory);expected,cpu,_,_,_=e.original(memory,s,case);e.native.device.seed(memory,0);physical=h.CPU.from_buffer_copy(bytes(s));physical.pc=entry;e.set_cpu(physical,True);low=1008;original_steps=0
    for step in range(10000):
     pc=e.core.m68k_get_reg(None,16);at=e.core.m68k_get_reg(None,15)
     if pc==h.STOP:break
     if 0xe540<=pc<0xe588:original_steps+=1
     if ARENA<=at<ARENA+SLOTS*STRIDE:low=min(low,at-base)
     else:assert sp-2<=at<=sp+4,('SP outside task/native arena',i,mode,hex(at))
     assert CODE<=pc<CODE+len(payload)or(mode!='native'and 0xe54a<=pc<0xe588),('original/escaped',i,mode,hex(pc));e.core.m68k_execute(1)
    else:raise AssertionError(('no return',i,mode))
    actual=e.native.device.ram();got=e.cpu();assert h.cpu_dict(got)==h.cpu_dict(cpu),('fullCPU',case,mode,h.cpu_dict(got),h.cpu_dict(cpu));a=bytearray(actual);b=bytearray(expected);a[ARENA:ARENA+SLOTS*STRIDE]=b[ARENA:ARENA+SLOTS*STRIDE]=memory[ARENA:ARENA+SLOTS*STRIDE];assert a==b,('publicRAM',i,mode)
    assert actual[CODE:CODE+len(payload)]==payload
    if mode=='native':
     assert low>=832 and original_steps==0
     assert actual[ARENA:base]==memory[ARENA:base]and actual[base+STRIDE:ARENA+SLOTS*STRIDE]==memory[base+STRIDE:ARENA+SLOTS*STRIDE]
     for lo,hi in [(0,16),(134,832),(1008,1024)]:assert actual[base+lo:base+hi]==memory[base+lo:base+hi],('private guard',i,lo)
     assert actual[base+130:base+134]==bytes(4)
    else:assert actual[ARENA:ARENA+SLOTS*STRIDE]==memory[ARENA:ARENA+SLOTS*STRIDE]and original_steps>0
    events=ordered(memory,s,entry);original_events=ordered(memory,s,0xe540);assert events==original_events,('guestbusorder',i,mode)
    row=dict(case=i,mode=mode,C_stack_bytes=1008-low,original_steps=original_steps,guest_bus_events=len(events),task_metadata_reads=1,full_CPU_public_stack_RAM_and_order_match=True)
    if mode=='native':rows.append(row)
    else:guards.append(row)
   if len(rows)%128==0:state.update(status='checking',completed=len(rows),fallbacks=len(guards));mark();print('completed',len(rows),flush=True)
 finally:e.native.close()
 assert len(rows)==2192 and len(guards)==320;save(out/'cases.json',rows);save(out/'fallbacks.json',guards);paths=[Path(__file__),Path(contract.__file__),*SRC.glob('native-shared.*'),*SRC.glob('*.inc'),SRC/'native-alu.h',SRC/'Makefile',build/'native-shared.bin',out/'cases.json',out/'fallbacks.json'];state.update(status='terminal_public_native_multiply_2192_and_320_guarded_fallbacks_match',completed=len(rows),fallbacks=len(guards),module_bytes=len(payload),payload=str(build/'native-shared.bin'),payload_sha256=sha(build/'native-shared.bin'),symbols=symbols,maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Publicentryusesoutput-onlyregisterstemporarily;noextraoriginalgueststackspill. Original2bytesignscratch isstrictlycompared. Guardcasescoverbothmodes/allCCR,busyframe,belowpool,unaligned,onepastpool andallbits pointers. Privatearena alone normalized;fallback cannotchangeanyarenabyte. No naturally reached globalredirect oraliases/IRQ proof.');mark();print(state['status'],flush=True)
if __name__=='__main__':main()
