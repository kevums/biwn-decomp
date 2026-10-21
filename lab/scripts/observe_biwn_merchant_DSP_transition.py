"""Fresh native read-only DSP observation around the actual combined-provider failure."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    failed_path=ROOT/'verification/native-formatter-C-processors/20261018T233557.255349Z/protocol.json'
    failed=json.loads(failed_path.read_text())
    assert failed['status']=='terminal_fresh_C_processors_driver_failure' and failed['exit_codes']=={'reference':0,'C':1}
    original=Path(failed['directory']);DSP=json.loads((original/'C/DSP-owner-report.json').read_text())
    assert DSP['uncovered']==460 and DSP['core_counts']['Original']==460
    out=ROOT/'verification/merchant-DSP-transition-observation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    command=list(failed['commands'][0]['command'])
    command[command.index('--frames')+1]='15852';command[command.index('--output')+1]=str(out/'reference')
    command+=['--observe-DSP-window','15845','15852','--DSP-witness-limit','1024']
    probe=Path(command[2]);assert sha(probe)==failed['source_sha256'][str(probe)]
    state=dict(status='running_native_read_only_DSP_transition_observation',pid=os.getpid(),directory=str(out),command=command,
        failed_run=str(failed_path),new_training=False,execution_ownership='Original CPU/GPU/DSP; read-only DSP observer only',
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',failed_path,probe,original/'C/DSP-owner-report.json',original/'C/DSP-first-uncovered-state.bin']},
        scope='Fresh native control on the same repaired disc and controller route. Observe frames15845..15851; no checkpoint restore, source-provider repair or fresh full C rerun.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/merchant-DSP-transition-observation-current.json',state)
    mark();print(out,flush=True)
    try:
        with(out/'reference.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
        state['exit_code']=code
        if code:
            state['status']='terminal_native_DSP_transition_observation_failed';mark();return
        report=json.loads((out/'reference/report.json').read_text());control=json.loads((original/'reference/report.json').read_text())
        assert len(report['frames'])==15852
        fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
        differences={k:sum(a[k]!=b[k]for a,b in zip(report['frames'],control['frames']))for k in fields}
        observation=json.loads((out/'reference/DSP-observation.json').read_text())
        outside={key:n for key,n in observation['PC_opcodes'].items() if not 0xf1b000<=int(key.split(':')[0],16)<0xf1d000}
        state.update(status='terminal_native_DSP_transition_observed_equal'if not any(differences.values())and not observation['errors']else'terminal_native_DSP_transition_observation_diverged',
            comparisons=differences,observer=observation,outside_DSP_local_RAM_instruction_counts=outside,
            reference_report_sha256=sha(out/'reference/report.json'),observed_original_PC_zero=any(key.startswith('0x0:')for key in outside))
        mark();print(json.dumps({k:state[k]for k in ['status','comparisons','outside_DSP_local_RAM_instruction_counts','observed_original_PC_zero']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_native_DSP_transition_driver_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
