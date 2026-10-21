"""Measure bounded headless throughput without instruction-trace disk writes.

Includes startup/checkpoint loading, file checks, frame hashes and captures
in each wall time. This is not native-window FPS or sustained playability.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    recipe_path = ROOT / 'verification/interactive-preview-recipe.json'
    recipe = json.loads(recipe_path.read_text())
    assert recipe['initial_checkpoint_origin'] == 'verified_source_execution'
    for path, digest in recipe['hashes'].items():
        assert sha(path) == digest, path
    publication = json.loads((ROOT / 'verification/primary-source-preview-current.json').read_text())
    assert sha(recipe_path) == publication['recipe_sha256']
    mail = json.loads(Path(recipe['mail_roundtrip_proof']).read_text())
    original = next(row['command'][:] for row in mail['commands'] if row['phase'] == 'reference')
    source = recipe['candidate'][:]
    out = ROOT / 'runs' / ('primary-preview-throughput-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), frames=600, commands=[],
                 recipe=str(recipe_path), recipe_sha256=sha(recipe_path), native_window=False, instruction_trace=False,
                 scope=__doc__, whole_game_complete=False)
    def mark():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/primary-preview-throughput-active.json', state)
    mark()
    print(out, flush=True)
    try:
        for name, command in [('reference', original), ('C', source)]:
            command[0] = sys.executable
            command[command.index('--frames') + 1] = '600'
            command[command.index('--output') + 1] = str(out / name)
            command += ['--no-instruction-trace']
            row = dict(phase=name, command=command)
            state['commands'].append(row)
            with (out / (name + '.log')).open('w') as log:
                start = time.monotonic()
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                row['pid'] = child.pid
                state.update(status='running_' + name, child_pid=child.pid)
                mark()
                print(name, 'PID', child.pid, flush=True)
                code = child.wait()
                row.update(exit_code=code, wall_seconds=time.monotonic() - start)
            mark()
            assert code == 0, (name, out / (name + '.log'))
        original_report = json.loads((out / 'reference/report.json').read_text())
        source_report = json.loads((out / 'C/report.json').read_text())
        checks = dict(complete_frames=len(source_report['frames']) == len(original_report['frames']) == 600,
                      all_frame_CPU_RAM_video_audio=source_report['frames'] == original_report['frames'],
                      no_errors=not source_report['errors'] and not original_report['errors'],
                      no_original_or_rejected_CPU=source_report['original_CPU_instructions'] == source_report['rejected_CPU_instructions'] == 0,
                      source_CPU_positive=source_report['owned_CPU_instructions'] > 0,
                      no_instruction_trace=source_report['instruction_trace_recorded'] is original_report['instruction_trace_recorded'] is False)
        hashes = {}
        for name in ['warm-RAM.bin', 'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']:
            hashes[name] = [sha(out / phase / name) for phase in ['reference', 'C']]
            checks[name] = hashes[name][0] == hashes[name][1]
        gpu = json.loads(Path(source_report['regular_GPU_report']).read_text())
        irq = json.loads(Path(source_report['CPU_IRQ_report']).read_text())
        checks['GPU_source_positive_no_fallback'] = gpu['counts']['Owned'] > 0 and gpu['counts']['Original'] == gpu['counts']['Rejected'] == 0 and not gpu['errors']
        checks['IRQ_selection_source_no_fallback'] = irq['selection']['Owned'] > 0 and irq['selection']['Original'] == irq['selection']['Rejected'] == 0
        checks['IRQ_entry_source_no_fallback'] = irq['core']['Owned'] > 0 and irq['core']['Original'] == irq['core']['Rejected'] == 0
        assert all(checks.values()), checks
        result = dict(status='bounded_headless_primary_profile_throughput_and_frame_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                      directory=str(out), frames=600, checks=checks, sha256=hashes, CPU_instructions=source_report['owned_CPU_instructions'],
                      phases=[dict(phase=row['phase'], wall_seconds=row['wall_seconds'], frames_per_total_wall_second=600 / row['wall_seconds']) for row in state['commands']],
                      source_checkpoint_origin=source_report['restored_source_checkpoint']['origin'], inherited_repair_bytes=0, post_restore_repair_bytes=56,
                      native_window_FPS_verified=False, physical_input_audio_verified=False, instruction_level_trace_compared=False,
                      scope='One600frame ordinary-input Deck/mail/world replay on the current64GB Mac. No instruction trace writes; full per-frame CPU/RAM/video/audio and final machine match. Total subprocess wall times include checks/load/restore/captures/hashing/cleanup. Throughput is not native-window FPS, frame pacing, arbitrary gameplay or future256GB Mac Studio performance.', whole_game_complete=False)
        save(out / 'verdict.json', result)
        save(ROOT / 'verification/primary-preview-throughput-current.json', result)
        state.update(status='terminal_benchmark_complete', proof=str(out / 'verdict.json'))
        mark()
        print(json.dumps(result, indent=2), flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    main()
