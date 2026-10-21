"""Synthetic fault controls for the exact outer watcher and completion gate."""
import ctypes as c,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';pre=read(v/'frame-phased-image-geometry-observer-qualified-v1-current.json');source=Path(pre['observer']);text=source.read_text()
    lo=text.index('/* O6_WATCHER_BEGIN:');hi=text.index('/* O6_WATCHER_END */',lo);monitor=text[lo:hi]
    array=next(line for line in text.splitlines()if line.startswith('static const uint32_t o6_inner_returns'))
    build=read(v/'frame-acquire-phased-disc-build-v1-current.json');s=build['outer_symbols'];slot=6;base=build['outer_arena_address']+slot*384;frame=base+16;sp=0xc0928+slot*1024+768
    out=v/'outer-frame-phased-image-geometry-observer-qualification-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    stub=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static struct cpu current;
static uint8_t memory[0x200000],*ram=memory,o6_used[101];
static uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)memory[a]<<8)|memory[a+1];}
static void read_cpu(struct cpu *out){*out=current;}
'''
    hooks=r'''
void fixture_reset(void){
 memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));memset(o6_used,0,sizeof(o6_used));
 memset(o6_mode,0,sizeof(o6_mode));memset(o6_helper_pending,0,sizeof(o6_helper_pending));memset(o6_incoming,0,sizeof(o6_incoming));
 memset(o6_entry_word,0,sizeof(o6_entry_word));memset(o6_call_sp,0,sizeof(o6_call_sp));memset(o6_logical_return,0,sizeof(o6_logical_return));memset(o6_shadow,0,sizeof(o6_shadow));
 memset(o6_helper_entries,0,sizeof(o6_helper_entries));memset(o6_helper_returns,0,sizeof(o6_helper_returns));
 o6_public=o6_native_entries=o6_native_returns=o6_original_returns=o6_original_steps=o6_fallbacks=o6_iterations=o6_original_iterations=o6_wait_slices=o6_errors=o6_C_outside=o6_C_observations=o6_protected_checks=o6_scheduler_boundaries=0;o6_min=368;o6_min_heap=0xffffffffu;
}
void fixture_register(unsigned i,uint32_t v){if(i<16)current.r[i]=v;}
void fixture_sr(uint16_t v){current.sr=v;}
void fixture_long(uint32_t a,uint32_t v){memory[a]=(uint8_t)(v>>24);memory[a+1]=(uint8_t)(v>>16);memory[a+2]=(uint8_t)(v>>8);memory[a+3]=(uint8_t)v;}
void fixture_word(uint32_t a,uint16_t v){memory[a]=(uint8_t)(v>>8);memory[a+1]=(uint8_t)v;}
void fixture_pc(uint32_t pc){o6_watch(pc);}
uint64_t fixture_stat(unsigned n){
 switch(n){case0:return0;}
 if(n==0)return o6_errors;if(n==1)return o6_pending_total();if(n==2)return o6_helper_pending_total();if(n==3)return o6_C_outside;
 if(n==4)return o6_public;if(n==5)return o6_native_entries;if(n==6)return o6_native_returns;if(n==7)return o6_original_returns;
 if(n==8)return o6_helper_entries[1];if(n==9)return o6_helper_returns[1];if(n==10)return o6_C_observations;if(n==11)return o6_protected_checks;return0;
}
'''.replace(' switch(n){case0:return0;}','').replace('return0','return 0')
    fixture=out/'fixture.c';fixture.write_text(stub+array+'\n'+monitor+hooks);library=out/'fixture.dylib'
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(fixture),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    lib=c.CDLL(str(library));lib.fixture_long.argtypes=[c.c_uint32,c.c_uint32];lib.fixture_word.argtypes=[c.c_uint32,c.c_uint16];lib.fixture_register.argtypes=[c.c_uint,c.c_uint32];lib.fixture_pc.argtypes=[c.c_uint32];lib.fixture_sr.argtypes=[c.c_uint16];lib.fixture_stat.argtypes=[c.c_uint];lib.fixture_stat.restype=c.c_uint64
    put=lib.fixture_long;reg=lib.fixture_register;pc=lib.fixture_pc
    variants=['legal_native','legal_original','bad_task','duplicate_public','bad_C_stack','bad_commit_register','bad_commit_SR','bad_commit_PC','bad_active','bad_C_saved_SP','bad_CPU_pointer','bad_helper_PC','bad_logical_return','bad_helper_return_SP','missing_helper_return','missing_outer_return','protected_frame_corruption','bad_outer_SP','bad_outer_A6','bad_outer_word']
    rows=[]
    for name in variants:
        lib.fixture_reset();native=name!='legal_original';put(0xc0920,1 if name=='bad_task'else 0xc0928+slot*1024);put(0x112d64,20000)
        values=[0x11110000+i for i in range(16)];values[15]=sp
        for i,value in enumerate(values):reg(i,value)
        put(sp,0xdeadbeee);pc(0x11e6c)
        if name=='duplicate_public':pc(0x11e6c)
        if native:
            pc(s['biwn_outer_entry']);reg(15,base+(140 if name=='bad_C_stack'else 204));pc(s['biwn_outer_asm_end']);reg(15,sp-12)
            for i,value in enumerate([*values[:15],sp-12]):put(frame+4+i*4,value)
            lib.fixture_word(frame+80,1 if name=='bad_commit_SR'else 0);put(frame+68,0x11f50 if name=='bad_commit_PC'else 0x11e86);put(frame+94,6);put(frame+114,0 if name=='bad_active'else 1)
            if name=='bad_commit_register':put(frame+4,7)
            pc(s['biwn_outer_iteration_boundary'])
            put(frame+98,base+(140 if name=='bad_C_saved_SP'else 204));put(frame+102,base+(100 if name=='bad_CPU_pointer'else 20));put(base+20+64,0x1182a if name=='bad_helper_PC'else 0x11828)
            put(frame+106,sp-16);put(frame+110,0x11e8e if name=='bad_logical_return'else 0x11e8c);put(sp-16,s['biwn_outer_helper_return']);reg(15,sp-16);pc(0x11828)
            if name=='protected_frame_corruption':put(base+300,1)
            pc(build['shared_Deck_symbols']['biwn_v4_scan_return'])
            if name!='missing_helper_return':reg(15,sp-10 if name=='bad_helper_return_SP'else sp-12);pc(s['biwn_outer_helper_return'])
        else:
            pc(0x11e86);put(sp-16,0x11e8c);reg(15,sp-16);pc(0x11828);reg(15,sp-12);pc(0x11e8c)
        reg(15,sp+2 if name=='bad_outer_SP'else sp)
        if name=='bad_outer_A6':reg(14,7)
        if name=='bad_outer_word':put(sp,0xdeadbeec)
        if native:
            for i,value in enumerate(values):put(frame+4+i*4,value)
            lib.fixture_word(frame+80,0);put(frame+68,0x11f6a);put(frame+94,0);put(frame+114,0)
        if name!='missing_outer_return':pc(s['biwn_outer_return']if native else 0x11f6a)
        stats=[lib.fixture_stat(i)for i in range(12)]
        accepted=not any(stats[:4])and stats[4]==1 and stats[8]==stats[9]==1 and (stats[5]==stats[6]==1 and stats[7]==0 and stats[10]>0 if native else stats[5]==stats[6]==0 and stats[7]==1)
        assert accepted==name.startswith('legal_'),(name,stats)
        rows.append(dict(case=name,gate_accepted=accepted,stats=stats))
    save(out/'cases.json',rows);proof=dict(status='terminal_outer_watcher_two_legal_eighteen_fault_controls_pass',directory=str(out),legal_controls=2,rejected_fault_controls=len(rows)-2,game_execution=False,
        source_sha256={str(p):sha(p)for p in [Path(__file__),source,fixture,library,out/'cases.json']},scope=__doc__+' Exact extracted watcher. Stubs supply CPU and RAM. Does not qualify all retained monitors, real scheduler behavior, timing, game correctness or observer nonintrusion.')
    save(out/'review.json',proof);save(v/'outer-frame-phased-image-geometry-observer-qualified-v1-current.json',proof);print(proof['status'],len(rows)-2,flush=True)


if __name__=='__main__':main()
