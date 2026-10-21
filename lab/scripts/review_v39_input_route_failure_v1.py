"""Keep a failed fresh route distinct from successful finite component checks."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    out = V/'v39-input-route-failure-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    deps = {str(Path(__file__)): sha(__file__)}
    lanes = {}
    for lane in ['candidate', 'control']:
        path = V/f'native-input-arena-image-fresh-input-v1-{lane}-current.json'
        job = read(path)
        assert job['status'].startswith('terminal_') and not job.get('child_pid')
        assert not subprocess.run(['ps', '-p', str(job['pid']), '-o', 'command='], text=True, capture_output=True).stdout.strip()
        for source, digest in job['source_sha256'].items():
            assert sha(source) == digest, source
        deps.update(job['source_sha256'])
        deps[str(path)] = sha(path)
        folder = Path(job['directory'])
        observations = {p.stem: read(p) for p in (folder/'candidate').glob('*-observation.json')}
        log = folder/'runtime.log'
        rows = []
        for line in log.read_text().splitlines():
            if line.startswith('{"frame"'):
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
        assert rows
        last = rows[-1]
        same_tail = []
        for row in reversed(rows):
            if row['CPU'] != last['CPU']:
                break
            same_tail.append(row['frame'])
        scalar_bad = {}
        for name, obs in observations.items():
            scalar_bad[name] = {k: v for k, v in obs.items() if isinstance(v, (int, float)) and v and any(tag in k for tag in ['errors', 'pending', 'outside', 'corruption', 'collision'])}
        raw = (folder/'candidate/RAM-final.bin').read_bytes()
        assert len(raw) == 0x200000
        fields = {}
        for name, at, size in [('raw_player_X', 0x49c50, 4), ('raw_player_Z', 0x49c56, 4), ('scene_word', 0x49c64, 2), ('player_mode_word', 0x49c60, 2), ('floor_word', 0x49c62, 2), ('tile_word', 0x49c8c, 2), ('held_buttons', 0x49ba4, 4)]:
            fields[name] = int.from_bytes(raw[at:at+size], 'big')
        report = folder/'candidate/report.json'
        lanes[lane] = dict(status=job['status'], error=job.get('error'), directory=str(folder), exact_executed_frames=len(read(report)['frames']) if report.exists() else None, last_logged_frame=last['frame'], last_logged_CPU=last['CPU'], last_logged_CPU_state=last['CPU_full'], same_sampled_PC_tail_first_frame=min(same_tail), same_sampled_PC_tail_last_frame=max(same_tail), repeated_PC_samples=len(same_tail), sample_interval_frames=60, final_RAM_selected_fields=fields, monitor_nonzero_errors_or_pending=scalar_bad, observations=observations, report_exists=report.exists(), fresh_route_pass=job['status'] == 'terminal_fresh_scene17_route_pending_review')
        save(out/(lane+'-job.json'), job)
        save(out/(lane+'-sampled-frame-log.json'), rows)
        for p in [log, *[p for p in (folder/'candidate').iterdir() if p.is_file()]]:
            deps[str(p)] = sha(p)
    assert not lanes['candidate']['fresh_route_pass'] and lanes['control']['fresh_route_pass']
    left, right = [Path(lanes[lane]['directory'])/'candidate/video-final.xrgb8888' for lane in ['candidate', 'control']]
    a, b = left.read_bytes(), right.read_bytes()
    assert len(a) == len(b) and len(a) % 4 == 0
    pixels = sum(a[i:i+4] != b[i:i+4] for i in range(0, len(a), 4))
    comparison = dict(final_video_equal=a == b, final_differing_pixels=pixels, selected_fields_equal=lanes['candidate']['final_RAM_selected_fields'] == lanes['control']['final_RAM_selected_fields'], input_only_control=True, scene_native_in_both_lanes=True, raw_state_normalized=False, cause_resolved=False, scope='Finite fresh HLE boots; same v39 layout/scene/resource code, only six input callsite bytes restored in control. Candidate route failed. Sampled CPU addresses do not identify the first corrupting instruction; a separate diagnostic trace is required. Endpoints may have different durations. No original whole-game fidelity, full source-only build, console or successful native-input gameplay claim.')
    facts = dict(status='terminal_v39_fresh_native_input_route_failed_control_completed_cause_open', directory=str(out), candidate=lanes['candidate'], control=lanes['control'], comparison=comparison, preflight_component_checks_superseded=False, candidate_fresh_route_qualified=False, default_promoted=False, installed_preview_changed=False, new_predictions=0, new_training=False, source_sha256=deps)
    save(out/'review.json', facts)
    save(V/'v39-input-route-failure-reviewed-v1-current.json', facts)
    print(facts['status'], comparison, flush=True)


if __name__ == '__main__':
    main()
