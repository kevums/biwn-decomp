"""One-shot startup-to-outdoor original/C comparison with no saved state.

Both processes start independently and retain full CPU instruction traces.
The sole program repair is the declared word-aligned marker scan. This variant retains the unmodified program until the exact previously verified merchant machine, applies the sole repair beforeframe23539, and continues through the recorded elevator/exit inputs. Earlier early-repair parity tests continue unchanged.
"""
import hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    startup = json.loads((ROOT / 'verification/CPU-IRQ-selection-startup-current.json').read_text())
    assert startup['status'] == 'terminal_three_lane_startup_processors_and_IRQ_selection_entry_match'
    proof = json.loads((ROOT / 'verification/merchant-outdoor-route-current.json').read_text())
    assert proof['status'] == 'controller_elevator_to_outdoor_original_C_match_no_scene_transplant'
    assert proof['frames'] == 1200 and proof['ordinary_controller_outdoor_entry_verified']
    out = ROOT / 'runs' / ('merchant-gated-outdoor-route-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    print(out, flush=True)
    prefix = json.loads((ROOT / 'verification/whole-merchant-global-fixed-input.json').read_text())['windows']
    continuation = json.loads((ROOT / 'verification/merchant-outdoor-controller-input.json').read_text())['windows']
    windows = prefix + [dict(start_frame=row['start_frame'] + 23538,
                             stop_frame=row['stop_frame'] + 23538, buttons=row['buttons']) for row in continuation]
    schedule = out / 'input.json'
    schedule.write_text(json.dumps(dict(windows=windows), indent=2) + '\n')
    core = ROOT / 'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    overlay = ROOT / 'verification/elevator-word-scan-overlay.json'
    common = [sys.executable, str(ROOT / 'scripts/probe_biwn_delayed_marker_repair.py'),
              '--warm-frames', '0', '--frames', '24738', '--core', str(core),
              '--frame-controller-script', str(schedule), '--capture-audio', '--native-CPU-bridge', '--extended-CPU',
              '--CPU-candidate', str(ROOT / 'verification/loaded-scene-doorway-CPU-experimental-candidate.json'),
              '--native-CPU-candidate', str(ROOT / 'verification/CPU-IRQ-selection-native-CPU-experimental-candidate.json'),
              '--experimental-mainstage-overlay', str(overlay)]
    for frame in [600, 15900, 23538, 23698, 24138, 24488, 24620, 24738]:
        common += ['--capture-frame', str(frame)]
    candidate = ['--source-CPU-IRQ-entry', '--regular-GPU-mode', 'C', '--renderer-bundles', '--renderer-overlays',
                 '--material-bundles', '--control-bundles', '--setup-bundles', '--native-GPU-bridge',
                 '--GPU-frame-only', '--native-GPU-candidate',
                 str(ROOT / 'verification/CPU-IRQ-selection-GPU-experimental-candidate.json'),
                 '--stop-on-GPU-original', '--native-DSP-owner', '--DSP-owner-kind', 'router', '--require-owned-DSP',
                 '--DSP-router-candidate', str(ROOT / 'verification/CPU-IRQ-selection-DSP-experimental-candidate.json')]
    commands = dict(reference=common + ['--mode', 'reference', '--output', str(out / 'reference')],
                    C=common + ['--mode', 'C', *candidate, '--output', str(out / 'C')])
    assert all('--restore-original-report' not in command and '--experimental-code-overlay' not in command
               for command in commands.values())
    pinned = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in [
        Path(__file__), ROOT / 'scripts/probe_biwn_delayed_marker_repair.py',
        ROOT / 'scripts/compare_biwn_frame_CPU_only.py',
        ROOT / 'scripts/biwn_CPU_IRQ_select_owner.py', ROOT / 'scripts/biwn_CPU_IRQ_owner.py',
        ROOT / 'projects/black-ice-white-noise/restoration/biwn_cpu_irq_select.c',
        ROOT / 'projects/black-ice-white-noise/restoration/biwn_cpu_irq_select.h',
        ROOT / 'verification/local-CPU-IRQ-selector-author-current.json',
        ROOT / 'verification/CPU-IRQ-selection-GPU-experimental-candidate.json',
        ROOT / 'verification/CPU-IRQ-selection-native-CPU-experimental-candidate.json',
        ROOT / 'verification/CPU-IRQ-selection-DSP-experimental-candidate.json', schedule, core, overlay]}
    for manifest_name in ['CPU-IRQ-selection-core-experimental-candidate.json',
                          'CPU-IRQ-bridge-experimental-candidate.json',
                          'CPU-IRQ-selection-GPU-experimental-candidate.json',
                          'CPU-IRQ-selection-native-CPU-experimental-candidate.json',
                          'CPU-IRQ-selection-DSP-experimental-candidate.json',
                          'local-CPU-IRQ-selector-author-current.json']:
        manifest_path = ROOT / 'verification' / manifest_name
        pinned[str(manifest_path)] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        manifest = json.loads(manifest_path.read_text())
        for field in ['library', 'kernel_library', 'CPU_library', 'cost_library']:
            if manifest.get(field):
                path = Path(manifest[field])
                pinned[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    state = dict(status='prepared', directory=str(out), pid=os.getpid(), frames=24738,
                 commands=commands, children={}, hashes=pinned, started_unix=time.time(),
                 scope='Two independent emulator starts; no original warmup, checkpoint restore, scene RAM transplant '
                       'or player relocation. Same recorded ordinary buttons for startup, merchant, two elevator floors and '
                       'outdoor exit. Existing18-byte marker-scan repair is applied once mainstage bytes are loaded. '
                       'Source CPU/GPU/DSP and IRQ selection/entry comparison pending. The repair is delayed until an exact unpatched merchant RAM+machine gate beforeframe23539. Original IRQ queue/line/ACK, host commit/prefetch/cycle charge, HLE/OP/devices remain.')

    def save():
        data = json.dumps(state, indent=2) + '\n'
        (out / 'protocol.json').write_text(data)
        (ROOT / 'verification/merchant-gated-outdoor-route-active.json').write_text(data)

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
        irq = json.loads((out / 'C/CPU-IRQ-owner-report.json').read_text())
        for field in ['selection', 'core']:
            assert irq[field]['Owned'] > 0 and irq[field]['Original'] == irq[field]['Rejected'] == 0
        gates = {}
        for phase in ['reference', 'C']:
            gate = json.loads((out / phase / 'pre-repair-merchant-gate.json').read_text())
            assert gate['before_frame'] == 23539 and gate['actual_RAM_sha256'] == gate['expected_RAM_sha256']
            assert gate['actual_machine_sha256'] == gate['expected_machine_sha256']
            assert gate['state_restored'] is False and gate['memory_injected'] is False
            gates[phase] = gate
        continuation = ROOT / 'runs/world-controls-20261017T083710.579729Z/reference'
        def file_sha(path):
            with path.open('rb') as stream:
                return hashlib.file_digest(stream, 'sha256').hexdigest()
        continuation_checks = {name: file_sha(out / 'reference' / name) == file_sha(continuation / name)
                               for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin']}
        state['exact_unpatched_merchant_gate'] = gates
        state['known_checkpoint_continuation_final_state'] = dict(source=str(continuation), checks=continuation_checks)
        state['source_IRQ'] = irq
        save()
        assert all(continuation_checks.values()), continuation_checks
        for name, digest in state['hashes'].items():
            assert file_sha(Path(name)) == digest, ('A pinned input changed during execution', name)
        state['remaining_providers'] = ['Original IRQ queue/device line', 'Original device ACK/vector resolution',
                                        'Host CPU commit/prefetch/cycle charge', 'Firmware HLE, object processor and devices']
        semantic_checks = {}
        for phase in ['reference', 'C']:
            folder = out / phase
            for frame, expected in [(23538, (2, 2, 314)), (23698, (2, 0, 312)), (24738, (1, 0, 312))]:
                raw = (folder / ('frame-' + str(frame) + '-RAM.bin')).read_bytes()
                got = tuple(int.from_bytes(raw[address:address + 2], 'big') for address in [0x49c60, 0x49c62, 0x49c64])
                semantic_checks[phase + '_frame' + str(frame)] = got == expected
        state['semantic_milestone_checks'] = semantic_checks
        save()
        assert all(semantic_checks.values()), semantic_checks
        state.update(status='terminal_exact_merchant_elevator_outdoor_CPU_GPU_DSP_IRQ_match',
                     comparison=str(out / 'comparison.json'), total_seconds=time.time() - state['started_unix'])
        save()
        (ROOT / 'verification/merchant-gated-outdoor-route-current.json').write_text(json.dumps(state, indent=2) + '\n')
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
