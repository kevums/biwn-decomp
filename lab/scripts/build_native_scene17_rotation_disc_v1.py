"""Separate v25 image: structured17F14 buffer rotation runs inside the native scene caller.
The original185B2 display-list builder remains captured; global17F14 is unchanged.
Existing direct completion polling and all prior native callers/helpers remain.
Final-address,observer,nesting and fresh gameplay qualification is still required.
"""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
import check_native_deck_scene_reset_v1 as five
five.SRC=five.SRC.parent/'deck-shared-v25-scene-rotation'
five.LAYOUT={**five.LAYOUT,'scene':(0x17e0e,144,608,816)}
import check_native_deck_outer_v1 as outer
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())


def main():
    pointers=[V/'native-deck-retained-scene17-rotation-v1-current.json',V/'native-geometry-scene17-rotation-v1-current.json',V/'native-Deck-outer-v1-current.json',V/'native-Deck-outer-connected-v1-current.json',V/'native-Deck-outer-fallback-v1-current.json',V/'native-Deck-outer-waits-v1-current.json']
    gates=[read(p)for p in pointers];fg,tg,og,cg,fb,wg=gates
    assert fg['completed']==4992 and tg['completed']==256 and fg['code_bytes']==tg['code_bytes'] and tg['maximum_C_stack_bytes']==164 and og['completed']==1280 and cg['completed']==128 and cg['task_slots']==101
    assert fb['completed']==384 and wg['completed']==192 and all(cg['native_returns'].values())
    for g in gates:
        for p,h in g['source_sha256'].items():assert sha(p)==h,p
    bus_gate=read(V/'scene17-rotation-input-public-bus-v1-current.json');assert bus_gate['completed']==13 and bus_gate['payload_sha256']==fg['payload_sha256']
    for path,digest in bus_gate['source_sha256'].items():assert sha(path)==digest,path
    for name,count in [('scene17-rotation-bridge-v1',770),('scene17-rotation-fallback-v1',384),('scene17-rotation-reentry-v1',64),('scene17-rotation-public-bus-v1',14)]:
        gate=read(V/(name+'-current.json'));assert gate['completed']==count and gate['status'].startswith('terminal_')
        for path,digest in gate['source_sha256'].items():assert sha(path)==digest,path
    previous=read(V/'native-Deck-shared-reviewed-v4-current.json');assert sha(previous['disc'])==previous['disc_sha256']
    previous_build=read(previous['build']);parent_path=Path(previous_build['parent_build']);parent=read(parent_path)
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
    for p,k in [('component','component_sha256'),('derived_stage','derived_stage_sha256'),('patch_manifest','patch_manifest_sha256')]:assert sha(parent[p])==parent[k]
    out=ROOT/'builds/BIWN-native-scene17-rotation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    save(out/'parent-build.json',parent)
    for i,g in enumerate(gates):save(out/f'gate-{i}.json',g)
    base=parent['resident_address'];address=parent['heap_start'];prefix=bytearray(Path(parent['component']).read_bytes());assert base+len(prefix)==address
    outer_address=(address+fg['code_bytes']+3)&~3;finalizer_address=(outer_address+og['code_bytes']+3)&~3
    deck=(finalizer_address+384+63)&~63;deck_bytes=101*1024;outer_arena=deck+deck_bytes;outer_bytes=101*576;heap=outer_arena+outer_bytes;reservation=heap-base
    copy_bytes=deck-base;clear=((40+copy_bytes+63)//64)*64;staging=0xfe200-clear
    assert copy_bytes%2==clear%2==0 and copy_bytes<=131072 and clear<=131072 and staging>=0xd9d28 and heap<0x1c0000
    jobs=[(five.SRC,out/'five-build',['ADDRESS='+hex(address),'ARENA_ADDRESS='+hex(deck)],'native-shared'),
          (outer.SRC,out/'outer-build',['ADDRESS='+hex(outer_address),'ARENA_ADDRESS='+hex(outer_arena),'DECK_ADDRESS='+hex(deck)],'native-outer')]
    for src,build,args,name in jobs:
        p=subprocess.run(['make','BUILD='+str(build),*args],cwd=src,capture_output=True,text=True);(out/(name+'-compiler.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    fcode=(out/'five-build/native-shared.bin').read_bytes();ocode=(out/'outer-build/native-outer.bin').read_bytes()
    assert len(fcode)==fg['code_bytes'] and len(ocode)==og['code_bytes']
    fs=five.symbols(out/'five-build/symbols.txt');osym=five.symbols(out/'outer-build/symbols.txt')
    assert fs['biwn_v4_coordinate']==address and osym['biwn_outer_entry']==outer_address,'ELF entry differs from binary load origin'
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);original=(session/'nextstage-68000-candidate.bin').read_bytes()
    assert not any(original[staging-0x4000:0xfe200-0x4000])
    lines=['.text','.globl biwn_native_deck_six_finalize','biwn_native_deck_six_finalize:']
    for label,a,count in [('deck_clear',deck,deck_bytes),('outer_clear',outer_arena,outer_bytes)]:
        lines +=[f'lea {hex(a)},%a0',f'move.w #{count//2-1},%d0',label+':','clr.w (%a0)+',f'dbra %d0,{label}']
    lines +=[f'lea {hex(deck)},%a0',f'lea {hex(outer_arena+16)},%a1','move.w #100,%d0','move.l #0xa5a5a5a5,%d1','deck_fences:']
    for lo,hi in five.FENCES:
        for at in range(lo,hi,4):lines.append(f'move.l %d1,{at}(%a0)')
    lines+=['move.l %a1,392(%a0)','lea 1024(%a0),%a0','lea 576(%a1),%a1','dbra %d0,deck_fences',f'lea {hex(outer_arena)},%a0','move.w #100,%d0','outer_fences:']
    for lo,hi in outer.FENCES:
        for at in range(lo,hi,4):lines.append(f'move.l %d1,{at}(%a0)')
    lines+=['lea 576(%a0),%a0','dbra %d0,outer_fences',f'lea {hex(staging)},%a0',f'move.w #{clear//2-1},%d0','stage_clear:','clr.w (%a0)+','dbra %d0,stage_clear','movem.l (%sp)+,%d0-%d7/%a0-%a6','move.w #0x2700,%sr','jmp 0x400a']
    assembly=out/'early-finalize.S';assembly.write_text('\n'.join(lines)+'\n');linker=out/'early-finalize.ld';linker.write_text('SECTIONS { . = '+hex(finalizer_address)+'; .text : { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
    tool=ROOT/'tools/m68k-elf/bin/m68k-elf-'
    for command in [[str(tool)+'as','-m68000','-o',str(out/'finalizer.o'),str(assembly)],[str(tool)+'ld','-T',str(linker),'-o',str(out/'finalizer.elf'),str(out/'finalizer.o')],[str(tool)+'objcopy','-O','binary',str(out/'finalizer.elf'),str(out/'finalizer.bin')]]:subprocess.run(command,check=True,capture_output=True)
    finalizer=(out/'finalizer.bin').read_bytes();assert len(finalizer)<=384 and finalizer_address+len(finalizer)<=deck
    named=subprocess.run([str(tool)+'nm','-n',str(out/'finalizer.elf')],capture_output=True,text=True,check=True).stdout
    actual=next(int(line.split()[0],16)for line in named.splitlines()if line.endswith(' biwn_native_deck_six_finalize'))
    assert actual==finalizer_address,'Finalizer ELF origin differs from binary load address'
    relocations=[];allowed=set()
    for delta,count in [(0,5),(4,1),(8,1)]:
        old=(address+delta).to_bytes(4,'big');indices=[i for i in range(len(prefix)-3)if prefix[i:i+4]==old];assert len(indices)==count,(delta,indices)
        for i in indices:prefix[i:i+4]=(heap+delta).to_bytes(4,'big');allowed.update(range(i,i+4));relocations.append(dict(address=base+i,old=address+delta,new=heap+delta))
    at=parent['symbols']['biwn_native_startup_finalize']-base;prefix[at:at+6]=b'\x4e\xf9'+finalizer_address.to_bytes(4,'big');allowed.update(range(at,at+6))
    assert all(i in allowed for i,(a,b)in enumerate(zip(Path(parent['component']).read_bytes(),prefix))if a!=b)
    resident=bytearray(reservation);resident[:len(prefix)]=prefix
    for a,data in [(address,fcode),(outer_address,ocode),(finalizer_address,finalizer)]:resident[a-base:a-base+len(data)]=data
    for slot in range(101):
        a=deck-base+slot*1024
        for lo,hi in five.FENCES:resident[a+lo:a+hi]=bytes([0xa5])*(hi-lo)
        resident[a+392:a+396]=(outer_arena+slot*576+16).to_bytes(4,'big')
        a=outer_arena-base+slot*576
        for lo,hi in outer.FENCES:resident[a+lo:a+hi]=bytes([0xa5])*(hi-lo)
    component=out/'resident-with-arenas.bin';component.write_bytes(resident);copy=out/'resident-copy-prefix.bin';copy.write_bytes(resident[:copy_bytes])
    before=Path(parent['derived_stage']).read_bytes();stage=bytearray(before);changes=[]
    def patch(a,data,reason):
        off=a-0x4000;old=bytes(stage[off:off+len(data)]);stage[off:off+len(data)]=data;changes.append(dict(address=hex(a),original=old.hex(),replacement=data.hex(),reason=reason))
    loader=bytearray(before[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]);assert loader[24:26]==bytes.fromhex('303c');loader[26:28]=(copy_bytes//2-1).to_bytes(2,'big')
    patch(0x4000,b'\x4e\xf9'+staging.to_bytes(4,'big'),'Move compact staging; initialize both Deck arenas before400A.')
    patch(staging,bytes(loader)+bytes(resident[:copy_bytes])+bytes(clear-40-copy_bytes),'Copy both native modules and GPU arena; separate finalizer clears and initializes both Deck arenas.')
    for name,(root,_,_,_)in five.LAYOUT.items():
        n=10 if name=='scene'else 8 if name=='geometry'else 6;assert before[root-0x4000:root-0x4000+n]==original[root-0x4000:root-0x4000+n]
        patch(root,b'\x4e\xf9'+fs['biwn_v4_'+name].to_bytes(4,'big')+bytes.fromhex('4e71')*(n//2-3),'Retained recovered '+name+' caller; final gates pending.')
    assert before[0x11e6c-0x4000:0x11e78-0x4000]==bytes.fromhex('4e56fff82d7900011e64fff8')
    patch(0x11e6c,b'\x4e\xf9'+osym['biwn_outer_entry'].to_bytes(4,'big')+bytes.fromhex('4e71')*3,'New outer-task bridge; whole twelve-byte prologue, with original fallback retained.')
    repair=read(V/'native-Deck-asset-repair-build-current.json')
    for row in repair['patches']:
        a=int(row['address'],16);assert bytes(stage[a-0x4000:a-0x4000+len(bytes.fromhex(row['original']))])==bytes.fromhex(row['original']);patch(a,bytes.fromhex(row['replacement']),'Retained explicit16-to13-frame restoration.')
    assert stage[0xfe200-0x4000:]==before[0xfe200-0x4000:]==original[0xfe200-0x4000:]
    stagepath=out/'mainstage-native-scene17-rotation-v1.bin';stagepath.write_bytes(stage);disc=out/'BIWN-23-native-scene17-rotation-v1-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True)
    offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
    with disc.open('r+b')as stream:
        for row in changes:
            pos=offset+int(row['address'],16)-0x4000;stream.seek(pos);assert stream.read(len(bytes.fromhex(row['original'])))==swap16(bytes.fromhex(row['original']));stream.seek(pos);stream.write(swap16(bytes.fromhex(row['replacement'])))
        stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256'] and sha(previous['disc'])==previous['disc_sha256']
    manifest=out/'stage-patches.json';save(manifest,dict(patches=read(parent['patch_manifest'])['patches']+changes,delta_patches=changes,heap_relocations=relocations))
    result=dict(parent);result.update(status='terminal_scene17_rotation_candidate_built_final_address_and_gameplay_pending',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),
        derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagepath),derived_stage_sha256=sha(stagepath),component=str(component),component_sha256=sha(component),component_bytes=reservation,
        copy_component=str(copy),copy_component_sha256=sha(copy),copy_component_bytes=copy_bytes,linked_component_bytes=parent['linked_component_bytes']+len(fcode)+len(ocode)+len(finalizer),
        heap_start=heap,heap_bytes_reserved=reservation,initial_heap_bytes=0x1c0000-heap,heap_layout_unchanged=False,staging_address=staging,staging_bytes_cleared=clear,native_entry_bytes=40+copy_bytes,
        shared_Deck_symbols=fs,shared_Deck_code_address=address,shared_Deck_code_bytes=len(fcode),deck_arena_address=deck,deck_arena_bytes=deck_bytes,deck_arena_slots=101,deck_arena_stride=1024,deck_layout=five.LAYOUT,deck_fences=five.FENCES,
        outer_symbols=osym,outer_code_address=outer_address,outer_code_bytes=len(ocode),outer_arena_address=outer_arena,outer_arena_bytes=outer_bytes,outer_arena_slots=101,outer_arena_stride=576,outer_fences=outer.FENCES,outer_pointer_offset=392,
        deck_finalizer_address=finalizer_address,deck_finalizer_bytes=len(finalizer),symbols={**parent['symbols'],'biwn_native_heap_start':heap},patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),layout_relocations=relocations,
        installed_Deck_entries=['11828','1186a','11ad4','11b4c','11d1a','11e6c'],installed_scene_entries=['17e0e'],new_readable_scene_entry='17e0e',scene_authorship='Coordinator readable scene plus structured buffer rotation; earlier local scene Author/Repair rejected; no new model output',prototype_scene_CPU_cases=770,prototype_scene_fallback_cases=384,prototype_scene_reentry_cases=64,prototype_scene_public_bus_cases=14,prototype_scene_C_stack_bytes=156,scene_native_direct_poll=True,scene_native_work_deadline=False,scene_native_helper_deadline=False,scene_host_test_budget_retained=True,scene_shares_input_face_guarded_frame=True,additional_arena_bytes=0,remaining_hosted_Deck_entries=[],newly_compiled_helper_entries=['10968','10ba4','11384','110d4','1142e','10734','1102a','17f14'],scene_internal_helper_entries=['17f14'],internal17F14_compiled=True,original17F14_global_entry_preserved=True,original185B2_display_list_retained=True,geometry_internal_helper_entries=['10968','10ba4','11384','110d4','1142e','10734'],input_internal_helper_entries=['1102a'],internal1102A_compiled=True,original1102A_global_entry_preserved=True,helper_global_entries_redirected=False,helpers_integrated_in_geometry_path_only=False,helpers_integrated_in_geometry_and_input=True,original110D4_global_entry_preserved=True,internal110D4_compiled=True,internal1142E_compiled=True,original1142E_global_entry_preserved=True,internal10734_compiled=True,original10734_global_entry_preserved=True,prototype_native_geometry_cases=256,retained_four_caller_cases=4992,prototype_geometry_C_stack_bytes=164,restoration_changes_original_behavior=True,game_frames=0,gameplay_verified=False,default_promoted=False,whole_game_complete=False,target_ALU_optimized=True,target_debug_liveness=True,
        physical_console_verified=False,new_training=False,new_predictions=0,input_native_primitives=True,input_explicit_CLR_sites=7,prototype_public_bus_cases=13,installed_preview_changed=False,scope=__doc__)
    paths=[Path(__file__),*pointers,parent_path,component,copy,stagepath,manifest,assembly,linker,out/'five-build/native-shared.bin',out/'outer-build/native-outer.bin']
    result['source_sha256']={str(p):sha(p)for p in paths};save(out/'protocol.json',result);save(V/'native-scene17-rotation-disc-build-v1-current.json',result)
    print({k:result[k]for k in ['status','linked_component_bytes','component_bytes','copy_component_bytes','initial_heap_bytes','deck_finalizer_bytes']},flush=True)


if __name__=='__main__':main()
