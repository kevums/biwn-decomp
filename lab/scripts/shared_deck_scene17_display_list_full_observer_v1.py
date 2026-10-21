"""Retain rotation and all earlier witnesses; add internal native clear commits."""
import re
from pathlib import Path
import shared_deck_scene17_display_list_complete_observer_v1 as prior
ROOT=prior.ROOT

def clear_monitor(build):
    text=Path(__file__).with_name('scene_clear_observer_v1.inc.c').read_text();s=build['shared_Deck_symbols']
    for name,value in dict(CLEAR_BEGIN=s['biwn_v26_clear_begin'],CLEAR_END=s['biwn_v26_clear_end'],CLEAR_ARENA=build['deck_arena_address']).items():
        text=re.sub(r'\b'+name+r'\b',str(value)+'u',text)
    return text

def display_monitor(build):
    text=Path(__file__).with_name('scene_display_observer_v1.inc.c').read_text();s=build['shared_Deck_symbols']
    for name,value in dict(DISPLAY_BEGIN=s['biwn_v27_display_begin'],DISPLAY_END=s['biwn_v27_display_end'],DISPLAY_ARENA=build['deck_arena_address']).items():text=re.sub(r'\b'+name+r'\b',str(value)+'u',text)
    return text

def observer_source(build,parent):
    text,source=prior.observer_source(build,parent)
    assert text.count('int32_t observe(uint32_t pc)')==1 and text.count('int observer_quiescent(void)')==1
    text=text.replace('int32_t observe(uint32_t pc)','static int32_t c26_retained_observe(uint32_t pc)').replace('int observer_quiescent(void)','static int c26_retained_quiescent(void)')
    text+='\n'+clear_monitor(build)+'\n'+display_monitor(build)+'\nint32_t observe(uint32_t pc){d27_watch(pc);c26_watch(pc);return c26_retained_observe(pc);}\nint observer_quiescent(void){return c26_retained_quiescent()&&!c26_pending_total()&&!d27_pending_total();}\n'
    return text,source
