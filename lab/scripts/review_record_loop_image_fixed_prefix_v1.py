"""Compare actual v37/v34 fixed navigation prefixes without causal claims."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from review_scene17_fixed_prefix_v1 import differences

def main():
    out=V/'record-loop-image-fixed-prefix-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    frames={};runs={};deps={str(Path(__file__)):sha(__file__)}
    for family in ['record-loop-image','record-strides']:
        for lane in ['candidate','control']:
            key=family+'-'+lane;pointer=V/f'{family}-fixed-prefix-v1-{lane}-current.json';g=read(pointer)
            assert g['status']=='terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance'
            for p,h in g['source_sha256'].items():assert sha(p)==h,p
            report=read(g['report']);schedule=read(g['schedule']);assert len(report['frames'])==len(schedule)==1000
            assert sha(g['report'])==g['report_sha256']and sha(g['schedule'])==g['schedule_sha256']
            assert [dict(frame=x['frame'],buttons=x['navigation']['buttons'])for x in report['frames']]==schedule
            assert g['boundary']['pre_finish_arena_errors']==g['boundary']['region_errors']==0
            assert g['raw_arena_errors_retained']==g['expected_end_only_arena_errors']
            frames[key]=report['frames'];runs[key]=dict(pointer=str(pointer),report=g['report'],schedule_sha256=g['schedule_sha256'],boundary=g['boundary'],observers=g['observers'],raw_arena_errors_retained=g['raw_arena_errors_retained'],expected_end_only_arena_errors=g['expected_end_only_arena_errors'],audio=report['audio'])
            deps[str(pointer)]=sha(pointer);deps.update(g['source_sha256'])
    assert len({x['schedule_sha256']for x in runs.values()})==1
    current=differences(frames['record-loop-image-candidate'],frames['record-loop-image-control'])
    previous=differences(frames['record-strides-candidate'],frames['record-strides-control'])
    layouts={lane:differences(frames['record-loop-image-'+lane],frames['record-strides-'+lane])for lane in ['candidate','control']}
    assert current['video_sha256']['count']==449 and current['video_sha256']['first_frame']==378
    assert current['CPU_full']['first_frame']==current['full_GPU_state_sha256']['first_frame']==376
    assert current['held_buttons']['count']==2 and current['held_buttons']['first_frame']==634
    assert current['full_DSP_state_sha256']['count']==0 and previous['video_sha256']['count']==450
    a,b=frames['record-loop-image-candidate'],frames['record-loop-image-control']
    proof=dict(status='terminal_v37_fixed_input_prefix_measured_visual_timing_and_audio_unresolved',directory=str(out),profile='deck-shared-v37-record-loop-advance-v2',frames_per_lane=1000,runs=runs,comparison=current,previous_v34_comparison=previous,layout_comparisons=layouts,
        identical_frontend_navigation_schedule=True,first_nonempty_navigation_frame=next(x['frame']for x in a if x['navigation']['buttons']),
        current_video_differences=449,previous_v34_video_differences=450,component_optimization_resolves_visual_timing=False,
        final_video_equal=a[-1]['video_sha256']==b[-1]['video_sha256'],complete_route_or_quiescence_acceptance=False,
        new_predictions=0,new_training=False,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,installed_preview_changed=False,whole_game_fidelity_proven=False,
        scope='Fresh1000frame truncated measurements with identical declared per-frame navigation inputs and the same intro/controller implementation. Current v37candidate/control share layout;control restores only10original scene-entry bytes and retains inherited global native providers. Comparison to v34also includes code relocation/boot-copy/heap changes;449versus450is not an isolated optimization benefit. Raw pending scene/GPU/end-only counts retained with independent fences;not a completed route. DSP hashes agree,but both audio outputs remain silent.',source_sha256=deps)
    save(out/'review.json',proof);save(V/'record-loop-image-fixed-prefix-reviewed-v1-current.json',proof)
    print('v37 fixed prefix449video differences,first378;two held-button differences;fidelity open.',flush=True)

if __name__=='__main__':main()
