"""Integrate four qualified native navigation roots into a new development disc.
The reservation grows1536bytes. Staging moves1024bytes earlier into original
zero bytes; exact loader/heap/component/live gates remain required afterwards.
Original/parent images are unchanged. This is not a gameplay publication.
"""
import json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 parent=read(V/'native-actor-chain-build-normalized-current.json');gate=read(V/'native-actor-navigation-final-current.json');live=read(V/'actor-chain-integration-reviewed-current.json')
 assert gate['status']=='terminal_native_navigation_final_pass'and gate['cases']==6144 and len(gate['original_sites'])==209 and gate['code_address']==0x165ce0 and gate['binary_bytes']==1428
 assert live['resident_bytes']==28448 and live['live_monitor_pass']
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256']and sha(parent['component'])==parent['component_sha256']
 resident=parent['resident_address'];old=Path(parent['linked_component']).read_bytes();assert len(old)==28448 and resident+len(old)==gate['code_address']
 reserve=30080;floor=resident+reserve;newbase=0xf6c00;clear=0x7600;assert floor==0x166340 and newbase+clear==0xfe200 and clear-40-reserve==88
 stage=bytearray(Path(parent['derived_stage']).read_bytes());before=bytes(stage);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);original_path=session/'nextstage-68000-candidate.bin';original=original_path.read_bytes()
 assert not any(original[newbase-0x4000:0xfe200-0x4000]),'Original staging window contains nonzero source bytes'
 assert not any(stage[newbase-0x4000:parent['staging_address']-0x4000])and not any(stage[0xfe000-0x4000:0xfe200-0x4000])
 out=ROOT/'builds/BIWN-native-actor-navigation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name,obj in [('parent-build.json',parent),('final-component.json',gate),('parent-live-review.json',live)]:save(out/name,obj)
 code=bytearray(old);relocations=[]
 def relocate(at,expected,replacement,reason):
  assert len(expected)==len(replacement)and code[at:at+len(expected)]==expected,(hex(at),expected.hex(),code[at:at+len(expected)].hex())
  code[at:at+len(expected)]=replacement;relocations.append(dict(resident_address=hex(resident+at),old=expected.hex(),new=replacement.hex(),reason=reason))
 for row in parent['layout_relocations'][:7]:
  expected=bytes.fromhex(row['new']);assert len(expected)==4;replacement=(int.from_bytes(expected,'big')+1536).to_bytes(4,'big');relocate(int(row['resident_address'],16)-resident,expected,replacement,'Raise declared heap boundary1536bytes for four native navigation routines.')
 relocate(0x16,(0xf7000).to_bytes(4,'big'),newbase.to_bytes(4,'big'),'Move staging clear start down1024bytes; preserve Atari trailer.')
 relocate(0x1c,(0x37ff).to_bytes(2,'big'),(clear//2-1).to_bytes(2,'big'),'Clear30208bytes throughFE200.')
 nav=Path(gate['binary']).read_bytes();code.extend(nav);assert len(code)==29876 and reserve-len(code)==204
 linked=out/'resident-linked.bin';linked.write_bytes(code);padded=out/'resident-padded.bin';padded.write_bytes(code+bytes(reserve-len(code)))
 loader=bytearray(stage[parent['staging_address']-0x4000:parent['staging_address']-0x4000+40]);assert loader[24:26]==bytes.fromhex('303c')and int.from_bytes(loader[26:28],'big')==parent['component_bytes']//2-1;loader[26:28]=(reserve//2-1).to_bytes(2,'big');window=bytes(loader)+padded.read_bytes()+bytes(clear-40-reserve);changes=[]
 def patch(at,replacement,reason):
  offset=at-0x4000;expected=bytes(stage[offset:offset+len(replacement)]);stage[offset:offset+len(replacement)]=replacement;changes.append(dict(address=hex(at),original=expected.hex(),replacement=replacement.hex(),reason=reason))
 patch(0x4000,b'\x4e\xf9'+newbase.to_bytes(4,'big'),'Relocate initial staging entry.')
 patch(newbase,window,'Relocate full resident staging/copy/clear;30080reservation/30208clear.')
 roots={0xf368:('biwn_native_actor_waypoint',8),0x13f12:('biwn_native_actor_nav_left_entry',6),0x13f7c:('biwn_native_actor_nav_right_entry',6),0x13fea:('biwn_native_actor_nav_front_entry',6)}
 for entry,(name,width)in roots.items():
  at=entry-0x4000;assert before[at:at+width]==original[at:at+width];patch(entry,b'\x4e\xf9'+gate['symbols'][name].to_bytes(4,'big')+(b'\x4e\x71'if width==8 else b''),'Bind original public navigation root to compiled high-level C.')
 assert stage[0xfe200-0x4000:]==before[0xfe200-0x4000:]and stage[0xfe200-0x4000:]==original[0xfe200-0x4000:]
 stagepath=out/'mainstage-native-navigation.bin';stagepath.write_bytes(stage);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-navigation-experimental.cdi';subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True)
 with disc.open('r+b')as f:
  for row in changes:
   at=offset+int(row['address'],16)-0x4000;expected=bytes.fromhex(row['original']);f.seek(at);assert f.read(len(expected))==swap16(expected);f.seek(at);f.write(swap16(bytes.fromhex(row['replacement'])))
  f.flush();os.fsync(f.fileno());f.seek(offset);assert swap16(f.read(len(stage)))==stage
 intervals=[(offset+int(x['address'],16)-0x4000,offset+int(x['address'],16)-0x4000+len(bytes.fromhex(x['original'])))for x in changes];position=changed=0
 with Path(parent['derived_disc']).open('rb')as a,disc.open('rb')as b:
  while True:
   left,right=a.read(1048576),b.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changed+=1
   position+=len(left)
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256'];origdisc=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert sha(origdisc)=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
 manifest=out/'stage-patches.json';save(manifest,dict(parent=str(out/'parent-build.json'),patches=read(parent['patch_manifest'])['patches']+changes,delta_patches=changes,resident_relocations=relocations))
 plan=dict(old_reserve=28544,new_reserve=reserve,additional_reserve=1536,old_floor='0x165d40',new_floor=hex(floor),old_initial_heap=369344,new_initial_heap=0x1c0000-floor,old_staging='0xf7000',new_staging=hex(newbase),clear_bytes=clear,clear_end='0xfe200',original_window_all_zero=True,trailer_unchanged=True,native_bytes=len(nav),new_resident_bytes=len(code),free_reserved_bytes=204,original_heap_semantics_and_runtime_use_still_require_fresh_checks=True);save(out/'layout-plan.json',plan)
 state=dict(parent);state.update(status='terminal_native_navigation_disc_built_pending_layout_startup_gameplay',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagepath),derived_stage_sha256=sha(stagepath),linked_component=str(linked),linked_component_bytes=len(code),component=str(padded),component_bytes=reserve,component_sha256=sha(padded),heap_start=floor,heap_bytes_reserved=reserve,staging_address=newbase,staging_bytes_cleared=clear,native_entry_bytes=40+reserve,symbols={**parent['symbols'],'biwn_native_heap_start':floor},navigation_start=gate['code_address'],navigation_end=gate['code_address']+len(nav),navigation_symbols=gate['symbols'],navigation_entries={hex(entry):gate['symbols'][name]for entry,(name,width)in roots.items()},navigation_returns={hex(entry):gate['symbols'][name+'_return']for entry,(name,width)in roots.items()},navigation_integrated=True,navigation_source=str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-navigation-reference-v2.c'),navigation_source_authorship='Coordinator adaptation; localmodelproposalnotadopted',free_reserved_bytes=reserve-len(code),layout_relocations=relocations,layout_plan=str(out/'layout-plan.json'),patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,component_gate=str(out/'final-component.json'),component_gate_sha256=sha(out/'final-component.json'),game_frames=0,gameplay_verified=False,default_promoted=False,physical_console_verified=False,whole_game_complete=False,new_training=False,new_local_code_adopted=False,parent_resident_prefix_bytes_unchanged=False,scope=__doc__)
 inputs=[Path(__file__),original_path,linked,padded,stagepath,manifest,*[out/x for x in ['parent-build.json','final-component.json','parent-live-review.json','layout-plan.json']]];state['source_sha256']={str(p):sha(p)for p in inputs};save(out/'protocol.json',state);save(V/'native-actor-navigation-disc-build-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=len(code),reserved_bytes=reserve,heap=hex(floor),changed_CDI_bytes=changed)))
if __name__=='__main__':main()
