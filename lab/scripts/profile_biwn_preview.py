"""Sample an isolated200frame preview, retaining exact baseline behavior checks.

Never attaches to, restarts or changes the long startup verification process.
Sampling is diagnostic; its wall time is not an interactive performance claim.
"""
import argparse,hashlib,json,os,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sample-seconds',type=int,default=2);args=ap.parse_args();assert 1<=args.sample_seconds<=10
    baseline=ROOT/'runs/world-controls-20261017T084146.540377Z'
    protocol=json.loads((baseline/'protocol.json').read_text());assert protocol['status']=='terminal_CPU_GPU_controls_match_DSP_inactive'
    command=next(row['command']for row in protocol['commands']if row['phase']=='C')[:]
    assert '--no-instruction-trace'not in command
    out=ROOT/'runs'/('preview-profile-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    command[command.index('--output')+1]=str(out/'C');command+=['--no-instruction-trace']
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),baseline=str(baseline),command=command,
               source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               scope='Isolated sourceCPU/GPU preview using the same naturally reached outdoor state and200recorded movement frames. Trace files off; sample attaches only to this child. Exact frame/final-state equivalence required. Sampling and concurrent workload preclude a performance acceptance claim.')
    def save():
        text=json.dumps(state,indent=2)+'\n';(out/'protocol.json').write_text(text);(ROOT/'verification/preview-profile-active.json').write_text(text)
    save()
    with(out/'C.log').open('w')as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state.update(status='running_isolated_preview',child_pid=child.pid);save();print('preview PID',child.pid,flush=True)
        deadline=time.monotonic()+30
        while child.poll()is None and time.monotonic()<deadline:
            progress=out/'C/progress.json'
            if progress.exists():
                try:
                    if json.loads(progress.read_text()).get('completed_frames',0)>=60:break
                except json.JSONDecodeError:pass
            time.sleep(0.1)
        if child.poll()is None:
            sample=['/usr/bin/sample',str(child.pid),str(args.sample_seconds),'-file',str(out/'sample.txt')]
            state.update(status='sampling_isolated_preview',sample_command=sample);save()
            measured=subprocess.run(sample,capture_output=True,text=True);(out/'sample-command.log').write_text(measured.stdout+'\n'+measured.stderr)
            state['sample_exit_code']=measured.returncode;save()
        else:state['sample_skipped']='Child completed before sampling; no profile evidence'
        code=child.wait()
    state['child_exit_code']=code
    try:
        assert code==0,str(out/'C.log')
        before=json.loads((baseline/'C/report.json').read_text());after=json.loads((out/'C/report.json').read_text())
        assert not before['errors']and not after['errors']and len(after['frames'])==200
        checks=dict(frame_records=before['frames']==after['frames'],
                    CPU_counts=before['owned_CPU_instructions']==after['owned_CPU_instructions'],
                    no_original_CPU=after['original_CPU_instructions']==0,no_rejected_CPU=after['rejected_CPU_instructions']==0,
                    no_CPU_disk_trace=not(out/'C/CPU-before-instructions.bin').exists()and not(out/'C/retired-instruction-costs.bin').exists())
        for name in ['warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']:
            checks[name]=(baseline/'C'/name).read_bytes()==(out/'C'/name).read_bytes()
        for label,key in [('GPU','regular_GPU_report'),('DSP','DSP_report')]:
            old=json.loads(Path(before[key]).read_text());new=json.loads(Path(after[key]).read_text())
            counts='counts'if label=='GPU'else'core_counts';checks[label+'_counts']=old[counts]==new[counts]
            checks[label+'_no_original_or_rejected']=new[counts]['Original']==new[counts]['Rejected']==0
        state['checks']=checks;assert all(checks.values()),checks
        state.update(status='terminal_profiled_preview_matches_baseline',CPU_instructions=after['owned_CPU_instructions'],
                     sampled=state.get('sample_exit_code')==0,interactive_performance_verified=False)
        save();(ROOT/'verification/preview-profile-current.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(dict(status=state['status'],sampled=state['sampled'],directory=str(out))),flush=True)
    except Exception as error:
        state.update(status='terminal_failed',error=repr(error));save();raise

if __name__=='__main__':main()
