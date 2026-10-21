"""One-shot startup-to-outdoor original/C comparison with no saved state.

Both processes start independently and retain full CPU instruction traces.
The sole program repair is the declared word-aligned marker scan.
"""
import hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    proof = json.loads((ROOT / 'verification/merchant-outdoor-route-current.json').read_text())
    assert proof['status'] == 'controller_elevator_to_outdoor_original_C_match_no_scene_transplant'
    assert proof['frames'] == 1200 and proof['ordinary_controller_outdoor_entry_verified']
    out = ROOT / 'runs' / ('fresh-outdoor-route-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    print(out, flush=True)
    prefix = json.loads((ROOT / 'verification/whole-merchant-global-fixed-input.json').read_text())['windows']
    continuation = json.loads((ROOT / 'verification/merchant-outdoor-controller-input.json').read_text())['windows']
    windows = prefix + [dict(start_frame=row['start_frame'] + 23538,
                             stop_frame=row['stop_frame'] + 23538, buttons=row['buttons']) for row in continuation]
    schedule = out / 'input.json'
    schedule.write_text(json.dumps(dict(windows=windows), indent=2) + '\n')
    core = ROOT / 'verification/DSP-music-context-build/20261016T095846.040285Z/source/virtualjaguar_libretro.dylib'
    overlay = ROOT / 'verification/elevator-word-scan-overlay.json'
    common = [sys.executable, str(ROOT / 'scripts/probe_biwn_frame_CPU_owner.py'),
              '--warm-frames', '0', '--frames', '24738', '--core', str(core),
              '--frame-controller-script', str(schedule), '--capture-audio', '--native-CPU-bridge', '--extended-CPU',
              '--CPU-candidate', str(ROOT / 'verification/loaded-scene-doorway-CPU-experimental-candidate.json'),
              '--native-CPU-candidate', str(ROOT / 'verification/loaded-scene-doorway-native-CPU-experimental-candidate.json'),
              '--experimental-mainstage-overlay', str(overlay)]
    for frame in [600, 15900, 23538, 23698, 24138, 24488, 24620, 24738]:
        common += ['--capture-frame', str(frame)]
    candidate = ['--regular-GPU-mode', 'C', '--renderer-bundles', '--renderer-overlays',
                 '--material-bundles', '--control-bundles', '--setup-bundles', '--native-GPU-bridge',
                 '--GPU-frame-only', '--native-GPU-candidate',
                 str(ROOT / 'verification/C-space-mail-shared-GPU-experimental-candidate.json'),
                 '--stop-on-GPU-original', '--native-DSP-owner', '--DSP-owner-kind', 'router', '--require-owned-DSP',
                 '--DSP-router-candidate', str(ROOT / 'verification/fast-DSP-router-experimental-candidate.json')]
    commands = dict(reference=common + ['--mode', 'reference', '--output', str(out / 'reference')],
                    C=common + ['--mode', 'C', *candidate, '--output', str(out / 'C')])
    assert all('--restore-original-report' not in command and '--experimental-code-overlay' not in command
               for command in commands.values())
    pinned = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in [
        Path(__file__), ROOT / 'scripts/probe_biwn_frame_CPU_owner.py',
        ROOT / 'scripts/compare_biwn_frame_CPU_only.py', schedule, core, overlay]}
    state = dict(status='prepared', directory=str(out), pid=os.getpid(), frames=24738,
                 commands=commands, children={}, hashes=pinned, started_unix=time.time(),
                 scope='Two independent emulator starts; no original warmup, checkpoint restore, scene RAM transplant '
                       'or player relocation. Same recorded ordinary buttons for startup, merchant, two elevator floors and '
                       'outdoor exit. Existing18-byte marker-scan repair is applied once mainstage bytes are loaded. '
                       'Source CPU/GPU/DSP comparison pending. Original IRQ/HLE/object processor/devices remain.')

    def save():
        data = json.dumps(state, indent=2) + '\n'
        (out / 'protocol.json').write_text(data)
        (ROOT / 'verification/fresh-outdoor-route-active.json').write_text(data)

    save()
    children, logs = {}, {}
    try:
        for phase, command in commands.items():
            logs[phase] = (out / (phase + '.log')).open('w')
            children[phase] = subprocess.Popen(command, stdout=logs[phase], stderr=subprocess.STDOUT)
            state['children'][phase] = dict(pid=children[phase].pid, status='running')
            state['status'] = 'running_independent_reference_and_C'
            save()
            print(phase, 'PID', children[phase].pid, flush=True)
        pending = set(children)
        while pending:
            for phase in list(pending):
                code = children[phase].poll()
                if code is not None:
                    state['children'][phase].update(status='terminal_completed' if code == 0 else 'terminal_failed', exit_code=code)
                    logs[phase].close()
                    pending.remove(phase)
                    save()
                    print(phase, 'exit', code, flush=True)
            if pending:
                time.sleep(2)
        assert all(row['exit_code'] == 0 for row in state['children'].values()), state['children']
        state['status'] = 'comparing'
        save()
        command = [sys.executable, str(ROOT / 'scripts/compare_biwn_frame_CPU_only.py'),
                   '--C-run', str(out / 'C'), '--reference', str(out / 'reference'),
                   '--expected-frames', '24738', '--experimental-code-overlay', str(overlay),
                   '--output', str(out / 'comparison.json')]
        state['comparison_command'] = command
        save()
        with (out / 'comparison.log').open('w') as log:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
        comparison = json.loads((out / 'comparison.json').read_text())
        assert comparison['status'] == 'CPU_GPU_DSP_frame_comparison_pass' and all(comparison['checks'].values())
        for phase in ['reference', 'C']:
            report = json.loads((out / phase / 'report.json').read_text())
            assert report['restored_original_checkpoint'] is None and report['warm_original_frames'] == 0
            raw = (out / phase / 'final-RAM.bin').read_bytes()
            assert int.from_bytes(raw[0x49c60:0x49c62], 'big') == 1
            assert int.from_bytes(raw[0x49c62:0x49c64], 'big') == 0
        state.update(status='terminal_startup_to_outdoor_CPU_GPU_DSP_match',
                     comparison=str(out / 'comparison.json'), total_seconds=time.time() - state['started_unix'])
        save()
        (ROOT / 'verification/fresh-outdoor-route-current.json').write_text(json.dumps(state, indent=2) + '\n')
        print(state['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error), total_seconds=time.time() - state['started_unix'])
        save()
        raise
    finally:
        for stream in logs.values():
            stream.close()


if __name__ == '__main__':
    main()
