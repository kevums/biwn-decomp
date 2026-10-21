"""Freeze read-only onset evidence; distinguish observer ordinals from cycles."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone
import json

def main():
    out=V/'record-strides-timing-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    rows={};jobs={};deps={str(Path(__file__)):sha(__file__)}
    for lane in ['candidate','control']:
        p=V/f'record-strides-timing-trace-v1-{lane}-current.json';j=read(p)
        assert j['status']=='terminal_readonly_timing_trace_prior_1000_frame_hashes_preserved'
        for path,h in j['source_sha256'].items():assert sha(path)==h,path
        assert j['prior_prefix_all_recorded_CPU_RAM_GPU_DSP_video_hashes_identical']
        jobs[lane]=j;rows[lane]=[json.loads(x)for x in Path(j['trace']).read_text().splitlines()]
        deps[str(p)]=sha(p);deps.update(j['source_sha256']);save(out/(lane+'-job.json'),j)
    common=0
    for a,b in zip(rows['candidate'],rows['control']):
        if a!=b:break
        common+=1
    assert common==18
    starts={lane:[x for x in a if x['pc']==0x17e0e]for lane,a in rows.items()}
    assert starts['candidate'][0]==starts['control'][0]
    assert starts['candidate'][0]['frame']==376 and starts['candidate'][0]['instruction_ordinal']==5964982
    assert [starts[lane][1]['frame']for lane in ['candidate','control']]==[379,378]
    ends={lane:[x for x in a if x['pc']==(1498912 if lane=='candidate'else 0x17f12)]for lane,a in rows.items()}
    report=ROOT/'reports/BIWN v34 Scene Timing Onset Review.txt'
    facts=dict(status='terminal_readonly_scene_timing_onset_localized_cause_not_resolved',directory=str(out),report=str(report),profile='deck-shared-v34-record-strides-v1',
        traced_frame_range=[370,390],candidate_events=len(rows['candidate']),control_events=len(rows['control']),identical_observed_events_before_branch=common,
        first_scene_entry_frame=376,first_scene_entry_observer_ordinal=5964982,first_scene_entry_event_identical=True,
        first_scene_return_observed_frames={lane:a[0]['frame']for lane,a in ends.items()},
        second_scene_entry_frames={lane:a[1]['frame']for lane,a in starts.items()},
        scene_entries_in_trace_window={lane:len(a)for lane,a in starts.items()},
        candidate_and_control_each_preserve_prior_1000_frame_CPU_RAM_GPU_DSP_video_hashes=True,
        cause_resolved=False,isolated_stride_timing=False,cycle_cost_measured=False,run_speed_ratio_measured=False,
        new_predictions=0,new_training=False,host_guest_RAM_writes=0,installed_preview_changed=False,
        next_action='Profile instructions and original logical stages inside the first scene call,including internal clear/record/rotation/display and mailbox wait work. Separate logical result equivalence from the compiled scheduling/timing changes;do not insert guessed delays or relax fidelity masks.',
        scope='Host-only PC/task/physical-stack/logical-frame/GPU-control logging. No execution ownership or guest-state changes. The observer ordinal counts callbacks,not retired cycles;native return bridge and original RTS are different boundaries. First scene entry is identical;later scene cadence differs. This localizes onset to scene-path execution but does not identify one helper/algorithm or prove causal cycle equivalence. Copied UI/model/training behavior was not exercised.')
    report.write_text('BIWN v34 — scene timing onset\n\n'
        'The read-only trace retains196candidate/240control events at selected scene/provider boundaries during frames370–390. Both instrumented1000frame runs exactly reproduce every recorded video,CPU,fullRAM,GPU,DSP and held-button hash/value from their corresponding uninstrumented fixed-input prefix. No host guest-state writes or execution ownership.\n\n'
        'The first18selected events agree byte-for-byte,through the first scene entry17E0E at frame376,observer ordinal5964982,taskC0D28,return17DE0. Both first returns are observed in frame377,but the second scene starts379candidate/378control. There are7candidate/9control scene entries in the traced window;the ninth control call remains outside the logged return window. This is scene-cadence evidence,not a gameplay speed ratio.\n\n'
        'The compiled scene return bridge and original finalRTS are different observation boundaries. The callback ordinal is not an instruction-cycle cost. The trace cannot isolate the stride edit or prove which helper caused the timing change. The standard1000frame comparison still has450video differences(first378),CPU/GPU divergence376,identical heldbuttons and DSPstate,zero nonzeroaudio. Original-control global native providers are retained.\n\n'+facts['next_action']+'\n')
    facts['source_sha256']={**deps,str(report):sha(report)};save(out/'review.json',facts);rp=V/'record-strides-timing-reviewed-v1-current.json';save(rp,facts)
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
    packet=read(w['packet']);save(out/'before-packet.json',packet)
    public={k:v for k,v in facts.items()if k!='source_sha256'}
    packet['record_strides_scene_timing_progress']=public
    packet['native_scene_draw_progress']['scene_timing_trace_progress']=public
    packet['native_geometry_records_progress']['scene_timing_trace_progress']=public
    packet['native_scene_draw_progress']['next_action']=facts['next_action']+' Continue remaining CPU/GPU/DSP/HLE source,silent audio,same-console rebuilding,useful training and copied-weight Chat usability.'
    packet['checked_current_summary']+=' Read-only trace preserves prior1000frameCPU/RAM/GPU/DSP/video hashes in both lanes:18selected events agree through scene entry376at same observerordinal;secondscene starts379candidate/378control. Cause unresolved;callbackcounts are not cycles or runspeed.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',packet)
    deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()});deps[str(report)]=sha(report);deps[str(rp)]=sha(rp)
    for path in deps:clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text((ROOT/'reports/BIWN Fresh Record Matrix Route Review.txt').read_text()+'\n'+(ROOT/'reports/BIWN v34 Identical Input Prefix Review.txt').read_text()+'\n'+report.read_text())
    print('Scene timing onset localized;cause and broader fidelity remain open.',flush=True)

if __name__=='__main__':main()
