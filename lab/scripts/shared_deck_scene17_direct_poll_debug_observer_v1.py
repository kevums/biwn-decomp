"""Retain all six-caller monitors and observe actual six compiled C services.

The original geometry control executes its six real helpers. The candidate's
six compiled helper returns are service C returns, before logical RTS pop.
"""
import re
from pathlib import Path
import shared_deck_scene17_direct_poll_deeper_observer_v1 as prior
ROOT=prior.ROOT
def observer_source(build,parent):
    text,source=prior.observer_source(build,parent)
    syms=build['shared_Deck_symbols'];outer=build['outer_symbols']
    old='{69844u,70702u,67380u,0u,0u,0u,0u,0u,0u}'
    # shared_watch counts only physical capture calls; internal helpers have
    # separate logical-context/service-return witnesses below.
    assert text.count(old)==1
    text=text.replace(old,'{57964u,0u,0u,0u,0u,0u,0u,0u,0u}')
    start=text.index('static unsigned g4_pending[101]');end=text.index('static const uint32_t o6_inner_returns',start)
    monitor=Path(__file__).with_name('debug_geometry_observer_v1.inc.c').read_text()
    constants=dict(G6_DEBUG_SERVICE=syms['service_geometry_debug'],G6_DEBUG_HELPERS=syms['service_geometry_debug_helpers'],G5_FACES_SERVICE=syms['service_geometry_faces'],G4_PLANE_SERVICE=syms['service_geometry_original'],G4_NATIVE_ENTRY=syms['biwn_v4_geometry'],G4_NATIVE_RETURN=syms['biwn_v4_geometry_return'],G4_HELPER_RETURN=syms['biwn_v4_geometry_helper_return'],G4_SERVICE=syms['service_geometry'],G4_MARKER=syms['biwn_v5_deeper_helper_marker'],G4_DECK=build['deck_arena_address'],G4_CODE=build['shared_Deck_code_address'],G4_END=build['shared_Deck_code_address']+build['shared_Deck_code_bytes'],G4_OUTER_RETURN=outer['biwn_outer_helper_return'],G4_OUTER_ARENA=build['outer_arena_address'])
    for name,value in constants.items():monitor=re.sub(r'\b'+name+r'\b',str(value)+'u',monitor)
    text=text[:start]+monitor+'\n'+text[end:]
    return text,source
