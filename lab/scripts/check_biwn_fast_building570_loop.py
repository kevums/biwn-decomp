"""Join checked building entry and exit into one uninterrupted preview loop."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(paths):
    h = hashlib.sha256()
    for path in paths:
        with path.open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                h.update(chunk)
    return h.hexdigest()


def main():
    recipe_path = ROOT / 'verification/outdoor-restoration-preview-recipe.json'
    recipe = json.loads(recipe_path.read_text())
    for name, expected in recipe['hashes'].items():
        assert digest([Path(name)]) == expected, name
    segments = [
        (ROOT / 'runs/north-building-comparison-20261017T100447.018770Z', 4000),
        (ROOT / 'runs/world-controls-20261017T102351.608281Z', 600),
    ]
    out = ROOT / 'runs' / ('fast-building570-loop-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    windows, offset = [], 0
    for folder, count in segments:
        source = json.loads((folder / 'input.json').read_text())
        for row in source['windows']:
            assert 1 <= row['start_frame'] < row['stop_frame'] <= count + 1
            windows.append(dict(row, start_frame=row['start_frame'] + offset, stop_frame=row['stop_frame'] + offset))
        offset += count
    assert offset == 4600
    input_path = out / 'input.json'
    input_path.write_text(json.dumps(dict(windows=windows), indent=2) + '\n')
    cpu = ROOT / 'verification/building570-exit-CPU-experimental-candidate.json'
    native = ROOT / 'verification/building570-fast-native-CPU-experimental-candidate.json'
    commands = {}
    checkpoint = ROOT / 'runs/world-controls-20261017T084146.540377Z/reference/report.json'
    import_path = ROOT / 'verification/GPU-register-checkpoint-current.json'
    imported = json.loads(import_path.read_text())
    assert imported['status'] == 'one_original_frame_cross_core_state_import_matches'
    assert imported['source_checkpoint'] == str(checkpoint)
    compatible_probe = Path(imported['directory']) / 'compatible_checkpoint_probe.py'
    assert digest([compatible_probe]) == imported['derivative_probe_sha256']
    assert digest([ROOT / 'scripts/probe_biwn_frame_CPU_owner.py']) == imported['parent_probe_sha256']
    # The prior preview is one original frame beyond this exact route seed.
    # Restore the full naturally reached state only at the beginning.
    for phase in ['reference', 'C']:
        command = list(recipe['candidate'])
        command[1] = str(compatible_probe)
        while '--capture-frame' in command:
            i = command.index('--capture-frame')
            del command[i:i + 2]
        for flag, value in [('--frames', '4600'), ('--frame-controller-script', str(input_path)),
                            ('--restore-original-report', str(checkpoint)),
                            ('--CPU-candidate', str(cpu)), ('--native-CPU-candidate', str(native)),
                            ('--mode', phase), ('--output', str(out / phase))]:
            command[command.index(flag) + 1] = value
        if phase == 'reference':
            # Reference uses original processors and the same observing CPU
            # bridge, with no source GPU/DSP owner or source opcode fallback.
            for flag in ['--regular-GPU-mode', '--native-GPU-candidate', '--DSP-owner-kind', '--DSP-router-candidate']:
                i = command.index(flag)
                del command[i:i + 2]
            for flag in ['--renderer-bundles', '--renderer-overlays', '--material-bundles', '--control-bundles',
                         '--setup-bundles', '--native-GPU-bridge', '--GPU-frame-only', '--stop-on-GPU-original',
                         '--native-DSP-owner', '--require-owned-DSP']:
                command.remove(flag)
        for frame in [1, 3268, 4000, 4159, 4600]:
            command += ['--capture-frame', str(frame)]
        commands[phase] = command
    pinned = set(Path(p) for p in recipe['hashes']) | {cpu, native, input_path, checkpoint, checkpoint.parent / 'final-RAM.bin', checkpoint.parent / 'final-serialized-state.bin', compatible_probe, import_path, Path(__file__).resolve()}
    for path in [cpu, native]:
        candidate = json.loads(path.read_text())
        pinned.add(Path(candidate['library']))
    hashes = {str(path): digest([path]) for path in pinned}
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), frames=4600,
                 commands=commands, hashes=hashes, segments=[dict(directory=str(p), frames=n) for p, n in segments],
                 initial_checkpoint=commands['C'][commands['C'].index('--restore-original-report') + 1],
                 explicit_core_import_proof=str(import_path),
                 scope='One4600frame continuation from the exact naturally reached outdoor checkpoint after200movement frames, one original frame before the prior O preview seed. Concatenated4000building570arrival and600exit input segments; no intermediate checkpoint restore, RAM transplant, player relocation or new code repair. Inherited18byte repair. Fast GPU backend plus two additional original CPU cases. Original IRQ/HLE/object processor/devices remain. Native window, physical audio, standalone/full-game and speed remain unverified.')

    def save():
        text = json.dumps(state, indent=2) + '\n'
        (out / 'protocol.json').write_text(text)
        (ROOT / 'verification/fast-building570-loop-active.json').write_text(text)

    save()
    print(out, flush=True)
    try:
        for phase, command in commands.items():
            with (out / (phase + '.log')).open('w') as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                state.update(status='running_' + phase, child_pid=child.pid)
                save()
                print(phase, child.pid, flush=True)
                code = child.wait()
            assert code == 0, (phase, code, out / (phase + '.log'))
        comparison = out / 'comparison.json'
        command = [sys.executable, str(ROOT / 'scripts/compare_biwn_frame_CPU_only.py'),
                   '--C-run', str(out / 'C'), '--reference', str(out / 'reference'),
                   '--expected-frames', '4600', '--original-checkpoint-report', state['initial_checkpoint'],
                   '--output', str(comparison)]
        with (out / 'comparison.log').open('w') as log:
            compared = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        result = json.loads(comparison.read_text())
        failed = [key for key, value in result['checks'].items() if not value]
        assert compared.returncode == 1 and failed == ['DSP_owned_positive'], failed
        assert result['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
        reports = {phase: json.loads((out / phase / 'report.json').read_text()) for phase in commands}
        # Independently require that joining the input files preserves each
        # previously checked segment's CPU, RAM and video at every frame.
        offset = 0
        segment_checks = {}
        for folder, count in segments:
            previous = json.loads((folder / 'reference/report.json').read_text())
            current = reports['reference']['frames'][offset:offset + count]
            segment_checks[folder.name + '_every_CPU_RAM_video'] = all(
                all(a[key] == b[key] for key in ['CPU', 'RAM', 'video'])
                for a, b in zip(current, previous['frames'], strict=True))
            offset += count
        assert all(segment_checks.values()), segment_checks
        for name in ['CPU-before-instructions.bin', 'retired-instruction-costs.bin', 'frontend-PCM.s16le']:
            segment_checks[name + '_matches_concatenated_originals'] = digest([out / 'reference' / name]) == digest([p / 'reference' / name for p, _ in segments])
        for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin']:
            segment_checks[name + '_matches_previous_exit'] = digest([out / 'reference' / name]) == digest([segments[-1][0] / 'reference' / name])
        assert all(segment_checks.values()), segment_checks
        raw = (out / 'C/final-RAM.bin').read_bytes()
        word = lambda a: int.from_bytes(raw[a:a + 2], 'big')
        assert (word(0x49c60), word(0x49c62), word(0x49c64)) == (1, 0, 570)
        for name, expected in hashes.items():
            assert digest([Path(name)]) == expected, name
        state.update(status='terminal_continuous_outdoor_building570_outdoor_source_match',
                     recorded_at=datetime.now(timezone.utc).isoformat(), comparison=str(comparison),
                     raw_combined_gate_passed=False, combined_gate_failed_checks=failed,
                     segment_checks=segment_checks, CPU_instructions=result['owned_CPU_instructions'],
                     GPU_counts=result['GPU_counts'], DSP_counts=result['DSP_counts'],
                     DSP_execution_verified=False, no_intermediate_restore=True, source_frames=4600,
                     final_scene_mode=1, final_retained_scene_index=570, native_window_verified=False,
                     default_preview_updated=False, whole_game_complete=False)
        save()
        (ROOT / 'verification/fast-building570-loop-current.json').write_text(json.dumps(state, indent=2) + '\n')
        print(state['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        save()
        raise


if __name__ == '__main__':
    main()
