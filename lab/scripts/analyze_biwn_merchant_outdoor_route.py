"""Audit an original/C elevator-to-outdoor continuation without a scene transplant."""
import argparse, collections, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sha = lambda raw: hashlib.sha256(raw).hexdigest()
get = lambda raw, address, width=4: int.from_bytes(raw[address:address + width], 'big')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    folder = args.run.resolve()
    protocol = json.loads((folder / 'protocol.json').read_text())
    comparison = json.loads((folder / 'comparison.json').read_text())
    reference = json.loads((folder / 'reference/report.json').read_text())
    rebuilt = json.loads((folder / 'C/report.json').read_text())
    failed = [key for key, value in comparison['checks'].items() if not value]
    assert failed in [[], ['DSP_owned_positive']], failed
    if failed:
        assert comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    assert not reference['errors'] and not rebuilt['errors']
    assert len(reference['frames']) == len(rebuilt['frames']) == 1200
    assert protocol['status'] in ['terminal_world_controls_match', 'terminal_CPU_GPU_controls_match_DSP_inactive']
    checkpoint = ROOT / 'runs/zero-warm-whole-merchant-reference/report.json'
    merchant_boot_path = ROOT / 'verification/zero-warm-whole-merchant-CPU-GPU-DSP-comparison.json'
    merchant_boot = json.loads(merchant_boot_path.read_text())
    assert merchant_boot['status'] == 'CPU_GPU_DSP_frame_comparison_pass' and all(merchant_boot['checks'].values())
    assert merchant_boot['reference'] == str(checkpoint.parent) and merchant_boot['original_warm_frames'] == 0
    for run in [reference, rebuilt]:
        assert run['restored_original_checkpoint']['report'] == str(checkpoint)
        assert run['restored_original_checkpoint']['exact_machine_and_RAM_before_execution'] is True
        overlay = run['experimental_code_overlay']
        assert len(overlay['patches']) == 1 and overlay['patches'][0]['address'] == '0x1b0ee'
    original_start = (checkpoint.parent / 'final-RAM.bin').read_bytes()
    initial = (folder / 'C/warm-RAM.bin').read_bytes()
    expected = bytearray(original_start)
    patch = rebuilt['experimental_code_overlay']['patches'][0]
    address = int(patch['address'], 16)
    old, new = bytes.fromhex(patch['original']), bytes.fromhex(patch['replacement'])
    assert len(old) == len(new) == 18 and expected[address:address + len(old)] == old
    expected[address:address + len(new)] = new
    assert initial == bytes(expected) == (folder / 'reference/warm-RAM.bin').read_bytes()
    final = (folder / 'C/final-RAM.bin').read_bytes()
    assert get(initial, 0x49c60, 2) == 2 and get(initial, 0x49c62, 2) == 2
    assert get(final, 0x49c60, 2) == 1 and get(final, 0x49c62, 2) == 0

    # The two planning runs must compose exactly into the fixed original replay.
    prefix = ROOT / 'runs/merchant-exit-discovery-20261017T083450.542060Z/reference'
    navigation = ROOT / 'runs/merchant-exit-navigation-20261017T083642.999290Z/reference'
    first = json.loads((prefix / 'report.json').read_text())
    second = json.loads((navigation / 'report.json').read_text())
    assert len(first['frames']) == len(second['frames']) == 600
    for index, row in enumerate(reference['frames']):
        other = first['frames'][index] if index < 600 else second['frames'][index - 600]
        for key in ['CPU', 'RAM', 'video']:
            assert row[key] == other[key], (index + 1, key)
        baseline = first['frames'][-1]['audio'] if index >= 600 else dict(frames=0, nonzero_samples=0)
        for key in ['frames', 'nonzero_samples']:
            assert row['audio'][key] == other['audio'][key] + baseline[key], (index + 1, 'audio', key)
    for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin']:
        assert (folder / 'reference' / name).read_bytes() == (navigation / name).read_bytes(), name
    assert (folder / 'reference/frontend-PCM.s16le').read_bytes() == (
        (prefix / 'frontend-PCM.s16le').read_bytes() + (navigation / 'frontend-PCM.s16le').read_bytes())

    trace = folder / 'C/CPU-before-instructions.bin'
    count, remainder = divmod(trace.stat().st_size, 78)
    assert remainder == 0 and count == comparison['owned_CPU_instructions']
    dtype = np.dtype({'names': ['PC', 'SR'], 'formats': ['>u4', '>u2'], 'offsets': [64, 76], 'itemsize': 78})
    entries = collections.Counter()
    sites = [0xf0fa, 0x191f4, 0x19fda, 0x1028e, 0x20f0c, 0x20e8c, 0x1aa40, 0x20f78, 0x20aa0, 0xdf7a, 0xdeb6, 0xdf6c, 0xde5c]
    for start in range(0, count, 1_000_000):
        records = np.memmap(trace, dtype=dtype, mode='r', offset=start * 78,
                            shape=(min(1_000_000, count - start),))
        for site in sites:
            entries[hex(site)] += int((records['PC'] == site).sum())
        del records
    assert entries['0x19fda'] > 0 and entries['0x1028e'] > 0 and entries['0x20f78'] >= 3
    captures = []
    for path in sorted((folder / 'C').glob('frame-*-RAM.bin'), key=lambda p: int(p.name.split('-')[1])):
        raw = path.read_bytes()
        captures.append(dict(frame=int(path.name.split('-')[1]), scene_mode=get(raw, 0x49c60, 2),
                             floor=get(raw, 0x49c62, 2), scene_index=get(raw, 0x49c64, 2),
                             X=get(raw, 0x49c50), Z=get(raw, 0x49c56)))
    bridge = json.loads((folder / 'C/native-CPU-bridge-report.json').read_text())
    report = dict(status='controller_elevator_to_outdoor_original_C_match_no_scene_transplant',
                  recorded_at=datetime.now(timezone.utc).isoformat(), directory=str(folder), frames=1200,
                  CPU_instructions=count, GPU_counts=comparison['GPU_counts'], DSP_counts=comparison['DSP_counts'],
                  combined_gate_passed=not failed, combined_gate_failed_checks=failed,
                  comparison=str(folder / 'comparison.json'), starting_checkpoint=str(checkpoint),
                  starting_checkpoint_state_sha256=rebuilt['restored_original_checkpoint']['state_sha256'],
                  initial_RAM_sha256=sha(initial), original_checkpoint_RAM_sha256=sha(original_start),
                  final_RAM_sha256=sha(final), exact_start_plus_only_18_byte_code_repair=True,
                  scene_RAM_transplant=False, player_position_injected=False, controller_only_navigation=True,
                  original_C_CPU_trace_and_cycle_costs_match=True, all_frame_RAM_video_PCM_and_final_machine_match=True,
                  original_planning_prefix_and_navigation_replay_exact=True,
                  ordinary_controller_outdoor_entry_verified=True, direct_fresh_boot_replay_verified=False,
                  direct_fresh_boot_to_outdoor_verified=False,
                  fresh_boot_to_merchant_previously_verified=True, fresh_boot_to_merchant_proof=str(merchant_boot_path),
                  DSP_execution_verified=not failed,
                  source_function_entries=dict(entries), captured_controls=captures,
                  final_scene_mode=get(final, 0x49c60, 2), final_floor=get(final, 0x49c62, 2),
                  final_position=dict(X=get(final, 0x49c50), Z=get(final, 0x49c56)),
                  unique_frontend_video_frames=len({row['video'] for row in rebuilt['frames']}),
                  PCM_units=dict(stereo_sample_frames=rebuilt['frames'][-1]['audio']['frames'],
                                 nonzero_individual_channel_samples=rebuilt['frames'][-1]['audio']['nonzero_samples']),
                  validation_loop_seconds=bridge['elapsed_seconds'],
                  local_planner_review=str(ROOT / 'verification/merchant-exit-qualified-plan-current.json'),
                  native_keyboard_verified=False, standalone=False, whole_game_complete=False,
                  source_sha256=sha(Path(__file__).read_bytes()),
                  scope='Exact original merchant checkpoint, then only the existing18-byte word-aligned marker-scan repair. '
                        'Ordinary buttons descend two elevator floors, dismiss the menu, and walk through the ground-floor exit '
                        'into naturally loaded outdoor mode1. No scene RAM transplant or player relocation. The fixed route '
                        'reproduces the original planning runs and reconstructed CPU/GPU/DSP comparison checks. '
                        'A checkpoint continuation is still used. Fresh boot-to-merchant was previously verified in a separate23538-frame comparison; '
                        'the new continuous fresh-start-to-outdoor replay is pending. This continuation has zero DSP instructions and silent PCM. '
                        'Original IRQ/HLE/object processor/device providers remain. Static instruction-level C is not all readable source, '
                        'and no standalone/full-game/native-keyboard/physical-audio claim is made.')
    (folder / 'merchant-outdoor-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    if args.publish:
        (ROOT / 'verification/merchant-outdoor-route-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['status', 'frames', 'CPU_instructions', 'GPU_counts', 'DSP_counts',
                                                  'final_scene_mode', 'final_position', 'validation_loop_seconds']}), flush=True)


if __name__ == '__main__':
    main()
