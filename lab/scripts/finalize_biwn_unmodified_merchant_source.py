"""Accept the new unpatched merchant checkpoint only from terminal evidence.

Reference is the exact same-core original prefix of the earlier24738frame
run, ending before its repair. Its recorded whole-machine gate binds the
merchant state to the separately preserved original merchant binary too.
No new original run or guest-state fabrication is used by this finalizer.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path, size=None):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        if size is None:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
        remaining = size
        while remaining:
            chunk = stream.read(min(8 * 1024 * 1024, remaining))
            assert chunk
            digest.update(chunk)
            remaining -= len(chunk)
    return digest.hexdigest()


def main():
    active_path = ROOT / 'verification/unified-unmodified-merchant-active.json'
    active = json.loads(active_path.read_text())
    out = Path(active['directory'])
    source = out / 'C'
    assert (source / 'report.json').exists(), 'No terminal source report yet; poll the same PID, do not restart'
    candidate_path = Path(active['command'][active['command'].index('--CPU-candidate') + 1])
    build = json.loads((candidate_path.parent / 'report.json').read_text())
    for table in [build['inputs_sha256'], build['artifacts_sha256']]:
        for name, expected in table.items():
            assert sha(name) == expected, ('Pinned build file changed', name)
    report = json.loads((source / 'report.json').read_text())
    reference = ROOT / 'runs/merchant-gated-source-replay-20261017T101240.185578Z/reference'
    original = json.loads((reference / 'report.json').read_text())
    gate = json.loads((reference / 'pre-repair-merchant-gate.json').read_text())
    frames = 23538
    checks = dict(source_mode=report['mode'] == 'C', original_mode=original['mode'] == 'reference',
                  complete_frames=len(report['frames']) == report['requested_frames'] == frames,
                  same_core=report['core_sha256'] == original['core_sha256'] == active['core_sha256'],
                  no_warmup=report['warm_original_frames'] == original['warm_original_frames'] == 0,
                  no_checkpoint=report['restored_original_checkpoint'] is None and original['restored_original_checkpoint'] is None,
                  no_source_repair=report['experimental_code_overlay'] is None,
                  original_prefix_unmodified=original['experimental_code_overlay']['applied_before_frame'] == frames + 1,
                  all_prefix_frames=report['frames'] == original['frames'][:frames],
                  no_errors=not report['errors'] and not original['errors'],
                  no_CPU_fallback=report['original_CPU_instructions'] == report['rejected_CPU_instructions'] == 0,
                  reference_gate_is_real=gate['state_restored'] is False and gate['memory_injected'] is False and gate['before_frame'] == frames + 1)
    actual_inputs = json.loads(Path(report['frame_controller_script']).read_text())['windows']
    original_inputs = json.loads(Path(original['frame_controller_script']).read_text())['windows']

    def buttons(windows):
        values = [set() for _ in range(frames)]
        for row in windows:
            for frame in range(max(1, row['start_frame']), min(frames + 1, row['stop_frame'])):
                values[frame - 1].update(row['buttons'])
        return values

    checks['same_prefix_controller_inputs'] = buttons(actual_inputs) == buttons(original_inputs)
    count = report['owned_CPU_instructions']
    hashes = {}
    for name, width in [('CPU-before-instructions.bin', 78), ('retired-instruction-costs.bin', 8)]:
        assert (source / name).stat().st_size == count * width
        hashes[name] = [sha(source / name), sha(reference / name, count * width)]
        checks[name] = hashes[name][0] == hashes[name][1]
    audio_bytes = report['audio']['frames'] * 4
    assert (source / 'frontend-PCM.s16le').stat().st_size == audio_bytes
    hashes['frontend-PCM.s16le'] = [sha(source / 'frontend-PCM.s16le'), sha(reference / 'frontend-PCM.s16le', audio_bytes)]
    checks['frontend-PCM.s16le'] = hashes['frontend-PCM.s16le'][0] == hashes['frontend-PCM.s16le'][1]
    merchant_original = Path(gate['expected_source'])
    merchant_report = json.loads((merchant_original / 'report.json').read_text())
    checks['CPU_count_matches_preserved_original_merchant'] = count == merchant_report['original_CPU_instructions']
    for name, key in [('final-RAM.bin', 'RAM'), ('final-serialized-state.bin', 'machine')]:
        expected = gate['actual_' + key + '_sha256']
        checks[name] = sha(source / name) == expected == gate['expected_' + key + '_sha256'] == sha(merchant_original / name)
        hashes[name] = [sha(source / name), expected]
    hashes['final-video.bin'] = [sha(source / 'final-video.bin'), original['frames'][frames - 1]['video']]
    checks['final_video'] = hashes['final-video.bin'][0] == hashes['final-video.bin'][1]
    checks['captured_PNG'] = (source / 'final-frame.png').read_bytes() == (reference / 'frame-23538.png').read_bytes()
    counters = {}
    gpu_source_instructions = None
    for label, path, count_key, error_key in [('GPU', report['regular_GPU_report'], 'counts', 'errors'),
                                               ('DSP', report['DSP_report'], 'core_counts', 'errors')]:
        observed = json.loads(Path(path).read_text())
        counters[label] = observed[count_key]
        if label == 'GPU':
            gpu_source_instructions = observed['C_source_instructions']
        checks[label + '_source_positive_no_fallback'] = observed[count_key]['Owned'] > 0 and observed[count_key]['Original'] == observed[count_key]['Rejected'] == 0 and not observed[error_key]
    irq = json.loads(Path(report['CPU_IRQ_report']).read_text())
    for label, key in [('IRQ_entry', 'core'), ('IRQ_selection', 'selection')]:
        counts = irq[key]
        checks[label + '_source_positive_no_fallback'] = counts['Owned'] > 0 and counts['Original'] == counts['Rejected'] == 0
    checks['IRQ_no_errors'] = irq['source']['errors'] == 0
    state = (source / 'final-RAM.bin').read_bytes()
    get = lambda address, size=2: int.from_bytes(state[address:address + size], 'big')
    final = dict(mode=get(0x49c60), floor=get(0x49c62), retained_scene=get(0x49c64), X=get(0x49c50, 4), Z=get(0x49c56, 4))
    checks['unmodified_merchant_state'] = final == dict(mode=2, floor=2, retained_scene=314, X=12831, Z=42385)
    counts = {int(pc): int(hits) for pc, hits in (line.split() for line in (out / 'attack-owner-counts.txt').read_text().splitlines())}
    comparison = dict(status='unmodified_source_merchant_prefix_comparison_' + ('pass' if all(checks.values()) else 'fail'),
                      recorded_at=datetime.now(timezone.utc).isoformat(), checks=checks, sha256=hashes,
                      source_report=str(source / 'report.json'), reference_prefix_report=str(reference / 'report.json'),
                      reference_exact_merchant_gate=str(reference / 'pre-repair-merchant-gate.json'),
                      separate_original_merchant_checkpoint=str(merchant_original / 'report.json'), frames=frames,
                      CPU_instructions=count, prefix_reference_core=original['core_sha256'])
    (out / 'comparison.json').write_text(json.dumps(comparison, indent=2) + '\n')
    assert all(checks.values()), [key for key, passed in checks.items() if not passed]
    proof = dict(status='fresh_start_unmodified_merchant_source_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                 directory=str(out), frames=frames, comparison=str(out / 'comparison.json'), all_comparison_gates_passed=True,
                 CPU_instructions=count, GPU_counts=counters['GPU'], DSP_counts=counters['DSP'],
                 GPU_source_instructions=gpu_source_instructions,
                 GPU_counter_units='Owned counts are callback bundles; source instruction count is separate.',
                 source_IRQ_selection=irq['selection'], source_IRQ_entry=irq['core'],
                 original_warm_frames=0, initial_checkpoint_restored=False, repair_bytes=0,
                 final_state=final, final_RAM_sha256=sha(source / 'final-RAM.bin'),
                 final_machine_sha256=sha(source / 'final-serialized-state.bin'),
                 exact_unmodified_merchant_gate=gate, source_CPU_compatible_attack_calls=counts[0x18df2],
                 source_CPU_compatible_attack_instruction_hits=sum(counts.values()),
                 native_window_verified=False, whole_game_complete=False,
                 remaining_providers=['Original IRQ queue/device line and ACK/vector', 'Host commit/prefetch/cycle charge',
                                      'Firmware HLE/CD bootstrap', 'Original Object Processor and hardware devices'],
                 scope='Unified attack/scene-exit/dual-marker source CPU plus sourceGPU/DSP/IRQselection/entry fromframe1, no original warmup/checkpoint or game-byte repair.23538frames match the unmodified prefix of the same-core original reference, including native CPU/cost traces, all frames and PCM. Final machine/RAM match that reference gate and the preserved original merchant binaries. This yields an unmodified source-owned merchant checkpoint; not an elevator/outdoor run, new readable high-level API installation, hardware-accuracy claim or standalone/whole-game proof.')
    (out / 'verdict.json').write_text(json.dumps(proof, indent=2) + '\n')
    (ROOT / 'verification/unmodified-source-merchant-current.json').write_text(json.dumps(proof, indent=2) + '\n')
    active.update(status='terminal_unmodified_source_merchant_match', comparison=str(out / 'comparison.json'),
                  proof=str(out / 'verdict.json'), final_state=final)
    active_path.write_text(json.dumps(active, indent=2) + '\n')
    (out / 'protocol.json').write_text(json.dumps(active, indent=2) + '\n')
    print(proof['status'], flush=True)


if __name__ == '__main__':
    main()
