"""Fault controls and exact watch on actual v40 off/on CPU executions."""
import ctypes as c
import importlib.util
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_frame_acquire_phased_image_task_stack_v1 as matrix
import check_biwn_scheduler as scheduler
import shared_deck_frame_phased_image_full_observer_v2 as full
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    bp=V/'frame-acquire-phased-disc-build-v1-current.json';b=read(bp)
    text,_=full.observer_source(b,read(V/'native-Deck-coordinate-disc-build-current.json'))
    at=text.index('struct acquire_call {');end=text.index('\n}\n\n/* Read-only live checks',at)+2
    watch=text[at:end];pred=text[text.index('static unsigned phased_frame_code('):text.index('static void watch_acquire(')]
    # pred is adjacent to watch; avoid a duplicate definition in the extracted block.
    watch=watch.replace(pred,'')
    at=text.index('static unsigned task_id_valid(');end=text.index('\nstatic void arena_check_guards',at)
    bounds=text[at:end]
    out=V/'frame-phased-acquire-watch-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=out/'fixture.c';library=out/'fixture.dylib'
    stub='''#include <stdint.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const uint8_t *ram;static struct cpu current;static unsigned arena_active[102];
static uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
static void read_cpu(struct cpu *o){*o=current;}
static void emit(uint32_t pc){(void)pc;}
'''
    exports='''
void snapshot(const void *memory,const struct cpu *cpu){ram=memory;current=*cpu;}
void pc(uint32_t value){watch_acquire(value);}
void clear(void){memset(acquire_slots,0,sizeof(acquire_slots));memset(arena_active,0,sizeof(arena_active));acquire_entries=acquire_native_entries=acquire_returns=acquire_old_steps=acquire_monitor_errors=acquire_native_steps=acquire_loader_calls=acquire_user_stack_observations=acquire_user_stack_outside=0;acquire_pending=acquire_slot_count=acquire_max_private_depth=0;acquire_user_min_headroom=0xffffffffu;}
uint64_t stat(unsigned i){switch(i){case 0:return acquire_monitor_errors;case 1:return acquire_user_stack_outside;case 2:return acquire_pending;case 3:return acquire_entries;case 4:return acquire_native_entries;case 5:return acquire_returns;case 6:return acquire_loader_calls;default:return 0;}}
'''
    source.write_text(stub+bounds+pred+watch+exports)
    result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True)
    (out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    f=c.CDLL(str(library));f.snapshot.argtypes=[c.c_void_p,c.POINTER(scheduler.CPU)];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64
    state=dict(status='qualifying_exact_frame_watch',directory=str(out),pid=os.getpid(),new_predictions=0,new_training=False)
    def mark():save(out/'protocol.json',state);save(V/'frame-phased-acquire-watch-v1-current.json',state)
    mark();controls=[]
    for fault in ['none','callee','saved','SP','return_word','NZ','missing_return','outside']:
        memory=bytearray(0x200000);task=0xc2128;sp=task+530;memory[0xc0920:0xc0924]=task.to_bytes(4,'big');memory[sp:sp+4]=(0x3000).to_bytes(4,'big')
        cpu=scheduler.CPU();cpu.registers[:]=[0x11000000+i for i in range(16)];cpu.registers[15]=sp;cpu.usp=sp;cpu.ssp=0x1fc000;cpu.sr=0x71f
        incoming=list(cpu.registers);buffer=(c.c_uint8*len(memory)).from_buffer(memory)
        def observe(pc):
            before=bytes(cpu);ram_before=bytes(memory);f.snapshot(buffer,c.byref(cpu));f.pc(pc);assert before==bytes(cpu)and ram_before==memory
        f.clear();observe(0x1ac68);observe(b['frame_phased_early_address'])
        cpu.registers[15]=task+(37 if fault=='outside'else 200);observe(b['frame_phased_early_address']+8)
        for i,reg in enumerate([2,3,4,5,6,7,10,11,12]):memory[sp-44+4*i:sp-40+4*i]=incoming[reg].to_bytes(4,'big')
        memory[sp-4:sp]=incoming[14].to_bytes(4,'big');cpu.registers[:]=incoming;cpu.registers[0]=0;cpu.sr=0x714
        if fault=='callee':cpu.registers[2]^=1
        if fault=='saved':memory[sp-44]^=1
        if fault=='SP':cpu.registers[15]+=2
        if fault=='return_word':memory[sp]^=1
        if fault=='NZ':cpu.sr^=4
        if fault!='missing_return':observe(b['frame_phased_symbols']['biwn_frame_phased_return'])
        stats=[f.stat(i)for i in range(7)];assert bool(any(stats[:3]))==(fault!='none'),(fault,stats)
        controls.append(dict(fault=fault,rejected=bool(any(stats[:3])),stats=stats))
    save(out/'controls.json',controls)
    origin=matrix.nested.run;observed=[];calls=0;RAM_checks=0
    def run(*args,**kwargs):
        nonlocal calls,RAM_checks
        if not args[6]:return origin(*args,**kwargs)
        off=origin(*args,**kwargs);n=args[0];execute=n.lib.m68k_execute;f.clear();boundary={0x1ac68,b['frame_phased_early_address'],b['frame_phased_symbols']['biwn_frame_phased_return'],matrix.g.LOADER,*matrix.nested.loader.HELPERS}
        def step(*values):
            nonlocal calls,RAM_checks
            before=matrix.g.cpu(n);cpu=scheduler.CPU();cpu.registers[:]=before[:16];cpu.pc=before[16];cpu.sr=before[17];cpu.usp=before[18];cpu.ssp=before[19]
            raw=n.device.ram()if cpu.pc in boundary else None
            f.snapshot(n.device.pointer,c.byref(cpu));f.pc(cpu.pc);calls+=1
            assert matrix.g.cpu(n)==before,'Observer changed actual CPU'
            if raw is not None:assert n.device.ram()==raw,'Observer changed actual RAM';RAM_checks+=1
            return execute(*values)
        n.lib.m68k_execute=step
        try:on=origin(*args,**kwargs)
        finally:n.lib.m68k_execute=execute
        assert off['cpu']==on['cpu'] and off['ram']==on['ram'] and off['calls']==on['calls'],'Off/on changed CPU/fullRAM/helpers'
        stats=[f.stat(i)for i in range(7)];assert stats[:3]==[0,0,0] and stats[3]==stats[4]==stats[5]==1,stats
        observed.append(dict(lane=len(observed),stats=stats,complete_RAM_CPU_and_helpers_identical_without_exclusions=True));return on
    matrix.nested.run=run
    original=Path(matrix.__file__);script=out/'selected-matrix.py';body=original.read_text()
    anchor="plans=[(slot,i)for slot in [0,50,100]for i in range(len(cases))]+[(slot,slot%len(cases))for slot in range(101)]"
    assert body.count(anchor)==1;body=body.replace(anchor,"plans=[(slot,i)for slot in [0,100]for i in [0,3,12,15,24,27]]")
    body=body.replace('frame-acquire-phased-image-task-stack-v1','frame-phased-watch-selected-functional-v1');script.write_text(body)
    try:
        spec=importlib.util.spec_from_file_location('selected_phased_watch_matrix',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.main()
        assert len(observed)==24 and calls>0 and RAM_checks>0
        save(out/'actual-lanes.json',observed)
        state.update(status='terminal_exact_phased_frame_watch_fault_controls_and_actual_CPU_readonly_pass',controls=len(controls),actual_off_on_pairs=len(observed),observer_calls=calls,whole_RAM_immediate_boundary_checks=RAM_checks,complete_off_on_CPU_RAM_helpers_equal_without_exclusions=True,original_metadata_bound=38,stronger_separate_task_guard_bytes=64,fixture_GPU_arenas_inactive=True,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(full.__file__),bp,original,source,library,script,out/'controls.json',out/'actual-lanes.json']});mark();print(state['status'],calls,RAM_checks,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:matrix.nested.run=origin


if __name__=='__main__':main()
