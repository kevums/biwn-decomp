"""Separate native disc with the existing evidence-backed selector13 repair.

This changes original behavior: source table/constructor say16 frames, while
the preserved mode3 marker groups contain13 frames. It is restoration work,
not a claim that the original program already used13.
"""
import json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
from extract_biwn_stage import swap16
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha

def main():
    out=ROOT/'builds/BIWN-native-Deck-asset-repair-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    bp=V/'native-Deck-coordinate-disc-build-current.json';build=read(bp);assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['derived_stage'])==build['derived_stage_sha256']
    manifest=read(V/'biwn-disc-resources.json');raw=Path(manifest['raw_track_path']);assert sha(raw)==manifest['source_raw_track_sha256'];data=swap16(raw.read_bytes())
    markers=[]
    for group in range(3):
        needle=(0xc000+group).to_bytes(4,'big')*16;at=data.find(needle);assert at>=0 and data.find(needle,at+1)<0
        markers.append(dict(group=group,tag=hex(0xc000+group),offset=at,payload_offset=at+64,payload_bytes=13*8192,payload_sha256=__import__('hashlib').sha256(data[at+64:at+64+13*8192]).hexdigest()))
    assert markers[1]['offset']-markers[0]['offset']==markers[2]['offset']-markers[1]['offset']==13*8192+64
    patches_path=V/'scene-constructor-selector13-inline-generation-current.json';patches=read(patches_path)['patches'];assert [int(p['address'],16)for p in patches]==[0x464a6,0x10ac2]
    stage=bytearray(Path(build['derived_stage']).read_bytes())
    for patch in patches:
        offset=int(patch['address'],16)-0x4000;before=bytes.fromhex(patch['original']);after=bytes.fromhex(patch['replacement']);assert len(before)==len(after)and stage[offset:offset+len(before)]==before
        stage[offset:offset+len(after)]=after
    stage_path=out/'mainstage-native-Deck-asset-repair.bin';stage_path.write_bytes(stage)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);payload_offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']
    disc=out/'BIWN-23-native-Deck-asset-repair-v1-experimental.cdi';p=subprocess.run(['/bin/cp','-c',build['derived_disc'],str(disc)],capture_output=True,text=True)
    if p.returncode:shutil.copyfile(build['derived_disc'],disc)
    intervals=[]
    with disc.open('r+b')as f:
        for patch in patches:
            at=payload_offset+int(patch['address'],16)-0x4000;before=swap16(bytes.fromhex(patch['original']));after=swap16(bytes.fromhex(patch['replacement']));f.seek(at);assert f.read(len(before))==before;f.seek(at);f.write(after);intervals.append((at,at+len(after)))
        f.flush();os.fsync(f.fileno())
    changes=0;pos=0
    with Path(build['derived_disc']).open('rb')as left,disc.open('rb')as right:
        while True:
            a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
            if not a:break
            if a!=b:
                for i,(x,y)in enumerate(zip(a,b)):
                    if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changes+=1
            pos+=len(a)
    state=dict(status='terminal_native_Deck_asset_repair_disc_built_pending_gameplay',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),parent_build=str(bp),parent_build_sha256=sha(bp),parent_disc=build['derived_disc'],parent_disc_sha256=build['derived_disc_sha256'],derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_stage=str(stage_path),derived_stage_sha256=sha(stage_path),patches=patches,declared_patch_bytes=sum(hi-lo for lo,hi in intervals),actual_changed_bytes=changes,mode3_marker_groups=markers,original_group_count=16,repaired_group_count=13,native_component_unchanged=True,native_code_bytes=44430,new_training=False,default_promoted=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),patches_path,raw]},scope=__doc__)
    save(out/'protocol.json',state);save(V/'native-Deck-asset-repair-build-current.json',state);print(state['status'],changes,'changed bytes',flush=True)

if __name__=='__main__':main()
