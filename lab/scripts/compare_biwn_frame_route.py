"""Compare completed C and original frame runs without changing either.

This proves only the supplied route and configured emulator, not the game.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--C-run', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rebuilt, original = args.C_run.resolve(), args.reference.resolve()
    c = json.loads((rebuilt/'report.json').read_text())
    o = json.loads((original/'report.json').read_text())
    gpu = json.loads(Path(c['regular_GPU_report']).read_text())
    op = json.loads(Path(c['OP_GPU_report']).read_text())
    original_op = json.loads(Path(o['OP_GPU_report']).read_text())
    checks = {
        'processor_modes': c['mode'] == 'C' and o['mode'] == 'reference' and op['mode'] == 'C',
        'checkpoint_identity': c.get('restored_original_checkpoint') == o.get('restored_original_checkpoint'),
        'core_sha256': c['core_sha256'] == o['core_sha256'],
        'warm_frames': c['warm_original_frames'] == o['warm_original_frames'],
        'controller_script_sha256': c.get('frame_controller_script_sha256') == o.get('frame_controller_script_sha256'),
        'complete_requested_frames': len(c['frames']) == c['requested_frames'] == len(o['frames']) == o['requested_frames'],
        'all_frame_CPU_RAM_pixels_audio': c['frames'] == o['frames'],
        'no_errors': not c['errors'] and not o['errors'] and not gpu['errors'] and not op['errors'],
        'no_original_CPU': c['original_CPU_instructions'] == 0,
        'no_rejected_CPU': c['rejected_CPU_instructions'] == 0,
        'all_reference_CPU_owned': c['owned_CPU_instructions'] == o['original_CPU_instructions'],
        'no_original_regular_GPU': gpu['counts']['Original'] == 0,
        'no_rejected_regular_GPU': gpu['counts']['Rejected'] == 0,
        'OP_all_reference_calls_owned': len(op['records']) == len(original_op['records']) == op['calls'] == original_op['calls'] and all(
            item.get('original_opcode_delta') == 0 and item.get('C_status') == 0 for item in op['records']),
        'OP_no_pending': not op['pending'],
    }
    hashes = {}
    for name in ['CPU-before-instructions.bin', 'retired-instruction-costs.bin',
                 'warm-RAM.bin', 'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin']:
        hashes[name] = [digest(rebuilt/name), digest(original/name)]
        checks[name] = hashes[name][0] == hashes[name][1]
    files = sorted(p.name for p in (original/'OP-GPU-slices').glob('*.bin'))
    rebuilt_files = sorted(p.name for p in (rebuilt/'OP-GPU-slices').glob('*.bin'))
    checks['OP_file_inventory'] = files == rebuilt_files and len(files) == 2*original_op['calls']
    mismatches = [name for name in files if not (rebuilt/'OP-GPU-slices'/name).is_file()
                  or digest(rebuilt/'OP-GPU-slices'/name) != digest(original/'OP-GPU-slices'/name)]
    checks['OP_raw_boundaries'] = not mismatches
    dsp=None
    if c.get('DSP_report'):
        dsp=json.loads(Path(c['DSP_report']).read_text())
        checks['DSP_owned_without_originals']=dsp['core_counts']['Owned']>0 and dsp['core_counts']['Original']==0
        checks['DSP_no_rejections']=dsp['core_counts']['Rejected']==0 and dsp['errors']==0
    if c.get('PCM_capture')or o.get('PCM_capture'):
        checks['both_PCM_captured']=bool(c.get('PCM_capture')and o.get('PCM_capture'))
        if checks['both_PCM_captured']:
            hashes['frontend_PCM']=[digest(Path(c['PCM_capture'])),digest(Path(o['PCM_capture']))]
            checks['frontend_PCM_byte_exact']=hashes['frontend_PCM'][0]==hashes['frontend_PCM'][1]
    result = {'status': 'route_comparison_pass' if all(checks.values()) else 'route_comparison_fail',
              'recorded_at': datetime.now(timezone.utc).isoformat(),
              'C_run': str(rebuilt), 'reference': str(original),
              'frames': len(c['frames']), 'CPU_owned_instructions': c['owned_CPU_instructions'],
              'GPU_counts': gpu['counts'], 'OP_report': op, 'DSP_report':dsp,
              'checks': checks, 'sha256': hashes, 'OP_files_compared': len(files),
              'OP_mismatches': mismatches, 'whole_game_complete': False,
              'limits': ['Fixed controller route and pinned emulator configuration only.',
                         'Original startup/checkpoint, IRQ, firmware HLE and devices remain providers; DSP ownership is reported explicitly.',
                         'Long-run GPU instruction hashes omitted; CPU/cost/frame/OP/final machine comparisons.']}
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['status', 'frames', 'CPU_owned_instructions', 'GPU_counts', 'checks']}), flush=True)
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == '__main__':
    main()
