"""Navigate and replay from the verified source-produced outdoor machine."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    runtime = json.loads((ROOT / 'verification/unified-restore-runtime-candidate.json').read_text())
    probe = json.loads((ROOT / 'verification/source-checkpoint-probe-candidate.json').read_text())
    for table in [runtime['artifacts_sha256'], runtime['inputs_sha256'], probe['artifacts_sha256']]:
        for name, digest in table.items():
            assert sha(name) == digest, name
    checkpoint_proof = ROOT / 'verification/merchant-gated-full-route-verdict-current.json'
    cold = json.loads(checkpoint_proof.read_text())
    checkpoint = Path(cold['directory']) / 'C/report.json'
    out = ROOT / 'runs' / ('source-checkpoint-north-route-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir(parents=True)
    plan = json.loads((ROOT / 'runs/north-building-route-plan-20261017T100311.140245Z/plan.json').read_text())
    plan['waypoints'].insert(0, dict(X=13120, Z=42416))
    assert len(plan['waypoints']) == 8
    plan_path = out / 'plan.json'
    save(plan_path, plan)
    base = [sys.executable, probe['probe'], '--warm-frames', '0', '--frames', '4000', '--core', runtime['core'],
            '--restore-source-report', str(checkpoint), '--source-checkpoint-proof', str(checkpoint_proof),
            '--capture-audio', '--native-CPU-bridge', '--extended-CPU', '--CPU-candidate', runtime['CPU_candidate'],
            '--native-CPU-candidate', runtime['native_CPU_candidate']]
    for frame in [1, 2000, 3268, 4000]:
        base += ['--capture-frame', str(frame)]
    state = dict(status='prepared', directory=str(out), pid=os.getpid(), commands=[], frames=4000,
                 source_checkpoint=str(checkpoint), source_checkpoint_proof=str(checkpoint_proof),
                 source_checkpoint_proof_sha256=sha(checkpoint_proof), plan=plan, runtime_build=runtime,
                 original_checkpoint_restored=False, inherited_program_repair_bytes=18,
                 new_program_repair_applied=False, scene_RAM_transplant=False, player_relocation=False,
                 whole_game_complete=False)

    def checkpoint_state():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/source-checkpoint-north-route-active.json', state)

    def run(phase, command):
        folder = out / phase
        command += ['--output', str(folder)]
        row = dict(phase=phase, command=command)
        state['commands'].append(row)
        with (out / (phase + '.log')).open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                     env={**os.environ, 'BIWN_LIVE_ATTACK_COUNTERS': str(folder / 'attack-owner-counts.txt')})
            row['pid'] = child.pid
            state.update(status='running_' + phase, child_pid=child.pid)
            checkpoint_state()
            print(phase, 'PID', child.pid, flush=True)
            code = child.wait()
        row['exit_code'] = code
        checkpoint_state()
        assert code == 0, (phase, out / (phase + '.log'))
        return folder

    checkpoint_state()
    try:
        discovery = run('planning', base + ['--mode', 'reference', '--navigation-plan', str(plan_path)])
        navigation = json.loads((discovery / 'navigation-report.json').read_text())
        RAM = (discovery / 'final-RAM.bin').read_bytes()
        state['planning_result'] = navigation
        state['planning_final_state'] = dict(mode=int.from_bytes(RAM[0x49c60:0x49c62], 'big'),
                                           retained_scene=int.from_bytes(RAM[0x49c64:0x49c66], 'big'))
        checkpoint_state()
        assert navigation['status'] == 'controller_plan_scene_mode_changed', navigation
        assert state['planning_final_state'] == dict(mode=2, retained_scene=570)
        inputs = discovery / 'navigation-input.json'
        reference = run('reference', base + ['--mode', 'reference', '--frame-controller-script', str(inputs)])
        reproduced = {name: sha(reference / name) == sha(discovery / name) for name in
                      ['CPU-before-instructions.bin', 'retired-instruction-costs.bin', 'warm-RAM.bin',
                       'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']}
        assert all(reproduced.values()), reproduced
        source = run('C', base + ['--mode', 'C', '--frame-controller-script', str(inputs), '--source-CPU-IRQ-entry',
                                '--regular-GPU-mode', 'C', '--renderer-bundles', '--renderer-overlays', '--material-bundles',
                                '--control-bundles', '--setup-bundles', '--native-GPU-bridge', '--GPU-frame-only',
                                '--native-GPU-candidate', runtime['GPU_candidate'], '--stop-on-GPU-original',
                                '--native-DSP-owner', '--DSP-owner-kind', 'router', '--require-owned-DSP',
                                '--DSP-router-candidate', runtime['DSP_candidate']])
        comparison_path = out / 'comparison.json'
        command = [sys.executable, probe['comparator'], '--C-run', str(source), '--reference', str(reference),
                   '--expected-frames', '4000', '--source-checkpoint-report', str(checkpoint),
                   '--source-checkpoint-proof', str(checkpoint_proof), '--output', str(comparison_path)]
        with (out / 'comparison.log').open('w') as log:
            code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
        comparison = json.loads(comparison_path.read_text())
        failed = [key for key, passed in comparison['checks'].items() if not passed]
        assert (code == 0 and not failed) or (code == 1 and failed == ['DSP_owned_positive'] and
                                              comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)), failed
        report = json.loads((source / 'report.json').read_text())
        assert report['restored_original_checkpoint'] is None
        assert report['restored_source_checkpoint']['origin'] == 'verified_source_execution'
        assert report['experimental_code_overlay'] is None
        counts = {int(pc): int(hits) for pc, hits in (line.split() for line in (source / 'attack-owner-counts.txt').read_text().splitlines())}
        proof = dict(status='source_checkpoint_to_scene570_unified_CPU_GPU_IRQ_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                     directory=str(out), comparison=str(comparison_path), frames=4000,
                     CPU_instructions=comparison['owned_CPU_instructions'], GPU_counts=comparison['GPU_counts'],
                     DSP_counts=comparison['DSP_counts'], source_IRQ=report['CPU_IRQ_report'],
                     source_checkpoint=report['restored_source_checkpoint'], original_checkpoint_restored=False,
                     inherited_program_repair_bytes=18, new_program_repair_applied=False,
                     raw_failed_checks=failed, DSP_execution_verified=not failed,
                     fixed_reference_reproduces_discovery=reproduced, final_state=state['planning_final_state'],
                     attack_instruction_hits=sum(counts.values()), attack_calls=counts[0x18df2],
                     source_runtime_build=runtime, native_window_verified=False, default_preview_promoted=False,
                     whole_game_complete=False,
                     scope='Starts by restoring the exact machine produced by the checked24738frame source startup/merchant/outdoor route on the same core. That state contains the earlier18byte marker repair; no new game-byte repair, position/scene transplant or readiness injection. Ordinary waypoint buttons reach scene570; fixed original replay reproduces discovery. New unified attack/scene-exit/dual-marker CPU and source GPU/IRQ run4000frames against original processors, with full CPU/cost/frame/final-machine checks. DSP coverage depends on recorded counters; raw inactive gate retained when applicable. Checkpoint continuation, not a new cold-start or standalone/whole-game proof.')
        save(out / 'verdict.json', proof)
        save(ROOT / 'verification/source-checkpoint-north-route-current.json', proof)
        state.update(status='terminal_source_checkpoint_route_match', comparison=str(comparison_path), proof=str(out / 'verdict.json'))
        checkpoint_state()
        print(proof['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        checkpoint_state()
        raise


if __name__ == '__main__':
    main()
