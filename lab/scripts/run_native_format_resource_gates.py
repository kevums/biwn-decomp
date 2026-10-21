"""Deterministic resource/lifecycle verification with bounded child processes."""
from pathlib import Path
from datetime import datetime, timezone
import concurrent.futures
import argparse
import hashlib
import json
import os
import subprocess
import sys
import threading
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',type=Path);args=parser.parse_args()
    pp=ROOT/'verification/native-format-resource-preparation-current.json';prep=json.loads(pp.read_text())
    for item in prep['drivers']:
        assert sha(item['parent'])==item['parent_sha256']
        assert sha(item['derived'])==item['derived_sha256']
    if args.resume:
        out=args.resume.resolve();state=json.loads((out/'protocol.json').read_text())
        assert state['status']=='terminal_failed' and state['preparation_sha256']==sha(pp)
        prior_pid=state['pid'];assert subprocess.run(['ps','-p',str(prior_pid),'-o','pid='],capture_output=True,text=True).returncode!=0,'Prior driver is still live'
        state.setdefault('orchestration_repairs',[]).append(dict(previous_error=state.pop('error'),previous_pid=prior_pid,
            reason='Acquire checker writes controlled-current only after full pass; preflight is in its immutable child protocol. Reuse completed receipts, no test weakening.',
            driver_as_run=str(out/'driver-as-run.py'),driver_as_run_sha256=sha(out/'driver-as-run.py'),resumed_driver_sha256=sha(__file__)))
        state.update(status='running',pid=os.getpid())
    else:
        out=ROOT/'verification/native-format-resource-gates'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
        state=dict(status='running',pid=os.getpid(),directory=str(out),preparation=str(pp),preparation_sha256=sha(pp),jobs={},
                   LLM_calls=0,training_updates=0,game_frames=0,default_promoted=False,whole_game_complete=False)
    lock=threading.Lock()
    def mark():
        text=json.dumps(state,indent=2)+'\n'
        for path in [out/'protocol.json',ROOT/'verification/native-format-resource-gates-active.json']:
            temp=path.with_suffix('.tmp');temp.write_text(text);temp.replace(path)
    def run(kind,limited=False):
        label='native-format-bundle-'+kind
        if kind=='loader':
            driver=ROOT/'scripts/check_biwn_native_load_kernel_variant.py'
            options=['--word-scan','--optimization','Os','--target-proof',prep['loader_target'],'--label',label]
        elif kind.startswith('loader-readiness'):
            driver=ROOT/'scripts/check_biwn_native_format_loader_readiness.py'
            options=['--component',str(ROOT/'verification/native-format-bundle-loader-current.json'),'--label',label]
            if kind.endswith('-nested'):options+=['--nested']
        else:
            suffix='readiness'if kind=='readiness-relocated'else'heap_witness'if kind=='heap-blitter-witness'else kind
            driver=ROOT/'scripts'/f'check_biwn_native_format_bundle_{suffix}.py';options=[]
            if kind=='readiness-relocated':options+=['--relocated']
            if kind=='heap-blitter-witness':options+=['--bundle']
        if limited:options+=['--limit','2']
        key=kind+('-preflight'if limited else'');command=[sys.executable,'-u',str(driver),*options];log_path=out/(key+'.log')
        previous=state['jobs'].get(key)
        if previous:
            assert previous['command']==command and previous['driver_sha256']==sha(driver)
            if previous['status']=='terminal_pass':
                path=Path(previous['proof']);assert sha(path)==previous['proof_sha256']
                proof=json.loads(path.read_text())
                if kind!='heap-blitter-witness':assert proof['compiled_binary_sha256']==prep['binary_sha256']
                print('Reused completed',key,flush=True);return
            assert subprocess.run(['ps','-p',str(previous['pid']),'-o','pid='],capture_output=True,text=True).returncode!=0,'Child is still live'
            child_out=Path(log_path.read_text().splitlines()[0]);path=child_out/'protocol.json'
            proof=json.loads(path.read_text());assert proof['pid']==previous['pid']
            assert proof['status'].startswith('terminal_')and'pass'in proof['status']
            code=0
            previous['recovered_completed_child_protocol']=str(path)
        else:
            with log_path.open('w')as log:
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
                with lock:state['jobs'][key]=dict(status='running',pid=child.pid,command=command,log=str(log_path),driver_sha256=sha(driver));mark()
                code=child.wait()
            path=ROOT/'verification'/(label+('-active.json'if kind=='acquire'and limited else'-controlled-current.json'if kind=='acquire'else'-current.json'))
        if code:
            with lock:state['jobs'][key].update(status='terminal_failed',exit_code=code);mark()
            raise RuntimeError(f'{key} failed: {log_path}')
        proof=json.loads(path.read_text());assert proof['status'].startswith('terminal_')and'pass'in proof['status']
        if kind=='heap-blitter-witness':
            parent=json.loads(Path(proof['component_proof']).read_text());assert parent['compiled_binary_sha256']==prep['binary_sha256']
        else:
            assert proof['compiled_binary_sha256']==prep['binary_sha256']
            if proof.get('compiled_binary'):assert sha(proof['compiled_binary'])==prep['binary_sha256']
        if limited:assert proof['limit']==2
        elif 'limit'in proof:assert proof['limit']is None
        snapshot=out/(key+'-proof.json');snapshot.write_bytes(path.read_bytes())
        with lock:
            state['jobs'][key].update(status='terminal_pass',exit_code=code,proof=str(snapshot),proof_sha256=sha(snapshot),
                                     native_cases=proof.get('native_cases'),trace_cases=proof.get('trace_cases'),
                                     readiness_cases=proof.get('cases'),native_call_pairs=proof.get('native_call_pairs'))
            mark()
        print(key,proof['status'],proof.get('native_cases',proof.get('cases',proof.get('native_call_pairs'))),flush=True)
    def checked(kind):
        run(kind,True);run(kind)
    mark();print(out,flush=True)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
            tasks=[pool.submit(checked,kind)for kind in ['initialize','acquire','allocator','loader']]
            for task in tasks:task.result()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
            tasks=[pool.submit(run,kind)for kind in ['lifecycle','heap-blitter-witness']]
            for task in tasks:task.result()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
            tasks=[pool.submit(checked,kind)for kind in ['readiness','readiness-relocated','loader-readiness','loader-readiness-nested']]
            for task in tasks:task.result()
        state.update(status='terminal_exact_format_resource_and_lifecycle_gates_pass',
                     scope='Controlled acquire, real-allocator acquire, source init, coupled heap lifecycle, blitter payload witness, controlled repaired loader and four two-client readiness profiles. Exact new payload/layout; retained providers, explicit BIOS adapters and synthetic startup fixtures remain. No new live game, IRQ timing, physical-console or whole-game proof.')
        mark();(ROOT/'verification/native-format-resource-gates-current.json').write_text(json.dumps(state,indent=2)+'\n')
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
