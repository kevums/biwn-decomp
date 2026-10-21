"""Append the final-address137E0source; keep reservation/heap/prior bytes fixed."""
import os,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-actor-initialize-disc-build-current.json';parent=read(bp);gp=v/'native-sprite-create-linked-current.json';gate=read(gp);jp=v/'native-actor-triple-current.json';joint=read(jp);np=v/'native-sprite-create-negatives-current.json';neg=read(np)
 assert gate['status']=='terminal_original_ABI_sprite_create_pass'and gate['cases']==1228 and gate['code_address']==0x164018 and len(gate['original_sites'])==184
 assert joint['status']=='terminal_three_original_ABI_roots_pass'and joint['cases']==2084 and joint['max_private_depth']==630
 assert neg['status']=='terminal_native_sprite_create_four_negatives_rejected'and len(neg['controls'])==4
 for obj in [gate,joint,neg]:
  for p,h in obj['source_sha256'].items():assert sha(p)==h,p
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256'];old=Path(parent['linked_component']).read_bytes();code=Path(gate['binary']).read_bytes();assert len(old)==21080 and len(code)==2180 and parent['resident_address']+len(old)==gate['code_address']
 out=ROOT/'builds/BIWN-native-sprite-create'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 for src,name in [(bp,'parent-build.json'),(gp,'final-component.json'),(jp,'joint-proof.json'),(np,'negative-proof.json')]:shutil.copy2(src,out/name)
 linked=out/'resident-linked.bin';linked.write_bytes(old+code);padded=out/'resident-padded.bin';padded.write_bytes(linked.read_bytes()+bytes(parent['component_bytes']-linked.stat().st_size));assert linked.stat().st_size==23260 and padded.stat().st_size==24512
 stage=bytearray(Path(parent['derived_stage']).read_bytes());changes=[]
 def patch(a,before,after,reason):
  at=a-0x4000;assert len(before)==len(after)and stage[at:at+len(before)]==before;stage[at:at+len(after)]=after;changes.append(dict(address=hex(a),original=before.hex(),replacement=after.hex(),reason=reason))
 patch(parent['staging_address']+40+len(old),bytes(len(code)),code,'Append final-address137E0source and original-facing ABI within unchanged checked reservation.')
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();target=gate['symbols']['biwn_native_sprite_create'];patch(0x137e0,baseline[0x137e0:0x137e8],b'\x4e\xf9'+target.to_bytes(4,'big')+b'\x4e\x71','Redirect137E0entry; preserve original inline callback data.')
 stagefile=out/'mainstage-native-sprite-create.bin';stagefile.write_bytes(stage)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-sprite-create-experimental.cdi';copy=subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],capture_output=True,text=True)
 if copy.returncode:shutil.copyfile(parent['derived_disc'],disc)
 from extract_biwn_stage import swap16
 with disc.open('r+b')as f:
  for row in changes:
   at=offset+int(row['address'],16)-0x4000;a=bytes.fromhex(row['original']);b=bytes.fromhex(row['replacement']);f.seek(at);assert f.read(len(a))==swap16(a);f.seek(at);f.write(swap16(b))
  f.flush();os.fsync(f.fileno());f.seek(offset);assert swap16(f.read(len(stage)))==stage
 intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in changes];pos=changed=0
 with Path(parent['derived_disc']).open('rb')as a,disc.open('rb')as b:
  while True:
   left,right=a.read(1048576),b.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changed+=1
   pos+=len(left)
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256'];manifest=out/'stage-patches.json';save(manifest,dict(patches=read(parent['patch_manifest'])['patches']+changes,delta_patches=changes,parent=str(out/'parent-build.json')))
 returns={}
 for name,entry in [('position',0x105da),('allocate',0x152a2),('decode',0xe2b8)]:
  pattern=b'\x4e\xb9'+entry.to_bytes(4,'big');assert code.count(pattern)==1;returns[name]=gate['code_address']+code.index(pattern)+6
 state=dict(parent);state.update(status='terminal_native_sprite_create_disc_built_pending_startup_context_gameplay',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),linked_component=str(linked),linked_component_bytes=23260,component=str(padded),component_bytes=24512,component_sha256=sha(padded),actor_initialize_component_gate=parent['component_gate'],component_gate=str(out/'final-component.json'),component_gate_sha256=sha(out/'final-component.json'),sprite_create_start=gate['code_address'],sprite_create_end=gate['code_address']+len(code),sprite_create_entry=target,sprite_create_return=gate['symbols']['biwn_native_sprite_create_return'],sprite_create_helper_returns=returns,symbols={**parent['symbols'],**gate['symbols']},patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,sprite_create_integrated=True,semantic_code_bytes=2180,appended_bytes=2180,parent_resident_prefix_byte_identical=True,entry_cases=0,linked_native_cases=1228,linked_changing_cases=0,game_frames=0,default_promoted=False,whole_game_complete=False,source=str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/sprite-create-reference.c'),scope=__doc__+' Startup/context/task/live validation pending. No new model code adoption or weight updates.',source_sha256={str(p):sha(p)for p in [Path(__file__),out/'parent-build.json',out/'final-component.json',out/'joint-proof.json',out/'negative-proof.json',Path(gate['binary']),Path(gate['ELF']),linked,padded,stagefile,manifest]})
 save(out/'protocol.json',state);save(v/'native-sprite-create-disc-build-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=23260,reserve=24512,free=1252,delta_CDI_changed_bytes=changed)))
if __name__=='__main__':main()
