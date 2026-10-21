"""One command: four isolated reference/C runs, comparison, optional local review."""
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--with-local-review',action='store_true');parser.add_argument('--rounds',type=int,default=120);args=parser.parse_args()
    folder=ROOT/'runs/fresh-HLE-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');folder.mkdir(parents=True)
    core=Path(json.loads((ROOT/'verification/BIWN-video-layout-current.json').read_text())['core_path'])
    library=Path(json.loads((ROOT/'verification/world-single-step-current.json').read_text())['library'])
    base=[sys.executable,str(ROOT/'scripts/check_biwn_entry_natural_task_rounds.py'),'--fresh-hle','--hle-assets','--hle-asset-clock','--loader-cycle-clock','--prefix-instruction-probe','--prefix-instruction-clock','--startup-clock-probe','--startup-instruction-probe','--startup-state-probe','--startup-cost-probe','--startup-elapsed-clock','--startup-single-step','--startup-boundary-events','--world-instruction-probe','--world-boundary-events','--framebuffer-probe','--frontend-video-layout','--world-stable-clock','--cpu-library',str(library),'--rounds',str(args.rounds),
          '--music-words','--jerry-events','--no-publish','--event-core',str(core)]+(['--sustained-input']if args.rounds>120 else[])
    jobs=[];records=[]
    try:
        for mode,plan in [('native','up-left'),('C','up-left'),('native','none'),('C','none')]:
            command=base+['--execution-mode',mode,'--input-plan',plan]+(['--OP-GPU-owner','--world-single-step']if mode=='C'else[])
            path=folder/('world-boundary-'+mode+'-'+plan+'.log');log=path.open('w')
            process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);jobs.append((process,log))
            records.append(dict(mode=mode,plan=plan,role='Original reference' if mode=='native' else 'Reconstructed C',input_plan=plan,
                                pid=process.pid,command=command,log=str(path)))
            print(records[-1]['role']+' / '+plan+': running; '+str(path),flush=True)
        (folder/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
        failed=[]
        for index,(process,log) in enumerate(jobs):
            code=process.wait();log.close();records[index]['exit_code']=code
            print(records[index]['role']+' / '+records[index]['input_plan']+': exit '+str(code),flush=True)
            if code:failed.append(records[index]['log'])
        (folder/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
        assert not failed, 'Run failed; inspect '+', '.join(failed)
        command=[sys.executable,str(ROOT/'scripts/record_biwn_world_boundary_runtime.py'),'--run-root',str(folder)]
        result=subprocess.run(command,capture_output=True,text=True);(folder/'comparison.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0,result.stderr
        audit=Path(result.stdout.strip());print('State/trace/event comparisons passed. Audit: '+str(audit),flush=True)
        proof=json.loads((audit/'report.json').read_text())
        for root in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
            session=json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text());path=Path(session['directory'])/'emulator-runtime/summary.json';summary=json.loads(path.read_text());summary['world_extended_runtime_comparison' if args.rounds>120 else 'world_boundary_runtime_comparison']={**proof,'report':str(audit/'report.json')};path.write_text(json.dumps(summary,indent=2)+'\n')
        if args.with_local_review:
            loaded=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True))
            ready=len(loaded)==1 and loaded[0].get('identifier')=='advertising-scholar' and loaded[0].get('contextLength')==32768 and loaded[0].get('parallel')==1
            if not ready:
                subprocess.run([str(ROOT/'lab'),'load','advertising','--profile','mac64-chat'],check=True)
            else:
                print('Reusing the loaded daily local model.',flush=True)
            question='Fetch boot_loader once. In at most 100 words explain the longest currently verified BIWN world run: task updates, simulated duration, CPU execution count versus added C instruction cases, pixel result, and remaining audio/playability/timing limits. Say who authored and tested the reconstruction. Do not claim new training or independent model verification.'
            command=[sys.executable,str(ROOT/'scripts/test_firmware_CD_routing.py'),'--thinking-off','--role','game_assistant','--question',question]
            result=subprocess.run(command,capture_output=True,text=True);(folder/'local-model.log').write_text(result.stdout+result.stderr)
            assert result.returncode==0,result.stderr
            pointer=json.loads((ROOT/'verification/easy-firmware-CD-routing-pointer.json').read_text())
            protocol=Path(pointer['directory'])/'protocol.json';output=json.loads(protocol.read_text())
            print('\nLOCAL GAME ASSISTANT (LM Studio SDK; same daily weights, not native Chat):\n'+output['results'][0]['answer'],flush=True)
            print('Exact prompts/responses: '+str(protocol),flush=True)
            print('Model answer saved for review; the state comparisons are separate emulator evidence.',flush=True)
        print('Bounded game proof passed. Platform HLE, synchronous GPU/DSP/blitter services and silent audio remain; full decompile incomplete.',flush=True)
    finally:
        for process,log in jobs:
            if process.poll() is None:process.terminate();process.wait()
            if not log.closed:log.close()


if __name__=='__main__':main()
