"""Review fresh native-collision/control routes with their actual scope."""
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def read(p):
    return json.loads(Path(p).read_text())


def main():
    v = ROOT / 'verification'
    out = v / 'actor-collision-integration-review' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    snapshots = out / 'snapshots'
    snapshots.mkdir()
    dependencies = {}

    def bind(p, expected=None):
        p = Path(p).resolve()
        digest = sha(p)
        assert expected is None or digest == expected, str(p)
        original = p
        if p.name.endswith(('-current.json', '-active.json')):
            import hashlib
            target = snapshots / (hashlib.sha256(str(p).encode()).hexdigest()[:12] + '-' + p.name)
            if not target.exists():
                shutil.copy2(p, target)
            assert sha(target) == digest
            p = target
        assert str(p) not in dependencies or dependencies[str(p)] == digest, str(original)
        dependencies[str(p)] = digest
        return p

    names = ['native-actor-collision-disc-build-current.json', 'native-actor-collision-final-current.json', 'actor-collision-development-reviewed-current.json', 'actor-move-collision-contexts-current.json', 'collision-nested-reserve-negative-current.json', 'actor-collision-final-startup-current.json']
    gates = {}
    for name in names:
        p = v / name
        obj = read(p)
        bind(p)
        for name2, expected in obj['source_sha256'].items():
            bind(name2, expected)
        gates[name] = obj
    build = gates[names[0]]
    assert build['linked_component_bytes'] == 28380 and build['free_reserved_bytes'] == 164
    assert gates[names[1]]['cases'] == 5120 and len(gates[names[1]]['original_sites']) == 109
    assert gates[names[3]]['completed'] == 5120 and gates[names[3]]['max_private_depth'] == 894
    assert gates[names[4]]['standalone_cases_passed'] == 32 and gates[names[4]]['defective_joint_rejected']
    assert gates[names[5]]['cases'] == 96
    jobs, reports = {}, {}
    for label in ['candidate', 'control']:
        pointer = v / ('native-actor-collision-' + label + '-current.json')
        job = read(pointer)
        assert job['status'] == 'terminal_native_actor_collision_route_pending_review' and job['exit_code'] == 0
        assert job['returned_outdoors'] and job['live_monitor_pass'] and job['collision_execution_counts_pass']
        assert subprocess.run(['ps', '-p', str(job['child_pid']), '-o', 'command='], capture_output=True).returncode != 0
        bind(pointer)
        for p, h in job['source_sha256'].items():
            bind(p, h)
        folder = Path(job['directory']) / 'candidate'
        for filename in ['report.json', 'gameplay-observation.json', 'frontend-PCM.s16le', 'original-emulator-final-frame.png']:
            bind(folder / filename)
        report = read(folder / 'report.json')
        observation = job['observations']
        assert report['disc_sha256'] == (build['derived_disc_sha256'] if label == 'candidate' else job['control_delta']['control_sha256'])
        assert observation['ac_entries'] == observation['ac_returns']
        assert observation['ac_pending'] == observation['ac_counter_errors'] == 0
        assert observation['am_entries'] == observation['am_native_entries'] == observation['am_returns']
        assert observation['am_errors'] == observation['am_context_corruptions'] == observation['am_stack_outside'] == 0
        assert observation['ac_entries'] == [observation['am_outdoor_calls'], observation['am_indoor_calls']]
        assert report['captured_state_input'] is None and report['host_CPU_or_GPU_register_seed'] is False
        assert report['C_CPU_backend']['mode'] == 'reference'
        if label == 'candidate':
            assert observation['ac_native'] == observation['ac_entries'] and observation['ac_original_steps'] == 0
        else:
            assert observation['ac_native'] == [0, 0] and observation['ac_original_steps'] > 0
            assert job['control_delta']['restored_entries'] == ['13b5a', '13bb0'] and job['control_delta']['declared_bytes'] == 14
        jobs[label], reports[label] = job, report
    keys = ['CPU_full', 'full_RAM_sha256', 'full_GPU_state_sha256', 'full_DSP_state_sha256', 'video_sha256', 'navigation', 'locomotion_state', 'held_buttons']
    comparisons = {key: sum(a[key] != b[key] for a, b in zip(reports['candidate']['frames'], reports['control']['frames'])) for key in keys}
    pcm = {}
    for label, job in jobs.items():
        p = Path(job['directory']) / 'candidate/frontend-PCM.s16le'
        pcm[label] = dict(bytes=p.stat().st_size, sha256=sha(p))
    comparison = dict(aligned_frames=min(len(reports['candidate']['frames']), len(reports['control']['frames'])), differing_frames=comparisons, PCM=pcm, PCM_equal=pcm['candidate'] == pcm['control'], adaptive_controller_paths_may_differ=True)
    save(out / 'comparison.json', comparison)
    image = Path(jobs['candidate']['directory']) / 'candidate/original-emulator-final-frame.png'
    lines = [
        'BIWN NATIVE COLLISION — REVIEWED FRESH ROUTES',
        'The new 28,380-byte native experiment returned outdoors in both fresh runs.',
        'The candidate executed 3,868 outdoor collision calls/returns in C; the control executed 3,949 original collision calls. Indoor collision was reached zero times in both.',
        'Both keep native movement and prior compiled game functions. Control restores only the two collision entry regions (14 declared bytes); reservation, staging, heap and installed unused collision code are common.',
        'Candidate movement: 13,872 calls/returns, max nested private depth894, minimum observed task headroom40, zero movement ABI/context/task-boundary errors. Finite user/supervisor composition separately reaches24bytes headroom under a tighter synthetic root matching a prior live minimum.',
        'Collision counters prove entry/body/return ownership; full collision CPU/SR/helper/publicRAM equivalence is the separate5120case matrix and2560case movement composition. Live stack/context checks use the qualified movement monitor. Arbitrary concurrency, interrupt depth and every collision outcome are not established.',
        'Actual native emulator CPU/GPU/DSP/IRQ/platform and HLE execute these runs. No host C-processor replacement or physical console boot proof applies.',
        'Aligned state/video/navigation/PCM comparison: ' + json.dumps(comparison),
        'Different instruction costs, schedules and adaptive inputs remain material limits. Earlier inherited discrepancies are unresolved. This is not a complete readable game or same-console release.',
        'Source and original-facing ABI: coordinator adapts existing high-level portable collision C. No new local Author adoption, training or weight change.',
        'Final image: ' + str(image),
    ]
    report_path = out / 'review.txt'
    report_path.write_text('\n\n'.join(lines) + '\n')
    bind(report_path)
    bind(out / 'comparison.json')
    bind(Path(__file__))
    result = dict(status='terminal_native_actor_collision_fresh_routes_reviewed', directory=str(out), report=str(report_path), resident_bytes=28380, candidate_frames=jobs['candidate']['frames'], control_frames=jobs['control']['frames'], outdoor_calls=[3868, 3949], indoor_calls=[0, 0], candidate_movement_calls=13872, max_private_depth=894, minimum_live_headroom=40, component_minimum_headroom=24, live_monitor_pass=True, comparison=comparison, image=str(image), default_preview_promoted=False, whole_game_complete=False, new_training=False, dependencies_sha256=dependencies, scope=__doc__)
    save(out / 'protocol.json', result)
    save(v / 'actor-collision-integration-reviewed-current.json', result)
    print(json.dumps({k: result[k] for k in ['status', 'candidate_frames', 'control_frames', 'live_monitor_pass']}))


if __name__ == '__main__':
    main()
