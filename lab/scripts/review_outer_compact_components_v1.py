"""Freeze exact compact-image component/resource evidence; do not claim fresh acceptance."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha,atomic

def main():
    counts={'native-Deck-outer-compact-v1':1280,'native-Deck-outer-fallback-compact-v1':384,'native-Deck-outer-waits-compact-v1':192,
        'native-Deck-outer-compact-connected-v1':128,'outer-compact-final-bridge-v1':772,'outer-compact-final-display-v1':1153,
        'outer-compact-final-fallback-v1':384,'outer-compact-final-reentry-v1':64,'outer-compact-final-public-bus-v1':14,
        'outer-compact-final-input-face-alias-v1':256,'native-deck-alias-nesting-outer-compact-final-v1':256,
        'native-outer-compact-geometry-alias-v1':128,'native-Deck-outer-connected-outer-compact-v1':128}
    others=['native-Deck-outer-compact-final-v1','outer-compact-geometry-observer-qualified-v1','outer-outer-compact-geometry-observer-qualified-v1',
        'shared-Deck-region-check-outer-compact-v1','outer-compact-shared-observer-qualified-v1','outer-compact-shared-observer-actual-CPU-v2',
        'outer-compact-observer-actual-CPU-v1','outer-compact-reset-observer-qualified-v1','outer-compact-commit-observer-v1',
        'outer-compact-clear-commit-observer-v1','outer-compact-outer-observer-actual-CPU-v2','outer-compact-copied-modules-v1']
    out=V/'outer-compact-components-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    gates={};deps={str(Path(__file__)):sha(__file__)}
    for name in [*counts,*others]:
        pointer=V/(name+'-current.json');g=read(pointer)
        assert g['status'].startswith('terminal_')and'failed'not in g['status'],name
        if name in counts:assert g['completed']==counts[name],name
        for p,h in g['source_sha256'].items():assert sha(p)==h,p
        for p,h in g.get('copied_source_sha256',{}).items():assert sha(p)==h,p
        deps.update(g['source_sha256']);deps[str(pointer)]=sha(pointer);save(out/(name+'.json'),g);gates[name]=g
    driver=gates['native-Deck-outer-compact-final-v1'];assert len(driver['results'])==8 and all(x['exit_code']==0 for x in driver['results'].values())
    assert gates['outer-compact-shared-observer-actual-CPU-v2']['CPU_lanes']==512
    assert gates['outer-compact-outer-observer-actual-CPU-v2']['CPU_lanes']==128
    assert gates['outer-compact-final-bridge-v1']['maximum_C_stack_bytes']==168
    bp=V/'native-outer-compact-disc-build-v1-current.json';b=read(bp);previous=read(V/'native-scene17-gpu-family-disc-build-v1-current.json')
    assert b['outer_arena_stride']==384 and b['outer_arena_bytes']==38784 and b['outer_code_bytes']==6060
    assert b['shared_Deck_code_bytes']==48738 and b['initial_heap_bytes']==139456
    assert previous['initial_heap_bytes']==120320 and previous['outer_arena_bytes']-b['outer_arena_bytes']==19392
    assert b['initial_heap_bytes']-previous['initial_heap_bytes']==19136
    assert sha(b['derived_disc'])==b['derived_disc_sha256'];deps.update(b['source_sha256']);deps[str(bp)]=sha(bp)
    for key in ['derived_disc','derived_stage','component','copy_component','patch_manifest','parent_build']:
        path=Path(b[key]);deps[str(path)]=sha(path)
    facts=dict(status='terminal_compact_outer_image_components_and_resources_reviewed_fresh_pending',directory=str(out),
        profile='scene-v30-plus-outer-v32-compact-v1',shared_profile='deck-shared-v30-scene-gpu-commands-v1',outer_profile='deck-outer-v32-compact-v1',
        authorship='Coordinator persistent outer-context specialization and layout change; canonical scene and previous game-model code are unchanged.',
        artifact_type='experimental_disc',new_disc_built=True,candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],
        shared_module_bytes=48738,outer_module_bytes=6060,linked_native_bytes=b['linked_component_bytes'],reservation_bytes=b['component_bytes'],boot_copy_bytes=b['copy_component_bytes'],
        initial_heap_bytes=139456,prior_initial_heap_bytes=120320,initial_heap_increase_bytes=19136,outer_arena_bytes_reclaimed=19392,
        outer_C_stack_bytes=164,outer_C_stack_reserved=224,outer_C_stack_margin=60,scene_C_stack_bytes=168,scene_C_stack_reserved=208,
        final_existing_gates=8,final_scene_cases=772,final_display_cases=1153,final_alias_and_nested_checks_verified=True,
        read_only_observers_qualified=True,actual_shared_observer_CPU_lanes=512,actual_outer_boundary_observer_CPU_lanes=128,
        both_copied_modules_byte_identical=True,new_unique_original_functions=0,new_model_code=False,new_predictions=0,new_training=False,optimizer_updates=0,
        fresh_gameplay_verified=False,live_heap_gain_measured=False,game_fidelity_verified=False,installed_preview_changed=False,whole_game_complete=False,
        inherited_global_GPU_redirects=True,pending_acceptance_wait_bypassed_inside_scene=True,
        scope='Arena shrink preserves224 bytes of C stack after a measured164-byte peak, retaining60 bytes of measured component margin. Only private outer slots shrink; original guest stacks and the101 existing Deck slots remain. All relocated code/startup/heap and finite alias/nesting/boundary checks pass. The actual outer monitor stays active at deliberately truncated iteration boundaries; that is explicitly checked, not quiescent-task acceptance. No arbitraryIRQ, complete scheduler, physical-console, audio or whole-game fidelity claim.')
    save(out/'facts.json',facts);facts['dependencies_sha256']=deps
    atomic(V/'outer-compact-components-reviewed-v1-current.json',facts)
    print(facts['status'],'heap+',facts['initial_heap_increase_bytes'],flush=True)

if __name__=='__main__':main()
