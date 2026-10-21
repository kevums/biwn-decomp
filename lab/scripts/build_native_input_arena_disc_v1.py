"""Build a separate v34-derived v39 input/resource-arena experimental CDI.

v6input uses provisional768admission; a676-byte task-arena resource adapter
is linked at the real resident origin with five checked old-entry jumps.
No game, image-address, same-task reentry or arbitraryIRQ qualification is
inherited from the source prototypes. Reviewed/failed/preview images remain.
"""
import importlib.util
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha
from extract_biwn_stage import swap16
from wide_bootstrap_support_v1 import plan_input_layout, stage_clear_lines


def symbols(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) == 3:
            result[parts[2]] = int(parts[0], 16)
    return result


def main():
    bp = V / 'native-record-strides-disc-build-v1-current.json'
    rp = V / 'native-input-rebase-v1-current.json'
    wp = V / 'local-wide-bootstrap-reviewed-v1-current.json'
    sp = V / 'native-input-real-stream-caller-v2-current.json'
    cp = V / 'native-input-real-stream-second-CPU-v1-current.json'
    parent, rebase, wide, stream, second = map(read, [bp, rp, wp, sp, cp])
    for receipt in [parent, rebase, wide, stream, second]:
        assert receipt['status'].startswith('terminal_') and 'failed' not in receipt['status']
        for path, digest in receipt.get('source_sha256', {}).items():
            assert sha(path) == digest, path
    for key in ['derived_disc', 'derived_stage', 'component', 'copy_component']:
        assert sha(parent[key]) == parent[key + '_sha256'], key
    assert rebase['runtime_source_statements_changed'] == 0
    assert rebase['copied_build_byte_identical'] and rebase['changed_byte_count'] == 144
    assert stream['completed'] == second['completed'] == 27
    assert stream['actual_loaded_payload_checks'] == second['actual_loaded_payload_checks'] == 6
    assert stream['native_max_caller_stack'] == second['native_max_caller_stack'] == 458
    v6_path=V/'native-input-arena-admission-v6-current.json';v6=read(v6_path)
    arena_path=V/'acquire-arena-prototype-v1-current.json';arena=read(arena_path)
    wait_path=V/'acquire-arena-real-wait-tasks-v2-current.json';wait=read(wait_path)
    irq_path=V/'acquire-arena-real-wait-GPU-irq-v1-current.json';irq=read(irq_path)
    primary_path=V/'native-input-acquire-arena-caller-v2-current.json';primary=read(primary_path)
    secondary_path=V/'native-input-acquire-arena-second-CPU-v1-current.json';secondary=read(secondary_path)
    entry_path=V/'native-input-arena-admission-entry-v1-current.json';entry=read(entry_path)
    identity_path=V/'acquire-arena-identity-v1-current.json';identity=read(identity_path)
    extra_paths=[v6_path,arena_path,wait_path,irq_path,primary_path,secondary_path,entry_path,identity_path]
    extras=[v6,arena,wait,irq,primary,secondary,entry,identity]
    for receipt in extras:
        assert receipt['status'].startswith('terminal_') and 'failed'not in receipt['status']
        for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    assert wait['completed']==32 and wait['actual_switches']==208 and wait['actual_GPU_submissions']==104
    assert irq['completed']==irq['actual_GPU_IRQ_returns']==16 and not irq['arbitrary_IRQ_qualified']
    assert primary['completed']==secondary['completed']==27 and entry['completed']==20188 and identity['completed']==432
    assert v6['changed_bytes']==1 and v6['native_reserve']==768 and v6['copied_build_byte_identical']
    code=Path(v6['payload']).read_bytes();old_input=Path(rebase['payload']).read_bytes()
    assert [i for i,(a,b)in enumerate(zip(old_input,code))if a!=b]==v6['changed_byte_offsets']
    plan = plan_input_layout(parent, len(code)+arena['code_bytes'])
    assert plan['input_address'] == rebase['new_base']
    assert plan['input_address'] + len(code) == rebase['code_end']
    resource_address=plan['input_address']+len(code)
    out = ROOT / 'builds/BIWN-native-input-arena-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out, flush=True)
    resource_source=Path(arena['source_profile'])
    tool_prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    resource_build=out/'resource-build';resource_build.mkdir()
    commands=[[tool_prefix+'as','-m68000','-o',str(resource_build/'native.o'),str(resource_source/'native-acquire.S')],
        [tool_prefix+'ld','--defsym=NATIVE_ADDRESS='+hex(resource_address),'--defsym=GPU_ARENA_BASE='+hex(parent['arena_address']),'--defsym=ACQUIRE_BODY='+hex(parent['symbols']['biwn_native_resource_acquire_body']),'-T',str(resource_source/'native.ld'),'-o',str(resource_build/'native.elf'),str(resource_build/'native.o')],
        [tool_prefix+'objcopy','-O','binary',str(resource_build/'native.elf'),str(resource_build/'native.bin')]]
    for command in commands:subprocess.run(command,check=True,capture_output=True)
    named=subprocess.check_output([tool_prefix+'nm','-n',str(resource_build/'native.elf')],text=True)
    (resource_build/'symbols.txt').write_text(named);resource_symbols=symbols(resource_build/'symbols.txt')
    resource_code=(resource_build/'native.bin').read_bytes()
    assert len(resource_code)==676 and resource_symbols['biwn_acquire_arena_entry']==resource_address
    assert resource_code==Path(arena['payload']).read_bytes(),'All resource code is position-independent internally or uses fixed external addresses; unexpected bytes changed'
    for name,old_value in arena['symbols'].items():
        if arena['code_address']<=old_value<arena['code_address']+len(resource_code):assert resource_symbols[name]==old_value+resource_address-arena['code_address'],name
    save(out/'resource-link-commands.json',commands)
    save(out / 'parent-build.json', parent)
    save(out / 'input-layout-plan.json', plan)
    base = parent['resident_address']
    deck, outer, heap = (plan[k] for k in ['deck_arena_address', 'outer_arena_address', 'heap_start'])
    native_root = ROOT / 'projects/black-ice-white-noise/restoration/native-m68k'
    shared_src = native_root / 'deck-shared-v34-record-strides-v1'
    outer_src = native_root / 'deck-outer-v32-compact-v1'
    jobs = [
        (shared_src, out / 'shared-build', ['ADDRESS=' + hex(parent['shared_Deck_code_address']), 'ARENA_ADDRESS=' + hex(deck)], 'native-shared'),
        (outer_src, out / 'outer-build', ['ADDRESS=' + hex(parent['outer_code_address']), 'ARENA_ADDRESS=' + hex(outer), 'DECK_ADDRESS=' + hex(deck)], 'native-outer'),
    ]
    for src, build, args, name in jobs:
        proc = subprocess.run(['make', 'BUILD=' + str(build), *args], cwd=src, capture_output=True, text=True)
        (out / (name + '-compiler.log')).write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0, proc.stderr
    shared = (out / 'shared-build/native-shared.bin').read_bytes()
    outer_code = (out / 'outer-build/native-outer.bin').read_bytes()
    fs, osym = symbols(out / 'shared-build/symbols.txt'), symbols(out / 'outer-build/symbols.txt')
    assert len(shared) == parent['shared_Deck_code_bytes']
    assert len(outer_code) == parent['outer_code_bytes']
    assert fs['biwn_v4_coordinate'] == parent['shared_Deck_code_address']
    assert osym['biwn_outer_entry'] == parent['outer_code_address']
    assert fs['DECK_ARENA_BASE'] == osym['DECK_ARENA_BASE'] == deck
    assert osym['OUTER_ARENA_BASE'] == outer
    old_resident = Path(parent['component']).read_bytes()
    prefix = bytearray(old_resident[:parent['shared_Deck_code_address'] - base])
    relocations, allowed = [], set()
    assert len(parent['layout_relocations']) == 7
    for row in parent['layout_relocations']:
        offset = row['address'] - base
        delta = row['new'] - parent['heap_start']
        assert delta in [0, 4, 8] and 0 <= offset <= len(prefix) - 4
        assert int.from_bytes(prefix[offset:offset+4], 'big') == row['new']
        prefix[offset:offset+4] = (heap + delta).to_bytes(4, 'big')
        allowed.update(range(offset, offset+4))
        relocations.append(dict(address=row['address'], old=row['new'], new=heap + delta))
    resource_patches=[]
    for old_name,new_name in [('biwn_native_resource_acquire','biwn_acquire_arena_entry'),('biwn_native_acquire_wait_capture','biwn_acquire_arena_wait'),('biwn_native_acquire_signal_capture','biwn_acquire_arena_signal'),('biwn_native_acquire_allocate_capture','biwn_acquire_arena_allocate'),('biwn_native_acquire_load_capture','biwn_acquire_arena_load')]:
        old_address=parent['symbols'][old_name];offset=old_address-base
        proof_row=next(row for row in arena['stub_patches']if row['entry']==old_address)
        assert prefix[offset:offset+6]==bytes.fromhex(proof_row['old'])
        replacement=bytes.fromhex('4ef9')+resource_symbols[new_name].to_bytes(4,'big')
        prefix[offset:offset+6]=replacement;allowed.update(range(offset,offset+6))
        resource_patches.append(dict(entry=old_address,target=resource_symbols[new_name],original=proof_row['old'],replacement=replacement.hex()))
    at = parent['symbols']['biwn_native_startup_finalize'] - base
    assert prefix[at:at+6] == bytes.fromhex('4ef9') + parent['deck_finalizer_address'].to_bytes(4, 'big')
    prefix[at:at+6] = bytes.fromhex('4ef9') + plan['finalizer_address'].to_bytes(4, 'big')
    allowed.update(range(at, at+6))
    assert all(i in allowed for i, (left, right) in enumerate(zip(old_resident, prefix)) if left != right)
    lines = ['.text', '.globl biwn_native_input_finalize', 'biwn_native_input_finalize:']
    for label, address, count in [('deck_clear', deck, parent['deck_arena_bytes']), ('outer_clear', outer, parent['outer_arena_bytes'])]:
        assert count % 2 == 0 and count // 2 <= 65536
        lines += [f'lea {hex(address)},%a0', f'move.w #{count//2-1},%d0', label + ':', 'clr.w (%a0)+', f'dbra %d0,{label}']
    lines += [f'lea {hex(deck)},%a0', f'lea {hex(outer+16)},%a1', 'move.w #100,%d0', 'move.l #0xa5a5a5a5,%d1', 'deck_fences:']
    for lo, hi in parent['deck_fences']:
        for offset in range(lo, hi, 4):
            lines.append(f'move.l %d1,{offset}(%a0)')
    lines += ['move.l %a1,392(%a0)', 'lea 1024(%a0),%a0', 'lea 384(%a1),%a1', 'dbra %d0,deck_fences', f'lea {hex(outer)},%a0', 'move.w #100,%d0', 'outer_fences:']
    for lo, hi in parent['outer_fences']:
        for offset in range(lo, hi, 4):
            lines.append(f'move.l %d1,{offset}(%a0)')
    lines += ['lea 384(%a0),%a0', 'dbra %d0,outer_fences']
    lines += stage_clear_lines(plan['staging_address'], plan['clear_bytes'])
    lines += ['movem.l (%sp)+,%d0-%d7/%a0-%a6', 'move.w #0x2700,%sr', 'jmp 0x400a']
    assembly, linker = out / 'finalizer.S', out / 'finalizer.ld'
    assembly.write_text('\n'.join(lines) + '\n')
    linker.write_text('SECTIONS { . = ' + hex(plan['finalizer_address']) + '; .text : { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
    tool = str(ROOT / 'tools/m68k-elf/bin/m68k-elf-')
    commands = [[tool+'as', '-m68000', '-o', str(out/'finalizer.o'), str(assembly)], [tool+'ld', '-T', str(linker), '-o', str(out/'finalizer.elf'), str(out/'finalizer.o')], [tool+'objcopy', '-O', 'binary', str(out/'finalizer.elf'), str(out/'finalizer.bin')]]
    for command in commands:
        subprocess.run(command, check=True, capture_output=True)
    finalizer = (out / 'finalizer.bin').read_bytes()
    assert len(finalizer) <= 384 and plan['finalizer_address'] + len(finalizer) <= deck
    named = subprocess.run([tool+'nm', '-n', str(out/'finalizer.elf')], check=True, capture_output=True, text=True).stdout
    assert any(line.endswith(' biwn_native_input_finalize') and int(line.split()[0], 16) == plan['finalizer_address'] for line in named.splitlines())
    resident = bytearray(heap - base)
    resident[:len(prefix)] = prefix
    segments = [(parent['shared_Deck_code_address'], shared), (parent['outer_code_address'], outer_code), (plan['input_address'], code), (resource_address,resource_code), (plan['finalizer_address'], finalizer)]
    assert all(a+len(data) <= next_a for (a, data), (next_a, _) in zip(segments, segments[1:]))
    for address, data in segments:
        resident[address-base:address-base+len(data)] = data
    for slot in range(101):
        address = deck - base + slot*1024
        for lo, hi in parent['deck_fences']:
            resident[address+lo:address+hi] = bytes([0xa5]) * (hi-lo)
        resident[address+392:address+396] = (outer+slot*384+16).to_bytes(4, 'big')
        address = outer - base + slot*384
        for lo, hi in parent['outer_fences']:
            resident[address+lo:address+hi] = bytes([0xa5]) * (hi-lo)
    component, copy = out / 'resident-with-arenas.bin', out / 'resident-copy-prefix.bin'
    component.write_bytes(resident)
    copy.write_bytes(resident[:plan['copy_bytes']])
    helper = native_root / 'input-wide-startup-prototype-v1/widen_loader.py'
    spec = importlib.util.spec_from_file_location('checked_local_widen_loader', helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    before = Path(parent['derived_stage']).read_bytes()
    loader = before[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]
    loader = module.widen_biwn_loader(loader, plan['copy_bytes'])
    assert loader[28:30] == bytes.fromhex('22d8')
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    original = (session/'nextstage-68000-candidate.bin').read_bytes()
    assert not any(original[plan['staging_address']-0x4000:0xfe200-0x4000])
    stage, changes = bytearray(before), []

    def patch(address, data, reason):
        offset = address-0x4000
        old = bytes(stage[offset:offset+len(data)])
        assert len(old) == len(data) and address % 2 == len(data) % 2 == 0
        stage[offset:offset+len(data)] = data
        changes.append(dict(address=hex(address), original=old.hex(), replacement=data.hex(), reason=reason))

    patch(0x4000, bytes.fromhex('4ef9')+plan['staging_address'].to_bytes(4, 'big'), 'Move startup staging to fit compiled input; same startup continuation.')
    patch(plan['staging_address'], loader+bytes(resident[:plan['copy_bytes']])+bytes(plan['clear_bytes']-40-plan['copy_bytes']), 'Verified local longword loader; initialize relocated arenas and clear staging with longwords.')
    assert before[0x1a266-0x4000:0x1a26c-0x4000] == bytes.fromhex('4eb9000191f4')
    patch(0x1a266, bytes.fromhex('4eb9')+rebase['new_entry'].to_bytes(4, 'big'), 'Redirect only the original input caller to guarded v5 input; global191F4 preserved.')
    assert stage[0x191f4-0x4000:0x1a1d0-0x4000] == before[0x191f4-0x4000:0x1a1d0-0x4000]
    assert stage[0xfe200-0x4000:] == before[0xfe200-0x4000:]
    stage_path = out/'mainstage-native-input-arena-v1.bin'
    stage_path.write_bytes(stage)
    disc = out/'BIWN-23-native-input-arena-v1-experimental.cdi'
    subprocess.run(['/bin/cp', '-c', parent['derived_disc'], str(disc)], check=True, capture_output=True)
    offset = read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
    with disc.open('r+b') as handle:
        for row in changes:
            old, replacement = bytes.fromhex(row['original']), bytes.fromhex(row['replacement'])
            handle.seek(offset+int(row['address'],16)-0x4000)
            assert handle.read(len(old)) == swap16(old)
            handle.seek(offset+int(row['address'],16)-0x4000)
            handle.write(swap16(replacement))
        handle.flush()
        os.fsync(handle.fileno())
        handle.seek(offset)
        assert swap16(handle.read(len(stage))) == stage
    assert sha(parent['derived_disc']) == parent['derived_disc_sha256']
    manifest = out/'stage-patches.json'
    save(manifest, dict(delta_patches=changes, heap_relocations=relocations, parent_manifest=parent['patch_manifest'], parent_manifest_sha256=parent['patch_manifest_sha256'],resource_entry_patches=resource_patches))
    state = dict(parent)
    state.update(status='terminal_input_resource_arena_image_built_UNQUALIFIED', profile='native-input-resource-arena-v39-experimental', directory=str(out), pid=os.getpid(), parent_build=str(out/'parent-build.json'), parent_build_sha256=sha(out/'parent-build.json'),
        derived_disc=str(disc), derived_disc_sha256=sha(disc), derived_stage=str(stage_path), derived_stage_sha256=sha(stage_path), component=str(component), component_sha256=sha(component), component_bytes=len(resident),
        copy_component=str(copy), copy_component_sha256=sha(copy), copy_component_bytes=plan['copy_bytes'], linked_component_bytes=plan['finalizer_address']-base+len(finalizer), heap_start=heap, heap_bytes_reserved=len(resident), initial_heap_bytes=plan['initial_heap_bytes'],
        staging_address=plan['staging_address'], staging_bytes_cleared=plan['clear_bytes'], native_entry_bytes=40+plan['copy_bytes'], shared_Deck_symbols=fs, outer_symbols=osym, deck_arena_address=deck, outer_arena_address=outer, deck_finalizer_address=plan['finalizer_address'], deck_finalizer_bytes=len(finalizer),
        symbols={**parent['symbols'], 'biwn_native_heap_start':heap}, layout_relocations=relocations, patch_manifest=str(manifest), patch_manifest_sha256=sha(manifest),
        native_input_address=plan['input_address'], native_input_entry=rebase['new_entry'], native_input_bytes=len(code), native_input_payload=v6['payload'], native_input_payload_sha256=sha(v6['payload']), native_input_profile=v6['source_profile'],native_input_reserve=768,resource_arena_code_address=resource_address,resource_arena_code_bytes=len(resource_code),resource_arena_symbols=resource_symbols,resource_arena_payload=str(resource_build/'native.bin'),resource_arena_payload_sha256=sha(resource_build/'native.bin'),resource_arena_source_profile=str(resource_source),resource_arena_entry_patches=resource_patches,additional_private_arena_bytes=0,source_wait32_and_IRQ16_proofs_do_not_qualify_new_image=True,same_task_reentry_qualified=False,
        startup_copy_width_bytes=4, startup_clear_width_bytes=4, local_widen_helper=str(helper), local_widen_helper_edited=False, input_callsite=0x1a266, global191F4_preserved=True,
        inherited_metadata_note='Ancestor component/prototype counts describe historical v34 proofs only. No current-image gate is inherited.', qualification_inherited=False, whole_parent_prefix_byte_identity=False, component_prefix_byte_identical=False, parent_resident_prefix_byte_identical=False,
        heap_layout_unchanged=False, staging_layout_unchanged=False, final_address_gates_verified=False, startup_heap_verified=False, alias_nesting_verified=False, observer_qualified=False, fresh_gameplay_verified=False, gameplay_verified=False, game_frames=0,
        physical_console_verified=False, arbitrary_IRQ_qualified=False, default_promoted=False, installed_preview_changed=False, whole_game_complete=False, new_training=False, new_predictions=0, optimizer_updates=0, original_disc_modified=False, pending_v37_changed=False, scope=__doc__)
    paths = [*extra_paths,*[p for p in resource_build.iterdir()if p.is_file()],resource_source/'native-acquire.S',resource_source/'native.ld',out/'resource-link-commands.json',Path(v6['payload']),Path(__file__), bp, rp, wp, sp, cp, helper, ROOT/'scripts/wide_bootstrap_support_v1.py', assembly, linker, component, copy, stage_path, manifest, out/'input-layout-plan.json', out/'parent-build.json', out/'shared-build/native-shared.bin', out/'outer-build/native-outer.bin', out/'shared-build/symbols.txt', out/'outer-build/symbols.txt', Path(rebase['payload'])]
    paths += [p for src in [shared_src, outer_src] for p in src.iterdir() if p.is_file()]
    state['source_sha256'] = {str(p):sha(p) for p in paths}
    save(out/'protocol.json', state)
    save(V/'native-input-arena-disc-build-v1-current.json', state)
    print({k:state[k] for k in ['status','native_input_bytes','component_bytes','copy_component_bytes','initial_heap_bytes','deck_finalizer_bytes']}, flush=True)


if __name__ == '__main__':
    main()
