"""Bind unchanged v40 module proofs and changed v41 actor proofs before fresh play.

Unchanged finite module/provider proofs retain their original controlled-helper
scope. They are not new v41 executions or proof of complete asynchronous chains.
The changed actor phases, task-layout guards, startup and observers run anew.
"""
from datetime import datetime, timezone
from pathlib import Path
import shared_deck_actor_phased_image_full_observer_v2 as monitor
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def without_actor_functions(text):
    for name in ['dispatch', 'initialize']:
        start = text.index('static void watch_actor_' + name + '(uint32_t pc){')
        end = text.index('\n}', start) + 2
        text = text[:start] + '/* actor watcher separately qualified */' + text[end:]
    return text


def main():
    bp = V / 'actor-phased-disc-build-v1-current.json'
    oldp = V / 'frame-phased-image-fresh-preflight-v1-current.json'
    b, old = read(bp), read(oldp)
    assert old['status'] == 'terminal_v40_exact_component_alias_and_readonly_observers_qualified_for_fresh'
    assert sha(old['build']) == old['build_sha256']
    deps = {str(p): sha(p) for p in [Path(__file__), Path(monitor.__file__), bp, oldp]}
    for p, h in old['source_sha256'].items():
        assert sha(p) == h, p
        deps[p] = h
    ancestor = read(b['parent_build'])
    assert sha(b['parent_build']) == b['parent_build_sha256']
    for field in ['resident_address', 'component_bytes', 'copy_component_bytes', 'linked_component_bytes', 'heap_start',
                  'initial_heap_bytes', 'staging_address', 'staging_bytes_cleared', 'shared_Deck_code_address', 'shared_Deck_code_bytes',
                  'outer_code_address', 'outer_code_bytes', 'native_input_address', 'native_input_entry', 'native_input_bytes',
                  'resource_arena_code_address', 'resource_arena_code_bytes', 'frame_phased_early_address', 'frame_phased_early_bytes',
                  'frame_phased_tail_address', 'frame_phased_tail_bytes', 'deck_arena_address', 'outer_arena_address', 'arena_address', 'arena_end']:
        assert b[field] == ancestor[field], field
    before, after = Path(ancestor['component']).read_bytes(), Path(b['component']).read_bytes()
    allowed = set()
    for block in b['actor_phased_replaced_blocks']:
        at = block['address'] - b['resident_address']
        allowed.update(range(at, at + block['bytes']))
    assert len(before) == len(after) and all(a == z or i in allowed for i, (a, z) in enumerate(zip(before, after)))
    gates = {}
    names = ['actor-phased-v1', 'actor-phased-fixed-v2', 'actor-phased-leaf-stack-v2',
             'actor-phased-image-startup-heap-v1', 'actor-phased-copied-rebuild-v1', 'actor-phased-watch-v1']
    for name in names:
        p = V / (name + '-current.json')
        g = read(p)
        assert g['status'].startswith('terminal_') and 'failed' not in g['status'] and 'preflight' not in g['status'], (name, g['status'])
        for source, h in g.get('source_sha256', g.get('dependencies_sha256', {})).items():
            assert sha(source) == h, source
            deps[source] = h
        deps[str(p)] = sha(p)
        gates[name] = g
    fixed = gates['actor-phased-fixed-v2']
    assert fixed['source_accepted'] and fixed['task_slots'] == 101 and fixed['protected_task_bytes'] == 64
    assert fixed['summaries']['initialize']['cases'] == 1024 and fixed['summaries']['joint']['cases'] == 856
    assert fixed['summaries']['initialize']['task_layout_pairs'] == fixed['summaries']['joint']['task_layout_pairs'] == 116
    assert gates['actor-phased-leaf-stack-v2']['maximum_wrapper_C_phase_depth'] == dict(dispatch=136, initialize=156)
    startup = gates['actor-phased-image-startup-heap-v1']
    assert startup['native_startup_cases'] == startup['Unicorn_startup_cases'] == 6 and startup['heap_initialize_cases'] == 192
    assert gates['actor-phased-copied-rebuild-v1']['new_builds'] == 2
    watch = gates['actor-phased-watch-v1']
    assert watch['actual_off_on_pairs'] == 48 and watch['fault_controls'] == 7 and watch['complete_off_on_CPU_RAM_helpers_equal_without_exclusions']
    out = V / 'actor-phased-fresh-preflight-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    text, _ = monitor.observer_source(b, read(V / 'native-Deck-coordinate-disc-build-current.json'))
    qualified = Path(watch['directory']) / 'observer.c'
    assert qualified.read_text() == text
    assert without_actor_functions(text) == without_actor_functions(Path(old['observer']).read_text())
    observer = out / 'observer.c'
    observer.write_text(text)
    deps[str(observer)] = sha(observer)
    deps.update({str(p): sha(p) for p in [Path(b['component']), Path(b['derived_stage']), Path(b['derived_disc']), Path(b['parent_build'])]})
    proof = dict(status='terminal_v41_unchanged_module_identity_and_new_actor_startup_readonly_checks_bound_for_fresh',
        directory=str(out), build=str(bp), build_sha256=sha(bp), observer=str(observer), observer_sha256=sha(observer),
        gate_names=old['gate_names'] + names, reused_v40_gate_names=old['gate_names'], new_gate_names=names,
        new_actor_initializer_pairs=1024, new_actor_joint_pairs=856, new_actor_task_layout_pairs=232,
        new_actor_off_on_pairs=48, actor_fault_controls=7, unchanged_v40_gate_executions_repeated=0,
        unchanged_modules_and_observer_text_outside_actor_watchers_byte_identical=True,
        new_actor_functions_at_original_public_addresses=True, additional_private_arena_bytes=0,
        new_predictions=0, new_training=False, whole_game_complete=False, fresh_gameplay_verified=False,
        actual_full_prefix_actor_helper_chain_qualified=False, arbitrary_IRQ_qualified=False,
        source_sha256=deps, scope=__doc__)
    save(out / 'review.json', proof)
    save(V / 'actor-phased-fresh-preflight-v1-current.json', proof)
    print(proof['status'], len(proof['gate_names']), flush=True)


if __name__ == '__main__':
    main()
