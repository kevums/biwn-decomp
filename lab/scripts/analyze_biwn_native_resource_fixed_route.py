"""Separate native26parent-trace agreement from failure of the prior intended route."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 rp=ROOT/'verification/native-resource-fixed-route-current.json';route=json.loads(rp.read_text());assert route['status']=='terminal_equal_duration_fixed_pad_pair_pending_analysis';directory=Path(route['directory']);rows={}
 for lane,result in route['results'].items():
  p=directory/lane/'report.json';assert sha(p)==result['report_sha256'];rows[lane]=json.loads(p.read_text())['frames'];assert len(rows[lane])==route['frames']==29783
 assert route['native25_prior_game_rows_different']==0 and route['native25_prior_PCM_equal']
 left=rows['native25_fixed'];right=rows['native26_fixed'];assert all(a['input_seen_mask']==b['input_seen_mask']and a['input_pressed_mask']==b['input_pressed_mask']and a['fixed_buttons']==b['fixed_buttons']for a,b in zip(left,right))
 fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','tile_word','equipped_word','movie_flag_words','movie_controller_state_word','cumulative_nonzero_audio_samples','video_sha256','GPU','DSP','GPU_R31_banks'];compared={k:dict(different_frames=sum(a[k]!=b[k]for a,b in zip(left,right)),first_different_frame=next((a['frame']for a,b in zip(left,right)if a[k]!=b[k]),None))for k in fields}
 game_fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256','cumulative_nonzero_audio_samples'];assert all(compared[k]['different_frames']==0 for k in game_fields)
 outcomes={lane:dict(merchant_position_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in data),outdoor_floor0_reached=any(x['player_mode_word']==1 and x['floor_word']==0 and x['scene_word']==312 and x['frame']>23538 for x in data),final_fields={k:data[-1][k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']})for lane,data in rows.items()}
 assert not outcomes['native26_fixed']['merchant_position_reached']and not outcomes['native26_fixed']['outdoor_floor0_reached']
 report=dict(status='terminal_native26_parent_game_video_PCM_match_inherited_route_failure',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(directory),route_proof=str(rp),route_proof_sha256=sha(rp),frames_per_lane=29783,actual_pad_callback_differences=0,native25_repeat_game_rows_different=0,native25_repeat_PCM_equal=True,outcomes=outcomes,compared_fields=compared,native26_matches_native25_selected_game_video_PCM=True,raw_PCM_equal=sha(directory/'native25_fixed/frontend-PCM.s16le')==sha(directory/'native26_fixed/frontend-PCM.s16le'),audio={lane:dict(nonzero_samples=x['nonzero_audio_samples'],stereo_frames=x['audio_stereo_frames'])for lane,x in route['results'].items()},current_disc_fixed_input_tested=True,fixed_input_equivalence_to_prior_native23=False,fixed_input_failure_profile=26,scope='Native25baseline repeats its prior fixed game rows/PCM exactly. Native26matches parent per-frame playerXZ/mode/floor/scene/video/cumulativePCM on this29783frame schedule; GPU PC differs9frames andR31banks5frames, so no full machine-state equivalence. Both stay floor2/scene314 and emit zero nonzeroPCM. This preserves the parent failure of the earlier native23merchant/outdoor schedule; equal silent PCM does not validate speech/playback. Native26adaptive route is separately complete. No physical/IRQ/general input or whole-game equivalence proof.',source_sha256={str(Path(__file__)):sha(__file__)})
 save(directory/'fixed-analysis.json',report);save(ROOT/'verification/native-resource-fixed-route-analysis-current.json',report)
 out=ROOT/'verification/native-resource-fixed-followup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);deps={};snapshots={}
 def pin(p,snapshot=False):
  p=Path(p).resolve();assert p.is_relative_to(ROOT);rel=str(p.relative_to(ROOT));digest=sha(p)
  if snapshot:
   dest=out/(hashlib.sha256(rel.encode()).hexdigest()[:12]+'-'+p.name)
   if not dest.exists():shutil.copy2(p,dest)
   assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;snapshots[rel]=str(dest.relative_to(ROOT))
  else:deps[rel]=digest
 for p in [rp,ROOT/'verification/native-resource-fixed-route-analysis-current.json',Path(__file__)]:pin(p,True)
 for p,d in route['source_sha256'].items():assert sha(p)==d;pin(p,True)
 for lane in route['results']:
  for name in ['report.json','gameplay-observation.json','RAM-final.bin','state-final.bin','frontend-PCM.s16le','video-final.xrgb8888']:pin(directory/lane/name)
 parent=ROOT/'verification/native-resource-publication-current.json';manifest=dict(status='published_native26_fixed_parent_match_and_inherited_failure',recorded_at=report['recorded_at'],directory=str(out),parent_publication_sha256=sha(parent),analysis=report,dependencies_sha256=deps,source_snapshots=snapshots,whole_game_complete=False)
 save(out/'publication.json',manifest);save(ROOT/'verification/native-resource-fixed-followup-current.json',manifest);print(json.dumps({'status':report['status'],'dependencies':len(deps),'parent_game_video_PCM_match':True,'prior23route_failure':True}),flush=True)
if __name__=='__main__':main()
