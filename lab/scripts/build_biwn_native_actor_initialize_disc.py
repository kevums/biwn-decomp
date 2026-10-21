"""Append tested134DCto checked24512layout; retain distinct layout-only control."""
import os,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';lp=v/'actor-initializer-layout-materialized-current.json';layout=read(lp);hp=v/'actor-layout-heap-operations-current.json';heap=read(hp);sp=v/'actor-layout-startup-heap-initialize-current.json';startup=read(sp);fp=v/'native-actor-initialize-final-current.json';gate=read(fp)
 assert heap['status']=='terminal_relocated_heap_native_blitter_and_ordered_pass'and heap['native_cases']==heap['ordered_cases']==3392
 assert startup['startup_cases']==96 and startup['heap_initialize_cases']==192 and gate['cases']==1024 and gate['code_address']==0x1639c4
 for obj in [heap,startup,gate]:
  for p,h in obj['source_sha256'].items():assert sha(p)==h,p
 assert sha(layout['derived_disc'])==layout['derived_disc_sha256'];old=Path(layout['linked_component']).read_bytes();code=Path(gate['binary']).read_bytes();assert len(old)==19460 and len(code)==1620 and layout['resident_address']+len(old)==gate['code_address']
 out=ROOT/'builds/BIWN-native-actor-initialize'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);shutil.copy2(lp,out/'parent-build.json');shutil.copy2(fp,out/'final-component.json')
 linked=out/'resident-linked.bin';linked.write_bytes(old+code);padded=out/'resident-padded.bin';padded.write_bytes(linked.read_bytes()+bytes(layout['component_bytes']-linked.stat().st_size));assert linked.stat().st_size==21080 and padded.stat().st_size==24512
 stage=bytearray(Path(layout['derived_stage']).read_bytes());changes=[]
 def patch(a,before,after,reason):
  at=a-0x4000;assert len(before)==len(after)and stage[at:at+len(before)]==before;stage[at:at+len(after)]=after;changes.append(dict(address=hex(a),original=before.hex(),replacement=after.hex(),reason=reason))
 patch(layout['staging_address']+40+len(old),bytes(len(code)),code,'Append final-address134DCsource and adapter within the newly checked reservation.')
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();target=gate['symbols']['biwn_native_actor_initialize'];patch(0x134dc,baseline[0x134dc:0x134e4],b'\x4e\xf9'+target.to_bytes(4,'big')+b'\x4e\x71','Redirect complete original134DCentry; original inline callback table remains unchanged.')
 stagefile=out/'mainstage-native-actor-initialize.bin';stagefile.write_bytes(stage)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset'];disc=out/'BIWN-23-native-actor-initialize-experimental.cdi';copy=subprocess.run(['/bin/cp','-c',layout['derived_disc'],str(disc)],capture_output=True,text=True)
 if copy.returncode:shutil.copyfile(layout['derived_disc'],disc)
 from extract_biwn_stage import swap16
 with disc.open('r+b')as f:
  for row in changes:
   at=offset+int(row['address'],16)-0x4000;a=bytes.fromhex(row['original']);b=bytes.fromhex(row['replacement']);f.seek(at);assert f.read(len(a))==swap16(a);f.seek(at);f.write(swap16(b))
  f.flush();os.fsync(f.fileno());f.seek(offset);assert swap16(f.read(len(stage)))==stage
 intervals=[(offset+int(r['address'],16)-0x4000,offset+int(r['address'],16)-0x4000+len(bytes.fromhex(r['original'])))for r in changes];pos=changed=0
 with Path(layout['derived_disc']).open('rb')as a,disc.open('rb')as b:
  while True:
   left,right=a.read(1048576),b.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changed+=1
   pos+=len(left)
 assert sha(layout['derived_disc'])==layout['derived_disc_sha256']
 manifest=out/'stage-patches.json';save(manifest,dict(patches=read(layout['patch_manifest'])['patches']+changes,delta_patches=changes,parent=str(out/'parent-build.json')))
 returns={}
 for name,entry in [('outside',0x102c4),('inside',0x10520),('task',0xdf6c)]:
  opcode=b'\x4e\xb9'+entry.to_bytes(4,'big');assert code.count(opcode)==1;returns[name]=gate['code_address']+code.index(opcode)+6
 state=dict(layout);state.update(status='terminal_native_actor_initialize_disc_built_pending_joint_startup_gameplay',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),linked_component=str(linked),linked_component_bytes=21080,component=str(padded),component_bytes=24512,component_sha256=sha(padded),actor_dispatch_component_gate=layout['component_gate'],component_gate=str(Path(gate['directory'])/'protocol.json'),component_gate_sha256=sha(Path(gate['directory'])/'protocol.json'),actor_initialize_start=gate['code_address'],actor_initialize_end=gate['code_address']+len(code),actor_initialize_entry=target,actor_initialize_return=gate['symbols']['biwn_native_actor_initialize_return'],actor_initialize_helper_returns=returns,symbols={**layout['symbols'],**gate['symbols'],'biwn_native_heap_start':layout['heap_start']},patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,initializer_integrated=True,semantic_code_bytes=1620,appended_bytes=1620,parent_resident_prefix_byte_identical=True,entry_cases=0,linked_native_cases=1024,linked_changing_cases=0,game_frames=0,default_promoted=False,whole_game_complete=False,scope='Coordinator134DCsource/ABI appended to separately checked larger reservation; final-address1024cases use common parent compiled10520. Full live original-helper/canary/gameplay not yet established. No new logical-function count or model/training claim.',source_sha256={str(p):sha(p)for p in [Path(__file__),out/'parent-build.json',out/'final-component.json',hp,sp,Path(gate['binary']),Path(gate['ELF']),linked,padded,stagefile,manifest]})
 save(out/'protocol.json',state);save(v/'native-actor-initialize-disc-build-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=21080,reserve=24512,heap=hex(state['heap_start']),delta_CDI_changed_bytes=changed)))

if __name__=='__main__':main()
