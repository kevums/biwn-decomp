"""Original formatter calls linked native helpers; check live stack at every return."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_formatter_cpu as fmt
from check_biwn_native_resource_release import REGS
from check_biwn_scheduler import Native
ROOT=fmt.ROOT;SP=fmt.SP;STOP=fmt.STOP
HELPERS={0x1b160:4,0x1b1a8:8}
DRIVER=r'''
#include <stdint.h>
#include <string.h>
typedef int(*exec_fn)(int);typedef unsigned(*get_fn)(void*,int);
typedef uint32_t(*observe_fn)(unsigned,unsigned,unsigned);
struct stats {uint32_t status,pc;uint64_t steps,cycles;};
int run(exec_fn execute,get_fn get,observe_fn observe,const uint8_t*allowed,
 uint32_t stop,uint32_t sp,uint64_t limit,struct stats*out){
 memset(out,0,sizeof(*out));uint32_t ret=0,end_sp=0,active=0;
 while(out->steps<limit){
  uint32_t pc=get(0,16),s=get(0,15);out->pc=pc;
  if(active&&pc==ret&&s==end_sp){if(observe(1,pc,s)!=1){out->status=4;return 4;}active=0;}
  if(pc==stop&&s==sp+4)return 0;
  if(pc>=0x200000||!allowed[pc]){out->status=1;return 1;}
  if(pc==0x1b160||pc==0x1b1a8){if(active){out->status=5;return 5;}ret=observe(0,pc,s);if(!ret){out->status=4;return 4;}end_sp=s+4;active=1;}
  int cycles=execute(1);if(cycles<=0){out->status=3;return 3;}
  out->steps++;out->cycles+=(unsigned)cycles;
 }out->status=2;return 2;
}
'''
class Stats(c.Structure):_fields_=[('status',c.c_uint32),('pc',c.c_uint32),('steps',c.c_uint64),('cycles',c.c_uint64)]
OBSERVE=c.CFUNCTYPE(c.c_uint32,c.c_uint32,c.c_uint32,c.c_uint32)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,s):Path(p).write_text(json.dumps(s,indent=2)+'\n')
def normalized(ram,reference,bundle,private):
    b=bytearray(ram)
    for a,z in [(bundle['base'],bundle['binary_bytes']),(0x1b160,6),(0x1b1a8,6),*[(a,z-a)for a,z in private]]:b[a:a+z]=reference[a:a+z]
    return bytes(b)
def masks(bundle,rows):
    original=bytearray(0x200000)
    for row in rows:original[row['address']]=1
    candidate=bytearray(original)
    for start,end in [(0x1b160,0x1b1a0),(0x1b1a8,0x1b200)]:
        candidate[start:end]=bytes(end-start);candidate[start]=1
    candidate[bundle['base']:bundle['base']+bundle['binary_bytes']]=bytes([1])*bundle['binary_bytes']
    return original,candidate
def seed_cpu(n,ram,case):
    n.device.seed(ram,0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,case['ssp']);l.m68k_set_reg(17,0);l.m68k_set_reg(15,case['usp']);l.m68k_set_reg(17,case['SR'])
    for i,value in enumerate(case['registers']):l.m68k_set_reg(i,value)
    l.m68k_set_reg(16,case['entry'])
def cpu(n):
    regs=[n.lib.m68k_get_reg(None,i)for i in range(18)];return regs+[n.prefix[16]if regs[17]&0x2000 else regs[15],regs[15]if regs[17]&0x2000 else n.prefix[17]]
def native(n,driver,ram,case,allowed,reference=None):
    seed_cpu(n,ram,case);records=[];active=None;private=[];failure=[]
    def observe(kind,pc,stack):
        nonlocal active
        try:
            memory=n.device.ram()
            if kind==0:
                active=dict(entry=pc,sp=stack,return_PC=int.from_bytes(memory[stack:stack+4],'big'),incoming_CPU=cpu(n))
                if reference is not None:assert active=={k:reference[len(records)][k]for k in active},'helper incoming CPU differs'
                return active['return_PC']
            record=dict(active,CPU=cpu(n),live_stack=memory[active['sp']-HELPERS[active['entry']]:SP+256].hex())
            if reference is not None:
                assert record==reference[len(records)],'helper returned CPU/public saves/live caller stack differs'
                private.append((active['sp']-8192,active['sp']-HELPERS[active['entry']]))
            records.append(record);active=None;return 1
        except BaseException as error:failure.append(repr(error));return 0
    callback=OBSERVE(observe);array=(c.c_uint8*len(allowed)).from_buffer_copy(allowed);stats=Stats()
    status=driver.run(c.cast(n.lib.m68k_execute,c.c_void_p),c.cast(n.lib.m68k_get_reg,c.c_void_p),callback,array,STOP,SP,10000000,c.byref(stats))
    assert status==0,('native boundary/budget/helper comparison',status,hex(stats.pc),failure)
    if reference is not None:assert len(records)==len(reference)
    return n.device.ram(),cpu(n),records,private,stats.steps
def trace(ram,case,allowed,bundle,compiled):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,ram)
    u.reg_write(UC_M68K_REG_SR,case['SR'])
    for reg,value in zip(REGS,case['registers']):u.reg_write(reg,value)
    events=[];active=None;private=[]
    def code(e,pc,width,_):
        nonlocal active
        stack=e.reg_read(UC_M68K_REG_A7)
        if active and pc==active['return']and stack==active['sp']+4:active=None
        assert allowed[pc],hex(pc)
        if pc in HELPERS:
            assert active is None
            active=dict(entry=pc,sp=stack,return_=0);active['return']=int.from_bytes(e.mem_read(stack,4),'big')
            if compiled:private.append((stack-8192,stack-HELPERS[pc]))
    def ignored(address,width):
        if compiled and bundle['base']<=address and address+width<=bundle['base']+bundle['binary_bytes']:return True
        if active and active['sp']-8192<=address and address+width<=active['sp']-HELPERS[active['entry']]:
            assert compiled,'Original helper accessed the proposed private C frame; alias unsupported'
            return True
        return False
    def read(e,t,a,w,v,_):
        if not ignored(a,w):events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,t,a,w,v,_):
        if not ignored(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(case['entry'],STOP,count=10000000,timeout=30000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
    return bytes(u.mem_read(0,0x200000)),events,private
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
    bp=Path('/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-ccr-format-bundle-current.json');bundle=json.loads(bp.read_text());assert sha(bundle['binary'])==bundle['binary_sha256']
    out=ROOT/'verification/native-ccr-format-callers'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'formatter-fullCPU-generation.json').read_text());a_mask,b_mask=masks(bundle,mapping['instructions_decoded'])
    (out/'driver.c').write_text(DRIVER);p=subprocess.run(['clang','-std=c99','-O2','-dynamiclib',str(out/'driver.c'),'-o',str(out/'driver.dylib')],capture_output=True,text=True);(out/'driver-build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    driver=c.CDLL(str(out/'driver.dylib'));driver.run.argtypes=[c.c_void_p,c.c_void_p,OBSERVE,c.POINTER(c.c_uint8),c.c_uint32,c.c_uint32,c.c_uint64,c.POINTER(Stats)];driver.run.restype=c.c_int
    original=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();candidate=bytearray(original);payload=Path(bundle['binary']).read_bytes();candidate[bundle['base']:bundle['base']+len(payload)]=payload
    for entry,name in [(0x1b160,'biwn_native_format_pad'),(0x1b1a8,'biwn_native_format_string')]:candidate[entry:entry+6]=b'\x4e\xf9'+bundle['symbols'][name].to_bytes(4,'big')
    cases=[dict(case,body=False)for case in fmt.cases()if case['entry']in [0x1b29c,0x1b45a]]
    if args.limit:cases=cases[:args.limit]
    save(out/'fixtures.json',cases);state=dict(status='running_original_formatter_native_helpers',pid=os.getpid(),directory=str(out),bundle=str(bp),bundle_sha256=sha(bp),native_cases=0,ordered_cases=0,helper_returns=0,source_accepted=False,whole_game_complete=False,game_frames=0)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-ccr-format-callers-active.json',state)
    mark();n=Native();rows=[];counts=Counter()
    try:
        for i,case in enumerate(cases):
            a=fmt.fixture(original,case);b=fmt.fixture(candidate,case)
            left,lc,records,_,steps=native(n,driver,a,case,a_mask)
            right,rc,new,private,newsteps=native(n,driver,b,case,b_mask,records)
            assert lc==rc and normalized(right,left,bundle,private)==left,('final CPU/RAM mismatch',case['id'])
            assert right[bundle['base']:bundle['base']+len(payload)]==payload
            lo=trace(a,case,a_mask,bundle,False);ro=trace(b,case,b_mask,bundle,True)
            if lo[1]!=ro[1]:
                save(out/'trace-mismatch.json',dict(case=case,original=lo[1],compiled=ro[1]));raise AssertionError('ordered formatter accesses differ')
            assert normalized(ro[0],lo[0],bundle,ro[2])==lo[0]
            counts.update(hex(row['entry'])for row in records)
            rows.append(dict(case=case['id'],kind=case['kind'],helper_returns=len(records),original_steps=steps,compiled_steps=newsteps,ordered_events=len(lo[1]),CPU=rc))
            state.update(native_cases=len(rows),ordered_cases=len(rows),helper_returns=sum(counts.values()),helper_entry_counts=dict(counts))
            if i%64==0:mark();print('Caller',len(rows),'/',len(cases),'helper returns',state['helper_returns'],flush=True)
        save(out/'results.json',rows);state.update(status='terminal_native_format_caller_preflight_pass'if args.limit else'terminal_original_formatter_native_helpers_CPU_RAM_access_pass',source_accepted=not bool(args.limit),case_kinds=dict(Counter(x['kind']for x in cases)),binary_sha256=bundle['binary_sha256'],source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/check_biwn_formatter_cpu.py',Path(bundle['binary']),out/'driver.c',out/'driver.dylib']},scope='Original complete formatter/format-core and original unsigned math execute, calling target-linked native pad/string. Full native CPU at complete return and every helper entry/return; helper public saves and live caller stack checked per return. Whole RAM except immutable payload/entry overlays and per-call private C stack unions; original helper accesses to private intervals rejected. Separate entire ordered public accesses include formatter scratch and public stack. Dead previous stack bytes in private unions excluded at final comparison, compensated by per-call public/live stack checks. No source function stubs, host formatter effects, gameframes, IRQ/timing/fault or physical-console proof. Other native bundle bodies and relocated heap are not exercised by these calls.');mark()
        if not args.limit:save(ROOT/'verification/native-ccr-format-callers-current.json',state)
        print(state['status'],state['native_cases'],state['helper_entry_counts'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error),case=case);mark();raise
    finally:n.close()
if __name__=='__main__':main()
