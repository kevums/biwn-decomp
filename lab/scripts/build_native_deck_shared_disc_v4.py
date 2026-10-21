"""Build a separate five-caller experimental disc, pending final/live gates.

Keeps the same 101x1024-byte Deck arena and prior guarded GPU arena.
The retained 13-frame asset restoration changes original 16-frame behavior.
Does not promote a preview or claim a complete source rebuild.
"""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
import check_native_deck_shared_v4 as kernel

V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 gate=read(V/'native-deck-shared-v4-current.json');nested=read(V/'native-deck-shared-connected-v4-current.json')
 assert gate['completed']==5248 and gate['fallback_cases']==20
 assert nested['completed']>=128 and nested['task_slots']==101
 assert gate['status']=='terminal_shared_v4_original_CPU_helper_fixtures_match'
 assert nested['status']=='terminal_retained_four_callers_nested_CPU_match_five_caller_payload' and nested['native_entries']['geometry']==0
 alias=read(V/'native-deck-alias-nesting-v4-current.json');assert alias['completed']==128
 geometry_alias=read(V/'native-deck-geometry-alias-v4-current.json');assert geometry_alias['completed']==128
 fallback=read(V/'shared-Deck-fallback-ABI-prototype-v4-current.json');assert fallback['completed']==1280
 for proof in [nested,alias,geometry_alias]:
  bound=read(Path(proof['directory'])/'component-gate.json');assert bound['payload_sha256']==gate['payload_sha256']
 for proof in [gate,nested,alias,geometry_alias,fallback]:
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p
 parent=read(V/'native-gpu-command-family-disc-build-current.json');assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
 for path,key in [('component','component_sha256'),('derived_stage','derived_stage_sha256'),('patch_manifest','patch_manifest_sha256')]:assert sha(parent[path])==parent[key]
 out=ROOT/'builds/BIWN-native-Deck-shared-v4'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 for name,value in [('parent-build',parent),('component-gate',gate),('connected-gate',nested),('alias-gate',alias),('geometry-alias-gate',geometry_alias),('fallback-gate',fallback)]:save(out/(name+'.json'),value)
 base=parent['resident_address'];prefix=bytearray(Path(parent['component']).read_bytes());old_floor=parent['heap_start'];assert base+len(prefix)==old_floor
 address=old_floor;arena=(address+gate['code_bytes']+192+63)&~63;arena_bytes=101*1024;heap=arena+arena_bytes;reservation=heap-base
 copy_bytes=arena-base;clear=((40+copy_bytes+63)//64)*64;staging=0xfe200-clear
 assert copy_bytes%2==clear%2==0 and copy_bytes<=131072 and clear<=131072 and staging>=0xd9d28
 build=out/'shared-build';p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(address),'ARENA_ADDRESS='+hex(arena)],cwd=kernel.SRC,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 code=(build/'native-shared.bin').read_bytes();syms=kernel.symbols(build/'symbols.txt');assert len(code)==gate['code_bytes'];finalizer_address=address+len(code)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);original=(session/'nextstage-68000-candidate.bin').read_bytes();assert not any(original[staging-0x4000:0xfe200-0x4000])
 assembly=out/'early-finalize.S';lines=['.text','.globl biwn_native_deck_early_finalize','biwn_native_deck_early_finalize:',f'lea {hex(arena)},%a0',f'move.w #{arena_bytes//2-1},%d0','1:clr.w (%a0)+','dbra %d0,1b',f'lea {hex(arena)},%a0','move.w #100,%d0','move.l #0xa5a5a5a5,%d1','2:']
 for lo,hi in kernel.FENCES:
  assert lo%4==hi%4==0
  for at in range(lo,hi,4):lines.append(f'move.l %d1,{at}(%a0)')
 lines+=['lea 1024(%a0),%a0','dbra %d0,2b',f'lea {hex(staging)},%a0',f'move.w #{clear//2-1},%d0','3:clr.w (%a0)+','dbra %d0,3b','movem.l (%sp)+,%d0-%d7/%a0-%a6','move.w #0x2700,%sr','jmp 0x400a'];assembly.write_text('\n'.join(lines)+'\n')
 linker=out/'early-finalize.ld';linker.write_text('SECTIONS { . = '+hex(finalizer_address)+'; .text : { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
 tool=ROOT/'tools/m68k-elf/bin/m68k-elf-'
 for command in [[str(tool)+'as','-m68000','-o',str(out/'finalizer.o'),str(assembly)],[str(tool)+'ld','-T',str(linker),'-o',str(out/'finalizer.elf'),str(out/'finalizer.o')],[str(tool)+'objcopy','-O','binary',str(out/'finalizer.elf'),str(out/'finalizer.bin')]]:subprocess.run(command,check=True,capture_output=True)
 finalizer=(out/'finalizer.bin').read_bytes();assert len(finalizer)<=192 and finalizer_address+len(finalizer)<=arena
 relocations=[];allowed=set()
 for delta,wanted in [(0,5),(4,1),(8,1)]:
  old=(old_floor+delta).to_bytes(4,'big');indices=[i for i in range(len(prefix)-3)if prefix[i:i+4]==old];assert len(indices)==wanted,(delta,indices)
  for i in indices:prefix[i:i+4]=(heap+delta).to_bytes(4,'big');allowed.update(range(i,i+4));relocations.append(dict(address=base+i,old=old_floor+delta,new=heap+delta))
 at=parent['symbols']['biwn_native_startup_finalize']-base;prefix[at:at+6]=b'\x4e\xf9'+finalizer_address.to_bytes(4,'big');allowed.update(range(at,at+6));before_prefix=Path(parent['component']).read_bytes();assert all(i in allowed for i,(a,b)in enumerate(zip(before_prefix,prefix))if a!=b)
 resident=bytearray(reservation);resident[:len(prefix)]=prefix;resident[address-base:address-base+len(code)]=code;resident[finalizer_address-base:finalizer_address-base+len(finalizer)]=finalizer
 for slot in range(101):
  at=arena-base+slot*1024
  for lo,hi in kernel.FENCES:resident[at+lo:at+hi]=bytes([0xa5])*(hi-lo)
 component=out/'resident-with-arenas.bin';component.write_bytes(resident);copy=out/'resident-copy-prefix.bin';copy.write_bytes(resident[:copy_bytes])
 before=Path(parent['derived_stage']).read_bytes();stage=bytearray(before);changes=[]
 def patch(a,data,reason):
  at=a-0x4000;old=bytes(stage[at:at+len(data)]);stage[at:at+len(data)]=data;changes.append(dict(address=hex(a),original=old.hex(),replacement=data.hex(),reason=reason))
 loader=bytearray(before[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]);assert loader[24:26]==bytes.fromhex('303c');loader[26:28]=(copy_bytes//2-1).to_bytes(2,'big')
 patch(0x4000,b'\x4e\xf9'+staging.to_bytes(4,'big'),'Relocate compact staging; initialize Deck arena separately before400A.')
 patch(staging,bytes(loader)+bytes(resident[:copy_bytes])+bytes(clear-40-copy_bytes),'Copy guarded GPU arena and five-caller module; resident finalizer initializes Deck arena.')
 for name,(root,offset,lower,top)in kernel.LAYOUT.items():
  size=8 if name=='geometry'else 6
  assert before[root-0x4000:root-0x4000+size]==original[root-0x4000:root-0x4000+size]
  patch(root,b'\x4e\xf9'+syms['biwn_v4_'+name].to_bytes(4,'big')+(b'\x4e\x71'if size==8 else b''),'Experimental shared-v4 '+name+' caller; component and nested CPU gates, final/live gates pending.')
 repair=read(V/'native-Deck-asset-repair-build-current.json')
 for row in repair['patches']:
  at=int(row['address'],16);assert bytes(stage[at-0x4000:at-0x4000+len(bytes.fromhex(row['original']))])==bytes.fromhex(row['original']);patch(at,bytes.fromhex(row['replacement']),'Retained explicit16-to13-frame asset restoration.')
 assert stage[0xfe200-0x4000:]==before[0xfe200-0x4000:]==original[0xfe200-0x4000:]
 stagepath=out/'mainstage-native-Deck-shared-v4.bin';stagepath.write_bytes(stage);disc=out/'BIWN-23-native-Deck-shared-v4-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
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
 state=dict(parent);state.update(status='terminal_native_Deck_shared_disc_built_pending_final_boot_live',pid=os.getpid(),directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagepath),derived_stage_sha256=sha(stagepath),component=str(component),component_bytes=reservation,component_sha256=sha(component),copy_component=str(copy),copy_component_bytes=copy_bytes,copy_component_sha256=sha(copy),linked_component_bytes=parent['linked_component_bytes']+len(code)+len(finalizer),heap_start=heap,heap_bytes_reserved=reservation,staging_address=staging,staging_bytes_cleared=clear,native_entry_bytes=40+copy_bytes,shared_Deck_symbols=syms,shared_Deck_code_address=address,shared_Deck_code_bytes=len(code),deck_arena_address=arena,deck_arena_bytes=arena_bytes,deck_arena_slots=101,deck_arena_stride=1024,deck_layout=kernel.LAYOUT,deck_fences=kernel.FENCES,deck_finalizer_address=finalizer_address,deck_finalizer_bytes=len(finalizer),symbols={**parent['symbols'],'biwn_native_heap_start':heap},patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),layout_relocations=relocations,delta_CDI_changed_bytes=changed,component_cases=5248,nested_cases=nested['completed'],installed_Deck_entries=['11828','1186a','11ad4','11b4c','11d1a'],remaining_hosted_Deck_entries=['11e6c'],restoration_changes_original_behavior=True,game_frames=0,gameplay_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False,new_training=False,new_predictions=0,scope=__doc__)
 paths=[Path(__file__),component,copy,stagepath,manifest,assembly,linker,out/'parent-build.json',out/'component-gate.json',out/'connected-gate.json',out/'alias-gate.json',Path(kernel.__file__)]
 prior_wrapper=kernel.SRC.parent/'deck-shared-v3/native-shared.c'
 # New geometry dispatch declarations are added within the wrapper; qualified algorithm includes remain identical.
 state.update(inherited_face_bridge_provenance=str(V/'native-Deck-shared-reviewed-v3-current.json'),face_algorithm_authorship='Existing coordinator-recovered body. Earlier local face bridge retained with coordinator v3-to-v4 symbol renaming; new geometry bridge is coordinator integration.',geometry_algorithm_authorship='Unchanged coordinator-recovered collect_geometry; coordinator native wrapper/capture/assembly integration.',new_local_source_adopted=False,geometry_alias_cases=128,prototype_full_fallback_cases=1280)
 paths.extend([prior_wrapper,kernel.SRC/'native-shared.c',kernel.SRC/'native-shared.S',kernel.SRC/'native-shared.ld',kernel.SRC/'Makefile',out/'geometry-alias-gate.json',out/'fallback-gate.json',V/'native-Deck-shared-reviewed-v3-current.json'])
 state['source_sha256']={str(p):sha(p)for p in paths};save(out/'protocol.json',state);save(V/'native-Deck-shared-disc-build-v4-current.json',state)
 print({k:state[k]for k in ['status','linked_component_bytes','component_bytes','copy_component_bytes','heap_start']})

if __name__=='__main__':main()
