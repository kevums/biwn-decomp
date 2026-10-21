"""Prototype direct use of the existing persistent outer CPU context.

No arena shrinking or game installation here. Host recovery retains its copied
CPU/error behavior; the native entry uses a persistent, private logical frame.
It still commits original guest CPU only at the assembly semantic boundaries.
"""
import shutil
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,save,sha

def main():
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    original=nd/'deck-outer-v1';target=nd/'deck-outer-v31-inplace-v1'
    assert not target.exists();shutil.copytree(original,target,ignore=shutil.ignore_patterns('build','__pycache__'))
    canonical=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-task-source/deck-task-source.c'
    text=canonical.read_text();start=text.index(' /* Continuations correspond');end=text.index('\nint biwn_deck_task_call(',start)
    body=text[start:end]
    assert body.count('switch(cpu->pc)')==1 and body.count('if(!s.error||s.error==6)*cpu=s.cpu;')==1
    body=body.replace('switch(cpu->pc)','switch(s.cpu.pc)').replace(' if(!s.error||s.error==6)*cpu=s.cpu;\n','')
    body=body.replace('&s','s').replace('s.','s->')
    body='''/* Canonical algorithm specialized to its already-owned persistent frame.
 * Intermediate logical shadow writes differ from the host copy-and-commit
 * implementation. Guest CPU commits and physical guest stack behavior remain
 * at the same assembly boundaries; no arbitrary IRQ/shadow equivalence claim.
 */
#undef CALL
#undef BUS_OK
#define CALL(target,ret) do{invoke(s,(target),(ret));if(s->error)goto finish;}while(0)
#define BUS_OK() do{if(s->error)goto finish;}while(0)
static int native_outer_resume(struct biwn_deck_context *s,uint32_t poll_budget){
 uint32_t *r=s->cpu.registers,v,mode;
'''+body+'\n#undef CALL\n#undef BUS_OK\n'
    (target/'native-inplace-resume.inc').write_text(body)
    p=target/'native-outer.c';text=p.read_text()
    old='''void biwn_outer_body(struct frame *f){
 f->context.error=biwn_deck_task_resume(&memory,&f->context.cpu,service,f,64,64);
}'''
    assert text.count(old)==1
    text=text.replace(old,'''#include "native-inplace-resume.inc"
void biwn_outer_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service;f->context.opaque=f;
 f->context.budget=64;f->context.error=0;
 f->context.error=native_outer_resume(&f->context,64);
}''')
    p.write_text(text)
    save(target/'derivation.json',dict(canonical=str(canonical),canonical_sha256=sha(canonical),
        parent_profile=str(original),change='Use existing persistent private logical CPU instead of a second local context; retain original guest commit/capture assembly.',
        arena_changed=False,disc_changed=False,new_predictions=0,new_training=False,
        arbitrary_IRQ_or_intermediate_shadow_equivalence=False))
    script=ROOT/'scripts/check_native_deck_outer_v1.py';test=script.read_text().replace("native-m68k/deck-outer-v1'","native-m68k/deck-outer-v31-inplace-v1'").replace('native-Deck-outer-v1','native-Deck-outer-inplace-v1')
    dest=ROOT/'scripts/check_native_deck_outer_inplace_v1.py';assert not dest.exists();dest.write_text(test)
    print(target,flush=True)

if __name__=='__main__':main()
