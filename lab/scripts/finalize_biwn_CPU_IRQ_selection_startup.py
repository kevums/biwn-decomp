"""Correct the declared-overlay comparison invocation, reusing completed outputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    active = ROOT / 'verification/CPU-IRQ-selection-startup-active.json'
    report = json.loads(active.read_text())
    out = Path(report['directory'])
    previous = out / 'source-comparison.json'
    old = json.loads(previous.read_text())
    assert [k for k, v in old['checks'].items() if not v] == ['expected_experimental_overlay']
    assert [k for k, v in report['checks'].items() if not v] == ['combined_CPU_GPU_DSP_gate']
    assert all(row['exit_code'] == 0 for row in report['children'].values())
    backup = out / 'comparison-invocation-before-overlay-option'
    backup.mkdir()
    for path in [previous, out / 'comparison.log', out / 'protocol.json']:
        shutil.copy2(path, backup / path.name)
    phases = ['parent_original', 'new_original', 'new_C']
    parsed = {phase: json.loads((out / phase / 'report.json').read_text()) for phase in phases}
    baseline = parsed['parent_original']
    for phase, observed in parsed.items():
        assert len(observed['frames']) == 600 and not observed['errors']
        assert observed['frames'] == baseline['frames']
        for name, digest in report['file_hashes'][phase].items():
            assert sha(out / phase / name) == digest == report['file_hashes']['parent_original'][name]
    command = report['commands']['new_C']
    overlay = command[command.index('--experimental-mainstage-overlay') + 1]
    with (out / 'comparison.log').open('w') as stream:
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/compare_biwn_frame_CPU_only.py'),
                                 '--C-run', str(out / 'new_C'), '--reference', str(out / 'new_original'),
                                 '--expected-frames', '600', '--experimental-code-overlay', overlay,
                                 '--output', str(previous)], stdout=stream, stderr=subprocess.STDOUT)
    corrected = json.loads(previous.read_text())
    assert result.returncode == 0 and all(corrected['checks'].values())
    report['checks']['combined_CPU_GPU_DSP_gate'] = True
    assert all(report['checks'].values())
    report.pop('error', None)
    report.update(status='terminal_three_lane_startup_processors_and_IRQ_selection_entry_match',
                  completed_at=datetime.now(timezone.utc).isoformat(), whole_game_complete=False,
                  original_probe_unchanged=sha(ROOT / 'scripts/probe_biwn_frame_CPU_owner.py') == report['original_probe_sha256'],
                  comparison_invocation_repair=dict(backup=str(backup), declared_overlay=overlay,
                                                    reason='Initial checker invocation omitted --experimental-code-overlay although all executions recorded the same byte-checked repair. Corrected declared expectation; no gate disabled and no execution rerun.'),
                  CPU_instructions=corrected['owned_CPU_instructions'], GPU_counts=corrected['GPU_counts'], DSP_counts=corrected['DSP_counts'],
                  remaining_providers=['Original IRQ queue/device line', 'Original device ACK/vector resolution',
                                       'Host CPU commit/prefetch and pinned cycle charge', 'Firmware HLE, object processor and devices'],
                  default_runtime_changed=False, native_window_verified=False, physical_audio_verified=False)
    for path in [out / 'protocol.json', active, ROOT / 'verification/CPU-IRQ-selection-startup-current.json']:
        path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'CPU_instructions', 'GPU_counts', 'DSP_counts', 'source_IRQ']}), flush=True)


if __name__ == '__main__':
    main()
