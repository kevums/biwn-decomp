"""Install the reviewed Reader43; preserve all game gates and raw failed trials."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    rp = V/'copied-Reader43-reviewed-v1-current.json'; r = read(rp)
    assert r['complete_requested_briefing_approved'] and r['words'] == 99
    for path, digest in r['source_sha256'].items(): assert sha(path) == digest, path
    wp = V/'native-Deck-current-status-v1-current.json'; w = read(wp)
    for path, digest in w['dependencies_sha256'].items(): assert sha(path) == digest, path
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = V/'Reader43-current-delivery-v1'/stamp; out.mkdir(parents=True)
    p = read(w['packet']); save(out/'before-packet.json', p)
    baseline = p['latest_native_candidate']; pending = p['pending_native_candidate']
    assert baseline['native_record_returns'] == 4777 and not pending['default_promoted']
    assert not pending['final_matrix_video_comparison_pass']
    p['previous_copied_Reader_before43'] = p['current_copied_Reader_progress']
    p['previous_default_Reader_before43'] = p['current_default_Reader_progress']
    scope = ('One ordinary copied-model prediction on the supplied v34 baseline/v37 failed matrix gate snapshot;99 words,two paragraphs. '
             'Facts,byte units,artifact distinction and unresolved causality pass. Warm CLI18.94s firsttext/25.18s complete,generation8.27s. '
             'Not cold-load,GUI click,native Chat,heldout quality or training gain. Preview and all game acceptance gates unchanged.')
    p['current_copied_Reader_progress'] = dict(status=r['status'], directory=r['directory'], report=r['report'],
        review=str(rp), actual_predictions=1, seconds=8.27, words=99, max_words=150, word_limit_pass=True,
        CLI_start_to_first_text_seconds=18.94, CLI_start_to_completion_seconds=25.18,
        required_current_numeric_facts_correct=True, supplied_snapshot_factual_claims_approved=True,
        artifact_type_error=False, artifact_type_pass=True, code_authorship_statement_present=True,
        complete_requested_briefing_approved=True, current_source_reply_verified=True,
        current_source_factual_claims_reviewed=True, provided_candidate_profile='v34',
        provided_source_profile='v37', latest_source_changed_since_last_prediction=False,
        broader_quality_approved=False, quality_approved=False, new_training=False, optimizer_updates=0,
        trained_adapter_used=False, native_Chat_display_verified=False, model_identifier=r['model_identifier'],
        ordinary_launcher_verified=True, default_reader_version=43, default_reader_prepared=True,
        default_reader_generation_verified=True, scope=scope)
    p['current_default_Reader_progress'] = dict(status=r['status'], version=43, prepared=True,
        current_evidence_preflight_verified=True, Root_and_copied_evidence_preflight_verified=False,
        actual_prediction_verified=True, new_predictions=1, new_training=False, native_Chat_verified=False,
        entry=str(P/'workbench/portable_biwn.py'), script=str(P/'workbench/scripts/run_deck_status_live_v43.py'), scope=scope)
    p['current_reader_failed_trials'] = []
    deps = {str(Path(__file__)):sha(__file__), str(rp):sha(rp), **r['source_sha256']}
    for version in [41,42]:
        receipt = V/f'copied-Reader{version}-rejected-v1-current.json'; trial = read(receipt)
        assert trial['status'].startswith('terminal_')
        p['current_reader_failed_trials'].append(dict(version=version,status=trial['status'],receipt=str(receipt),adopted=False))
        deps[str(receipt)] = sha(receipt)
        deps.update(trial.get('source_sha256',{}))
    p['checked_current_summary'] += ' Ordinary copied Reader43 passes supplied-snapshot facts/byte units/causal scope and format at99words;warm CLI18.94s firsttext,25.18s complete,generation8.27s. Earlier Reader41/42 failures preserved;not weighttraining or broadquality.'
    p['checked_answer'] = p['checked_current_summary']; p['recorded_at'] = datetime.now(timezone.utc).isoformat()
    save(out/'current-status-packet.json', p)
    deps.update({str(x):sha(x) for x in out.iterdir() if x.is_file()})
    entry = ROOT/'scripts/portable_biwn_entry_v23.py'
    for source in [ROOT/'scripts/run_deck_status_live_v43.py', entry]:
        deps[str(source)] = sha(source); clone(source, P/'workbench/scripts'/source.name)
    clone(P/'workbench/portable_biwn.py', out/'before-portable_biwn.py')
    clone(entry, P/'workbench/portable_biwn.py'); assert sha(entry) == sha(P/'workbench/portable_biwn.py')
    deps[str(out/'before-portable_biwn.py')] = sha(out/'before-portable_biwn.py')
    for path, digest in deps.items():
        source = Path(path); assert source.is_relative_to(ROOT), source
        assert sha(source) == digest, source
        clone(source, P/'workbench'/source.relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w); clone(wp,P/'workbench/verification'/wp.name)
    save(V/'Reader43-current-delivery-v1-current.json',dict(status='terminal_reviewed_Reader43_installed_delivery_checks_pending',
         directory=str(out), new_predictions_in_delivery=0,new_training=False,native_Chat_verified=False))
    print('Reviewed Reader43 installed;v34 baseline and failed v37 matrix gate preserved.',flush=True)


if __name__ == '__main__': main()
