"""Replay verified long inputs, adding read-only input/slot-state observations."""
import csv
from datetime import datetime,timezone
import json,os,re,signal,subprocess,time
from pathlib import Path
from observe_biwn_processor_state import ROOT,digest


def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def rows(path):
    with path.open()as stream:return list(csv.DictReader(stream))


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    prior=json.loads((session/'emulator-runtime/long-audio-current.json').read_text())
    baseline=next(r for r in prior['runs']if r['name']=='long-input');old=Path(baseline['directory'])
    assert baseline['status']=='terminal'and baseline['exit_code']==0
    core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib';image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';bios=ROOT/'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin';binary=ROOT/'tools/biwn-inventory-probe'
    sources=[core,image,bios,binary,ROOT/'scripts/biwn_audio_streaming_probe.c',ROOT/'tools/biwn-audio-streaming-probe']
    hashes={str(p):digest(p)for p in sources}
    assert hashes[str(core)]=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    assert hashes[str(image)]=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    out=session/'emulator-runtime'/('inventory-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));inputs=out/'inputs';inputs.mkdir(parents=True)
    (inputs/image.name).symlink_to(image);(inputs/'jaguarcd_bios.bin').symlink_to(bios)
    cmd=list(baseline['command']);cmd[0]=str(binary);cmd[2]=str(inputs/image.name);cmd[cmd.index('--system-dir')+1]=str(inputs)
    protocol={'source':str(ROOT/'scripts/biwn_inventory_probe.c'),'source_sha256':digest(ROOT/'scripts/biwn_inventory_probe.c'),'command':cmd,'hashes':hashes,
              'baseline':str(old),'scope':'Exact same9000frame assisted-BIOS input replay and one GPU bank0R31 assignment after437; observer adds input49BAC and state49D54/49D56postframe samples plus read/write watches. No core/DSP changes.',
              'limits':['Latest1024PC windows and postframe data are sampled, not instruction-time memory or complete execution coverage.','Watch records have no width field; reconstruct widths only where original instruction and pinned emitter support it.','Original-game emulator observation, not reconstructed rendering or hardware proof.']}
    save(out/'protocol.json',protocol);state={'status':'starting','command':cmd,'wall_budget_seconds':180};save(out/'status.json',state)
    env=os.environ.copy();env.update(BIWN_EXPERIMENT_GPU_STACK='F03FF0',VJ_EXPECT_BUILD='unknown',VJ_HARNESS_LOG_INFO='1',VJ_TRACE_RING='4194304')
    started=time.monotonic()
    with (out/'run.log').open('w')as log:
        p=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);state.update(status='running',pid=p.pid);save(out/'status.json',state);print('inventory',p.pid,'running',flush=True)
        try:p.wait(timeout=180)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
            state['wall_budget_expired']=True
    state.update(status='terminal',exit_code=p.returncode,seconds=round(time.monotonic()-started,3));save(out/'status.json',state)
    assert p.returncode==0,'Probe failed; inspect retained log'
    for name in ['audio-path-frames.csv','audio-command-frames.csv','dsp-frames.bin','dsp-banks.csv','dsp-history.csv','observed_CPU_pcs.csv']:
        assert digest(out/name)==digest(old/name),'New observer changes baseline: '+name
    for ppm in old.glob('frame-*.ppm'):assert digest(out/ppm.name)==digest(ppm)
    inventory=rows(out/'inventory-frames.csv');assert len(inventory)==9000
    end=re.search(r'AUDIO_STREAM frames=(\d+) ring=(\d+) unreadable=(\d+) watched=(\d+) initialization_count=(\d+) max_frame_events=(\d+) CPU_pcs=(\d+)',(out/'run.log').read_text())
    assert end and end[1]=='9000'and end[3]=='0'and end[5]=='1'and int(end[6])<4194304
    assert hashes=={str(p):digest(p)for p in sources}
    changes=[]
    for a,b in zip(inventory[621:],inventory[622:]):
        if a['state_49d54']!=b['state_49d54']or a['state_49d56']!=b['state_49d56']:
            changes.append({'frame':int(b['frame']),'input':b['input_49bac'],'before':[a['state_49d54'],a['state_49d56']],'after':[b['state_49d54'],b['state_49d56']]})
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'observed_inventory_replay_completed_pending_review','directory':str(out),'protocol':protocol,
            'run':state,'all9000_baseline_frames_commands_DSP_CPU_catalog_and_captures_identical':True,
            'ring_events_consumed':int(end[2]),'watched_records':int(end[4]),'max_frame_events':int(end[6]),'unreadable_records':0,
            'post621_slot_state_changes':changes,'final_inventory_state':inventory[-1],'inputs_core_previous_observer_unchanged':True,
            'artifact_sha256':{p.name:digest(p)for p in out.iterdir()if p.is_file()and p.name not in ['report.json','protocol.json']}}
    save(out/'report.json',report);save(session/'emulator-runtime/inventory-current.json',report)
    print(json.dumps({'directory':str(out),'seconds':state['seconds'],'slot_changes':changes,'watched_records':int(end[4]),'baseline_match':True}),flush=True)


if __name__=='__main__':main()
