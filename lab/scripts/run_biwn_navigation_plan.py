"""Explore a source doorway with read-only feedback and ordinary pad input.

Records a fixed controller script for a separate original/C replay. This
reference-only planning execution is not an equivalence verdict.
"""
import argparse,hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--frames',type=int,default=1000);args=ap.parse_args();assert 1<=args.frames<=1200
    prior=json.loads((ROOT/'verification/loaded-scene-frames-current.json').read_text());assert prior['status']in ['terminal_CPU_GPU_match_DSP_inactive','terminal_CPU_GPU_DSP_match']
    plan=json.loads((ROOT/'verification/local-doorway-route-plan-current.json').read_text());path=Path(plan['directory'])/'plan.json'
    out=ROOT/'runs'/('doorway-navigation-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    command=next(row['command']for row in prior['commands']if row['phase']=='reference')
    for flag in ['--capture-frame','--frame-controller-script']:
        while flag in command:
            i=command.index(flag);del command[i:i+2]
    command[command.index('--frames')+1]=str(args.frames);command[command.index('--output')+1]=str(out/'reference')
    command+=['--navigation-plan',str(path),'--no-instruction-trace']
    for frame in sorted(set([1,min(100,args.frames),min(200,args.frames),min(400,args.frames),min(600,args.frames),min(800,args.frames),args.frames])):command+=['--capture-frame',str(frame)]
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),command=command,source_frame_run=prior['directory'],local_planner=plan['directory'],scope='Reference-only ordinary-controller route planning from the declared C-loaded scene transplant. No original/C verdict; fixed captured buttons must replay separately.')
    def save():
        text=json.dumps(state,indent=2)+'\n';(out/'protocol.json').write_text(text);(ROOT/'verification/doorway-navigation-active.json').write_text(text)
    with(out/'reference.log').open('w')as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state.update(status='running_reference_planning',child_pid=child.pid);save();print('reference PID',child.pid,flush=True);code=child.wait()
    state['exit_code']=code
    if code:state.update(status='terminal_failed');save();raise RuntimeError(str(out/'reference.log'))
    report=json.loads((out/'reference/navigation-report.json').read_text());result=json.loads((out/'reference/report.json').read_text());assert not result['errors']
    state.update(status='terminal_plan_complete'if report['status']=='controller_plan_scene_mode_changed'else'terminal_plan_incomplete',navigation=report,input_script=str(out/'reference/navigation-input.json'),input_script_sha256=hashlib.sha256((out/'reference/navigation-input.json').read_bytes()).hexdigest());save()
    (ROOT/'verification/doorway-navigation-current.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(dict(status=state['status'],last=report['last'])),flush=True)

if __name__=='__main__':main()
