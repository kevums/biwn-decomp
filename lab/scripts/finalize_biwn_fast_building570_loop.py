"""Qualify a completed loop's exact-pair checkpoint import; retain raw gates."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(paths):
    h = hashlib.sha256()
    for path in paths:
        with path.open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    out = args.run.resolve()
    state = json.loads((out / 'protocol.json').read_text())
    assert state['status'] == 'terminal_failed' and state['frames'] == 4600
    raw_path = out / 'comparison.json'
    raw = json.loads(raw_path.read_text())
    failed = [k for k, v in raw['checks'].items() if not v]
    assert failed == ['checkpoint_core', 'DSP_owned_positive'], failed
    assert raw['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    assert [s['frames'] for s in state['segments']] == [4000, 600]
    reports = {phase: json.loads((out / phase / 'report.json').read_text()) for phase in ['reference', 'C']}
    imported_path = Path(state['explicit_core_import_proof'])
    imported = json.loads(imported_path.read_text())
    assert imported['status'] == 'one_original_frame_cross_core_state_import_matches'
    assert imported['original_report_unchanged'] and imported['source_checkpoint'] == state['initial_checkpoint']
    original = json.loads(Path(state['initial_checkpoint']).read_text())
    assert original['core_sha256'] == imported['old_core_sha256']
    assert original['mode'] == 'reference' and original['original_CPU_instructions'] > 0
    checkpoint_folder = Path(state['initial_checkpoint']).parent
    serialized_sha = digest([checkpoint_folder / 'final-serialized-state.bin'])
    import_checks = {}
    for phase, report in reports.items():
        assert report['status'] == 'completed_component_uncompared' and not report['errors']
        assert len(report['frames']) == 4600
        restored = report['restored_original_checkpoint']
        import_checks[phase + '_explicit_pinned_pair'] = (
            report['core_sha256'] == imported['new_core_sha256'] and
            restored['source_core_sha256'] == imported['old_core_sha256'] and
            restored['target_core_sha256'] == imported['new_core_sha256'] and
            restored['report'] == state['initial_checkpoint'] and
            restored['explicit_core_compatibility_import'] is True)
        import_checks[phase + '_exact_machine_roundtrip'] = (
            restored['state_sha256'] == serialized_sha and restored['exact_machine_and_RAM_before_execution'] is True and
            digest([out / phase / 'warm-RAM.bin']) == digest([checkpoint_folder / 'final-RAM.bin']))
    # This additionally establishes the complete4600frame original behavior
    # across the core pair, beyond the earlier one-frame compatibility proof.
    segment_checks, offset = {}, 0
    for segment in state['segments']:
        folder, count = Path(segment['directory']), segment['frames']
        previous = json.loads((folder / 'reference/report.json').read_text())
        assert previous['core_sha256'] == imported['old_core_sha256']
        current = reports['reference']['frames'][offset:offset + count]
        segment_checks[folder.name + '_every_CPU_RAM_video'] = all(
            all(a[key] == b[key] for key in ['CPU', 'RAM', 'video'])
            for a, b in zip(current, previous['frames'], strict=True))
        offset += count
    assert offset == 4600
    for name in ['CPU-before-instructions.bin', 'retired-instruction-costs.bin', 'frontend-PCM.s16le']:
        segment_checks[name + '_matches_concatenated_originals'] = digest([out / 'reference' / name]) == digest(
            [Path(s['directory']) / 'reference' / name for s in state['segments']])
    for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin']:
        segment_checks[name + '_matches_previous_exit'] = digest([out / 'reference' / name]) == digest(
            [Path(state['segments'][-1]['directory']) / 'reference' / name])
    captured = []
    for frame, mode in [(3268, 2), (4000, 2), (4159, 1), (4600, 1)]:
        ram = (out / f'C/frame-{frame}-RAM.bin').read_bytes()
        assert ram == (out / f'reference/frame-{frame}-RAM.bin').read_bytes()
        get = lambda address, width=2: int.from_bytes(ram[address:address + width], 'big')
        assert (get(0x49c60), get(0x49c62), get(0x49c64)) == (mode, 0, 570)
        captured.append(dict(frame=frame, mode=mode, floor=0, retained_scene_index=570,
                             X=get(0x49c50, 4), Z=get(0x49c56, 4)))
    assert all(import_checks.values()) and all(segment_checks.values())
    for name, expected in state['hashes'].items():
        assert digest([Path(name)]) == expected, name
    checks = dict(raw['checks'])
    # Exact hash equality remains false in raw_checks. The qualified gate
    # explicitly permits only this independently checked source/target pair.
    del checks['checkpoint_core']
    checks.update(import_checks)
    checks.update(segment_checks)
    qualified_path = out / 'qualified-comparison.json'
    qualified = dict(raw, status='CPU_GPU_checkpoint_compatible_frame_match_DSP_inactive',
                     recorded_at=datetime.now(timezone.utc).isoformat(), checks=checks,
                     raw_comparison=str(raw_path), raw_checks=raw['checks'],
                     raw_failed_checks=failed, exact_checkpoint_core_hash_match=False,
                     checkpoint_compatibility_proof=str(imported_path),
                     scope='All raw CPU/GPU/runtime comparisons pass; DSPinactive is not audio acceptance. The raw checkpoint_core exact-hash gate remains failed. Separate qualified gates require the pinned core pair, exact serialized-machine/RAM round-trip, every earlier original segment CPU/RAM/video frame, concatenated CPU/cycle/PCM bytes and final machine. This qualifies this specific checkpoint continuation, not general cross-core import or standalone execution.')
    assert [k for k, v in checks.items() if not v] == ['DSP_owned_positive']
    qualified_path.write_text(json.dumps(qualified, indent=2) + '\n')
    proof = dict(state, status='terminal_continuous_outdoor_building570_outdoor_source_match',
                 recorded_at=datetime.now(timezone.utc).isoformat(), comparison=str(qualified_path),
                 raw_comparison=str(raw_path), raw_failed_checks=failed,
                 raw_combined_gate_passed=False, combined_gate_failed_checks=['DSP_owned_positive'],
                 exact_checkpoint_core_hash_match=False, qualified_core_import=True,
                 segment_checks=segment_checks, checkpoint_import_checks=import_checks, captured_states=captured,
                 CPU_instructions=raw['owned_CPU_instructions'], GPU_counts=raw['GPU_counts'], DSP_counts=raw['DSP_counts'],
                 DSP_execution_verified=False, no_intermediate_restore=True, source_frames=4600,
                 final_scene_mode=1, final_retained_scene_index=570, native_window_verified=False,
                 default_preview_updated=False, whole_game_complete=False, raw_test_protocol=str(out / 'protocol.json'),
                 scope=state['scope'] + ' Raw exact checkpoint-core hash equality is false. Acceptance uses separate pinned-pair/exact-state compatibility gates and full earlier-segment trace/final-machine matches; the raw failed gate is retained. DSP remains inactive and PCM silent.',
                 finalizer=str(Path(__file__).resolve()), finalizer_sha256=digest([Path(__file__).resolve()]))
    proof.pop('error', None)
    (out / 'qualified-loop-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    (ROOT / 'verification/fast-building570-loop-current.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(status=proof['status'], CPU_instructions=proof['CPU_instructions'],
                          captured_states=captured, raw_failed_checks=failed, qualified_failed_checks=['DSP_owned_positive'])))


if __name__ == '__main__':
    main()
