"""Qualify the read-only interior oracle on original/final-address component fixtures."""
import ctypes as c
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import check_biwn_native_interior_select_v2 as gate
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


class CPU(c.Structure):
    _fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]


def read(p):return json.loads(Path(p).read_text())


def main():
    bp=ROOT/'verification/native-interior-select-disc-build-current.json';build=read(bp)
    assert build['status']=='terminal_native_interior_select_disc_built_entry_verified_pending_gameplay'
    proof=read(build['component_gate']);assert proof['stable_cases']==1958 and proof['changing_cases']==768
    assert sha(build['component_gate'])==build['component_gate_sha256']
    for p,h in proof['dependencies_sha256'].items():assert sha(p)==h,p
    out=ROOT/'verification/native-interior-monitor'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'scripts/native_interior_select_observer.inc.c';text=source.read_text()
    for key,value in {'__INTERIOR_START__':build['interior_select_start'],'__INTERIOR_END__':build['interior_select_end'],
                      '__INTERIOR_ACTOR_ENTRY__':build['interior_actor_entry'],'__INTERIOR_SPRITE_ENTRY__':build['interior_sprite_entry'],
                      '__INTERIOR_RETURN__':build['interior_select_return']}.items():
        assert key in text;text=text.replace(key,str(value)+'u')
    header='''#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char *ram;static uint32_t frame,errors;static void (*read_cpu)(struct cpu*);
/* Fixture-only task-context adapter. Dense table fixtures overlap C0920;
 * do not alter any fixture RAM or predictor memory reads to install a task. */
#define BIWN_INTERIOR_TASK() (0x1e0000u-0x404u)
static uint32_t rd16(uint32_t a){if(a>0x1ffffe){errors++;return 0;}return ((uint32_t)ram[a]<<8)|ram[a+1];}
static uint32_t rd32(uint32_t a){if(a>0x1ffffc){errors++;return 0;}return (rd16(a)<<16)|rd16(a+2);}
static void emit(uint32_t pc){(void)pc;}
static void select_debug_cpu(FILE *file,const struct cpu *cpu){
    fprintf(file,"{\\\"D0\\\":%u,\\\"D1\\\":%u,\\\"A0\\\":%u,\\\"A1\\\":%u,\\\"SR\\\":%u}",cpu->r[0],cpu->r[1],cpu->r[8],cpu->r[9],cpu->sr);
}
'''
    footer='''
void begin(const void *memory,void *reader){
    ram=memory;read_cpu=(void(*)(struct cpu*))reader;
    memset(interior_calls,0,sizeof(interior_calls));interior_slots=interior_pending=interior_debug_count=0;
    interior_entries=interior_native_entries=interior_returns=interior_old_steps=interior_native_steps=0;
    interior_errors=interior_skips=interior_successes=interior_failures=interior_iterations=interior_user_observations=interior_stack_outside=0;
    memset(interior_kind_entries,0,sizeof(interior_kind_entries));memset(interior_kind_successes,0,sizeof(interior_kind_successes));memset(interior_kind_failures,0,sizeof(interior_kind_failures));
    interior_min_headroom=0xffffffffu;interior_max_depth=errors=0;
}
void step(uint32_t pc){watch_interior(pc);}
uint32_t check(void){return errors+(uint32_t)interior_errors+(uint32_t)interior_stack_outside+interior_pending+(interior_entries!=1)+(interior_returns!=1);}
void dump(const char *path){FILE *f=fopen(path,"w");fputs("{\\\"diagnostics\\\":true",f);interior_debug_dump(f);fputs("}",f);fclose(f);}
'''
    cpp=out/'monitor.c';cpp.write_text(header+text+footer);library=out/'monitor.dylib'
    result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,
                          env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32]
    lib.check.restype=c.c_uint32;lib.dump.argtypes=[c.c_char_p]
    current=CPU();callback=c.CFUNCTYPE(None,c.POINTER(CPU))(lambda target:c.memmove(target,c.byref(current),c.sizeof(current)))
    baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();patched=bytearray(baseline)
    payload=Path(build['linked_component']).read_bytes();assert len(payload)==18888
    start=build['resident_address'];patched[start:start+len(payload)]=payload
    for entry,target in [(0x10520,build['interior_actor_entry']),(0x105da,build['interior_sprite_entry'])]:
        patched[entry:entry+8]=b'\x4e\xf9'+target.to_bytes(4,'big')+b'\x4e\x71'
    engine=gate.engine;engine.BASE=build['interior_select_start'];engine.SP=gate.SP;engine.STOP=gate.STOP;engine.seed=gate.seed
    length=build['interior_select_end']-engine.BASE;native=engine.Native()
    cases=gate.vectors();checks=[];negatives=[]
    deps=[source,Path(__file__),cpp,library,bp,Path(build['component_gate']),Path(gate.__file__),Path(engine.__file__),
          ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']
    hashes={str(p):sha(p)for p in deps}
    state=dict(status='running_interior_live_oracle_fixtures',pid=os.getpid(),directory=str(out),planned=len(cases)*2,completed=0,
               source_sha256=hashes,new_training=False,default_promoted=False)
    def mark():
        save(out/'protocol.json',state);save(ROOT/'verification/native-interior-monitor-active.json',state)
    mark()
    def before(case,seeded):
        memory=c.create_string_buffer(seeded)
        current.r[:]=case['incoming']+[gate.SP];current.pc=engine.ENTRY;current.sr=case['sr']
        current.usp=0x1fe000 if case['sr']&0x2000 else gate.SP
        current.ssp=gate.SP if case['sr']&0x2000 else 0x1ff000
        lib.begin(memory,c.cast(callback,c.c_void_p));lib.step(engine.ENTRY)
        assert memory.raw[:0x200000]==seeded,'Monitor wrote entry RAM'
        return memory
    def after(case,memory,ram,cpu,original):
        c.memmove(memory,ram,len(ram));current.r[:]=cpu[:16];current.r[15]=gate.SP
        current.pc=(0x10650 if case['kind'] else 0x105d8)if original else build['interior_select_return']
        current.sr=cpu[17];current.usp=cpu[18]-(4 if not case['sr']&0x2000 else 0)
        current.ssp=cpu[19]-(4 if case['sr']&0x2000 else 0)
    try:
        for index,case in enumerate(cases):
            engine.ENTRY,engine.END=gate.RANGES[case['kind']]
            for original,image in [(True,baseline),(False,patched)]:
                seeded=gate.seed(image,case);memory=before(case,seeded)
                ram,cpu,_,steps,cycles,minimum=engine.native(native,image,case,length,original)
                after(case,memory,ram,cpu,original);lib.step(current.pc);error=lib.check()
                assert memory.raw[:0x200000]==ram,'Monitor wrote return RAM'
                if error:
                    lib.dump(str(out/'failure.json').encode());save(out/'failure-case.json',dict(index=index,original=original,case=case,errors=error))
                    raise AssertionError(f'oracle mismatch{index} original={original} errors={error}')
                checks.append(dict(index=index,kind=case['kind'],original=original,steps=steps,cycles=cycles,private_depth=gate.SP-minimum))
                if index in [0,3] and not original:
                    memory=before(case,seeded);after(case,memory,ram,cpu,original)
                    if index==0:current.r[0]^=1;reason='wrong returned D0'
                    else:
                        a=(case['object']&0xffffff)+42
                        c.memmove(c.addressof(memory)+a,bytes([memory.raw[a]^1]),1);reason='wrong actor selected field'
                    lib.step(current.pc);assert lib.check()>0,'Injected return corruption escaped the observer'
                    negatives.append(dict(index=index,reason=reason,rejected=True))
                state['completed']+=1
            if index%128==0:mark()
        assert len(negatives)==2
        assert all(sha(p)==h for p,h in hashes.items()),'Monitor inputs changed during qualification'
        save(out/'results.json',checks);save(out/'negative-controls.json',negatives)
        state.update(status='terminal_interior_live_oracle_stable_fixtures_pass',original_cases=len(cases),compiled_cases=len(cases),
                     negative_controls=negatives,scope='Read-only stable-entry/return oracle qualified on1958original+1958final-address compiled fixtures, both10520/105DA and all99original sites covered by underlying gate. Exact fixture RAM preserved, including dense32768records; fixture-only task-ID macro replaces context lookup, not any predictor RAM read. Post-RTS CPU adapted to pre-RTS at publicSP. Entry/return RAM-write guards and two corrupted-return negatives pass. Does not predict changing reads or arbitrary concurrent/device behavior; no per-instruction live stack, gameplay or physical hardware claim.')
        mark();save(ROOT/'verification/native-interior-monitor-current.json',state)
        print(json.dumps({k:state[k]for k in ['status','original_cases','compiled_cases']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_interior_live_oracle_failed',error=repr(error));mark();raise
    finally:native.close()


if __name__=='__main__':main()
