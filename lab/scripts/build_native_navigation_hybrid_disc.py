"""Replace the verified navigation group with explicitly attributed hybrid C.
Keep the first28448 resident bytes, heap/reserve/staging/loader/trailer unchanged.
Only the navigation tail and four public entry patches change. Fresh startup,
rendered observer qualification and native route/control review remain required.
"""
import json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 parent=read(V/'native-actor-navigation-build-normalized-current.json');gate=read(V/'native-navigation-hybrid-final-current.json');review=read(V/'navigation-hybrid-component-reviewed-current.json')
 assert gate['cases']==6144 and gate['code_address']==0x165ce0 and gate['binary_bytes']==1588 and review['final_group_cases']==6144
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256']and sha(parent['component'])==parent['component_sha256']
 old=Path(parent['component']).read_bytes();prefix=gate['code_address']-parent['resident_address'];payload=Path(gate['binary']).read_bytes();assert prefix==28448 and len(old)==30080
 code=old[:prefix]+payload;assert len(code)==30036;new=code+bytes(len(old)-len(code));assert new[:prefix]==old[:prefix]
 out=ROOT/'builds/BIWN-native-navigation-hybrid'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name,obj in [('parent-build.json',parent),('final-component.json',gate),('hybrid-review.json',review)]:save(out/name,obj)
 linked=out/'resident-linked.bin';linked.write_bytes(code);padded=out/'resident-padded.bin';padded.write_bytes(new)
 stage=bytearray(Path(parent['derived_stage']).read_bytes());before=bytes(stage);changes=[]
 def patch(address,expected,replacement,reason):
  at=address-0x4000;assert len(expected)==len(replacement)and stage[at:at+len(expected)]==expected;stage[at:at+len(expected)]=replacement;changes.append(dict(address=hex(address),original=expected.hex(),replacement=replacement.hex(),reason=reason))
 patch(parent['staging_address']+40+prefix,old[prefix:],new[prefix:],'Replace navigation tail with local13F12draft plus3explicitcoordinatorcorrections; other3roots coordinator.')
 roots={0xf368:('biwn_native_actor_waypoint',8),0x13f12:('biwn_native_actor_nav_left_entry',6),0x13f7c:('biwn_native_actor_nav_right_entry',6),0x13fea:('biwn_native_actor_nav_front_entry',6)}
 for entry,(name,width)in roots.items():patch(entry,before[entry-0x4000:entry-0x4000+width],b'\x4e\xf9'+gate['symbols'][name].to_bytes(4,'big')+(b'\x4e\x71'if width==8 else b''),'Bind public navigation root to final-address hybrid group.')
 assert stage[:6]==before[:6]and stage[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]==before[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]and stage[0xfe200-0x4000:]==before[0xfe200-0x4000:]
 stagepath=out/'mainstage-native-navigation-hybrid.bin';stagepath.write_bytes(stage);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-navigation-hybrid-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True)
 with disc.open('r+b')as f:
  for row in changes:
   at=offset+int(row['address'],16)-0x4000;expected=bytes.fromhex(row['original']);f.seek(at);assert f.read(len(expected))==swap16(expected);f.seek(at);f.write(swap16(bytes.fromhex(row['replacement'])))
  f.flush();os.fsync(f.fileno());f.seek(offset);assert swap16(f.read(len(stage)))==stage
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
 manifest=out/'stage-patches.json';save(manifest,dict(parent=str(out/'parent-build.json'),patches=read(parent['patch_manifest'])['patches']+changes,delta_patches=changes))
 state=dict(parent)
 for key in ['superseded_build_metadata','superseded_build_metadata_sha256','metadata_correction','parent_resident_prefix_bytes_unchanged']:state.pop(key,None)
 state.update(status='terminal_native_navigation_hybrid_disc_built_pending_startup_gameplay',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagepath),derived_stage_sha256=sha(stagepath),linked_component=str(linked),linked_component_bytes=len(code),component=str(padded),component_sha256=sha(padded),component_gate=str(out/'final-component.json'),component_gate_sha256=sha(out/'final-component.json'),navigation_start=gate['code_address'],navigation_end=gate['code_address']+len(payload),navigation_symbols=gate['symbols'],navigation_entries={hex(entry):gate['symbols'][name]for entry,(name,width)in roots.items()},navigation_returns={hex(entry):gate['symbols'][name+'_return']for entry,(name,width)in roots.items()},navigation_source=str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-navigation-hybrid-v1.c'),navigation_source_authorship='Hybrid13F12: localconciseAuthordraft+3explicitcoordinatorcorrections. Other3roots coordinator.',source=str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-navigation-hybrid-v1.c'),sources=parent['sources']+[str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-navigation-hybrid-v1.c'),str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-navigation-left-hybrid-v1.c')],free_reserved_bytes=len(old)-len(code),semantic_code_bytes=len(payload),new_native_bytes=len(payload),replaced_native_bytes=1428,unchanged_parent_prefix_bytes=prefix,inherited_layout_relocations=parent['layout_relocations'],layout_relocations=[],heap_layout_unchanged=True,staging_layout_unchanged=True,patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,game_frames=0,gameplay_verified=False,default_promoted=False,new_training=False,new_local_code_adopted=True,unchanged_local_output_adopted=False,scope=__doc__)
 inputs=[Path(__file__),linked,padded,stagepath,manifest,*[out/x for x in ['parent-build.json','final-component.json','hybrid-review.json']]];state['source_sha256']={str(p):sha(p)for p in inputs};save(out/'protocol.json',state);save(V/'native-navigation-hybrid-disc-build-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=len(code),free_bytes=len(old)-len(code),changed_CDI_bytes=changed)))
if __name__=='__main__':main()
