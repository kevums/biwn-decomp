"""Publish scoped component and actual native-Chat evidence without promotion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
CHAT = Path.home()/'.lmstudio/conversations/1792337022998.conversation.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2)+'\n')


def tool_value(content):
    try:
        value = json.loads(content)
    except json.JSONDecodeError:
        value = json.loads(json.loads('"'+content+'"'))
    assert isinstance(value, list) and len(value) == 1 and value[0]['type'] == 'text'
    return json.loads(value[0]['text'])


def main():
    now = datetime.now(timezone.utc)
    out = ROOT/'verification/native-format-component-chat-review'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    dependencies = {}
    snapshots = {}

    def bind(path, snapshot=False):
        path = Path(path).resolve()
        dependencies[str(path)] = sha(path)
        if snapshot:
            target = out/'snapshots'/(hashlib.sha256(str(path).encode()).hexdigest()[:16]+'-'+path.name)
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path, target)
            assert sha(target) == dependencies[str(path)]
            snapshots[str(path)] = str(target)

    bundle_path = ROOT/'verification/native-format-bundle-current.json'
    bundle = read(bundle_path)
    expected = bundle['binary_sha256']
    bind(bundle_path, True)
    bind(bundle['binary'])
    prep_path = ROOT/'verification/native-format-component-driver-preparation-current.json'
    prep = read(prep_path)
    assert prep['binary_sha256'] == expected
    bind(prep_path, True)
    bind(prep['makefile'], True)
    for driver in prep['drivers']:
        assert sha(driver['parent']) == driver['parent_sha256']
        assert sha(driver['derived']) == driver['derived_sha256']
        bind(driver['parent'], True)
        bind(driver['derived'], True)
    matrices_path = ROOT/'verification/native-format-component-matrices-current.json'
    matrices = read(matrices_path)
    assert matrices['status'] == 'terminal_six_linked_component_matrices_pass'
    bind(matrices_path, True)
    gates = {}
    for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release']:
        path = ROOT/'verification'/f'native-format-bundle-{kind}-current.json'
        gate = read(path)
        assert gate['limit'] is None
        assert gate['compiled_binary_sha256'] == expected == sha(gate['compiled_binary'])
        assert gate['binary_bytes'] == 8742
        assert gate['status'].startswith('terminal_') and 'pass' in gate['status']
        bind(path, True)
        for artifact in Path(gate['directory']).rglob('*'):
            if artifact.is_file():
                bind(artifact)
        for table in ['source_sha256', 'execution_dependencies_sha256']:
            values = gate.get(table, {})
            if isinstance(values, dict):
                for source, digest in values.items():
                    assert sha(source) == digest, source
                    bind(source)
        gates[kind] = dict(status=gate['status'], native_cases=gate.get('native_cases', gate.get('cpu_cases')),
                           trace_cases=gate['trace_cases'], binary_bytes=gate['binary_bytes'],
                           changing_read_native_cases=gate.get('changing_read_native_cases'),
                           checker_source_accepted_flag=gate['source_accepted'],
                           coordinator_accepts_scoped_matrix=True,
                           scope=gate.get('scope', gate.get('limits')))
    # The controller's historical checker never changes source_accepted from False.
    # Preserve its raw flag; accepting its scoped matrix requires terminal status,
    # full counts and exact payload hash, all independently checked above.
    assert gates['controller']['native_cases'] == 1216 and gates['controller']['trace_cases'] == 1024
    assert gates['rng']['native_cases'] == 1682 and gates['rng']['trace_cases'] == 298
    expected_counts = {'tasks':(1280,1280),'scheduler':(1664,896),'heap':(3392,3392),
                       'copy':(3260,3260),'free':(1411,1411),'release':(768,768)}
    for kind, counts in expected_counts.items():
        assert (gates[kind]['native_cases'],gates[kind]['trace_cases']) == counts

    deck_path = ROOT/'verification/native-format-deck-pair-current.json'
    deck = read(deck_path)
    assert deck['status'] == 'terminal_fresh_format_deck_pair_classified'
    assert deck['exit_codes'] == {'candidate':0,'control':0}
    bind(deck_path, True)
    deck_review = {}
    for lane in ['candidate','control']:
        directory = Path(deck['directory'])/lane
        report_path = directory/'report.json'
        assert sha(report_path) == deck['report_sha256'][lane]
        report = read(report_path)
        observer = read(directory/'gameplay-observation.json')
        assert observer == deck['observations'][lane]
        assert observer['format_returns'] == observer['format_entries'] == [72,0]
        assert observer['format_tracking_errors'] == observer['format_pending_at_finish'] == 0
        assert observer['format_stack_outside'] == [0,0]
        assert report['executed_frames'] == 2600
        frames = report['frames']
        assert len(frames) == 2600
        assert all(x['debug_overlay_word'] == 0 and x['editor_state_word'] == 0 for x in frames)
        post = [x for x in frames if x['frame'] >= 1660]
        assert all(x['held_input_long'] == 33562624 for x in post)
        deck_review[lane] = dict(executed_frames=2600, observer=observer,
                                 editor_or_debug_word_activated=False,
                                 held_input_unchanged_after_frame=1660,
                                 movie_flag_at_1665=frames[1664]['movie_flag_words'])
        for artifact in directory.rglob('*'):
            if artifact.is_file():
                bind(artifact)
    for source, digest in deck['source_sha256'].items():
        assert sha(source) == digest
        bind(source, Path(source).suffix in ['.py','.c','.json'])

    chat = read(CHAT)
    assert chat['name'] == 'BIWN — Visible String Recovery'
    assert chat['preset'] == '@local:biwn-visible-recovery'
    assert chat['plugins'] == ['mcp/biwn-string-workbench']
    assert len(chat['messages']) == 2
    user = chat['messages'][0]['versions'][0]
    assistant = chat['messages'][1]['versions'][0]
    requests = []
    results = {}
    blocks = []
    stats = []
    statuses = []
    for step in assistant['steps']:
        if step['type'] == 'toolStatus':
            statuses.append(step['statusState']['status'])
        if step.get('genInfo'):
            info = step['genInfo']
            assert info['identifier'] == 'advertising-scholar'
            assert info['stats']['stopReason'] == 'eosFound'
            stats.append(info['stats'])
        for content in step.get('content', []):
            if content['type'] == 'toolCallRequest':
                assert content['pluginIdentifier'] == 'mcp/biwn-string-workbench'
                assert content['parameters'] == {}
                requests.append(content['name'])
            elif content['type'] == 'toolCallResult':
                assert content['name'] not in results
                results[content['name']] = tool_value(content['content'])
            elif content['type'] == 'text':
                blocks.append(content['text'])
    assert requests == ['get_biwn_string_task','lift_biwn_string_task']
    assert len(statuses) == 2 and all(x['type'] == 'toolCallSucceeded' for x in statuses)
    assert len(stats) == 3
    lifted = results['lift_biwn_string_task']
    assert lifted['status'] == 'verified_exact_native_string_source'
    assert lifted['source_sha256'] == sha(lifted['source'])
    assert lifted['generated_source'] == Path(lifted['source']).read_text()
    assert lifted['fresh_CPU_tests_run_in_this_call'] is False
    final = blocks[-1]
    assert lifted['source'] in final and 'reused' in final and 'no fresh CPU tests' in final
    assert '1945 native' in final and '16 changing-read' in final and '36/36' in final
    preset_path = Path.home()/'.lmstudio/config-presets/BIWN Visible Recovery.preset.json'
    preset = read(preset_path)
    fields = {x['key']:x['value'] for x in preset['operation']['fields']}
    assert fields['llm.prediction.contextOverflowPolicy'] == 'stopAtLimit'
    assert fields['llm.prediction.temperature'] == 0
    bind(CHAT, True)
    bind(preset_path, True)
    bind(lifted['source'])
    bind(lifted['gate_receipt'], True)
    chat_proof = dict(status='terminal_actual_native_Chat_string_recovery_verified',
                      chat_name=chat['name'], live_conversation=str(CHAT),
                      immutable_conversation=snapshots[str(CHAT)],
                      model='advertising-scholar', actual_weights='Qwen3_5 27B6bit',
                      context_length=32768, temperature=0, reasoning_enabled=False,
                      tool_requests=requests, tool_statuses=statuses, inference_stats=stats,
                      source=lifted['source'], source_sha256=lifted['source_sha256'],
                      native_cases=1945, stable_ordered_cases=1945, changing_read_cases=16,
                      instruction_coverage=[36,36],
                      C_origin='deterministic_typed_IR_lifter_not_LLM_author',
                      fresh_CPU_tests_run_in_Chat=False,
                      prior_exact_CPU_receipt_reused=True,
                      UI_observation='CUA observed enabled bounded MCP, two calls, full final response, named chat and saved preset. No imported assistant response.',
                      saved_preset=str(preset_path), context_overflow_now='stopAtLimit',
                      context_overflow_during_first_test='truncateMiddle; single test used42percent of32K context, no truncation observed',
                      independent_LLM_agents=1, new_training=False, whole_game_complete=False)
    save(out/'native-Chat-proof.json', chat_proof)
    save(ROOT/'verification/native-string-native-Chat-current.json', chat_proof)
    user_prompt = ''.join(c.get('text','') for c in user['content'])
    (out/'exact-prompts-and-response.txt').write_text(
        'Coordinator: Codex operated LM Studio UI and deterministic checkers.\n'
        'Local LLM role: recovery Coordinator on the shared27B6bit base; no C Author role in this call.\n'
        'Tool roles: validated fact retrieval, typed-IR re-lowering and exact prior receipt reuse.\n'
        'Verifier: retained CPU/native ABI and separate ordered-access checks; no LLM judgment used to pass matrices.\n\n'
        'SYSTEM PROMPT\n'+fields['llm.prediction.systemPrompt']+'\n\nUSER PROMPT\n'+user_prompt+
        '\n\nEXACT ASSISTANT TEXT\n'+'\n'.join(blocks)+'\n\n'
        'Full tool arguments/results and model stats are in the immutable conversation snapshot.\n')

    prior_path = ROOT/'verification/native-format-integration-publication-current.json'
    prior = read(prior_path)
    changed = []
    for source, digest in prior['dependencies_sha256'].items():
        if sha(source) != digest:
            changed.append(source)
    assert not changed, changed
    bind(prior_path, True)
    bind(Path(__file__), True)
    bind(ROOT/'scripts/run_native_format_component_matrices.py', True)
    bind(ROOT/'scripts/prepare_native_format_component_gates.py', True)
    summary = dict(status='terminal_scoped_component_and_native_Chat_review_published',
                   recorded_at=now.isoformat(), directory=str(out), gates=gates,
                   deck_experiment=deck_review, deck_string_helper_exercised=False,
                   frame_equivalent=False, timing_vs_algorithm_cause_resolved=False,
                   native_Chat=chat_proof, exact_prompts=str(out/'exact-prompts-and-response.txt'),
                   prior_integration_dependencies_unchanged=len(prior['dependencies_sha256']),
                   all_affected_component_matrices_and_lifecycles_complete=False,
                   default_preview_promoted=False, physical_console_verified=False,
                   new_training=False, whole_game_complete=False, goal_complete=False,
                   dependencies_sha256=dependencies, source_snapshots=snapshots)
    save(out/'review.json', summary)
    save(ROOT/'verification/native-format-component-chat-review-current.json', summary)
    report = ROOT/'reports/native-format-components-and-visible-Chat.txt'
    lines = ['The new8742byte experimental build passes eight scoped linked component matrices.',
             'Fresh native CPU/ordered matrix cases (each number is a comparison case, not a function count):']
    for kind, gate in gates.items():
        lines.append(f"  {kind}: {gate['native_cases']} native CPU; {gate['trace_cases']} ordered-access.")
    lines += ['', 'Free additionally replays declared changing reads through native CPU; all per-gate limits remain in the receipts.',
              'Controller checker retains its historical source_accepted=false flag; the review separately verifies its terminal pass, full1216/1024 counts and exact linked bytes.',
              '', 'LM Studio Chat: BIWN — Visible String Recovery.',
              'The actual local model called both configured MCP tools once, then reported the exact checked source and1945/1945+16 checks with36/36 instruction coverage.',
              'Those CPU checks were reused from the exact bound receipt. C came from the deterministic typed-IR lifter. This is not a new model-authored decompilation or training run.',
              'Saved native preset: BIWN Visible Recovery. Context overflow now stops at the limit. The first test used42% of32K context.',
              'To watch: open the named chat in LM Studio. To repeat in a new chat: load the model, select the preset, enable biwn-string-workbench, and submit the saved user prompt. Tool approval was saved for only that bounded two-tool server.',
              '', 'Deck experiment:2600fresh HLEboot frames per lane. Both lanes return from padding72times; string0times. No observed stack violation; candidate minimum observed padding stack headroom650bytes, control742bytes.',
              'The editor/debug words never activate; the guest held-input word remains unchanged from1660 despite later ordinary frontend input. The Deck/debug route is therefore not validated. Both lanes show this limitation.',
              'Candidate/control differ in193video frames; timing/IRQ versus semantic cause unresolved. No default promotion.',
              '', 'Remaining: exact-build acquisition/loader/readiness/lifecycle integration, live string coverage, frame differences, broader gameplay/audio, physical-console rebuild, reliable local C authorship/training and broader advertising quality.',
              'Future256GB hardware remains untested. Advertising daily27Bbase/model/workflows remain available; prior same-weight reviewers missed scientific issues, so broad research reliability is not claimed.',
              '', 'Exact roles/prompts/responses: '+str(out/'exact-prompts-and-response.txt'),
              'Complete review: '+str(out/'review.json')]
    report.write_text('\n'.join(lines)+'\n')
    ledger_path = ROOT/'verification/goal-continuation-current.json'
    ledger = read(ledger_path)
    save(out/'prior-goal-state.json', ledger)
    ledger.update(status='active_eight_linked_component_matrices_and_visible_native_Chat_verified_full_goal_incomplete',
                  recorded_at=now.isoformat(),
                  previous_turn_classification='No goal implementation in the preview-controls clarification; revalidated pending Deck process as terminal and ran the next independent matrices.',
                  this_turn_classification='progress', native_Chat_verified=True,
                  native_Chat_proof=str(ROOT/'verification/native-string-native-Chat-current.json'),
                  latest_component_review=str(ROOT/'verification/native-format-component-chat-review-current.json'),
                  goal_complete=False, next_actions=[
                      'Revalidate acquisition/loader/readiness and full lifecycles on exact8742byte linked payload.',
                      'Diagnose shared Deck/debug activation failure; obtain live string-helper coverage with repairs explicitly declared where required.',
                      'Resolve formatter frame differences before any default promotion.',
                      'Continue reliable local source authorship/training and advertising evidence/education quality checks.',
                      'Finish whole-game/source-console rebuild and test future hardware when available.'])
    # Finite jobs in this publication are terminal. Do not carry stale child PIDs forward.
    ledger['latest_finite_job_status'] = matrices['status']
    ledger['latest_finite_jobs_running'] = []
    save(ledger_path, ledger)
    with (ROOT/'runs/agent-work-audit.jsonl').open('a') as log:
        log.write(json.dumps(dict(time=now.isoformat(), event='eight_exact_linked_matrices_and_actual_native_Chat_published',
                                 coordinator='Codex', local_LLM_role='recoveryCoordinator(shared27B6bit)',
                                 actual_MCP_calls=requests, C_origin='deterministic_typed_IR_lifter',
                                 prompts=str(out/'exact-prompts-and-response.txt'), proof=str(out/'review.json'),
                                 native_Chat=True, training_updates=0, default_promoted=False,
                                 whole_game_complete=False))+'\n')
    print(json.dumps(dict(status=summary['status'], report=str(report), directory=str(out),
                          bound_files=len(dependencies), native_Chat_verified=True), indent=2))


if __name__ == '__main__':
    main()
