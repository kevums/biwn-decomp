"""Analyze saved frame observations without rerunning or changing controller inputs.
A nearby matching video hash is temporal correspondence,not fidelity proof.
"""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def intervals(values):
 result=[]
 for x in values:
  if result and x==result[-1][1]+1:result[-1][1]=x
  else:result.append([x,x])
 return result

def main():
 out=V/'native-debug-frame-differences-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);paths=[Path(__file__)];families={}
 keys=['scene_word','raw_player_X','raw_player_Z','player_mode_word','tile_word','equipped_word','movie_flag_words','movie_controller_state_word','floor_word','raw_word_49c5c','locomotion_state','held_buttons','cumulative_nonzero_audio_samples']
 for family in ['clear','debug']:
  proof_path=V/f'native-Deck-{family}-gameplay-reviewed-v1-current.json';proof=read(proof_path);assert proof['differing_video_frames']==62
  reports={};trials={}
  for lane in ['candidate','control']:
   jp=V/f'native-Deck-{family}-geometry-v1-{lane}-current.json';job=read(jp);rp=Path(job['report']);assert sha(rp)==job['report_sha256'];reports[lane]=read(rp);start=reports[lane]['ordinary_Deck_input_trial']['start_frame'];trials[lane]=reports[lane]['frames'][start:];paths.extend([jp,rp])
  a,b=trials['candidate'],trials['control'];start=reports['candidate']['ordinary_Deck_input_trial']['start_frame'];assert start==reports['control']['ordinary_Deck_input_trial']['start_frame']
  rows=[];semantic={key:[]for key in keys}
  for i,(left,right)in enumerate(zip(a,b)):
   for key in keys:
    if left[key]!=right[key]:semantic[key].append(i+1)
   if left['video_sha256']!=right['video_sha256']:
    matches=[]
    for lag in range(-8,9):
     j=i+lag
     if 0<=j<len(b)and left['video_sha256']==b[j]['video_sha256']:matches.append(lag)
    rows.append(dict(offset=i+1,frame=left['frame'],nearby_control_video_lags=matches,semantic_differing_fields=[key for key in keys if left[key]!=right[key]],candidate_PC=left['CPU'],control_PC=right['CPU']))
  assert len(rows)==62
  families[family]=dict(start_frame=start,candidate_trial_frames=len(a),control_trial_frames=len(b),video_difference_offsets=[row['offset']for row in rows],video_difference_intervals=intervals([row['offset']for row in rows]),semantic_difference_offsets=semantic,semantic_difference_intervals={key:intervals(value)for key,value in semantic.items()if value},video_differences_with_control_hash_within8frames=sum(bool(row['nearby_control_video_lags'])for row in rows),video_differences_without_nearby_hash=[row['offset']for row in rows if not row['nearby_control_video_lags']],unpaired_candidate_tail_offsets=list(range(len(b)+1,len(a)+1)),unpaired_control_tail_offsets=list(range(len(a)+1,len(b)+1)),rows=rows)
  paths.append(proof_path)
 a=families['clear'];b=families['debug'];save(out/'families.json',families)
 result=dict(status='terminal_saved_frame_temporal_and_public_field_difference_analysis',directory=str(out),new_game_execution=False,new_predictions=0,new_training=False,unchanged_inputs=True,previous_clear_difference_offsets_equal_new_debug=a['video_difference_offsets']==b['video_difference_offsets'],current_video_differences=62,current_video_difference_intervals=b['video_difference_intervals'],current_semantic_difference_intervals=b['semantic_difference_intervals'],current_video_differences_with_nearby_control_hash=b['video_differences_with_control_hash_within8frames'],current_video_differences_without_nearby_hash=b['video_differences_without_nearby_hash'],unpaired_candidate_tail_offsets=b['unpaired_candidate_tail_offsets'],fidelity_verified=False,scope=__doc__+' Only the named public frame fields are compared;CPU registers,RAM/GPU/DSP internals and subframe behavior are not normalized or declared equivalent. Both frame counts and unmatched tails are preserved.',source_sha256={str(p):sha(p)for p in [*paths,out/'families.json']})
 text='SAVED GAMEPLAY FRAME DIFFERENCES\n\n'+json.dumps({k:v for k,v in result.items()if k not in ['source_sha256']},indent=2)+'\n\nEvidence:'+str(out/'families.json')+'\n';report=ROOT/'reports/Native Debug Saved Frame Difference Analysis.txt';report.write_text(text);result['report']=str(report);result['source_sha256'][str(report)]=sha(report);save(out/'review.json',result);save(V/'native-debug-frame-differences-v1-current.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['source_sha256','scope']},indent=2))
if __name__=='__main__':main()
