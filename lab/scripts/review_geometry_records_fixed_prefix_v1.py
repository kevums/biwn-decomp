"""Compare existing v32 and new v33 equal-input prefixes; preserve live boundaries."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from review_scene17_fixed_prefix_v1 import differences

def main():
 out=V/'geometry-records-fixed-prefix-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 runs={};frames={};deps={str(Path(__file__)):sha(__file__)}
 for family,version in [('outer-compact','v6'),('geometry-records','v1')]:
  for lane in ['candidate','control']:
   key=family+'-'+lane;p=V/f'{family}-fixed-prefix-{version}-{lane}-current.json';g=read(p)
   assert g['status']=='terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance'
   for path,h in g['source_sha256'].items():assert sha(path)==h,path
   deps.update(g['source_sha256']);deps[str(p)]=sha(p)
   report=read(g['report']);schedule=read(g['schedule']);assert sha(g['report'])==g['report_sha256'] and len(report['frames'])==len(schedule)==1000
   assert [dict(frame=x['frame'],buttons=x['navigation']['buttons'])for x in report['frames']]==schedule
   frames[key]=report['frames'];runs[key]=dict(pointer=str(p),report=g['report'],schedule_sha256=g['schedule_sha256'],boundary=g['boundary'],raw_arena_errors_retained=g['raw_arena_errors_retained'],observers=g['observers'])
 assert len({x['schedule_sha256']for x in runs.values()})==1
 pairs={'v33_candidate_control':('geometry-records-candidate','geometry-records-control'),'v32_candidate_control':('outer-compact-candidate','outer-compact-control'),'v33_control_versus_v32_control':('geometry-records-control','outer-compact-control'),'v33_candidate_versus_v32_candidate':('geometry-records-candidate','outer-compact-candidate')}
 comparisons={label:differences(frames[left],frames[right])for label,(left,right)in pairs.items()}
 state=dict(status='terminal_v33_and_v32_fixed_input_prefixes_reviewed_fidelity_open',directory=str(out),frames_per_lane=1000,runs=runs,comparisons=comparisons,identical_frontend_schedule=True,new_predictions=0,new_training=False,installed_preview_changed=False,whole_game_fidelity_proven=False,scope='Two new v33 fresh prefixes and two existing v32 prefixes use identical frontend buttons. All raw active-slot/end-only arena counts are retained with independent fences. This is a truncated measurement,not route/quiescence acceptance. Native record body,module size and relocated code/heap differ; no isolated170A0speed or physical-console/IRQ/audio fidelity claim.',source_sha256=deps)
 save(out/'review.json',state);save(V/'geometry-records-fixed-prefix-reviewed-v1-current.json',state)
 for label,x in comparisons.items():print(label,x['video_sha256'],x['held_buttons'],flush=True)
if __name__=='__main__':main()
