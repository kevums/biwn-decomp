"""Publish reviewed five-caller evidence and accept the saved local Reader.

Checks saved hashes; does not rerun gameplay, inference or training.
"""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V = ROOT/'verification'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2)+'\n')


def main():
    out = V/'native-Deck-current-status-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    review_path = V/'native-Deck-shared-reviewed-v4-current.json'
    review = read(review_path)
    assert review['status'] == 'terminal_fresh_five_native_Deck_callers_reviewed'
    assert len(review['installed_recovered_Deck_entries']) == 5
    assert review['remaining_hosted_only_Deck_entries'] == ['11e6c']
    # Verify the actual saved sources/results before publishing a compact packet.
    checked = dict(review['source_sha256'])
    checked.update({review['build']: review['build_sha256'], review['disc']: review['disc_sha256']})
    for name, expected in checked.items():
        assert sha(name) == expected, name
    build = read(review['build'])
    for name, expected in build['source_sha256'].items():
        assert sha(name) == expected, name
    for source, name in [(review_path, 'review.json'), (Path(review['build']), 'build.json')]:
        shutil.copyfile(source, out/name)

    reader_path = V/'Deck-status-live-v17-current.json'
    reader = read(reader_path)
    assert reader['status'] == 'terminal_streamed_local_briefing_pending_source_review'
    assert reader['format_pass'] and reader['new_predictions'] == 1
    for name, expected in reader['source_sha256'].items():
        assert sha(name) == expected, name
    # Coordinator source review: both raw fields preserve the exact current
    # returns, author, older GUI scope, video disagreement and unfinished work.
    answer = reader['answer']
    assert '18 native returns versus 18 original-geometry-control returns' in answer['completed']
    assert 'other four callers return 19 times each' in answer['completed']
    assert 'coordinator work' in answer['completed']
    assert all(x in answer['limits'] for x in ['three-caller', '19 video frames differ', 'cycle identity is unverified', '13-frame', 'original 16-frame', 'Audio/physical', 'training'])
    reader_review = dict(reader, status='terminal_v17_local_reader_source_review_accepted',
                         coordinator_review='Raw response accepted without editing. Saved local SDK stream, not an observed native Chat display.',
                         reviewed_against=str(out/'review.json'), reviewed_against_sha256=sha(out/'review.json'))
    save(out/'reader-reviewed.json', reader_review)
    save(V/'Deck-status-live-v17-reviewed-current.json', reader_review)

    report = ROOT/'reports/Five Native Deck Callers Review.txt'
    report.write_text(
        'BIWN — FIVE NATIVE DECK CALLERS\n\n'
        'The separate experimental disc now installs recovered scan, face, geometry, input and coordinate callers. '
        'The outer task at 0x11E6C remains hosted-only among the six recovered Deck callers. These six are one subsystem, not the entire game.\n\n'
        'Both the candidate and its control ran 25,007 frames from a fresh boot. '
        'Only the eight-byte geometry entry patch was restored in the control; its other four callers stayed native. '
        'The candidate returned from native geometry 18 times and the control returned from original geometry 18 times. '
        'Each of the five real original geometry helpers returned 18 times in both runs. '
        'The other four native callers returned 19 times each. All observed pending/error counters finished at zero, '
        'the Deck and GPU fences passed, and immutable native code stayed unchanged.\n\n'
        'All 5,248 component cases also pass at their deployed addresses. The retained four-caller nested matrix passes 128 cases at each address; '
        'it does not exercise geometry. Each of the input/face and coordinate/geometry alias matrices passes 128 cases at each address. '
        'There are 1,280 final-address full-CPU/full-RAM fallback checks, six startup checks, 192 heap initializations and 36 capacity checks. '
        'The exact region observer rejected 58 injected faults and the geometry watcher rejected eight isolated faults. '
        'These finite checks do not prove arbitrary suspension, reentry or interrupt safety.\n\n'
        'The 24,607 pre-trial recorded frames match after excluding the declared static RAM and stage hashes affected by the entry patch. '
        'During active play 19 video frames differ; the final video matches. Cycle identity and full-state identity are not established. '
        'The existing 13-frame restoration changes original 16-frame behavior. Original helpers, busy fallbacks, emulator and HLE dependencies remain. '
        'Full-game rebuilding, audio and physical-console fidelity remain incomplete.\n\n'
        'Geometry recovery and native integration are coordinator work. Earlier local face bridge work is retained with coordinator symbol renaming. '
        'This result does not establish a new model-authored geometry algorithm or a newly trained game model.\n\n'
        'Desktop BIWN Test Preview remains the earlier three-caller checkpoint build. The five-caller GUI has not been observed. '
        'The saved local Reader response used one prediction, streamed in 7.27 seconds and passed source review. '
        'Exact prompts, raw responses and events are saved in '+reader['directory']+'.\n\n'
        'Advertising V12 remains rejected for adoption: 128 audited updates were completed, but matched source audits scored '
        '22/24 for the base and 17/24 for the adapter. The daily base is retained; broader research and education validation remains unfinished.\n\n'
        'Experimental disc: '+review['disc']+'\nDisc SHA-256: '+review['disc_sha256']+'\n'
        'Review: '+str(out/'review.json')+'\n')
    summary = (
        'Five native Deck callers are installed in a separate reviewed experimental disc; outer task 0x11E6C remains hosted-only. '
        'Fresh candidate/control runs each cover 25,007 frames. Native geometry returns 18 times versus 18 original-geometry control returns; '
        'each of five original helpers returns 18 times and each other native caller returns 19 times. '
        'There are 19 differing video frames despite equal final video; cycle identity is unverified. '
        'Geometry integration is coordinator work. The desktop preview still uses the older three-caller checkpoint. '
        'Full readable game rebuilding, arbitrary suspension/IRQ, audio and physical-console fidelity remain unfinished. '
        'The 13-frame restoration changes original 16-frame behavior. Older C-processor tests apply only to their historical discs, not this image.')
    experimental = dict(derived_disc=review['disc'], derived_disc_sha256=review['disc_sha256'],
                        resident_bytes=review['native_code_bytes'], reserved_bytes=review['total_reservation_bytes'],
                        initial_heap_bytes=review['initial_heap_bytes'], authorship=review['authorship'])
    packet = dict(project='Black Ice/White Noise revision 23', schema_version=2,
                  status='terminal_native_geometry_status_v2_published',
                  milestone='five native Deck callers, reviewed v4', checked_current_summary=summary,
                  checked_answer=summary, report=str(report), experimental_build=experimental,
                  facts=dict(experimental_build=experimental),
                  installed_recovered_Deck_entries=review['installed_recovered_Deck_entries'],
                  remaining_hosted_only_Deck_entries=review['remaining_hosted_only_Deck_entries'],
                  gameplay_comparison={k:review[k] for k in ['candidate_frames','control_frames','ordinary_native_returns',
                    'same_layout_control_returns','same_layout_control_original_geometry_calls','geometry_observations',
                    'matching_video_frames','differing_video_frames','final_video_equal','timing_cycle_identity_verified']},
                  helper_gates={k:review[k] for k in ['component_cases','final_address_cases','fallback_ABI_cases','startup_cases',
                    'heap_initialize_cases','capacity_cases','native_region_fault_controls','geometry_watcher_fault_controls']},
                  nested_matrix_scope='128 retained four-caller cases at each address; geometry entries zero. Two separate alias pairs:128 cases each at each address.',
                  current_processors='Retained reference emulator CPU/GPU/DSP executing mixed original and compiled game code.',
                  processor_tests=[], older_source_CPU_GPU_DSP_tests_apply_to_this_disc=False,
                  local_C_authorship=review['authorship'], preview_native_Deck_callers=3, latest_image_GUI_verified=False,
                  restoration_changes_original_behavior=True, original_frames_per_group=16, restored_frames_per_group=13,
                  whole_game_complete=False, physical_console_verified=False, standalone_runtime_verified=False,
                  new_training=False, default_promoted=False, native_Chat_verified=False, goal_complete=False,
                  this_lookup_executes_game_tests=False, this_lookup_invokes_model_or_training=False,
                  remaining=['Outer Deck task11E6C native integration','Full readable game source build','Arbitrary suspension/reentry/IRQ',
                             'Timing, visual, audio and physical-console fidelity','Latest-image GUI validation','Broad accepted game and Advertising training'])
    save(out/'current-status.json', packet)
    shutil.copyfile(report, out/'review.txt')
    dependencies = [out/'current-status.json', out/'review.json', out/'build.json', out/'review.txt',
                    out/'reader-reviewed.json', Path(review['disc'])]
    state = dict(status='terminal_reviewed_five_caller_status_published', directory=str(out), packet=str(out/'current-status.json'),
                 report=str(report), source_review=str(review_path), full_source_dependencies_verified=len(checked)+len(build['source_sha256']),
                 dependencies_sha256={str(p):sha(p) for p in dependencies},
                 new_game_execution=False, new_prediction=False, new_training=False, whole_goal_complete=False)
    save(V/'native-Deck-current-status-v1-current.json', state)
    for name in ['BIWN Latest Work.txt','BIWN Latest Result.txt']:
        path=ROOT/name
        if path.exists(): shutil.copyfile(path,out/('before-'+name))
        path.write_text('BIWN CURRENT REVIEWED RESULT\n\n'+summary+'\n\nFull review: '+str(report)+'\n\nDisc: '+review['disc']+'\n')
    print(json.dumps(dict(directory=str(out),verified_source_records=state['full_source_dependencies_verified'],disc=review['disc'],reader_review='accepted'),indent=2))


if __name__ == '__main__':
    main()
