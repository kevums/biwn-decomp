"""Check compact transport on nonzero game-disc audio, from an original capture."""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT/'verification/compact-DSP-game-audio-current.json'


def main():
    if STATE.exists():
        prior=json.loads(STATE.read_text())
        assert prior['status'].startswith('terminal_'), 'Inspect existing job and handle; do not restart active work'
    candidate_path=ROOT/'verification/compact-DSP-router-experimental-candidate.json'
    candidate=json.loads(candidate_path.read_text())
    core=Path(candidate['core_path'])
    assert hashlib.sha256(core.read_bytes()).hexdigest()==candidate['required_core_sha256']
    out=ROOT/'runs'/('compact-DSP-game-audio-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    windows=json.loads((ROOT/'verification/whole-merchant-global-fixed-input.json').read_text())['windows']
    capture_frames,span=15900,600
    def schedule(start,length,path):
        selected=[]
        for window in windows:
            first=max(window['start_frame'],start+1)
            stop=min(window['stop_frame'],start+length+1)
            if first<stop:selected.append(dict(start_frame=first-start,stop_frame=stop-start,buttons=window['buttons']))
        path.write_text(json.dumps(dict(windows=selected),indent=2)+'\n')
    schedule(0,capture_frames,out/'boot-input.json')
    schedule(capture_frames,span,out/'span-input.json')
    native=ROOT/'verification/compact-DSP-unmodified-route-native-CPU-experimental-candidate.json'
    CPU=ROOT/'verification/zero-warm-startup-CPU-experimental-candidate.json'
    base=[sys.executable,str(ROOT/'scripts/probe_biwn_frame_CPU_owner.py'),
          '--warm-frames','0','--native-CPU-bridge','--extended-CPU',
          '--CPU-candidate',str(CPU),'--native-CPU-candidate',str(native),
          '--core',str(core),'--capture-audio']
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),commands=[],
        scope='Unmodified game image and ordinary fixed inputs. New-core original15900frame capture, followed by original versus sourceCPU/GPU/DSP600frame continuation. No experimental game-code overlay. IRQ/HLE/devices remain. Nonzero PCM and exact comparison required; not complete song/physical audio/standalone proof.')
    def save():
        data=json.dumps(state,indent=2)+'\n'
        STATE.write_text(data)
        (out/'protocol.json').write_text(data)
    def run(phase,command):
        state.update(status='running_'+phase,phase_command=command)
        state['commands'].append(dict(phase=phase,command=command))
        with (out/(phase+'.log')).open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;save()
            print(phase,'PID',child.pid,flush=True)
            code=child.wait()
        state['last_exit_code']=code;save()
        assert code==0,(phase,code)
    save()
    try:
        run('original_capture',base+['--mode','reference','--frames',str(capture_frames),
            '--frame-controller-script',str(out/'boot-input.json'),'--no-instruction-trace',
            '--output',str(out/'boot')])
        checkpoint=out/'boot/report.json'
        saved=json.loads(checkpoint.read_text())
        assert saved['mode']=='reference' and saved['owned_CPU_instructions']==0
        assert not saved['errors'] and len(saved['frames'])==capture_frames
        continuation=['--frames',str(span),'--restore-original-report',str(checkpoint),
                      '--frame-controller-script',str(out/'span-input.json')]
        run('reference',base+['--mode','reference']+continuation+['--output',str(out/'reference')])
        original=json.loads((out/'reference/report.json').read_text())
        assert original['audio']['nonzero_samples']>0, 'No nonzero actual game audio in declared span'
        GPU=['--regular-GPU-mode','C','--renderer-bundles','--renderer-overlays',
             '--material-bundles','--control-bundles','--setup-bundles','--native-GPU-bridge',
             '--GPU-frame-only','--native-GPU-candidate',str(ROOT/'verification/startup-variant-shared-GPU-experimental-candidate.json'),
             '--stop-on-GPU-original']
        DSP=['--native-DSP-owner','--DSP-owner-kind','router','--DSP-router-candidate',str(candidate_path),'--require-owned-DSP']
        run('candidate',base+['--mode','C']+continuation+GPU+DSP+['--output',str(out/'C')])
        comparison=out/'comparison.json'
        run('comparison',[sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),
            '--C-run',str(out/'C'),'--reference',str(out/'reference'),'--expected-frames',str(span),
            '--original-checkpoint-report',str(checkpoint),'--output',str(comparison)])
        proof=json.loads(comparison.read_text())
        assert proof['status']=='CPU_GPU_DSP_frame_comparison_pass' and all(proof['checks'].values())
        rebuilt=json.loads((out/'C/report.json').read_text())
        assert rebuilt['audio']==original['audio'] and rebuilt['audio']['nonzero_samples']>0
        state.update(status='terminal_native_source_nonzero_game_audio_match',comparison=str(comparison),
                     audio=rebuilt['audio'],frames=span,whole_game_complete=False)
        save();print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise


if __name__=='__main__':main()
