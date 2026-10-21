"""Full fresh merchant route: source CPU/GPU/DSP and portable IRQ entry."""
import json
import os
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'verification/CPU-GPU-DSP-IRQ-full-route-pipeline-state.json'
def save(**fields):
    state=json.loads(STATE.read_text())if STATE.exists()else{}
    state.update(fields);STATE.write_text(json.dumps(state,indent=2)+'\n')
def main():
    assert not STATE.exists(),'Review existing pipeline rather than starting another.'
    start=json.loads((ROOT/'verification/CPU-GPU-DSP-IRQ-startup600-comparison.json').read_text())
    assert all(start['checks'].values())and start['source_IRQ_entry']['core']['Owned']>0
    command=json.loads((ROOT/'verification/CPU-GPU-DSP-IRQ-startup600-job.json').read_text())['command'][:]
    command[command.index('--frames')+1]='23538'
    command[command.index('--output')+1]=str(ROOT/'runs/CPU-GPU-DSP-IRQ-whole-merchant')
    command+=['--frame-controller-script',str(ROOT/'verification/whole-merchant-global-fixed-input.json')]
    core=command[command.index('--core')+1]
    reference=[sys.executable,str(ROOT/'scripts/probe_biwn_frame_CPU_owner.py'),'--mode','reference','--warm-frames','0','--frames','23538','--core',core,'--capture-audio','--frame-controller-script',str(ROOT/'verification/whole-merchant-global-fixed-input.json'),'--output',str(ROOT/'runs/CPU-GPU-DSP-IRQ-whole-merchant-reference')]
    workers=[];save(status='starting',pid=os.getpid())
    for label,cmd in [('reference',reference),('source',command)]:
        folder=Path(cmd[cmd.index('--output')+1]);assert not folder.exists()
        with (ROOT/f'runs/CPU-GPU-DSP-IRQ-whole-merchant-{label}.log').open('w')as log:worker=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
        path=ROOT/f'verification/CPU-GPU-DSP-IRQ-whole-merchant-{label}-job.json'
        job=dict(status='running',directory=str(folder),pid=worker.pid,command=cmd,whole_game_complete=False,scope='23538normal pad frames fromframe1,no warmup/checkpoint. Source variant owns CPU/GPU/DSP plusIRQentry; reference is original. IRQselection/ACK,hostcommit/prefetch/cyclecharge,HLE/devices remain original; comparison pending.')
        path.write_text(json.dumps(job,indent=2)+'\n');workers.append((worker,job,path))
    save(status='running',worker_pids={label:w.pid for label,(w,_,_)in zip(['reference','source'],workers)})
    for worker,job,path in workers:
        code=worker.wait();job.update(status='terminal_completed_pending_comparison'if code==0 else'terminal_failed',exit_code=code);path.write_text(json.dumps(job,indent=2)+'\n')
    assert all(job['exit_code']==0 for _,job,_ in workers),'A replay failed; inspect its retained log/report'
    comparison=ROOT/'verification/CPU-GPU-DSP-IRQ-whole-merchant-comparison.json';save(status='comparing')
    subprocess.run([sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),'--C-run',str(ROOT/'runs/CPU-GPU-DSP-IRQ-whole-merchant'),'--reference',str(ROOT/'runs/CPU-GPU-DSP-IRQ-whole-merchant-reference'),'--expected-frames','23538','--output',str(comparison)],check=True)
    for _,job,path in workers:
        job.update(status='terminal_verified_comparison',comparison=str(comparison));path.write_text(json.dumps(job,indent=2)+'\n')
    save(status='terminal_verified_comparison',comparison=str(comparison))
if __name__=='__main__':
    try:main()
    except Exception as error:save(status='terminal_failed',error=repr(error));raise
