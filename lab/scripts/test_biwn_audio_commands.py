"""No-input versus A/B/C input, tracing bounded original-game audio commands."""
import csv
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from observe_biwn_processor_state import ROOT,digest


def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def rows(path):
    with path.open() as stream:return list(csv.DictReader(stream))


def main():
    s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    bios=ROOT/'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    binary=ROOT/'tools/biwn-audio-command-probe'
    hashes={str(p):digest(p) for p in (core,image,bios,binary)}
    assert hashes[str(core)]=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    assert hashes[str(image)]=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    out=s/'emulator-runtime'/('audio-commands-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    inputs=out/'inputs';inputs.mkdir(parents=True)
    (inputs/image.name).symlink_to(image);(inputs/'jaguarcd_bios.bin').symlink_to(bios)
    protocol={'scope':'Assisted BIOS with the earlier single GPU bank0R31 assignment after437. No DSP/core edits. Compare no input with scripted A/B/C presses. Trace CPU-visible writes to F1BADC..F1BAE7 and3BCE0..3BD7F after350; post-frame mailbox and40mainRAM words captured.',
              'source':str(ROOT/'scripts/biwn_audio_command_probe.c'),'source_sha256':digest(ROOT/'scripts/biwn_audio_command_probe.c'),
              'hashes':hashes,'limitations':['DSP self-writes to local RAM are not watch-visible; post-frame sampling can miss transient commands.','Chosen buttons/900frames are limited interaction, not exhaustive gameplay or sound triggering.','Bus records can be halves of32bit writes. No original hardware or rebuilt-game validation.']}
    save(out/'protocol.json',protocol)
    runs=[];all_frames={};all_commands={}
    for name,events in [('baseline',[]),('buttons',['690:a:30','780:b:30','870:c:30'])]:
        d=out/name;d.mkdir()
        cmd=[str(binary),str(core),str(inputs/image.name),'--frames','900','--bios','--system-dir',str(inputs),
             '--option','virtualjaguar_cd_boot_mode=bios','--option','virtualjaguar_usefastblitter=enabled',
             '--option','virtualjaguar_crash_detect=enabled']
        for e in events:cmd+=['--press',e]
        env=os.environ.copy();env.update(BIWN_EXPERIMENT_GPU_STACK='F03FF0',VJ_EXPECT_BUILD='unknown',VJ_HARNESS_LOG_INFO='1',VJ_TRACE_RING='4194304')
        status={'name':name,'command':cmd,'status':'starting','wall_budget_seconds':90,'events':events};save(d/'status.json',status)
        started=time.monotonic()
        with (d/'run.log').open('w') as log:
            p=subprocess.Popen(cmd,cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            status.update(pid=p.pid,status='running');save(d/'status.json',status);print(name,p.pid,flush=True)
            try:p.wait(timeout=90)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                status['wall_budget_expired']=True
        status.update(status='terminal',exit_code=p.returncode,seconds=round(time.monotonic()-started,3),directory=str(d));save(d/'status.json',status)
        if p.returncode:raise RuntimeError('Audio command probe failed: '+str(d))
        f=rows(d/'audio-path-frames.csv');c=rows(d/'audio-command-frames.csv');w=rows(d/'audio-watch-events.csv')
        assert len(f)==len(c)==900
        status.update(watch_records=len(w),game_phase_watch_records=[e for e in w if int(e['frame'])>=622],
                      game_phase_nonzero_audio_frames=[x['frame'] for x in f[621:] if int(x['i2s_nonzero_capture_count'])],
                      artifact_sha256={p.name:digest(p) for p in d.iterdir() if p.is_file() and p.name!='status.json'})
        save(d/'status.json',status);runs.append(status);all_frames[name]=f;all_commands[name]=c
        print(name,'terminal',status['seconds'],len(w),'watch records',flush=True)
    prior=Path(json.loads((s/'emulator-runtime/audio-path-current.json').read_text())['directory'])/'bios-stack-experiment/audio-path-frames.csv'
    assert all_frames['baseline']==rows(prior)
    assert all_frames['baseline'][:689]==all_frames['buttons'][:689]
    assert all_commands['baseline'][:689]==all_commands['buttons'][:689]
    differences={k:[int(a['frame']) for a,b in zip(all_frames['baseline'],all_frames['buttons']) if a[k]!=b[k]] for k in ('cpu_pc','gpu_pc','dsp_pc','framebuffer_hash','audio_nonsilent_total')}
    command_differences=[int(a['frame']) for a,b in zip(all_commands['baseline'],all_commands['buttons']) if a!=b]
    assert hashes=={str(p):digest(p) for p in (core,image,bios,binary)}
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'directory':str(out),'status':'completed_pending_coordinator_review','protocol':protocol,'runs':runs,
            'baseline_all900_frame_rows_match_audio_path_probe':True,'pre_input_frame_and_command_rows_equal_through689':True,
            'difference_frames':differences,'command_state_difference_frames':command_differences,'inputs_core_unchanged':True}
    save(out/'report.json',report);save(s/'emulator-runtime/audio-commands-current.json',report)
    print(json.dumps({'directory':str(out),'difference_counts':{k:len(v) for k,v in differences.items()},'command_state_difference_frames':command_differences,'game_audio_nonzero_frames':[r['game_phase_nonzero_audio_frames'] for r in runs]}),flush=True)


if __name__=='__main__':main()
