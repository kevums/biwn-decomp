"""Compare retained first-policy prefixes with fresh clearance followup."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from run_biwn_native_fast_gameplay_route import ROOT,save,sha

def prefix_hash(path,count):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        while count:
            chunk=f.read(min(count,1048576));assert chunk;h.update(chunk);count-=len(chunk)
    return h.hexdigest()

def main():
    a_path=ROOT/'verification/native-word-scan-route-current.json';b_path=ROOT/'verification/native-word-scan-clearance-long-route-current.json';a=json.loads(a_path.read_text());b=json.loads(b_path.read_text());result={}
    for lane in b['lanes']:
        pa=Path(a['directory'])/lane/'report.json';pb=Path(b['directory'])/lane/'report.json';ra=json.loads(pa.read_text());rb=json.loads(pb.read_text());old,new=ra['frames'],rb['frames']
        first=next(x['frame']for x in old if(x.get('navigation')or{}).get('return_started')and x['player_mode_word']==1)
        assert len(new)>=first
        changed=[i+1 for i,(x,y)in enumerate(zip(old[:first],new[:first]))if x!=y]
        # Current fixed audio callback batch is800stereo16bit samples/frame.
        size_a=(Path(a['directory'])/lane/'frontend-PCM.s16le').stat().st_size;size_b=(Path(b['directory'])/lane/'frontend-PCM.s16le').stat().st_size
        assert size_a==len(old)*3200 and size_b==len(new)*3200
        ha=prefix_hash(Path(a['directory'])/lane/'frontend-PCM.s16le',first*3200);hb=prefix_hash(Path(b['directory'])/lane/'frontend-PCM.s16le',first*3200)
        result[lane]=dict(first_outdoor_frame_in_first_run=first,prefix_frames_compared=first,full_recorded_rows_different=len(changed),first_row_difference=changed[0]if changed else None,PCM_prefix_equal=ha==hb,old_PCM_prefix_sha256=ha,new_PCM_prefix_sha256=hb,old_report_sha256=sha(pa),new_report_sha256=sha(pb))
    proof=dict(status='terminal_repaired_route_prefixes_compared',recorded_at=datetime.now(timezone.utc).isoformat(),first_protocol=str(a_path),first_protocol_sha256=sha(a_path),followup_protocol=str(b_path),followup_protocol_sha256=sha(b_path),results=result,source_sha256={str(Path(__file__)):sha(__file__)},scope='Full recorded per-frame dictionaries and exact frontend PCM through the first outdoorentry in each repaired lane. The policy changes only after that entry. Original/native unrepaired controls are earlier fresh executions and never reach that branch; no new unrepaired runs or whole-game/physical-timing equivalence claim.')
    save(ROOT/'verification/native-word-scan-prefix-current.json',proof);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
