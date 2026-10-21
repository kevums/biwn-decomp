"""Run unchanged component matrices against the separately linked format build.

This is deterministic verification orchestration, not an LLM agent or training.
Release waits for the full free receipt from this exact binary.
"""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    prep_path = ROOT/'verification/native-format-component-driver-preparation-current.json'
    prep = json.loads(prep_path.read_text())
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = ROOT/'verification/native-format-component-matrices'/stamp
    out.mkdir(parents=True)
    state = dict(status='running', pid=os.getpid(), directory=str(out),
                 preparation=str(prep_path), preparation_sha256=sha(prep_path),
                 expected_binary_sha256=prep['binary_sha256'], jobs={},
                 LLM_calls=0, training_updates=0, whole_game_complete=False,
                 default_preview_promoted=False)
    lock = threading.Lock()

    def mark():
        text = json.dumps(state, indent=2)+'\n'
        for path in [out/'protocol.json', ROOT/'verification/native-format-component-matrices-active.json']:
            temp = path.with_suffix('.tmp')
            temp.write_text(text)
            temp.replace(path)

    def run(kind, limited=False):
        driver = ROOT/'scripts'/f'check_biwn_native_format_bundle_{kind}.py'
        record = next(x for x in prep['drivers'] if x['kind'] == kind)
        assert sha(driver) == record['derived_sha256']
        command = [sys.executable, '-u', str(driver), '--bundle']
        if limited:
            command += ['--limit', '2']
        key = kind+('-preflight' if limited else '')
        log_path = out/(key+'.log')
        with log_path.open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            with lock:
                state['jobs'][key] = dict(status='running', pid=child.pid, command=command,
                                          log=str(log_path), driver_sha256=sha(driver))
                mark()
            code = child.wait()
        proof_path = ROOT/'verification'/f'native-format-bundle-{kind}-current.json'
        active_path = ROOT/'verification'/f'native-format-bundle-{kind}-active.json'
        if code:
            with lock:
                state['jobs'][key].update(status='failed', exit_code=code,
                                          active_proof=str(active_path))
                mark()
            raise RuntimeError(f'{key} failed; inspect {log_path}')
        proof = json.loads(proof_path.read_text())
        assert proof.get('limit') == (2 if limited else None), proof_path
        assert proof['compiled_binary_sha256'] == prep['binary_sha256']
        assert sha(proof['compiled_binary']) == prep['binary_sha256']
        assert proof['binary_bytes'] == 8742
        assert proof['status'].startswith('terminal_') and 'pass' in proof['status']
        snapshot = out/(key+'-proof.json')
        snapshot.write_bytes(proof_path.read_bytes())
        with lock:
            state['jobs'][key].update(status='terminal_pass', exit_code=code,
                                      proof=str(snapshot), proof_sha256=sha(snapshot),
                                      native_cases=proof.get('native_cases'),
                                      trace_cases=proof.get('trace_cases'))
            mark()
        print(key, proof['status'], proof.get('native_cases'), proof.get('trace_cases'), flush=True)

    mark()
    print(out, flush=True)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(run, kind) for kind in ['tasks','scheduler','heap','copy','free']]
            for job in jobs:
                job.result()
        # The derived release gate now requires this new build's full free proof.
        run('release', limited=True)
        run('release')
        state.update(status='terminal_six_linked_component_matrices_pass',
                     scope='Exact8742byte linked payload; full existing task/scheduler/heap/copy/free/release matrices. Synchronous component evidence with stated per-gate provider/private-stack limits; not whole-game, timing-equivalence or physical-console proof.')
        mark()
        (ROOT/'verification/native-format-component-matrices-current.json').write_text(json.dumps(state, indent=2)+'\n')
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    main()
