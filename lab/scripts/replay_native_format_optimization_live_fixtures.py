"""Replay identical real helper entries on original and exact linked target code.

Stable-RAM native CPU/flags/full RAM and separate ordered accesses. Compare
sampled live return CPU and helper-written bytes; measure native instruction cost.
"""
from pathlib import Path
from datetime import datetime,timezone
import ctypes as c
import argparse,hashlib,json,os,subprocess
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_scheduler import Native
from check_biwn_native_resource_release import REGS
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
DRIVER=r'''
#include <stdint.h>
#include <string.h>
typedef int(*execute_fn)(int);typedef unsigned(*get_fn)(void*,int);
struct stats{uint32_t status,pc,minimum_sp,pad;uint64_t steps,cycles;};
int run(execute_fn execute,get_fn get,uint32_t stop,uint32_t sp,uint32_t base,uint32_t end,uint32_t entry,uint32_t original,uint32_t original_end,struct stats*out){
 memset(out,0,sizeof(*out));out->minimum_sp=sp;
 while(out->steps<1000000u){
  uint32_t pc=get(0,16),stack=get(0,15);out->pc=pc;if(stack<out->minimum_sp)out->minimum_sp=stack;
  if(pc==stop&&stack==sp+4u)return 0;
  if(original?!(pc>=entry&&pc<original_end):!(pc==entry||(pc>=base&&pc<end))){out->status=1;return 1;}
  int cycles=execute(1);if(cycles<=0){out->status=3;return 3;}
  out->steps++;out->cycles+=(unsigned)cycles;
 }out->status=2;return 2;
}
'''
class Stats(c.Structure):
    _fields_=[('status',c.c_uint32),('pc',c.c_uint32),('minimum_sp',c.c_uint32),('pad',c.c_uint32),('steps',c.c_uint64),('cycles',c.c_uint64)]
ENTRIES=[0x1b160,0x1b1a8];ENDS=[0x1b1a0,0x1b200];PUBLIC=[4,8]
def normalize(ram,reference,entry,sp,minimum,kind):
    b=bytearray(ram);b[entry:entry+6]=reference[entry:entry+6]
    assert minimum<=sp-PUBLIC[kind]
    b[minimum:sp-PUBLIC[kind]]=reference[minimum:sp-PUBLIC[kind]]
    return bytes(b)
def native(n,driver,memory,event,bundle,original):
    n.device.seed(memory,0);lib=n.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0)
    lib.m68k_set_reg(17,0x2000);lib.m68k_set_reg(15,event['ssp']);lib.m68k_set_reg(17,0);lib.m68k_set_reg(15,event['usp']);lib.m68k_set_reg(17,event['SR'])
    for index,value in enumerate(event['registers']):lib.m68k_set_reg(index,value)
    entry=ENTRIES[event['kind']];lib.m68k_set_reg(16,entry);stats=Stats()
    code=driver.run(c.cast(lib.m68k_execute,c.c_void_p),c.cast(lib.m68k_get_reg,c.c_void_p),event['return_PC'],event['entry_sp'],bundle['base'],bundle['base']+bundle['binary_bytes'],entry,int(original),ENDS[event['kind']],c.byref(stats))
    assert code==0,('native replay boundary/budget',code,hex(stats.pc),event['kind'],event['ordinal'])
    regs=[lib.m68k_get_reg(None,i)for i in range(18)];cpu=dict(registers=regs[:16],PC=regs[16],SR=regs[17],usp=n.prefix[16]if regs[17]&0x2000 else regs[15],ssp=regs[15]if regs[17]&0x2000 else n.prefix[17])
    return n.device.ram(),cpu,stats
def trace(memory,event,bundle,original,minimum):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(memory))
    u.reg_write(UC_M68K_REG_SR,event['SR'])
    for reg,value in zip(REGS,event['registers']):u.reg_write(reg,value)
    events=[];entry=ENTRIES[event['kind']];sp=event['entry_sp']
    def private(a,w):return minimum<=a and a+w<=sp-PUBLIC[event['kind']]
    def read(engine,t,a,w,v,_):
        assert 0<=a and a+w<=0x200000
        if private(a,w):assert not original,'Original helper used proposed private scratch';return
        events.append(['r',a,w,int.from_bytes(engine.mem_read(a,w),'big')])
    def write(engine,t,a,w,v,_):
        assert 0<=a and a+w<=0x200000
        if private(a,w):assert not original,'Original helper wrote proposed private scratch';return
        events.append(['w',a,w,v&((1<<(8*w))-1)])
    def code(engine,pc,width,_):
        assert entry<=pc<ENDS[event['kind']]if original else pc==entry or bundle['base']<=pc<bundle['base']+bundle['binary_bytes'],hex(pc)
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(entry,event['return_PC'],count=1000000,timeout=10000000)
    assert u.reg_read(UC_M68K_REG_PC)==event['return_PC']and u.reg_read(UC_M68K_REG_A7)==sp+4
    return events
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--bundle-proof',type=Path,required=True);parser.add_argument('--label',required=True);args=parser.parse_args()
    capture_path=ROOT/'verification/native-format-live-capture-current.json';capture=json.loads(capture_path.read_text());assert capture['status']=='terminal_bounded_real_format_call_capture_complete'
    bp=args.bundle_proof.resolve();bundle=json.loads(bp.read_text());payload=Path(bundle['binary']).read_bytes();assert sha(bundle['binary'])==bundle['binary_sha256']
    base_bp=ROOT/'verification/native-format-bundle-current.json';base_bundle=json.loads(base_bp.read_text());base_payload=Path(base_bundle['binary']).read_bytes();assert sha(base_bundle['binary'])==base_bundle['binary_sha256'];assert bundle['base']==base_bundle['base']and bundle['heap_start']==base_bundle['heap_start']and bundle['reserved_bytes']==base_bundle['reserved_bytes']
    baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';original_code=baseline.read_bytes();assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    out=ROOT/'verification/native-format-optimization-replay'/args.label/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=out/'driver.c';source.write_text(DRIVER);library=out/'driver.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    driver=c.CDLL(str(library));driver.run.argtypes=[c.c_void_p,c.c_void_p,*([c.c_uint32]*7),c.POINTER(Stats)];driver.run.restype=c.c_int
    state=dict(status='running_identical_live_entry_replays',pid=os.getpid(),directory=str(out),capture_proof=str(capture_path),capture_proof_sha256=sha(capture_path),bundle=str(bp),bundle_sha256=sha(bp),completed=0,whole_game_complete=False,LLM_calls=0,training_updates=0)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/('native-format-optimization-replay-'+args.label+'-active.json'),state)
    mark();n=Native();rows=[];dependencies={str(p):sha(p)for p in [Path(__file__),capture_path,bp,base_bp,Path(bundle['binary']),Path(base_bundle['binary']),baseline,source,library]}
    try:
        for lane,meta in capture['captures'].items():
            directory=Path(meta['directory']);event_path=directory/'events.jsonl';assert sha(event_path)==meta['events_sha256'];dependencies[str(event_path)]=sha(event_path)
            events=[json.loads(line)for line in event_path.read_text().splitlines()];pending={}
            for event in events:
                key=(event['kind'],event['ordinal'])
                if event['event']=='entry':pending[key]=event;continue
                entry=pending.pop(key);kind=entry['kind'];address=ENTRIES[kind];sp=entry['entry_sp']
                path=directory/entry['ram_file'];actual_path=directory/event['ram_file'];dependencies[str(path)]=sha(path);dependencies[str(actual_path)]=sha(actual_path)
                memory=path.read_bytes();actual=actual_path.read_bytes();assert memory[base_bundle['base']:base_bundle['base']+len(base_payload)]==base_payload
                left=bytearray(memory);left[bundle['base']:bundle['heap_start']]=payload+bytes(bundle['reserved_bytes']-len(payload));left[address:ENDS[kind]]=original_code[address:ENDS[kind]]
                right=bytearray(memory);right[bundle['base']:bundle['heap_start']]=payload+bytes(bundle['reserved_bytes']-len(payload));right[address:address+6]=b'\x4e\xf9'+bundle['symbols']['biwn_native_format_'+('pad'if kind==0 else'string')].to_bytes(4,'big')
                a,ac,ast=native(n,driver,left,entry,bundle,True);b,bc,bst=native(n,driver,right,entry,bundle,False)
                assert ac==bc and normalize(b,a,address,sp,bst.minimum_sp,kind)==a,('identical live entry nativeCPU/RAM differs',lane,key)
                assert b[bundle['base']:bundle['base']+len(payload)]==payload
                at=trace(left,entry,bundle,True,bst.minimum_sp);bt=trace(right,entry,bundle,False,bst.minimum_sp)
                assert at==bt,('identical live entry ordered public accesses differ',lane,key)
                written={}
                for typ,addr,width,value in at:
                    if typ=='w':
                        for offset,byte in enumerate(value.to_bytes(width,'big')):written[addr+offset]=byte
                mismatch=[hex(addr)for addr,value in written.items()if actual[addr]!=value]
                live_cpu={k:event[k]for k in ['registers','PC','SR','usp','ssp']}
                cpu_match=ac==live_cpu
                rows.append(dict(lane=lane,kind=kind,ordinal=entry['ordinal'],entry_frame=entry['frame'],return_frame=event['frame'],
                    native_CPU_and_public_RAM_match=True,ordered_public_accesses_match=True,ordered_event_count=len(at),
                    original_cycles=ast.cycles,compiled_cycles=bst.cycles,original_steps=ast.steps,compiled_steps=bst.steps,
                    minimum_compiled_SP=bst.minimum_sp,entry_SP=sp,private_scratch_bytes=sp-PUBLIC[kind]-bst.minimum_sp,
                    live_return_CPU_matches_replay=cpu_match,live_helper_written_bytes_match=not mismatch,
                    live_written_bytes=len(written),live_write_mismatches=mismatch[:20],
                    live_CPU_difference={k:dict(replay=ac[k],live=live_cpu[k])for k in ac if ac[k]!=live_cpu[k]},
                    supervisor_excursions=event['supervisor_excursions'],supervisor_steps=event['supervisor_steps'],other_task_steps=event['other_task_steps'],first_supervisor_PC=event['first_supervisor_PC']))
                if len(rows)%16==0:state['completed']=len(rows);mark();print('Replay',len(rows),flush=True)
            assert not pending
        assert len(rows)==84
        save(out/'results.json',rows);summary={}
        for kind in [0,1]:
            selected=[r for r in rows if r['kind']==kind];orig=sum(r['original_cycles']for r in selected);compiled=sum(r['compiled_cycles']for r in selected)
            summary['pad'if kind==0 else'string']=dict(cases=len(selected),original_cycles=orig,compiled_cycles=compiled,cycle_ratio=compiled/orig,
                live_return_CPU_matches=sum(r['live_return_CPU_matches_replay']for r in selected),live_written_bytes_matches=sum(r['live_helper_written_bytes_match']for r in selected),
                selected_live_calls_with_supervisor_execution=sum(r['supervisor_steps']>0 for r in selected),minimum_original_cycles=min(r['original_cycles']for r in selected),maximum_compiled_cycles=max(r['compiled_cycles']for r in selected))
        state.update(status='terminal_optimization_live_fixture_CPU_RAM_ordered_pass',completed=len(rows),summary=summary,dependencies_sha256=dependencies,
            source_accepted=False,full_fixture_gate_accepted=False,fresh_game_run=False,counterfactual_optimization=True,live_return_CPU_all_match=all(r['live_return_CPU_matches_replay']for r in rows),live_written_bytes_all_match=all(r['live_helper_written_bytes_match']for r in rows),
            whole_game_frame_equivalence=False,timing_cause_completely_proven=False,
            scope='84previously captured entries replayed counterfactually through original and new optimization variant with identical RAM/CPU and IRQ disabled. Both replay lanes install the new payload into the unchanged reserved code window. The new variant has not run in a fresh game; live-return comparisons use the prior base build captures. Full returnCPU and2MBRAM match excluding only entry6byte JMP and actually observed private C scratch below original public saves. Separate Unicorn native-width public read/write order matches. Actual live returnCPU and helper-written final bytes checked separately; live GPU/device writes elsewhere are not equated to offline RAM. Native test CPU cycle sums measure implementation cost, not physical timing. Selected supervised excursions do not establish source/vector identity or prove all frame differences; no new source/training/default/whole-game proof.')
        mark();save(ROOT/'verification'/('native-format-optimization-replay-'+args.label+'-current.json'),state);print(json.dumps(summary),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
    finally:n.close()
if __name__=='__main__':main()
