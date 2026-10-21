"""Bind the current local status workflow and its actual MCP/model evidence."""
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reference_mcp_bridge import ReferenceBridge


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2)+'\n')


def main():
    now = datetime.now(timezone.utc)
    out = ROOT/'verification/current-biwn-status-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    current = ROOT/'verification/current-biwn-status-reader-current.json'
    state = read(current)
    assert state['status'] == 'terminal_local_current_status_pending_review'
    assert state['answer_review_flags'] == [] and len(state['calls']) == 1
    assert len(state['answer'].split()) < 180
    with ReferenceBridge() as bridge:
        actual = bridge.call('project_evidence', {'topic':'status'})
        assert actual == state['calls'][0]['result']
        metadata = bridge.metadata
    assert actual['experimental_build']['declared_resident_redirects'] == 25
    assert actual['experimental_build']['resident_bytes'] == 9042
    assert actual['long_route_delay_frames'] == 4816
    assert not any(actual[k] for k in ['whole_game_complete', 'whole_game_speedup_demonstrated',
                                       'physical_console_verified', 'physical_audio_or_quality_verified',
                                       'frame_equivalent', 'default_promoted', 'new_training'])
    regression = read(ROOT/'verification/current-status-regression-current.json')
    assert regression['score']['earned_points'] == '3.25'
    assert regression['score']['maximum_points'] == '5'
    assert len(regression['references']['evidence']) == 2
    assert regression['string_result']['verified']
    assert not regression['string_result']['fresh_CPU_tests_run_in_this_call']
    rejection = read(ROOT/'verification/current-status-integrity-rejection.json')
    assert rejection['changed_bound_artifact_rejected'] and not rejection['older_status_fallback_served']
    # Coordinator read the entire raw answer against the actual returned facts.
    # This is a grounded development explanation, not a held-out coding eval.
    state.update(coordinator_review_pending=False,
                 coordinator_review='accepted_scoped_grounded_status_explanation',
                 review_scope='Reviewed complete raw answer against exact tool response. No source edits, new game tests, authorship or training claim.')
    save(Path(state['directory'])/'protocol.json', state)
    save(current, state)
    first = ROOT/'runs/current-biwn-status-20261018T163753.921975Z'
    prior = read(first/'protocol.json')
    assert prior['answer_review_flags'] == ['word_limit_exceeded']
    assert len(prior['answer'].split()) == 217
    report = ROOT/'reports/current-biwn-status-workflow.txt'
    text = (
        'CURRENT BIWN LOCAL STATUS WORKFLOW\n'+now.isoformat()+'\n\n'
        'Open Desktop → Local AI Lab → Ask BIWN Candidate Status.command.\n'
        'The existing launcher now uses the current experimental publication through the actual configured LM Studio MCP server. '
        'It no longer defaults to the older native28 question. The model runs locally through the SDK; this is not native Chat generation.\n\n'
        'WHO DID WHAT\n'
        'Codex coordinator: updated the compact evidence reader, installed source/runtime copies, reviewed raw output and published this receipt.\n'
        'Local Reader: daily advertising-scholar / Qwen3_5 27B 6bit; one role using the existing weights. '
        'Two development runs, one evidence call each. First answer217words failed the180word limit; preserved. '
        'A tighter prompt produced'+str(len(state['answer'].split()))+'words in'+str(round(state['seconds'], 2))+'seconds. '
        'No independent Reviewer model or new training.\n'
        'MCP/tool: verifies all2012 bound evidence files and exact binary/CDI hashes, then returns scoped facts. '
        'The lookup does not execute CPU/gameplay tests or inspect unrelated live processes. '
        'An isolated changed-artifact test rejected corrupt evidence without returning an older milestone.\n\n'
        'WHAT THE LOCAL READER REPORTED\n'+state['answer']+'\n\n'
        'REGRESSION CHECKS\n'
        'Configured advertising MCP:2 reference results; model-proposed supplied rubric arithmetic3.25/5. '
        'This proves retrieval/arithmetic transport, not paper interpretation or grading correctness.\n'
        'Configured string MCP: exact existing checked C and1945case CPU receipt reused; source certificate unchanged. '
        'No fresh CPU test was run by this call.\n\n'
        'WATCH IN LM STUDIO\n'
        'The earlier native chats BIWN — Visible String Recovery and Advertising — Visible Research Desk remain saved. '
        'For current progress in a game chat, enable the existing local-ai-lab integration and ask: '
        'Call project_evidence with topic status once and explain the latest experimental build and its limits. '
        'That integration must be enabled in the particular chat. The last native-window inspection timed out; '
        'this publication verifies configured stdio and SDK inference, not a new visible Chat response or an already-running cached tool process.\n\n'
        'EXACT PROMPTS AND RESPONSES\n'+state['directory']+'/prompts-and-responses.txt\n'
        'First overlong response: '+str(first/'prompts-and-responses.txt')+'\n\n'
        'REMAINING FULL GOAL\n'
        'Complete source/game/platform recovery, timing fidelity, physical-console and audio verification; '
        'reliable local C authorship and advertising research/education training; future256GBhardware validation. '
        'Existing previews/model weights were not promoted. The full goal remains active.\n'
    )
    report.write_text(text)
    top = ('CURRENT LOCAL STATUS — '+now.isoformat()+'\n\n'
           'Ask BIWN Candidate Status.command now reads the latest9042byte experimental build through configured MCP. '
           'Actual local Reader: one status tool call, '+str(len(state['answer'].split()))+'words, '+str(round(state['seconds'], 2))+'seconds. '
           'Earlier217word response retained as a word-limit failure. No new weights or default preview changes. '
           'This run uses the local SDK; no new native Chat generation verified.\n'
           'Report: '+str(report)+'\nPrompts: '+state['directory']+'/prompts-and-responses.txt\n\nEARLIER RECORDS\n\n')
    guide = ROOT/'CURRENT LOCAL INFERENCE.txt'
    guide.write_text(top+guide.read_text())
    watch = ROOT/'WATCH LOCAL AGENTS.txt'
    old = watch.read_text()
    old = old.replace('This experimental result is not yet included in every legacy local status lookup. The named nativeChat demonstrations below remain scoped to their saved evidence.',
                      'The canonical project_evidence status tool and Ask BIWN Candidate Status.command now include this result. Historical topic-specific tools retain their own scopes. The named nativeChat demonstrations below remain scoped to their saved evidence.')
    watch.write_text('CURRENT PROGRESS QUESTION\nAsk BIWN Candidate Status.command runs the local Reader with current verified facts. '
                     'Prompts/responses are printed and saved. For native Chat, enable local-ai-lab in a game chat and request project_evidence(topic=status); '
                     'a fresh native-window response was not verified this continuation.\nReport: '+str(report)+'\n\n'+old)
    deps = {}
    snapshots = {}

    def bind(path, snapshot=False):
        path = Path(path).resolve()
        deps[str(path)] = sha(path)
        if snapshot:
            target = out/'snapshots'/(hashlib.sha256(str(path).encode()).hexdigest()[:16]+'-'+path.name)
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path, target)
            snapshots[str(path)] = str(target)

    publication = ROOT/'verification/native-optimized-format-publication-current.json'
    for path, expected in read(publication)['dependencies_sha256'].items():
        assert sha(path) == expected, path
        deps[path] = expected
    for name in ['native_format_evidence.py', 'chat_tools.py', 'reference_mcp_bridge.py',
                 'scripts/ask_biwn_current_status.py', 'scripts/publish_current_biwn_status.py',
                 'Ask BIWN Candidate Status.command', 'CURRENT LOCAL INFERENCE.txt', 'WATCH LOCAL AGENTS.txt',
                 'verification/current-biwn-status-reader-current.json',
                 'verification/current-status-regression-current.json', 'verification/current-status-integrity-rejection.json']:
        bind(ROOT/name, True)
    runtime = Path.home()/'.lmstudio/local-ai-lab'
    for name in ['chat_tools.py', 'native_format_evidence.py']:
        assert sha(ROOT/name) == sha(runtime/name)
        bind(runtime/name, True)
    bind(Path.home()/'.lmstudio/mcp.json', True)
    bind(publication, True)
    bind(report, True)
    for folder in [Path(state['directory']), first, Path(regression['directory'])]:
        for path in folder.rglob('*'):
            if path.is_file():
                bind(path, True)
    proof = dict(status='terminal_current_local_status_MCP_and_Reader_review_published',
                 recorded_at=now.isoformat(), directory=str(out), report=str(report),
                 actual_fresh_MCP=metadata, exact_return_matches_reviewed_model_evidence=True,
                 publication_evidence_files_verified=actual['evidence_files_verified'],
                 model_runs=2, current_model_seconds=state['seconds'], current_model_words=len(state['answer'].split()),
                 first_run_rejection='217words exceeds180word limit', raw_final_answer_accepted_unchanged=True,
                 current_answer_review='Scoped grounded status explanation only; not a held-out benchmark.',
                 advertising_retrieval_and_rubric_transport_verified=True, string_certificate_unchanged=True,
                 native_Chat_generation_verified_this_continuation=False,
                 native_UI_observation='LM Studio getApp timed out after120.603seconds',
                 deterministic_game_tests_started_this_continuation=False, new_training=False,
                 default_promoted=False, whole_game_complete=False, goal_complete=False,
                 dependencies_sha256=deps, snapshots=snapshots)
    save(out/'report.json', proof)
    save(ROOT/'verification/current-biwn-status-publication-current.json', proof)
    ledger = ROOT/'verification/goal-continuation-current.json'
    goal = read(ledger)
    save(out/'goal-before.json', goal)
    goal.update(status='active_current_local_status_MCP_and_inference_verified_full_goal_incomplete',
                recorded_at=now.isoformat(), previous_goal_turn_classification='no_progress_on_full_goal_controls_answer_only',
                current_goal_turn_classification='progress',
                current_goal_turn_progress='Installed current compact canonical status, verified configured MCP and two local Reader outputs, retained initial word-limit failure; advertising and exact string-tool regression pass.',
                current_goal_turn_evidence=str(ROOT/'verification/current-biwn-status-publication-current.json'),
                latest_current_status_workflow=str(report), latest_local_inference=state['directory'],
                native_Chat_this_continuation=False, new_training=False, whole_game_complete=False, goal_complete=False,
                next_actions=['Diagnose the optimized outdoor-exit delay using actual navigation/actor/scene evidence.',
                              'Verify the current status response in native LM Studio Chat when UI access works.',
                              'Continue source/platform recovery, fidelity and physical console/audio checks.',
                              'Improve local authorship and advertising research/education training with representative source-grounded evaluation.'])
    save(ledger, goal)
    with (ROOT/'runs/agent-work-audit.jsonl').open('a') as stream:
        stream.write(json.dumps(dict(time=now.isoformat(), action='current_status_workflow_published',
                                     coordinator='source/runtime evidence and launcher update, deterministic checks, raw-output review',
                                     local_roles=['Reader'], local_model_runs=2, independent_reviewer=False,
                                     new_training=False, native_Chat_verified=False, proof=str(ROOT/'verification/current-biwn-status-publication-current.json')))+'\n')
    print(json.dumps({k:proof[k] for k in ['status', 'report', 'model_runs', 'current_model_seconds', 'current_model_words']}))


if __name__ == '__main__':
    main()
