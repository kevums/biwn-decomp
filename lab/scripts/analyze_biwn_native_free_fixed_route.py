"""Classify actual equal-duration fixed-pad results, including negative outcomes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 rp=ROOT/'verification/native-free-fixed-route-current.json';route=json.loads(rp.read_text());assert route['status']=='terminal_equal_duration_fixed_pad_pair_pending_analysis';directory=Path(route['directory']);rows={}
 for lane,result in route['results'].items():
  p=directory/lane/'report.json';assert sha(p)==result['report_sha256'];rows[lane]=json.loads(p.read_text())['frames'];assert len(rows[lane])==route['frames']
 assert route['native23_prior_game_rows_different']==0 and route['native23_prior_PCM_equal']
 left=rows['native23_fixed'];right=rows['native25_fixed'];assert len(left)==len(right)==29783
 pad_diffs=sum(a['input_seen_mask']!=b['input_seen_mask']or a['input_pressed_mask']!=b['input_pressed_mask']or a['fixed_buttons']!=b['fixed_buttons']for a,b in zip(left,right));assert pad_diffs==0
 fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256','cumulative_nonzero_audio_samples','GPU','DSP']
 compared={k:dict(different_frames=sum(a[k]!=b[k]for a,b in zip(left,right)),first_different_frame=next((a['frame']for a,b in zip(left,right)if a[k]!=b[k]),None))for k in fields}
 outcomes={lane:dict(merchant_position_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in data),outdoor_floor0_reached=any(x['player_mode_word']==1 and x['floor_word']==0 and x['scene_word']==312 and x['frame']>23538 for x in data),final_fields={k:data[-1][k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']})for lane,data in rows.items()}
 report=dict(status='terminal_fixed_input_native25_equivalence_rejected',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(directory),route_proof=str(rp),route_proof_sha256=sha(rp),frames_per_lane=29783,actual_pad_callback_differences=pad_diffs,native23_repeat_game_rows_different=0,native23_repeat_PCM_equal=True,outcomes=outcomes,compared_fields=compared,audio={lane:dict(nonzero_samples=result['nonzero_audio_samples'],stereo_frames=result['audio_stereo_frames'])for lane,result in route['results'].items()},raw_PCM_equal=sha(directory/'native23_fixed/frontend-PCM.s16le')==sha(directory/'native25_fixed/frontend-PCM.s16le'),adaptive_route_result_superseded=False,fixed_input_equivalence=False,whole_game_complete=False,scope='Equal29783frame fresh ordinaryHLE/CDloads in retained emulator. Same recordedpad masks and actual input callbacks; priornative23game rows/PCM repeat exactly. Native25fixedrun fails the previous merchant/outdoor route and has zero nonzeroPCM, so adaptive-route completion is insufficient for equivalence. This does not isolate which code/timing change causes divergence, prove a low-level free semantic defect, or establish physical behavior. New current disclosure must retain this failed control.',source_sha256={str(Path(__file__)):sha(__file__)})
 save(directory/'fixed-input-analysis.json',report);save(ROOT/'verification/native-free-fixed-route-analysis-current.json',report)
 # Freeze a distinct follow-up; never rewrite the earlier publication.
 out=ROOT/'verification/native-free-fixed-followup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);deps={};snapshots={}
 for p in [rp,ROOT/'verification/native-free-fixed-route-analysis-current.json',Path(__file__),Path(route['source_route_proof'])]:
  rel=str(p.resolve().relative_to(ROOT));dest=out/(hashlib.sha256(rel.encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,dest);deps[str(dest.relative_to(ROOT))]=sha(dest);snapshots[rel]=str(dest.relative_to(ROOT))
 for p,d in route['source_sha256'].items():assert sha(p)==d;deps[str(Path(p).relative_to(ROOT))]=d
 for lane in route['results']:
  for name in ['report.json','gameplay-observation.json','RAM-final.bin','state-final.bin','frontend-PCM.s16le','video-final.xrgb8888']:
   p=directory/lane/name;deps[str(p.relative_to(ROOT))]=sha(p)
 pub=ROOT/'verification/native-free-publication-current.json';parent=json.loads(pub.read_text());manifest=dict(status='published_native25_failed_fixed_input_control',recorded_at=report['recorded_at'],parent_publication=str(pub.relative_to(ROOT)),parent_publication_sha256=sha(pub),directory=str(out),analysis=report,dependencies_sha256=deps,source_snapshots=snapshots,whole_game_complete=False)
 save(out/'followup.json',manifest);save(ROOT/'verification/native-free-fixed-followup-current.json',manifest);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
