"""Compare saved equal-frame replays; never substitute for complete-route fidelity."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha

FIELDS = ['video_sha256', 'raw_player_X', 'raw_player_Z', 'scene_word',
          'player_mode_word', 'tile_word', 'equipped_word', 'movie_flag_words',
          'held_buttons', 'CPU_full', 'full_GPU_state_sha256',
          'full_DSP_state_sha256', 'active_actor_snapshot']


def differences(a, b, fields=FIELDS):
    assert len(a) == len(b)
    result = {}
    for key in fields:
        assert all((key in x) == (key in y) for x, y in zip(a, b)), key
        rows = [x['frame'] for x, y in zip(a, b) if x.get(key) != y.get(key)]
        result[key] = dict(count=len(rows), first_frame=rows[0] if rows else None,
                           recorded_pairs=sum(key in x for x in a))
    return result


def main():
    out = V/'scene17-fixed-prefix-review-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    deps = [Path(__file__)]
    runs, frames = {}, {}
    for profile in ['wait', 'direct-poll']:
        for lane in ['candidate', 'control']:
            key = profile+'-'+lane
            pointer = V/f'scene17-{profile}-fixed-prefix-v2-{lane}-current.json'
            state = read(pointer)
            assert state['status'] == 'terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance'
            assert sha(state['report']) == state['report_sha256']
            for path, digest in state['source_sha256'].items():
                assert sha(path) == digest, path
            schedule = read(state['schedule'])
            assert sha(state['schedule']) == state['schedule_sha256']
            report = read(state['report'])
            assert len(report['frames']) == 1000
            assert [dict(frame=x['frame'], buttons=x['navigation']['buttons']) for x in report['frames']] == schedule
            frames[key] = report['frames']
            runs[key] = dict(pointer=str(pointer), report=state['report'],
                             schedule_sha256=state['schedule_sha256'],
                             live_GPU_slots=[i for i, x in enumerate(state['boundary']['active']) if x],
                             raw_arena_errors=state['raw_arena_errors_retained'],
                             pre_finish_arena_errors=state['boundary']['pre_finish_arena_errors'],
                             independently_checked_region_errors=state['boundary']['region_errors'])
            deps += [pointer, Path(state['report']), Path(state['schedule']), *map(Path, state['source_sha256'])]
    assert len({x['schedule_sha256'] for x in runs.values()}) == 1
    baseline_pointer = V/'native-scene17-wait-fresh-v2-control-current.json'
    baseline = read(baseline_pointer)
    original = read(baseline['report'])['frames'][:1000]
    assert len(original) == 1000
    # The earlier ordinary-route report predates actor snapshot recording.
    baseline_fields = [x for x in FIELDS if x != 'active_actor_snapshot'] + ['full_RAM_sha256']
    baseline_replay = differences(original, frames['wait-control'], baseline_fields)
    assert not any(x['count'] for x in baseline_replay.values()), baseline_replay
    controls = differences(frames['wait-control'], frames['direct-poll-control'])
    assert not any(x['count'] for k, x in controls.items() if k != 'CPU_full'), controls
    control_CPU_differences = [dict(frame=x['frame'], wait=x['CPU_full'], direct_poll=y['CPU_full'])
                               for x, y in zip(frames['wait-control'], frames['direct-poll-control'])
                               if x['CPU_full'] != y['CPU_full']]
    comparisons = {profile: differences(frames[profile+'-candidate'], frames[profile+'-control']) for profile in ['wait', 'direct-poll']}
    deps += [baseline_pointer, Path(baseline['report'])]
    result = dict(status='terminal_fixed_input_measurements_reviewed_fidelity_unresolved', directory=str(out),
                  frames_per_lane=1000, runs=runs, comparisons=comparisons,
                  control_observations=controls, control_CPU_differences=control_CPU_differences,
                  prior_control_replay=baseline_replay,
                  direct_poll_resolves_video_difference=False,
                  new_predictions=0, new_training=False, installed_preview_changed=False,
                  scope='Identical frontend buttons at each frame. Controls match video, GPU/DSP state and selected gameplay fields across the two layouts. Full control CPU state differs at frame181 in the N flag; raw states are preserved, no CPU identity claim. The v23 control replay matches prior CPU/video/full RAM hashes. Actor snapshots are periodic. Candidate video differs first at frame549 in both variants before the first held-input sample difference600. Direct polling alone does not resolve this prefix. End-of-prefix live GPU calls remain recorded, all fences independently checked; this is not route completion or whole-game, IRQ, audio or physical-console fidelity.',
                  source_sha256={str(p):sha(p) for p in dict.fromkeys(deps)})
    save(out/'review.json', result)
    save(V/'scene17-fixed-prefix-review-v1-current.json', result)
    print(result['status'], comparisons, flush=True)


if __name__ == '__main__':
    main()
