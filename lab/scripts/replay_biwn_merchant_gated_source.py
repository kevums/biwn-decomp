"""Retry only source execution with both marker variants; reuse the checked original."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    pointer = ROOT / 'verification/merchant-gated-outdoor-route-active.json'
    previous = json.loads(pointer.read_text())
    assert previous['status'] == 'terminal_failed'
    original = Path(previous['directory']) / 'reference'
    reference = json.loads((original / 'report.json').read_text())
    assert len(reference['frames']) == 24738 and not reference['errors']
    assert reference['warm_original_frames'] == 0 and reference['restored_original_checkpoint'] is None
    native_path = ROOT / 'verification/dual-marker-native-CPU-experimental-candidate.json'
    unit_path = ROOT / 'verification/dual-marker-bridge-current.json'
    native = json.loads(native_path.read_text())
    unit = json.loads(unit_path.read_text())
    assert unit['status'] == 'both_marker_variants_native_bridge_CPU_RAM_cycle_match' and unit['cases'] == 2496
    assert unit['candidate_sha256'] == sha(native_path)
    assert reference['core_sha256'] == native['required_core_sha256']
    gate = json.loads((original / 'pre-repair-merchant-gate.json').read_text())
    assert gate['before_frame'] == 23539 and gate['actual_RAM_sha256'] == gate['expected_RAM_sha256']
    assert gate['actual_machine_sha256'] == gate['expected_machine_sha256']
    baseline = ROOT / 'runs/world-controls-20261017T083710.579729Z/reference'
    for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin']:
        assert sha(original / name) == sha(baseline / name)
    out = ROOT / 'runs' / ('merchant-gated-source-replay-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    (out / 'reference').symlink_to(original, target_is_directory=True)
    command = list(previous['commands']['C'])
    command[command.index('--native-CPU-candidate') + 1] = str(native_path)
    command[command.index('--output') + 1] = str(out / 'C')
    assert '--restore-original-report' not in command and command[command.index('--warm-frames') + 1] == '0'
    inputs = dict(previous['hashes'])
    for path in [Path(__file__), native_path, unit_path, Path(native['library']), Path(native['directory']) / 'fast_CPU_bridge.c',
                 Path(native['original_marker_CPU_library']), original / 'report.json', original / 'pre-repair-merchant-gate.json']:
        inputs[str(path)] = sha(path)
    state = dict(status='prepared', directory=str(out), pid=os.getpid(), frames=24738, hashes=inputs,
                 previous_failed_run=previous['directory'], commands=dict(reference=previous['commands']['reference'], C=command),
                 children=dict(reference=dict(pid=previous['children']['reference']['pid'], status='terminal_reused_reference', exit_code=0)),
                 started_unix=time.time(), scope='Source starts independently fromframe1 with no warmup/checkpoint. Reuses an immutable independently completed original reference: exact unpatched merchant RAM+machine gate before23539, then sole marker repair and elevator/exit inputs. Separate bridge accepts exact original/repaired18byte variants; no opcode fallback. Queue/line/ACK, host commit/prefetch/cycle charge, HLE/OP/devices remain.')

    def record():
        for path in [out / 'protocol.json', pointer]:
            path.write_text(json.dumps(state, indent=2) + '\n')

    record()
    try:
        with (out / 'C.log').open('w') as stream:
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
            state.update(status='running_source_with_reused_original', children=dict(state['children'], C=dict(pid=process.pid, status='running')))
            record()
            print(out, 'C PID', process.pid, flush=True)
            code = process.wait()
        state['children']['C'].update(status='terminal_completed' if code == 0 else 'terminal_failed', exit_code=code)
        record()
        assert code == 0, (code, out / 'C.log')
        overlay = command[command.index('--experimental-mainstage-overlay') + 1]
        compare = [sys.executable, str(ROOT / 'scripts/compare_biwn_frame_CPU_only.py'), '--C-run', str(out / 'C'),
                   '--reference', str(original), '--expected-frames', '24738', '--experimental-code-overlay', overlay,
                   '--output', str(out / 'comparison.json')]
        with (out / 'comparison.log').open('w') as stream:
            subprocess.run(compare, stdout=stream, stderr=subprocess.STDOUT, check=True)
        result = json.loads((out / 'comparison.json').read_text())
        assert all(result['checks'].values())
        source_gate = json.loads((out / 'C/pre-repair-merchant-gate.json').read_text())
        assert source_gate == gate
        irq = json.loads((out / 'C/CPU-IRQ-owner-report.json').read_text())
        for field in ['selection', 'core']:
            assert irq[field]['Owned'] > 0 and irq[field]['Original'] == irq[field]['Rejected'] == 0
        semantic = {}
        for phase in ['reference', 'C']:
            for frame, expected in [(23538, (2, 2, 314)), (23698, (2, 0, 312)), (24738, (1, 0, 312))]:
                raw = (out / phase / ('frame-' + str(frame) + '-RAM.bin')).read_bytes()
                actual = tuple(int.from_bytes(raw[a:a + 2], 'big') for a in [0x49c60, 0x49c62, 0x49c64])
                semantic[phase + '_frame' + str(frame)] = actual == expected
        assert all(semantic.values()), semantic
        for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin']:
            assert sha(out / 'C' / name) == sha(baseline / name)
        assert all(sha(Path(path)) == digest for path, digest in inputs.items())
        state.update(status='terminal_exact_merchant_elevator_outdoor_CPU_GPU_DSP_IRQ_match',
                     source_IRQ=irq, exact_unpatched_merchant_gate=source_gate, semantic_milestone_checks=semantic,
                     comparison=str(out / 'comparison.json'), whole_game_complete=False, total_seconds=time.time() - state['started_unix'])
        record()
        (ROOT / 'verification/merchant-gated-outdoor-route-current.json').write_text(json.dumps(state, indent=2) + '\n')
        print(state['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error), total_seconds=time.time() - state['started_unix'])
        record()
        raise


if __name__ == '__main__':
    main()
