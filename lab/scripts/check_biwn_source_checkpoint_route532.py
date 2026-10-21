"""Broaden ordinary gameplay coverage from the accepted source outdoor state.

Static room/portal hypothesis is tested using only ordinary pad inputs. An
adaptive original run discovers inputs, a fixed original run must reproduce
it, then source CPU/GPU/IRQ is compared over the entire fixed route.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

from biwn_verified_source_checkpoint import verify_source_checkpoint

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    runtime = json.loads((ROOT / 'verification/unified-restore-runtime-candidate.json').read_text())
    probe = json.loads((ROOT / 'verification/source-checkpoint-probe-candidate.json').read_text())
    checkpoint_proof = ROOT / 'verification/merchant-gated-full-route-verdict-current.json'
    cold = json.loads(checkpoint_proof.read_text())
    checkpoint = Path(cold['directory']) / 'C/report.json'
    provenance = verify_source_checkpoint(checkpoint, checkpoint_proof, runtime['core'])
    for table in [runtime['artifacts_sha256'], runtime['inputs_sha256'], probe['artifacts_sha256']]:
        for name, digest in table.items():
            assert sha(name) == digest, name
    hypothesis_path = ROOT / 'verification/source-checkpoint-static-route-532-hypothesis.json'
    hypothesis = json.loads(hypothesis_path.read_text())
    assert Path(hypothesis['source_RAM']).resolve() == checkpoint.parent / 'final-RAM.bin'
    assert sha(hypothesis['source_RAM']) == hypothesis['source_RAM_sha256']
    assert hypothesis['gate']['target'] == 532 and hypothesis['gate']['direction'] == 2
    out = ROOT / 'runs' / ('source-checkpoint-route532-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    shutil.copy2(hypothesis_path, out / 'static-hypothesis.json')
    # First move inside the starting corridor. Approach the final doorway
    # perpendicular to its boundary, inside the direction-valid64unit strip.
    points = [[13120, 42408]] + hypothesis['points'][:-1]
    points += [[14208, hypothesis['gate']['point'][1]], hypothesis['gate']['point']]
    corners = []
    for point in points:
        while len(corners) >= 2:
            a, b = corners[-2:]
            first = [b[i] - a[i] for i in [0, 1]]
            second = [point[i] - b[i] for i in [0, 1]]
            if first[0] * second[1] != first[1] * second[0] or sum(first[i] * second[i] for i in [0, 1]) < 0:
                break
            corners.pop()
        corners.append(point)
    waypoints = []
    previous = [12992, 42408]
    for target in corners:
        steps = max(1, math.ceil(max(abs(target[i] - previous[i]) for i in [0, 1]) / 600))
        for step in range(1, steps + 1):
            point = [round(previous[i] + (target[i] - previous[i]) * step / steps) for i in [0, 1]]
            if not waypoints or point != [waypoints[-1]['X'], waypoints[-1]['Z']]:
                waypoints.append(dict(X=point[0], Z=point[1]))
        previous = target
    assert len(waypoints) <= 8
    plan = dict(waypoints=waypoints, position_tolerance=8, heading_tolerance=1, opening_A_frames=0, stop_scene_mode=2)
    plan_path = out / 'plan.json'
    save(plan_path, plan)
    frames = 6000
    base = [sys.executable, probe['probe'], '--warm-frames', '0', '--frames', str(frames), '--core', runtime['core'],
            '--restore-source-report', str(checkpoint), '--source-checkpoint-proof', str(checkpoint_proof),
            '--capture-audio', '--native-CPU-bridge', '--extended-CPU', '--CPU-candidate', runtime['CPU_candidate'],
            '--native-CPU-candidate', runtime['native_CPU_candidate']]
    for frame in [1, 3000, frames]:
        base += ['--capture-frame', str(frame)]
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), frames=frames, commands=[],
                 source_checkpoint=provenance, original_checkpoint_restored=False, inherited_program_repair_bytes=18,
                 new_program_repair_applied=False, player_relocation=False, scene_RAM_transplant=False,
                 runtime=runtime, probe_build=probe, static_hypothesis=str(out / 'static-hypothesis.json'),
                 static_planner='Coordinator adaptation of plan_biwn_alternate_entrance.py; no local LLM navigation',
                 static_planner_source_sha256=sha(ROOT / 'scripts/plan_biwn_alternate_entrance.py'),
                 source_RAM_sha256=hypothesis['source_RAM_sha256'], plan=plan, target_scene=532, whole_game_complete=False)
    def mark():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/source-checkpoint-route532-active.json', state)
    def run(phase, command):
        folder = out / phase
        command = command + ['--output', str(folder)]
        item = dict(phase=phase, command=command)
        state['commands'].append(item)
        with (out / (phase + '.log')).open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                     env={**os.environ, 'BIWN_LIVE_ATTACK_COUNTERS': str(folder / 'attack-owner-counts.txt')})
            item['pid'] = child.pid
            state.update(status='running_' + phase, child_pid=child.pid)
            mark()
            print(phase, 'PID', child.pid, flush=True)
            code = child.wait()
        item['exit_code'] = code
        mark()
        assert code == 0, (phase, out / (phase + '.log'))
        return folder
    mark()
    print(out, flush=True)
    try:
        planning = run('planning', base + ['--mode', 'reference', '--navigation-plan', str(plan_path)])
        navigation = json.loads((planning / 'navigation-report.json').read_text())
        raw = (planning / 'final-RAM.bin').read_bytes()
        final = dict(mode=int.from_bytes(raw[0x49c60:0x49c62], 'big'), scene=int.from_bytes(raw[0x49c64:0x49c66], 'big'))
        state.update(planning_result=navigation, planning_final_state=final)
        mark()
        assert navigation['status'] == 'controller_plan_scene_mode_changed' and final == dict(mode=2, scene=532), (navigation, final)
        inputs = planning / 'navigation-input.json'
        reference = run('reference', base + ['--mode', 'reference', '--frame-controller-script', str(inputs)])
        reproduced = {name: sha(planning / name) == sha(reference / name) for name in
                      ['CPU-before-instructions.bin', 'retired-instruction-costs.bin', 'warm-RAM.bin', 'final-RAM.bin',
                       'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']}
        assert all(reproduced.values()), reproduced
        source = run('C', base + ['--mode', 'C', '--frame-controller-script', str(inputs), '--source-CPU-IRQ-entry',
                                 '--regular-GPU-mode', 'C', '--renderer-bundles', '--renderer-overlays', '--material-bundles',
                                 '--control-bundles', '--setup-bundles', '--native-GPU-bridge', '--GPU-frame-only',
                                 '--native-GPU-candidate', runtime['GPU_candidate'], '--stop-on-GPU-original',
                                 '--native-DSP-owner', '--DSP-owner-kind', 'router', '--require-owned-DSP',
                                 '--DSP-router-candidate', runtime['DSP_candidate']])
        comparison_path = out / 'comparison.json'
        command = [sys.executable, probe['comparator'], '--C-run', str(source), '--reference', str(reference),
                   '--expected-frames', str(frames), '--source-checkpoint-report', str(checkpoint),
                   '--source-checkpoint-proof', str(checkpoint_proof), '--output', str(comparison_path)]
        with (out / 'comparison.log').open('w') as log:
            code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
        comparison = json.loads(comparison_path.read_text())
        failed = [key for key, passed in comparison['checks'].items() if not passed]
        assert (code == 0 and not failed) or (code == 1 and failed == ['DSP_owned_positive'] and comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)), failed
        report = json.loads((source / 'report.json').read_text())
        assert report['restored_original_checkpoint'] is None and report['experimental_code_overlay'] is None
        counts = {int(pc): int(hits) for pc, hits in (line.split() for line in (source / 'attack-owner-counts.txt').read_text().splitlines())}
        proof = dict(status='source_checkpoint_ordinary_route_to_building532_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                     directory=str(out), frames=frames, comparison=str(comparison_path), CPU_instructions=comparison['owned_CPU_instructions'],
                     GPU_counts=comparison['GPU_counts'], DSP_counts=comparison['DSP_counts'], raw_failed_checks=failed,
                     fixed_reference_reproduces_planning=reproduced, source_checkpoint=report['restored_source_checkpoint'],
                     inherited_program_repair_bytes=18, new_program_repair_applied=False, final_state=final,
                     attack_calls=counts[0x18df2], source_IRQ_report=report['CPU_IRQ_report'],
                     native_window_verified=False, whole_game_complete=False, default_preview_promoted=False,
                     scope='Ordinary controller route from same-core source-owned outdoor machine to building532. Earlier18byte repair is inherited; no new code repair/scene transplant/player relocation. Fixed original input replay reproduces adaptive original discovery. Source CPU/GPU/IRQ finite-route comparison; inactive DSP gate retained if present. Not a new cold start, readable high-level API, native keyboard/audio or standalone/whole-game proof.')
        save(out / 'verdict.json', proof)
        save(ROOT / 'verification/source-checkpoint-route532-current.json', proof)
        state.update(status='terminal_route532_match', proof=str(out / 'verdict.json'))
        mark()
        print(proof['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        mark()
        raise


if __name__ == '__main__':
    main()
