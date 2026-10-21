"""One-shot pipeline: verify live reference, compile its missing cases, replay C."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'verification/scene532-full-pipeline-state.json'
def save(**fields):
    current=json.loads(STATE.read_text())if STATE.exists()else{}
    current.update(fields);STATE.write_text(json.dumps(current,indent=2)+'\n')
def run(script,*args):
    command=[sys.executable,str(ROOT/'scripts'/script),*map(str,args)]
    save(phase_command=command);subprocess.run(command,check=True)
def main():
    assert not STATE.exists(),'Never launch another pipeline over a saved execution.'
    save(status='waiting_for_original_reference',pid=os.getpid())
    path=ROOT/'verification/scene532-full-fixed-reference-job.json';job=json.loads(path.read_text());folder=Path(job['directory'])
    while not(folder/'report.json').exists():
        command=subprocess.run(['ps','-p',str(job['pid']),'-o','command='],capture_output=True,text=True).stdout
        assert str(folder)in command and 'probe_biwn_frame_CPU_owner.py'in command,'Reference handle missing without terminal report'
        save(reference_pid=job['pid'],reference_handle_live=True);time.sleep(5)
    run('review_biwn_fixed_route_reference.py','--target',532)
    save(status='compiling_source_cases')
    candidate=ROOT/'verification/scene532-route-CPU-experimental-candidate.json'
    native=ROOT/'verification/scene532-route-native-CPU-experimental-candidate.json'
    run('build_biwn_route_CPU.py','--reference',folder,'--base-candidate',ROOT/'verification/scene17-route-CPU-experimental-candidate.json','--instruction-RAM',ROOT/'verification/zero-warm-startup-instruction-atlas.bin','--movie-privileged-events','--function','biwn_scene532_route_CPU_step','--output-manifest',candidate)
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    run('build_biwn_fast_CPU_bridge.py','--CPU-candidate',candidate,'--candidate-output',native,'--CPU-private-source',core.parent)
    prior=json.loads((ROOT/'verification/scene17-full-three-processor-job.json').read_text());command=prior['command'][:]
    for flag,value in [('--frames','19870'),('--frame-controller-script',ROOT/'verification/scene532-global-fixed-input.json'),('--CPU-candidate',candidate),('--native-CPU-candidate',native),('--output',ROOT/'runs/scene532-full-fixed-CPU-GPU-DSP')]:command[command.index(flag)+1]=str(value)
    command+=['--DSP-router-candidate',str(ROOT/'verification/fast-DSP-router-experimental-candidate.json')]
    out=Path(command[command.index('--output')+1]);assert not out.exists()
    with (ROOT/'runs/scene532-full-fixed-CPU-GPU-DSP.log').open('w')as log:worker=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
    cjob=dict(status='running',pid=worker.pid,directory=str(out),command=command,whole_game_complete=False,scope='19870normal scene532route frames fromframe1 with sourceCPU/GPU/DSP; no warmup/checkpoint. Isolated newly compiledCPUcases and optimizedDSP; originalIRQ/HLE/devices remain. Comparison pending.')
    cp=ROOT/'verification/scene532-full-three-processor-job.json';cp.write_text(json.dumps(cjob,indent=2)+'\n')
    save(status='source_replay_running',source_worker_pid=worker.pid);code=worker.wait();cjob.update(status='terminal_completed_pending_comparison'if code==0 else'terminal_source_failed',exit_code=code);cp.write_text(json.dumps(cjob,indent=2)+'\n');assert code==0,code
    comparison=ROOT/'verification/scene532-full-fixed-CPU-GPU-DSP-comparison.json';save(status='comparing_complete_execution')
    run('compare_biwn_frame_CPU_only.py','--C-run',out,'--reference',folder,'--expected-frames',19870,'--output',comparison)
    cjob.update(status='terminal_verified_comparison',comparison=str(comparison));cp.write_text(json.dumps(cjob,indent=2)+'\n');save(status='terminal_verified_comparison',comparison=str(comparison))
if __name__=='__main__':
    try:main()
    except Exception as error:save(status='terminal_failed',error=repr(error));raise
