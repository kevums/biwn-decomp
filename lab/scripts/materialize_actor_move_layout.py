"""Materialize layout-only28544reservation with relocated staging; keep Atari trailer."""
import os,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 pp=ROOT/'verification/actor-move-layout-plan-current.json';plan=read(pp);bp=ROOT/'verification/native-sprite-create-disc-build-current.json';b=read(bp);assert plan['status']=='terminal_read_only_actor_move_layout_plan_no_changes'
 for p,h in plan['source_sha256'].items():assert sha(p)==h,p
 assert sha(b['derived_disc'])==b['derived_disc_sha256'];old=Path(b['linked_component']).read_bytes();code=bytearray(old);relocations=[]
 def change(at,before,after,reason):
  assert len(before)==len(after)and code[at:at+len(before)]==before;code[at:at+len(after)]=after;relocations.append(dict(resident_address=hex(b['resident_address']+at),old=before.hex(),new=after.hex(),reason=reason))
 for row in plan['heap_operands']:change(int(row['operand'],16)-b['resident_address'],int(row['old'],16).to_bytes(4,'big'),int(row['new'],16).to_bytes(4,'big'),'Raise heap floor/initial header boundary to165D40.')
 change(0x16,(0xf8000).to_bytes(4,'big'),(0xf7000).to_bytes(4,'big'),'Move staging clear base down4KB, retaining trailer.')
 change(0x1c,bytes.fromhex('2fff'),bytes.fromhex('37ff'),'Clear28672stagingbytes atF7000..FE000.')
 assert len(code)==23260 and len(relocations)==9
 out=ROOT/'builds/BIWN-actor-move-layout'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(bp,out/'parent-build.json');shutil.copy2(pp,out/'layout-plan.json');linked=out/'resident-linked.bin';linked.write_bytes(code);padded=out/'resident-padded.bin';reserve=plan['proposed_reserve'];padded.write_bytes(code+bytes(reserve-len(code)))
 stage=bytearray(Path(b['derived_stage']).read_bytes());original=bytes(stage);oldbase=b['staging_address'];newbase=0xf7000;clear=28672;loader=bytearray(stage[oldbase-0x4000:oldbase-0x4000+40]);assert loader[24:28]==bytes.fromhex('303c2fdf');loader[26:28]=int(plan['staging']['new_copy_WORD'],16).to_bytes(2,'big');newwindow=bytes(loader)+padded.read_bytes()+bytes(clear-40-reserve);assert len(newwindow)==clear;changes=[]
 def patch(a,before,after,reason):
  at=a-0x4000;assert len(before)==len(after)and stage[at:at+len(before)]==before;stage[at:at+len(after)]=after;changes.append(dict(address=hex(a),original=before.hex(),replacement=after.hex(),reason=reason))
 patch(0x4000,stage[:6],b'\x4e\xf9'+newbase.to_bytes(4,'big'),'Move initial staging entry toF7000.')
 patch(newbase,original[newbase-0x4000:0xfe000-0x4000],newwindow,'Relocate full staging payload;28544reservation/28672clear, preserve Atari trailer atFE520.')
 assert stage[0xfe000-0x4000:]==original[0xfe000-0x4000:]
 stagefile=out/'mainstage-layout28544.bin';stagefile.write_bytes(stage);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset'];disc=out/'BIWN-23-layout28544-original-movement.cdi';p=subprocess.run(['/bin/cp','-c',b['derived_disc'],str(disc)],capture_output=True,text=True)
 if p.returncode:shutil.copyfile(b['derived_disc'],disc)
 from extract_biwn_stage import swap16
 with disc.open('r+b')as f:
  for row in changes:
   f.seek(offset+int(row['address'],16)-0x4000);before=bytes.fromhex(row['original']);assert f.read(len(before))==swap16(before);f.seek(offset+int(row['address'],16)-0x4000);f.write(swap16(bytes.fromhex(row['replacement'])))
  f.flush();os.fsync(f.fileno());f.seek(offset);assert swap16(f.read(len(stage)))==stage
 intervals=[(offset+int(x['address'],16)-0x4000,offset+int(x['address'],16)-0x4000+len(bytes.fromhex(x['original'])))for x in changes];pos=changed=0
 with Path(b['derived_disc']).open('rb')as a,disc.open('rb')as c:
  while True:
   left,right=a.read(1048576),c.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changed+=1
   pos+=len(left)
 assert sha(b['derived_disc'])==b['derived_disc_sha256'];manifest=out/'stage-patches.json';save(manifest,dict(patches=read(b['patch_manifest'])['patches']+changes,delta_patches=changes,resident_relocations=relocations,parent=str(out/'parent-build.json')))
 state=dict(b);state.update(status='terminal_actor_move_layout28544_materialized_pending_checks',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stagefile),derived_stage_sha256=sha(stagefile),linked_component=str(linked),linked_component_bytes=23260,component=str(padded),component_bytes=reserve,component_sha256=sha(padded),heap_start=int(plan['proposed_heap_floor'],16),heap_bytes_reserved=reserve,staging_address=newbase,staging_bytes_cleared=clear,native_entry_bytes=40+reserve,symbols={**b['symbols'],'biwn_native_heap_start':int(plan['proposed_heap_floor'],16)},patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),delta_CDI_changed_bytes=changed,layout_relocations=relocations,movement_integrated=False,semantic_code_bytes=0,game_frames=0,default_promoted=False,whole_game_complete=False,trailer_preserved=True,scope=__doc__+' Heap/startup/final movement/live checks pending; not published as latest testeddisc.',source_sha256={str(p):sha(p)for p in [Path(__file__),out/'parent-build.json',out/'layout-plan.json',linked,padded,stagefile,manifest]});save(out/'protocol.json',state);save(ROOT/'verification/actor-move-layout-materialized-current.json',state);print(json.dumps(dict(status=state['status'],staging=hex(newbase),reserve=reserve,heap=hex(state['heap_start']),delta_bytes=changed,trailer_preserved=True)))
if __name__=='__main__':main()
