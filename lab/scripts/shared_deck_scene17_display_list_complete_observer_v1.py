"""Preserve all qualified watchers and add read-only native rotation commitments."""
import re
from pathlib import Path
import shared_deck_scene17_display_list_reset_observer_v1 as prior
ROOT=prior.ROOT

def rotation_monitor(build):
    text=Path(__file__).with_name('scene_rotation_display_observer_v2.inc.c').read_text()
    symbols=build['shared_Deck_symbols']
    values=dict(ROTATION_BEGIN=symbols['biwn_v25_rotation_begin'],ROTATION_END=symbols['biwn_v25_rotation_end'],
                ROTATION_DISPLAY_BEGIN=symbols['biwn_v27_display_begin'],ROTATION_DISPLAY_END=symbols['biwn_v27_display_end'],ROTATION_ARENA=build['deck_arena_address'])
    for name,value in values.items():
        text=re.sub(r'\b'+name+r'\b',str(value)+'u',text)
    return text

def observer_source(build,parent):
    text,source=prior.observer_source(build,parent)
    assert text.count('int32_t observe(uint32_t pc)')==1 and text.count('int observer_quiescent(void)')==1
    text=text.replace('int32_t observe(uint32_t pc)','static int32_t r25_retained_observe(uint32_t pc)').replace('int observer_quiescent(void)','static int r25_retained_quiescent(void)')
    text+='\n'+rotation_monitor(build)+'\nint32_t observe(uint32_t pc){r25_watch(pc);return r25_retained_observe(pc);}\nint observer_quiescent(void){return r25_retained_quiescent()&&!r25_pending_total();}\n'
    return text,source
