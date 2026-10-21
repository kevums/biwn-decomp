"""Add both complete local GPU command wrappers to a separate experimental disc.
Reserve grows512bytes; staging moves512earlier, trailerFE200 preserved.
No keyboard-preview promotion or game-frame/hardware proof here.
"""
import json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 parent=read(V/'native-actor-direction-disc-build-current.json');gate=read(V/'native-gpu-mailbox-final-current.json');assert gate['cases']==2492 and gate['resident_bytes']==31538 and gate['binary_bytes']==702
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256']and sha(parent['component'])==parent['component_sha256'];out=ROOT/'builds/BIWN-native-gpu-mailbox'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name,obj in [('parent-build.json',parent),('mailbox-component.json',gate)]:save(out/name,obj)
 reserve=gate['reserve_bytes'];staging=gate['staging_address'];clear=gate['staging_clear_bytes'];source_dir=Path(gate['directory']);linked=out/'resident-linked.bin';padded=out/'resident-padded.bin';linked.write_bytes((source_dir/'resident-linked.bin').read_bytes());padded.write_bytes((source_dir/'resident-padded.bin').read_bytes());assert len(linked.read_bytes())==31538 and len(padded.read_bytes())==31616
 stage=bytearray(Path(parent['derived_stage']).read_bytes());before=bytes(stage);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);original_path=session/'nextstage-68000-candidate.bin';original=original_path.read_bytes();assert not any(original[staging-0x4000:0xfe200-0x4000])and not any(stage[staging-0x4000:parent['staging_address']-0x4000]);changes=[]
 def patch(address,replacement,reason):
  at=address-0x4000;expected=bytes(stage[at:at+len(replacement)]);stage[at:at+len(replacement)]=replacement;changes.append(dict(address=hex(address),original=expected.hex(),replacement=replacement.hex(),reason=reason))
 loader=bytearray(stage[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]);assert loader[24:26]==bytes.fromhex('303c')and int.from_bytes(loader[26:28],'big')==parent['component_bytes']//2-1;loader[26:28]=(reserve//2-1).to_bytes(2,'big')
 patch(0x4000,b'\x4e\xf9'+staging.to_bytes(4,'big'),'Relocate staging entry for512byte larger resident reserve.')
 patch(staging,bytes(loader)+padded.read_bytes()+bytes(clear-40-reserve),'Relocated resident payload/clear;trailer boundary unchanged.')
 for entry,symbol in [(0xe220,'biwn_native_gpu_submit_4320'),(0xe2b8,'biwn_native_gpu_submit_4b00')]:
  assert before[entry-0x4000:entry+6-0x4000]==original[entry-0x4000:entry+6-0x4000]
  patch(entry,b'\x4e\xf9'+gate['symbols'][symbol].to_bytes(4,'big'),'Redirect complete CPU command wrapper to checked unchanged local repair; actual E098 retained.')
 assert stage[0xfe200-0x4000:]==before[0xfe200-0x4000:]==original[0xfe200-0x4000:]
 stagepath=out/'mainstage-native-mailbox.bin';stagepath.write_bytes(stage);disc=out/'BIWN-23-native-mailbox-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
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
 state=dict(parent);state.update(status='terminal_native_gpu_mailbox_disc_built_pending_layout_startup_gameplay',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagepath),derived_stage_sha256=sha(stagepath),linked_component=str(linked),linked_component_bytes=31538,component=str(padded),component_bytes=reserve,component_sha256=sha(padded),heap_start=gate['heap_start'],heap_bytes_reserved=reserve,staging_address=staging,staging_bytes_cleared=clear,native_entry_bytes=40+reserve,symbols={**parent['symbols'],'biwn_native_heap_start':gate['heap_start']},mailbox_symbols=gate['symbols'],mailbox_start=gate['code_address'],mailbox_end=gate['code_address']+gate['binary_bytes'],mailbox_source=gate['source'],mailbox_component_gate=str(out/'mailbox-component.json'),mailbox_component_gate_sha256=sha(out/'mailbox-component.json'),mailbox_source_authorship=gate['source_authorship'],free_reserved_bytes=78,layout_relocations=gate['layout_relocations'],patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,latest_added_native_bytes=704,whole_parent_prefix_byte_identity=False,prior_algorithm_bodies_unchanged=True,source=gate['source'],sources=parent['sources']+[gate['source']],game_frames=0,gameplay_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False,new_training=False,new_local_code_adopted=True,scope=__doc__)
 inputs=[Path(__file__),linked,padded,stagepath,manifest,out/'parent-build.json',out/'mailbox-component.json'];state['source_sha256']={str(p):sha(p)for p in inputs};save(out/'protocol.json',state);save(V/'native-gpu-mailbox-disc-build-current.json',state);print(json.dumps({k:state[k]for k in ['status','linked_component_bytes','component_bytes','heap_start','staging_address']}))
if __name__=='__main__':main()
