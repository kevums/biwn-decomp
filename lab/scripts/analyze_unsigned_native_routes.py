"""Read completed route artifacts; separate content/timing from speed claims."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def intervals(rows,predicate):
 result=[];start=None;last=None
 for row in rows:
  yes=predicate(row)
  if yes and start is None:start=row['frame']
  if not yes and start is not None:result.append([start,last]);start=None
  last=row['frame']
 if start is not None:result.append([start,last])
 return result
proof=ROOT/'verification/native-unsigned-format-long-route-current.json';state=json.loads(proof.read_text());assert state['status']=='terminal_fresh_base_optimized_adaptive_routes_classified';root=Path(state['directory']);lanes={}
for lane in ['parent','unsigned']:
 path=root/lane/'report.json';assert sha(path)==state['results'][lane]['report_sha256'];r=json.loads(path.read_text());rows=r['frames'];last=0;sounding=[]
 for row in rows:
  value=row['cumulative_nonzero_audio_samples']
  if value>last:sounding.append(row['frame'])
  last=value
 lanes[lane]=dict(rows=rows,frames=len(rows),movie_flag_nonzero_intervals=intervals(rows,lambda r:any(r['movie_flag_words'])),audio_count_increasing_frames=len(sounding),first_audio_count_increase=sounding[0] if sounding else None,last_audio_count_increase=sounding[-1] if sounding else None,first_navigation_return=next((r['frame'] for r in rows if (r.get('navigation')or{}).get('return_started')),None))
a,b=lanes['parent']['rows'],lanes['unsigned']['rows'];fields=['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word','video_sha256','cumulative_nonzero_audio_samples']
comparison={k:dict(first_different_frame=next((x['frame'] for x,y in zip(a,b) if x[k]!=y[k]),None),different_shared_prefix_rows=sum(x[k]!=y[k] for x,y in zip(a,b))) for k in fields}
for v in lanes.values():v.pop('rows')
inputs=[proof,Path(__file__),*[root/lane/'report.json' for lane in ['parent','unsigned']]]
result=dict(status='completed_route_fields_compared_no_speedup_or_frame_equivalence',directory=str(root),lanes=lanes,selected_shared_prefix_comparison=comparison,frame_difference_new_minus_parent=state['results']['unsigned']['executed_frames']-state['results']['parent']['executed_frames'],same_adaptive_policy_not_identical_inputs=True,raw_PCM_equal=sha(root/'parent/frontend-PCM.s16le')==sha(root/'unsigned/frontend-PCM.s16le'),route_complete_both=all(r['merchant_reached'] and r['completed_outdoor_hold'] and r['return_floor_values']==[0,1] for r in state['results'].values()),interpretation='Different route lengths, positions, movie-flag intervals and captured audio. No whole-game speedup, fixed-input equivalence, physical audio or cause isolation. Both finite adaptive routes complete; exact arithmetic semantics were tested separately with IRQ disabled.',dependencies_sha256={str(p):sha(p) for p in inputs})
(root/'selected-field-analysis.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'verification/native-unsigned-route-analysis-current.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['lanes','frame_difference_new_minus_parent','raw_PCM_equal','route_complete_both']},indent=2))
