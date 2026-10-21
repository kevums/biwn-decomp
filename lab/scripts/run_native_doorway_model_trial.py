"""One local native-function Author/Reviewer trial, with at most one repair."""
import argparse,fcntl,json,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check-only',action='store_true');args=parser.parse_args();v=ROOT/'verification'
    author=ROOT/'scripts/author_biwn_native_doorway.py';repair=ROOT/'scripts/repair_biwn_native_doorway_once.py';gate=read(v/'native-doorway-current.json')
    assert gate['source_accepted'] and gate['native_cases']==2025 and gate['changing_coordinate_cases']==768
    assert author.is_file()and repair.is_file()
    if args.check_only:
        print(json.dumps(dict(status='native_doorway_trial_targets_checked_no_prediction',commands=[[sys.executable,str(author)],[sys.executable,str(repair)]],maximum_Author_attempts=2,automatic_source_adoption=False)));return
    with(ROOT/'runs/.native-doorway-workflow.lock').open('a')as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise SystemExit('A native doorway trial is already running. Its saved prompts remain available under Start Local AI -> I.')
        out=ROOT/'runs'/('native-doorway-model-trial-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());state=dict(status='running',pid=os.getpid(),directory=str(out),roles=[],maximum_Author_attempts=2,automatic_source_adoption=False,native_Chat_verified=False,new_training=False)
        def save():
            (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(v/'native-doorway-model-trial-current.json').write_text(json.dumps(state,indent=2)+'\n')
        save();print('Exact prompts/responses: Start Local AI -> I\nTrial: '+str(out),flush=True)
        try:
            for script,pointer,field in [(author,'local-native-doorway-author-current.json','raw_kernel_gate_pass'),(repair,'local-native-doorway-repair-current.json','raw_repair_gate_pass')]:
                print('Running '+script.name,flush=True);child=subprocess.Popen([sys.executable,'-u',str(script)]);code=child.wait();assert code==0,'Local role workflow failed; retain raw outputs and inspect its receipt'
                result=read(v/pointer);assert result['pid']==child.pid,'Concurrent direct workflow changed the current receipt; do not adopt or repair an ambiguous run'
                state['roles'].append(dict(script=str(script),receipt=str(Path(result['directory'])/'protocol.json'),gate_pass=result[field]));save()
                if result[field]:break
            state.update(status='terminal_native_doorway_model_trial_component_pass'if state['roles'][-1]['gate_pass']else'terminal_native_doorway_model_trial_rejected',source_adopted=False);save();print(state['status']+'; candidate remains experimental until integration review.',flush=True)
        except BaseException as error:state.update(status='terminal_native_doorway_model_trial_failed',error=repr(error));save();raise
if __name__=='__main__':main()
