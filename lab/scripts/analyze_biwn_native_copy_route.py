"""Review actual task route transitions and retained native21 determinism."""
from pathlib import Path
from datetime import datetime,timezone
import json
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
    rp=ROOT/'verification/native-copy-route-current.json';route=json.loads(rp.read_text());assert route['status']=='terminal_fresh_native21_native23_copy_routes_classified';directory=Path(route['directory'])
    prior=json.loads(Path(route['prior_route_proof']).read_text());assert sha(route['prior_route_proof'])==route['prior_route_proof_sha256'];result={};allrows={}
    for lane,row in route['results'].items():
        path=directory/lane/'report.json';assert sha(path)==row['report_sha256'];rows=json.loads(path.read_text())['frames'];allrows[lane]=rows
        start=next((i for i,x in enumerate(rows)if(x.get('navigation')or{}).get('return_started')),None)
        transitions=[]if start is None else [(rows[i-1]['floor_word'],rows[i]['floor_word'],rows[i]['frame'])for i in range(start,len(rows))if rows[i]['floor_word']!=rows[i-1]['floor_word']]
        last=rows[-1];previous_floor=None if start is None or start==0 else rows[start-1]['floor_word']
        hold=(last.get('navigation')or{}).get('outdoor_hold',0)==120 and all(x['player_mode_word']==1 and x['floor_word']==0 for x in rows[-120:])
        clearance=(last['raw_player_X']-13056)**2+(last['raw_player_Z']-42400)**2<=64
        result[lane]=dict(previous_floor=previous_floor,transitions=transitions,hold120=hold,clearance=clearance,merchant_reached=row['merchant_reached'],continuous_merchant_to_outdoor=bool(previous_floor==2 and [x[:2]for x in transitions]==[(2,1),(1,0)]and hold and clearance and row['merchant_reached']))
    old=Path(prior['directory'])/'native21_repaired';oldrows=json.loads((old/'report.json').read_text())['frames'];current=allrows['native21_repaired'];differences=sum(a!=b for a,b in zip(oldrows,current))+abs(len(oldrows)-len(current));PCM=sha(old/'frontend-PCM.s16le')==sha(directory/'native21_repaired/frontend-PCM.s16le')
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='terminal_native_copy_routes_semantically_reviewed',route_proof=str(rp),route_proof_sha256=sha(rp),results=result,both_completed=all(x['continuous_merchant_to_outdoor']for x in result.values()),native21_repeat_full_rows_different=differences,native21_repeat_PCM_equal=PCM,native21_repeat_frames=len(current),final_raw_video_equal=sha(directory/'native21_repaired/video-final.xrgb8888')==sha(directory/'native23_repaired/video-final.xrgb8888'),final_PCM_equal=sha(directory/'native21_repaired/frontend-PCM.s16le')==sha(directory/'native23_repaired/frontend-PCM.s16le'),source_sha256={str(Path(__file__)):sha(__file__)},scope='Actual precedingfloor2 and ordered2→1→0transitions, source-derived outdoorclearance and120outdoorhold rows. Native21repeat compared with preceding preserved run, including fullrecordedrow dictionaries andPCM. Not cross-profile per-frame/whole-game/physical equivalence.')
    save(directory/'semantic-analysis.json',report);save(ROOT/'verification/native-copy-route-analysis-current.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
