"""Materialize a new experimental loader/heap layout; no default promotion."""
import json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-actor-dispatch-gap320-disc-build-current.json';parent=read(bp);pp=v/'actor-initializer-layout-plan-current.json';plan=read(pp)
 assert plan['status']=='terminal_read_only_initializer_layout_plan_no_changes'and not plan['changes_made']
 for p,h in plan['source_sha256'].items():assert sha(p)==h,p
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256']and sha(parent['derived_stage'])==parent['derived_stage_sha256']
 out=ROOT/'builds/BIWN-actor-initializer-layout'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);shutil.copy2(bp,out/'parent-build.json');shutil.copy2(pp,out/'layout-plan.json')
 prefix=bytearray(Path(parent['linked_component']).read_bytes());before_prefix=bytes(prefix)
 for row in plan['heap_floor_operand_relocations']:
  at=int(row['operand_address'],16)-parent['resident_address'];old=int(row['old_value'],16).to_bytes(4,'big');new=int(row['new_value'],16).to_bytes(4,'big');assert prefix[at:at+4]==old;prefix[at:at+4]=new
 assert len(prefix)==19460;reserve=plan['proposed_reserve'];floor=int(plan['proposed_heap_floor'],16)
 linked=out/'resident-layout-linked.bin';linked.write_bytes(prefix);padded=out/'resident-layout-padded.bin';padded.write_bytes(prefix+bytes(reserve-len(prefix)))
 stage=bytearray(Path(parent['derived_stage']).read_bytes());patches=[]
 def patch(address,before,after,reason):
  at=address-0x4000;assert len(before)==len(after)and stage[at:at+len(before)]==before,(hex(address),reason)
  stage[at:at+len(after)]=after;patches.append(dict(address=hex(address),original=before.hex(),replacement=after.hex(),reason=reason))
 source=parent['staging_address']+40;before=bytes(stage[source-0x4000:source-0x4000+reserve]);assert before[:19460]==before_prefix and not any(before[19460:])
 patch(source,before,padded.read_bytes(),'Seven explicit relocated heap operands, enlarged zero-padded reservation; initializer not yet appended.')
 count=plan['loader_count'];patch(int(count['operand_address'],16),int(count['old_WORD'],16).to_bytes(2,'big'),int(count['new_WORD'],16).to_bytes(2,'big'),'Copy24512reserved bytes using12256WORDiterations.')
 stagefile=out/'mainstage-native-layout.bin';stagefile.write_bytes(stage)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset'];disc=out/'BIWN-23-layout24512-original-initializer.cdi'
 clone=subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],capture_output=True,text=True)
 if clone.returncode:shutil.copyfile(parent['derived_disc'],disc)
 from extract_biwn_stage import swap16
 with disc.open('r+b')as stream:
  for row in patches:
   at=offset+int(row['address'],16)-0x4000;a=bytes.fromhex(row['original']);b=bytes.fromhex(row['replacement']);stream.seek(at);assert stream.read(len(a))==swap16(a);stream.seek(at);stream.write(swap16(b))
  stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
 intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in patches];position=changed=0
 with Path(parent['derived_disc']).open('rb')as a,disc.open('rb')as b:
  while True:
   left,right=a.read(1048576),b.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changed+=1
   position+=len(left)
 assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
 manifest=out/'stage-patches.json';save(manifest,dict(patches=read(parent['patch_manifest'])['patches']+patches,delta_patches=patches,parent=str(out/'parent-build.json')))
 state=dict(parent);state.update(status='experimental_layout24512_materialized_pending_checks',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),linked_component=str(linked),linked_component_bytes=len(prefix),component=str(padded),component_bytes=reserve,component_sha256=sha(padded),heap_start=floor,heap_bytes_reserved=reserve,native_entry_bytes=40+reserve,source_heap_operand_relocations=plan['heap_floor_operand_relocations'],loader_count_change=count,patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,initializer_integrated=False,entry_cases=0,game_frames=0,default_promoted=False,whole_game_complete=False,original_disc_modified=False,copy_method='APFSclone'if not clone.returncode else'filecopy',source_sha256={str(p):sha(p)for p in [Path(__file__),out/'parent-build.json',out/'layout-plan.json',Path(parent['derived_stage']),Path(parent['linked_component']),linked,padded,stagefile,manifest]})
 state['symbols']={**parent['symbols'],'biwn_native_heap_start':floor}
 save(out/'protocol.json',state);save(v/'actor-initializer-layout-materialized-current.json',state);print(json.dumps(dict(status=state['status'],reserve=reserve,heap=hex(floor),changed_disc_bytes=changed,copy_method=state['copy_method'])))

if __name__=='__main__':main()
