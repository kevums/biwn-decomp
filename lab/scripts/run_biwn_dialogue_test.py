"""One-command 32-frame natural merchant CPU/GPU/DSP comparison.

Restores an original checkpoint. Hardware/IRQ/firmware services remain original.
"""
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--with-local-review',action='store_true');args=parser.parse_args()
    out=ROOT/'runs/dialogue-launcher'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    print('32-frame merchant audio test: reconstructed CPU/GPU/DSP, original checkpoint and hardware services.',flush=True)
    print('Prompts, commands and results: '+str(out),flush=True)
    core=Path(json.loads((ROOT/'verification/DSP-owner-experimental-candidate.json').read_text())['core_path'])
    common=[sys.executable,str(ROOT/'scripts/probe_biwn_frame_CPU_owner.py'),'--warm-frames','600','--frames','32',
            '--restore-original-report',str(ROOT/'runs/merchant-DSP-owner-core-original-reference/checkpoint-00015906/report.json'),
            '--frame-controller-script',str(ROOT/'verification/merchant-audio-start-fixed-continuation-input.json'),
            '--native-CPU-bridge','--extended-CPU','--CPU-candidate',str(ROOT/'verification/merchant-CPU-experimental-candidate.json'),
            '--native-CPU-candidate',str(ROOT/'verification/combined-merchant-native-CPU-experimental-candidate.json'),'--core',str(core),'--capture-audio']
    commands=[]
    for mode in ['reference','C']:
        cmd=common+['--mode',mode,'--output',str(out/mode),'--OP-GPU-mode','trace'if mode=='reference'else'C','--regular-GPU-mode','none'if mode=='reference'else'C']
        if mode=='C':cmd+=['--renderer-bundles','--renderer-overlays','--material-bundles','--control-bundles','--setup-bundles','--native-GPU-bridge','--GPU-frame-only','--native-GPU-candidate',str(ROOT/'verification/movie-trampoline-shared-GPU-experimental-candidate.json'),'--OP-GPU-candidate',str(ROOT/'verification/OP-private-experimental-candidate.json'),'--native-DSP-owner']
        commands.append(cmd);(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');print('Running '+mode,flush=True)
        with (out/(mode+'.log')).open('w')as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT.parents[1])
        if result.returncode:raise SystemExit('Execution rejected; inspect '+str(out/(mode+'.log')))
    cmd=[sys.executable,str(ROOT/'scripts/compare_biwn_frame_route.py'),'--C-run',str(out/'C'),'--reference',str(out/'reference'),'--output',str(out/'report.json')]
    with (out/'comparison.log').open('w')as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:raise SystemExit('Comparison failed; inspect '+str(out/'comparison.log'))
    proof=json.loads((out/'report.json').read_text());run=json.loads((out/'C/report.json').read_text());proof.update(frontend_nonzero_audio_samples=run['audio']['nonzero_samples'],reconstructed_DSP_playback_verified=True,DSP_scope='Captured checkpoint32frames only; original IRQ/device/firmware services, no standalone/fullgame proof.',new_training=False,coordinator_authored=True)
    (out/'report.json').write_text(json.dumps(proof,indent=2)+'\n');print('Report: '+str(out/'report.json'),flush=True)
    print('Passed:32frames; CPU/GPU/DSP and PCM exact. Nonzero audio samples:'+str(proof['frontend_nonzero_audio_samples']),flush=True)
    if args.with_local_review:
        import fcntl
        sys.path.insert(0,str(ROOT));import lab
        evidence={k:proof[k]for k in ['status','frames','CPU_owned_instructions','GPU_counts','frontend_nonzero_audio_samples','reconstructed_DSP_playback_verified','whole_game_complete']}
        task='In under65words explain only these supplied facts: this32frame captured-checkpoint CPU/GPU/DSP comparison passed and PCM matched the original; original hardware/IRQ/firmware services remain; full game and complete combined dialogue remain unfinished. Your role is to explain the supplied comparison result. Use plain language and include only these facts.'
        with (ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            response=lab.generate('advertising',lab.COMMON,json.dumps({'task':task,'evidence':evidence}),320)
        (out/'local-reader.json').write_text(json.dumps(response,indent=2)+'\n')
        (out/'prompts-and-responses.txt').write_text('LOCAL READER\nREQUEST:\n'+json.dumps(response['request'],indent=2)+'\nRESPONSE:\n'+response['text']+'\n')
        print(response['text'],flush=True)

if __name__=='__main__':main()
