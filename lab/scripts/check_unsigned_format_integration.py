"""Exact O2-lean component/install/resource inventory; bounded child processes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,concurrent.futures,json,os,subprocess,sys,threading
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',type=Path);args=parser.parse_args()
    pp=ROOT/'verification/native-unsigned-format-preparation-current.json';prep=read(pp);bp=ROOT/'verification/native-unsigned-format-bundle-current.json';bundle=read(bp)
    assert prep['bundle_sha256']==sha(bp)and sha(bundle['binary'])==prep['binary_sha256']
    for row in prep['drivers']:assert sha(row['derived'])==row['derived_sha256']
    if args.resume:
        out=args.resume.resolve();state=read(out/'protocol.json');assert state['status']=='terminal_failed'
        assert subprocess.run(['ps','-p',str(state['pid']),'-o','pid='],capture_output=True,text=True).returncode!=0,'Prior driver still live'
        assert sha(out/'preparation-as-run.json')==state['preparation_sha256']
        state.setdefault('orchestration_repairs',[]).append(dict(previous_error=state.pop('error'),previous_preparation=str(out/'preparation-as-run.json'),previous_preparation_sha256=state['preparation_sha256'],reason='RNG binary artifact filename corrected; same expected binary/tests, reuse completed immutable receipts.'))
        state.update(status='running_core_matrices',pid=os.getpid(),preparation=str(pp),preparation_sha256=sha(pp))
    else:
        out=ROOT/'verification/native-unsigned-format-integration'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
        state=dict(status='running_core_matrices',pid=os.getpid(),directory=str(out),preparation=str(pp),preparation_sha256=sha(pp),binary_sha256=prep['binary_sha256'],binary_bytes=8956,jobs={},LLM_calls=0,training_updates=0,default_promoted=False,whole_game_complete=False)
    lock=threading.Lock()
    def mark():
        text=json.dumps(state,indent=2)+'\n'
        for p in [out/'protocol.json',ROOT/'verification/native-unsigned-format-integration-active.json']:
            tmp=p.with_suffix('.tmp');tmp.write_text(text);tmp.replace(p)
    def run(kind,limited=False):
        stem='native-unsigned-format-bundle-'+kind
        if kind=='entry':driver=ROOT/'scripts/check_biwn_native_unsigned_format_disc_entry.py';options=[];stem='native-unsigned-format-disc-entry'
        elif kind=='loader':
            driver=ROOT/'scripts/check_biwn_native_load_kernel_variant.py';options=['--word-scan','--optimization','Os','--target-proof',str(ROOT/'verification/native-unsigned-format-loader-target-current.json'),'--label',stem]
        elif kind.startswith('loader-readiness'):
            driver=ROOT/'scripts/check_biwn_native_unsigned_format_loader_readiness.py';options=['--component',str(ROOT/'verification/native-unsigned-format-bundle-loader-current.json'),'--label',stem]
            if kind.endswith('-nested'):options+=['--nested']
        else:
            suffix='heap_witness'if kind=='heap-blitter-witness'else'readiness'if kind=='readiness-relocated'else kind
            driver=ROOT/'scripts'/f'check_biwn_native_unsigned_format_bundle_{suffix}.py';options=[]
            if kind in ['tasks','scheduler','heap','copy','free','release','heap-blitter-witness']:options+=['--bundle']
            if kind=='rng':options+=['--source',str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/rng-native.c')]
            if kind=='readiness-relocated':options+=['--relocated']
        if limited:options+=['--limit','2']
        key=kind+('-preflight'if limited else'');cmd=[sys.executable,'-u',str(driver),*options];previous=state['jobs'].get(key)
        if previous and previous['status']=='terminal_pass':
            assert previous['command']==cmd and previous['driver_sha256']==sha(driver)
            path=Path(previous['proof']);assert sha(path)==previous['proof_sha256']
            proof=read(path)
            for table in ['source_sha256','artifacts_sha256','execution_dependencies_sha256']:
                values=proof.get(table,{})
                if isinstance(values,dict):
                    for p,h in values.items():assert sha(p)==h,p
            print('Reused completed',key,flush=True);return
        if previous:
            assert previous['status']=='terminal_failed','Unresolved running child cannot be restarted'
            state.setdefault('failed_attempts',[]).append(dict(key=key,**previous))
        log=out/(key+('-retry'if previous else'')+'.log')
        with log.open('w')as stream:
            child=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT)
            with lock:state['jobs'][key]=dict(status='running',pid=child.pid,command=cmd,log=str(log),driver_sha256=sha(driver));mark()
            code=child.wait()
        if code:
            with lock:state['jobs'][key].update(status='terminal_failed',exit_code=code);mark()
            raise RuntimeError(f'{key}: {log}')
        suffix='-active.json'if kind=='acquire'and limited else'-controlled-current.json'if kind=='acquire'else'-current.json'
        path=ROOT/'verification'/(stem+suffix);proof=read(path)
        assert proof['status'].startswith('terminal_')and'pass'in proof['status']
        if kind=='entry':assert proof['entry_cases']==96 and proof['component_cases']==5151
        elif kind=='heap-blitter-witness':assert read(proof['component_proof'])['compiled_binary_sha256']==prep['binary_sha256']
        else:
            assert proof['compiled_binary_sha256']==prep['binary_sha256']
            if proof.get('compiled_binary'):assert sha(proof['compiled_binary'])==prep['binary_sha256']
            if 'binary_bytes'in proof:assert proof['binary_bytes']==8956
        if limited:assert proof['limit']==2
        elif 'limit'in proof:assert proof['limit']is None
        snapshot=out/(key+'-proof.json');snapshot.write_bytes(path.read_bytes())
        with lock:state['jobs'][key].update(status='terminal_pass',exit_code=code,proof=str(snapshot),proof_sha256=sha(snapshot),native_cases=proof.get('native_cases',proof.get('cpu_cases')),trace_cases=proof.get('trace_cases'),cases=proof.get('cases'));mark()
        print(key,proof['status'],proof.get('native_cases',proof.get('cpu_cases',proof.get('cases',proof.get('native_call_pairs')))),flush=True)
    def checked(kind):run(kind,True);run(kind)
    def parallel(kinds,preflight=True):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
            futures=[pool.submit(checked if preflight else run,kind)for kind in kinds]
            for future in futures:future.result()
    mark();print(out,flush=True)
    try:
        parallel(['controller','rng','tasks','scheduler','heap','copy','free']);checked('release')
        dp=ROOT/'verification/native-unsigned-format-disc-build-current.json';disc=read(dp)
        assert disc['linked_component']==bundle['binary']and disc['linked_component_bytes']==8956
        assert disc['component_bytes']==9216 and disc['heap_start']==0x1611c0
        assert Path(disc['component']).read_bytes()==Path(bundle['binary']).read_bytes()+bytes(260)
        layout=dict(status='exact_optimized_format_component_fixture_metadata',resident_address=bundle['base'],heap_start=bundle['heap_start'],component_bytes=9216,component=disc['component'],component_sha256=sha(disc['component']),patch_manifest=disc['patch_manifest'],patch_manifest_sha256=sha(disc['patch_manifest']),symbols=bundle['symbols'],disc_proof=str(dp),disc_proof_sha256=sha(dp))
        save(ROOT/'verification/native-unsigned-format-bundle-linked-fixture-current.json',layout);save(out/'linked-fixture.json',layout)
        target=dict(status='exact_optimized_format_loader_target',binary=bundle['binary'],binary_sha256=bundle['binary_sha256'],symbols=bundle['symbols'],resident_base=bundle['base'],bundle_proof=str(bp),bundle_proof_sha256=sha(bp))
        save(ROOT/'verification/native-unsigned-format-loader-target-current.json',target);save(out/'loader-target.json',target)
        state['status']='running_install_and_resource_matrices';mark()
        parallel(['entry','initialize'],False)
        parallel(['acquire','allocator','loader'])
        parallel(['lifecycle','heap-blitter-witness'],False)
        parallel(['readiness','readiness-relocated','loader-readiness','loader-readiness-nested'])
        required=['controller','rng','tasks','scheduler','heap','copy','free','release','entry','initialize','acquire','allocator','loader','lifecycle','heap-blitter-witness','readiness','readiness-relocated','loader-readiness','loader-readiness-nested']
        assert all(state['jobs'][k]['status']=='terminal_pass'for k in required)
        state.update(status='terminal_optimized_format_install_and_component_resource_inventory_pass',full_gates=required,
                     scope='Exact8956byte optimized payload; original full component matrices,96startup/5151installed ABI, resources/lifecycle/four readiness profiles. Full helper/caller matrices are separate prior receipts on same hash. No new fresh-game/IRQ/physical-console/whole-game proof.')
        mark();save(ROOT/'verification/native-unsigned-format-integration-current.json',state)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
