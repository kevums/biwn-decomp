"""Original 1B212 number formatter vs standalone compiled native C.

No original helper is executed by the candidate. CPU, public RAM and ordered
native-width accesses are checked separately; real DIVU-zero is observed with
an explicitly inert RTE handler, with only its saved PC relocated.
"""
import argparse, hashlib, json, os, random, shutil, subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_scheduler import Native
from check_biwn_native_resource_release import REGS
from check_biwn_native_unsigned_division import cpu

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
BASE=0x15edc0; ENTRY=0x1b212; END=0x1b29c
SP=0x1e0000; SSP=0x1ff000; STOP=0x1f0000; HANDLER=0x1f1000
DEST=0x190000; REMAINING=0x18fc00; PRIVATE=1024; PUBLIC_DEPTH=56
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def pack(v,w):return (v&((1<<(8*w))-1)).to_bytes(w,'big')
def vectors(zero=False):
 rng=random.Random(0x1b2122026);rows=[]
 def add(number,radix,width,left,sr,pad):
  regs=[rng.getrandbits(32) for _ in range(15)]+[SP]
  if zero:regs[1]=0  # DIVU-zero leaves D1 unchanged; digit-table EA remains valid.
  # Width0x8000 wraps positive after digit-count subtraction in the original.
  # Bound that padding fixture's output; do not mistake its long original loop
  # for a candidate mismatch. Large remaining is separately crossed with width0.
  if width==0x8000 and left==0x7fff:left=254
  rows.append(dict(number=number,radix=radix,width=width,left=left,sr=sr,pad=pad,registers=regs))
 if zero:
  for mode in [0,0x2000]:
   for ccr in range(32):
    for i,number in enumerate([0,1,0x80000000,0xffffffff]):add(number,0,[0,1,8,0xffff][i],[0,1,7,0xffff][i],mode|ccr,0x1230)
  return rows
 # Each mode/CCR crosses zero, negative and positive count/width boundaries.
 for mode in [0,0x2000]:
  for ccr in range(32):
   for i,(number,radix,width,left) in enumerate([
    (0,10,0,0),(1,8,1,1),(0xffffffff,16,20,7),
    (0x80000000,10,0x8000,7),(0xffff,8,0xffff,0x8000),
    (0x10000,16,2,0xffff),(0,10,20,254),(0x7fffffff,10,12,2),
    (0x8000,8,0,20),(0xffffffff,2,0,40),
    (0,1,0,1),(0xff,10,0x7fff,0),(0x80000000,10,0,0x7fff)]):
    add(number,radix,width,left,mode|ccr,[0,0xff,0x1230,0x8000][(ccr+i)%4])
 values=[0,1,2,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 for number in values:
  for radix in [2,3,7,8,10,15,16,17,36]:
   i=len(rows);add(number,radix,[0,1,2,8,20,40,0x8000,0xffff][i%8],[0,1,2,7,40,254,0x7fff,0x8000,0xffff][i%9],(0x2000 if i%2 else 0)|(i%32),0x1230)
 for i in range(256):add(rng.getrandbits(32),rng.choice([2,3,8,10,16,36]),rng.choice([0,1,2,20,40,0x8000,0xffff]),rng.choice([0,1,2,7,254,0x8000,0xffff]),(0x2000 if i%2 else 0)|((i%8)<<8)|(i%32),rng.getrandbits(16))
 return rows
def seed(image,case):
 b=bytearray(image);b[20:24]=pack(HANDLER,4);b[HANDLER:HANDLER+2]=b'\x4e\x73'
 b[DEST:DEST+512]=b'\xa5'*512;b[0x15b7a0:0x15b7e0]=b'\xa5'*64
 b[REMAINING:REMAINING+2]=pack(case['left'],2)
 args=pack(STOP,4)+pack(DEST,4)+pack(case['number'],4)+pack(case['radix'],2)+pack(REMAINING,4)+pack(case['width'],2)+pack(case['pad'],2)
 b[SP:SP+len(args)]=args;return bytes(b)
def allowed(pc,length,compiled):
 return BASE<=pc<BASE+length if compiled else ENTRY<=pc<END or 0xe61c<=pc<0xe68c
def run(n,image,case,entry,length,compiled,coverage):
 l=n.lib;n.device.seed(seed(image,case),0);l.m68k_pulse_reset();l.m68k_set_irq(0)
 l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SSP)
 l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1d0000)
 l.m68k_set_reg(17,case['sr'])
 for i,v in enumerate(case['registers']):l.m68k_set_reg(i,v)
 l.m68k_set_reg(16,entry);faults=[];smallest=SP
 for step in range(200000):
  pc=l.m68k_get_reg(None,16)
  if pc==STOP:break
  smallest=min(smallest,l.m68k_get_reg(None,15))
  if pc==HANDLER:
   ram=n.device.ram();st=l.m68k_get_reg(None,15)
   faults.append(dict(cpu=cpu(n),frame_SP=st,frame_SR=int.from_bytes(ram[st:st+2],'big'),frame_PC=int.from_bytes(ram[st+2:st+6],'big')))
  else:assert allowed(pc,length,compiled),('PC escaped',hex(pc));coverage[pc]+=1
  assert l.m68k_execute(1)>0
 else:raise AssertionError('number formatter instruction budget')
 result=cpu(n);assert result[15]==SP+4
 ram=n.device.ram()
 if compiled:assert ram[BASE:BASE+length]==image[BASE:BASE+length],'modified executable'
 return result,faults,step,ram,smallest
def normalize(memory,reference,length,faults=()):
 b=bytearray(memory)
 for lo,hi in [(BASE,BASE+length),(SP-PRIVATE,SP-PUBLIC_DEPTH)]:b[lo:hi]=reference[lo:hi]
 # Public exception frame SR/CPU are compared at each fault; saved PC is the
 # sole declared relocation. The final words outside these four bytes compare.
 for f in faults:
  a=f['frame_SP']+2;b[a:a+4]=reference[a:a+4]
 return bytes(b)
def ordered(image,case,entry,length,compiled,changing=False):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000)
 u.mem_map(0,0x200000);u.mem_write(0,seed(image,case));u.reg_write(UC_M68K_REG_SR,case['sr'])
 for r,v in zip(REGS,case['registers']):u.reg_write(r,v)
 events=[];smallest=SP;queue=[2,4,2,1] if changing else []
 def internal(a,w):
  nonlocal smallest
  if compiled and BASE<=a and a+w<=BASE+length:return True
  if SP-PRIVATE<=a and a+w<=SP-PUBLIC_DEPTH:
   assert compiled,'Original accessed private interval';smallest=min(smallest,a);return True
  return False
 def code(e,pc,w,_):assert allowed(pc,length,compiled),('ordered PC escaped',hex(pc))
 def rd(e,t,a,w,v,_):
  if internal(a,w):return
  if a==REMAINING and w==2 and queue:e.mem_write(a,pack(queue.pop(0),2))
  events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
 def wr(e,t,a,w,v,_):
  if not internal(a,w):events.append(['w',a,w,v&((1<<(w*8))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr)
 u.emu_start(entry,STOP,count=200000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
 return events,bytes(u.mem_read(0,0x200000)),smallest
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=ROOT/'verification/native-number-format-number'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),native_cases=0,ordered_cases=0,zero_cases=0,source_accepted=False,whole_game_complete=False,default_promoted=False,new_training=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-number-format-number-active.json',state)
 mark();print(out,flush=True);n=None
 try:
  paths=[Path(__file__),NATIVE/'format-number-native.c',NATIVE/'format-number-native.h',NATIVE/'format-number-shim.S',NATIVE/'semantic-divide-zero.S',NATIVE/'format-number.ld',NATIVE/'Makefile.format-number',NATIVE/'unsigned-division-native.c',NATIVE/'unsigned-division-native.h',NATIVE/'format-pad-native.h',NATIVE/'m68k-fact-helpers-v2.h',ROOT/'scripts/lower_biwn_format_number_native.py']
  snap=out/'source';snap.mkdir()
  for p in paths:shutil.copy2(p,snap/p.name)
  bundle_path=ROOT/'verification/native-number-format-bundle-current.json';bundle=json.loads(bundle_path.read_text());binary=Path(bundle['binary']);elf=Path(bundle['ELF']);payload=binary.read_bytes();assert sha(binary)==bundle['binary_sha256'];prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
  paths.append(bundle_path)
  symbols={a[2]:int(a[0],16) for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines() if len(a:=line.split())==3}
  save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
  original=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(original).hexdigest()=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
  candidate=bytearray(original);candidate[BASE:BASE+len(payload)]=payload;candidate=bytes(candidate)
  cases=vectors();zeros=vectors(True)
  if args.limit:cases=cases[:args.limit];zeros=zeros[:args.limit]
  save(out/'fixtures.json',dict(normal=cases,zero=zeros));state.update(status='normal_native_and_ordered_running',binary=str(binary),binary_sha256=sha(binary),binary_bytes=len(payload));mark()
  n=Native();coverage=Counter();nativecoverage=Counter();rows=[];minsp=SP;minaccess=SP
  for i,case in enumerate(cases):
   left=run(n,original,case,ENTRY,len(payload),False,coverage);right=run(n,candidate,case,symbols['biwn_native_format_number'],len(payload),True,nativecoverage)
   a=ordered(original,case,ENTRY,len(payload),False);b=ordered(candidate,case,symbols['biwn_native_format_number'],len(payload),True)
   if left[0]!=right[0] or normalize(right[3],left[3],len(payload))!=left[3] or a[0]!=b[0] or normalize(b[1],a[1],len(payload))!=a[1]:
    save(out/'mismatch.json',dict(index=i,case=case,CPU_original=left[0],CPU_native=right[0],RAM_differences=[dict(address=hex(k),original=x,candidate=y) for k,(x,y) in enumerate(zip(left[3],normalize(right[3],left[3],len(payload)))) if x!=y][:32],ordered_original=a[0],ordered_native=b[0]));raise AssertionError('CPU/RAM/ordered mismatch')
   assert not left[1] and not right[1]
   minsp=min(minsp,right[4]);minaccess=min(minaccess,b[2]);rows.append(dict(case=i,original_steps=left[2],native_steps=right[2],public_events=len(a[0])))
   state.update(native_cases=len(rows),ordered_cases=len(rows))
   if i%64==0:mark();print('normal',len(rows),'/',len(cases),flush=True)
  save(out/'normal-results.json',rows);state['status']='zero_exception_running';mark();zerorows=[]
  for i,case in enumerate(zeros):
   left=run(n,original,case,ENTRY,len(payload),False,coverage);right=run(n,candidate,case,symbols['biwn_native_format_number'],len(payload),True,nativecoverage)
   assert left[0]==right[0],('zero CPU',i,left[0],right[0])
   assert len(left[1])==len(right[1])==2,('fault count',i,left[1],right[1])
   for old,new in zip(left[1],right[1]):
    a=old.copy();b=new.copy();oldpc=a.pop('frame_PC');newpc=b.pop('frame_PC')
    assert a==b,('fault state',i,a,b)
    offset=oldpc-0xe678;assert offset in [0,2] and newpc==symbols['biwn_native_semantic_divide_fault']+offset,('fault PC',hex(oldpc),hex(newpc))
   norm=normalize(right[3],left[3],len(payload),right[1])
   if norm!=left[3]:save(out/'zero-RAM-mismatch.json',dict(case=case,differences=[dict(address=hex(k),original=x,candidate=y)for k,(x,y)in enumerate(zip(left[3],norm))if x!=y][:32]));raise AssertionError(('zero RAM',i))
   minsp=min(minsp,right[4]);zerorows.append(dict(case=i,faults=right[1],full_CPU_frame_SR_equal=True));state['zero_cases']=len(zerorows)
   if i%64==0:mark();print('zero',len(zerorows),'/',len(zeros),flush=True)
  save(out/'zero-results.json',zerorows)
  changing=0
  for case in cases[:16]:
   a=ordered(original,case,ENTRY,len(payload),False,True);b=ordered(candidate,case,symbols['biwn_native_format_number'],len(payload),True,True)
   assert a[0]==b[0] and normalize(b[1],a[1],len(payload))==a[1],'changing remaining trace mismatch';changing+=1
  save(out/'original-coverage.json',{hex(k):v for k,v in sorted(coverage.items())});save(out/'native-coverage.json',{hex(k):v for k,v in sorted(nativecoverage.items())})
  original_instructions={r['pc'] for r in json.loads((ROOT/'verification/native-format-number-lowering-current.json').read_text())['rows']}
  if not args.limit:assert original_instructions<=coverage.keys(),list(map(hex,original_instructions-coverage.keys()))
  assert minsp>SP-496,'C frames reach zero-bridge bookkeeping region'
  state.update(status='terminal_native_format_number_preflight_pass' if args.limit else 'terminal_native_format_number_CPU_RAM_ordered_zero_fault_pass',source_accepted=not bool(args.limit),changing_cases=changing,original_instruction_coverage=[len(original_instructions&coverage.keys()),len(original_instructions)],minimum_real_C_SP=hex(minsp),minimum_normal_private_access=hex(minaccess),source_authorship='coordinator_deterministic_lowering',dependencies_sha256={str(p):sha(p) for p in paths+[binary,elf]},scope='Complete pinned 1B212 body on finite declared stable valid-pointer fixtures. Both CPU modes/all32 CCR; native CPU D/A/PC/SR/USP/SSP and all public RAM, original stack saves and digit scratch. Separate normal ordered public native-width accesses, including16 controlled remaining-read sequences. Original execution into private interval rejected. Candidate executes only compiled code, including arithmetic C bodies. Radix0 realDIVU faults compare both trap contexts and return with inertRTE and declared savedPC relocation. Private1024-byte Cstack below original56-byte publicdepth/code overlay excluded. Arbitrary aliasing, nonterminating radix1 nonzero, changing arguments, arbitrary handlers, IRQ timing, gameplay and physical console not proved.')
  mark()
  if not args.limit:save(ROOT/'verification/native-number-format-number-current.json',state)
  print(json.dumps({k:state[k] for k in ['status','native_cases','ordered_cases','zero_cases','binary_bytes','original_instruction_coverage']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:
  if n:n.close()
if __name__=='__main__':main()
