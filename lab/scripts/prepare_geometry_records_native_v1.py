"""Build an unpromoted shared prototype with native readable170A0.

Only its existing copy/matrix providers remain real captured helpers. All
canonical source files stay unchanged; existing scene arena bounds stay208.
"""
import shutil
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
    proof=read(V/'geometry-records-structured-host-v1-current.json');assert proof['completed']==512 and proof['host_guards']==19
    for p,h in proof['source_sha256'].items():assert sha(p)==h,p
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';prior=nd/'deck-shared-v30-scene-gpu-commands-v1';target=nd/'deck-shared-v33-geometry-records-v1'
    if target.exists():
        assert {p.name:p.read_bytes()for p in target.iterdir()if p.is_file()}=={p.name:p.read_bytes()for p in prior.iterdir()if p.is_file()},'Existing profile is not the unchanged failed copy'
    else:shutil.copytree(prior,target,ignore=shutil.ignore_patterns('build','__pycache__'))
    path=target/'native-shared.c';text=path.read_text()
    anchor='static inline void native_scene17_call('
    assert text.count(anchor)==1;text=text.replace(anchor,'static void geometry_records_body(struct biwn_deck_context *) __attribute__((noinline));\n'+anchor)
    anchor=' else status=s->service(s->opaque,s->bus,&s->cpu,target);';assert text.count(anchor)==1
    text=text.replace(anchor,' else if(target==0x170a0)geometry_records_body(s);\n'+anchor)
    anchor='\n#undef deck_call\n#undef deck_pop\n#undef deck_push\n';assert text.count(anchor)>=1
    body='''
/* Readable record builder keeps original E3E0/E220 providers and guest frames.
 * Native CLR instructions include their real68000 dummy operand reads. */
#define GEOMETRY_RECORDS_NATIVE_DIRECT 1
#define GEOMETRY_RECORDS_BEGIN(s) __asm__ volatile(".globl biwn_v33_records_begin\\nbiwn_v33_records_begin:":::"memory")
#define GEOMETRY_RECORDS_END(s) __asm__ volatile(".globl biwn_v33_records_end\\nbiwn_v33_records_end:":::"memory")
#define deck_read deeper_read
#define deck_write native_display_write
#include "../../experimental/geometry-records-structured-v1/coordinator-reference.inc"
#undef deck_write
#undef deck_read
'''
    at=text.rindex(anchor);text=text[:at]+'\n'+body+text[at:]
    anchor=' if(target==0x170a0)return biwn_v4_capture_scene_geometry(opaque,cpu,biwn_v4_scene_helper_return);';assert text.count(anchor)==1
    text=text.replace(anchor,' if(target==0xe3e0)return biwn_v4_capture_scene_record_copy(opaque,cpu,biwn_v4_scene_helper_return);\n if(target==0xe220)return biwn_v4_capture_scene_record_matrix(opaque,cpu,biwn_v4_scene_helper_return);')
    anchor='static int service_scene(';assert text.count(anchor)==1
    text=text.replace(anchor,'extern int biwn_v4_capture_scene_record_copy(struct frame *,struct biwn_task_cpu *,return_fn);\nextern int biwn_v4_capture_scene_record_matrix(struct frame *,struct biwn_task_cpu *,return_fn);\n'+anchor)
    path.write_text(text)
    path=target/'native-shared.S';text=path.read_text();assert text.count('capture scene_geometry,0x170a0')==1
    path.write_text(text.replace('capture scene_geometry,0x170a0','capture scene_record_copy,0xe3e0\ncapture scene_record_matrix,0xe220'))
    save(target/'geometry-records-derivation.json',dict(parent_profile=str(prior),canonical_readable_source=str(ROOT/'projects/black-ice-white-noise/restoration/experimental/geometry-records-structured-v1/coordinator-reference.inc'),canonical_host_proof=str(V/'geometry-records-structured-host-v1-current.json'),
        entry='0x170a0',captured_providers=['0xe3e0','0xe220'],original_global_170A0_unchanged=True,scene_arena_bytes=208,arena_changed=False,new_predictions=0,new_training=False,disc_integrated=False,authorship='Coordinator readable record builder and target adaptation; no new unique original function.'))
    print(target,flush=True)

if __name__=='__main__':main()
