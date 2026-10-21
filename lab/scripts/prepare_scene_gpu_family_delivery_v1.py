"""Prepare separate v30 build/check drivers without changing frozen v29 evidence."""
from pathlib import Path
import ast

S = Path(__file__).resolve().parent

def replace(text, before, after, count=1):
    assert text.count(before) == count, (before, text.count(before))
    return text.replace(before, after)

def write(name, text):
    ast.parse(text)
    path = S / name
    assert not path.exists(), path
    path.write_text(text)

def main():
    text = (S/'check_scene17_direct_dispatch_copied_rebuild_v1.py').read_text()
    text = text.replace('Build unpromoted direct-dispatch scene module', 'Build unpromoted GPU-command-family scene module')
    text = text.replace('deck-shared-v29-scene-direct-dispatch-v1', 'deck-shared-v30-scene-gpu-commands-v1')
    text = text.replace('scene17-display-list-bridge-v6', 'scene17-gpu-family-bridge-v2')
    text = text.replace('scene17-direct-dispatch-copied-rebuild-v1', 'scene17-gpu-family-copied-rebuild-v1')
    text = replace(text, "'projects/black-ice-white-noise/restoration/experimental/scene-display-list-algorithm-v2']", "'projects/black-ice-white-noise/restoration/experimental/scene-display-list-algorithm-v2','projects/black-ice-white-noise/restoration/experimental/scene-gpu-command-family-v1']")
    text = text.replace('terminal_copied_direct_dispatch_prototype_module_byte_identical', 'terminal_copied_gpu_family_prototype_module_byte_identical')
    write('check_scene17_gpu_family_copied_rebuild_v1.py', text)

    text = (S/'build_native_scene17_direct_dispatch_disc_v1.py').read_text()
    text = replace(text, text[:text.index('import json')], '"""Separate v30 scene GPU CPU command-family experimental disc.\nSix CPU mailbox helpers plus clear, rotation and display-list builder execute\nstructured C inside the scene caller. Only170A0 remains captured in that caller.\nGlobal GPU entries and GPU programs are preserved. This is construction only:\nnew final-image, fallback/nesting, alias, observer and fresh-route proof remain\nrequired before reviewing gameplay. No Desktop preview promotion.\n"""\n')
    text = text.replace('deck-shared-v29-scene-direct-dispatch-v1', 'deck-shared-v30-scene-gpu-commands-v1')
    text = text.replace('native-deck-retained-scene17-direct-dispatch-v1', 'native-deck-retained-scene17-gpu-family-v1')
    text = text.replace('native-geometry-scene17-direct-dispatch-v1', 'native-geometry-scene17-gpu-family-v1')
    start = text.index("    bus_gate=read(")
    end = text.index("    previous=read(", start)
    text = text[:start] + '''    component_names=[('scene17-gpu-family-bridge-v2',772),('scene-gpu-command-family-native-v1',768),('scene-gpu-command-family-host-v1',768)]
    component_gates=[]
    for name,count in component_names:
        gate=read(V/(name+'-current.json'));assert gate['completed']==count and gate['status'].startswith('terminal_')
        for path,digest in gate['source_sha256'].items():assert sha(path)==digest,path
        if 'payload_sha256' in gate:assert gate['payload_sha256']==fg['payload_sha256']==tg['payload_sha256']
        component_gates.append(gate)
    copied=read(V/'scene17-gpu-family-copied-rebuild-v1-current.json');assert copied['bytes']==fg['code_bytes'] and copied['same_as_selected_prototype_module']
''' + text[end:]
    text = text.replace('scene17-direct-dispatch', 'scene17-gpu-family')
    text = text.replace("scene_authorship='Coordinator readable scene plus structured buffer rotation, clear and display-list builder; earlier local scene Author/Repair rejected; no new model output'", "scene_authorship='Coordinator readable scene and six GPU CPU mailbox helpers, buffer rotation, clear and display-list builder. Two actual local Author/Repair outputs were rejected and are not installed.'")
    text = text.replace('prototype_scene_fallback_cases=384,prototype_scene_reentry_cases=64,prototype_scene_public_bus_cases=14', 'prototype_scene_fallback_cases=0,prototype_scene_reentry_cases=0,prototype_scene_public_bus_cases=0')
    text = text.replace("'e03a','185b2']", "'e03a','185b2','e098','e0a6','e0f2','e148','e19e','e202']")
    text = replace(text, 'scene_internal_helper_entries=', "final_address_gates_verified=False,alias_nesting_verified=False,observer_qualified=False,fresh_gameplay_verified=False,scene_gpu_CPU_helpers_internal=True,remaining_original_scene_services=['170a0'],GPU_programs_recovered_by_this_change=False,scene_internal_helper_entries=")
    start=text.index('    import scene17_display_list_runtime_v1 as display\n')
    end=text.index("    result['source_sha256']",start)
    text=text[:start]+"    paths += [V/(name+'-current.json') for name,count in component_names]+[V/'scene17-gpu-family-copied-rebuild-v1-current.json']\n    paths += [p for g in component_gates for p in map(Path,g['source_sha256'])]\n"+text[end:]
    text=text.replace('terminal_scene17_display_list_candidate_built_final_address_and_gameplay_pending','terminal_scene17_gpu_family_candidate_built_all_integration_reviews_pending')
    write('build_native_scene17_gpu_family_disc_v1.py',text)

    text=(S/'check_scene17_gpu_family_bridge_v2.py').read_text()
    text=replace(text,'CODE=0x180000;ARENA=0x1b0000;',"_BUILD=read(V/'native-scene17-gpu-family-disc-build-v1-current.json');CODE=_BUILD['shared_Deck_code_address'];ARENA=_BUILD['deck_arena_address'];")
    text=text.replace("'scene17-gpu-family-bridge-v2'", "'scene17-gpu-family-final-bridge-v1'")
    text=text.replace("'scene17-gpu-family-bridge-v2-current.json'", "'scene17-gpu-family-final-bridge-v1-current.json'")
    text=replace(text,"payload=(build/'native-shared.bin').read_bytes();syms=", "payload=(build/'native-shared.bin').read_bytes();resident=Path(_BUILD['component']).read_bytes();assert payload==resident[CODE-_BUILD['resident_address']:CODE-_BUILD['resident_address']+len(payload)];syms=")
    text=replace(text,'paths=[Path(__file__),',"paths=[V/'native-scene17-gpu-family-disc-build-v1-current.json',Path(__file__),")
    write('check_scene17_gpu_family_final_bridge_v1.py',text)

if __name__=='__main__':main()
