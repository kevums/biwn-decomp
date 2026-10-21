"""Record only frames438–439 with the existing pinned-core flight recorder."""
import csv
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from observe_biwn_processor_state import digest, ROOT

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    binary=ROOT/'tools/biwn-gpu-transition-probe'
    core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    bios=ROOT/'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    hashes={str(p):digest(p) for p in (binary,core,image,bios)}
    assert hashes[str(image)]=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    out=session/'emulator-runtime'/('gpu-transition-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    inputs=out/'inputs';inputs.mkdir(parents=True)
    (inputs/image.name).symlink_to(image);(inputs/'jaguarcd_bios.bin').symlink_to(bios)
    command=[str(binary),str(core),str(inputs/image.name),'--frames','900','--bios','--system-dir',str(inputs),
             '--option','virtualjaguar_cd_boot_mode=bios','--option','virtualjaguar_usefastblitter=enabled',
             '--option','virtualjaguar_crash_detect=enabled']
    protocol={'command':command,'cwd':str(out),'wall_budget_seconds':90,'armed_after_frame':437,'disarmed_after_frame':439,
              'watches':['F02100..F0211F writes','F03000..F0305F writes','F03800..F03803 writes'],
              'scope':'Existing flight recorder only. GPU/DSP writes to their own local RAM are not watch-visible. Snapshot register flags can be NCZ-stale; both GPU banks copied directly. No guest-state or core changes.'}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    env=os.environ.copy();env.update(VJ_EXPECT_BUILD='unknown',VJ_HARNESS_LOG_INFO='1',VJ_TRACE_RING='1048576')
    start=time.monotonic()
    with (out/'run.log').open('w') as log:
        process=subprocess.Popen(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        print('BIOS transition process',process.pid,flush=True)
        try:process.wait(timeout=90)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
            protocol['wall_budget_expired']=True
    status={'directory':str(out),'exit_code':process.returncode,'seconds':round(time.monotonic()-start,3),'status':'terminal'}
    (out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    if process.returncode:raise RuntimeError('Transition probe failed: '+str(out))
    with (out/'frame-pcs.csv').open() as f:frames=list(csv.DictReader(f))
    with (session/'emulator-runtime/pc-observer-20261012T221455.207800Z/bios/frame_pcs.csv').open() as f:baseline=list(csv.DictReader(f))
    assert len(frames)==len(baseline)==900
    mismatches=[int(a['frame']) for a,b in zip(frames,baseline) if a!=b]
    with (out/'events.csv').open() as f:events=list(csv.DictReader(f))
    assert {int(e['frame']) for e in events}<={438,439}
    status.update(frames=900,prior_PC_mismatch_frames=mismatches,events=len(events),
                  watch_write_events=sum(e['type']=='12' for e in events),
                  input_and_core_hashes=hashes,observer_source_sha256=digest(ROOT/'scripts/biwn_gpu_transition_probe.c'),
                  artifact_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name not in ('status.json','protocol.json')})
    assert hashes=={str(p):digest(p) for p in (binary,core,image,bios)}
    (out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    (session/'emulator-runtime/gpu-transition-current.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status,indent=2),flush=True)

if __name__=='__main__':main()
