"""Bounded, local headless RAM and framebuffer captures of the preserved CDI.

These are assisted emulator observations, not physical hardware validation.
No model inference, source-image edits, emulator-core edits or network calls.
"""
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import extract_biwn_stage as stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['bios', 'hle'], action='append')
    parser.add_argument('--press', action='append', default=[])
    args = parser.parse_args()
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    vendor = root / 'tools/virtualjaguar-runtime-source'
    core = vendor / 'virtualjaguar_libretro.dylib'
    image = root / 'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    bios = root / 'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    before = {str(p): stage.cdi_layout.sha(p) for p in [image, bios]}
    if before[str(image)] != stage.IMAGE_SHA:
        raise ValueError('Preserved CDI changed')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = session / 'emulator-runtime' / ('capture-' + stamp)
    inputs = output / 'inputs'
    inputs.mkdir(parents=True)
    (inputs / image.name).symlink_to(image)
    (inputs / 'jaguarcd_bios.bin').symlink_to(bios)
    environment = os.environ.copy()
    environment.update(VJ_EXPECT_BUILD='unknown', VJ_HARNESS_LOG_INFO='1')
    runs = []
    for mode in args.mode or ['bios', 'hle']:
        for kind, tool in [('ram', 'cd_wedge_probe'), ('visual', 'cd_visual_verify')]:
            cwd = output / mode / kind
            cwd.mkdir(parents=True)
            binary = vendor / 'test/tools' / tool
            command = [str(binary), str(core), str(inputs / image.name), '--frames', '900',
                       '--system-dir', str(inputs),
                       '--option', 'virtualjaguar_cd_boot_mode=' + mode,
                       '--option', 'virtualjaguar_usefastblitter=enabled',
                       '--option', 'virtualjaguar_crash_detect=enabled']
            if mode == 'bios':
                command.append('--bios')
            for press in args.press:
                command += ['--press', press]
            if kind == 'ram':
                command += ['--arm', '1000', '--freeze-frames', '900', '--snap-prefix', str(cwd / 'snapshot')]
                for frame in [0, 1, 30, 120, 300, 600, 899]:
                    command += ['--snap', str(frame)]
            else:
                command += ['--outdir', str(cwd), '--shot-every', '299', '--json']
            run = {'mode': mode, 'kind': kind, 'command': command, 'cwd': str(cwd),
                   'core_sha256': stage.cdi_layout.sha(core),
                   'probe_sha256': stage.cdi_layout.sha(binary),
                   'started_at': datetime.now(timezone.utc).isoformat(),
                   'frames': 900, 'wall_budget_seconds': 90, 'log': str(cwd / 'run.log'),
                   'input_events': args.press}
            started = time.monotonic()
            with (cwd / 'run.log').open('w') as log:
                process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=log,
                                           stderr=subprocess.STDOUT, start_new_session=True)
                run.update(pid=process.pid, status='running')
                (cwd / 'status.json').write_text(json.dumps(run, indent=2) + '\n')
                print(mode, kind, process.pid, flush=True)
                try:
                    process.wait(timeout=90)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    run['wall_budget_expired'] = True
            run.update(status='terminal', exit_code=process.returncode,
                       seconds=round(time.monotonic() - started, 3),
                       finished_at=datetime.now(timezone.utc).isoformat())
            run['artifacts'] = {p.name: stage.cdi_layout.sha(p) for p in sorted(cwd.iterdir())
                                if p.suffix in ['.ram', '.gpu', '.dsp', '.tom', '.ppm']}
            (cwd / 'status.json').write_text(json.dumps(run, indent=2) + '\n')
            runs.append(run)
            print(mode, kind, 'terminal', process.returncode, flush=True)
    after = {str(p): stage.cdi_layout.sha(p) for p in [image, bios]}
    if after != before:
        raise ValueError('Input hashes changed during capture')
    report = {'time': datetime.now(timezone.utc).isoformat(), 'runs': runs,
              'input_hashes_before_and_after': after, 'inputs_unchanged': True,
              'scope': '900-frame assisted emulator RAM/framebuffer observations. No local LLM dispatch. BIOS mode still injects boot stub/trampoline/synthetic TOC. No menu/gameplay or hardware-accuracy claim.'}
    (output / 'captures.json').write_text(json.dumps(report, indent=2) + '\n')
    (session / 'emulator-runtime/current-capture.json').write_text(json.dumps({'directory': str(output)}, indent=2) + '\n')
    print(output / 'captures.json', flush=True)


if __name__ == '__main__':
    main()
