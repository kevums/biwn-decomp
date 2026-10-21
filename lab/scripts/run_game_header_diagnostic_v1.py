"""Run one frozen base/selected-adapter diagnostic sequentially under inference lock."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    prepared=json.loads((ROOT/'verification/game-header-diagnostic-v1-prepared-current.json').read_text())
    out=Path(prepared['directory']);manifest=out/'manifest.json'
    # This directory is single use; a missing/expired observation never restarts it.
    protocol=out/'run.json';assert not protocol.exists(),protocol
    originals=[ROOT/'verification'/n for n in ['game-geometry-v4-base-evaluation-current.json','game-geometry-v4-adapter-evaluation-current.json','game-geometry-checkpoint-selection-v4-current.json']]
    before={str(p):sha(p)for p in originals}
    state=dict(status='starting',directory=str(out),pid=os.getpid(),phases=[],scope=prepared['scope'],default_promoted=False,
               original_results_sha256=before,execution_scripts_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/evaluate_game_header_diagnostic_v1.py']})
    def save():
        for path in [protocol,ROOT/'verification/game-header-diagnostic-v1-current.json']:path.write_text(json.dumps(state,indent=2)+'\n')
    save()
    try:
        for phase in ['base','adapter']:
            command=[sys.executable,str(ROOT/'scripts/evaluate_game_header_diagnostic_v1.py'),'--manifest',str(manifest)]
            if phase=='adapter':command.append('--adapter')
            with (out/(phase+'-run.log')).open('w')as log:
                child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
                state.update(status='running',phase=phase,child_pid=child.pid)
                state['phases'].append(dict(phase=phase,pid=child.pid,command=command));save()
                code=child.wait();state['phases'][-1]['exit_code']=code;save()
                assert code==0,(phase,code)
        assert all(sha(p)==h for p,h in before.items())
        state.update(status='terminal_paired_diagnostic_pending_review',original_results_unchanged=True);save()
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise
if __name__=='__main__':main()
