"""Append both original-facing collision C roots to the checked movement disc.

The existing reservation, heap floor and staging stay fixed. Startup and fresh
gameplay of this new image are separate gates. No default preview promotion.
"""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save
from extract_biwn_stage import swap16


def read(path):
    return json.loads(Path(path).read_text())


def main():
    v = ROOT / 'verification'
    parent = read(v / 'native-actor-move-disc-build-current.json')
    gate = read(v / 'native-actor-collision-final-current.json')
    contexts = read(v / 'actor-move-collision-contexts-current.json')
    review = read(v / 'actor-collision-development-reviewed-current.json')
    assert gate['status'] == 'terminal_original_ABI_actor_collision_pass' and gate['cases'] == 5120
    assert contexts['status'] == 'terminal_final_movement_context_oracle_pass' and contexts['completed'] == 5120 and contexts['max_private_depth'] == 894
    assert review['negative_controls'] == 5 and review['original_instruction_sites'] == 109
    for item in [gate, contexts, review]:
        for name, digest in item['source_sha256'].items():
            assert sha(name) == digest, name
    assert sha(parent['derived_disc']) == parent['derived_disc_sha256']
    assert sha(parent['component']) == parent['component_sha256']
    old = Path(parent['linked_component']).read_bytes()
    code = Path(gate['binary']).read_bytes()
    assert len(old) == 26220 and len(code) == 2160
    assert parent['resident_address'] + len(old) == gate['code_address'] == 0x16542c
    assert len(old) + len(code) <= parent['component_bytes'] == 28544
    out = ROOT / 'builds/BIWN-native-actor-collision' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    for name, value in [('parent-build.json', parent), ('final-component.json', gate), ('context-gate.json', contexts), ('development-review.json', review)]:
        save(out / name, value)
    linked = out / 'resident-linked.bin'
    padded = out / 'resident-padded.bin'
    linked.write_bytes(old + code)
    padded.write_bytes(old + code + bytes(parent['component_bytes'] - len(old) - len(code)))
    stage = bytearray(Path(parent['derived_stage']).read_bytes())
    before_stage = bytes(stage)
    changes = []

    def patch(address, before, after, reason):
        at = address - 0x4000
        assert len(before) == len(after) and stage[at:at + len(before)] == before
        stage[at:at + len(after)] = after
        changes.append(dict(address=hex(address), original=before.hex(), replacement=after.hex(), reason=reason))

    patch(parent['staging_address'] + 40 + len(old), bytes(len(code)), code, 'Append both collision C bodies and original-facing ABI inside the existing reservation.')
    baseline = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    entries = {}
    for address, width, name in [(0x13b5a, 8, 'outdoor'), (0x13bb0, 6, 'indoor')]:
        target = gate['symbols']['biwn_native_actor_collision_' + name]
        entries[name] = target
        patch(address, baseline[address:address + width], b'\x4e\xf9' + target.to_bytes(4, 'big') + (b'\x4e\x71' if width == 8 else b''), 'Redirect original ' + hex(address) + ' to collision C; real geometry helpers retained.')
    assert stage[0xfe000 - 0x4000:] == before_stage[0xfe000 - 0x4000:]
    stagefile = out / 'mainstage-native-actor-collision.bin'
    stagefile.write_bytes(stage)
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    offset = read(session / 'nextstage-mapping.json')['payload_raw_cdi_offset']
    disc = out / 'BIWN-23-native-actor-collision-experimental.cdi'
    subprocess.run(['/bin/cp', '-c', parent['derived_disc'], str(disc)], check=True, capture_output=True)
    with disc.open('r+b') as stream:
        for row in changes:
            at = offset + int(row['address'], 16) - 0x4000
            before = bytes.fromhex(row['original'])
            stream.seek(at)
            assert stream.read(len(before)) == swap16(before)
            stream.seek(at)
            stream.write(swap16(bytes.fromhex(row['replacement'])))
        stream.flush()
        os.fsync(stream.fileno())
        stream.seek(offset)
        assert swap16(stream.read(len(stage))) == stage
    intervals = [(offset + int(row['address'], 16) - 0x4000, offset + int(row['address'], 16) - 0x4000 + len(bytes.fromhex(row['original']))) for row in changes]
    position = changed = 0
    with Path(parent['derived_disc']).open('rb') as first, disc.open('rb') as second:
        while True:
            left, right = first.read(1048576), second.read(1048576)
            assert len(left) == len(right)
            if not left:
                break
            if left != right:
                for i, (a, b) in enumerate(zip(left, right)):
                    if a != b:
                        assert any(lo <= position + i < hi for lo, hi in intervals)
                        changed += 1
            position += len(left)
    assert sha(parent['derived_disc']) == parent['derived_disc_sha256']
    manifest = out / 'stage-patches.json'
    save(manifest, dict(patches=read(parent['patch_manifest'])['patches'] + changes, delta_patches=changes, parent=str(out / 'parent-build.json')))
    helper_returns = {}
    for label, address in [('outside_index', 0x1039c), ('outside_scan', 0x102c4), ('inside_outside', 0x1028e), ('inside_index', 0x10652)]:
        pattern = b'\x4e\xb9' + address.to_bytes(4, 'big')
        assert code.count(pattern) == 1
        helper_returns[label] = gate['code_address'] + code.index(pattern) + 6
    state = dict(parent)
    state.update(status='terminal_native_actor_collision_disc_built_pending_startup_gameplay', directory=str(out), parent_build=str(out / 'parent-build.json'), parent_build_sha256=sha(out / 'parent-build.json'), derived_disc=str(disc), derived_disc_sha256=sha(disc), derived_stage=str(stagefile), derived_stage_sha256=sha(stagefile), linked_component=str(linked), linked_component_bytes=len(old) + len(code), component=str(padded), component_sha256=sha(padded), actor_move_component_gate=parent['component_gate'], component_gate=str(out / 'final-component.json'), component_gate_sha256=sha(out / 'final-component.json'), symbols={**parent['symbols'], **gate['symbols']}, collision_start=gate['code_address'], collision_end=gate['code_address'] + len(code), collision_entries=entries, collision_returns={name: gate['symbols']['biwn_native_actor_collision_' + name + '_return'] for name in entries}, collision_helper_returns=helper_returns, collision_private_reserve=704, collision_integrated=True, semantic_code_bytes=len(code), appended_bytes=len(code), free_reserved_bytes=parent['component_bytes'] - linked.stat().st_size, parent_resident_prefix_byte_identical=True, patch_manifest=str(manifest), patch_manifest_sha256=sha(manifest), delta_CDI_changed_bytes=changed, source=str(ROOT / 'projects/black-ice-white-noise/restoration/native-m68k/actor-collision-reference.c'), game_frames=0, default_promoted=False, whole_game_complete=False, scope=__doc__)
    paths = [Path(__file__), linked, padded, stagefile, manifest, *[out / name for name in ['parent-build.json', 'final-component.json', 'context-gate.json', 'development-review.json']]]
    state['source_sha256'] = {str(p): sha(p) for p in paths}
    save(out / 'protocol.json', state)
    save(v / 'native-actor-collision-disc-build-current.json', state)
    print(json.dumps(dict(status=state['status'], resident_bytes=state['linked_component_bytes'], free_reserved_bytes=state['free_reserved_bytes'], changed_CDI_bytes=changed)))


if __name__ == '__main__':
    main()
