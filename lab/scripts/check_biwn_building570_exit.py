"""Replay the original-discovered exit using ordinary inputs and source CPU/GPU."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--CPU-candidate', type=Path, default=ROOT / 'verification/building570-exit-CPU-experimental-candidate.json')
    parser.add_argument('--native-CPU-candidate', type=Path, default=ROOT / 'verification/building570-exit-native-CPU-experimental-candidate.json')
    parser.add_argument('--reuse-reference', type=Path)
    args = parser.parse_args()
    planning = json.loads((ROOT / 'verification/building570-exit-plan-current.json').read_text())
    assert planning['status'] == 'terminal_reference_exit_complete'
    discovery = Path(planning['directory']) / 'reference'
    command = [sys.executable, str(ROOT / 'scripts/run_biwn_world_controls.py'),
               '--checkpoint', planning['source_checkpoint'], '--frames', '600',
               '--input-script', str(discovery / 'navigation-input.json'),
               '--CPU-candidate', str(args.CPU_candidate.resolve()),
               '--native-CPU-candidate', str(args.native_CPU_candidate.resolve()),
               '--GPU-candidate', str(ROOT / 'verification/C-space-mail-shared-GPU-experimental-candidate.json'),
               '--capture-frame', '1', '--capture-frame', '159', '--capture-frame', '300', '--capture-frame', '600']
    if args.reuse_reference:
        command += ['--reuse-reference', str(args.reuse_reference.resolve())]
    subprocess.run(command, check=True)
    completed = json.loads((ROOT / 'verification/world-controls-current.json').read_text())
    assert completed['status'] in ['terminal_world_controls_match', 'terminal_CPU_GPU_controls_match_DSP_inactive']
    out = Path(completed['directory'])
    assert '--checkpoint' in command and planning['source_checkpoint'] in completed['commands'][0]['command']
    fixed = json.loads((out / 'reference/report.json').read_text())
    adaptive = json.loads((discovery / 'report.json').read_text())
    assert fixed['frames'] == adaptive['frames']
    matches = {name: sha(out / 'reference' / name) == sha(discovery / name)
               for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']}
    assert all(matches.values()), matches
    raw = (out / 'C/final-RAM.bin').read_bytes()
    get = lambda address, width=2: int.from_bytes(raw[address:address + width], 'big')
    state = dict(mode=get(0x49c60), floor=get(0x49c62), retained_scene_index=get(0x49c64), X=get(0x49c50, 4), Z=get(0x49c56, 4))
    assert state == dict(mode=1, floor=0, retained_scene_index=570, X=11492, Z=43455)
    comparison = json.loads((out / 'comparison.json').read_text())
    gpu = json.loads((out / 'C/regular-GPU-bundles/report.json').read_text())
    proof = dict(status='ordinary_controller_scene570_exit_to_outdoor_original_source_match',
                 recorded_at=datetime.now(timezone.utc).isoformat(), directory=str(out), frames=600,
                 CPU_instructions=comparison['owned_CPU_instructions'], GPU_counts=comparison['GPU_counts'],
                 GPU_source_instructions=gpu['C_source_instructions'], GPU_counter_units='Callback bundles, including existing delayed pairs.',
                 DSP_counts=comparison['DSP_counts'], combined_gate_failed_checks=[k for k, v in comparison['checks'].items() if not v],
                 comparison=str(out / 'comparison.json'), ordinary_controller_exit_verified=True,
                 final_state=state, planning_reference_reproduced_exactly=True, planning_matches=matches,
                 source_checkpoint=planning['source_checkpoint'], source_boundary=planning['source_boundary'],
                 source_RAM_sha256=sha(out / 'reference/warm-RAM.bin'), controller_plan=planning['plan'],
                 scene_RAM_transplant=False, player_relocation=False, new_code_overlay=False,
                 native_keyboard_verified=False, physical_audio_verified=False, whole_game_complete=False,
                 scope='Exact source-matched indoor570 checkpoint, ordinary buttons exit through direction1/key13/floor0. Inherited18byte repair only. All CPUstates/costs, frameRAM/video/PCM and finalmachine match original. Fixed input reproduces the independent adaptive discovery. Original IRQ/HLE/OP/devices remain. DSP/audio scope is only the observed counters/gates; native window and standalone execution are unverified.')
    assert proof['source_RAM_sha256'] == planning['source_RAM_sha256']
    unit_path = ROOT / 'verification/building570-exit-new-CPU-cases-current.json'
    unit = json.loads(unit_path.read_text())
    candidate = json.loads(args.CPU_candidate.read_text())
    if candidate['library'] == unit['candidate'] and candidate['source_sha256'] == unit['source_sha256']:
        import numpy as np
        trace = out / 'C/CPU-before-instructions.bin'
        assert trace.stat().st_size % 78 == 0
        rows = np.memmap(trace, mode='r', dtype=np.dtype({'names': ['pc'], 'formats': ['>u4'], 'offsets': [64], 'itemsize': 78}))
        proof['new_source_instruction_hits'] = {item['PC']: int(np.count_nonzero(rows['pc'] == int(item['PC'], 16))) for item in unit['instructions']}
        assert all(proof['new_source_instruction_hits'].values())
        proof['new_instruction_native_proof'] = str(unit_path)
        proof['implementation_authorship'] = 'Coordinator generated the2original instruction cases; separate640native CPU/RAM/cycle fixtures and this600frame original/source replay. No new local-model code or weights.'
    for path in [out / 'scene570-exit-proof.json', ROOT / 'verification/building570-exit-route-current.json']:
        path.write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
