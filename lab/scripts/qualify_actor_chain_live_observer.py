"""Qualify the exact C observer used for shared-C-chain gameplay monitoring.

Stratified original/native public roots cover nested original control calls,
physical capture canaries and virtual C collision boundaries. Full algorithm
coverage remains the prior7680case matrix. Corruptions affect decoded CPU/mirror
observations only, never native guest state. Read-only behavior is checked.
"""
import ctypes as c
import json
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_actor_chain as fixtures
import actor_chain_native_replay as replay
from actor_chain_observer_source import render

ROOT=fixtures.ROOT
class CPU(c.Structure):
    _fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]


def main():
    gate=fixtures.direct.g.read(ROOT/'verification/native-actor-chain-final-current.json')
    build=fixtures.direct.g.read(ROOT/'verification/native-actor-chain-build-normalized-current.json')
    for p,h in gate['source_sha256'].items():assert fixtures.direct.g.sha(p)==h,p
    snapshot,payload,symbols,_=fixtures.prepare(gate)
    out=ROOT/'verification/actor-chain-live-observer'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source,include=render(build)
    header='''#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char *ram;static unsigned errors;static void(*read_cpu)(struct cpu*);
#define BIWN_ACTOR_CHAIN_TASK() (0x1ff000u-0x3bcu)
static uint32_t rd32(uint32_t a){if(a>0x1ffffc){errors++;return 0;}return((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
static void emit(uint32_t pc){(void)pc;}
'''
    footer='''
static void array(FILE*f,const char*n,const uint64_t*v,unsigned count){fprintf(f,",\\"%s\\":[",n);for(unsigned i=0;i<count;i++)fprintf(f,"%s%llu",i?",":"",(unsigned long long)v[i]);fputc(']',f);}
void begin(const void*m,void*reader){ram=m;read_cpu=(void(*)(struct cpu*))reader;errors=0;memset(ach_calls,0,sizeof(ach_calls));ach_slots=ach_pending=0;
memset(ach_entries,0,sizeof(ach_entries));memset(ach_native,0,sizeof(ach_native));memset(ach_returns,0,sizeof(ach_returns));memset(ach_old_steps,0,sizeof(ach_old_steps));memset(ach_max_depth,0,sizeof(ach_max_depth));
for(unsigned i=0;i<3;i++)ach_min_headroom[i]=0xffffffffu;memset(ach_helper_counts,0,sizeof(ach_helper_counts));memset(ach_virtual_entries,0,sizeof(ach_virtual_entries));memset(ach_virtual_returns,0,sizeof(ach_virtual_returns));ach_source_steps=ach_errors=ach_context_errors=ach_virtual_errors=ach_stack_outside=ach_stack_observations=ach_context_checks=0;}
void step(uint32_t pc){watch_actor_chain(pc);}
void counts(uint64_t*out){unsigned at=0;uint64_t scalars[]={ach_pending,ach_source_steps,ach_errors,ach_context_errors,ach_virtual_errors,ach_stack_outside,ach_stack_observations,ach_context_checks,errors};for(unsigned i=0;i<9;i++)out[at++]=scalars[i];
const uint64_t*groups[]={ach_entries,ach_native,ach_returns,ach_old_steps,ach_max_depth,ach_min_headroom,ach_helper_counts,ach_virtual_entries,ach_virtual_returns};const unsigned widths[]={3,3,3,3,3,3,6,2,2};for(unsigned g=0;g<9;g++)for(unsigned i=0;i<widths[g];i++)out[at++]=groups[g][i];}
void dump(const char*path){FILE*f=fopen(path,"w");if(f){fputs("{\\"monitor\\":1",f);ach_dump(f);fputs("}\\n",f);fclose(f);}}
'''
    cpp=out/'monitor.c';cpp.write_text(header+source+footer);library=out/'monitor.dylib'
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.counts.argtypes=[c.POINTER(c.c_uint64)];lib.dump.argtypes=[c.c_char_p]
    native=fixtures.chain.Native();mirror=c.create_string_buffer(0x200000);negative=None;override=None;injected=False
    def reader(target):
        cpu=CPU();cpu.r[:]=[native.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=native.lib.m68k_get_reg(None,16);cpu.sr=native.lib.m68k_get_reg(None,17);cpu.usp=native.prefix[16]if cpu.sr&0x2000 else cpu.r[15];cpu.ssp=cpu.r[15]if cpu.sr&0x2000 else native.prefix[17]
        if override=='task_SP':cpu.r[15]=fixtures.chain.SP-920
        if override=='helper_X':cpu.sr^=16
        if override=='callee_D2':cpu.r[2]^=1
        c.memmove(target,c.byref(cpu),c.sizeof(cpu))
    callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader)
    watched={0x13c9a,0x13b5a,0x13bb0,0x13f10,0x13bae,0x13c98,0x13440,0xe220,0x1039c,0x102c4,0x1028e,0x10652,build['actor_move_entry'],build['actor_move_return'],*build['collision_entries'].values(),*build['collision_returns'].values(),build['actor_chain_virtual_collision_entry'],build['actor_chain_virtual_collision_return'],*[row['return_PC']for row in build['actor_chain_helpers']]}
    class Observer:
        def begin(self,*args):
            c.memmove(mirror,native.device.pointer,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p))
        def step(self,pc):
            nonlocal injected,override
            if pc in watched:c.memmove(mirror,native.device.pointer,0x200000)
            if negative and not injected:
                if negative=='task_SP'and pc==build['actor_move_entry']:override=negative;injected=True
                if negative=='helper_X'and pc==0x13440:override=negative;injected=True
                if negative=='callee_D2'and pc==build['actor_move_return']:override=negative;injected=True
                if negative=='virtual_SP'and pc==build['actor_chain_virtual_collision_entry']:
                    at=fixtures.chain.SP-360+60;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
                if negative=='saved_context'and pc==next(row['return_PC']for row in build['actor_chain_helpers']if row['target']==0x13440):
                    at=fixtures.chain.SP-360;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
            before=mirror.raw[:0x200000]if pc in watched else None;actual=native.device.ram()if pc in watched else None
            lib.step(pc);override=None
            if pc in watched:assert mirror.raw[:0x200000]==before and native.device.ram()==actual,'C observer wrote RAM'
        def finish(self):pass
    observer=Observer()
    def counts():
        values=(c.c_uint64*37)();lib.counts(values);return list(values)
    collisions=fixtures.direct.vectors();movements=fixtures.chain.vectors();groups=[]
    for entry in[0x13b5a,0x13bb0]:
        rows=[row for row in collisions if row['entry']==entry];indices=sorted(set([0,1,3,4,5,7,8,9]+list(range(0,len(rows),40))))
        groups.extend(('collision',fixtures.direct,i,rows[i])for i in indices)
    indices=sorted(set([0,16,32,80,96,112,160,176]+list(range(0,len(movements),20))))
    groups.extend(('movement',fixtures.chain,i,movements[i])for i in indices)
    state=dict(status='qualifying_shared_C_chain_live_observer',directory=str(out),pid=os.getpid(),planned=2*len(groups),completed=0);rows=[];controls=[]
    def mark():fixtures.direct.g.save(out/'protocol.json',state);fixtures.direct.g.save(ROOT/'verification/actor-chain-live-observer-active.json',state)
    mark()
    try:
        for number,(name,engine,index,case)in enumerate(groups):
            outputs=[]
            for compiled in[False,True]:
                expected=engine.execute(snapshot,case,payload,symbols,compiled);result,depth=replay.replay(engine,native,snapshot,case,payload,symbols,compiled,expected,observer);values=counts()
                if any(values[i]for i in[0,2,3,4,5,8]):
                    fixtures.direct.g.save(out/'failure.json',dict(group=name,index=index,compiled=compiled,case=case,counts=values));raise AssertionError('C live observer rejected valid execution')
                assert values[9:12]==values[15:18]
                assert values[12:15]==(values[9:12]if compiled else[0,0,0])
                if compiled:assert values[18:21]==[0,0,0]
                outputs.append(result);rows.append(dict(group=name,index=index,compiled=compiled,counts=values,native_depth=depth))
            assert outputs[0]==outputs[1];state['completed']=len(rows)
            if number%32==0:mark();print('Observer roots',number+1,'/',len(groups),flush=True)
        results=fixtures.direct.g.read(Path(gate['directory'])/'results.json');witness=next(row for row in results if row['group']=='movement'and row['candidate_depth']==564 and not(movements[row['index']]['sr']&0x2000));case=movements[witness['index']];expected=fixtures.chain.execute(snapshot,case,payload,symbols,True)
        for negative in['task_SP','virtual_SP','helper_X','saved_context','callee_D2']:
            injected=False;replay.replay(fixtures.chain,native,snapshot,case,payload,symbols,True,expected,observer);values=counts();assert injected and any(values[i]for i in[2,3,4,5,8]),negative
            controls.append(dict(defect=negative,rejected=True,counts=values,native_CPU_or_RAM_changed=False))
        negative=None;fixtures.direct.g.save(out/'results.json',rows);fixtures.direct.g.save(out/'negative-controls.json',controls);lib.dump(str(out/'last-negative-monitor.json').encode())
        paths=[Path(__file__),Path(replay.__file__),ROOT/'scripts/actor_chain_observer_source.py',include,cpp,library,out/'negative-controls.json',ROOT/'verification/native-actor-chain-build-normalized-current.json',Path(gate['binary']),Path(gate['ELF'])]
        state.update(status='terminal_shared_C_chain_live_observer_qualified',cases=len(groups),completed=len(rows),negative_controls=controls,max_native_depth=max(row['native_depth']for row in rows if row['compiled']),source_sha256={str(p):fixtures.direct.g.sha(p)for p in paths},scope=__doc__)
        mark();fixtures.direct.g.save(ROOT/'verification/actor-chain-live-observer-current.json',state);print(state['status'],len(rows))
    except BaseException as error:state.update(status='terminal_shared_C_chain_live_observer_failed',error=repr(error));mark();raise
    finally:native.close()


if __name__=='__main__':main()
