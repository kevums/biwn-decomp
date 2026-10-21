"""New complete 1B160..1B1A0 formatting helper; full native CPU plus ordered bus."""
import argparse,hashlib,json,os,random,subprocess,shutil
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_native_resource_release import REGS
from check_biwn_scheduler import Native
from check_biwn_native_button_digit import ROOT,sha,save
BASE,ENTRY,END,SP,STOP=0x148000,0x1b160,0x1b1a0,0x1e0000,0x1f0000
def vectors():
 rng=random.Random(0x1b160);pairs=[(a,b)for a in [0,1,2,8,0x8000,0xffff]for b in [0,1,3,0x8000]]
 pairs += [(0x7fff,3),(254,255)]
 rows=[]
 for mode in [0,0x2000]:
  for flags in range(32):
   for i,(a,b)in enumerate(pairs):
    incoming=[rng.getrandbits(32)for _ in range(15)];incoming[2]=[0,1,0x80000000,0x7fffffff][(flags+i)%4]
    rows.append(dict(left=a,width=b,char=[0,255,0x1200,0x1234,0x8000][(flags+i)%5],incoming=incoming,sr=mode|flags))
  for flags in [0,16]:rows.append(dict(left=0x7fff,width=0x8000,char=0x12ff,incoming=[0x80000000]*15,sr=mode|flags))
 return rows
def seed(image,case):
 b=bytearray(image);b[0x120000:0x128000]=bytes([0xa5])*0x8000;b[0x130000:0x130002]=case['left'].to_bytes(2,'big')
 args=(STOP.to_bytes(4,'big')+(0x120000).to_bytes(4,'big')+case['char'].to_bytes(2,'big')+(0x130000).to_bytes(4,'big')+case['width'].to_bytes(2,'big'))
 b[SP:SP+len(args)]=args;return bytes(b)
def normalize(ram,ref,length):
 b=bytearray(ram)
 for a,z in [(BASE,length),(ENTRY,8),(SP-8192,8192-4)]:b[a:a+z]=ref[a:a+z]
 return bytes(b)
def allowed(pc,length,original):return ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length
def native(n,image,case,length,original):
 n.device.seed(seed(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
 supervisor=bool(case['sr']&0x2000);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if supervisor else 0x1ff000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fe000 if supervisor else SP);l.m68k_set_reg(17,case['sr'])
 for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
 l.m68k_set_reg(16,ENTRY);coverage=set()
 for _ in range(1000000):
  pc=l.m68k_get_reg(None,16)
  if pc==STOP and l.m68k_get_reg(None,15)==SP+4:break
  assert allowed(pc,length,original),hex(pc)
  coverage.add(pc);l.m68k_execute(1)
 else:raise AssertionError('Format padding did not return')
 cpu=[l.m68k_get_reg(None,i)for i in range(18)];cpu.extend([n.prefix[16]if supervisor else cpu[15],cpu[15]if supervisor else n.prefix[17]])
 ram=n.device.ram()
 if not original:assert ram[BASE:BASE+length]==image[BASE:BASE+length],'candidate modified executable bytes'
 return ram,cpu,coverage
def trace(image,case,length,original,changing=False):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,case))
 for reg,value in zip(REGS,case['incoming']+[SP]):u.reg_write(reg,value)
 u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,SP);events=[];queue=[2,4,2,1]if changing else[]
 def ignored(a,w):return SP-8192<=a and a+w<=SP-4 or BASE<=a and a+w<=BASE+length
 def read(e,access,a,w,v,_):
  if ignored(a,w):return
  if a==0x130000 and w==2 and queue:e.mem_write(a,queue.pop(0).to_bytes(2,'big'))
  events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
 def write(e,access,a,w,v,_):
  if not ignored(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
 def code(e,a,w,_):assert allowed(a,length,original),hex(a)
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start(ENTRY,STOP,count=1000000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
 ram=bytes(u.mem_read(0,0x200000))
 if not original:assert ram[BASE:BASE+length]==image[BASE:BASE+length],'candidate modified executable bytes'
 return ram,events
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--limit',type=int);args=p.parse_args()
 nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';source=(args.source or nd/'format-pad-reference.c').resolve();out=ROOT/'verification/native-format-pad'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),coordinator_reference=source==nd/'format-pad-reference.c',source_accepted=False,whole_game_complete=False,game_frames=0)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-format-pad-active.json',state)
 mark()
 try:
  snapshots=out/'source-snapshot';snapshots.mkdir()
  paths=[source,Path(__file__),nd/'format-pad-native.h',nd/'format-pad-shim.S']
  for q in paths:shutil.copy2(q,snapshots/q.name)
  prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');commands=[[prefix+'gcc','-m68000','-msoft-float','-std=c99','-Os','-ffreestanding','-fno-pie','-fno-common','-Wall','-Wextra','-Werror','-I'+str(nd),'-c',str(source),'-o',str(out/'body.o')],[prefix+'as','-m68000','-o',str(out/'shim.o'),str(nd/'format-pad-shim.S')],[prefix+'ld','-Ttext='+hex(BASE),'-e','biwn_native_format_pad','-o',str(out/'candidate.elf'),str(out/'shim.o'),str(out/'body.o')],[prefix+'objcopy','-O','binary',str(out/'candidate.elf'),str(out/'candidate.bin')]]
  with(out/'build.log').open('w')as log:
   for command in commands:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT);assert r.returncode==0,command
  payload=(out/'candidate.bin').read_bytes();image=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert sha(ROOT/'render-assets/biwn-inventory-baseline.bin')=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
  candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71';cases=vectors()
  if args.limit:cases=cases[:args.limit]
  save(out/'fixtures.json',cases);n=Native();coverage=set();rows=[];traces=0
  try:
   for i,c in enumerate(cases):
    a=native(n,image,c,len(payload),True);b=native(n,candidate,c,len(payload),False)
    normalized=normalize(b[0],a[0],len(payload))
    if a[1]!=b[1]or normalized!=a[0]:save(out/'mismatch.json',dict(case=i,parameters=c,original_CPU=a[1],compiled_CPU=b[1],RAM_differences=[dict(address=hex(k),original=x,compiled=y)for k,(x,y)in enumerate(zip(a[0],normalized))if x!=y][:32]));raise AssertionError('CPU/RAM mismatch')
    x=trace(image,c,len(payload),True);y=trace(candidate,c,len(payload),False);assert x[1]==y[1]and normalize(y[0],x[0],len(payload))==x[0],'ordered access mismatch'
    coverage.update(a[2]);traces+=1;rows.append(dict(case=i,CPU=b[1],ordered_events=len(x[1])))
    if i%128==0:state['completed']=len(rows);mark();print('Padding',len(rows),'/',len(cases),flush=True)
   for c in cases[:16]:
    a=trace(image,c,len(payload),True,True);b=trace(candidate,c,len(payload),False,True);assert a[1]==b[1]and normalize(b[0],a[0],len(payload))==a[0];traces+=1
  finally:n.close()
  save(out/'results.json',rows);asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000',f'--start-address={ENTRY}',f'--stop-address={END}',str(ROOT/'render-assets/biwn-inventory-baseline.bin')],text=True);(out/'original.asm').write_text(asm)
  expected={int(line.split(':',1)[0].strip(),16)for line in asm.splitlines()if ':'in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()}
  if not args.limit:assert expected<=coverage
  state.update(status='terminal_native_format_pad_preflight_pass'if args.limit else'terminal_native_format_pad_CPU_RAM_ordered_access_pass',native_cases=len(rows),trace_cases=traces,original_instruction_coverage=[len(expected&coverage),len(expected)],binary_bytes=len(payload),compiled_binary=str(out/'candidate.bin'),compiled_binary_sha256=sha(out/'candidate.bin'),source_accepted=not args.limit,artifacts_sha256={str(q):sha(q)for q in [source,Path(__file__),nd/'format-pad-native.h',nd/'format-pad-shim.S']},scope='Stable target RAM,fullD/A/PC/SR/USP/SSP and2MB publicRAM including original4byte D2 save. Two stack modes/all32CCR,negative/zero/positive remaining and wrapping signed width cases. Separate ordered native-width public accesses and16controlled changing-count read traces. Private8KBstack,code/entry excluded. No arbitrary alias/fault/IRQ/concurrency/cycle/livegame/physical or whole-game proof. Authorship is recorded by coordinator_reference and the separate Author receipt. Checker execution does not train weights.');mark();save(ROOT/'verification/native-format-pad-current.json',state);print(state['status'],len(rows),traces,state['original_instruction_coverage'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
