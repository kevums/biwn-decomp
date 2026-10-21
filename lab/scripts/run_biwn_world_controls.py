"""Exercise ordinary world movement from an exact original checkpoint."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def review_comparison(out):
    result=json.loads((out/'comparison.json').read_text())
    failed={key for key,value in result['checks'].items()if not value}
    if not failed:
        return dict(status='terminal_world_controls_match',comparison=str(out/'comparison.json'),
                    frames=result['frames'],DSP_execution_verified=True)
    # Preserve the combined gate's failure. A stopped DSP cannot establish DSP
    # implementation coverage; the exact CPU/GPU and full-state evidence is
    # still useful as an explicitly narrower observation.
    assert failed=={'DSP_owned_positive'},failed
    rebuilt=json.loads((out/'C/report.json').read_text())
    dsp=json.loads(Path(rebuilt['DSP_report']).read_text())
    assert dsp['calls']==dsp['owned']==dsp['uncovered']==dsp['errors']==0
    assert all(dsp['core_counts'][key]==0 for key in ['Owned','Original','Rejected'])
    return dict(status='terminal_CPU_GPU_controls_match_DSP_inactive',
                comparison=str(out/'comparison.json'),raw_combined_gate_passed=False,
                combined_gate_failed_checks=sorted(failed),frames=result['frames'],
                CPU_instructions=result['owned_CPU_instructions'],GPU_counts=result['GPU_counts'],
                DSP_execution_verified=False,
                scope='CPU instruction states/costs, per-frame RAM/video/audio and full final state match. DSP did not execute and audio was silent; this run supplies no DSP or audible-output coverage.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--CPU-candidate',type=Path,default=ROOT/'verification/zero-warm-startup-CPU-experimental-candidate.json')
    parser.add_argument('--native-CPU-candidate',type=Path,default=ROOT/'verification/zero-warm-startup-native-CPU-experimental-candidate.json')
    parser.add_argument('--GPU-candidate',type=Path,default=ROOT/'verification/startup-variant-shared-GPU-experimental-candidate.json')
    parser.add_argument('--reuse-reference',type=Path)
    parser.add_argument('--exit-elevator',action='store_true')
    parser.add_argument('--checkpoint',type=Path,default=ROOT/'runs/zero-warm-whole-merchant-reference/report.json')
    parser.add_argument('--frames',type=int,default=360)
    parser.add_argument('--input-script',type=Path)
    parser.add_argument('--experimental-code-overlay',type=Path)
    parser.add_argument('--capture-frame',type=int,action='append')
    args=parser.parse_args()
    out = ROOT/'runs'/('world-controls-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    checkpoint = args.checkpoint.resolve()
    original = json.loads(checkpoint.read_text())
    core = ROOT/'verification/DSP-music-context-build/20261016T095846.040285Z/source/virtualjaguar_libretro.dylib'
    assert original['mode']=='reference' and original['owned_CPU_instructions']==0 and not original['errors']
    frames=args.frames
    assert 1<=frames<=1200
    assert frames==360 or args.input_script, 'Longer routes require an explicit input schedule'
    windows=[dict(start_frame=start,stop_frame=stop,buttons=buttons) for start,stop,buttons in
             [(1,61,['U']),(61,91,['R']),(91,151,['U']),(151,181,['L']),
              (181,241,['D']),(241,271,['L']),(271,331,['U'])]]
    if args.exit_elevator:
        windows=[dict(start_frame=start,stop_frame=stop,buttons=buttons)for start,stop,buttons in
                 [(1,10,['C']),(20,80,['U']),(80,110,['R']),(110,170,['U']),
                  (170,200,['L']),(200,260,['D']),(260,290,['L']),(290,350,['U'])]]
    if args.input_script:
        windows=json.loads(args.input_script.read_text())['windows']
        for window in windows:
            assert 1<=window['start_frame']<window['stop_frame']<=frames+1
            from biwn_controller import BUTTONS
            assert set(window['buttons'])<=BUTTONS
    schedule=out/'input.json';schedule.write_text(json.dumps(dict(windows=windows),indent=2)+'\n')
    common=[sys.executable,str(ROOT/'scripts/probe_biwn_frame_CPU_owner.py'),
            '--warm-frames','0','--frames',str(frames),'--core',str(core),
            '--restore-original-report',str(checkpoint),'--frame-controller-script',str(schedule),
            '--capture-audio','--native-CPU-bridge','--extended-CPU',
            '--CPU-candidate',str(args.CPU_candidate.resolve()),
            '--native-CPU-candidate',str(args.native_CPU_candidate.resolve())]
    if args.experimental_code_overlay:common+=['--experimental-code-overlay',str(args.experimental_code_overlay.resolve())]
    captures=sorted(set(args.capture_frame or [1,max(1,frames//6),max(1,frames//2),max(1,2*frames//3),frames]))
    assert len(captures)<=8 and all(1<=frame<=frames for frame in captures)
    for frame in captures:common+=['--capture-frame',str(frame)]
    gpu=['--regular-GPU-mode','C','--renderer-bundles','--renderer-overlays','--material-bundles',
         '--control-bundles','--setup-bundles','--native-GPU-bridge','--GPU-frame-only',
         '--native-GPU-candidate',str(args.GPU_candidate.resolve()),
         '--stop-on-GPU-original']
    dsp=['--native-DSP-owner','--DSP-owner-kind','router','--require-owned-DSP',
         '--DSP-router-candidate',str(ROOT/'verification/fast-DSP-router-experimental-candidate.json')]
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),commands=[],
               scope='Ordinary controller sequence (menu exit requested='+str(args.exit_elevator)+'); exact original checkpoint. Explicit game overlay='+str(args.experimental_code_overlay)+'; source CPU/GPU/DSP under emulator IRQ/HLE/devices. No live keyboard or standalone claim.')
    def save():
        text=json.dumps(state,indent=2)+'\n';(out/'protocol.json').write_text(text)
        (ROOT/'verification/world-controls-current.json').write_text(text)
    def run(phase,command,allow_comparison_failure=False):
        state.update(status='running_'+phase)
        state['commands'].append(dict(phase=phase,command=command))
        with(out/(phase+'.log')).open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;save();print(phase,'PID',child.pid,flush=True)
            code=child.wait()
        state['last_exit_code']=code;save()
        if code and not (allow_comparison_failure and code==1):raise RuntimeError(f'{phase} exited {code}; see {out/(phase+".log")}')
    save();print(out,flush=True)
    try:
        if args.reuse_reference:
            reused=args.reuse_reference.resolve();saved=json.loads((reused/'report.json').read_text())
            assert saved['mode']=='reference' and not saved['errors'] and len(saved['frames'])==frames
            assert saved['core_sha256']==hashlib.sha256(core.read_bytes()).hexdigest()
            assert saved['frame_controller_script_sha256']==hashlib.sha256(schedule.read_bytes()).hexdigest()
            saved_overlay=saved.get('experimental_code_overlay')
            expected_overlay=hashlib.sha256(args.experimental_code_overlay.read_bytes()).hexdigest()if args.experimental_code_overlay else None
            assert (saved_overlay['sha256']if saved_overlay else None)==expected_overlay
            assert saved['restored_original_checkpoint']['report']==str(checkpoint)
            assert saved['restored_original_checkpoint']['exact_machine_and_RAM_before_execution']is True
            (out/'reference').symlink_to(reused,target_is_directory=True)
            state['reused_reference']=str(reused);save()
        else:
            run('reference',common+['--mode','reference','--output',str(out/'reference')])
        run('C',common+['--mode','C',*gpu,*dsp,'--output',str(out/'C')])
        comparison=out/'comparison.json'
        compare_command=[sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),
                       '--C-run',str(out/'C'),'--reference',str(out/'reference'),
                       '--expected-frames',str(frames),'--original-checkpoint-report',str(checkpoint),
                       '--output',str(comparison)]
        if args.experimental_code_overlay:compare_command+=['--experimental-code-overlay',str(args.experimental_code_overlay.resolve())]
        run('compare',compare_command,allow_comparison_failure=True)
        state.update(review_comparison(out))
        save();print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise


if __name__=='__main__':main()
