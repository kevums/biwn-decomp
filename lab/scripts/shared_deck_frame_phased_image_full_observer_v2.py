"""Retain exact v39 observers and add resource/input scratch lifetime checks."""
import re
from pathlib import Path
import shared_deck_frame_phased_image_full_observer_v1 as prior
ROOT=prior.ROOT


def resource_monitor(build):
    data=Path(__file__).with_name('resource_input_arena_watch_v1.inc.c').read_text()
    symbols=build['resource_arena_symbols'];payload=Path(build['resource_arena_payload']).read_bytes();base=build['resource_arena_code_address']
    switches=[];returns=[]
    for name in ['wait','signal','allocate','load']:
        at=symbols['biwn_acquire_arena_'+name];block=payload[at-base:at-base+112]
        switch=block.index(bytes.fromhex('214f00442e68003c'))+4
        switches.append(at+switch);returns.append(symbols['biwn_acquire_arena_'+name+'_return'])
    stage=Path(build['derived_stage']).read_bytes();GPU=[]
    for entry in [0xe0a6,0xe0f2,0xe148,0xe19e,0xe202,0xe220,0xe26c,0xe2b8]:
        raw=stage[entry-0x4000:entry-0x4000+6];assert raw[:2]==bytes.fromhex('4ef9');GPU.append(int.from_bytes(raw[2:],'big'))
    values=dict(R39_GPU_ENTRIES='{'+','.join(str(x)+'u'for x in GPU)+'}',R39_SWITCHES='{'+','.join(str(x)+'u'for x in switches)+'}',R39_HELPER_RETS='{'+','.join(str(x)+'u'for x in returns)+'}',R39_GPU_ARENA=str(build['arena_address'])+'u',R39_ENTRY=str(symbols['biwn_acquire_arena_entry'])+'u',R39_RETURN=str(symbols['biwn_acquire_arena_return'])+'u',I39_ADMISSION=str(build['native_input_entry'])+'u',I39_NATIVE_ENTRY=str(build['native_input_address']+0x2828)+'u',I39_CODE=str(build['native_input_address'])+'u',I39_END=str(build['native_input_address']+build['native_input_bytes'])+'u')
    for name,value in values.items():data=re.sub(r'\b'+name+r'\b',lambda _:value,data)
    return data


def observer_source(build,parent):
    text,source=prior.observer_source(build,parent)
    start=text.index('static void watch_acquire(uint32_t pc){')
    end=text.index('\n}\n\n/* Read-only live checks',start)+2
    watch=text[start:end]
    assert watch.count('!(pc>=0x162722u&&pc<0x162d64u)')==watch.count('if(pc>=0x162722u&&pc<0x162d64u)')==1
    watch=watch.replace('!(pc>=0x162722u&&pc<0x162d64u)','!phased_frame_code(pc)').replace('if(pc>=0x162722u&&pc<0x162d64u)','if(phased_frame_code(pc))')
    watch=watch.replace('0x162762u',hex(build['frame_phased_symbols']['biwn_frame_phased_return'])+'u')
    a=build['frame_phased_early_address'];z=a+build['frame_phased_early_bytes'];t=build['frame_phased_tail_address'];u=t+build['frame_phased_tail_bytes']
    predicate=f'static unsigned phased_frame_code(uint32_t pc){{return (pc>={a}u&&pc<{z}u)||(pc>={t}u&&pc<{u}u);}}\n'
    text=text[:start]+predicate+watch+text[end:]

    assert text.count('int32_t observe(uint32_t pc)')==text.count('int observer_quiescent(void)')==1
    text=text.replace('int32_t observe(uint32_t pc)','static int32_t r39_retained_observe(uint32_t pc)').replace('int observer_quiescent(void)','static int r39_retained_quiescent(void)')
    text+='\n'+resource_monitor(build)+'\nint32_t observe(uint32_t pc){r39_watch(pc);return r39_retained_observe(pc);}\nint observer_quiescent(void){return r39_retained_quiescent()&&!r39_pending_total()&&!r39_helper_total()&&!i39_pending_total();}\n'
    return text,source
