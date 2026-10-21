"""Retain Deck/mail capability on the new same-core source merchant profile.

Source checkpoint origin and all three legacy repairs are explicit. This
test does not silently reinterpret modified behavior as the original game.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

from biwn_verified_unmodified_merchant_checkpoint import verify_source_checkpoint

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def finish_mail(out, state):
    comparison = json.loads((out / 'comparison.json').read_text())
    failed = [key for key, value in comparison['checks'].items() if not value]
    assert failed == ['DSP_owned_positive'] and comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    assert [(row['phase'], row['exit_code']) for row in state['commands']] == [('reference', 0), ('C', 0), ('comparison', 1)]
    original = json.loads((out / 'reference/report.json').read_text())
    source = json.loads((out / 'C/report.json').read_text())
    trace = out / 'reference/CPU-before-instructions.bin'
    assert trace.stat().st_size == original['original_CPU_instructions'] * 78
    assert sha(trace) == comparison['sha256']['CPU-before-instructions.bin'][0] == comparison['sha256']['CPU-before-instructions.bin'][1]
    # The native bridge leaves report.PC_counts empty. Count the actual full
    # accepted trace instead; these are observed PCs, not inferred calls.
    dtype = np.dtype({'names': ['pc'], 'formats': ['>u4'], 'offsets': [64], 'itemsize': 78})
    records = np.memmap(trace, mode='r', dtype=dtype)
    addresses, hits = np.unique(records['pc'], return_counts=True)
    pcs = {hex(int(pc)): int(count) for pc, count in zip(addresses, hits)}
    save(out / 'observed-PC-counts.json', dict(trace=str(trace), trace_sha256=sha(trace), counts=pcs))
    assert pcs.get('0x16bf4', 0) == pcs.get('0x15e8e', 0) == 1
    assert pcs.get('0x1a54a', 0) >= 2
    provenance = verify_source_checkpoint(state['source_checkpoint']['report'], state['source_checkpoint']['source_proof'], state['runtime']['core'])
    assert source['restored_original_checkpoint'] is None and source['restored_source_checkpoint']['inherited_repair_bytes'] == 0
    assert source['experimental_code_overlay']['after_exact_restore']
    assert sum(len(bytes.fromhex(p['replacement'])) for p in source['experimental_code_overlay']['patches']) == 56
    irq = json.loads(Path(source['CPU_IRQ_report']).read_text())
    gpu = json.loads(Path(source['regular_GPU_report']).read_text())
    proof = dict(status='source_merchant_Deck_mail_roundtrip_match', recorded_at=datetime.now(timezone.utc).isoformat(),
        directory=str(out), frames=200, comparison=str(out / 'comparison.json'), commands=state['commands'],
        source_checkpoint=provenance, original_checkpoint_restored=False, inherited_program_repair_bytes=0,
        post_restore_repair_bytes=56, patches=state['patches'], CPU_instructions=comparison['owned_CPU_instructions'],
        GPU_counts=comparison['GPU_counts'], GPU_source_instructions=gpu['C_source_instructions'],
        GPU_counter_units='Owned counts are callback bundles; source instruction count is separate.', DSP_counts=comparison['DSP_counts'],
        source_IRQ_selection=irq['selection'], source_IRQ_entry=irq['core'], raw_failed_checks=failed,
        observed_PC_counts=str(out / 'observed-PC-counts.json'),
        mail_list_calls=pcs['0x16bf4'], mail_message_calls=pcs['0x15e8e'], world_returns=pcs['0x1a54a'],
        native_window_verified=False, physical_audio_verified=False, default_preview_promoted=False, whole_game_complete=False,
        scope='Same-core source-owned unmodified merchant checkpoint, then56explicit legacy repair bytes in3patches. Ordinary B+C/4/A/C/C/0 opens Deck, mail list and one message, backs out and returns to world. Source CPU/GPU/IRQ matches original traces/frames/PCM/final machine; raw inactive DSP gate retained. Not unmodified-program behavior, a new cold start, physical keyboard/audio or standalone/whole-game proof.')
    save(out / 'verdict.json', proof)
    save(ROOT / 'verification/source-checkpoint-mail-current.json', proof)
    return proof


def main():
    runtime = json.loads((ROOT / 'verification/unified-restore-runtime-candidate.json').read_text())
    probe = json.loads((ROOT / 'verification/unmodified-merchant-checkpoint-probe-candidate.json').read_text())
    proof_path = ROOT / 'verification/unmodified-source-merchant-current.json'
    cold = json.loads(proof_path.read_text())
    checkpoint = Path(cold['directory']) / 'C/report.json'
    provenance = verify_source_checkpoint(checkpoint, proof_path, runtime['core'])
    for table in [runtime['inputs_sha256'], runtime['artifacts_sha256'], probe['artifacts_sha256']]:
        for path, digest in table.items():
            assert sha(path) == digest, path
    out = ROOT / 'runs' / ('source-checkpoint-mail-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    old_recipe = json.loads((ROOT / 'verification/interactive-preview-recipe.json').read_text())
    old_command = old_recipe['candidate']
    controls = Path(old_command[old_command.index('--frame-controller-script') + 1])
    overlay = Path(old_command[old_command.index('--experimental-code-overlay') + 1])
    for source, name in [(controls, 'input.json'), (overlay, 'combined-repair.json')]:
        assert sha(source) == old_recipe['hashes'][str(source)], source
        shutil.copy2(source, out / name)
    patches = json.loads((out / 'combined-repair.json').read_text())['patches']
    repair_bytes = sum(len(bytes.fromhex(p['replacement'])) for p in patches)
    assert len(patches) == 3 and repair_bytes == 56
    frames = 200
    base = [sys.executable, probe['probe'], '--warm-frames', '0', '--frames', str(frames), '--core', runtime['core'],
            '--restore-source-report', str(checkpoint), '--source-checkpoint-proof', str(proof_path),
            '--experimental-code-overlay', str(out / 'combined-repair.json'), '--capture-audio',
            '--native-CPU-bridge', '--extended-CPU', '--CPU-candidate', runtime['CPU_candidate'],
            '--native-CPU-candidate', runtime['native_CPU_candidate'], '--frame-controller-script', str(out / 'input.json')]
    for frame in [1, 30, 60, 90, 120, 150, 180, 200]:
        base += ['--capture-frame', str(frame)]
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), commands=[], runtime=runtime,
                 probe_build=probe, source_checkpoint=provenance, inherited_program_repair_bytes=0,
                 post_restore_repair_bytes=repair_bytes, patches=patches, original_checkpoint_restored=False,
                 default_preview_promoted=False, whole_game_complete=False)
    def mark():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/source-checkpoint-mail-active.json', state)
    def run(phase, command):
        item = dict(phase=phase, command=command)
        state['commands'].append(item)
        with (out / (phase + '.log')).open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                env={**os.environ, 'BIWN_LIVE_ATTACK_COUNTERS': str(out / (phase + '-attack-owner-counts.txt'))})
            item['pid'] = child.pid
            state.update(status='running_' + phase, child_pid=child.pid)
            mark()
            print(phase, 'PID', child.pid, flush=True)
            code = child.wait()
        item['exit_code'] = code
        mark()
        return code
    mark()
    print(out, flush=True)
    try:
        assert run('reference', base + ['--mode', 'reference', '--output', str(out / 'reference')]) == 0
        assert run('C', base + ['--mode', 'C', '--source-CPU-IRQ-entry', '--regular-GPU-mode', 'C', '--renderer-bundles',
            '--renderer-overlays', '--material-bundles', '--control-bundles', '--setup-bundles', '--native-GPU-bridge',
            '--GPU-frame-only', '--native-GPU-candidate', runtime['GPU_candidate'], '--stop-on-GPU-original',
            '--native-DSP-owner', '--DSP-owner-kind', 'router', '--require-owned-DSP', '--DSP-router-candidate', runtime['DSP_candidate'],
            '--output', str(out / 'C')]) == 0
        compare = [sys.executable, probe['comparator'], '--C-run', str(out / 'C'), '--reference', str(out / 'reference'),
            '--expected-frames', str(frames), '--source-checkpoint-report', str(checkpoint), '--source-checkpoint-proof', str(proof_path),
            '--experimental-code-overlay', str(out / 'combined-repair.json'), '--output', str(out / 'comparison.json')]
        code = run('comparison', compare)
        assert code == 1
        proof = finish_mail(out, state)
        state.update(status='terminal_mail_roundtrip_match', proof=str(out / 'verdict.json'))
        mark()
        print(proof['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    main()
