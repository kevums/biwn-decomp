"""Retain completed gates; run the existing kernel-aware loader readiness tests."""
from pathlib import Path
from datetime import datetime,timezone
import concurrent.futures,hashlib,json,os,subprocess,sys,threading
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    prior_path=ROOT/'verification/native-format-resource-gates-active.json';prior=json.loads(prior_path.read_text());assert prior['status']=='terminal_failed'
    prior_out=Path(prior['directory']);prep_as_run=prior_out/'preparation-as-run.json';assert sha(prep_as_run)==prior['preparation_sha256']
    prep_path=ROOT/'verification/native-format-resource-preparation-current.json';prep=json.loads(prep_path.read_text())
    driver=ROOT/'scripts/check_biwn_native_format_loader_readiness.py';row=next(x for x in prep['drivers']if x['kind']=='loader_readiness');assert sha(driver)==row['derived_sha256']
    assert row['parent'].endswith('check_biwn_native_load_kernel_readiness.py')
    passed={}
    for kind,job in prior['jobs'].items():
        if job['status']=='terminal_pass':
            path=Path(job['proof']);assert sha(path)==job['proof_sha256'];proof=json.loads(path.read_text())
            if proof.get('compiled_binary_sha256'):assert proof['compiled_binary_sha256']==prep['binary_sha256']
            for table in ['source_sha256','artifacts_sha256','execution_dependencies_sha256']:
                values=proof.get(table,{})
                if isinstance(values,dict):
                    for p,h in values.items():assert sha(p)==h,p
            passed[kind]=job
    assert all(k in passed for k in ['acquire','allocator','initialize','loader','lifecycle','heap-blitter-witness','readiness','readiness-relocated'])
    out=ROOT/'verification/native-format-loader-readiness-finish'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    state=dict(status='running',pid=os.getpid(),directory=str(out),preparation=str(prep_path),preparation_sha256=sha(prep_path),
               prior_driver_failure=str(prior_out/'loader-readiness-harness-failure.json'),prior_preparation=str(prep_as_run),
               prior_completed_gates_reused=passed,jobs={},
               correction='Initial adaptation used the general loader gate; existing scan kernel was misclassified as an external helper. Use the prior native28 kernel-aware gate with exact ELF/object-derived ownership range. Stack assertions and tests remain unchanged.',
               production_code_changed=False,training_updates=0,LLM_calls=0,whole_game_complete=False)
    lock=threading.Lock()
    def mark():
        text=json.dumps(state,indent=2)+'\n'
        for p in [out/'protocol.json',ROOT/'verification/native-format-loader-readiness-finish-active.json']:
            tmp=p.with_suffix('.tmp');tmp.write_text(text);tmp.replace(p)
    def run(nested,limited):
        kind='loader-readiness'+('-nested'if nested else'');key=kind+('-preflight'if limited else'');label='native-format-bundle-'+kind
        cmd=[sys.executable,'-u',str(driver),'--component',str(ROOT/'verification/native-format-bundle-loader-current.json'),'--label',label]
        if nested:cmd+=['--nested']
        if limited:cmd+=['--limit','2']
        log=out/(key+'.log')
        with log.open('w')as stream:
            child=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT)
            with lock:state['jobs'][key]=dict(status='running',pid=child.pid,command=cmd,log=str(log));mark()
            code=child.wait()
        if code:
            with lock:state['jobs'][key].update(status='terminal_failed',exit_code=code);mark()
            raise RuntimeError(str(log))
        path=ROOT/'verification'/(label+'-current.json');proof=json.loads(path.read_text())
        assert proof['compiled_binary_sha256']==prep['binary_sha256']
        assert proof['cases']==(2 if limited else 16)and proof['limit']==(2 if limited else None)
        assert proof['real_readiness_component_pass']==(not limited)
        snapshot=out/(key+'-proof.json');snapshot.write_bytes(path.read_bytes())
        with lock:state['jobs'][key].update(status='terminal_pass',exit_code=code,cases=proof['cases'],proof=str(snapshot),proof_sha256=sha(snapshot));mark()
        print(key,proof['status'],proof['cases'],flush=True)
    def lane(nested):run(nested,True);run(nested,False)
    mark();print(out,flush=True)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
            futures=[pool.submit(lane,nested)for nested in [False,True]]
            for future in futures:future.result()
        state.update(status='terminal_exact_format_resource_and_lifecycle_gates_pass',
                     binary_sha256=prep['binary_sha256'],binary_bytes=8742,heap_start=0x1611c0,reservation_bytes=9216,
                     scope='Controlled acquire, real-allocator acquire, initializer, coupled heap lifecycle, blitter payload witness, repaired loader and four two-client readiness profiles pass on exact new payload/layout. Synthetic fixtures, explicit BIOS adapters, retained providers and per-gate exclusions remain. No new full-game/IRQ/physical-console proof.')
        mark();(ROOT/'verification/native-format-resource-gates-current.json').write_text(json.dumps(state,indent=2)+'\n')
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
