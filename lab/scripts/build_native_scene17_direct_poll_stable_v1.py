"""V24 direct polling in the existing v23 reservation/staging/heap layout.
Changes only the padded linked shared-module region in the existing stage.
The compact v24 build is preserved separately and is not this comparison.
Final-address,observers and gameplay remain unqualified until measured.
"""
import os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from extract_biwn_stage import swap16
from check_native_deck_coordinate_v1 import symbols
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 previousp=V/'native-scene17-wait-disc-build-v1-current.json';parent=read(previousp)
 for path,h in parent['source_sha256'].items():assert sha(path)==h,path
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
 stems=['native-deck-retained-scene17-direct-poll-v1','native-geometry-scene17-direct-poll-v1','scene17-direct-poll-bridge-v1','scene17-direct-poll-fallback-v1','scene17-direct-poll-reentry-v1','scene17-direct-poll-public-bus-v1','scene17-direct-poll-input-public-bus-v1'];gates={n:read(V/(n+'-current.json'))for n in stems}
 for name,g in gates.items():
  assert g['status'].startswith('terminal_')and'failed'not in g['status'],name
  for path,h in g['source_sha256'].items():assert sha(path)==h,(name,path)
 assert [gates[n]['completed']for n in stems]==[4992,256,770,384,64,14,13]
 out=ROOT/'builds/BIWN-native-scene17-direct-poll-stable-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'parent-build.json',parent)
 src=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v24-scene-direct-poll';address=parent['shared_Deck_code_address'];arena=parent['deck_arena_address'];build=out/'five-build';p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(address),'ARENA_ADDRESS='+hex(arena)],cwd=src,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 code=(build/'native-shared.bin').read_bytes();syms=symbols(build/'symbols.txt');old_size=parent['shared_Deck_code_bytes'];assert len(code)==44108<old_size==44226
 for key,value in parent['shared_Deck_symbols'].items():
  if key.startswith('biwn_v4_')and not key.endswith('_body'):assert syms[key]==value,key
 base=parent['resident_address'];offset=address-base;old_component=Path(parent['component']).read_bytes();old_module=old_component[offset:offset+old_size];padded=code+bytes.fromhex('4e71')*((old_size-len(code))//2);assert len(padded)==old_size
 resident=bytearray(old_component);resident[offset:offset+old_size]=padded;assert resident[:offset]==old_component[:offset]and resident[offset+old_size:]==old_component[offset+old_size:]
 component=out/'resident-with-arenas.bin';component.write_bytes(resident);copy=out/'resident-copy-prefix.bin';copy.write_bytes(resident[:parent['copy_component_bytes']])
 old_stage=Path(parent['derived_stage']).read_bytes();stage=bytearray(old_stage);at=parent['staging_address']+40+offset-0x4000;assert stage[at:at+old_size]==old_module;stage[at:at+old_size]=padded;assert stage[:at]==old_stage[:at]and stage[at+old_size:]==old_stage[at+old_size:]
 stagep=out/'mainstage-native-scene17-direct-poll-stable.bin';stagep.write_bytes(stage);disc=out/'BIWN-23-native-scene17-direct-poll-stable-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);raw_offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
 with disc.open('r+b')as f:f.seek(raw_offset+at);assert f.read(old_size)==swap16(old_module);f.seek(raw_offset+at);f.write(swap16(padded));f.flush();os.fsync(f.fileno());f.seek(raw_offset);assert swap16(f.read(len(stage)))==stage
 manifest=out/'stage-patches.json';save(manifest,dict(patches=read(parent['patch_manifest'])['patches'],delta_patches=[dict(address=hex(at+0x4000),original=old_module.hex(),replacement=padded.hex(),reason='New linked native scene direct poll;shared-module-only change in unchanged v23 layout')],previous_manifest=parent['patch_manifest']))
 subprocess.run(['/bin/cp','-cR',str(Path(parent['directory'])/'outer-build'),str(out/'outer-build')],check=True,capture_output=True)
 result=dict(parent);result.update(status='terminal_scene17_direct_poll_stable_candidate_built_final_gates_pending',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagep),derived_stage_sha256=sha(stagep),component=str(component),component_sha256=sha(component),copy_component=str(copy),copy_component_sha256=sha(copy),shared_Deck_code_bytes=len(code),shared_Deck_reserved_code_bytes=old_size,shared_Deck_padding_bytes=old_size-len(code),shared_Deck_symbols=syms,linked_component_bytes=parent['linked_component_bytes']-old_size+len(code),patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),heap_layout_unchanged=True,same_layout_parent=previousp.name,same_staging_copy_size=True,only_shared_module_stage_bytes_changed=True,scene_native_direct_poll=True,scene_native_work_deadline=False,scene_native_helper_deadline=False,prototype_scene_CPU_cases=770,prototype_scene_C_stack_bytes=108,game_frames=0,gameplay_verified=False,default_promoted=False,installed_preview_changed=False,whole_game_complete=False,new_training=False,new_predictions=0,scope=__doc__)
 paths=[Path(__file__),previousp,*[V/(n+'-current.json')for n in stems],*src.glob('*'),component,copy,stagep,manifest,build/'native-shared.bin',build/'symbols.txt'];result['source_sha256']={str(p):sha(p)for p in paths if p.is_file()};save(out/'protocol.json',result)
 pointer=V/'native-scene17-direct-poll-disc-build-v1-current.json'
 if pointer.exists():
  old=read(pointer);assert old['status'].startswith('terminal_');save(V/'native-scene17-direct-poll-compact-disc-build-v1-current.json',old)
 save(pointer,result);print(result['status'],len(code),result['initial_heap_bytes'],result['component_bytes'],flush=True)
if __name__=='__main__':main()
