"""Coordinator review of one bounded installed-tool question, no repair/training."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: json.loads(path.read_text())
save = lambda path, value: path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    pointer = read(ROOT / 'verification/easy-doorway-cleanup-scope-current.json')
    raw = Path(pointer['directory'])
    protocol = read(raw / 'protocol.json')
    assert protocol['status'] == 'completed_pending_coordinator_review'
    question = protocol['questions'][0]
    assert not question['response_quality_flags'] and question['rounds'] == 2 and question['answer_words'] == 50
    results = [json.loads(part['content']) for event in question['events'] for part in event['content']
               if part['type'] == 'toolCallResult']
    assert len(results) == 1
    observed = results[0]['current_standalone_doorway_boundary_cleanup']
    assert observed['cleanup_cases'] == 556 and not observed['cleanup_helpers_scripted'] and not observed['actual_scheduled_boundary_loading_verified']
    final = ''.join(part.get('text', '') for part in question['events'][-1]['content'] if part['type'] == 'text')
    # Human semantic review: all six cleanup functions/no nested helper scripts
    # is directly supported. Lack of full transition/natural entry is explicit.
    assert 'six' in final and 'unverified' in final and 'reachability' in final
    models = json.loads(subprocess.check_output([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'],
                       cwd=Path.home() / '.lmstudio', text=True))
    assert len(models) == 1 and models[0]['status'] == 'idle' and models[0]['queued'] == 0
    now = datetime.now(timezone.utc).isoformat()
    out = ROOT / 'verification/doorway-cleanup-inference-review' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    review = {'recorded_at': now, 'status': 'single_SDK_tool_answer_accepted_for_bounded_scope',
              'raw_directory': str(raw), 'interface': protocol['interface'], 'model': protocol['model'],
              'seconds': question['SDK_reported_seconds'], 'words_including_pre_tool_text': question['answer_words'],
              'response_quality_flags': [], 'final_answer': final, 'tool': 'project_evidence(cleanup)',
              'coordinator_semantic_review': 'Correctly distinguishes checked actual cleanup from unverified scheduled doorway-to-loaded-scene transition/natural reachability.',
              'prior_SDK_format_failure_fixed': False, 'general_reliability_verified': False,
              'native_Chat_verified': False, 'native_UI_observation': {'action': "cua.getApp('LM Studio')",
                  'requested_timeout_ms': 10000, 'observed_seconds': 120.6171, 'result': 'Sky Computer Use request timed out',
                  'screen_or_lock_state_observed': False, 'UI_changes_verified': False},
              'model_state': models, 'repair_generations': 0, 'weights_defaults_presets_changed': False,
              'whole_goal_complete': False}
    save(out / 'review.json', review)
    files = [raw / 'protocol.json', raw / 'prompts-and-responses.txt', ROOT / 'chat_tools.py',
             ROOT / 'scripts/test_doorway_cleanup_chat_scope.py',
             ROOT / 'scripts/record_doorway_cleanup_inference_review.py', ROOT / 'verification/doorway-cleanup-MCP-check.json']
    (out / 'snapshot').mkdir()
    for path in files:
        shutil.copy2(path, out / 'snapshot' / path.name)
    save(out / 'manifest.json', {'recorded_at': now, 'files': {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}})
    save(ROOT / 'verification/doorway-cleanup-inference-review.json', {**review, 'directory': str(out)})
    note = ('LOCAL INFERENCE — DOORWAY / CLEANUP QUESTION\n' + now + '\n\n'
            'One fresh question through the LM Studio Python SDK with the installed six scoped tools selected project_evidence(cleanup). The answer used the new evidence, returned two final sentences,50words including pre-tool text,43.38seconds and no mechanical flags; coordinator accepted its scoped facts. No repair generation,weights,preset/default changes. This single clean result does not fix the prior duplicated/thinking-tag SDK failure or establish general reliability. Native Chat remains unverified: app observation timed out after120.6171seconds despite requested10seconds, with no screen/lock state observed or UI change verified.\n\n'
            'USER PROMPT\n' + question['user'] + '\n\nFINAL LOCAL ANSWER\n' + final + '\n\n'
            'EXACT SYSTEM/USER/TOOL/RESPONSE TRANSCRIPT\n' + str(raw / 'prompts-and-responses.txt') + '\n\n'
            'STATE\n27B6bit base advertising-scholar is loaded,idle,32Kcontext,oneworker,queue0. Advertising assistant and source-reviewed lesson retained; no new training. Full goal active/incomplete.\n\nAUDIT\n' + str(out) + '\n')
    (ROOT / 'CURRENT LOCAL INFERENCE.txt').write_text(note)
    (out / 'readable-results.txt').write_text(note)
    with (ROOT / 'CURRENT DECOMPILATION.txt').open('a') as stream:
        stream.write('\n' + note)
    for name in ['config.json', 'verification/current-runtime-state.json', 'verification/everyday-inference.json']:
        path = ROOT / name
        state = read(path)
        state['doorway_cleanup_local_inference_review'] = review
        save(path, state)
    shutil.copy2(ROOT / 'config.json', Path.home() / '.lmstudio/local-ai-lab/config.json')
    print(json.dumps({'review': str(out), 'seconds': review['seconds'], 'flags': [], 'native_Chat_verified': False}))


if __name__ == '__main__':
    main()
