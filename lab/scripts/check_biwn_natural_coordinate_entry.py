"""Activate the existing coordinate item through ordinary pads in real frames.

Starts from the checked source-produced outdoor machine, inheriting its
declared18byte repair. No item grant, player/scene transplant or new patch.
The frame runtime remains instruction-compatible C, separate from the new
readable semantic coordinate-controls module.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from biwn_verified_source_checkpoint import verify_source_checkpoint

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=['cancel', 'confirm', 'edit'], default='cancel')
    args = parser.parse_args()
    runtime = json.loads((ROOT / 'verification/unified-restore-runtime-candidate.json').read_text())
    probe = json.loads((ROOT / 'verification/source-checkpoint-probe-candidate.json').read_text())
    source_proof = ROOT / 'verification/merchant-gated-full-route-verdict-current.json'
    cold = json.loads(source_proof.read_text())
    checkpoint = Path(cold['directory']) / 'C/report.json'
    origin = verify_source_checkpoint(checkpoint, source_proof, runtime['core'])
    for table in [runtime['artifacts_sha256'], runtime['inputs_sha256'], probe['artifacts_sha256']]:
        for path, digest in table.items(): assert sha(path) == digest, path
    initial = (checkpoint.parent / 'final-RAM.bin').read_bytes()
    word = lambda raw, a: int.from_bytes(raw[a:a + 2], 'big')
    long = lambda raw, a: int.from_bytes(raw[a:a + 4], 'big')
    assert word(initial, 0x49c60) == 1
    assert word(initial, 0x49d2c + 3 * 2) == 0x46
    out = ROOT / 'runs' / ('natural-coordinate-' + args.case + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir(); print(out, flush=True)
    windows = [dict(start_frame=1, stop_frame=9, buttons=['4']),
               dict(start_frame=30, stop_frame=39, buttons=['B', 'C'])]
    if args.case == 'cancel':
        windows.append(dict(start_frame=250, stop_frame=260, buttons=['C']))
        frames = 400
        captures = [1, 30, 60, 150, 255, frames]
    else:
        # Use the nearest cell around the starting position. The game's own
        # coordinate feature, rather than a host RAM write, computes/reloads it.
        x, z = long(initial, 0x49c50) >> 6, long(initial, 0x49c56) >> 6
        assert 32 <= x <= 966 and 32 <= z <= 719
        text = f'{x:03}{z:03}'
        actions = list(text)
        if args.case == 'edit':
            actions = list(text[:3]) + ['B', text[2]] + list(text[3:]) + ['B', text[-1]]
        spacing = 80 if args.case == 'edit' else 120
        for i, button in enumerate(actions):
            frame = 200 + i * spacing
            windows.append(dict(start_frame=frame, stop_frame=frame + 8, buttons=[button]))
        accept_frame = 1080 if args.case == 'edit' else 950
        windows.append(dict(start_frame=accept_frame, stop_frame=accept_frame + 8, buttons=['A']))
        frames = 1500
        captures = [1, 60, 350, 600, 900, 960, 1200, frames]
    assert len(captures) <= 8
    input_path = out / 'ordinary-input.json'; save(input_path, dict(windows=windows))
    common = [sys.executable, probe['probe'], '--warm-frames', '0', '--frames', str(frames),
              '--core', runtime['core'], '--restore-source-report', str(checkpoint),
              '--source-checkpoint-proof', str(source_proof), '--capture-audio', '--native-CPU-bridge',
              '--extended-CPU', '--CPU-candidate', runtime['CPU_candidate'],
              '--native-CPU-candidate', runtime['native_CPU_candidate'], '--frame-controller-script', str(input_path)]
    for frame in captures: common += ['--capture-frame', str(frame)]
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), case=args.case, frames=frames,
        source_checkpoint=origin, commands=[], controller_windows=windows,
        selected_inventory_position=4, observed_item_id='0x46', inherited_repair_bytes=18,
        new_program_repair=False, item_granted=False, player_RAM_relocated=False, scene_RAM_transplanted=False,
        initial_position=dict(X=long(initial, 0x49c50), Z=long(initial, 0x49c56)),
        readable_high_level_module_installed_in_live_frames=False, whole_game_complete=False,
        runtime=runtime, probe=probe, source_script_sha256=sha(__file__))
    shutil.copy2(__file__, out / Path(__file__).name)
    def mark():
        save(out / 'protocol.json', state)
        save(ROOT / ('verification/natural-coordinate-' + args.case + '-active.json'), state)
    def run(phase, command):
        row = dict(phase=phase, command=command); state['commands'].append(row)
        with (out / (phase + '.log')).open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                env={**os.environ, 'BIWN_LIVE_ATTACK_COUNTERS': str(out / (phase + '-attack-counts.txt'))})
            row['pid'] = child.pid; state.update(status='running_' + phase, child_pid=child.pid); mark()
            print(phase, 'PID', child.pid, flush=True)
            row['exit_code'] = child.wait()
        mark()
        return row['exit_code']
    mark()
    try:
        assert run('reference', common + ['--mode', 'reference', '--output', str(out / 'reference')]) == 0
        ref = json.loads((out / 'reference/report.json').read_text())
        trace_path = out / 'reference/CPU-before-instructions.bin'
        dtype = np.dtype({'names': ['pc'], 'formats': ['>u4'], 'offsets': [64], 'itemsize': 78})
        records = np.memmap(trace_path, mode='r', dtype=dtype)
        pcs, hits = np.unique(records['pc'], return_counts=True)
        counts = dict(zip(map(int, pcs), map(int, hits)))
        watched = {hex(pc): counts.get(pc, 0) for pc in [0x191f4, 0x18e92, 0x1b718, 0x12620, 0xe4c0, 0x20e8c, 0xdf60, 0xdf22, 0x20f78, 0xdf3e]}
        position_stores = []
        if args.case != 'cancel':
            typed = np.memmap(trace_path, mode='r', dtype=np.dtype({'names':['D6','pc'], 'formats':['>u4','>u4'], 'offsets':[24,64], 'itemsize':78}))
            for pc, target in [(0x18f80, (x << 6) | 32), (0x18f90, (z << 6) | 32)]:
                indices = np.flatnonzero(typed['pc'] == pc)
                position_stores.append(dict(PC=hex(pc), values=[int(typed[i]['D6']) for i in indices], expected=target))
        final_ref = (out / 'reference/final-RAM.bin').read_bytes()
        state.update(original_observed_entries=watched, original_final_state=dict(mode=word(final_ref, 0x49c60),
            scene=word(final_ref, 0x49c64), selected=word(final_ref, 0x49d54),
            X=long(final_ref, 0x49c50), Z=long(final_ref, 0x49c56)),
            original_trace_sha256=sha(trace_path))
        state['original_coordinate_position_stores'] = position_stores
        mark()
        assert watched['0x18e92'] > 0, 'Ordinary controls did not enter coordinate code; inspect reference captures'
        if args.case != 'cancel':
            assert all(s['values'] == [s['expected']] for s in position_stores), position_stores
        assert run('C', common + ['--mode', 'C', '--source-CPU-IRQ-entry', '--regular-GPU-mode', 'C',
            '--renderer-bundles', '--renderer-overlays', '--material-bundles', '--control-bundles', '--setup-bundles',
            '--native-GPU-bridge', '--GPU-frame-only', '--native-GPU-candidate', runtime['GPU_candidate'],
            '--stop-on-GPU-original', '--native-DSP-owner', '--DSP-owner-kind', 'router', '--require-owned-DSP',
            '--DSP-router-candidate', runtime['DSP_candidate'], '--output', str(out / 'C')]) == 0
        compare = [sys.executable, probe['comparator'], '--C-run', str(out / 'C'), '--reference', str(out / 'reference'),
            '--expected-frames', str(frames), '--source-checkpoint-report', str(checkpoint),
            '--source-checkpoint-proof', str(source_proof), '--output', str(out / 'comparison.json')]
        code = run('comparison', compare)
        comparison = json.loads((out / 'comparison.json').read_text())
        failed = [key for key, value in comparison['checks'].items() if not value]
        assert (code == 0 and not failed) or (code == 1 and failed == ['DSP_owned_positive'] and comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)), failed
        final = (out / 'C/final-RAM.bin').read_bytes()
        assert word(final, 0x49d54) == 3 and word(final, 0x49c60) == 1
        if args.case == 'cancel':
            assert long(final, 0x49c50) == state['initial_position']['X'] and long(final, 0x49c56) == state['initial_position']['Z']
        else:
            assert (long(final, 0x49c50), long(final, 0x49c56)) == ((x << 6) | 32, (z << 6) | 32)
        report = dict(status='natural_coordinate_' + args.case + '_source_runtime_match', recorded_at=datetime.now(timezone.utc).isoformat(),
            directory=str(out), frames=frames, comparison=str(out / 'comparison.json'), CPU_instructions=comparison['owned_CPU_instructions'],
            GPU_counts=comparison['GPU_counts'], DSP_counts=comparison['DSP_counts'], raw_failed_checks=failed,
            source_checkpoint=origin, observed_original_entry_counts=watched, ordinary_controller_windows=windows,
            final_state=state['original_final_state'], inherited_repair_bytes=18, new_game_byte_repair=False,
            observed_coordinate_position_stores=position_stores,
            item_granted=False, host_player_relocation=False, scene_RAM_transplant=False,
            readable_high_level_coordinate_module_in_frame_runtime=False, whole_game_complete=False,
            scope='Real frames from the verified source outdoor machine, existing inventory position4/item46, ordinary selection/activation/keypad/cancel or confirm inputs. Full instruction-compatible source CPU/cycle/frame/PCM/final-machine comparison. Inherited18byte earlier repair, no new patch/item grant/RAM relocation. This traverses the original coordinate routine and its static C instruction bodies; the separate readable semantic API is not installed in live frames. Not a new cold start, physical keyboard or whole-game/standalone proof.')
        save(out / 'verdict.json', report)
        save(ROOT / ('verification/natural-coordinate-' + args.case + '-current.json'), report)
        state.update(status='terminal_natural_coordinate_match', proof=str(out / 'verdict.json')); mark()
        print(report['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error)); mark(); raise


if __name__ == '__main__':
    main()
