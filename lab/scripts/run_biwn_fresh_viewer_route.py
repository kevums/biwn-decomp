"""Run the prepared full fresh-boot repaired route with explicit process receipts."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'verification/fresh-viewer-full-current.json'


def review_completed(out):
    """Audit an existing terminal comparison; never launches or restarts work."""
    out=Path(out);proof=out/'comparison.json';result=json.loads(proof.read_text())
    assert result['status']=='CPU_GPU_DSP_frame_comparison_pass' and all(result['checks'].values())
    native=json.loads((out/'reference/report.json').read_text())
    assert native['PC_counts'].get('0x11e86',0)>0
    assert native['PC_counts'].get('0x196f8',0)>0
    ram=(out/'C/final-RAM.bin').read_bytes()
    # Source19710..19724 restores outdoor mode1 when49C60==1,
    # otherwise indoor mode2. A fresh route need not end indoors.
    expected=1 if int.from_bytes(ram[0x49c60:0x49c62],'big')==1 else 2
    assert int.from_bytes(ram[0x15b530:0x15b532],'big')==expected
    for frame in [23590,23658]:
        assert(out/'C'/f'frame-{frame}.png').read_bytes()==(out/'reference'/f'frame-{frame}.png').read_bytes()
    return dict(comparison=str(proof),viewer_render_iterations=native['PC_counts']['0x11e86'],
                restored_world_mode=expected,world_mode_rule='Source19710..19724:49C60==1 ->mode1,otherwise mode2')


def main():
    state=json.loads(STATE.read_text())
    assert state['status']=='prepared', 'Never restart over an existing execution'
    out=Path(state['directory']);state.update(pid=os.getpid(),started_unix=time.time())
    def save():
        STATE.write_text(json.dumps(state,indent=2)+'\n')
        (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n')
    save()
    try:
        for phase in ['reference','candidate']:
            command=state['commands'][phase]
            if phase=='reference' and state.get('reuse_reference'):
                reference=Path(state['reuse_reference']).resolve()
                report=json.loads((reference/'report.json').read_text())
                assert (out/'reference').resolve()==reference
                assert report['mode']=='reference' and report['status']=='completed_component_uncompared'
                assert not report['errors'] and report['owned_CPU_instructions']==0
                assert report['regular_GPU_report'] is None and report['DSP_report'] is None
                assert report['restored_original_checkpoint'] is None and report['warm_original_frames']==0
                assert report['requested_frames']==len(report['frames'])==23658
                candidate=state['commands']['candidate']
                def option(name):return candidate[candidate.index(name)+1]
                def sha(path):
                    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
                assert report['core_sha256']==sha(option('--core'))
                assert report['frame_controller_script_sha256']==sha(option('--frame-controller-script'))
                overlay=report['experimental_code_overlay']
                assert overlay['sha256']==sha(option('--experimental-mainstage-overlay'))
                assert overlay['applied_before_frame']==48 and overlay['after_exact_restore'] is False
                state.update(status='reference_reused',reference_report=str(reference/'report.json'))
                save()
                continue
            state.update(status='running_'+phase,phase_command=command)
            with (out/(phase+'.log')).open('w')as log:
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;save()
                print(phase+' PID '+str(child.pid)+'; results: '+str(out),flush=True)
                code=child.wait()
            state.update(last_exit_code=code);save()
            assert code==0,(phase,code)
        proof=out/'comparison.json'
        reference=state['commands']['reference'];overlay=reference[reference.index('--experimental-mainstage-overlay')+1]
        command=[sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),
            '--C-run',str(out/'C'),'--reference',str(out/'reference'),'--expected-frames','23658',
            '--experimental-code-overlay',overlay,'--output',str(proof)]
        state.update(status='comparing',phase_command=command);save()
        with (out/'comparison.log').open('w')as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT)
        reviewed=review_completed(out)
        state.update(status='terminal_verified_comparison',**reviewed,
                     total_seconds=time.time()-state['started_unix'])
        save();print(state['status'],proof,flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise


if __name__=='__main__':main()
