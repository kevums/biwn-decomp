"""Compare new rotation replays and retain the earlier measured polling variants."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha
from review_scene17_fixed_prefix_v1 import differences


def main():
    priorp=V/'scene17-rotation-fixed-prefix-review-v1-current.json';prior=read(priorp)
    for path,digest in prior['source_sha256'].items():assert sha(path)==digest,path
    out=V/'scene17-clear-fixed-prefix-review-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    frames={};runs={};deps=[Path(__file__),priorp]
    for lane in ['candidate','control']:
        pointer=V/f'scene17-clear-fixed-prefix-v4-{lane}-current.json';state=read(pointer)
        assert state['status']=='terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance'
        for path,digest in state['source_sha256'].items():assert sha(path)==digest,path
        assert sha(state['report'])==state['report_sha256']
        frames[lane]=read(state['report'])['frames'];assert len(frames[lane])==1000
        runs[lane]=dict(pointer=str(pointer),report=state['report'],schedule_sha256=state['schedule_sha256'],
                        boundary=state['boundary'],raw_arena_errors=state['raw_arena_errors_retained'],rotation=state['observers']['rotation'],clear=state['observers']['clear'])
        deps += [pointer,Path(state['report']),*map(Path,state['source_sha256'])]
    assert runs['candidate']['schedule_sha256']==runs['control']['schedule_sha256']==prior['runs']['control']['schedule_sha256']
    old=read(prior['runs']['control']['report'])['frames']
    compared=differences(frames['candidate'],frames['control'])
    control_changes=differences(old,frames['control'])
    result=dict(status='terminal_clear_fixed_input_prefix_reviewed',directory=str(out),frames_per_lane=1000,
                runs=runs,comparisons={**prior['comparisons'],'clear':compared},
                new_control_versus_prior_layout=control_changes,identical_frontend_schedule=True,
                preview_changed=False,new_predictions=0,new_training=False,whole_game_fidelity_proven=False,
                scope='Candidate/control share the v26 layout and receive the exact original recorded frontend buttons. Comparison with earlier variants retains their separate layouts and measured control changes. Prefix boundaries may contain live calls; raw pending/end-arena counts and independent fence checks are preserved. This is not a complete route, cycle, IRQ, audio or console proof.',
                source_sha256={str(p):sha(p)for p in dict.fromkeys(deps)})
    save(out/'review.json',result);save(V/'scene17-clear-fixed-prefix-review-v1-current.json',result)
    print(result['status'],'video',compared['video_sha256'],'control video',control_changes['video_sha256'],flush=True)


if __name__=='__main__':main()
