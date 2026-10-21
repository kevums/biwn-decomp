"""Overlay fixed-address phased actors on v40 without moving any layout."""
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha
from extract_biwn_stage import swap16


def main():
    bp = V / 'frame-acquire-phased-disc-build-v1-current.json'
    fp = V / 'actor-phased-fixed-v2-current.json'
    parent, proof = read(bp), read(fp)
    assert proof['source_accepted'] and proof['task_slots'] == 101
    assert proof['summaries']['initialize']['cases'] == 1024 and proof['summaries']['joint']['cases'] == 856
    for receipt in [parent, proof]:
        for p, h in receipt.get('source_sha256', receipt.get('dependencies_sha256', {})).items():
            assert sha(p) == h, p
    for key in ['derived_disc', 'derived_stage', 'component', 'copy_component']:
        assert sha(parent[key]) == parent[key + '_sha256']
    out = ROOT / 'builds/BIWN-actor-phased-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out / 'parent-build.json', parent)
    base = parent['resident_address']
    old = Path(parent['component']).read_bytes()
    resident = bytearray(old)
    changes = []
    symbols = {}
    allowed = set()
    for name in ['dispatch', 'initialize']:
        artifact = proof['artifacts'][name]
        address = artifact['code_address']
        payload = Path(artifact['binary']).read_bytes()
        at = address - base
        assert 0 <= at and at + len(payload) <= parent['copy_component_bytes']
        assert artifact['symbols']['biwn_native_actor_' + name] == parent['symbols']['biwn_native_actor_' + name]
        changes.append(dict(module=name, address=address, bytes=len(payload), original=old[at:at+len(payload)].hex(), replacement=payload.hex()))
        resident[at:at+len(payload)] = payload
        allowed.update(range(at, at+len(payload)))
        symbols[name] = artifact['symbols']
    changed = [i for i, (a, b) in enumerate(zip(old, resident)) if a != b]
    assert changed and all(i in allowed for i in changed)
    assert len(resident) == parent['component_bytes']
    # Absolute calls/jumps to superseded capture adapters must not survive
    # outside the replaced blocks. This is a byte-pattern check, not a full
    # indirect control-flow proof.
    references = []
    for key in ['biwn_native_actor_dispatch_actor_capture', 'biwn_native_actor_dispatch_sprite_capture',
                'biwn_native_actor_initialize_outside_capture', 'biwn_native_actor_initialize_inside_capture', 'biwn_native_actor_initialize_task_capture']:
        for opcode in [bytes.fromhex('4eb9'), bytes.fromhex('4ef9')]:
            needle = opcode + parent['symbols'][key].to_bytes(4, 'big')
            start = 0
            while (pos := old.find(needle, start)) >= 0:
                assert all(i in allowed for i in range(pos, pos+6)), (key, hex(base+pos))
                references.append(dict(symbol=key, address=base+pos, entirely_replaced=True))
                start = pos + 1
    component, copy, linked = out / 'resident-with-arenas.bin', out / 'resident-copy-prefix.bin', out / 'resident-code.bin'
    component.write_bytes(resident)
    copy.write_bytes(resident[:parent['copy_component_bytes']])
    linked.write_bytes(resident[:parent['linked_component_bytes']])
    old_stage = Path(parent['derived_stage']).read_bytes()
    stage = bytearray(old_stage)
    patches = []
    for change in changes:
        address = parent['staging_address'] + 40 + change['address'] - base
        at = address - 0x4000
        before, after = bytes.fromhex(change['original']), bytes.fromhex(change['replacement'])
        assert stage[at:at+len(before)] == before
        stage[at:at+len(after)] = after
        patches.append(dict(address=address, before=before.hex(), after=after.hex(), reason=change['module'] + ' phased source overlay'))
    stage_path = out / 'mainstage-actor-phased-v1.bin'
    stage_path.write_bytes(stage)
    disc = out / 'BIWN-23-actor-phased-v1-experimental.cdi'
    subprocess.run(['/bin/cp', '-c', parent['derived_disc'], str(disc)], check=True, capture_output=True)
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    offset = read(session / 'nextstage-mapping.json')['payload_raw_cdi_offset']
    with disc.open('r+b') as handle:
        for patch in patches:
            before, after = bytes.fromhex(patch['before']), bytes.fromhex(patch['after'])
            handle.seek(offset + patch['address'] - 0x4000)
            assert handle.read(len(before)) == swap16(before)
            handle.seek(offset + patch['address'] - 0x4000)
            handle.write(swap16(after))
        handle.flush()
        os.fsync(handle.fileno())
        handle.seek(offset)
        assert swap16(handle.read(len(stage))) == stage
    assert sha(parent['derived_disc']) == parent['derived_disc_sha256']
    manifest = out / 'actor-overlay-manifest.json'
    save(manifest, dict(parent_manifest=parent['patch_manifest'], parent_manifest_sha256=parent['patch_manifest_sha256'],
        resident_blocks=changes, stage_patches=patches, superseded_absolute_capture_references=references,
        public_entries_preserved=True, all_other_resident_bytes_identical=True, changed_resident_bytes=len(changed)))
    state = dict(parent)
    state.update(status='terminal_actor_phased_v41_image_built_UNQUALIFIED', profile='native-actor-phased-v41-experimental',
        directory=str(out), pid=os.getpid(), parent_build=str(out / 'parent-build.json'), parent_build_sha256=sha(out / 'parent-build.json'),
        derived_disc=str(disc), derived_disc_sha256=sha(disc), derived_stage=str(stage_path), derived_stage_sha256=sha(stage_path),
        component=str(component), component_sha256=sha(component), copy_component=str(copy), copy_component_sha256=sha(copy),
        linked_component=str(linked), linked_component_sha256=sha(linked),
        actor_phased_source=str(ROOT / 'projects/black-ice-white-noise/restoration/native-m68k/actor-phased-fixed-v2'),
        actor_phased_artifacts=proof['artifacts'], actor_phased_symbols=symbols, actor_phased_replaced_blocks=changes,
        actor_phased_transient_context_bytes=96, actor_phased_C_frames_parked_across_helpers=0, actor_phased_new_arena_bytes=0,
        patch_manifest=str(manifest), patch_manifest_sha256=sha(manifest), heap_layout_unchanged=True, staging_layout_unchanged=True,
        inherited_metadata_note='v40 layout and unchanged bytes preserved; actor internals superseded by actor_phased_symbols. Prior finite gates need explicit scope/identity binding. No gameplay qualification inherited.',
        qualification_inherited=False, final_address_gates_verified=False, startup_heap_verified=False, alias_nesting_verified=False,
        observer_qualified=False, fresh_gameplay_verified=False, gameplay_verified=False, game_frames=0,
        physical_console_verified=False, arbitrary_IRQ_qualified=False, default_promoted=False, installed_preview_changed=False,
        whole_game_complete=False, new_training=False, new_predictions=0, optimizer_updates=0, original_disc_modified=False)
    paths = [Path(__file__), bp, fp, out / 'parent-build.json', component, copy, linked, stage_path, manifest]
    paths += [Path(a[k]) for a in proof['artifacts'].values() for k in ['binary', 'ELF']]
    state['source_sha256'] = {str(p): sha(p) for p in paths}
    save(out / 'protocol.json', state)
    save(V / 'actor-phased-disc-build-v1-current.json', state)
    print(state['status'], 'changed bytes', len(changed), 'heap', state['initial_heap_bytes'], flush=True)


if __name__ == '__main__':
    main()
