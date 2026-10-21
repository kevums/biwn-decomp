"""Strict instruction/event/pixel proof across120world updates, both plans."""
from pathlib import Path
from datetime import datetime,timezone
import json,struct,collections,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',type=Path);parser.add_argument('--no-publish',action='store_true');args=parser.parse_args();folder=args.run_root or Path(read(ROOT/'runs/world-boundary-full-pointer.json')['directory']);commands=read(folder/'commands.json');plans=sorted({v['plan']for v in commands});assert len(commands)==len(plans)*2 and all(v['exit_code']==0 for v in commands);assert all({v['mode']for v in commands if v['plan']==plan}=={'native','C'}for plan in plans);runs={};requested={int(v['command'][v['command'].index('--rounds')+1])for v in commands};assert len(requested)==1;rounds=requested.pop()
    for plan in plans:
        ds={m:Path((folder/f'world-boundary-{m}-{plan}.log').read_text().splitlines()[0])for m in ['native','C']};n,c=ds['native'],ds['C']
        ns,cs=read(n/'native-startup.json')['startup'],read(c/'C-startup.json')['startup']
        for k in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:assert ns[k]==cs[k],(plan,'startup',k)
        for stage in ['startup','world']:
            for suffix in ['instruction-PCs.bin','CPU-state-hashes.bin','instruction-costs.bin']:assert(n/f'native-{stage}-{suffix}').read_bytes()==(c/f'C-{stage}-{suffix}').read_bytes(),(plan,stage,suffix)
            assert read(n/f'native-{stage}-boundary-events.json')==read(c/f'C-{stage}-boundary-events.json'),(plan,stage,'events')
            assert(n/f'native-{stage}-framebuffer.bin').read_bytes()==(c/f'C-{stage}-framebuffer.bin').read_bytes(),(plan,stage,'framebuffer')
            assert read(n/f'native-{stage}-framebuffer.json')==read(c/f'C-{stage}-framebuffer.json'),(plan,stage,'framebuffer layout')
        for suffix in ['world-return-checkpoints.json','JERRY-events.json','music.json','world-GPU-IRQ-resumes.json']:assert read(n/('native-'+suffix))==read(c/('C-'+suffix)),(plan,suffix)
        host_layout='--frontend-video-layout' in commands[0]['command']
        if host_layout:
            assert read(n/'native-host-video-layout-changes.json')==read(c/'C-host-video-layout-changes.json'),(plan,'host layout changes')
            for stage in ['startup','world']:
                layout=read(c/f'C-{stage}-framebuffer.json')
                assert layout['screen_pitch_pixels']==layout['tom_width']==layout['frontend_width'] and layout['tom_height']==layout['frontend_height'],(plan,stage,'host layout mismatch')
        nr,cr=read(n/'native.json'),read(c/'C.json')
        for k in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert nr[k]==cr[k],(plan,'world',k)
        assert cr['C_original_CPU_attempts']==cr['C_original_GPU_opcodes']==cr['C_original_DSP_opcodes']==0, (plan,'original processor escape')
        assert nr['timer_events']==cr['timer_events']==0
        points=read(c/'C-world-return-checkpoints.json');assert len(points)==rounds and all('framebuffer_sha256'in v for v in points)
        cost_bytes=(n/'native-world-instruction-costs.bin').read_bytes();actual_bytes=(n/'native-world-original-cycle-costs.bin').read_bytes();instructions=len(cost_bytes)//8;assert len(cost_bytes)%8==0 and len(actual_bytes)==instructions*4;deltas=collections.Counter();actual_cycles=0
        for (pc,cost),(v,) in zip(struct.iter_unpack('>II',cost_bytes),struct.iter_unpack('>I',actual_bytes)):
            actual_cycles+=v
            if v!=cost:deltas[(pc,v-cost)]+=1
        assert all(pc==0xe7d4 and delta==56 for pc,delta in deltas)
        clock=read(c/'C-world-boundary-events.json');assert clock['CPU_cycles']==actual_cycles
        native_OP=read(n/'world-OP-GPU-reference-slices/report.json');owned=read(c/'C-world-OP-GPU-owner.json');assert native_OP['calls']==owned['calls']
        for a,b in zip(native_OP['records'],owned['records']):
            for k in ['index','cycles','before_GPU_sha256','after_GPU_sha256']:assert a[k]==b[k],(plan,'world OP',k)
        assert owned['original_GPU_opcodes_on_C_side']==0
        jerry=read(c/'C-JERRY-events.json');silent=all(v['PCM']==[0,0]for v in jerry['events'])
        runs[plan]=dict(sources={m:str(d)for m,d in ds.items()},world_returns=rounds,framebuffer_layout=read(c/'C-world-framebuffer.json'),original_CPU_GPU_DSP_execution_on_C_side=0,world_CPU_instructions=instructions,world_CPU_cycles=actual_cycles,world_elapsed_us=clock['elapsed_us'],world_main_events=clock['main_events'],world_JERRY_events=clock['JERRY_events'],world_GPU_timer_handlers=len(clock['GPU_timers']),world_OP_GPU_slices=owned['calls'],world_OP_GPU_source_instructions=owned['source_instructions'],pending_GPU_IRQ_services=len(read(c/'C-world-GPU-IRQ-resumes.json')),all_CPU_state_event_checkpoint_and_pixel_bytes_match=True,distinct_framebuffer_hashes=len({v['framebuffer_sha256']for v in points}),all_recorded_PCM_pairs_silent=silent,final_player=points[-1]['player'])
    out=ROOT/'verification/world-boundary-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);report=dict(status=f'startup_and{rounds}world_CPU_boundary_main_JERRY_OP_GPU_and_pixels_'+('input_control_match'if set(plans)=={'up-left','none'}else'original_C_match'),directory=str(out),run_root=str(folder),runs=runs,event_core=commands[0]['command'][commands[0]['command'].index('--event-core')+1],CPU_library=next(v['command'][v['command'].index('--cpu-library')+1]for v in commands if v['mode']=='C'),host_video_geometry_refresh='--frontend-video-layout' in commands[0]['command'],global_cycle_scheduling_verified=False,whole_game_complete=False,coordinator_authored=True,new_training=False,limits=['CPU instruction costs now advance main/JERRY queues through startup and world tasks, with C-owned OP GPU slices and source pending IRQ continuations. GPU/DSP/blitter remain synchronous; no asynchronous cross-processor/physical timing proof.','Shared1xhost framebuffer allocation/checkpoint hashes match. Not RetroArch/composited/physical scanout or a standalone playable application.','Platform HLE/authentication bypass, silent PCM and remaining scenes/game paths remain unfinished. Decoder scratch retained; only current disabled pipeline/DRAM timing profile.'])
    current=read(ROOT/'verification/world-single-step-current.json')
    if report['CPU_library']==current['library']:
        report['new_fixed_CPU_instruction_cases']=current.get('new_fixed_CPU_instruction_cases',0)
    report['world_clock_targets_idempotent']='--world-stable-clock' in commands[0]['command']
    report['world_checkpoints_before_next_CPU_IRQ_entry']=True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not args.no_publish:(ROOT/'verification/world-boundary-runtime-current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
