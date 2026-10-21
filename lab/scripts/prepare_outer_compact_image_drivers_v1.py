"""Construct isolated compact-arena build and exact-address verifier drivers."""
import ast
from pathlib import Path
S=Path(__file__).resolve().parent

def put(name,text):
    ast.parse(text);p=S/name;assert not p.exists(),p;p.write_text(text)

def main():
    text=(S/'build_native_scene17_gpu_family_disc_v1.py').read_text()
    text=text.replace('import check_native_deck_outer_v1 as outer','import check_native_deck_outer_compact_v1 as outer')
    text=text.replace("V/'native-Deck-outer-v1-current.json'","V/'native-Deck-outer-compact-v1-current.json'")
    text=text.replace("V/'native-Deck-outer-connected-v1-current.json'","V/'native-Deck-outer-compact-connected-v1-current.json'")
    text=text.replace("V/'native-Deck-outer-fallback-v1-current.json'","V/'native-Deck-outer-fallback-compact-v1-current.json'")
    text=text.replace("V/'native-Deck-outer-waits-v1-current.json'","V/'native-Deck-outer-waits-compact-v1-current.json'")
    # The shared v30 CPU module is unchanged. Only outer code and arena layout
    # advance, so do not rename its immutable preflight dependencies.
    for before,after in [('BIWN-native-scene17-gpu-family-v1','BIWN-native-outer-compact-v1'),('mainstage-native-scene17-gpu-family-v1','mainstage-native-outer-compact-v1'),('BIWN-23-native-scene17-gpu-family-v1','BIWN-23-native-outer-compact-v1'),('native-scene17-gpu-family-disc-build-v1-current.json','native-outer-compact-disc-build-v1-current.json')]:
        text=text.replace(before,after)
    text=text.replace('outer_bytes=101*576','outer_bytes=101*384').replace('lea 576(%a1)','lea 384(%a1)').replace('lea 576(%a0)','lea 384(%a0)').replace('outer_arena+slot*576','outer_arena+slot*384').replace('slot*576','slot*384').replace('outer_arena_stride=576','outer_arena_stride=384')
    text=text.replace('terminal_scene17_gpu_family_candidate_built_all_integration_reviews_pending','terminal_compact_outer_candidate_built_all_integration_reviews_pending')
    text=text.replace('scene_gpu_CPU_helpers_internal=True,','outer_persistent_context=True,outer_C_stack_reserved=224,outer_C_stack_prototype_peak=164,outer_arena_bytes_reclaimed=19392,scene_gpu_CPU_helpers_internal=True,')
    text=text.replace('new final-image, fallback/nesting, alias, observer and fresh-route proof remain','New384-byte persistent outer slots require final-image, fallback/nesting, alias, observer and fresh-route proof. Existing global GPU redirects are inherited and the scene wait retains v30 behavior; all remain explicit. New proof requirements remain')
    put('build_native_outer_compact_disc_v1.py',text)

    text=(S/'check_native_scene17_gpu_family_final_v1.py').read_text().replace('scene17-gpu-family','outer-compact')
    text=text.replace("b['outer_arena_bytes']==58176","b['outer_arena_bytes']==38784")
    text=text.replace("'scripts/check_native_deck_outer_v1.py'","'scripts/check_native_deck_outer_compact_v1.py'")
    # The compact standalone driver has its own family name; remap its pointer
    # for dependent exact-address fallback/wait checkers.
    text=text.replace(".replace('native-Deck-outer-v1','native-Deck-outer-outer-compact-final-v1')", ".replace('native-Deck-outer-compact-v1','native-Deck-outer-outer-compact-final-v1')")
    text=text.replace("'import check_native_deck_outer_v1 as outer','import native_outer_final_checker as outer'", "'import check_native_deck_outer_compact_v1 as outer','import native_outer_final_checker as outer'")
    text=text.replace("f'scripts/check_native_deck_outer_{kind}_v1.py'", "f'scripts/check_native_deck_outer_{kind}_compact_v1.py'")
    text=text.replace("'native-Deck-outer-v1-current.json','native-Deck-outer-outer-compact-final-v1-current.json'", "'native-Deck-outer-compact-v1-current.json','native-Deck-outer-outer-compact-final-v1-current.json'")
    text=text.replace("'native-Deck-outer-'+kind+'-v1','native-Deck-outer-'+kind+'-outer-compact-final-v1'", "'native-Deck-outer-'+kind+'-compact-v1','native-Deck-outer-'+kind+'-outer-compact-final-v1'")
    put('check_native_outer_compact_final_v1.py',text)

    for name in ['check_scene17_gpu_family_final_bridge_v1.py','check_scene17_gpu_family_final_fallback_v1.py','check_scene17_gpu_family_final_reentry_v1.py','check_scene17_gpu_family_final_public_bus_v1.py','check_scene17_gpu_family_final_input_face_alias_v1.py','check_scene_gpu_family_final_native_v1.py','check_native_deck_alias_nesting_scene17_gpu_family_v1.py','check_native_scene17_gpu_family_geometry_alias_v1.py']:
        text=(S/name).read_text().replace('scene17_gpu_family','outer_compact').replace('scene17-gpu-family','outer-compact').replace('scene_gpu_family_final_native','outer_compact_final_display').replace('scene-gpu-family-final-native','outer-compact-final-display')
        # Runtime and canonical v30 body paths remain the same.
        text=text.replace('scene-outer-compact','scene-gpu-family')
        dest=name.replace('scene17_gpu_family','outer_compact').replace('scene_gpu_family_final_native','outer_compact_final_display')
        put(dest,text)

if __name__=='__main__':main()
