"""Add input-handoff logging while preserving all qualified five-helper monitors."""
from pathlib import Path
import re
import shared_deck_faces_observer_v1 as prior
ROOT=prior.ROOT
def observer_source(build,parent):
    text,source=prior.observer_source(build,parent)
    assert text.count('void set_frame(uint32_t value)')==1
    assert text.count('int32_t observe(uint32_t pc)')==1
    text=text.replace('void set_frame(uint32_t value)','static void handoff_retained_set_frame(uint32_t value)',1)
    text=text.replace('int32_t observe(uint32_t pc)','static int32_t handoff_retained_observe(uint32_t pc)',1)
    extra=Path(__file__).with_name('faces_handoff_trace_v1.inc.c').read_text()
    constants=dict(HANDOFF_DIGIT_NATIVE=build['symbols']['biwn_native_button_digit'],HANDOFF_DIGIT_BODY=build['symbols']['biwn_native_button_digit_compact'],HANDOFF_OUTER_RETURN=build['outer_symbols']['biwn_outer_return'])
    for key,value in constants.items():extra=re.sub(r'\b'+key+r'\b',str(value)+'u',extra)
    return text+'\n'+extra,source
