"""Append final-address13C9Ato checked shifted-staging layout; live context pending."""
import os,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'actor-move-layout-materialized-current.json';b=read(bp);gp=v/'native-actor-move-linked-current.json';g=read(gp);proofs=[read(v/n)for n in ['actor-move-layout-startup-heap-initialize-current.json','actor-move-layout-heap-operations-current.json','actor-move-layout-capacity-witness-current.json','native-actor-move-negatives-current.json']]
 assert g['cases']==2624 and len(g['original_sites'])==192 and g['code_address']==0x16489c and g['binary_bytes']==2960
 assert proofs[0]['startup_cases']==96 and proofs[0]['heap_initialize_cases']==192 and proofs[1]['native_cases']==proofs[1]['ordered_cases']==3392 and proofs[2]['cases']==36 and len(proofs[3]['controls'])==4
 for x in [g,*proofs]:
  for p,h in x['source_sha256'].items():assert sha(p)==h,p
 assert sha(b['derived_disc'])==b['derived_disc_sha256'];old=Path(b['linked_component']).read_bytes();code=Path(g['binary']).read_bytes();assert len(old)==23260 and b['resident_address']+len(old)==g['code_address']
 out=ROOT/'builds/BIWN-native-actor-move'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(bp,out/'parent-build.json');shutil.copy2(gp,out/'final-component.json')
 linked=out/'resident-linked.bin';linked.write_bytes(old+code);padded=out/'resident-padded.bin';padded.write_bytes(linked.read_bytes()+bytes(b['component_bytes']-linked.stat().st_size));assert linked.stat().st_size==26220
 stage=bytearray(Path(b['derived_stage']).read_bytes());before_stage=bytes(stage);changes=[]
 def patch(a,before,after,reason):
  at=a-0x4000;assert len(before)==len(after)and stage[at:at+len(before)]==before;stage[at:at+len(after)]=after;changes.append(dict(address=hex(a),original=before.hex(),replacement=after.hex(),reason=reason))
 patch(b['staging_address']+40+len(old),bytes(len(code)),code,'Append final-address13C9A C and original-facing ABI within28544reservation.')
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();target=g['symbols']['biwn_native_actor_move'];patch(0x13c9a,baseline[0x13c9a:0x13ca2],b'\x4e\xf9'+target.to_bytes(4,'big')+b'\x4e\x71','Redirect original13C9Aentry; actual helper targets retained.')
 assert stage[0xfe000-0x4000:]==before_stage[0xfe000-0x4000:]
 stagefile=out/'mainstage-native-actor-move.bin';stagefile.write_bytes(stage);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-actor-move-experimental.cdi';p=subprocess.run(['/bin/cp','-c',b['derived_disc'],str(disc)],capture_output=True,text=True)
 if p.returncode:shutil.copyfile(b['derived_disc'],disc)
 from extract_biwn_stage import swap16
 with disc.open('r+b')as f:
  for row in changes:
   at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['original']);f.seek(at);assert f.read(len(before))==swap16(before);f.seek(at);f.write(swap16(bytes.fromhex(row['replacement'])))
  f.flush();os.fsync(f.fileno());f.seek(offset);assert swap16(f.read(len(stage)))==stage
 intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in changes];pos=changed=0
 with Path(b['derived_disc']).open('rb')as a,disc.open('rb')as c:
  while True:
   left,right=a.read(1048576),c.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changed+=1
   pos+=len(left)
 assert sha(b['derived_disc'])==b['derived_disc_sha256'];manifest=out/'stage-patches.json';save(manifest,dict(patches=read(b['patch_manifest'])['patches']+changes,delta_patches=changes,parent=str(out/'parent-build.json')));returns={}
 for name,entry in [('direction',0x13440),('submit',0xe220),('outdoor',0x13b5a),('indoor',0x13bb0)]:
  pattern=b'\x4e\xb9'+entry.to_bytes(4,'big');assert code.count(pattern)==1;returns[name]=g['code_address']+code.index(pattern)+6
 state=dict(b);state.update(status='terminal_native_actor_move_disc_built_pending_context_startup_gameplay',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),linked_component=str(linked),linked_component_bytes=26220,component=str(padded),component_sha256=sha(padded),sprite_create_component_gate=b['component_gate'],component_gate=str(out/'final-component.json'),component_gate_sha256=sha(out/'final-component.json'),actor_move_start=g['code_address'],actor_move_end=g['code_address']+len(code),actor_move_entry=target,actor_move_return=g['symbols']['biwn_native_actor_move_return'],actor_move_helper_returns=returns,symbols={**b['symbols'],**g['symbols']},patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,movement_integrated=True,semantic_code_bytes=2960,appended_bytes=2960,parent_resident_prefix_byte_identical=True,source=str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-move-reference.c'),game_frames=0,default_promoted=False,whole_game_complete=False,scope=__doc__,source_sha256={str(p):sha(p)for p in [Path(__file__),out/'parent-build.json',out/'final-component.json',Path(g['binary']),Path(g['ELF']),linked,padded,stagefile,manifest]});save(out/'protocol.json',state);save(v/'native-actor-move-disc-build-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=26220,reserve=b['component_bytes'],heap=hex(b['heap_start']),changed_bytes=changed)))
if __name__=='__main__':main()
