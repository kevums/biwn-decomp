"""Compare fresh DSP ownership runs with untouched same-core originals."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--C-run', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-frames', type=int, required=True)
    args = parser.parse_args()
    rebuilt, original = args.C_run.resolve(), args.reference.resolve()
    c = json.loads((rebuilt/'report.json').read_text())
    o = json.loads((original/'report.json').read_text())
    dsp = json.loads((rebuilt/'DSP-owner-report.json').read_text())
    checks = {k: c[k] == o[k] for k in ['core_sha256', 'disc_sha256', 'requested_options',
              'boot_strategy', 'frames', 'audio', 'final_RAM_sha256',
              'final_serialized_state_sha256']}
    checks.update(complete_frames=len(c['frames']) == len(o['frames']) == c['executed_frames'] ==
                  o['executed_frames'] == args.expected_frames,
                  video_layout=all(c['video'][k] == o['video'][k] for k in ['width', 'height', 'pitch']),
                  original_has_no_source_owner=not o.get('source_DSP_execution'),
                  DSP_original_zero=dsp['core_counts']['Original'] == 0,
                  DSP_rejected_zero=dsp['core_counts']['Rejected'] == 0,
                  DSP_uncovered_zero=dsp['uncovered'] == 0,
                  DSP_errors_zero=dsp['errors'] == 0,
                  DSP_owned_positive=dsp['owned'] == dsp['core_counts']['Owned'] > 0)
    hashes = {}
    for name in ['RAM-final.bin', 'GPU-final.bin', 'state-final.bin', 'frontend-PCM.s16le']:
        values = []
        for folder in [rebuilt, original]:
            with (folder/name).open('rb') as stream:
                values.append(hashlib.file_digest(stream, 'sha256').hexdigest())
        hashes[name] = values
        checks[name] = values[0] == values[1]
    result = dict(status='fresh_DSP_comparison_pass' if all(checks.values()) else 'fresh_DSP_comparison_fail',
                  recorded_at=datetime.now(timezone.utc).isoformat(), C_run=str(rebuilt),
                  reference=str(original), frames=len(c['frames']), DSP_report=dsp,
                  DSP_scope=c.get('source_DSP_execution'), checks=checks, sha256=hashes,
                  whole_game_complete=False, full_music_playback_verified=False,
                  limits=['Declared DSP window only; original CPU/GPU/hardware/IRQ/HLE providers.',
                          'Recorded frame fields and final RAM/GPU/machine/PCM; no instruction state trace.',
                          'Silent PCM cannot establish audible music quality or physical timing.'])
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status', 'frames', 'checks']}))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == '__main__':
    main()
