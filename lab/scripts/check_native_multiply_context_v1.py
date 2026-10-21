"""Recovered E540 in the native software-CPU context vs original full return.
Exact public argument/sign-word/RTS bus order is checked independently in
Unicorn. Ordinary nonaliasing task RAM, successful bus, no IRQ/disc claim.
"""
import ctypes as c,json,os,random,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;V=ROOT/'verification';SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v13-multiply';CODE=0x180000;DATA=0x1a0000;CSP=0x1f4000;GSP=0x1e8000
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return h.sha(Path(p).read_bytes())
def pack(s):return struct.pack('>19IH',*s.registers,s.pc,s.usp,s.ssp,s.sr)
def unpack(raw):
 v=struct.unpack('>19IH',raw);s=h.CPU();s.registers[:]=v[:16];s.pc,s.usp,s.ssp,s.sr=v[16:];return s
def fixtures():
 values=[0,1,2,0x7fff,0x8000,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff,0xffff0000,0x8000ffff]
 critical=[(0,0),(0,1),(1,0),(1,1),(0xffffffff,1),(1,0xffffffff),(0xffffffff,0xffffffff),(0x80000000,1),(0x80000000,0xffffffff),(0x80000000,0x80000000),(0x7fffffff,2),(0x10000,0x10000),(0xffff,0xffff),(0x8000ffff,0xffff0000),(0x12345678,0x87654321),(0x7fffffff,0x7fffffff)]
 pairs=[pair for pair in critical for _ in range(64)]+[(a,b)for a in values for b in values];rng=random.Random(0xe54013);pairs +=[(rng.getrandbits(32),rng.getrandbits(32))for _ in range(1024)]
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
 for i,(a,b)in enumerate(pairs):
  s=h.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[GSP];s.pc=0xe540;s.sr=(0x2000 if i&1 else 0)|((i//2)%32)|(((i//64)%8)<<8);s.usp=0x1d8000 if i&1 else GSP;s.ssp=GSP if i&1 else 0x1ff000
  memory=bytearray(baseline);memory[GSP-64:GSP+32]=rng.randbytes(96);memory[GSP:GSP+12]=struct.pack('>3I',h.STOP,a,b)
  yield bytes(memory),s,dict(root=0xe540,variant=i,a=a,b=b)
def main():
 out=V/'native-multiply-context-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,disc_changed=False)
 def mark():save(out/'protocol.json',state);save(V/'native-multiply-context-v1-current.json',state)
 mark();source=out/'native-multiply-wrapper.c';source.write_text('#include "'+str(SRC.parent.parent/'experimental/deck-scene-source/deck-scene-contract.h')+'"\n'+r'''
static inline uint32_t deeper_read(struct biwn_deck_context *s,uint32_t a,unsigned w){if(s->error)return 0;a&=0xffffffu;return w==2?*(volatile uint16_t *)a:*(volatile uint32_t *)a;}
static inline void deeper_write(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v){if(s->error)return;a&=0xffffffu;if(w==2)*(volatile uint16_t *)a=(uint16_t)v;else *(volatile uint32_t *)a=v;}
'''+ '#include "'+str(SRC/'native-multiply-context.inc')+'"\n'+r'''
#include <stddef.h>
void *memcpy(void *out,const void *in,size_t n){unsigned char *d=out;const unsigned char *p=in;while(n--)*d++=*p++;return out;}
int run(struct biwn_task_cpu *cpu){struct biwn_deck_context s;s.cpu=*cpu;s.error=0;native_multiply_context(&s);if(s.error)return s.error;s.cpu.pc=deeper_read(&s,s.cpu.registers[15],4);s.cpu.registers[15]+=4;deck_bank(&s);*cpu=s.cpu;return 0;}
''')
 tool=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');elf=out/'native-multiply.elf';binary=out/'native-multiply.bin';command=[tool+'gcc','-m68000','-msoft-float','-std=c11','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-Dinline=inline __attribute__((always_inline))','-Wl,-Ttext='+hex(CODE)+',--entry,run',str(source),'-o',str(elf)];p=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr;subprocess.run([tool+'objcopy','-O','binary',str(elf),str(binary)],check=True);payload=binary.read_bytes();syms=subprocess.check_output([tool+'nm','-n',str(elf)],text=True);entry=next(int(x.split()[0],16)for x in syms.splitlines()if x.endswith(' run'));subprocess.run([tool+'objdump','-dr',str(elf)],stdout=(out/'disassembly.txt').open('w'),check=True)
 h.RANGES[0xe540]=0xe588;engine=h.Engine();rows=[]
 def private(a,w):return DATA<=a and a+w<=DATA+78 or CSP-2048<=a and a+w<=CSP+8
 def ordered(memory,initial,start):
  u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,memory);u.reg_write(UC_M68K_REG_SR,initial.sr)
  for reg,value in zip(REGS,initial.registers):u.reg_write(reg,value)
  events=[]
  def rd(uc,access,a,w,value,data):
   if not private(a,w):events.append(['r',a,w,int.from_bytes(u.mem_read(a,w),'big')])
  def wr(uc,access,a,w,value,data):
   if not private(a,w):events.append(['w',a,w,value&((1<<(8*w))-1)])
  u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start(start,h.STOP,count=10000,timeout=1000000);assert u.reg_read(UC_M68K_REG_PC)==h.STOP;return events
 try:
  for ram,initial,case in fixtures():
   memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');memory[DATA:DATA+78]=pack(initial);memory[CSP:CSP+8]=struct.pack('>2I',h.STOP,DATA);memory=bytes(memory);expected,cpu,_,_,steps=engine.original(memory,initial,case)
   physical=h.CPU();physical.registers[:]=[(0x1234567*(n+1))&0xffffffff for n in range(15)]+[CSP];physical.pc=entry;physical.sr=initial.sr&0x2000;physical.usp=0x1d8000 if physical.sr else CSP;physical.ssp=CSP if physical.sr else 0x1ff000;engine.native.device.seed(memory,0);engine.set_cpu(physical,True)
   for chunk in range(10):
    engine.core.m68k_execute(10000)
    if engine.cpu().pc==h.STOP:break
   else:raise AssertionError(('native bound',case))
   actual=engine.native.device.ram();done=engine.cpu();got=unpack(actual[DATA:DATA+78]);assert done.registers[0]==0 and done.registers[15]==CSP+4
   for index in [*range(2,8),*range(10,15)]:assert done.registers[index]==physical.registers[index],('C ABI',case,index)
   def normalize(raw):
    b=bytearray(raw);b[DATA:DATA+78]=memory[DATA:DATA+78];b[CSP-2048:CSP+8]=memory[CSP-2048:CSP+8];return bytes(b)
   if h.cpu_dict(got)!=h.cpu_dict(cpu)or normalize(actual)!=normalize(expected):save(out/'counterexample.json',dict(case=case,expected_CPU=h.cpu_dict(cpu),native_CPU=h.cpu_dict(got)));raise AssertionError(('CPU/RAM',case))
   assert actual[CODE:CODE+len(payload)]==payload and actual[CSP-2064:CSP-2048]==memory[CSP-2064:CSP-2048]
   events=ordered(memory,physical,entry);original_events=ordered(memory,initial,0xe540)
   if events!=original_events:save(out/'order-mismatch.json',dict(case=case,expected=original_events,actual=events));raise AssertionError(('order',case))
   rows.append(dict(case=case,original_instructions=steps,public_bus_events=len(events),full_CPU_public_RAM_order_and_C_ABI_match=True))
   if len(rows)%128==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
 finally:engine.native.close()
 assert len(rows)==2192;save(out/'cases.json',rows);paths=[Path(__file__),source,SRC/'native-multiply-context.inc',binary,Path(h.__file__),out/'cases.json'];state.update(status='terminal_native_multiply_context_2192_full_CPU_RAM_order_cases_match',completed=len(rows),payload=str(binary),payload_sha256=sha(binary),source_sha256={str(p):sha(p)for p in paths},scope=__doc__+'1024critical scalar/all32CCR/both-mode cases,144boundarygrid and1024seededrandom pairs. All logical D/A/PC/SR/USP/SSP and public stackbytes match. Physical callee-saved C registers and private fence preserved. No modelauthorship/adoption or sharedmodule integration implied.');mark();print(state['status'],flush=True)
if __name__=='__main__':main()
