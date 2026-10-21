"""Complete1102A reset body vs original68000: CPU/publicRAM and ordered widths.
Successful direct RAM, descriptor/global/guest-return alias cases, no IRQ/disc proof.
"""
import argparse,ctypes as c,json,os,random,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.m68k_const import *
import check_native_multiply_context_v1 as prior
h=prior.h;ROOT=h.ROOT;V=ROOT/'verification';SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v18-scene-reset'
CODE=prior.CODE;DATA=prior.DATA;CSP=prior.CSP;GSP=prior.GSP;REGS=prior.REGS;save=prior.save;sha=prior.sha;pack=prior.pack;unpack=prior.unpack
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1102a18)
 bases=[0x80000,0x90000,0x400e4,0x400e8,0x400ec,0x47b84,0x47b8c,0x403fe,0x10080000,GSP-4]
 pointers=[base for base in bases for _ in range(64)]+[0x70000+2*rng.randrange(0x10000)for _ in range(128)]
 for i,base in enumerate(pointers):
  s=h.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[GSP];s.pc=0x1102a;s.sr=(0x2000 if i&1 else 0)|((i//2)%32)|(((i//64)%8)<<8);s.usp=0x1d8000 if i&1 else GSP;s.ssp=GSP if i&1 else 0x1ff000
  m=bytearray(baseline)
  for lo,hi in [(0x47b88,0x47be0),(0x400e0,0x40108),(0x40400,0x4040e),(GSP-64,GSP+32)]:m[lo:hi]=rng.randbytes(hi-lo)
  physical=base&0xffffff;m[physical+4:physical+16]=rng.randbytes(12);m[0x400e6:0x400ea]=base.to_bytes(4,'big');m[GSP:GSP+4]=h.STOP.to_bytes(4,'big')
  yield bytes(m),s,dict(root=0x1102a,variant=i,descriptor=hex(base))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=SRC/'native-scene-reset.inc');ap.add_argument('--output',type=Path);ap.add_argument('--family',default='native-scene-reset-context-v1');args=ap.parse_args();assert args.family.replace('-','').isalnum()
 out=args.output or V/args.family/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,disc_changed=False)
 def mark():save(out/'protocol.json',state);save(V/(args.family+'-current.json'),state)
 mark();source=out/'wrapper.c';source.write_text('#include "'+str(SRC.parent.parent/'experimental/deck-scene-source/deck-scene-contract.h')+'"\n'+r'''
static inline uint32_t deeper_read(struct biwn_deck_context *s,uint32_t a,unsigned w){if(s->error)return 0;a&=0xffffffu;return w==2?*(volatile uint16_t *)a:*(volatile uint32_t *)a;}
static inline void deeper_write(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v){if(s->error)return;a&=0xffffffu;if(w==2)*(volatile uint16_t *)a=(uint16_t)v;else *(volatile uint32_t *)a=v;}
'''+ '#include "'+str(args.source.resolve())+'"\n'+r'''
#include <stddef.h>
void *memcpy(void *o,const void *in,size_t n){unsigned char *d=o;const unsigned char *p=in;while(n--)*d++=*p++;return o;}
int run(struct biwn_task_cpu *cpu){struct biwn_deck_context s;s.cpu=*cpu;s.error=0;native_scene_reset_context(&s);if(s.error)return s.error;s.cpu.pc=deeper_read(&s,s.cpu.registers[15],4);s.cpu.registers[15]+=4;deck_bank(&s);*cpu=s.cpu;return 0;}
''')
 tool=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');elf=out/'reset.elf';binary=out/'reset.bin';command=[tool+'gcc','-m68000','-msoft-float','-std=c11','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-Dinline=inline __attribute__((always_inline))','-Wl,-Ttext='+hex(CODE)+',--entry,run',str(source),'-o',str(elf)];a=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(a.stdout+a.stderr);assert a.returncode==0,a.stderr
 subprocess.run([tool+'objcopy','-O','binary',str(elf),str(binary)],check=True);payload=binary.read_bytes();symbols=subprocess.check_output([tool+'nm','-n',str(elf)],text=True);entry=next(int(x.split()[0],16)for x in symbols.splitlines()if x.endswith(' run'));subprocess.run([tool+'objdump','-dr',str(elf)],stdout=(out/'disassembly.txt').open('w'),check=True)
 h.RANGES[0x1102a]=0x110d4;engine=h.Engine();rows=[];coverage=set()
 def private(a,w):return DATA<=a and a+w<=DATA+78 or CSP-2048<=a and a+w<=CSP+8
 def ordered(memory,initial,start):
  u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,memory);u.reg_write(UC_M68K_REG_SR,initial.sr)
  descriptor=int.from_bytes(memory[0x400e6:0x400ea],'big')
  if descriptor>>24:
   # Unicorn has a 32-bit mapping even with the68000 model. Only this
   # read-only descriptor alias is additionally mapped; physical bus event
   # addresses below are masked to the original24-bit address bus.
   alias_page=descriptor&~4095;physical_page=alias_page&0xffffff
   u.mem_map(alias_page,4096);u.mem_write(alias_page,memory[physical_page:physical_page+4096])
  for reg,value in zip(REGS,initial.registers):u.reg_write(reg,value)
  events=[];raw_events=[];implicit=[]
  def rd(uc,access,a,w,value,data):
   a&=0xffffff
   if not private(a,w):
    event=['r',a,w,int.from_bytes(u.mem_read(a,w),'big')];events.append(event);raw_events.append(event)
  def wr(uc,access,a,w,value,data):
   a&=0xffffff
   if not private(a,w):
    event=['w',a,w,value&((1<<(8*w))-1)];events.append(event);raw_events.append(event)
  def instruction(uc,pc,size,data):
   # M68000PRM section4-74: memory CLR reads before clearing. Unicorn
   # omits this dummy read; expand only decoded CLR memory instructions,
   # identically in both lanes. No CPU or memory state is modified here.
   op=int.from_bytes(u.mem_read(pc,2),'big')
   if op&0xff00!=0x4200:return
   widthcode=(op>>6)&3;mode=(op>>3)&7;reg=op&7
   if mode==0:return
   assert widthcode in [1,2],('unexpected CLR width',hex(pc),hex(op));w=2 if widthcode==1 else 4
   if mode==2:a=u.reg_read(REGS[8+reg])
   elif mode==5:
    displacement=int.from_bytes(u.mem_read(pc+2,2),'big',signed=True);a=u.reg_read(REGS[8+reg])+displacement
   elif mode==7 and reg==1:a=int.from_bytes(u.mem_read(pc+2,4),'big')
   else:raise AssertionError(('unhandled CLR EA',hex(pc),hex(op)))
   a&=0xffffff
   if not private(a,w):
    event=['r',a,w,int.from_bytes(u.mem_read(a,w),'big')];events.append(event);implicit.append(dict(PC=hex(pc),event=event))
  u.hook_add(UC_HOOK_CODE,instruction);u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start(start,h.STOP,count=10000,timeout=1000000);assert u.reg_read(UC_M68K_REG_PC)==h.STOP;return events,raw_events,implicit
 try:
  for ram,initial,case in fixtures():
   memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');memory[DATA:DATA+78]=pack(initial);memory[CSP:CSP+8]=struct.pack('>2I',h.STOP,DATA);memory=bytes(memory);expected,cpu,_,seen,_=engine.original(memory,initial,case);coverage|=seen
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
   events,raw_events,implicit=ordered(memory,physical,entry);original_events,original_raw,original_implicit=ordered(memory,initial,0x1102a)
   if events!=original_events or raw_events!=original_raw:save(out/'order-mismatch.json',dict(case=case,expected=original_events,actual=events,raw_expected=original_raw,raw_actual=raw_events));raise AssertionError(('order',case))
   assert len(implicit)==len(original_implicit)==19
   if case['variant']==0:save(out/'ordered-case-zero.json',dict(raw_unicorn_events=raw_events,hardware_expanded_events=events,original_CLR=original_implicit,native_CLR=implicit))
   rows.append(dict(case=case,public_bus_events=len(events),raw_Unicorn_events=len(raw_events),hardware_CLR_reads_expanded_each_lane=19,full_CPU_public_RAM_order_and_C_ABI_match=True))
   if len(rows)%128==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
 finally:engine.native.close()
 assert len(rows)==768;expected_locations={x.address for x in h.Cs(h.CS_ARCH_M68K,h.CS_MODE_BIG_ENDIAN|h.CS_MODE_M68K_000).disasm((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x1102a:0x110d4],0x1102a)};assert coverage==expected_locations
 save(out/'cases.json',rows);paths=[Path(__file__),args.source,source,binary,Path(h.__file__),out/'cases.json',out/'ordered-case-zero.json'];state.update(status='terminal_reset_complete_768_CPU_RAM_order_C_ABI_cases_match',completed=len(rows),instruction_locations=[len(coverage),len(expected_locations)],payload=str(binary),payload_sha256=sha(binary),source_sha256={str(p):sha(p)for p in paths},CLR_trace_expansion=dict(manual='https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf',section='4-74',raw_Unicorn_omits_CLR_reads=True,applied_symmetrically_to_both_lanes=True,expected_public_CLR_instructions=19),scope=__doc__+'640critical descriptor/alias cases acrossall32CCR/bothmodes,128seededrandom descriptors,alloriginalinstructionlocations. RawUnicorn data events compare;bothlanes also expand19physicalCLRdummyreads according toM68000manual anddecodednativeopcode. No memory/CPUmutation bytraceobserver. LogicalCPUbanks/PC/SR and public2MBRAM compare; only test CPU buffer/Cstack excluded. Extra gueststackwrites absent. No host bus-error/IRQ/physicalgameclaim.');mark();print(state['status'],flush=True)
if __name__=='__main__':main()
