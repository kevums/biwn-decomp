"""Finish one already-running source job after its exact process ends.

This is a one-shot compute-job dependency, not a recurring monitor. It never
restarts a source run and never marks the overall project complete.
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


def source_liveness(pid, directory):
    """Unknown observations keep waiting; only actual absence/end is terminal."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False, 'process_handle_missing'
    except (PermissionError, OSError):
        return True, 'liveness_unknown_retry_same_handle'
    try:
        process = subprocess.run(['ps', '-p', str(pid), '-o', 'stat=,args='], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return True, 'process_handle_present_observation_failed_retry'
    text = process.stdout.strip()
    if process.returncode or not text:
        return True, 'process_handle_present_ps_transient_retry'
    if text.split()[0].startswith('Z'):
        return False, 'original_process_terminal_zombie'
    if str(directory / 'C') not in text:
        return False, 'pid_now_belongs_to_different_process'
    return True, 'same_source_process_confirmed'


def main():
    active = json.loads((ROOT / 'verification/unified-unmodified-merchant-active.json').read_text())
    source_pid, out = active['pid'], Path(active['directory'])
    finalizer = ROOT / 'scripts/finalize_biwn_unmodified_merchant_source.py'
    expected = hashlib.sha256(finalizer.read_bytes()).hexdigest()
    state = dict(status='waiting_for_same_source_process', watcher_pid=os.getpid(), source_pid=source_pid,
                 directory=str(out), finalizer=str(finalizer), finalizer_sha256=expected,
                 source_restarted=False, whole_game_complete=False)

    def save():
        state['observed_at'] = datetime.now(timezone.utc).isoformat()
        text = json.dumps(state, indent=2) + '\n'
        (out / 'finalization-watch.json').write_text(text)
        (ROOT / 'verification/unified-merchant-finalization-watch-current.json').write_text(text)

    save()
    while True:
        live, observation = source_liveness(source_pid, out)
        state['same_source_process_live'] = bool(live)
        state['liveness_observation'] = observation
        try:
            state['progress'] = json.loads((out / 'C/progress.json').read_text())
        except (OSError, ValueError):
            # A concurrent write/observation failure is not process termination.
            pass
        save()
        if not live:
            break
        time.sleep(20)
    if not (out / 'C/report.json').exists():
        state['status'] = 'terminal_source_process_ended_without_report'
        save()
        raise SystemExit(1)
    assert hashlib.sha256(finalizer.read_bytes()).hexdigest() == expected, 'Finalizer changed after dispatch; do not silently run another verifier'
    state['status'] = 'running_terminal_comparison'
    save()
    with (out / 'finalization.log').open('w') as log:
        code = subprocess.run([sys.executable, str(finalizer)], stdout=log, stderr=subprocess.STDOUT).returncode
    state.update(status='terminal_comparison_pass' if code == 0 else 'terminal_comparison_failed',
                 finalizer_exit_code=code, finalization_log=str(out / 'finalization.log'))
    save()
    raise SystemExit(code)


if __name__ == '__main__':
    main()
