"""Original unsigned arithmetic vs compiled C, public accesses and zero faults."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_scheduler import Native
from check_biwn_native_resource_release import REGS
ROOT=Path(__file__).resolve().parents[1];NATIVE=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
_bundle=json.loads((ROOT/'verification/native-core-format-bundle-current.json').read_text());BASE=_bundle['base'];SP=0x1e0000;SSP=0x1ff000;STOP=0x1f0000;HANDLER=0x1f1000;PRIVATE=512
NAMES={0xe61c:'biwn_native_unsigned_divide',0xe67c:'biwn_native_unsigned_remainder'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def seed(image,case):
 b=bytearray(image);b[20:24]=HANDLER.to_bytes(4,'big');b[HANDLER:HANDLER+2]=b'\x4e\x73'
 b[SP:SP+12]=STOP.to_bytes(4,'big')+case['a'].to_bytes(4,'big')+case['b'].to_bytes(4,'big');return bytes(b)
def cpu(n):
 regs=[n.lib.m68k_get_reg(None,i) for i in range(18)]
 return regs+[n.prefix[16] if regs[17]&0x2000 else regs[15],regs[15] if regs[17]&0x2000 else n.prefix[17]]
def run(n,image,case,entry,length,compiled,coverage):
 l=n.lib;n.device.seed(image,0);l.m68k_pulse_reset();l.m68k_set_irq(0)
 l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SSP);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1d0000);l.m68k_set_reg(17,case['sr']);l.m68k_set_reg(15,SP)
 for i,v in enumerate(case['registers']):l.m68k_set_reg(i,v)
 l.m68k_set_reg(16,entry);faults=[];steps=0
 while steps<20000:
  pc=l.m68k_get_reg(None,16)
  if pc==STOP:break
  if pc==HANDLER:
   ram=n.device.ram();st=l.m68k_get_reg(None,15)
   faults.append(dict(cpu=cpu(n),frame_SR=int.from_bytes(ram[st:st+2],'big'),frame_PC=int.from_bytes(ram[st+2:st+6],'big')))
  else:
   assert (BASE<=pc<BASE+length) if compiled else (0xe61c<=pc<0xe68c),('escaped PC',hex(pc))
   coverage[pc]+=1
  assert l.m68k_execute(1)>0;steps+=1
 else:raise AssertionError('Instruction budget')
 result=cpu(n);assert result[15]==SP+4
 return result,faults,steps,n.device.ram()
def normalized(memory,reference,length,entry,sr):
 b=bytearray(memory);public=12 if entry==0xe67c else 0
 for lo,hi in [(BASE,BASE+length),(SP-PRIVATE,SP-public),(SSP-64,SSP)]:b[lo:hi]=reference[lo:hi]
 return bytes(b)
def ordered(image,case,entry,length,compiled):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,image);u.reg_write(UC_M68K_REG_SR,case['sr'])
 for reg,value in zip(REGS,case['registers']):u.reg_write(reg,value)
 events=[];public=12 if case['entry']==0xe67c else 0;smallest=SP
 def internal(a,w):
  nonlocal smallest
  if compiled and BASE<=a and a+w<=BASE+length:return True
  if SP-PRIVATE<=a and a+w<=SP-public:
   assert compiled,'Original accesses C-private interval'
   smallest=min(smallest,a);return True
  return False
 def code(e,pc,w,_):assert (BASE<=pc<BASE+length) if compiled else (0xe61c<=pc<0xe68c),('ordered PC escaped',hex(pc))
 def rd(e,t,a,w,v,_):
  if not internal(a,w):events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
 def wr(e,t,a,w,v,_):
  if not internal(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start(entry,STOP,count=20000)
 assert u.reg_read(UC_M68K_REG_PC)==STOP
 return events,smallest
def vectors():
 rng=random.Random(0xe61c2026);values=[0,1,2,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 ab=[(a,b) for a in values for b in values if b]+[(rng.getrandbits(32),rng.getrandbits(32)or 1) for _ in range(512)]
 rows=[]
 def add(a,b,sr,d2):
  regs=[rng.getrandbits(32) for _ in range(15)]+[SP];regs[2]=d2;rows.append(dict(a=a,b=b,sr=sr,registers=regs))
 for i,(a,b) in enumerate(ab):add(a,b,(0x2000 if i%2 else 0)|((i%8)<<8)|(i%32),rng.getrandbits(32))
 for a,b in [(0,1),(1,1),(0xffffffff,3),(0x80000000,0x10000),(0xffffffff,0x10001),(0x7fffffff,0x80000000)]:
  for mode in [0,0x2000]:
   for ccr in range(32):
    for d2 in [0,0x80000000,0xffffffff]:add(a,b,mode|ccr,d2)
 rng.shuffle(rows);return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=NATIVE/'unsigned-division-native.c');ap.add_argument('--label',default='linked-reference');ap.add_argument('--limit',type=int);args=ap.parse_args();assert args.label.replace('-','').isalnum()
 out=ROOT/'verification/native-core-format-math'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+args.label);out.mkdir(parents=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(args.source.resolve()),source_sha256=sha(args.source),label=args.label,native_cases=0,ordered_cases=0,zero_cases=0,new_training=False,whole_game_complete=False,default_promoted=False)
 def mark():save(out/'protocol.json',state);save(ROOT/f'verification/native-core-format-math-{args.label}-active.json',state)
 mark();print(out,flush=True);n=None
 try:
  bundle_path=ROOT/'verification/native-core-format-bundle-current.json';bundle=json.loads(bundle_path.read_text());full=Path(bundle['binary']).read_bytes();assert sha(bundle['binary'])==bundle['binary_sha256']
  payload=full;assert len(payload)==15408
  binary=out/'linked-tail.bin';binary.write_bytes(payload);elf=Path(bundle['ELF']);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
  for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
   a=line.split()
   if len(a)==3:symbols[a[2]]=int(a[0],16)
  save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
  original=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();candidate=bytearray(original);candidate[BASE:BASE+len(payload)]=payload;candidate=bytes(candidate);cases=vectors();cases=cases[:args.limit] if args.limit else cases
  state.update(status='normal_native_and_ordered_running',binary=str(binary),binary_sha256=sha(binary),binary_bytes=len(payload),symbols=symbols);mark();n=Native();coverage=Counter();compiled_coverage=Counter();rows=[];minimum_stack=SP
  for entry,name in NAMES.items():
   for index,values in enumerate(cases):
    case=dict(values,entry=entry);left=seed(original,case);right=seed(candidate,case)
    expected,oldfaults,oldsteps,oldram=run(n,left,case,entry,len(payload),False,coverage);actual,faults,steps,ram=run(n,right,case,symbols[name],len(payload),True,compiled_coverage)
    assert actual==expected,('CPU',hex(entry),index,case,expected,actual)
    assert not oldfaults and not faults
    assert normalized(ram,oldram,len(payload),entry,case['sr'])==oldram,('RAM',hex(entry),index)
    lo,_=ordered(left,case,entry,len(payload),False);ro,smallest=ordered(right,case,symbols[name],len(payload),True)
    if lo!=ro:save(out/'trace-mismatch.json',dict(case=case,original=lo,candidate=ro));raise AssertionError(('Public access order',hex(entry),index))
    minimum_stack=min(minimum_stack,smallest)
    rows.append(dict(entry=hex(entry),a=case['a'],b=case['b'],SR=case['sr'],D2=case['registers'][2],original_steps=oldsteps,native_steps=steps,public_events=len(lo)))
    state.update(native_cases=len(rows),ordered_cases=len(rows))
    if index%128==0:mark();print(hex(entry),index,'/',len(cases),flush=True)
  save(out/'normal-results.json',rows);state['status']='zero_exception_running';mark();zeros=[]
  for entry,name in NAMES.items():
   selected=[dict(a=a,b=0,sr=mode|ccr,registers=[(0x10203040+i*0x091a2b3c)&0xffffffff for i in range(15)]+[SP]) for a in [0,1,0x80000000,0xffffffff] for mode in [0,0x2000] for ccr in range(32)]
   if args.limit:selected=selected[:args.limit]
   for index,values in enumerate(selected):
    case=dict(values,entry=entry);expected,oldfaults,_,oldram=run(n,seed(original,case),case,entry,len(payload),False,coverage);actual,faults,_,ram=run(n,seed(candidate,case),case,symbols[name],len(payload),True,compiled_coverage)
    assert actual==expected,('Zero CPU',hex(entry),index,expected,actual)
    assert len(oldfaults)==len(faults)==1
    old=oldfaults[0].copy();new=faults[0].copy();oldpc=old.pop('frame_PC');newpc=new.pop('frame_PC');assert old==new,('Zero frame',hex(entry),index,old,new)
    offset=oldpc-0xe678;assert offset in [0,2] and newpc==symbols[name+'_fault']+offset,('Zero fault PC mapping',hex(oldpc),hex(newpc))
    assert normalized(ram,oldram,len(payload),entry,case['sr'])==oldram,('Zero RAM',hex(entry),index)
    zeros.append(dict(entry=hex(entry),numerator=case['a'],SR=case['sr'],saved_original_PC=oldpc,saved_native_PC=newpc,full_CPU_frame_SR_equal=True));state['zero_cases']=len(zeros)
   print('zero',hex(entry),len(selected),flush=True)
  save(out/'zero-results.json',zeros);save(out/'original-coverage.json',{hex(k):v for k,v in sorted(coverage.items())});save(out/'compiled-coverage.json',{hex(k):v for k,v in sorted(compiled_coverage.items())})
  state.update(status='terminal_native_unsigned_preflight_pass' if args.limit else 'terminal_native_unsigned_full_CPU_public_accesses_zero_fault_pass',original_instruction_addresses=len(coverage),minimum_C_stack_address=hex(minimum_stack),source_accepted=not bool(args.limit),source_authorship='coordinator' if args.label=='linked-reference' else 'external_candidate',scope='Two complete normal-return unsigned arithmetic entry contracts with stable stack arguments. Full D/A/PC/SR/USP/SSP, public final RAM including E67C stack pushes, ordered public reads/writes in IRQ-disabled fixtures. C-private stack below original public saves excluded, original accesses into that interval rejected in normal traces. Zero faults use new DIVU and declared inert RTE handler; trap CPU/frameSR and full return compare with declared savedPC relocation. No asynchronous argument mutation, arbitrary handler behavior, interrupt timing, gameplay or physical-console proof.',dependencies_sha256={str(p):sha(p) for p in [Path(__file__),args.source.resolve(),NATIVE/'unsigned-division-native.h',NATIVE/'unsigned-division-shim.S',NATIVE/'unsigned-division.ld',NATIVE/'Makefile.unsigned-division',binary,elf]})
  mark()
  if not args.limit and args.label=='linked-reference':save(ROOT/'verification/native-core-format-math-linked-current.json',state)
  print(json.dumps({k:state[k] for k in ['status','binary_bytes','native_cases','ordered_cases','zero_cases','original_instruction_addresses']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:
  if n:n.close()
if __name__=='__main__':main()
