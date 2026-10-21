"""Bind the completed cache-cluster tests and retain every model attempt."""
import json
from pathlib import Path
from datetime import datetime, timezone
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def read(path):
    return json.loads(Path(path).read_text())


def main():
    verification = ROOT / 'verification'
    build_path = verification / 'native-cache-cluster-build-current.json'
    build = read(build_path)
    candidate_path = verification / 'native-cache-cluster-route-current.json'
    control_path = verification / 'native-cache-cluster-layout-control-current.json'
    candidate, control = read(candidate_path), read(control_path)
    deps = {}

    def bind(path, expected=None):
        path = Path(path).resolve()
        actual = sha(path)
        assert expected is None or actual == expected, str(path)
        assert str(path) not in deps or deps[str(path)] == actual, str(path)
        deps[str(path)] = actual

    bind(build_path)
    for field in ['derived_disc', 'derived_stage', 'patch_manifest']:
        bind(build[field], build[field + '_sha256'])
    for path, digest in build['source_sha256'].items():
        bind(path, digest)
    assert build['linked_component_bytes'] == 16872
    assert build['component_bytes'] == build['heap_bytes_reserved'] == 20480
    assert build['heap_native_and_ordered_cases'] == 3392
    assert build['entry_cases'] == 96
    assert build['installed_heap_allocation_compaction_witness']
    assert build['component_cases'] == {
        'lookup': {'stable': 1376, 'changing': 256, 'changing_full_native': True},
        'single': {'stable': 1376, 'changing': 256, 'changing_full_native': True},
        'multi': {'stable': 864, 'changing': 4, 'changing_full_native': False},
    }
    resident = Path(build['component']).read_bytes()
    bind(build['component'])
    bind(build['linked_component'])
    for part in build['components']:
        for key in ['proof', 'source', 'binary']:
            bind(part[key], part[key + '_sha256'])
        offset = part['address'] - build['resident_address']
        assert resident[offset:offset + part['bytes']] == Path(part['binary']).read_bytes()

    lanes = []
    for proof_path, lane in [(candidate_path, candidate), (control_path, control)]:
        bind(proof_path)
        assert lane['status'] == 'terminal_native_frame_acquire_route_pending_review'
        assert lane['build_proof_sha256'] == sha(build_path)
        assert lane['exit_code'] == 0 and lane['live_monitor_pass'] and lane['returned_outdoors']
        assert lane['host_guest_RAM_writes'] == lane['checkpoint_restores'] == 0
        for path, digest in lane['source_sha256'].items():
            bind(path, digest)
        directory = Path(lane['directory'])
        report_path = directory / 'candidate/report.json'
        bind(report_path, lane['report_sha256'])
        report = read(report_path)
        observations = read(directory / 'candidate/gameplay-observation.json')
        assert observations == lane['observations']
        for name in ['gameplay-observation.json', 'frontend-PCM.s16le', 'RAM-final.bin', 'state-final.bin']:
            bind(directory / 'candidate' / name)
        bind(directory / 'candidate/gameplay-events.bin')
        assert report['C_CPU_backend']['stats']['errors'] == 0
        assert observations['lookup_counts'][0] == observations['lookup_counts'][2] == 555
        assert observations['single_counts'][0] == observations['single_counts'][2] == 264
        assert observations['lookup_matches'] == 552 and observations['lookup_misses'] == 3
        assert observations['single_decrements'] == 261
        assert observations['multi_counts'] == [0] * 8
        lanes.append((lane, report))

    left, right = lanes[0][1], lanes[1][1]
    fields = ['raw_player_X', 'raw_player_Z', 'scene_word', 'player_mode_word', 'floor_word',
              'video_sha256', 'navigation', 'CPU_full', 'full_GPU_state_sha256', 'full_DSP_state_sha256']
    differences = {key: sum(a[key] != b[key] for a, b in zip(left['frames'], right['frames'])) for key in fields}
    pcm_equal = sha(Path(candidate['directory']) / 'candidate/frontend-PCM.s16le') == sha(Path(control['directory']) / 'candidate/frontend-PCM.s16le')
    model_path = verification / 'native-frame-lookup-model-reviewed-current.json'
    model = read(model_path)
    bind(model_path)
    assert model['repair_gate_pass'] and not model['raw_attempt_pass']
    assert model['raw_reviewer_missed_stride_error'] and not model['raw_local_source_edited_by_coordinator']
    transcript = ROOT / 'reports/native-cache-lookup-prompts-and-responses.txt'
    sections = []
    for title, path in [('ORIGINAL AUTHOR AND REVIEWER — FAILED STRIDE', model['raw_attempt']),
                        ('ONE AUTHOR REPAIR AND REVIEWER — PASSED COMPONENT GATES', model['repair'])]:
        folder = Path(path).parent
        for p in folder.iterdir():
            if p.is_file():
                bind(p)
        sections.append(title + '\n\n' + (folder / 'prompts-and-responses.txt').read_text())
    transcript.write_text('\n\n'.join(sections))
    bind(transcript)
    now = datetime.now(timezone.utc)
    out = verification / 'native-cache-cluster-reviewed' / now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    report_path = ROOT / 'reports/native-cache-cluster.txt'
    report_path.write_text(
        'BIWN — NATIVE CACHE CLUSTER\n' + now.isoformat() + '\n\n'
        'The experimental disc now composes complete native 68000 lookup, frame acquisition, single/group reference release and resource-table initialization routines with the prior native code. '
        'The resident code uses 16,872 bytes in a 20,480-byte reservation; the heap floor rises by 4KB. This is a mixed original/new game, not a whole-game source rebuild.\n\n'
        'CHECKED BUILD\n'
        'At the final installed addresses: lookup 1,376 stable + 256 changing-tag cases; single release 1,376 stable + 256 changing-reference cases; group release 864 stable full CPU/RAM cases + four ordered-access changing-read cases. '
        'Group changing-read cases do not have a full native CPU comparison. Existing acquisition 631 normal + 192 zero-divisor cases, table initialization 192 cases, raised-heap 3,392 cases, startup 96 cases and an installed allocation/compaction witness passed. '
        'Private scratch stack and code exclusions, fixture dependencies and IRQ/fault limits remain as declared by each component proof.\n\n'
        'FRESH GAMEPLAY\n'
        f'Candidate: {candidate["frames"]:,} frames. Same-layout original-three-entry control: {control["frames"]:,} frames. Both completed merchant/media/outdoor navigation. '
        'Each observed 555 lookup calls (552 matches/three misses), 264 single releases (261 decrements), 116 acquisition returns and one table initialization. All live register/cache/public-stack checks passed. '
        'Candidate lookup and single-release private depth was 24 bytes each; acquisition retained 88 bytes minimum task-stack headroom. No group-release calls occurred; its live gameplay behavior remains unverified. '
        f'The candidate/control compared prefix is {min(candidate["frames"], control["frames"]):,} frames, with {differences["video_sha256"]:,} differing video frames. PCM bytes equal: {pcm_equal}. '
        'The control restores only lookup/single/group entry points; acquisition, table initialization and the 20KB layout remain compiled. Timing, route, video and audio differences persist. This does not isolate a defect or establish exact whole-game equivalence. No whole-game speedup, physical audio/console boot or default promotion is claimed.\n\n'
        'WHO DID WHAT\n'
        'Local Qwen3.5 27B base: four actual inference calls—Author, Reviewer, one repair Author, Reviewer. The first C draft used a two-byte stride instead of four; the Reviewer missed it. '
        'The original-CPU checker exposed the concrete wrong read. The repair Author changed the complete source to use four-byte records, and the resulting scalar C file was accepted without coordinator C edits. '
        'Codex coordinator supplied the contract, ABI wrapper, compiler wiring, checker, diagnostic, other recovered routines, disc integration and live observer. Reviewer agreement is not independent validation. '
        'No weights were updated and this task differs from the earlier three-function training comparison.\n\n'
        'EXACT PROMPTS / RAW RESPONSES\n' + str(transcript) + '\n\n'
        'Native LM Studio Chat display remains unverified; the latest UI attempt timed out. The existing interactive preview was not restarted.\n'
    )
    bind(report_path)
    bind(Path(__file__))
    result = dict(status='terminal_native_cache_cluster_build_and_two_live_routes_reviewed_with_differences',
                  recorded_at=now.isoformat(), directory=str(out), report=str(report_path), transcript=str(transcript),
                  build=str(build_path), build_sha256=sha(build_path), candidate=str(candidate_path), control=str(control_path),
                  candidate_frames=candidate['frames'], control_frames=control['frames'], compared_prefix_frames=min(candidate['frames'], control['frames']),
                  same_layout_candidate_control_differences=differences, same_layout_PCM_equal=pcm_equal,
                  group_release_gameplay_reached=False, local_model_predictions=4, new_training=False,
                  native_Chat_verified=False, default_promoted=False, whole_game_complete=False,
                  physical_console_verified=False, dependencies_sha256=deps)
    save(out / 'protocol.json', result)
    save(verification / 'native-cache-cluster-reviewed-current.json', result)
    print(json.dumps({k: result[k] for k in ['status', 'candidate_frames', 'control_frames', 'same_layout_PCM_equal', 'same_layout_candidate_control_differences']}), flush=True)


if __name__ == '__main__':
    main()
