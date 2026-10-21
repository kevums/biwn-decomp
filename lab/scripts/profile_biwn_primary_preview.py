"""Sample a new isolated primary-preview replay and check exact output retention."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    proof = json.loads((ROOT / 'verification/primary-preview-throughput-current.json').read_text())
    assert proof['frames'] == 600 and all(proof['checks'].values())
    baseline = Path(proof['directory'])
    protocol = json.loads((baseline / 'protocol.json').read_text())
    command = next(row['command'][:] for row in protocol['commands'] if row['phase'] == 'C')
    assert '--no-instruction-trace' in command and '--live-window' not in command
    out = ROOT / 'runs' / ('primary-preview-profile-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    command[0] = sys.executable
    command[command.index('--output') + 1] = str(out / 'C')
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), baseline=str(baseline), command=command,
                 source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 scope='Statistical sample of a new isolated 600-frame source preview. No existing game process is attached/restarted. Sampling plus concurrent local inference excludes a clean throughput claim. All frame records and final artifacts must match the accepted baseline.')
    def save():
        text = json.dumps(state, indent=2) + '\n'
        (out / 'protocol.json').write_text(text)
        (ROOT / 'verification/primary-preview-profile-active.json').write_text(text)
    save(); print(out, flush=True)
    with (out / 'C.log').open('w') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        state.update(status='running_isolated_preview', child_pid=child.pid); save()
        deadline = time.monotonic() + 30
        while child.poll() is None and time.monotonic() < deadline:
            progress = out / 'C/progress.json'
            if progress.exists():
                try:
                    if json.loads(progress.read_text()).get('completed_frames', 0) >= 60:
                        break
                except json.JSONDecodeError:
                    pass
            time.sleep(0.1)
        if child.poll() is None:
            sample = ['/usr/bin/sample', str(child.pid), '2', '-file', str(out / 'sample.txt')]
            state.update(status='sampling', sample_command=sample); save()
            result = subprocess.run(sample, capture_output=True, text=True)
            (out / 'sample-command.log').write_text(result.stdout + '\n' + result.stderr)
            state['sample_exit_code'] = result.returncode
        else:
            state['sample_skipped'] = 'Child terminal before sample'
        state['child_exit_code'] = child.wait()
    save()
    assert state['child_exit_code'] == 0
    before = json.loads((baseline / 'C/report.json').read_text())
    after = json.loads((out / 'C/report.json').read_text())
    checks = dict(frames=before['frames'] == after['frames'], no_errors=not after['errors'],
                  source_CPU=before['owned_CPU_instructions'] == after['owned_CPU_instructions'] > 0,
                  no_original_or_rejected=after['original_CPU_instructions'] == after['rejected_CPU_instructions'] == 0,
                  no_instruction_trace=after['instruction_trace_recorded'] is False)
    for name in ['warm-RAM.bin', 'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']:
        checks[name] = (baseline / 'C' / name).read_bytes() == (out / 'C' / name).read_bytes()
    state['checks'] = checks
    assert all(checks.values()), checks
    state.update(status='terminal_sampled_primary_preview_matches_baseline', sampled=state.get('sample_exit_code') == 0,
                 native_window_FPS_verified=False, new_source_function=False, whole_game_complete=False)
    save()
    (ROOT / 'verification/primary-preview-profile-current.json').write_text(json.dumps(state, indent=2) + '\n')
    print(state['status'], flush=True)


if __name__ == '__main__':
    main()
