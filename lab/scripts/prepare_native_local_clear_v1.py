"""Integrate the unedited local typed Repair into a separate native prototype.
The target specialization reuses the existing successful direct bus and native
flag primitives. No installed disc,preview,model weights or original source changes.
"""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 parent=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v10';target=parent.with_name('deck-shared-v11-local-clear');assert not target.exists();local=read(V/'local-typed-clear-target-v2-current.json');assert local['completed']==260 and local['ordered_cases']==260 and local['budget_cases']==35 and not local['raw_function_hand_edited']
 for p,h in local['source_sha256'].items():assert sha(p)==h,p
 shutil.copytree(parent,target);source=target/'native-shared.c';text=source.read_text();anchor='#include "native-clear-stages.inc"';assert text.count(anchor)==1
 extra='''
/* Unedited local Repair body. Only its private C symbol is renamed;the target
 * bus and flag profile is supplied by the coordinator,as for other native bodies. */
#include "../../experimental/typed-deck-primitives-v1/typed-registers.h"
static void local_typed_clear_records(struct biwn_deck_context *,biwn_deck_write8,uint32_t) __attribute__((noinline,used));
#define clear_records local_typed_clear_records
#include "../../experimental/deck-clear-local-typed-v3/clear-records.c"
#undef clear_records
'''
 text=text.replace(anchor,anchor+extra);old='if(target==0x10968)native_clear_records(&f->context,65536);';new='if(target==0x10968)local_typed_clear_records(&f->context,0,65536);';assert text.count(old)==1;text=text.replace(old,new);source.write_text(text)
 script=ROOT/'scripts/check_native_deck_debug_real_v1.py';code=script.read_text().replace('deck-shared-v10','deck-shared-v11-local-clear').replace("family='native-Deck-debug-real-v1'if args.real_dependencies else'native-Deck-debug-v1'", "family='native-Deck-local-clear-real-v1'if args.real_dependencies else'native-Deck-local-clear-fixture-v1'")
 code=code.replace("SRC/'Makefile',SRC/'native-alu.h'", "SRC/'Makefile',SRC/'native-alu.h',SRC.parent.parent/'experimental/typed-deck-primitives-v1/typed-registers.h',SRC.parent.parent/'experimental/deck-clear-local-typed-v3/clear-records.c'")
 checker=ROOT/'scripts/check_native_deck_local_clear_v1.py';checker.write_text(code)
 out=V/'native-local-clear-integration-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);raw=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-clear-local-typed-v3/clear-records.c'
 paths=[Path(__file__),source,checker,raw,raw.parent.parent/'typed-deck-primitives-v1/typed-registers.h',V/'local-typed-clear-target-v2-current.json'];state=dict(status='terminal_local_raw_function_native_prototype_prepared_unqualified',directory=str(out),prototype=str(target),local_raw_function=str(raw),raw_function_sha256=sha(raw),raw_body_hand_edited=False,symbol_only_preprocessor_rename=True,target_bus_and_flag_profile_coordinator_supplied=True,native_disc_changed=False,installed_preview_changed=False,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__);save(out/'review.json',state);save(V/'native-local-clear-integration-v1-current.json',state);print(target)
if __name__=='__main__':main()
