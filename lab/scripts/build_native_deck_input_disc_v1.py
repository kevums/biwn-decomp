"""Separate native Deck input candidate; copy code and initialize its larger arena.

The 16-bit staging loop copies only the immutable prefix plus the old GPU
arena. The new Deck arena is zeroed and guarded by a resident early finalizer,
so its103424bytes do not inflate the staging copy past the65536-word limit.
No default-preview promotion, physical-console or whole-game claim.
"""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
import check_native_deck_coordinate_v1 as kernel
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 input_gate=read(V/'native-deck-input-v1-current.json');assert input_gate['completed']==2048 and input_gate['task_slots']==101
 nested=read(V/'native-deck-input-nesting-v1-current.json');assert nested['completed']==128
 for p,h in {**input_gate['source_sha256'],**nested['source_sha256']}.items():assert sha(p)==h,p
 gate=read(V/'native-deck-coordinate-v2-current.json');assert gate['completed']==576 and gate['task_slots_covered']==101
 connected=read(V/'native-deck-connected-v2-current.json');assert connected['status']=='terminal_native_coordinate_connected_real_helpers_match'and connected['paired_checkpoints']==31
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 parent=read(V/'native-gpu-command-family-disc-build-current.json');assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
 out=ROOT/'builds/BIWN-native-Deck-input-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 save(out/'parent-build.json',parent);save(out/'component-gate.json',gate);save(out/'connected-gate.json',connected)
 base=parent['resident_address'];prefix=bytearray(Path(parent['component']).read_bytes());old_floor=parent['heap_start'];assert base+len(prefix)==old_floor
 address=old_floor;build=out/'deck-build';first_arena=(address+gate['code_bytes']+input_gate['code_bytes']+192+63)&~63
 def compile_deck(arena):
  p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(address),'ARENA_ADDRESS='+hex(arena)],cwd=kernel.SRC,capture_output=True,text=True);(out/'deck-compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  return (build/'native-deck.bin').read_bytes(),kernel.symbols(build/'symbols.txt')
 deck,syms=compile_deck(first_arena);assert len(deck)==gate['code_bytes']
 input_address=address+len(deck);input_build=out/'input-build'
 input_source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-input-v1'
 p=subprocess.run(['make','BUILD='+str(input_build),'ADDRESS='+hex(input_address),'ARENA_ADDRESS='+hex(first_arena)],cwd=input_source,capture_output=True,text=True);(out/'input-compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 input_code=(input_build/'native-input.bin').read_bytes();input_symbols=kernel.symbols(input_build/'symbols.txt');assert len(input_code)==input_gate['code_bytes']
 finalizer_address=input_address+len(input_code)
 # Finalizer instruction sizes are address-independent; choose a fixed192
 # byte append region and align the separate data arena after it.
 arena=(finalizer_address+192+63)&~63;assert arena==first_arena
 arena_bytes=101*1024;heap=arena+arena_bytes;reservation=heap-base
 copy_bytes=arena-base;clear=((40+copy_bytes+63)//64)*64;staging=0xfe200-clear
 assert copy_bytes%2==clear%2==0 and copy_bytes<=131072 and clear<=131072 and staging>=0xd9d28
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);original=(session/'nextstage-68000-candidate.bin').read_bytes();assert not any(original[staging-0x4000:0xfe200-0x4000])
 assembly=out/'early-finalize.S';assembly.write_text(f'''.text
.globl biwn_native_deck_early_finalize
biwn_native_deck_early_finalize:
lea {hex(arena)},%a0
move.w #{arena_bytes//2-1},%d0
1:clr.w (%a0)+
dbra %d0,1b
lea {hex(arena)},%a0
move.w #100,%d0
move.l #0xa5a5a5a5,%d1
2:move.l %d1,(%a0)
move.l %d1,4(%a0)
move.l %d1,8(%a0)
move.l %d1,12(%a0)
move.l %d1,128(%a0)
move.l %d1,132(%a0)
move.l %d1,136(%a0)
move.l %d1,140(%a0)
move.l %d1,256(%a0)
move.l %d1,260(%a0)
move.l %d1,264(%a0)
move.l %d1,268(%a0)
move.l %d1,704(%a0)
move.l %d1,708(%a0)
move.l %d1,712(%a0)
move.l %d1,716(%a0)
move.l %d1,1008(%a0)
move.l %d1,1012(%a0)
move.l %d1,1016(%a0)
move.l %d1,1020(%a0)
lea 1024(%a0),%a0
dbra %d0,2b
lea {hex(staging)},%a0
move.w #{clear//2-1},%d0
3:clr.w (%a0)+
dbra %d0,3b
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w #0x2700,%sr
jmp 0x400a
''')
 linker=out/'early-finalize.ld';linker.write_text('SECTIONS { . = '+hex(finalizer_address)+'; .text : { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
 tool=ROOT/'tools/m68k-elf/bin/m68k-elf-';subprocess.run([str(tool)+'as','-m68000','-o',str(out/'finalizer.o'),str(assembly)],check=True);subprocess.run([str(tool)+'ld','-T',str(linker),'-o',str(out/'finalizer.elf'),str(out/'finalizer.o')],check=True);subprocess.run([str(tool)+'objcopy','-O','binary',str(out/'finalizer.elf'),str(out/'finalizer.bin')],check=True)
 finalizer=(out/'finalizer.bin').read_bytes();assert len(finalizer)<=192
 relocations=[];allowed=set()
 for delta,wanted in [(0,5),(4,1),(8,1)]:
  old=(old_floor+delta).to_bytes(4,'big');indices=[i for i in range(len(prefix)-3)if prefix[i:i+4]==old];assert len(indices)==wanted,(delta,indices)
  for i in indices:
   prefix[i:i+4]=(heap+delta).to_bytes(4,'big');allowed.update(range(i,i+4));relocations.append(dict(address=base+i,old=old_floor+delta,new=heap+delta))
 at=parent['symbols']['biwn_native_startup_finalize']-base;prefix[at:at+6]=b'\x4e\xf9'+finalizer_address.to_bytes(4,'big');allowed.update(range(at,at+6))
 before_prefix=Path(parent['component']).read_bytes();assert all(i in allowed for i,(a,b)in enumerate(zip(before_prefix,prefix))if a!=b)
 resident=bytearray(reservation);resident[:len(prefix)]=prefix;resident[address-base:address-base+len(deck)]=deck;resident[input_address-base:input_address-base+len(input_code)]=input_code;resident[finalizer_address-base:finalizer_address-base+len(finalizer)]=finalizer
 for i in range(101):
  offset=arena-base+i*1024;resident[offset:offset+16]=bytes([0xa5])*16;resident[offset+1008:offset+1024]=bytes([0xa5])*16
  for lo in [128,256,704]:resident[offset+lo:offset+lo+16]=bytes([0xa5])*16
 component=out/'resident-with-arenas.bin';component.write_bytes(resident);copy=out/'resident-copy-prefix.bin';copy.write_bytes(resident[:copy_bytes])
 before=Path(parent['derived_stage']).read_bytes();stage=bytearray(before);changes=[]
 def patch(a,data,reason):
  at=a-0x4000;old=bytes(stage[at:at+len(data)]);stage[at:at+len(data)]=data;changes.append(dict(address=hex(a),original=old.hex(),replacement=data.hex(),reason=reason))
 loader=bytearray(before[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]);assert loader[24:26]==bytes.fromhex('303c');loader[26:28]=(copy_bytes//2-1).to_bytes(2,'big')
 patch(0x4000,b'\x4e\xf9'+staging.to_bytes(4,'big'),'Relocate compact staging;new arena initialized separately before400A.')
 patch(staging,bytes(loader)+bytes(resident[:copy_bytes])+bytes(clear-40-copy_bytes),'Copy old guarded GPU arena/new native coordinate code;early resident finalizer initializes the larger Deck arena.')
 assert before[0x11d1a-0x4000:0x11d20-0x4000]==original[0x11d1a-0x4000:0x11d20-0x4000]
 patch(0x11d1a,b'\x4e\xf9'+syms['biwn_native_deck_coordinate'].to_bytes(4,'big'),'Qualified localV6Repair+10coordinatorflagupdates,withcoordinator68000/task-stack/nativehelperbridge.')
 patch(0x11b4c,b'\x4e\xf9'+input_symbols['biwn_native_deck_input'].to_bytes(4,'big'),'Qualified coordinator input C, separate per-task frame144/stack704, original helper ABI and guarded fallback.')
 repair=read(V/'native-Deck-asset-repair-build-current.json')
 for row in repair['patches']:
  at=int(row['address'],16);assert bytes(stage[at-0x4000:at-0x4000+len(bytes.fromhex(row['original']))])==bytes.fromhex(row['original'])
  patch(at,bytes.fromhex(row['replacement']),'Retained explicit source-assembled16-to13-frame Deck asset restoration.')
 assert stage[0xfe200-0x4000:]==before[0xfe200-0x4000:]==original[0xfe200-0x4000:]
 stagepath=out/'mainstage-native-Deck-input.bin';stagepath.write_bytes(stage);disc=out/'BIWN-23-native-Deck-input-v1-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
 with disc.open('r+b')as stream:
  for row in changes:
   pos=offset+int(row['address'],16)-0x4000;stream.seek(pos);assert stream.read(len(bytes.fromhex(row['original'])))==swap16(bytes.fromhex(row['original']));stream.seek(pos);stream.write(swap16(bytes.fromhex(row['replacement'])))
  stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
 intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in changes];position=changed=0
 with Path(parent['derived_disc']).open('rb')as a,disc.open('rb')as b:
  while True:
   left,right=a.read(1048576),b.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changed+=1
   position+=len(left)
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
 manifest=out/'stage-patches.json';save(manifest,dict(patches=read(parent['patch_manifest'])['patches']+changes,delta_patches=changes,heap_relocations=relocations))
 state=dict(parent);state.update(status='terminal_native_Deck_input_disc_built_pending_boot_heap_live',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagepath),derived_stage_sha256=sha(stagepath),component=str(component),component_bytes=reservation,component_sha256=sha(component),copy_component=str(copy),copy_component_bytes=copy_bytes,copy_component_sha256=sha(copy),linked_component_bytes=parent['linked_component_bytes']+len(deck)+len(input_code)+len(finalizer),heap_start=heap,heap_bytes_reserved=reservation,staging_address=staging,staging_bytes_cleared=clear,native_entry_bytes=40+copy_bytes,deck_symbols=syms,deck_code_address=address,deck_code_bytes=len(deck),deck_arena_address=arena,deck_arena_bytes=arena_bytes,deck_arena_slots=101,deck_arena_stride=1024,deck_finalizer_address=finalizer_address,deck_finalizer_bytes=len(finalizer),symbols={**parent['symbols'],'biwn_native_heap_start':heap},patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),layout_relocations=relocations,delta_CDI_changed_bytes=changed,coordinate_source_authorship='LocalV6Repair+10coordinatorstackflagupdates;coordinatornativeABI/bootloader/arena adapters.',coordinate_component_cases=576,coordinate_connected_checkpoint_pairs=31,game_frames=0,gameplay_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False,new_training=False,new_predictions=0,scope=__doc__)
 state.update(input_symbols=input_symbols,input_code_address=input_address,input_code_bytes=len(input_code),input_component_cases=2048,input_nested_cases=128,input_frame_offset=144,input_C_stack_top=704,input_fence_offsets=[128,256,704],input_source_authorship='Coordinator qualified recovered input body and native ABI; local ABI review rejected.',installed_Deck_entries=['11b4c','11d1a'],remaining_hosted_Deck_entries=['11828','11ad4','11e6c','1186a'],restoration_changes_original_behavior=True,input_component_gate=str(V/'native-deck-input-v1-current.json'),input_nested_gate=str(V/'native-deck-input-nesting-v1-current.json'))
 state['source_sha256']={str(p):sha(p)for p in [Path(__file__),component,copy,stagepath,manifest,assembly,linker,out/'parent-build.json',out/'component-gate.json',out/'connected-gate.json']};save(out/'protocol.json',state);save(V/'native-Deck-input-disc-build-current.json',state)
 print({k:state[k]for k in ['status','linked_component_bytes','component_bytes','copy_component_bytes','heap_start','staging_address']})
if __name__=='__main__':main()
