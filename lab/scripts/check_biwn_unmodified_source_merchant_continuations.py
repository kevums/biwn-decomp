"""Compare combat/elevator from the new zero-repair source merchant machine.

Run only after the existing startup finalizer accepts its complete run. The
two combat paths have no game-byte repair; the elevator path explicitly
applies the established 18-byte repair after restoring the exact checkpoint.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from biwn_verified_unmodified_merchant_checkpoint import verify_source_checkpoint

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main(combined_profile=False):
    proof_path = ROOT / 'verification/unmodified-source-merchant-current.json'
    # Missing terminal proof is not a reason to restart the original source job.
    assert proof_path.exists(), 'Source startup comparison is pending; poll its existing PID/watcher'
    cold = json.loads(proof_path.read_text())
    runtime = json.loads((ROOT / 'verification/unified-restore-runtime-candidate.json').read_text())
    probe = json.loads((ROOT / 'verification/unmodified-merchant-checkpoint-probe-candidate.json').read_text())
    checkpoint = Path(cold['directory']) / 'C/report.json'
    provenance = verify_source_checkpoint(checkpoint, proof_path, runtime['core'])
    for table in [runtime['artifacts_sha256'], runtime['inputs_sha256'], probe['artifacts_sha256']]:
        for path, digest in table.items():
            assert sha(path) == digest, path
    combat = json.loads((ROOT / 'verification/ordinary-gameplay-damage-current.json').read_text())
    mail = None
    combined = None
    if combined_profile:
        mail = json.loads((ROOT / 'verification/source-checkpoint-mail-current.json').read_text())
        assert mail['status'] == 'source_merchant_Deck_mail_roundtrip_match'
        assert mail['source_checkpoint']['report_sha256'] == provenance['report_sha256']
        combined = Path(mail['directory']) / 'combined-repair.json'
        mail_report = json.loads((Path(mail['directory']) / 'C/report.json').read_text())
        assert sha(combined) == mail_report['experimental_code_overlay']['sha256']
        assert sum(len(bytes.fromhex(p['replacement'])) for p in json.loads(combined.read_text())['patches']) == 56
    prefix = 'primary-source-profile-' if combined_profile else 'unmodified-source-merchant-continuations-'
    active_name = 'primary-source-profile-active.json' if combined_profile else 'unmodified-source-merchant-continuations-active.json'
    proof_name = 'primary-source-profile-current.json' if combined_profile else 'unmodified-source-merchant-continuations-current.json'
    out = ROOT / 'runs' / (prefix + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    cases = []
    for row in combat['cases']:
        source = Path(row['input'])
        target = out / (row['name'] + '-input.json')
        target.write_bytes(source.read_bytes())
        cases.append(dict(name=row['name'], frames=row['frames'], input=str(target), input_source=str(source),
                          input_source_sha256=sha(source), repair=str(combined) if combined else None,
                          repair_bytes=56 if combined else 0, expected_attack_calls=9 if row['name'] == 'unarmed' else 8))
    old = ROOT / 'runs/merchant-gated-source-replay-20261017T101240.185578Z/C/report.json'
    old_report = json.loads(old.read_text())
    full_inputs = json.loads(Path(old_report['frame_controller_script']).read_text())['windows']
    windows = [dict(start_frame=max(1, w['start_frame'] - 23538), stop_frame=min(1201, w['stop_frame'] - 23538), buttons=w['buttons'])
               for w in full_inputs if w['stop_frame'] > 23539 and w['start_frame'] < 24739]
    assert windows and all(w['start_frame'] < w['stop_frame'] for w in windows)
    elevator_input = out / 'elevator-input.json'
    save(elevator_input, dict(windows=windows))
    repair = combined or Path(old_report['experimental_code_overlay']['manifest'])
    assert sha(repair) == (mail_report['experimental_code_overlay']['sha256'] if combined else old_report['experimental_code_overlay']['sha256'])
    cases.append(dict(name='two_floors_outdoors', frames=1200, input=str(elevator_input),
                      input_source=old_report['frame_controller_script'], input_source_sha256=sha(old_report['frame_controller_script']),
                      repair=str(repair), repair_sha256=sha(repair), repair_bytes=56 if combined else 18))
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), source_checkpoint=provenance,
                 cases=cases, commands=[], source_runtime_build=runtime, frozen_probe_build=probe,
                 inherited_program_repair_bytes=0, original_checkpoint_restored=False, whole_game_complete=False,
                 combined_profile=combined_profile, mail_roundtrip_proof=str(ROOT / 'verification/source-checkpoint-mail-current.json') if combined else None)
    def mark():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification' / active_name, state)
    def run(phase, command, log_path, counter_path=None):
        item = dict(phase=phase, command=command)
        state['commands'].append(item)
        with log_path.open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                     env={**os.environ, **({'BIWN_LIVE_ATTACK_COUNTERS': str(counter_path)} if counter_path else {})})
            item['pid'] = child.pid
            state.update(status='running_' + phase, child_pid=child.pid)
            mark()
            print(phase, 'PID', child.pid, flush=True)
            code = child.wait()
        item['exit_code'] = code
        mark()
        return code
    mark()
    try:
        results = []
        for case in cases:
            folder = out / case['name']
            folder.mkdir()
            base = [sys.executable, probe['probe'], '--warm-frames', '0', '--frames', str(case['frames']), '--core', runtime['core'],
                    '--restore-source-report', str(checkpoint), '--source-checkpoint-proof', str(proof_path),
                    '--capture-audio', '--native-CPU-bridge', '--extended-CPU', '--CPU-candidate', runtime['CPU_candidate'],
                    '--native-CPU-candidate', runtime['native_CPU_candidate'], '--frame-controller-script', case['input']]
            if case['repair']:
                base += ['--experimental-code-overlay', case['repair']]
            counters = folder / 'attack-owner-counts.txt'
            reference = base + ['--mode', 'reference', '--output', str(folder / 'reference')]
            assert run(case['name'] + '_reference', reference, folder / 'reference.log') == 0
            source = base + ['--mode', 'C', '--source-CPU-IRQ-entry', '--regular-GPU-mode', 'C', '--renderer-bundles',
                             '--renderer-overlays', '--material-bundles', '--control-bundles', '--setup-bundles',
                             '--native-GPU-bridge', '--GPU-frame-only', '--native-GPU-candidate', runtime['GPU_candidate'],
                             '--stop-on-GPU-original', '--native-DSP-owner', '--DSP-owner-kind', 'router', '--require-owned-DSP',
                             '--DSP-router-candidate', runtime['DSP_candidate'], '--output', str(folder / 'C')]
            assert run(case['name'] + '_source', source, folder / 'source.log', counters) == 0
            compare = [sys.executable, probe['comparator'], '--C-run', str(folder / 'C'), '--reference', str(folder / 'reference'),
                       '--expected-frames', str(case['frames']), '--source-checkpoint-report', str(checkpoint),
                       '--source-checkpoint-proof', str(proof_path), '--output', str(folder / 'comparison.json')]
            if case['repair']:
                compare += ['--experimental-code-overlay', case['repair']]
            code = run(case['name'] + '_comparison', compare, folder / 'comparison.log')
            comparison = json.loads((folder / 'comparison.json').read_text())
            failed = [key for key, passed in comparison['checks'].items() if not passed]
            assert (code == 0 and not failed) or (code == 1 and failed == ['DSP_owned_positive'] and comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)), (case['name'], failed)
            report = json.loads((folder / 'C/report.json').read_text())
            assert report['restored_original_checkpoint'] is None
            assert report['restored_source_checkpoint']['inherited_repair_bytes'] == 0
            overlay = report['experimental_code_overlay']
            if case['repair']:
                assert overlay['after_exact_restore'] and overlay['original_disc_modified'] is False
                assert sum(len(bytes.fromhex(p['replacement'])) for p in overlay['patches']) == case['repair_bytes']
            else:
                assert overlay is None
            counts = {int(pc): int(hits) for pc, hits in (line.split() for line in counters.read_text().splitlines())}
            if 'expected_attack_calls' in case:
                assert counts[0x18df2] == case['expected_attack_calls'] and counts[0x18e5c] == 1
            ram = (folder / 'C/final-RAM.bin').read_bytes()
            read = lambda address, size=2: int.from_bytes(ram[address:address+size], 'big')
            final = dict(mode=read(0x49c60), floor=read(0x49c62), retained_scene=read(0x49c64), X=read(0x49c50, 4), Z=read(0x49c56, 4))
            if case['name'] == 'two_floors_outdoors':
                assert final == dict(mode=1, floor=0, retained_scene=312, X=12992, Z=42408), final
            results.append(dict(name=case['name'], frames=case['frames'], comparison=str(folder / 'comparison.json'),
                                CPU_instructions=comparison['owned_CPU_instructions'], GPU_counts=comparison['GPU_counts'], DSP_counts=comparison['DSP_counts'],
                                source_checkpoint=report['restored_source_checkpoint'], inherited_repair_bytes=0,
                                continuation_repair_bytes=case['repair_bytes'], attack_calls=counts[0x18df2],
                                damage_instructions=counts[0x18e5c], final_state=final, raw_failed_checks=failed))
        proof = dict(status='source_merchant_combined_repair_combat_and_elevator_profile_match' if combined else 'unmodified_source_merchant_combat_and_elevator_continuations_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                     directory=str(out), cases=results, source_checkpoint=provenance, original_checkpoint_restored=False,
                     inherited_program_repair_bytes=0, whole_game_complete=False, default_preview_promoted=False,
                     mail_roundtrip_proof=state['mail_roundtrip_proof'],
                     scope=('Same-core unified source CPU/GPU/IRQ continues from the zero-repair cold-source merchant machine. All three branches apply the same56byte legacy Deck/selector/marker repair after exact restore; separate200frame mail proof uses that same profile. ' if combined else 'Same-core unified source CPU/GPU/IRQ continues from the zero-repair cold-source merchant machine. Two separate natural combat branches have no repair; the elevator branch explicitly applies18bytes after exact restore. ') + 'Full native CPU/cost/frame/PCM/final-machine comparisons; raw inactive DSP gate retained. CPU-compatible attack replacement, not the high-level API, physical keyboard/audio or standalone/whole-game proof.')
        save(out / 'verdict.json', proof)
        save(ROOT / 'verification' / proof_name, proof)
        state.update(status='terminal_continuations_match', proof=str(out / 'verdict.json'))
        mark()
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--combined-profile', action='store_true', help='Test all branches with the existing56byte Deck/mail+marker repair set; preserve separate0/18byte proofs')
    args = parser.parse_args()
    main(args.combined_profile)
