"""Retain all prior read-only monitors and add input reset service commits."""
import re
from pathlib import Path
import shared_deck_record_strides_debug_observer_v1 as prior
ROOT=prior.ROOT
def reset_monitor(build):
 text=Path(__file__).with_name('scene_reset_observer_v1.inc.c').read_text();s=build['shared_Deck_symbols']
 for name,value in dict(RESET_DISPATCH=s['dispatch'],RESET_MARKER=s['biwn_v18_scene_reset_marker'],RESET_ARENA=build['deck_arena_address'],RESET_INPUT_HELPER_RETURN=s['biwn_v4_input_helper_return']).items():text=re.sub(r'\b'+name+r'\b',str(value)+'u',text)
 return text
def observer_source(build,parent):
 text,source=prior.observer_source(build,parent);assert text.count('int32_t observe(uint32_t pc)')==1 and text.count('int observer_quiescent(void)')==1
 text=text.replace('int32_t observe(uint32_t pc)','static int32_t reset_retained_observe(uint32_t pc)').replace('int observer_quiescent(void)','static int reset_retained_quiescent(void)')
 text+='\n'+reset_monitor(build)+'\nint32_t observe(uint32_t pc){reset_watch(pc);return reset_retained_observe(pc);}\nint observer_quiescent(void){return reset_retained_quiescent()&&!reset_pending_total();}\n'
 return text,source
