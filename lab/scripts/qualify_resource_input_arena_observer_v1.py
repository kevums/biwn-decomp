"""Fault controls for exact v39 resource/input observer; fixture buffers only."""
import ctypes as c
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from shared_deck_input_arena_image_full_observer_v2 import resource_monitor


def main():
    bp=V/'native-input-arena-disc-build-v1-current.json';b=read(bp)
    body=resource_monitor(b);out=V/'resource-input-arena-observer-qualified-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    stub='''#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static uint8_t owned[0x200000],*ram=owned;
static struct cpu current;
static unsigned arena_active[102],arena_used[102];
static uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}
static void read_cpu(struct cpu *o){*o=current;}
static unsigned task_id_valid(uint32_t task){return task>=0xc0928u&&task<0xd9d28u&&!((task-0xc0928u)&1023u);}
static unsigned task_arena_slot(uint32_t task){return task_id_valid(task)?(task-0xc0928u)/1024u:101u;}
static void arena_check_guards(void){}
'''
    arrays=['r39_mode','r39_helper','i39_pending','i39_route','r39_incoming','i39_incoming','r39_word','r39_low','r39_high','i39_entry_sp','r39_shadow','arena_active','arena_used']
    zero=['r39_public','r39_entries','r39_returns','r39_errors','r39_alias_errors','r39_C_outside','r39_C_observations','r39_guest_observations','r39_parked_checks','r39_helper_entries','r39_helper_returns','i39_calls','i39_native','i39_original','i39_returns','i39_errors','i39_C_outside','i39_C_observations','r39_guest_depth','i39_guest_depth','r39_live','i39_live','r39_helpers_live']
    hooks='\nvoid fixture_reset(void){ram=owned;memset(owned,0,sizeof(owned));memset(&current,0,sizeof(current));'+''.join('memset('+name+',0,sizeof('+name+'));'for name in arrays)+''.join(name+'=0;'for name in zero)+'r39_C_low=240;}\n'
    hooks+='''void fixture_put(uint32_t a,uint32_t v){ram[a]=v>>24;ram[a+1]=v>>16;ram[a+2]=v>>8;ram[a+3]=v;}
void fixture_word(uint32_t a,uint16_t v){ram[a]=v>>8;ram[a+1]=v;}
void fixture_reg(unsigned i,uint32_t v){if(i<16)current.r[i]=v;}
void fixture_sr(uint16_t v){current.sr=v;}
void fixture_PC(uint32_t pc){current.pc=pc;}
void fixture_observe(uint32_t pc){r39_watch(pc);}
void fixture_CPU(void *out){memcpy(out,&current,sizeof(current));}
void fixture_RAM(void *out){memcpy(out,ram,0x200000);}
void fixture_live(void *memory,const struct cpu *cpu,uint32_t pc){ram=memory;current=*cpu;r39_watch(pc);}
void fixture_active(unsigned slot,unsigned value){if(slot<102)arena_active[slot]=value;}
uint64_t fixture_stat(unsigned n){
 if(n==0)return r39_errors;if(n==1)return r39_alias_errors;if(n==2)return r39_C_outside;if(n==3)return r39_pending_total();
 if(n==4)return r39_helper_total();if(n==5)return r39_returns;if(n==6)return r39_helper_returns;if(n==7)return i39_errors;
 if(n==8)return i39_C_outside;if(n==9)return i39_pending_total();if(n==10)return i39_returns;if(n==11)return i39_native;
 if(n==12)return i39_original;if(n==13)return r39_parked_checks;if(n==14)return r39_helper_entries;return0;
}
'''.replace('return0','return 0')
    source=out/'fixture.c';source.write_text(stub+body+hooks);library=out/'fixture.dylib'
    result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True)
    (out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    f=c.CDLL(str(library));f.fixture_put.argtypes=[c.c_uint32,c.c_uint32];f.fixture_word.argtypes=[c.c_uint32,c.c_uint16];f.fixture_reg.argtypes=[c.c_uint,c.c_uint32];f.fixture_sr.argtypes=[c.c_uint16];f.fixture_PC.argtypes=f.fixture_observe.argtypes=[c.c_uint32];f.fixture_active.argtypes=[c.c_uint,c.c_uint]
    f.fixture_stat.argtypes=[c.c_uint];f.fixture_stat.restype=c.c_uint64;f.fixture_CPU.argtypes=f.fixture_RAM.argtypes=[c.c_void_p];f.fixture_live.argtypes=[c.c_void_p,c.POINTER(scheduler.CPU),c.c_uint32]
    rows=[];calls=0;slot=6;task=0xc0928+slot*1024;other=task+1024;arena=b['arena_address']+slot*256;frame=arena+168;guest=task+900;parked=frame-100;registers=[0x11110000+i for i in range(15)]
    symbols=b['resource_arena_symbols'];aux=Path(b['resource_arena_payload']).read_bytes();base=b['resource_arena_code_address'];switches=[];returns=[]
    for name in ['wait','signal','allocate','load']:
        address=symbols['biwn_acquire_arena_'+name];block=aux[address-base:address-base+112];switches.append(address+block.index(bytes.fromhex('214f00442e68003c'))+4);returns.append(symbols['biwn_acquire_arena_'+name+'_return'])
    stage=Path(b['derived_stage']).read_bytes();GPU=int.from_bytes(stage[0xe220-0x4000+2:0xe220-0x4000+6],'big')
    def observe(pc):
        nonlocal calls
        f.fixture_PC(pc);before=scheduler.CPU();after=scheduler.CPU();f.fixture_CPU(c.byref(before));left=c.create_string_buffer(0x200000);right=c.create_string_buffer(0x200000);f.fixture_RAM(left)
        f.fixture_observe(pc);f.fixture_CPU(c.byref(after));f.fixture_RAM(right)
        assert bytes(before)==bytes(after)and left.raw==right.raw,'Observer modified supplied CPU/RAM';calls+=1
    def init():
        f.fixture_reset();f.fixture_put(0xc0920,task)
        for i,value in enumerate(registers):f.fixture_reg(i,value)
        f.fixture_reg(15,guest);f.fixture_sr(0x71f);f.fixture_put(guest,0x3000)
    def start_resource():
        init();observe(0x1af04);observe(symbols['biwn_acquire_arena_entry'])
        for i,value in enumerate(registers):f.fixture_put(frame+i*4,value)
        f.fixture_put(frame+60,guest);f.fixture_word(frame+64,0);f.fixture_word(frame+66,0x71f)
    def resource_return(fault='none'):
        for i,value in enumerate(registers):f.fixture_reg(i,value)
        f.fixture_reg(15,guest);f.fixture_sr(0x71f)
        if fault=='callee':f.fixture_reg(2,0)
        if fault=='commit':f.fixture_reg(0,0)
        if fault=='SP':f.fixture_reg(15,guest+2)
        if fault=='word':f.fixture_put(guest,0)
        if fault=='SR':f.fixture_sr(0)
        observe(symbols['biwn_acquire_arena_return'])
    for fault in ['none','callee','commit','SP','word','SR','missing_return','duplicate_public','GPU_alias','resource_inside_GPU','C_low','C_other_slot']:
        start_resource()
        if fault=='duplicate_public':observe(0x1af04)
        elif fault=='GPU_alias':observe(GPU)
        elif fault=='resource_inside_GPU':f.fixture_active(slot,1);observe(0x1af04);observe(symbols['biwn_acquire_arena_entry'])
        elif fault=='C_low':f.fixture_reg(15,arena+14);observe(b['symbols']['biwn_native_resource_acquire_body'])
        elif fault=='C_other_slot':f.fixture_reg(15,arena+256+100);observe(b['symbols']['biwn_native_resource_acquire_body'])
        if fault!='missing_return':resource_return(fault)
        bad=bool(f.fixture_stat(0)or f.fixture_stat(2)or f.fixture_stat(3)or f.fixture_stat(4))
        assert bad==(fault!='none'),fault;rows.append(dict(group='resource_commit_and_owner',fault=fault,rejected=bad))
    for kind in range(4):
        for fault in ['none','other_task_GPU','parked_low','parked_high','wrong_frame','wrong_guest','wrong_low_SP','duplicate_switch','wrong_return_SP','missing_helper_return']:
            start_resource();f.fixture_reg(8,frame);f.fixture_reg(15,parked);f.fixture_put(frame+68,parked)
            if fault=='wrong_frame':f.fixture_reg(8,frame+4)
            if fault=='wrong_guest':f.fixture_put(frame+60,guest+4)
            if fault=='wrong_low_SP':f.fixture_reg(15,arena+14)
            observe(switches[kind])
            if fault=='duplicate_switch':observe(switches[kind])
            if fault in ['parked_low','parked_high']:f.fixture_put(parked if fault=='parked_low'else frame+68,0xabcdef01)
            f.fixture_put(0xc0920,other);f.fixture_reg(15,other+900)
            if fault=='other_task_GPU':f.fixture_put(arena+256+120,0xaabbccdd);observe(GPU)
            else:observe(0x6200)
            f.fixture_put(0xc0920,task);f.fixture_reg(15,guest-24-[4,4,4,20][kind]+(2 if fault=='wrong_return_SP'else 0))
            if fault!='missing_helper_return':observe(returns[kind])
            bad=bool(f.fixture_stat(0)or f.fixture_stat(2)or f.fixture_stat(4))
            assert bad==(fault not in ['none','other_task_GPU']),(kind,fault)
            rows.append(dict(group='parked_state_and_helper_return',kind=kind,fault=fault,rejected=bad))
    for route in ['native','original']:
        for fault in ['none','callee','SP','missing_route','duplicate_call','bad_entry_SP','bad_entry_word','native_stack_low','native_supervisor','missing_return']:
            init();observe(0x1a266);entry_sp=guest-4;f.fixture_reg(15,entry_sp);f.fixture_put(entry_sp,0x1a26c)
            if fault=='duplicate_call':observe(0x1a266)
            if fault=='bad_entry_SP':f.fixture_reg(15,entry_sp-2)
            if fault=='bad_entry_word':f.fixture_put(entry_sp,0x3000)
            if route=='native':observe(b['native_input_entry'])
            # Original calls skip the admission entry, so a deliberately
            # corrupted admission seam applies only to the native route.
            if fault!='missing_route':observe(b['native_input_address']+0x2828 if route=='native'else 0x191f4)
            if fault=='native_stack_low':f.fixture_reg(15,task+62);observe(b['native_input_address'])
            if fault=='native_supervisor':f.fixture_sr(0x271f);observe(b['native_input_address'])
            for i,value in enumerate(registers):f.fixture_reg(i,value)
            f.fixture_sr(0x71f);f.fixture_reg(15,guest+(2 if fault=='SP'else 0))
            if fault=='callee':f.fixture_reg(14,0)
            if fault!='missing_return':observe(0x1a26c)
            bad=bool(f.fixture_stat(7)or f.fixture_stat(8)or f.fixture_stat(9))
            wanted=fault!='none'and not(route=='original'and fault in ['bad_entry_SP','bad_entry_word','native_stack_low','native_supervisor'])
            assert bad==wanted,(route,fault,bad,wanted);rows.append(dict(group='input_route_commit',route=route,fault=fault,rejected=bad))
    # A missing resource public entry must never be accepted silently.
    init();observe(symbols['biwn_acquire_arena_entry']);assert f.fixture_stat(0)>0;rows.append(dict(group='missing_public_resource',rejected=True))
    save(out/'cases.json',rows)
    paths=[Path(__file__),bp,ROOT/'scripts/resource_input_arena_watch_v1.inc.c',ROOT/'scripts/shared_deck_input_arena_image_full_observer_v2.py',source,library,out/'compiler.log',out/'cases.json']
    proof=dict(status='terminal_exact_resource_input_observer_fault_and_readonly_fixture_controls_pass',directory=str(out),fixture=str(source),library=str(library),controls=len(rows),observer_calls_readonly_checked=calls,all_CPU_and2MB_fixture_RAM_unchanged_by_observation=True,actual_guest_execution=False,same_task_conflicts_rejected_not_repaired=True,source_sha256={str(p):sha(p)for p in paths},new_predictions=0,optimizer_updates=0,scope=__doc__)
    save(out/'protocol.json',proof);save(V/'resource-input-arena-observer-qualified-v1-current.json',proof);print(proof['status'],len(rows),calls,flush=True)


if __name__=='__main__':main()
