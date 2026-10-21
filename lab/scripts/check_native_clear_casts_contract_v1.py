"""Native clear-loop source versus original68000 and retained callback contract.
Full helper input matrix,budget boundaries and native public data-access traces.
Only the target's successful direct bus is exercised;host callback failures remain
in the unchanged portable implementation. No arbitrary aliases,IRQ or disc claim.
"""
import argparse,ctypes as c,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;V=ROOT/'verification';SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v12-clear-casts'
CODE=0x180000;DATA=0x1a0000;CSP=0x1f4000;STOP=h.STOP
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return h.sha(Path(p).read_bytes())
def pack(s):return struct.pack('>19IH',*s.registers,s.pc,s.usp,s.ssp,s.sr)
def unpack(raw):
 values=struct.unpack('>19IH',raw);s=h.CPU();s.registers[:]=values[:16];s.pc,s.usp,s.ssp,s.sr=values[16:];return s
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=V/'native-clear-casts-contract-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',pid=os.getpid(),directory=str(out),new_predictions=0,new_training=False,native_disc_changed=False)
 def mark():save(out/'protocol.json',state);save(V/'native-clear-casts-contract-v1-current.json',state)
 mark()
 try:
  source=out/'native-clear-wrapper.c';source.write_text('#include "'+str(SRC.parent.parent/'experimental/deck-scene-source/deck-scene-contract.h')+'"\n#include "'+str(SRC/'native-alu.h')+'"\n'+r'''
#define deck_nz native_deck_nz
#define deck_alu native_deck_alu
#define scene_alu16 native_scene_alu16
#define scene_shift native_scene_shift
static inline uint32_t deeper_read(struct biwn_deck_context *s,uint32_t a,unsigned w){
 if(s->error)return 0;a&=0xffffffu;return w==2?*(volatile uint16_t *)a:*(volatile uint32_t *)a;
}
'''+ '#include "'+str(SRC/'native-clear-stages.inc')+'"\n'+r'''
#include <stddef.h>
void *memcpy(void *out,const void *in,size_t n){unsigned char *d=out;const unsigned char *p=in;while(n--)*d++=*p++;return out;}
_Static_assert(sizeof(struct biwn_task_cpu)==78,"CPU layout");
int run(struct biwn_task_cpu *cpu,uint32_t budget){
 struct biwn_deck_context s;s.cpu=*cpu;s.error=0;
 native_clear_records(&s,budget);
 if(s.error)return s.error;
 s.cpu.pc=deeper_read(&s,s.cpu.registers[15],4);s.cpu.registers[15]+=4;deck_bank(&s);*cpu=s.cpu;return 0;
}
''')
  tool=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');elf=out/'native-clear.elf';binary=out/'native-clear.bin'
  command=[tool+'gcc','-m68000','-msoft-float','-std=c11','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Dinline=inline __attribute__((always_inline))','-Wl,-Ttext='+hex(CODE)+',--entry,run',str(source),'-o',str(elf)]
  p=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
  subprocess.run([tool+'objcopy','-O','binary',str(elf),str(binary)],check=True);payload=binary.read_bytes();syms=subprocess.check_output([tool+'nm','-n',str(elf)],text=True);entry=next(int(x.split()[0],16)for x in syms.splitlines()if x.endswith(' run'))
  subprocess.run([tool+'objdump','-dr',str(elf)],stdout=(out/'disassembly.txt').open('w'),check=True)
  library=out/'portable-reference.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(h.SRC),str(h.SRC/'coordinator-reference.c'),str(h.SRC/'helper-adapter.c'),'-o',str(library)],capture_output=True,text=True);(out/'portable-compiler.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
  fn=c.CDLL(str(library)).biwn_geometry_helper_call;fn.argtypes=[c.POINTER(h.Bus),h.W8,c.POINTER(h.CPU),h.SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int
  engine=h.Engine();rows=[];guards=[];traces=[]
  def prepare(ram,initial,budget):
   memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[STOP:STOP+2]=bytes.fromhex('60fe');memory[DATA:DATA+78]=pack(initial);memory[CSP:CSP+12]=struct.pack('>3I',STOP,DATA,budget);return bytes(memory)
  def normalize(raw,initial_memory):
   memory=bytearray(raw);memory[DATA:DATA+78]=initial_memory[DATA:DATA+78];memory[CSP-2048:CSP+12]=initial_memory[CSP-2048:CSP+12];return bytes(memory)
  def native(ram,initial,budget):
   engine.native.device.seed(ram,0);physical=h.CPU();physical.registers[15]=CSP;physical.pc=entry;physical.sr=initial.sr&0x2000;physical.usp=0x1d0000 if physical.sr else CSP;physical.ssp=CSP if physical.sr else 0x1ff000;engine.set_cpu(physical,True)
   for n in range(5000):
    engine.core.m68k_execute(10000)
    if engine.cpu().pc==STOP:break
   else:raise AssertionError(('native bound',hex(engine.cpu().pc)))
   memory=engine.native.device.ram();assert memory[CODE:CODE+len(payload)]==payload;assert memory[CSP-2064:CSP-2048]==ram[CSP-2064:CSP-2048]
   return engine.cpu().registers[0],normalize(memory,ram),unpack(memory[DATA:DATA+78]),n+1
  def ordered(ram,initial,budget):
   u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,ram);u.reg_write(UC_M68K_REG_SR,initial.sr&0x2000);u.reg_write(UC_M68K_REG_A7,CSP);events=[]
   def public(a,w):return not(DATA<=a and a+w<=DATA+78 or CSP-2048<=a and a+w<=CSP+12)
   def on_read(uc,access,a,w,value,data):
    if public(a,w):events.append(['r',a,w,int.from_bytes(u.mem_read(a,w),'big')])
   def on_write(uc,access,a,w,value,data):
    if public(a,w):events.append(['w',a,w,value&((1<<(8*w))-1)])
   u.hook_add(UC_HOOK_MEM_READ,on_read);u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.emu_start(entry,STOP,count=4000000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
   return events
  try:
   for ram,initial,case in h.fixtures():
    if case['root']!=0x10968:continue
    i=case['variant']
    if args.limit and i>=args.limit:continue
    memory=prepare(ram,initial,65536);expected,cpu,_,_,steps=engine.original(memory,initial,case)
    status,actual,got,chunks=native(memory,initial,65536)
    if status or normalize(expected,memory)!=actual or h.cpu_dict(cpu)!=h.cpu_dict(got):
     save(out/'counterexample.json',dict(case=case,status=status,expected_CPU=h.cpu_dict(cpu),native_CPU=h.cpu_dict(got),RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(normalize(expected,memory),actual))if x!=y][:40]));raise AssertionError(out/'counterexample.json')
    # Independent generated-ISA trace vs retained ordered callback contract.
    result=engine.translated(fn,memory,initial,case);assert result[0]==0 and not result[-1]and h.cpu_dict(result[2])==h.cpu_dict(cpu)
    events=ordered(memory,initial,65536)
    if events!=result[4]:save(out/'trace-mismatch.json',dict(case=case,expected=result[4][:60],native=events[:60],counts=[len(result[4]),len(events)]));raise AssertionError(out/'trace-mismatch.json')
    traces.append(dict(case=i,events=len(events),sha256=h.sha(json.dumps(events).encode())))
    if i in [1,2,3,256,257,258,259]:
     # Zero budget is meaningful for this internal body,not the public wrapper.
     for budget in [1,63,64,65,127]:
      m=prepare(ram,initial,budget);reference=engine.translated(fn,m,initial,case,byte_budget=budget);status,actual,got,_=native(m,initial,budget)
      assert status==reference[0]and not reference[-1]and actual==normalize(reference[1],m)and h.cpu_dict(got)==h.cpu_dict(reference[2]),('budget',i,budget,status,reference[0])
      trace=ordered(m,initial,budget);assert trace==reference[4],('budget trace',i,budget);guards.append(dict(case=i,budget=budget,status=status,ordered_events=len(trace)))
    rows.append(dict(case=i,original_instructions=steps,native_execute_chunks=chunks,CPU_nonprivate_RAM_and_ordered_contract_match=True))
    if len(rows)%16==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
  finally:engine.native.close()
  save(out/'cases.json',rows);save(out/'budgets.json',guards);save(out/'ordered-traces.json',traces)
  paths=[Path(__file__),source,binary,SRC/'native-clear-stages.inc',SRC/'native-alu.h',h.SRC/'coordinator-reference.c',h.SRC/'helper-contract.h',h.SRC/'helper-adapter.c',Path(h.__file__),out/'cases.json',out/'budgets.json',out/'ordered-traces.json']
  state.update(status='terminal_clear_contract_preflight_pass'if args.limit else'terminal_native_clear_helper_CPU_RAM_budget_order_match',completed=len(rows),budget_cases=len(guards),ordered_cases=len(traces),source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' OriginalCPU is the pinned emulator;generated-ISA public byte/argument/RTS reads and writes use independentUnicorn hooks and the retained explicit CLR read-before-write callback contract. Native scratch CPU/context/Cstack alone are normalized. Standalone compilation of the exact native source;final-image ABI/relocation and fresh gameplay require their own gates.');mark();print(state['status'],len(rows),len(guards),flush=True)
 except BaseException as error:state.update(status='terminal_native_clear_contract_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
