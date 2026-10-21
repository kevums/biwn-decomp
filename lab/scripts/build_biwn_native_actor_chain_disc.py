"""Replace movement/collision wrappers with the qualified shared C call chain.

Preserve the 23260-byte native prefix, reservation, heap floor and loader layout.
This new disc remains a development image until startup and fresh gameplay pass.
"""
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification'
    parent=read(v/'native-actor-collision-disc-build-current.json')
    gate=read(v/'native-actor-chain-final-current.json')
    contexts=read(v/'actor-chain-contexts-current.json')
    defects=read(v/'actor-chain-source-defects-current.json')
    assert gate['collision_cases']==5120 and gate['movement_cases']==2560 and gate['code_address']==0x16489c
    assert contexts['cases']==7680 and contexts['completed']==15360 and contexts['max_native_private_depth']==564 and contexts['minimum_headroom']==354
    assert len(contexts['negative_controls'])==5 and len(defects['controls'])==2
    for obj in [gate,contexts,defects]:
        for p,h in obj['source_sha256'].items():assert sha(p)==h,p
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256'] and sha(parent['component'])==parent['component_sha256']
    old=Path(parent['component']).read_bytes();code=Path(gate['binary']).read_bytes()
    assert len(code)==5188 and parent['resident_address']+23260==gate['code_address']
    linked=old[:23260]+code
    assert len(linked)==28448 and len(old)==parent['component_bytes']==28544
    padded=linked+bytes(len(old)-len(linked))
    out=ROOT/'builds/BIWN-native-actor-chain'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for name,value in [('parent-build.json',parent),('final-component.json',gate),('context-gate.json',contexts),('source-defects.json',defects)]:save(out/name,value)
    linked_path=out/'resident-linked.bin';linked_path.write_bytes(linked)
    padded_path=out/'resident-padded.bin';padded_path.write_bytes(padded)
    stage=bytearray(Path(parent['derived_stage']).read_bytes());before_stage=bytes(stage);changes=[]
    def patch(a,before,after,reason):
        offset=a-0x4000;assert len(before)==len(after)and stage[offset:offset+len(before)]==before
        stage[offset:offset+len(after)]=after;changes.append(dict(address=hex(a),original=before.hex(),replacement=after.hex(),reason=reason))
    patch(parent['staging_address']+40+23260,old[23260:],padded[23260:],'Replace movement/collision tail with shared C-ABI chain; keep reservation and heap floor.')
    roots={0x13c9a:('biwn_native_actor_move',8),0x13b5a:('biwn_native_actor_collision_outdoor',8),0x13bb0:('biwn_native_actor_collision_indoor',6)}
    for entry,(name,width)in roots.items():
        before=before_stage[entry-0x4000:entry-0x4000+width]
        after=b'\x4e\xf9'+gate['symbols'][name].to_bytes(4,'big')+(b'\x4e\x71'if width==8 else b'')
        patch(entry,before,after,'Bind public root to shared-context C chain; internal movement/collision uses C ABI.')
    assert stage[0xfe000-0x4000:]==before_stage[0xfe000-0x4000:]
    stage_path=out/'mainstage-native-actor-chain.bin';stage_path.write_bytes(stage)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
    disc=out/'BIWN-23-native-actor-chain-experimental.cdi'
    subprocess.run(['/bin/cp','-c',parent['derived_disc'],str(disc)],check=True,capture_output=True)
    with disc.open('r+b')as stream:
        for row in changes:
            at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['original']);stream.seek(at);assert stream.read(len(before))==swap16(before)
            stream.seek(at);stream.write(swap16(bytes.fromhex(row['replacement'])))
        stream.flush();os.fsync(stream.fileno());stream.seek(offset);assert swap16(stream.read(len(stage)))==stage
    intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in changes]
    pos=changed=0
    with Path(parent['derived_disc']).open('rb')as left,disc.open('rb')as right:
        while True:
            a,b=left.read(1048576),right.read(1048576);assert len(a)==len(b)
            if not a:break
            if a!=b:
                for i,(x,y)in enumerate(zip(a,b)):
                    if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changed+=1
            pos+=len(a)
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
    original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    assert sha(original)=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    manifest=out/'stage-patches.json';save(manifest,dict(patches=read(parent['patch_manifest'])['patches']+changes,delta_patches=changes,parent=str(out/'parent-build.json')))
    syms=gate['symbols'];addresses=sorted(set(syms.values())|{gate['code_address']+len(code)});helpers=[]
    for name,target in [('biwn_native_actor_move_direction_capture',0x13440),('biwn_native_actor_move_submit_capture',0xe220),('biwn_native_actor_collision_outside_index_capture',0x1039c),('biwn_native_actor_collision_outside_scan_capture',0x102c4),('biwn_native_actor_collision_inside_outside_capture',0x1028e),('biwn_native_actor_collision_inside_index_capture',0x10652),('biwn_actor_chain_outside_index_capture',0x1039c),('biwn_actor_chain_outside_scan_capture',0x102c4),('biwn_actor_chain_inside_outside_capture',0x1028e),('biwn_actor_chain_inside_index_capture',0x10652)]:
        start=syms[name];end=next(a for a in addresses if a>start);body=code[start-gate['code_address']:end-gate['code_address']];pattern=b'\x4e\xb9'+target.to_bytes(4,'big');assert body.count(pattern)==1
        helpers.append(dict(name=name,entry=start,target=target,return_PC=start+body.index(pattern)+6))
    state=dict(parent)
    state.update(status='terminal_native_actor_chain_disc_built_pending_startup_gameplay',directory=str(out),parent_build=str(out/'parent-build.json'),parent_build_sha256=sha(out/'parent-build.json'),derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stage_path),derived_stage_sha256=sha(stage_path),linked_component=str(linked_path),linked_component_bytes=len(linked),component=str(padded_path),component_sha256=sha(padded_path),component_gate=str(out/'final-component.json'),component_gate_sha256=sha(out/'final-component.json'),symbols={**{k:a for k,a in parent['symbols'].items()if a<gate['code_address']},**syms},actor_chain_start=gate['code_address'],actor_chain_end=gate['code_address']+len(code),actor_chain_private_reserve=320,actor_chain_context_bytes=80,actor_chain_helpers=helpers,actor_chain_virtual_collision_entry=syms['biwn_actor_chain_collision_call'],actor_chain_virtual_collision_return=syms['biwn_actor_chain_collision_call_return'],actor_move_start=gate['code_address'],actor_move_end=gate['code_address']+len(code),actor_move_entry=syms['biwn_native_actor_move'],actor_move_return=syms['biwn_native_actor_move_return'],actor_move_helper_returns={label:next(row['return_PC']for row in helpers if row['target']==target)for label,target in [('direction',0x13440),('submit',0xe220)]},collision_entries={label:syms['biwn_native_actor_collision_'+label]for label in ['outdoor','indoor']},collision_returns={label:syms['biwn_native_actor_collision_'+label+'_return']for label in ['outdoor','indoor']},free_reserved_bytes=len(old)-len(linked),semantic_code_bytes=len(code),replaced_native_bytes=5120,new_native_bytes=5188,parent_resident_prefix_bytes_unchanged=23260,delta_CDI_changed_bytes=changed,patch_manifest=str(manifest),patch_manifest_sha256=sha(manifest),sources=[str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k'/name)for name in ['actor-chain-move.c','actor-chain-collision.c']],game_frames=0,whole_game_complete=False,default_promoted=False,scope=__doc__)
    paths=[Path(__file__),linked_path,padded_path,stage_path,manifest,*[out/name for name in ['parent-build.json','final-component.json','context-gate.json','source-defects.json']]]
    state['source_sha256']={str(p):sha(p)for p in paths}
    save(out/'protocol.json',state);save(v/'native-actor-chain-disc-build-current.json',state)
    print(json.dumps(dict(status=state['status'],resident_bytes=len(linked),free_bytes=state['free_reserved_bytes'],changed_CDI_bytes=changed)))


if __name__=='__main__':main()
