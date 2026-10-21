"""One-shot full merchant route: new-core NULL and portable IRQ-entry owner."""
import json
import os
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'verification/CPU-IRQ-full-route-pipeline-state.json'
def save(**fields):
    value=json.loads(STATE.read_text())if STATE.exists()else{}
    value.update(fields);STATE.write_text(json.dumps(value,indent=2)+'\n')
def main():
    assert not STATE.exists(),'Existing pipeline state must be reviewed instead of overwritten.'
    core=json.loads((ROOT/'verification/CPU-IRQ-owner-experimental-candidate.json').read_text())['core_path']
    save(status='running_replays',pid=os.getpid());workers=[]
    for label,extra in [('NULL',[]),('source',['--source-CPU-IRQ-entry'])]:
        out=ROOT/f'runs/CPU-IRQ-whole-merchant-{label}';assert not out.exists()
        command=[sys.executable,str(ROOT/'scripts/probe_biwn_fresh_CD_boot.py'),'--boot','hle','--frames','23538','--core',core,'--frame-controller-script',str(ROOT/'verification/whole-merchant-global-fixed-input.json'),'--capture-audio','--no-publish','--output',str(out)]+extra
        with (ROOT/f'runs/CPU-IRQ-whole-merchant-{label}.log').open('w')as log:worker=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        job=dict(status='running',pid=worker.pid,directory=str(out),command=command,scope='23538fresh normal pad frames; originalCPU/GPU/DSP. Source variant owns IRQ entry after original device ACK. Original IRQ selection/ACK/hostcommit/prefetch/cyclecharge/HLE/devices remain; full comparison pending.',whole_game_complete=False)
        path=ROOT/f'verification/CPU-IRQ-whole-merchant-{label}-job.json';path.write_text(json.dumps(job,indent=2)+'\n');workers.append((worker,job,path))
    save(worker_pids={label:worker.pid for label,(worker,_,_)in zip(['NULL','source'],workers)})
    for worker,job,path in workers:
        code=worker.wait();job.update(status='terminal_completed_pending_comparison'if code==0 else'terminal_failed',exit_code=code);path.write_text(json.dumps(job,indent=2)+'\n');assert code==0,(path,code)
    save(status='comparing')
    for reference,candidate,kind,extra in [('DSP-router-core-whole-merchant-original','CPU-IRQ-whole-merchant-NULL','NULL',[]),('CPU-IRQ-whole-merchant-NULL','CPU-IRQ-whole-merchant-source','source',['--require-source-IRQ'])]:
        output=ROOT/f'verification/CPU-IRQ-whole-merchant-{kind}-comparison.json'
        command=[sys.executable,str(ROOT/'scripts/compare_biwn_fresh_CPU_IRQ.py'),'--reference',str(ROOT/'runs'/reference),'--candidate',str(ROOT/'runs'/candidate),'--frames','23538','--output',str(output)]+extra
        save(comparison_command=command);subprocess.run(command,check=True)
    for _,job,path in workers:
        job.update(status='terminal_verified_comparison');path.write_text(json.dumps(job,indent=2)+'\n')
    save(status='terminal_verified_comparison')
if __name__=='__main__':
    try:main()
    except Exception as error:save(status='terminal_failed',error=repr(error));raise
