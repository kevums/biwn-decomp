"""Bind the actual received stream and freeze tested small source artifacts."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,shutil
import check_native_deck_fresh_restore_v1 as common
from extract_biwn_stage import swap16
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha
def main():
    state=read(V/'native-Deck-asset-repair-delivery-current.json');pub=Path(state['directory']);bindings=read(pub/'source-and-raw-artifact-hashes.json')
    for p,digest in bindings.items():assert sha(p)==digest,p
    old=read(V/'native-Deck-ordinary-input-reviewed-current.json');ram_path=Path(old['candidate']['directory'])/'RAM-final.bin';ram=ram_path.read_bytes();buf=ram[0x1c0000:0x1c8000]
    manifest=read(V/'biwn-disc-resources.json');track=Path(manifest['raw_track_path']);assert sha(track)==manifest['source_raw_track_sha256'];data=swap16(track.read_bytes())
    start=data.find(buf);assert start>=0 and data.find(buf,start+1)<0
    marker=(0xc001).to_bytes(4,'big')*16;at=data.find(marker);assert at>=0 and data.find(marker,at+1)<0
    assert start==20834690 and at==20826066 and at-start==-8624 and marker not in buf
    witness=dict(status='terminal_actual_native_received_stream_matches_preserved_disc_marker_behind',recorded_at=datetime.now(timezone.utc).isoformat(),RAM_interval=[0x1c0000,0x1c8000],received_bytes=32768,received_sha256=hashlib.sha256(buf).hexdigest(),unique_normalized_track_offset=start,requested_group_marker_offset=at,marker_delta=-8624,marker_not_in_searched_buffer=True,source_sha256={str(p):sha(p)for p in [Path(__file__),ram_path,track,V/'biwn-disc-resources.json']},scope='Exact actual ordinary-native-run32768byte received RAM buffer matches preserved normalized disc once; desired64byteC001 marker is8624bytes before this actual stream. This is not inferred only from the older fixed-phase file provider. No game state modified.')
    wp=V/'native-Deck-actual-marker-stream-current.json';save(wp,witness);save(pub/wp.name,witness)
    bindings.update({str(p):sha(p)for p in [wp,Path(__file__),ram_path,track,V/'biwn-disc-resources.json']})
    # Immutable copies preserve the exact tested files if a later continuation
    # legitimately updates a current pointer/helper in the workspace.
    frozen=pub/'frozen-small-artifacts';frozen.mkdir(exist_ok=True);copies=[]
    for original,digest in sorted(bindings.items()):
        p=Path(original);assert sha(p)==digest
        if p.stat().st_size>8*1024*1024:continue
        name=hashlib.sha256(original.encode()).hexdigest()[:16]+'-'+p.name;target=frozen/name;shutil.copyfile(p,target);assert sha(target)==digest
        copies.append(dict(original_path=original,frozen_path=str(target.relative_to(pub)),sha256=digest))
    save(pub/'source-and-raw-artifact-hashes.json',bindings);save(pub/'frozen-small-artifacts-manifest.json',dict(files=copies,count=len(copies),scope='Original paths remain useful for large immutable raw files; these exact small-file snapshots survive later workspace updates.'))
    state.update(actual_marker_stream_witness=str(wp),actual_marker_stream_witness_sha256=sha(wp),frozen_small_artifacts=len(copies),raw_source_bindings=len(bindings))
    save(pub/'protocol.json',state);save(V/'native-Deck-asset-repair-delivery-current.json',state)
    goalpath=V/'goal-continuation-current.json';goal=read(goalpath);goal['native_Deck_asset_repair_delivery']=state;save(goalpath,goal);save(pub/'goal-state-final.json',goal)
    files={str(p.relative_to(pub)):sha(p)for p in pub.rglob('*')if p.is_file()and p.name!='integrity.json'};save(pub/'integrity.json',dict(files=files,count=len(files)))
    for p,digest in files.items():assert sha(pub/p)==digest
    print(witness['status'],len(copies),'files frozen;',len(bindings),'raw/source bindings',flush=True)
if __name__=='__main__':main()
