"""Complete original formatter/core calls versus native C, no original callees."""
import argparse,ctypes as c,hashlib,json,os,random,shutil,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_formatter_cpu as fmt
from check_biwn_scheduler import Native
from check_biwn_native_resource_release import REGS
ROOT=fmt.ROOT;N=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
BASE=0x15edc0;SP=fmt.SP;STOP=fmt.STOP;PRIVATE=8192
ENTRIES={0x1b29c:'biwn_native_format_core',0x1b45a:'biwn_native_format_variadic'}
DEPTH={0x1b29c:118,0x1b45a:138}
DRIVER=r'''
#include <stdint.h>
#include <string.h>
typedef int(*exec_fn)(int);typedef unsigned(*get_fn)(void*,int);
struct stats{uint32_t status,pc,min_sp;uint64_t steps;};
int run(exec_fn execute,get_fn get,const uint8_t*allowed,uint8_t*coverage,uint32_t stop,uint32_t sp,uint64_t limit,struct stats*out){
 memset(out,0,sizeof(*out));out->min_sp=sp;
 while(out->steps<limit){uint32_t pc=get(0,16),s=get(0,15);out->pc=pc;if(s<out->min_sp)out->min_sp=s;
  if(pc==stop&&s==sp+4)return 0;
  if(pc>=0x200000||!allowed[pc]){out->status=1;return 1;}
  coverage[pc]=1;if(execute(1)<=0){out->status=3;return 3;}out->steps++;
 }out->status=2;return 2;
}
'''
class Stats(c.Structure):_fields_=[('status',c.c_uint32),('pc',c.c_uint32),('min_sp',c.c_uint32),('steps',c.c_uint64)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def vectors():
 cases=[dict(case,body=False)for case in fmt.cases()if case['entry']in ENTRIES];rng=random.Random(0x1b29c2026)
 def add(entry,text,args,sr,kind):
  initial=[(fmt.FMT,text.encode()+b'\0'),(fmt.STRING,b'Hi\x80\xff\0')]
  if entry==0x1b29c:
   argument=fmt.pack(fmt.DEST,4)+fmt.pack(fmt.FMT,4)+fmt.pack(fmt.ARGS,4);initial.append((fmt.ARGS,args))
  else:argument=fmt.pack(fmt.DEST,4)+fmt.pack(fmt.FMT,4)+args
  cases.append(dict(id=len(cases),entry=entry,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=sr,usp=0x170000 if sr&0x2000 else SP,ssp=SP if sr&0x2000 else 0x1d0000,body=False,render=False,outer_RTS=0x1b458 if entry==0x1b29c else 0x1b476,read_queues=[],argument_hex=argument.hex(),initial=[[a,data.hex()]for a,data in initial],kind=kind))
 for entry in ENTRIES:
  for mode in [0,0x2000]:
   for flags in range(32):
    add(entry,'%ld/%u/%o/%Lx',fmt.pack(0x80000000,4)+fmt.pack(0xffff,2)+fmt.pack(0xffff,2)+fmt.pack(0xffffffff,4),mode|flags,'full_CCR_numeric')
    add(entry,'%5s/%c/%%/%s',fmt.pack(fmt.STRING,4)+fmt.pack(0x12ff,2)+fmt.pack(0,4),mode|flags,'full_CCR_text')
  for width in ['32767','32768','65535','65536','99999999999999999999']:
   for spec in ['d','x','s','c']:
    arg=fmt.pack(0x8000,2)if spec=='d'else fmt.pack(0xbeef,2)if spec=='x'else fmt.pack(fmt.STRING,4)if spec=='s'else fmt.pack(0xff,2)
    add(entry,'%'+width+spec+'!',arg,0x2000|(len(cases)%32),'wrapping_width')
 return cases
def cpu(n):
 values=[n.lib.m68k_get_reg(None,i)for i in range(18)]
 return values+[n.prefix[16]if values[17]&0x2000 else values[15],values[15]if values[17]&0x2000 else n.prefix[17]]
def native(n,driver,image,case,entry,mask,coverage):
 n.device.seed(fmt.fixture(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
 l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,case['ssp']);l.m68k_set_reg(17,0);l.m68k_set_reg(15,case['usp']);l.m68k_set_reg(17,case['SR'])
 for i,v in enumerate(case['registers']):l.m68k_set_reg(i,v)
 l.m68k_set_reg(16,entry);stats=Stats();status=driver.run(c.cast(l.m68k_execute,c.c_void_p),c.cast(l.m68k_get_reg,c.c_void_p),mask,coverage,STOP,SP,10000000,c.byref(stats))
 assert not status,('CPU boundary/budget',status,hex(stats.pc),case)
 return n.device.ram(),cpu(n),stats
def normalize(memory,reference,length,entry):
 b=bytearray(memory)
 for lo,hi in [(BASE,BASE+length),(SP-PRIVATE,SP-DEPTH[entry])]:b[lo:hi]=reference[lo:hi]
 return bytes(b)
def ordered(image,case,entry,mask,length,compiled):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,fmt.fixture(image,case));u.reg_write(UC_M68K_REG_SR,case['SR'])
 for reg,v in zip(REGS,case['registers']):u.reg_write(reg,v)
 events=[];smallest=SP
 def ignored(a,w):
  nonlocal smallest
  if compiled and BASE<=a and a+w<=BASE+length:return True
  if SP-PRIVATE<=a and a+w<=SP-DEPTH[case['entry']]:
   assert compiled,'Original accessed proposed C-private region';smallest=min(smallest,a);return True
  return False
 def code(e,pc,w,_):assert mask[pc],('ordered PC escaped',hex(pc))
 def rd(e,t,a,w,v,_):
  if not ignored(a,w):events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
 def wr(e,t,a,w,v,_):
  if not ignored(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr)
 u.emu_start(entry,STOP,count=10000000,timeout=30000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
 return bytes(u.mem_read(0,0x200000)),events,smallest
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=ROOT/'verification/native-fast-core-format-core'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),native_cases=0,ordered_cases=0,source_accepted=False,whole_game_complete=False,default_promoted=False,new_training=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-fast-core-format-core-active.json',state)
 mark();n=None
 try:
  paths=[Path(__file__),ROOT/'scripts/lower_biwn_format_core_native.py',N/'format-core-native.c',N/'format-core-native.h',N/'format-core-shim.S',N/'format-core.ld',N/'Makefile.format-core',N/'format-number-native.c',N/'format-number-native.h',N/'unsigned-division-native.c',N/'unsigned-division-native.h',N/'semantic-divide-zero.S',N/'format-pad-reference.c',N/'format-pad-native.h',N/'format-string-native.h',ROOT/'verification/native-string-ccr-preparation/20261018T170741.453379Z/format-string-ccr.c']
  snap=out/'source';snap.mkdir()
  for p in paths:shutil.copy2(p,snap/p.name)
  bundle_path=ROOT/'verification/native-fast-core-format-bundle-current.json';bundle=json.loads(bundle_path.read_text());binary=Path(bundle['binary']);elf=Path(bundle['ELF']);payload=binary.read_bytes();assert sha(binary)==bundle['binary_sha256'];prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
  paths.append(bundle_path);paths += [Path(p)for p in bundle['optimized_sources'].values()]+[Path(bundle['optimized_header'])]
  symbols={a[2]:int(a[0],16)for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines()if len(a:=line.split())==3};save(out/'symbols.json',symbols)
  (out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
  source=out/'driver.c';source.write_text(DRIVER);library=out/'driver.dylib';result=subprocess.run(['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(library)],capture_output=True,text=True);(out/'driver-build.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
  driver=c.CDLL(str(library));driver.run.argtypes=[c.c_void_p,c.c_void_p,c.POINTER(c.c_uint8),c.POINTER(c.c_uint8),c.c_uint32,c.c_uint32,c.c_uint64,c.POINTER(Stats)];driver.run.restype=c.c_int
  session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'formatter-fullCPU-generation.json').read_text());originalmask=bytearray(0x200000)
  for row in mapping['instructions_decoded']:originalmask[row['address']]=1
  candidatemask=bytearray(0x200000);candidatemask[BASE:BASE+len(payload)]=bytes([1])*len(payload)
  masks=[(c.c_uint8*len(v)).from_buffer_copy(v)for v in [originalmask,candidatemask]];covers=[(c.c_uint8*0x200000)()for _ in range(2)]
  original=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(original).hexdigest()=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
  candidate=bytearray(original);candidate[BASE:BASE+len(payload)]=payload;candidate=bytes(candidate);cases=vectors()
  if args.limit:cases=cases[:args.limit]
  save(out/'fixtures.json',cases);state.update(status='native_and_ordered_running',binary=str(binary),binary_bytes=len(payload),binary_sha256=sha(binary));mark();n=Native();rows=[];minsp=SP;minaccess=SP
  for i,case in enumerate(cases):
   target=symbols[ENTRIES[case['entry']]];a=native(n,driver,original,case,case['entry'],masks[0],covers[0]);b=native(n,driver,candidate,case,target,masks[1],covers[1]);left=ordered(original,case,case['entry'],originalmask,len(payload),False);right=ordered(candidate,case,target,candidatemask,len(payload),True)
   normalized=normalize(b[0],a[0],len(payload),case['entry'])
   if a[1]!=b[1]or normalized!=a[0]or left[1]!=right[1]or normalize(right[0],left[0],len(payload),case['entry'])!=left[0]:
    save(out/'mismatch.json',dict(index=i,case=case,original_CPU=a[1],native_CPU=b[1],RAM_differences=[dict(address=hex(j),original=x,candidate=y)for j,(x,y)in enumerate(zip(a[0],normalized))if x!=y][:32],original_events=left[1],native_events=right[1]));raise AssertionError('CPU/RAM/ordered mismatch')
   assert b[0][BASE:BASE+len(payload)]==payload
   rows.append(dict(case=case['id'],kind=case['kind'],entry=hex(case['entry']),original_steps=a[2].steps,native_steps=b[2].steps,ordered_events=len(left[1])));minsp=min(minsp,b[2].min_sp);minaccess=min(minaccess,right[2]);state.update(native_cases=len(rows),ordered_cases=len(rows))
   if i%64==0:mark();print('formatter',len(rows),'/',len(cases),flush=True)
  save(out/'results.json',rows);coverage={row['address']for row in mapping['instructions_decoded']if covers[0][row['address']]};save(out/'coverage.json',list(map(hex,sorted(coverage))))
  lowering=json.loads((ROOT/'verification/native-format-core-lowering-current.json').read_text());expected={row['pc']for routine in lowering['routines']for row in routine['rows']}
  if not args.limit:assert expected<=coverage,list(map(hex,expected-coverage))
  state.update(status='terminal_native_format_core_preflight_pass'if args.limit else'terminal_native_format_core_full_CPU_RAM_ordered_pass',source_accepted=not bool(args.limit),original_new_instruction_coverage=[len(expected&coverage),len(expected)],original_all_helper_instruction_addresses=len(coverage),minimum_real_C_SP=hex(minsp),minimum_private_access=hex(minaccess),case_kinds=dict(Counter(x['kind']for x in cases)),dependencies_sha256={str(p):sha(p)for p in paths+[binary,elf,source,library]},scope='Complete core1B29C and variadic1B45A entries on original1654formatter cases plus allCCR/bothCPU/text/numeric/wrapping-width fixtures. FullD/A/PC/SR/USP/SSP and public2MBRAM, originalLINK/MOVEM saves/localremaining/argument stack/digit scratch/RTS reads; separate entire ordered public native-width accesses. Candidate executes compiled C and native shim only, no original helper bodies. Private8KBbelow source maximum118byte(core)/138byte(variadic) public stack/code overlay excluded; original accesses to private interval rejected. Valid finite supplied formats/argument pointers, no arbitrary aliases/faults/IRQ/cycle/gameplay/physical or whole-game proof.')
  mark()
  if not args.limit:save(ROOT/'verification/native-fast-core-format-core-current.json',state)
  print(json.dumps({k:state[k]for k in ['status','native_cases','ordered_cases','binary_bytes','original_new_instruction_coverage']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:
  if n:n.close()
if __name__=='__main__':main()
