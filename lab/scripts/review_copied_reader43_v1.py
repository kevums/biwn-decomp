"""Review the existing Reader43 result; never regenerate or rewrite its reply."""
import shutil
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha


def main():
    bp = V / 'copied-Reader43-ordinary-benchmark-v1-current.json'
    bench = read(bp)
    assert bench['status'] == 'terminal_ordinary_copied_Reader43_prediction_and_warm_CLI_timing_pending_review'
    assert bench['new_predictions'] == 1 and bench['exit_code'] == 0
    for path, digest in bench['source_sha256'].items():
        assert sha(path) == digest, path
    folder = Path(bench['run_directory']); job = read(folder / 'protocol.json')
    assert job['status'] == 'terminal_streamed_current_Reader43_pending_source_review'
    for path, digest in job['source_sha256'].items():
        assert sha(path) == digest, path
    text = (folder / 'response.txt').read_text()
    assert text == read(folder / 'response.json')['text']
    evidence = read(folder / 'evidence.json')
    baseline = evidence['current_experimental_disc']; pending = evidence['pending_native_candidate']
    assert baseline['native_record_returns'] == baseline['native_display_returns'] == 4777
    assert baseline['differing_video_frames'] == 8717 and baseline['final_video_equal']
    assert pending['new_disc_built'] and not pending['promoted']
    assert not pending['matrix_route']['baseline_final_video_gate_pass']
    assert not pending['matrix_route']['cause_resolved']
    assert evidence['connected_scene_stack_bytes'] == dict(unit='bytes', used=168, reserved=208)
    assert evidence['sampled_free_heap_bytes_while_outer_active'] == dict(candidate=14320,control=14320)
    assert not evidence['global_heap_minimum_measured']
    assert evidence['new_weight_updates'] == 0
    assert not evidence['local_coding']['latest_Author_compile_pass']
    assert not evidence['local_coding']['latest_Repair_compile_pass']
    required = ['v34', '4,777 native record/display returns', '8,717 differing video frames',
                'final video agreeing', 'remains unpromoted', 'final matrix-video gate failed',
                'different expanded poses alongside the pixel mismatch', '168 bytes', '208 bytes',
                'Sampled outer-active free heap was 14,320 bytes', 'preview is unchanged',
                'full source-only same-console rebuild is unproven', 'Coordinator authorship',
                'Latest local coding failed', 'zero new weight updates', 'base and adapter scores were 0/4 each']
    assert all(s in text for s in required)
    assert all(s not in text.lower() for s in ['due to', 'caused by', 'reserved slots', 'global minimum was'])
    assert len(text.split()) == bench['words'] == 99 and len(text.strip().split('\n\n')) == 2
    assert bench['generation_seconds'] == job['seconds'] == 8.27
    assert bench['CLI_start_to_first_text_seconds'] == 18.94
    assert bench['CLI_start_to_completion_seconds'] == 25.18
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = V / 'copied-Reader43-reviewed-v1' / stamp; out.mkdir(parents=True)
    shutil.copytree(folder, out / 'actual-run')
    shutil.copytree(bench['directory'], out / 'benchmark')
    save(out / 'benchmark-source-receipt.json', bench)
    report = ROOT / 'reports/BIWN Copied Local Reader43 Briefing Review.txt'
    report.write_text('BIWN — ordinary copied local briefing\n\n'
        'One saved actual prediction passes supplied-snapshot factual review and the requested two-paragraph/150-word format:99 words. '
        'Warm ordinary CLI:18.94 seconds to first observed text,25.18 seconds to completion;generation8.27 seconds. '
        'These timings include setup and evidence retrieval and exclude any earlier resource queue. First text is polled at100ms resolution. '
        'No cold-load,native Chat display,general quality or useful training gain is established.\n\n'
        'The reply keeps v34 as reviewed baseline and v37 as an unpromoted image whose matrix-video gate failed. '
        'It reports the correct record/display counter4777,video8717,stack168/208 bytes,and sampled outer-active free heap14320 bytes. '
        'It describes pose/pixel differences together without claiming causality. Preview unchanged,source-only same-console rebuild unproven, '
        'coordinator authorship,latest local coding failures,zero new weight updates and earlier base0/4 adapter0/4 are preserved. '
        'The sampled heap statement does not claim a global minimum.\n\n'
        'Reader41 and42 remain rejected:41 had167 words and confused scene/display counts;42 used slots for byte counts and claimed an unsupported cause. '
        'Reader43 supplies explicit units and the unresolved-causality rule. Raw responses and exact prompts are retained. '
        'The inherited transcript header says READER40;the executable,protocol,prompt and model receipt identify version43. The raw header is not rewritten.\n\n'
        'RAW RESPONSE\n' + text + '\n')
    sources = [Path(__file__), bp, report, ROOT/'scripts/run_deck_status_live_v43.py',
               ROOT/'scripts/portable_biwn_entry_v23.py', *[p for p in out.rglob('*') if p.is_file()]]
    facts = dict(status='terminal_copied_Reader43_supplied_snapshot_facts_units_causal_scope_and_format_pass',
                 directory=str(out), report=str(report), actual_predictions=1,
                 original_run_directory=str(folder), model_identifier=job['model_identifier'],
                 seconds=8.27, CLI_start_to_first_text_seconds=18.94, CLI_start_to_completion_seconds=25.18,
                 words=99, word_limit_pass=True, two_paragraphs=True, max_words=150,
                 supplied_snapshot_factual_claims_approved=True, complete_requested_briefing_approved=True,
                 artifact_type_pass=True, code_authorship_statement_present=True, stack_units_correct=True,
                 pose_causality_not_claimed=True, ordinary_copied_launcher_verified=True,
                 broader_quality_approved=False, held_out_benchmark=False, new_training=False,
                 optimizer_updates=0, native_Chat_display_verified=False,
                 source_sha256={str(p):sha(p) for p in sources})
    save(out/'review.json', facts); save(V/'copied-Reader43-reviewed-v1-current.json', facts)
    for p in [*sources, out/'review.json', V/'copied-Reader43-reviewed-v1-current.json']:
        dest = P/'workbench'/p.relative_to(ROOT); dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    print(facts['status'], '99 words;18.94s first text/25.18s complete', flush=True)


if __name__ == '__main__': main()
