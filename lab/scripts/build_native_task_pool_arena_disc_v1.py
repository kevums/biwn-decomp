"""Separate disc candidate with recovered pool initialization and task-owned GPU stacks.
Code bytes, mutable arena data, and the total resident reservation are distinct.
No preview promotion or full-game/hardware claim.
"""
import json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 gate=read(V/'task-pool-arena-final-current.json');assert gate['status']=='terminal_final_task_pool_and_GPU_arena_CPU_ownership_pass'
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 gd=Path(gate['directory']);parent=read(gd/'parent-build.json')
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256'] and sha(parent['component'])==parent['component_sha256']
 out=ROOT/'builds/BIWN-native-task-pool-arena-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 save(out/'parent-build.json',parent);save(out/'final-component.json',gate)
 linked=out/'resident-code.bin';padded=out/'resident-with-arenas.bin';linked.write_bytes((gd/'resident-code.bin').read_bytes());padded.write_bytes((gd/'resident-with-arenas.bin').read_bytes())
 reserve=gate['reservation_bytes'];staging=gate['staging_address'];clear=gate['staging_clear_bytes'];assert len(linked.read_bytes())==gate['resident_code_bytes'] and len(padded.read_bytes())==reserve
 stage=bytearray(Path(parent['derived_stage']).read_bytes());before=bytes(stage)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);original=(session/'nextstage-68000-candidate.bin').read_bytes()
 assert not any(original[staging-0x4000:0xfe200-0x4000]) and not any(stage[staging-0x4000:parent['staging_address']-0x4000]);changes=[]
 def patch(address,replacement,reason):
  at=address-0x4000;old=bytes(stage[at:at+len(replacement)]);stage[at:at+len(replacement)]=replacement;changes.append(dict(address=hex(address),original=old.hex(),replacement=replacement.hex(),reason=reason))
 loader=bytearray(stage[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]);assert loader[24:26]==bytes.fromhex('303c') and int.from_bytes(loader[26:28],'big')==parent['component_bytes']//2-1;loader[26:28]=(reserve//2-1).to_bytes(2,'big')
 patch(0x4000,b'\x4e\xf9'+staging.to_bytes(4,'big'),'Relocate staging for initializer code and separately reserved GPU stack arenas.')
 patch(staging,bytes(loader)+padded.read_bytes()+bytes(clear-40-reserve),'Copy code and guarded arena data; clear staging through unchanged FE200 trailer boundary.')
 assert before[0xdd40-0x4000:0xdd48-0x4000]==original[0xdd40-0x4000:0xdd48-0x4000]
 patch(0xdd40,b'\x4e\xf9'+gate['pool_symbols']['biwn_native_task_pool_initialize'].to_bytes(4,'big')+b'\x4e\x71','Complete recovered initializer, including actual USP and supervisor-to-user transition.')
 for entry,symbol in [(0xe220,'biwn_native_gpu_submit_4320'),(0xe2b8,'biwn_native_gpu_submit_4b00')]:
  assert before[entry-0x4000:entry+6-0x4000]==b'\x4e\xf9'+parent['mailbox_symbols'][symbol].to_bytes(4,'big')
  patch(entry,b'\x4e\xf9'+gate['GPU_symbols'][symbol].to_bytes(4,'big'),'Unchanged local repair with task-owned C stack ABI; real E098 helper retained.')
 assert stage[0xfe200-0x4000:]==before[0xfe200-0x4000:]==original[0xfe200-0x4000:]
 stagepath=out/'mainstage-native-task-pool-arena.bin';stagepath.write_bytes(stage);disc=out/'BIWN-23-native-task-pool-arena-v1-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
 with disc.open('r+b')as stream:
  for row in changes:
   at=offset+int(row['address'],16)-0x4000;expected=bytes.fromhex(row['original']);stream.seek(at);assert stream.read(len(expected))==swap16(expected);stream.seek(at);stream.write(swap16(bytes.fromhex(row['replacement'])))
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
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256'];assert sha(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi')=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
 manifest=out/'stage-patches.json';save(manifest,dict(parent=str(out/'parent-build.json'),patches=read(parent['patch_manifest'])['patches']+changes,delta_patches=changes,resident_relocations=gate['layout_relocations']))
 state=dict(parent)
 state.update(status='terminal_task_pool_arena_disc_built_pending_startup_heap_and_live_routes',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagepath),derived_stage_sha256=sha(stagepath),linked_component=str(linked),linked_component_bytes=gate['resident_code_bytes'],component=str(padded),component_bytes=reserve,component_sha256=sha(padded),heap_start=gate['heap_start'],heap_bytes_reserved=reserve,staging_address=staging,staging_bytes_cleared=clear,native_entry_bytes=40+reserve,symbols={**parent['symbols'],'biwn_native_heap_start':gate['heap_start']},mailbox_symbols=gate['GPU_symbols'],mailbox_start=gate['GPU_address'],mailbox_end=gate['GPU_address']+gate['GPU_bytes'],mailbox_source=gate['GPU_source'],mailbox_source_authorship=gate['GPU_source_authorship'],mailbox_private_reserve_by_entry={'e220':10,'e2b8':10},pool_symbols=gate['pool_symbols'],pool_start=gate['pool_address'],pool_end=gate['pool_address']+gate['pool_bytes'],pool_source=gate['pool_source'],pool_source_authorship=gate['pool_source_authorship'],arena_address=gate['arena_address'],arena_end=gate['arena_end'],arena_slots=102,arena_slot_stride=256,arena_guards_each_end=16,arena_usable_slot_bytes=224,reserved_arena_bytes=gate['reserved_arena_bytes'],free_code_gap_bytes=gate['free_code_gap_bytes'],free_tail_bytes=gate['free_tail_bytes'],free_reserved_bytes=gate['free_code_gap_bytes']+gate['free_tail_bytes'],layout_relocations=gate['layout_relocations'],patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,latest_added_native_bytes=gate['resident_code_bytes']-parent['linked_component_bytes'],prior_algorithm_bodies_unchanged=True,whole_parent_prefix_byte_identity=False,source=gate['pool_source'],sources=parent['sources']+[gate['pool_source'],gate['GPU_source']],final_component_gate=str(out/'final-component.json'),final_component_gate_sha256=sha(out/'final-component.json'),game_frames=0,gameplay_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False,new_training=False,new_predictions=0,new_local_code_adopted=True,heap_layout_unchanged=False,staging_layout_unchanged=False,scope=__doc__)
 inputs=[Path(__file__),linked,padded,stagepath,manifest,out/'parent-build.json',out/'final-component.json'];state['source_sha256']={str(p):sha(p)for p in inputs};save(out/'protocol.json',state);save(V/'native-task-pool-arena-disc-build-current.json',state);print(json.dumps({k:state[k]for k in ['status','linked_component_bytes','component_bytes','reserved_arena_bytes','heap_start','staging_address']}))
if __name__=='__main__':main()
