"""Fresh native disc boot, existing outdoor route, then ordinary Deck inputs.

No snapshot restore, supplied CPU/task state, selector repair or guest writes.
The retained HLE/emulator/device/IRQ providers and read-only monitors remain.
"""
import argparse
import json
import os
import signal
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT; V=ROOT/'verification'; read=common.read; save=common.save; sha=common.sha

def replace(text, old, new):
    assert text.count(old)==1,(old[:100],text.count(old))
    return text.replace(old,new)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--original-disc',action='store_true');args=parser.parse_args()
    label='original-Deck-ordinary-input'if args.original_disc else 'native-Deck-ordinary-input-v2'
    out=V/label/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    parent_path=V/'native-Deck-coordinate-v2-quiescent-candidate-current.json';parent=read(parent_path)
    assert parent['status'].startswith('terminal_')and parent['live_monitor_pass']
    parent_probe=Path(parent['command'][2]);text=parent_probe.read_text()
    text=replace(text,'    navigation_inputs = set()', '    navigation_inputs = set()\n    deck_trial_start=None\n    deck_trial_inputs=[]')
    text=replace(text,'            core.retro_run()', '''            if deck_trial_start is not None:
                offset=current_frame-deck_trial_start
                buttons=['1']if 1<=offset<9 else ['B','C']if 25<=offset<34 else ['0']if 225<=offset<234 else []
                navigation_inputs={button_ids[name]for name in buttons}
                navigation={'ordinary_Deck_trial_offset':offset,'buttons':buttons,'no_guest_memory_writes':True}
                deck_trial_inputs.append({'frame':current_frame,'offset':offset,'buttons':buttons})
            core.retro_run()''')
    text=replace(text, "            if outdoor_hold>=120 and row['player_mode_word']==1:\n                if observer.observer_quiescent():break\n                assert outdoor_hold<632,'Watched calls did not quiesce within512extra normalframes'", """            if deck_trial_start is None and outdoor_hold>=120 and row['player_mode_word']==1:
                if observer.observer_quiescent():deck_trial_start=current_frame
                else:assert outdoor_hold<632,'Watched calls did not quiesce within512extra normalframes'
            if deck_trial_start is not None and current_frame-deck_trial_start>=400:break""")
    text=replace(text,"        division_observer=c.CDLL(", "        report['ordinary_Deck_input_trial']=dict(start_frame=deck_trial_start,inputs=deck_trial_inputs,scope='Ordinary keypad1,release,B+C,release,0,release after fresh outdoor route. No guest code/RAM/CPU/task state injection or extra selector patch.')\n        division_observer=c.CDLL(")
    if args.original_disc:text=replace(text,"report['native_compiled_game_C_execution']=True","report['native_compiled_game_C_execution']=False")
    probe=out/'probe.py';probe.write_text(text)
    command=list(parent['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'candidate')
    build=read(V/'native-Deck-coordinate-disc-build-current.json')
    if args.original_disc:
        original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';manifest=read(V/'biwn-disc-resources.json');assert sha(original)==manifest['source_CDI_sha256'];command[command.index('--disc')+1]=str(original)
    state=dict(original_disc_baseline=args.original_disc,status='running_fresh_native_disc_ordinary_Deck_input',directory=str(out),pid=os.getpid(),command=command,parent=str(parent_path),parent_sha256=sha(parent_path),source_sha256={str(p):sha(p)for p in [Path(__file__),parent_probe,probe]},snapshot_restores=0,host_guest_memory_writes=0,host_CPU_or_task_seeds=0,new_training=False,whole_game_complete=False,native_disc_changed=False)
    pointer=V/(label+'-current.json')
    def mark():save(out/'protocol.json',state);save(pointer,state)
    child=None;mark()
    try:
        with(out/'runtime.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},start_new_session=True);state['child_pid']=child.pid;mark()
            try:code=child.wait(timeout=900)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
        state['child_pid']=None;assert code==0,(out/'runtime.log').read_text()[-5000:]
        report=read(out/'candidate/report.json');observed=read(out/'candidate/gameplay-observation.json')
        assert report['ordinary_Deck_input_trial']['start_frame']is not None
        assert len(report['ordinary_Deck_input_trial']['inputs'])==400
        assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']
        state.update(status='terminal_ordinary_Deck_input_observed_pending_review',frames=len(report['frames']),trial_start=report['ordinary_Deck_input_trial']['start_frame'],deck_entries=observed.get('deck_entries'),deck_native_entries=observed.get('deck_native_entries'),deck_native_returns=observed.get('deck_native_returns'),deck_source_steps=observed.get('deck_source_steps'),deck_invalid_entries=observed.get('deck_invalid_entries'),mailbox_entries=observed.get('mb_entries'),observations=observed,report=str(out/'candidate/report.json'),report_sha256=sha(out/'candidate/report.json'))
        mark();print(json.dumps({k:state[k]for k in ['status','frames','trial_start','deck_entries','deck_native_entries','deck_native_returns']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error),child_pid=None if child is None or child.poll()is not None else child.pid);mark();raise

if __name__=='__main__':main()
