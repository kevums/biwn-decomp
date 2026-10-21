"""Fresh ordinary route on the separate native13-frame Deck repair disc."""
import os,signal,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha
def main():
    bp=V/'native-Deck-asset-repair-build-current.json';build=read(bp);assert build['status']=='terminal_native_Deck_asset_repair_disc_built_pending_gameplay'and sha(build['derived_disc'])==build['derived_disc_sha256']
    parent_path=V/'native-Deck-ordinary-input-current.json';parent=read(parent_path);assert parent['status']=='terminal_ordinary_Deck_input_observed_pending_review'
    out=V/'native-Deck-asset-repair-gameplay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=Path(parent['directory'])/'probe.py';assert sha(source)==parent['source_sha256'][str(source)]
    probe=out/'probe.py';probe.write_bytes(source.read_bytes());command=list(parent['command']);command[2]=str(probe);command[command.index('--disc')+1]=build['derived_disc'];command[command.index('--output')+1]=str(out/'candidate')
    state=dict(status='running_fresh_native_Deck_asset_repair',directory=str(out),pid=os.getpid(),command=command,build_proof=str(bp),build_proof_sha256=sha(bp),parent_input_proof=str(parent_path),parent_input_proof_sha256=sha(parent_path),source_sha256={str(p):sha(p)for p in [Path(__file__),source,probe]},snapshot_restores=0,host_CPU_or_task_seeds=0,host_guest_memory_writes=0,native_component_unchanged=True,experimental_restoration_repair=True,default_promoted=False,new_training=False,whole_game_complete=False)
    pointer=V/'native-Deck-asset-repair-gameplay-current.json'
    def mark():save(out/'protocol.json',state);save(pointer,state)
    child=None;mark()
    try:
        with(out/'runtime.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},start_new_session=True);state['child_pid']=child.pid;mark()
            try:code=child.wait(timeout=900)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
        state['child_pid']=None;assert code==0,(out/'runtime.log').read_text()[-4000:]
        report=read(out/'candidate/report.json');observed=read(out/'candidate/gameplay-observation.json');assert report['ordinary_Deck_input_trial']['start_frame']is not None and len(report['ordinary_Deck_input_trial']['inputs'])==400
        state.update(status='terminal_native_Deck_asset_repair_gameplay_pending_review',frames=len(report['frames']),trial_start=report['ordinary_Deck_input_trial']['start_frame'],deck_entries=observed['deck_entries'],deck_native_entries=observed['deck_native_entries'],deck_native_returns=observed['deck_native_returns'],deck_source_steps=observed['deck_source_steps'],deck_invalid_entries=observed['deck_invalid_entries'],acquire_pending=observed['acquire_pending'],mailbox_entries=observed['mb_entries'],observations_path=str(out/'candidate/gameplay-observation.json'),report_path=str(out/'candidate/report.json'),report_sha256=sha(out/'candidate/report.json'));mark();print({k:state[k]for k in ['status','frames','deck_entries','deck_native_returns','acquire_pending']},flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error),child_pid=None if child is None or child.poll()is not None else child.pid);mark();raise
if __name__=='__main__':main()
