"""Trace fast backend over the identical660frame movement prefix."""
from datetime import datetime,timezone
import json,os,subprocess
from pathlib import Path
from run_biwn_native_gameplay_route import ROOT,save,sha


def main():
    p=ROOT/'verification/native-movement-controls-current.json';prior=json.loads(p.read_text())
    bpath=ROOT/'verification/native-fast-rng-disc-build-current.json';b=json.loads(bpath.read_text())
    assert prior['status']=='terminal_four_arm_movement_prefix_pending_write_analysis'
    for path,digest in prior['source_sha256'].items():assert sha(path)==digest,path
    assert sha(b['derived_disc'])==b['derived_disc_sha256']
    out=ROOT/'verification/native-fast-movement-prefix'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    command=list(next(row['command']for row in prior['commands']if row['lane']=='native'))
    command[command.index('--disc')+1]=b['derived_disc'];command[command.index('--output')+1]=str(out/'fast')
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),frames=660,command=command,prior_control_proof=str(p),prior_control_proof_sha256=sha(p),build_proof=str(bpath),build_proof_sha256=sha(bpath),source_sha256={**prior['source_sha256'],str(Path(__file__)):sha(__file__)},scope='Fresh fast660frame lane using immutable prior four-arm cadence probe/core/input. Reference and controls are retained earlier observations; separate fresh24738pair checks new reference reproducibility. Observer ignores payload argument and reads only CPU/RAM; no host guest writes.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-fast-movement-prefix-active.json',state)
    mark()
    try:
        with (out/'fast.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state.update(status='running',child_pid=child.pid);mark();print('PID',child.pid,flush=True);code=child.wait()
        assert code==0,code
        observation=json.loads((out/'fast/gameplay-observation.json').read_text());assert not observation['errors'] and observation['old_rng_steps']==0
        state.update(status='terminal_fast_movement_prefix_pending_analysis',observation=observation);mark();save(ROOT/'verification/native-fast-movement-prefix-current.json',state);print(state['status'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise


if __name__=='__main__':main()
