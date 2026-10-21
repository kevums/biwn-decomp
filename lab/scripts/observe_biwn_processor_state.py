"""Bounded BIOS/HLE post-frame snapshots; no emulator core modifications."""
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def main():
    session = Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    core = ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    binary = ROOT/'tools/biwn-processor-state-probe'
    image = ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    bios = ROOT/'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    preserved = {str(p): digest(p) for p in (core, binary, image, bios)}
    assert preserved[str(image)] == '0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = session/'emulator-runtime'/('processor-state-'+stamp)
    inputs = out/'inputs'; inputs.mkdir(parents=True)
    (inputs/image.name).symlink_to(image)
    (inputs/'jaguarcd_bios.bin').symlink_to(bios)
    baseline = session/'emulator-runtime/pc-observer-20261012T221455.207800Z'
    env = os.environ.copy(); env.update(VJ_EXPECT_BUILD='unknown', VJ_HARNESS_LOG_INFO='1')
    rows = []
    for mode in ('bios', 'hle'):
        cwd = out/mode; cwd.mkdir()
        command = [str(binary), str(core), str(inputs/image.name), '--frames', '900',
                   '--system-dir', str(inputs), '--option', 'virtualjaguar_cd_boot_mode='+mode,
                   '--option', 'virtualjaguar_usefastblitter=enabled',
                   '--option', 'virtualjaguar_crash_detect=enabled']
        if mode == 'bios': command.append('--bios')
        status = {'mode': mode, 'command': command, 'cwd': str(cwd),
                  'started_at': datetime.now(timezone.utc).isoformat(), 'wall_budget_seconds': 90}
        (cwd/'status.json').write_text(json.dumps(status, indent=2)+'\n')
        start = time.monotonic()
        with (cwd/'run.log').open('w') as log:
            process = subprocess.Popen(command, cwd=cwd, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            print(mode, process.pid, flush=True)
            try: process.wait(timeout=90)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL); process.wait()
                status['wall_budget_expired'] = True
        status.update(exit_code=process.returncode, seconds=round(time.monotonic()-start, 3), status='terminal')
        (cwd/'status.json').write_text(json.dumps(status, indent=2)+'\n')
        if process.returncode: raise RuntimeError('Probe failed: '+str(cwd))
        with (cwd/'processor-state.csv').open() as f: frames = list(csv.DictReader(f))
        with (baseline/mode/'frame_pcs.csv').open() as f: previous = list(csv.DictReader(f))
        assert len(frames) == len(previous) == 900
        assert (cwd/'gpu-frames.bin').stat().st_size == 900*4096
        assert (cwd/'dsp-frames.bin').stat().st_size == 900*8192
        mismatches = [int(a['frame']) for a,b in zip(frames,previous)
                      if any(a[k] != b[k] for k in ('frame','cpu_pc','gpu_pc','dsp_pc'))]
        low = [f for f in frames if int(f['gpu_pc'],16) < 0x4000]
        wait = [f for f in frames if int(f['cpu_pc'],16) in (0x180178,0x18017e,0x180182)]
        status.update(frames=900, prior_PC_trace_mismatch_frames=mismatches,
                      low_gpu_pc_frames=len(low), first_low_gpu_pc=low[0] if low else None,
                      boot_wait_frames=len(wait), first_boot_wait=wait[0] if wait else None,
                      final_frame=frames[-1],
                      nonzero_i2s_capture_frames=sum(int(f['i2s_nonzero_capture_count'])>0 for f in frames),
                      artifact_sha256={p.name:digest(p) for p in cwd.iterdir() if p.is_file() and p.name!='status.json'})
        (cwd/'status.json').write_text(json.dumps(status, indent=2)+'\n')
        rows.append(status)
        print(mode, 'terminal', status['seconds'], 'seconds;', len(mismatches), 'PC mismatch frames', flush=True)
    assert preserved == {str(p): digest(p) for p in (core,binary,image,bios)}
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'directory': str(out),
              'runs': rows, 'preserved_inputs_and_core': preserved,
              'observer_source_sha256': digest(ROOT/'scripts/biwn_processor_state_probe.c'),
              'originals_and_core_unchanged': True, 'framebuffer_hash_collection_enabled': False,
              'scope': 'Read-only direct diagnostic accessors and post-frame RAM snapshots of the original game in the pinned emulator. BIOS path is assisted. Matching sampled PCs do not prove every side effect unchanged, complete instruction coverage, hardware correctness or reconstructed C execution.'}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    (session/'emulator-runtime/processor-state-current.json').write_text(json.dumps(report, indent=2)+'\n')
    print(out, flush=True)

if __name__ == '__main__': main()
