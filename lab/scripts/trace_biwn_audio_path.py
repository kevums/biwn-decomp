"""Bounded audio-path observations of unchanged core and preserved original game."""
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from observe_biwn_processor_state import ROOT, digest


def save(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    bios=ROOT/'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    binary=ROOT/'tools/biwn-audio-path-probe'
    hashes={str(p):digest(p) for p in (core,image,bios,binary)}
    assert hashes[str(core)]=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    assert hashes[str(image)]=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    out=session/'emulator-runtime'/('audio-path-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    inputs=out/'inputs';inputs.mkdir(parents=True)
    (inputs/image.name).symlink_to(image);(inputs/'jaguarcd_bios.bin').symlink_to(bios)
    protocol={'scope':'DSP banks/RAM/history and audio registers sampled after each frame. Trace watches writes to DSP controlsF1A100..F1A13F and DACF1A148..F1A157 from after350 through900. No DSP/core edits. BIOS experiment repeats one GPU bank0R31 assignment after437; HLE has no guest writes by observer.',
              'limits':['Latest1024DSP PCs per frame, incomplete instruction coverage; history may retain prior-frame entries when stopped.',
                        'DSP/GPU local-RAM self-writes invisible to watch recorder; full8192byte post-frame snapshots saved.',
                        'Raw DSP flags can have stale NCZ bits; no condition-code inference.',
                        'Core symbol names/register interpretation are implementation evidence, not primary hardware documentation.',
                        'No reconstructed C or physical hardware test, no listening judgment or proof of music presence.'],
              'ring_capacity':4194304,'wall_budget_seconds_per_run':90,
              'hashes':hashes,'observer_source_sha256':digest(ROOT/'scripts/biwn_audio_path_probe.c')}
    save(out/'protocol.json',protocol)
    stack=Path(json.loads((session/'emulator-runtime/gpu-stack-test-current.json').read_text())['directory'])
    runs=[]
    for name,mode,setting in [('hle','hle',None),('bios-stack-experiment','bios','F03FF0')]:
        cwd=out/name;cwd.mkdir()
        command=[str(binary),str(core),str(inputs/image.name),'--frames','900','--system-dir',str(inputs),
                 '--option','virtualjaguar_cd_boot_mode='+mode,'--option','virtualjaguar_usefastblitter=enabled',
                 '--option','virtualjaguar_crash_detect=enabled']
        if mode=='bios':command.append('--bios')
        env=os.environ.copy();env.update(VJ_EXPECT_BUILD='unknown',VJ_HARNESS_LOG_INFO='1',VJ_TRACE_RING='4194304')
        env.pop('BIWN_EXPERIMENT_GPU_STACK',None)
        if setting:env['BIWN_EXPERIMENT_GPU_STACK']=setting
        status={'name':name,'command':command,'status':'starting','setting':setting,'wall_budget_seconds':90}
        save(cwd/'status.json',status)
        started=time.monotonic()
        with (cwd/'run.log').open('w') as log:
            process=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            status.update(pid=process.pid,status='running');save(cwd/'status.json',status)
            print(name,process.pid,flush=True)
            try:process.wait(timeout=90)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                status['wall_budget_expired']=True
        status.update(status='terminal',exit_code=process.returncode,seconds=round(time.monotonic()-started,3))
        save(cwd/'status.json',status)
        if process.returncode:raise RuntimeError('Audio path probe failed: '+str(cwd))
        with (cwd/'audio-path-frames.csv').open() as f:frames=list(csv.DictReader(f))
        prior=stack/'initialized/processor-state.csv' if setting else session/'emulator-runtime/pc-observer-20261012T221455.207800Z/hle/frame_pcs.csv'
        with prior.open() as f:baseline=list(csv.DictReader(f))
        assert len(frames)==len(baseline)==900
        keys=['frame','cpu_pc','gpu_pc','dsp_pc']+(['framebuffer_hash'] if setting else [])
        mismatches=[int(a['frame']) for a,b in zip(frames,baseline) if any(a[k]!=b[k] for k in keys)]
        assert not mismatches, mismatches[:8]
        assert (cwd/'dsp-frames.bin').stat().st_size==900*8192
        end=re.search(r'AUDIO_PATH frames=(\d+) ring=(\d+) unreadable=(\d+) watched=(\d+) initialization_count=(\d+)',(cwd/'run.log').read_text())
        assert end and int(end[3])==0 and int(end[2])<=4194304
        status.update(directory=str(cwd),frames=900,baseline_trace=str(prior),baseline_compared_columns=keys,
                      baseline_mismatch_frames=mismatches,ring_events=int(end[2]),ring_unreadable=0,
                      watched_events=int(end[4]),initialization_count=int(end[5]),final_frame=frames[-1],
                      artifact_sha256={p.name:digest(p) for p in cwd.iterdir() if p.is_file() and p.name!='status.json'})
        assert status['initialization_count']==bool(setting)
        save(cwd/'status.json',status);runs.append(status)
        print(name,'terminal',status['seconds'],'seconds;',status['watched_events'],'watch events',flush=True)
    assert hashes=={str(p):digest(p) for p in (core,image,bios,binary)}
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'directory':str(out),
            'status':'observations_completed_pending_coordinator_review','protocol':protocol,'runs':runs,
            'inputs_and_core_unchanged':True}
    save(out/'report.json',report);save(session/'emulator-runtime/audio-path-current.json',report)
    print(out,flush=True)


if __name__=='__main__':main()
