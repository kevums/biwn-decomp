"""Strict proof for C CPU delegation with original GPU/DSP providers."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def same(left, right, name):
    a, b = (left / name).read_bytes(), (right / name).read_bytes()
    assert a == b, (name, str(left), str(right))
    return dict(bytes=len(a), sha256=hashlib.sha256(a).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-root', type=Path, required=True)
    parser.add_argument('--layout', choices=['simple','directions'], default='directions')
    args = parser.parse_args()
    folder = args.run_root.resolve()
    runs = {}
    directions = ['none'] if args.layout == 'simple' else sorted({row['direction'] for row in read(folder / 'commands.json')})
    if args.layout != 'simple':
        assert all(row['exit_code'] == 0 for row in read(folder / 'commands.json'))
    for direction in directions:
        paths = {mode:folder / (mode if args.layout == 'simple' else direction+'-'+mode)
                 for mode in ['reference','C','baseline']}
        native, owned = read(paths['reference'] / 'report.json'), read(paths['C'] / 'report.json')
        assert native['status'] == owned['status'] == 'completed_component_uncompared'
        assert not native['errors'] and not owned['errors']
        assert native['core_sha256'] == owned['core_sha256']
        assert native['warm_CPU'] == owned['warm_CPU'] and native['warm_original_frames'] == owned['warm_original_frames']
        assert native['requested_frames'] == owned['requested_frames'] == len(native['frames']) == len(owned['frames'])
        assert native['frames'] == owned['frames'] and native['audio'] == owned['audio'] and native['video'] == owned['video']
        assert owned['original_CPU_instructions'] == owned['rejected_CPU_instructions'] == 0
        assert native['owned_CPU_instructions'] == native['rejected_CPU_instructions'] == 0
        assert owned['owned_CPU_instructions'] == native['original_CPU_instructions'] == owned['CPU_before_instructions'] == native['CPU_before_instructions']
        if 'fixed_C_instruction_steps' in owned:
            assert owned['fixed_C_instruction_steps'] + owned['HLE_stub_RTS_count'] == owned['owned_CPU_instructions']
        files = {name:same(paths['reference'], paths['C'], name) for name in [
            'warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin',
            'final-RAM.bin','final-video.bin','final-serialized-state.bin']}
        observer_invariant = None
        if (paths['baseline'] / 'report.json').exists():
            baseline = read(paths['baseline'] / 'report.json')
            assert baseline['status'] == 'completed_component_uncompared'
            assert native['warm_CPU'] == baseline['warm_CPU'] and native['frames'] == baseline['frames']
            observer_invariant = {name:same(paths['reference'],paths['baseline'],name) for name in [
                'warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin']}
        runs[direction] = dict(frames=owned['requested_frames'], owned_CPU_instructions=owned['owned_CPU_instructions'],
                               fixed_C_instruction_steps=owned.get('fixed_C_instruction_steps'),
                               HLE_stub_RTS_count=owned['HLE_stub_RTS_count'], original_CPU_instructions=0,
                               frame_state_cost_pixel_and_serialized_machine_match=True,
                               artifacts=files, observer_invariant=observer_invariant,
                               source_paths={key:str(value) for key,value in paths.items()},
                               all_audio_samples_silent=owned['audio']['nonzero_samples']==0,
                               core=owned['core'], core_sha256=owned['core_sha256'], CPU_library=owned['CPU_library'])
    out = ROOT / 'verification/frame-CPU-owner-runtime' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    proof = dict(status='frame_scheduled_C_CPU_component_matches_original',directory=str(out),run_root=str(folder),runs=runs,
                 CPU_handoff_after_original_warm_frames=owned['warm_original_frames'],original_GPU_DSP_providers=True,
                 ordinary_core_frame_scheduler=True,new_training=False,coordinator_authored=True,whole_game_complete=False,
                 limits=['Owned CPU window only; warm startup, GPU/DSP and core IRQ/HLE remain original providers.',
                         'Four platform RTS aliases handled explicitly; fixed C instruction identities fenced against checked source bytes.',
                         'Existing queue resolver drops irrelevant snoop entries; retained prefetched instruction words reject with no fallback.',
                         'Full serialized machine equality is scoped to these runs, not physical accuracy, all paths or a standalone C game.'])
    (out / 'report.json').write_text(json.dumps(proof,indent=2)+'\n')
    current = ROOT / 'verification/frame-CPU-owner-runtime-current.json'
    previous = read(current) if current.exists() else None
    if not previous or max(run['frames'] for run in previous['runs'].values()) <= max(run['frames'] for run in runs.values()):
        current.write_text(json.dumps(proof,indent=2)+'\n')
    print(out,flush=True)


if __name__=='__main__':main()
