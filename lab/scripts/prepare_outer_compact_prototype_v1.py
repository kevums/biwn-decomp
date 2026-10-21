"""Keep the persistent outer algorithm, shrinking each owned arena by192 bytes.

The prior164-byte component peak retains the prior60-byte measured margin:
224 bytes of C stack at144..368, a118-byte context at16..134, and unchanged
16-byte leading/trailing fences plus the existing8-byte context/stack fence.
No guest task stacks or Deck arenas are repurposed.
"""
import ast,shutil
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
    g=read(V/'native-Deck-outer-inplace-v1-current.json');c=read(V/'native-Deck-outer-inplace-connected-v1-current.json')
    assert g['completed']==1280 and c['completed']==128
    assert g['maximum_C_stack_bytes']==c['maximum_outer_C_stack_bytes']==164
    for proof in [g,c]:
        for p,h in proof['source_sha256'].items():assert sha(p)==h,p
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    source=nd/'deck-outer-v31-inplace-v1';target=nd/'deck-outer-v32-compact-v1'
    assert not target.exists();shutil.copytree(source,target,ignore=shutil.ignore_patterns('build','__pycache__'))
    p=target/'native-outer.S';text=p.read_text()
    for before,after in [('mulu.w #576,%d0','mulu.w #384,%d0'),('lea 544(%a0),%sp','lea 352(%a0),%sp'),('lea -544(%sp),%a0','lea -352(%sp),%a0')]:
        assert text.count(before)==1,before;text=text.replace(before,after)
    text=text.replace('compact576-byte outer frame','compact384-byte outer frame');p.write_text(text)
    for name in ['native-outer.c','native-inplace-resume.inc']:
        assert (target/name).read_bytes()==(source/name).read_bytes()
    save(target/'compact-layout.json',dict(parent_profile=str(source),parent_source_sha256={str(p):sha(p)for p in source.glob('*')if p.is_file()},
        previous_stride=576,stride=384,slots=101,context=[16,134],C_stack=[144,368],fences=[[0,16],[136,144],[368,384]],
        previous_observed_C_stack=164,C_stack_reserved=224,previous_measured_margin_retained=60,arena_bytes_reclaimed_if_integrated=19392,
        unchanged_guest_stack=True,unchanged_Deck_arena=True,disc_integrated=False,new_predictions=0,new_training=False))
    scripts=ROOT/'scripts'
    text=(scripts/'check_native_deck_outer_inplace_v1.py').read_text().replace('deck-outer-v31-inplace-v1','deck-outer-v32-compact-v1').replace('native-Deck-outer-inplace-v1','native-Deck-outer-compact-v1')
    text=text.replace('STRIDE=576','STRIDE=384').replace('(560,576)','(368,384)').replace('low=560','low=368').replace('range(144,560)','range(144,368)').replace('C_stack_bytes=560-low','C_stack_bytes=368-low')
    ast.parse(text);p=scripts/'check_native_deck_outer_compact_v1.py';assert not p.exists();p.write_text(text)
    for kind in ['fallback','waits']:
        text=(scripts/f'check_native_deck_outer_{kind}_inplace_v1.py').read_text().replace('check_native_deck_outer_inplace_v1','check_native_deck_outer_compact_v1').replace('native-Deck-outer-inplace-v1','native-Deck-outer-compact-v1').replace('native-Deck-outer-'+kind+'-inplace-v1','native-Deck-outer-'+kind+'-compact-v1')
        ast.parse(text);p=scripts/f'check_native_deck_outer_{kind}_compact_v1.py';assert not p.exists();p.write_text(text)
    print(target,flush=True)

if __name__=='__main__':main()
