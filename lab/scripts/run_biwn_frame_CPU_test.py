"""Fresh normal-frame CPU comparisons, with optional saved local-model review."""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames', type=int, choices=[4,60], default=60)
    parser.add_argument('--with-local-review', action='store_true')
    args = parser.parse_args()
    folder = ROOT / 'runs/frame-CPU-launcher' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    folder.mkdir(parents=True)
    print('CPU reconstruction under the normal frame scheduler; original startup/GPU/DSP/HLE providers.', flush=True)
    print('Exact commands and traces: ' + str(folder), flush=True)
    jobs, records = [], []
    try:
        for direction in ['none','U']:
            for mode in ['baseline','reference','C']:
                path = folder / (direction+'-'+mode)
                command = [sys.executable, str(ROOT / 'scripts/probe_biwn_frame_CPU_owner.py'),
                           '--mode',mode,'--direction',direction,'--frames',str(args.frames),'--output',str(path)]
                log = (folder / (direction+'-'+mode+'.log')).open('w')
                process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                jobs.append((process,log,time.monotonic()))
                records.append(dict(mode=mode,direction=direction,command=command,pid=process.pid,output=str(path)))
        save(folder / 'commands.json',records)
        for row,(process,log,started) in zip(records,jobs):
            try:
                row['exit_code'] = process.wait(timeout=max(1,300-(time.monotonic()-started)))
            except subprocess.TimeoutExpired:
                process.terminate();process.wait(timeout=5);row['exit_code']=124
            log.close();save(folder / 'commands.json',records)
            print(row['direction']+' / '+row['mode']+': exit '+str(row['exit_code']),flush=True)
        if any(row['exit_code'] for row in records):
            raise RuntimeError('A run rejected or failed; no passing comparison published. Inspect saved logs.')
        check = subprocess.run([sys.executable,str(ROOT / 'scripts/record_biwn_frame_CPU_owner.py'),
                                '--run-root',str(folder)],capture_output=True,text=True)
        (folder / 'comparison.log').write_text(check.stdout+check.stderr)
        if check.returncode:
            raise RuntimeError('Strict comparison failed. See comparison.log.')
        report = Path(check.stdout.strip()) / 'report.json'
        proof = json.loads(report.read_text())
        seen = set()
        for root in [ROOT,Path.home() / '.lmstudio/local-ai-lab']:
            session = json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())
            path = Path(session['directory']) / 'emulator-runtime/summary.json'
            if path in seen:continue
            seen.add(path);summary=json.loads(path.read_text())
            previous=summary.get('frame_scheduler_CPU_component')
            if not previous or max(v['frames'] for v in previous['runs'].values()) <= args.frames:
                summary['frame_scheduler_CPU_component']={**proof,'report':str(report)}
                save(path,summary)
        print('PASS: instruction states/costs, frame RAM/pixels and complete serialized machine match.',flush=True)
        print('Report: '+str(report),flush=True)
        if args.with_local_review:
            question=('Fetch boot_loader once. In under100words summarize frame_scheduler_CPU_component: '
                      'normal frame count, original warm startup, owned CPU count, original GPU/DSP providers, '
                      'audio/full-game limits and authorship. Distinguish this from the1200world-task proof. '
                      'Do not claim whole-game completion, new training or independent model verification.')
            result=subprocess.run([sys.executable,str(ROOT / 'scripts/test_firmware_CD_routing.py'),
                                   '--thinking-off','--question',question],capture_output=True,text=True)
            (folder / 'local-model.log').write_text(result.stdout+result.stderr)
            if result.returncode:
                print('Machine comparison passed; local summary failed. Inspect local-model.log.',flush=True)
            else:
                pointer=json.loads((ROOT / 'verification/easy-firmware-CD-routing-pointer.json').read_text())
                protocol=Path(pointer['directory']) / 'protocol.json';output=json.loads(protocol.read_text())
                print('Local Assistant (SDK, same daily weights; saved for source review):\n'+output['results'][0]['answer'],flush=True)
                print('Exact prompts/responses: '+str(protocol),flush=True)
        print('CPU component only; original warm/GPU/DSP/HLE remain providers. Complete C game unfinished.',flush=True)
    finally:
        for process,log,_ in jobs:
            if process.poll() is None:process.terminate();process.wait()
            if not log.closed:log.close()


if __name__=='__main__':main()
