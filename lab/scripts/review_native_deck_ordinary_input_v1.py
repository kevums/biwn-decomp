"""Review the ordinary input witness without relabeling a stalled run as pass."""
import ctypes as c
from datetime import datetime, timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT; V=ROOT/'verification'; read=common.read; save=common.save; sha=common.sha

class CPU(c.Structure):
    _fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
class Event(c.Structure):
    _fields_=[('frame',c.c_uint32),('pc',c.c_uint32),('cpu',CPU),('fields',c.c_uint32*6)]

def lane(pointer):
    state=read(pointer);assert state['status']=='terminal_ordinary_Deck_input_observed_pending_review'
    for p,digest in state['source_sha256'].items():assert sha(p)==digest
    folder=Path(state['directory'])/'candidate';report_path=folder/'report.json';report=read(report_path)
    assert sha(report_path)==state['report_sha256']
    assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']
    assert sha(report['disc'])==report['disc_sha256']and sha(report['core'])==report['core_sha256']
    trial=report['ordinary_Deck_input_trial'];assert len(trial['inputs'])==400
    for i,row in enumerate(trial['inputs'],1):
        expected=['1']if 1<=i<9 else ['B','C']if 25<=i<34 else ['0']if 225<=i<234 else []
        assert row==dict(frame=trial['start_frame']+i,offset=i,buttons=expected)
    observations=read(folder/'gameplay-observation.json')
    raw_ram=folder/'RAM-final.bin';assert sha(raw_ram)==report['final_RAM_sha256'];ram=raw_ram.read_bytes()
    event_path=folder/'gameplay-events.bin';raw=event_path.read_bytes();assert c.sizeof(Event)==112 and len(raw)%112==0
    entries=[]
    for i in range(0,len(raw),112):
        event=Event.from_buffer_copy(raw[i:i+112])
        if event.frame>trial['start_frame']and event.pc in [0x1ac68,0x1b044]:
            entries.append(dict(frame=event.frame,pc=hex(event.pc),registers=list(event.cpu.r)))
    fields=['deck_entries','deck_native_entries','deck_native_returns','deck_source_steps','deck_invalid_entries','acquire_entries','acquire_returns','acquire_pending','acquire_monitor_errors','acquire_user_stack_outside','mb_pending','mb_errors','mb_context_errors','arena_errors']
    summary=dict(directory=str(folder),frames=len(report['frames']),trial_start=trial['start_frame'],trial_frames=400,last_CPU=report['frames'][-1]['CPU_full'],observations={key:observations.get(key)for key in fields},post_input_resource_entries=entries,CD_progress=hex(int.from_bytes(ram[0xbd848:0xbd84c],'big')),last_video_sha256=report['frames'][-1]['video_sha256'],disc=report['disc'],disc_sha256=report['disc_sha256'],core_sha256=report['core_sha256'])
    paths=[pointer,report_path,raw_ram,folder/'state-final.bin',event_path,folder/'gameplay-observation.json',folder/'original-emulator-final-frame.png',Path(state['directory'])/'probe.py',Path(state['directory'])/'runtime.log',*[Path(p)for p in state['source_sha256']]]
    return summary,paths

def main():
    out=V/'native-Deck-ordinary-input-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    candidate,paths=lane(V/'native-Deck-ordinary-input-current.json')
    obs=candidate['observations'];assert obs['deck_entries']==obs['deck_native_entries']==obs['deck_native_returns']==0
    assert obs['acquire_entries']==124 and obs['acquire_returns']==123 and obs['acquire_pending']==1
    assert all(obs[k]==0 for k in ['acquire_monitor_errors','acquire_user_stack_outside','mb_pending','mb_errors','mb_context_errors','arena_errors'])
    ram=Path(candidate['directory'],'RAM-final.bin').read_bytes();frame=candidate['last_CPU']['registers'][10]
    get=lambda a:int.from_bytes(ram[a:a+4],'big')
    last_loader=[row for row in candidate['post_input_resource_entries']if row['pc']=='0x1b044'][-1]
    assert get(frame+60)==last_loader['registers'][15]
    candidate['pending_native_loader']=dict(frame_address=hex(frame),virtual_loader_SP=hex(get(frame+60)),expected_transfer_end=hex(get(frame+40)),actual_CD_progress=candidate['CD_progress'],seek_byte_offset=hex(get(frame+12)),marker=hex(get(frame+8)),requested_bytes=hex(get(frame+44)),returned_word_pointer=hex(get(frame+48)),scope='Final actual native loader frame and original public1B044 entry event agree. Progress below requested end; this identifies the observed wait, not its cause.')
    assert int(candidate['CD_progress'],16)<get(frame+40)
    baseline=None;baseline_path=V/'original-Deck-ordinary-input-current.json'
    if baseline_path.exists()and read(baseline_path)['status']=='terminal_ordinary_Deck_input_observed_pending_review':
        baseline,bound=lane(baseline_path);paths+=bound
    elif baseline_path.exists()and read(baseline_path)['status']=='terminal_failed':
        original=read(baseline_path);folder=Path(original['directory'])/'candidate';rp=folder/'report.json'
        if rp.exists():
            report=read(rp);assert report['ordinary_Deck_input_trial']['start_frame']is None and not report['ordinary_Deck_input_trial']['inputs']
            assert len(report['frames'])==report['scene_change_frame']+report['stop_after_scene_change_frames'] and report['native_compiled_game_C_execution']is False
            assert sha(report['disc'])==report['disc_sha256']
            baseline=dict(status='original_disc_route_did_not_reach_Deck_trial',directory=str(folder),frames=len(report['frames']),trial_start=None,last_CPU=report['frames'][-1]['CPU_full'],last_navigation=report['frames'][-1]['navigation'],disc=report['disc'],disc_sha256=report['disc_sha256'],cause_comparison_valid=False,scope='Unmodified original disc was run with the same adaptive navigation logic, but never reached the outdoor/quiescent condition that starts the new Deck input sequence. This is not a matched Deck-loading baseline and cannot attribute the candidate stall.')
            paths.extend([baseline_path,rp,folder/'gameplay-observation.json',folder/'RAM-final.bin',folder/'state-final.bin',folder/'original-emulator-final-frame.png',Path(original['directory'])/'probe.py',Path(original['directory'])/'runtime.log'])
    state=dict(status='terminal_ordinary_Deck_input_stall_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),candidate=candidate,original_disc_baseline=baseline,cause_identified=False,natural_coordinate_activation_verified=False,native_disc_changed=False,default_promoted=False,new_training=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in set(paths+[Path(__file__)])},scope='Fresh native disc and ordinary input after the same adaptive route. Zero coordinate calls, one unfinished resource acquisition with CD progress below requested end. Read-only monitors report no observed ABI/stack/arena errors; pending acquisition prevents whole-route pass. Original baseline may use native-specific observers only as raw event collectors; native-only ownership/arena checks on original image are inapplicable. No timing/physical/whole-game or cause attribution.')
    save(out/'report.json',state);save(V/'native-Deck-ordinary-input-reviewed-current.json',state);print(state['status'],'baseline complete',baseline is not None)

if __name__=='__main__':main()
