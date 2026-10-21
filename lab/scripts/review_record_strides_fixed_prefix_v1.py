"""Review current-image fixed input evidence, preserving unfinished calls."""
from datetime import datetime,timezone
from pathlib import Path
import subprocess
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone
from review_scene17_fixed_prefix_v1 import differences

def main():
    out=V/'record-strides-fixed-prefix-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    runs={};frames={};deps={str(Path(__file__)):sha(__file__)}
    for family in ['record-strides','geometry-records']:
        for lane in ['candidate','control']:
            key=family+'-'+lane;p=V/f'{family}-fixed-prefix-v1-{lane}-current.json';g=read(p)
            assert g['status']=='terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance'
            for path,h in g['source_sha256'].items():assert sha(path)==h,path
            assert sha(g['report'])==g['report_sha256'] and sha(g['schedule'])==g['schedule_sha256']
            report=read(g['report']);schedule=read(g['schedule']);rows=report['frames']
            assert len(rows)==len(schedule)==1000
            assert [dict(frame=x['frame'],buttons=x['navigation']['buttons'])for x in rows]==schedule
            assert g['boundary']['pre_finish_arena_errors']==g['boundary']['region_errors']==0
            assert g['raw_arena_errors_retained']==g['expected_end_only_arena_errors']
            frames[key]=rows
            runs[key]=dict(pointer=str(p),report=g['report'],schedule_sha256=g['schedule_sha256'],boundary=g['boundary'],observers=g['observers'],raw_arena_errors_retained=g['raw_arena_errors_retained'],expected_end_only_arena_errors=g['expected_end_only_arena_errors'],audio=report['audio'])
            deps[str(p)]=sha(p);deps.update(g['source_sha256'])
    assert len({r['schedule_sha256']for r in runs.values()})==1
    pair=differences(frames['record-strides-candidate'],frames['record-strides-control'])
    layouts={lane:differences(frames['record-strides-'+lane],frames['geometry-records-'+lane])for lane in ['candidate','control']}
    assert pair['video_sha256']['count']==450 and pair['video_sha256']['first_frame']==378
    assert pair['held_buttons']['count']==0 and pair['CPU_full']['first_frame']==pair['full_GPU_state_sha256']['first_frame']==376
    assert pair['full_DSP_state_sha256']['count']==0
    assert layouts['control']['video_sha256']['count']==199
    assert all(runs['record-strides-'+lane]['audio']['nonzero_samples']==0 for lane in ['candidate','control'])
    report=ROOT/'reports/BIWN v34 Identical Input Prefix Review.txt'
    state=dict(status='terminal_v34_fixed_input_prefix_reviewed_timing_and_audio_unresolved',directory=str(out),report=str(report),profile='deck-shared-v34-record-strides-v1',frames_per_lane=1000,
        runs=runs,comparison=pair,layout_comparisons_to_prior_v33=layouts,identical_frontend_schedule=True,held_buttons_identical=True,
        final_video_equal=frames['record-strides-candidate'][-1]['video_sha256']==frames['record-strides-control'][-1]['video_sha256'],
        ordinary_movement_inputs_start_frame=600,first_video_difference_precedes_movement=True,
        active_native_scene_calls_at_end=runs['record-strides-candidate']['observers']['shared']['pending'],
        complete_route_or_quiescence_acceptance=False,new_predictions=0,new_training=False,installed_preview_changed=False,
        whole_game_fidelity_proven=False,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,
        scope='Fresh fixed1000frame measurement with identical frontend buttons. Candidate/control use the same v34 layout;control restores only10original scene-entry bytes,not global native providers. CPU/GPU divergence precedes movement inputs;this excludes adaptive controller feedback as the sole explanation,not all other timing causes. Candidate ends with an active native scene call;control ends with one active GPU arena. Raw pending/end-only counts are retained with independent fences,not relabeled as complete-route success. Comparison to v33 includes relocation/layout/heap changes;not an isolated stride cost or quality improvement.')
    report.write_text('BIWN v34 — identical input prefix\n\n'
        'Two new fresh1000frame runs use the exact same per-frame button schedule. Video differs on450frames,first378;CPU and GPU state hashes first differ at376. Recorded held-button RAM values match on every frame. PlayerX first differs at643(358frames total),Zat650(342). Scene,mode,tile,equipped and movie fields agree throughout. FullDSPstate hashes match throughout. Movement inputs start600,so adaptive control feedback cannot solely explain the first divergence. This does not identify a unique causal instruction or prove fidelity.\n\n'
        'Both lanes emit800000audio frames and zero nonzero samples. Candidate prefix ends with one pending native scene call;control ends with one active GPUarena/end-only count. Pre-finish errors and independent region checks are zero;fences and unused slots pass. These unfinished states are preserved. This truncated measurement is not a complete route or quiescence acceptance.\n\n'
        'The control keeps the v34 layout and inherited global native copy/matrix/wait providers and restores only10original scene-entry bytes. Prior v33prefixes use the same frontend schedule but a different layout. New versus old control differs on199video frames,first227,before current candidate/control divergence. This warns against treating450versus prior448as an isolated stride improvement/regression. No replay of old tests,no game-state injection,no new prediction or optimizer update. Preview unchanged.\n\n'
        'Next:trace original/compiled scene entry and GPU submission/return timing around frames375–379 using read-only instrumentation;retain full differences and avoid masking state to manufacture equality. Continue silent-audio and whole-game source recovery.\n')
    state['source_sha256']={**deps,str(report):sha(report)}
    save(out/'review.json',state);rp=V/'record-strides-fixed-prefix-reviewed-v1-current.json';save(rp,state)
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
    packet=read(w['packet']);save(out/'before-packet.json',packet)
    facts={k:v for k,v in state.items()if k not in ['source_sha256','runs']}
    packet['record_strides_fixed_input_progress']=facts
    for key in ['native_scene_draw_progress','native_geometry_records_progress','latest_native_candidate']:
        d=packet[key];d['current_fixed_input_video_comparison']=pair['video_sha256'];d['current_fixed_input_comparison_verified']=True
        d['fixed_input_control_layout_changes']=layouts['control'];d['fixed_input_review']=str(rp)
        d['fixed_input_scope']=state['scope']
        d['next_action']='Trace scene/GPU submission and return timing around first equal-input CPU/GPU divergence376 and video378;investigate silent audio. Continue remaining readable CPU/GPU/DSP/HLE source and same-console rebuilding,useful heldout training and copied-weight native Chat. Preserve separate route counts and unpromoted v35component.'
    packet['native_scene_draw_progress']['record_strides_fixed_input_progress']=facts
    packet['checked_current_summary']+=' Current v34identical-input1000frame prefix is now measured:450video differences first378,CPU/GPU first376;held-buttonRAM matches throughout,DSPstate matches throughout. Movement starts600. Both audio outputs silent. Active scene/GPUcalls at endpoint are retained,not routeacceptance. Previousv33prefix448is historical and differentlayout;new/oldcontrol differ199videoframes.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',packet)
    deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()});deps[str(report)]=sha(report);deps[str(rp)]=sha(rp)
    for path in deps:clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for label,cmd in [('Root',[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_native_status_v8.py'),'--brief']),('copied',[str(P/'runtime/python/bin/python3.12'),str(P/'workbench/portable_biwn.py'),'status'])]:
        q=subprocess.run(cmd,cwd='/',capture_output=True,text=True,timeout=180);(out/(label+'-status.txt')).write_text(q.stdout+q.stderr)
        assert q.returncode==0,q.stderr
        assert '450 differing video frames of 1,000'in q.stdout and '190 native / 266 original'in q.stdout
    save(V/'record-strides-fixed-prefix-delivery-v1-current.json',dict(status='terminal_v34_fixed_input_review_published_Root_and_copied_status_verified',directory=str(out),new_predictions=0,new_training=False))
    print('v34 prefix450video differences;Root/copied status verified.',flush=True)

if __name__=='__main__':main()
