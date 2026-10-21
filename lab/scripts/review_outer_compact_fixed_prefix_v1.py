"""Compare four actual identical-input1000-frame replays, retaining raw boundary state."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from review_scene17_fixed_prefix_v1 import differences

def main():
    out=V/'outer-compact-fixed-prefix-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    runs={};frames={};deps={str(Path(__file__)):sha(__file__)}
    for family in ['scene17-gpu-family','outer-compact']:
        for lane in ['candidate','control']:
            key=family+'-'+lane;p=V/(key.replace('-candidate','-fixed-prefix-v6-candidate').replace('-control','-fixed-prefix-v6-control')+'-current.json');g=read(p)
            assert g['status']=='terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance'
            for path,h in g['source_sha256'].items():assert sha(path)==h,path
            deps.update(g['source_sha256']);deps[str(p)]=sha(p)
            report=read(g['report']);schedule=read(g['schedule']);assert len(report['frames'])==len(schedule)==1000
            assert [dict(frame=x['frame'],buttons=x['navigation']['buttons'])for x in report['frames']]==schedule
            frames[key]=report['frames'];runs[key]=dict(pointer=str(p),report=g['report'],schedule_sha256=g['schedule_sha256'],boundary=g['boundary'],raw_arena_errors_retained=g['raw_arena_errors_retained'],observers=g['observers'])
    assert len({x['schedule_sha256']for x in runs.values()})==1
    comparisons={}
    pairs={'v30_candidate_control':('scene17-gpu-family-candidate','scene17-gpu-family-control'),
        'compact_candidate_control':('outer-compact-candidate','outer-compact-control'),
        'compact_control_versus_v30_control':('outer-compact-control','scene17-gpu-family-control'),
        'compact_candidate_versus_v30_candidate':('outer-compact-candidate','scene17-gpu-family-candidate')}
    for label,(left,right)in pairs.items():
        compared=differences(frames[left],frames[right]);assert compared['held_buttons']['count']==0
        comparisons[label]=compared
    state=dict(status='terminal_compact_and_v30_fixed_input_prefixes_reviewed',directory=str(out),frames_per_lane=1000,runs=runs,comparisons=comparisons,
        identical_frontend_schedule=True,new_predictions=0,new_training=False,preview_changed=False,whole_game_fidelity_proven=False,
        scope='Four actual fresh equal-frame prefixes use the same recorded frontend schedule, with no checkpoint or host state repair. Raw active-slot/end-only arena counts and independent fence checks are retained; this is not complete-route acceptance. Both layouts retain the same scene C and inherited GPU wait behavior; outer context, arena layout and boot-copy changes differ. No causal speed, IRQ, audio or physical-console claim.',source_sha256=deps)
    save(out/'review.json',state);save(V/'outer-compact-fixed-prefix-reviewed-v1-current.json',state)
    for label,comparison in comparisons.items():print(label,comparison['video_sha256'],flush=True)

if __name__=='__main__':main()
