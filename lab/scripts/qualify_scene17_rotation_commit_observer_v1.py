"""Native rotation witness over actual CPU steps, with independent host-only corruption replays."""
import ctypes as c, importlib.util, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone
import scene17_host_runtime_v1 as support
import shared_deck_scene17_rotation_complete_observer_v1 as monitor
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    bp=V/'native-scene17-rotation-disc-build-v1-current.json';build=read(bp)
    out=V/'scene17-rotation-commit-observer-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    stub='''#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000],*ram=memory;\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}\nstatic uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}\nstatic void read_cpu(struct cpu *s){*s=current;}\n'''
    extra='''\nvoid snapshot(const void *raw,const struct cpu *s){memcpy(memory,raw,sizeof(memory));current=*s;}\nvoid pc(uint32_t v){r25_watch(v);}\nvoid clear(void){memset(r25_slots,0,sizeof(r25_slots));r25_entries=r25_returns=r25_helpers=r25_helper_returns=r25_errors=0;}\nuint64_t stat(unsigned n){if(n==0)return r25_entries;if(n==1)return r25_returns;if(n==2)return r25_helpers;if(n==3)return r25_helper_returns;if(n==4)return r25_errors;return r25_pending_total();}\n'''
    source=out/'fixture.c';source.write_text(stub+monitor.rotation_monitor(build)+extra);lib=out/'fixture.dylib'
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    f=c.CDLL(str(lib));f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64;f.rotation_dump.argtypes=[c.c_char_p]
    syms=build['shared_Deck_symbols'];sites={syms['biwn_v25_rotation_begin'],syms['biwn_v25_rotation_end'],syms['biwn_v4_scene_helper_return'],0x185b2}
    rows=[];checkpoints=[];selected=False;collect=False;original=support.Runtime
    def observe(state,raw):
        nonlocal selected,collect
        if state.pc==syms['biwn_v25_rotation_begin'] and not selected and not checkpoints:collect=True
        if collect:
            checkpoints.append((raw,support.base.CPU.from_buffer_copy(bytes(state))))
            index=len(checkpoints)-1;(out/f'debug-{index}-RAM.bin').write_bytes(raw)
            save(out/f'debug-{index}-CPU.json',support.base.cd.scheduler.cpu_dict(state))
        f.snapshot(c.create_string_buffer(raw),c.byref(state));f.pc(state.pc)
        if collect:save(out/f'debug-{len(checkpoints)-1}-stats.json',[f.stat(i) for i in range(6)])
        if state.pc==syms['biwn_v25_rotation_end'] and collect:collect=False;selected=True
    def finish():
        values=[f.stat(i) for i in range(6)]
        if not any(values):return
        assert values[4]==values[5]==0 and values[:4]==[values[0]]*4, values
        rows.append(dict(entries=values[0],returns=values[1],helper_entries=values[2],helper_returns=values[3],errors=values[4],pending=values[5]));f.clear()
    class Observed(original):
        in_reference=False
        def reset(self,*args):
            finish();f.clear();return super().reset(*args)
        def native(self,*args):
            self.in_reference=True
            try:return super().native(*args)
            finally:self.in_reference=False;f.clear()
        def scripted(self,state,target):
            # The component harness applies this external service before its
            # RTS instruction. Its entry must be observed before that effect,
            # exactly where a real185B2 first instruction would be observed.
            if not self.in_reference and target==0x185b2:
                observe(state,self.device.ram())
            return super().scripted(state,target)
        def __init__(self,*args):
            super().__init__(*args);self.old_execute=self.core.m68k_execute
            def step(*args):
                if not self.in_reference:
                    state=super(Observed,self).cpu()
                    if state.pc in sites and state.pc!=0x185b2:
                        observe(state,self.device.ram())
                return self.old_execute(*args)
            self.core.m68k_execute=step
        def close(self):
            finish();self.core.m68k_execute=self.old_execute;return super().close()
    support.Runtime=Observed;f.clear()
    try:
        text=(ROOT/'scripts/check_scene17_rotation_final_bridge_v1.py').read_text().replace("out=V/'scene17-rotation-final-bridge-v1'","out=V/'scene17-rotation-commit-observed-body-v1'")
        script=out/'actual-native-harness.py';script.write_text(text);spec=importlib.util.spec_from_file_location('rotation_monitor_actual',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sys.argv=[str(script),'--limit','64'];m.main();finish()
    finally:support.Runtime=original
    assert rows and sum(x['entries'] for x in rows)>0
    assert [s.pc for _,s in checkpoints]==[syms['biwn_v25_rotation_begin'],0x185b2,syms['biwn_v4_scene_helper_return'],syms['biwn_v25_rotation_end']], [hex(s.pc) for _,s in checkpoints]
    raw0,s0=checkpoints[0];task=int.from_bytes(raw0[0xc0920:0xc0924],'big');frame=build['deck_arena_address']+task-0xc0928+144;faults=[]
    for i,(raw,cpu) in enumerate(checkpoints):
        (out/f'checkpoint-{i}-RAM.bin').write_bytes(raw);save(out/f'checkpoint-{i}-CPU.json',support.base.cd.scheduler.cpu_dict(cpu))
    def replay(name,modify=None,skip=None):
        f.clear()
        for i,(raw,cpu) in enumerate(checkpoints):
            if skip==i:continue
            memory=bytearray(raw);state=support.base.CPU.from_buffer_copy(bytes(cpu))
            if modify:modify(i,memory,state)
            f.snapshot(c.create_string_buffer(bytes(memory)),c.byref(state));f.pc(state.pc)
        path=out/('control-'+name+'.json');assert f.rotation_dump(str(path).encode())==0;d=read(path)
        return d['errors']==d['pending']==0 and d['entries']==d['returns']==d['helper_entries']==d['helper_returns']==1
    assert replay('legal')
    for name,index,address in [('begin_PC',0,frame+68),('begin_bank',0,frame+72),('buffer_rotation',1,0xbd83c),('display_pointer',1,0x43daa),('saved_return',1,frame+110),('saved_CPU',1,frame+102),('saved_A2',3,frame+44),('end_SP',3,frame+64),('end_PC',3,frame+68),('end_SR',3,frame+81),('active',3,frame+117),('error',3,frame+97),('service',3,frame+82)]:
        def mutate(i,memory,state,index=index,address=address):
            if i==index:memory[address]^=1
        assert not replay(name,mutate),name;faults.append(dict(name=name,rejected=True))
    for name,index,reg in [('helper_A0',1,8),('helper_SP',1,15),('return_SP',2,15)]:
        def mutate(i,memory,state,index=index,reg=reg):
            if i==index:state.registers[reg]^=2
        assert not replay(name,mutate),name;faults.append(dict(name=name,rejected=True))
    for index,name in enumerate(['missing_begin','missing_helper_entry','missing_helper_return','missing_end']):
        assert not replay(name,skip=index),name;faults.append(dict(name=name,rejected=True))
    save(out/'cases.json',rows);save(out/'faults.json',faults)
    proof=dict(status='terminal_rotation_monitor_actual_CPU_and_fault_controls_pass',directory=str(out),actual_native_scene_lanes=64,
               native_rotation_entries=sum(x['entries'] for x in rows),rejected_fault_controls=len(faults),host_guest_RAM_writes=0,
               new_predictions=0,new_training=False,source_sha256={str(p):sha(p) for p in [Path(__file__),Path(monitor.__file__),ROOT/'scripts/scene_rotation_observer_v1.inc.c',bp,source,lib,script,out/'cases.json',out/'faults.json',*out.glob('checkpoint-*')]},
               scope=__doc__+' Observer copies snapshots before native instruction execution. External185B2entry is observed before its declared fixture effect; its RTS return and native markers use actual m68k_execute boundaries. Buffer triples, helper-entryCPU/flags/stack arguments, retained185B2returnCPU and native logical commit are checked. Host corruption replay does not modify game state. Services are component fixtures, not fresh game or IRQ proof.')
    save(out/'review.json',proof);save(V/'scene17-rotation-commit-observer-v1-current.json',proof);print(proof['status'],proof['native_rotation_entries'],len(faults),flush=True)


if __name__=='__main__':main()
