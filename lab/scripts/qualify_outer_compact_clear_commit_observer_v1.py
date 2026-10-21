"""Read-only clear witness over actual native CPU steps and host-only corruption replays."""
import ctypes as c, importlib.util, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone
import scene_gpu_family_scene_runtime_v2 as support
import shared_deck_outer_compact_full_observer_v1 as monitor
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
    bp=V/'native-outer-compact-disc-build-v1-current.json';build=read(bp)
    out=V/'outer-compact-clear-commit-observer-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    stub='''#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000],*ram=memory;\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}\nstatic uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}\nstatic void read_cpu(struct cpu *s){*s=current;}\n'''
    extra='''\nvoid snapshot(const void *raw,const struct cpu *s){memcpy(memory,raw,sizeof(memory));current=*s;}\nvoid pc(uint32_t v){c26_watch(v);}\nvoid clear(void){memset(c26_slots,0,sizeof(c26_slots));c26_entries=c26_returns=c26_errors=c26_original_entries=c26_original_returns=0;}\nuint64_t stat(unsigned n){if(n==0)return c26_entries;if(n==1)return c26_returns;if(n==2)return c26_errors;if(n==3)return c26_pending_total();if(n==4)return c26_original_entries;return c26_original_returns;}\n'''
    source=out/'fixture.c';source.write_text(stub+monitor.clear_monitor(build)+extra);lib=out/'fixture.dylib'
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    f=c.CDLL(str(lib));f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64;f.clear_dump.argtypes=[c.c_char_p]
    s=build['shared_Deck_symbols'];sites={s['biwn_v26_clear_begin'],s['biwn_v26_clear_end']};rows=[];checkpoints=[];selected=False;collect=False;original=support.Runtime
    def finish():
        values=[f.stat(i)for i in range(6)]
        if not any(values):return
        assert values[0]==values[1] and values[2:]==[0]*4,values
        rows.append(dict(entries=values[0],returns=values[1],errors=values[2],pending=values[3],original_entries=values[4],original_returns=values[5]));f.clear()
    class Observed(original):
        in_reference=False
        def reset(self,*args):finish();f.clear();return super().reset(*args)
        def native(self,*args):
            self.in_reference=True
            try:return super().native(*args)
            finally:self.in_reference=False;f.clear()
        def __init__(self,*args):
            super().__init__(*args);self.old_execute=self.core.m68k_execute
            def step(*args):
                nonlocal selected,collect
                if not self.in_reference:
                    state=super(Observed,self).cpu()
                    if state.pc in sites:
                        raw=self.device.ram()
                        if state.pc==s['biwn_v26_clear_begin'] and not selected:collect=True
                        if collect:
                            checkpoints.append((raw,support.base.CPU.from_buffer_copy(bytes(state))))
                            i=len(checkpoints)-1;(out/f'checkpoint-{i}-RAM.bin').write_bytes(raw);save(out/f'checkpoint-{i}-CPU.json',support.base.cd.scheduler.cpu_dict(state))
                        f.snapshot(c.create_string_buffer(raw),c.byref(state));f.pc(state.pc)
                        if state.pc==s['biwn_v26_clear_end']and collect:collect=False;selected=True
                return self.old_execute(*args)
            self.core.m68k_execute=step
        def close(self):finish();self.core.m68k_execute=self.old_execute;return super().close()
    support.Runtime=Observed;f.clear()
    try:
        text=(ROOT/'scripts/check_outer_compact_final_bridge_v1.py').read_text().replace("out=V/'outer-compact-final-bridge-v1'","out=V/'outer-compact-clear-commit-observed-body-v1'")
        script=out/'actual-native-harness.py';script.write_text(text);spec=importlib.util.spec_from_file_location('clear_monitor_actual',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sys.argv=[str(script),'--limit','64'];m.main();finish()
    finally:support.Runtime=original
    assert sum(x['entries']for x in rows)>0 and [x.pc for _,x in checkpoints]==[s['biwn_v26_clear_begin'],s['biwn_v26_clear_end']]
    raw0,state0=checkpoints[0];task=int.from_bytes(raw0[0xc0920:0xc0924],'big');frame=build['deck_arena_address']+task-0xc0928+144;guest_sp=int.from_bytes(raw0[frame+64:frame+68],'big');faults=[]
    def replay(name,modify=None,skip=None):
        f.clear()
        for i,(raw,cpu)in enumerate(checkpoints):
            if i==skip:continue
            memory=bytearray(raw);state=support.base.CPU.from_buffer_copy(bytes(cpu))
            if modify:modify(i,memory,state)
            f.snapshot(c.create_string_buffer(bytes(memory)),c.byref(state));f.pc(state.pc)
        path=out/('control-'+name+'.json');assert f.clear_dump(str(path).encode())==0;d=read(path)
        return d['errors']==d['pending']==0 and d['entries']==d['returns']==1
    assert replay('legal')
    corrupt=[('begin_PC',0,frame+68),('begin_bank',0,frame+72),('return_word',1,guest_sp),('saved_D0',1,guest_sp-4),('D0',1,frame+4),('A0',1,frame+36),('SP',1,frame+64),('PC',1,frame+68),('USP',1,frame+72),('SSP',1,frame+76),('SR_X',1,frame+81),('error',1,frame+97),('active',1,frame+117),('bus',1,frame),('service',1,frame+82),('budget',1,frame+90)]
    for name,index,address in corrupt:
        def mutate(i,memory,state,index=index,address=address,name=name):
            if i==index:memory[address]^=16 if name=='SR_X'else 1
        assert not replay(name,mutate),name;faults.append(dict(name=name,rejected=True))
    for i,name in enumerate(['missing_begin','missing_end']):assert not replay(name,skip=i),name;faults.append(dict(name=name,rejected=True))
    def badstack(i,memory,state):
        if i==1:state.registers[15]=0
    assert not replay('physical_stack',badstack);faults.append(dict(name='physical_stack',rejected=True))
    save(out/'cases.json',rows);save(out/'faults.json',faults)
    proof=dict(status='terminal_clear_monitor_actual_CPU_and_fault_controls_pass',directory=str(out),actual_native_scene_lanes=64,native_clear_entries=sum(x['entries']for x in rows),rejected_fault_controls=len(faults),host_guest_RAM_writes=0,new_predictions=0,new_training=False,
               source_sha256={str(p):sha(p)for p in [Path(__file__),Path(monitor.__file__),ROOT/'scripts/scene_clear_observer_v1.inc.c',bp,source,lib,script,out/'cases.json',out/'faults.json',*out.glob('checkpoint-*')]},
               scope=__doc__+' All registers/banks, finalX=1/NZVC=0, guest return/savedD0, frame metadata and C stack are checked. Actual physical MMIO instructions execute with declared post-read input fixtures; MMIO ordering is separately verified. No guest state writes by observation or fault replay; no fresh-game/IRQ/console proof.')
    save(out/'review.json',proof);save(V/'outer-compact-clear-commit-observer-v1-current.json',proof);print(proof['status'],proof['native_clear_entries'],len(faults),flush=True)

if __name__=='__main__':main()
