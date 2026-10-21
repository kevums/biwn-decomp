"""Record reviewed local inference and the separate actor scheduler checkpoint."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    now = datetime.now(timezone.utc).isoformat()
    proof = read(ROOT / 'verification/biwn-actor-task-runtime-checks.json')
    out = Path(proof['directory'])
    assert read(out / 'status.json')['status'] == 'terminal_pass'
    for name, digest in read(out / 'harness-snapshot/manifest.json').items():
        assert hashlib.sha256((out / 'harness-snapshot' / name).read_bytes()).hexdigest() == digest
    question_dir = Path(read(ROOT / 'verification/easy-actor-task-runtime-current.json')['directory'])
    protocol = read(question_dir / 'protocol.json')
    assert protocol['status'] == 'completed_pending_coordinator_review'
    question = protocol['questions'][0]
    answer = '\n'.join(b['text'].strip() for e in question['events'] if e['role'] == 'assistant'
                       for b in e['content'] if b['type'] == 'text' and b['text'].strip())
    calls = [b['toolCallRequest'] for e in question['events'] for b in e['content'] if b['type'] == 'toolCallRequest']
    assert len(calls) == 1 and calls[0]['arguments'] == {'topic': 'actor_task'}
    assert '3,072' in answer and 'No,' in answer and 'blocked' in answer and 'scripted' in answer
    assert 'TRAP2' in answer and len(answer.split()) <= 90
    models = json.loads(subprocess.check_output([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'],
                                               cwd=Path.home() / '.lmstudio', text=True))
    assert len(models) == 1 and models[0]['status'] == 'idle' and models[0]['queued'] == 0
    assert read(ROOT / 'verification/actor-task-runtime-MCP-check.json')['status'] == 'fresh_installed_actor_task_scheduler_evidence_passed'
    audit = ROOT / 'verification/actor-task-runtime-review' / out.name
    audit.mkdir(parents=True, exist_ok=True)
    shutil.copy2(question_dir / 'protocol.json', audit / 'ordinary-question.json')
    audit_text = ('ACTOR SCHEDULER CHECKPOINT\n\nWHO DID WHAT\n'
                  'Codex authored the actor caller and native/C comparison harness. Original emulated M68000 execution is the behavioral oracle. '
                  'No local-model code drafts or independent reviewer agents were used in this checkpoint. '
                  'The existing 27B local model answered one ordinary evidence question through LM Studio localhost SDK. '
                  'Native Chat remained locked; this transcript is separate from native Chat history.\n\n'
                  'COMMANDS\n.venv/bin/python scripts/check_biwn_actor_task_runtime.py --limit 4\n'
                  '.venv/bin/python scripts/check_biwn_actor_task_runtime.py\n'
                  '.venv/bin/python scripts/check_actor_task_runtime_mcp.py\n'
                  '.venv/bin/python scripts/test_actor_task_runtime_question.py\n\n'
                  'SYSTEM\n' + protocol['system'] + '\n\nUSER\n' + question['user'] + '\n\nTOOLS\n' +
                  json.dumps(calls, indent=2) + '\n\nANSWER\n' + answer + '\n\nLIMITS\n'
                  'The 128-case actor/two-idle scheduler proof is separate from the 21-context startup. Six helpers are scripts; '
                  'movement updates are test fixtures. Removal is unexecuted. No full game, complete AI, hardware, new training or default promotion is established.\n')
    (audit / 'prompts-and-responses.txt').write_text(audit_text)
    review = {'recorded_at': now, 'directory': str(audit), 'status': 'ordinary_actor_scheduler_scope_answer_correct_one_call',
              'question': question['user'], 'answer': answer, 'tool_calls': calls,
              'SDK_reported_seconds': question['SDK_reported_seconds'],
              'native_UI': 'CUA confirmed locked this turn; no unlock requested.',
              'scope': 'One ordinary localhost SDK question, separate from native Chat; not a general accuracy or speed benchmark.'}
    save(ROOT / 'verification/actor-task-runtime-review.json', review)
    evidence = ['verification/biwn-actor-task-runtime-checks.json', 'verification/actor-task-runtime-MCP-check.json',
                'verification/actor-task-runtime-review.json', str((audit / 'prompts-and-responses.txt').relative_to(ROOT))]
    checkpoint = {'recorded_at': now, 'published_components': 96, 'pending_actor_caller_components': 1,
                  'cases': 128, 'actor_iterations': 1024, 'scheduler_handoffs': 3072,
                  'full_CPU_stack_banks_and_whole_RAM_match': True, 'real_scheduler': True,
                  'scripted_actor_helpers': 6, 'removal_executed': False, 'startup21_actor_bodies_executed': 0,
                  'ordinary_question_correct': True, 'ordinary_question_tools': 1,
                  'model_idle': True, 'known_compute_jobs': 'terminal', 'native_UI': 'locked',
                  'new_training': False, 'model_defaults_unchanged': True, 'full_goal_status': 'active incomplete',
                  'evidence': evidence,
                  'next_work': 'Replace actor waypoint/steering/RNG/movement scripts, check full callee CPU effects, then connect actors to larger startup/world/render tests.'}
    save(ROOT / 'verification/actor-task-runtime-checkpoint.json', checkpoint)
    for name in ['current-runtime-state.json', 'requirements-audit.json', 'everyday-inference.json', 'setup-status.json']:
        path = ROOT / 'verification' / name
        value = read(path)
        value.update(actor_task_scheduler_review=review, actor_task_scheduler_checkpoint=checkpoint)
        if name == 'current-runtime-state.json':
            value.update(recorded_at=now, models=models,
                         local_inference_jobs='Terminal. One ordinary scope question passed with one evidence call; local model idle.',
                         emulator_jobs='Terminal. 128 actor/two-idle native/C cases, 1024 iterations and 3072 actual scheduler handoffs pass.',
                         latest_API_ease_review=str(ROOT / 'verification/actor-task-runtime-review.json'))
        if name == 'requirements-audit.json':
            value.update(recorded_at_utc=now,
                         this_goal_turn_classification='Progress: 128 actor/two-idle scheduler cases pass; 3072 handoffs; ordinary SDK scope answer correct with one tool call. Six helpers remain scripted; published count 96.',
                         next_safe_work=checkpoint['next_work'])
        save(path, value)
    note = ('\nACTOR SCHEDULER INTEGRATION — ' + now + '\n\n'
            '128 cases, 1024 actor iterations and 3072 real scheduler handoffs match native CPU execution. '
            'All registers, SR, USP/SSP and complete RAM including private stacks match. Six helpers remain scripts. '
            'The 21-context startup still blocks actor bodies; removal remains pending. Published count remains 96.\n\n'
            'One ordinary local evidence question passed with one actor_task tool call. SDK-reported time: ' +
            str(question['SDK_reported_seconds']) + ' seconds. This is a single sample, separate from native Chat.\n\n'
            'Exact prompts, calls, responses and responsibilities:\n' + str(audit / 'prompts-and-responses.txt') + '\n\n'
            'NEXT\n' + checkpoint['next_work'] + '\nFull goal active and incomplete.\n')
    for name in ['POST REVIEW.txt', 'projects/black-ice-white-noise/restoration/READ ME.txt']:
        with (ROOT / name).open('a') as handle:
            handle.write(note)
    path = ROOT / 'CURRENT DECOMPILATION.txt'
    text = path.read_text().replace('Native Chat is locked; local inference checks are saved separately.',
                                   'Native Chat is locked. One ordinary localhost question correctly described this result with one evidence call. Exact prompts/responses: ' + str(audit / 'prompts-and-responses.txt'))
    path.write_text(text)
    subprocess.run([str(ROOT / '.venv/bin/python'), str(ROOT / 'scripts/install_chat_runtime.py')], check=True)
    print(json.dumps({'published_components': 96, 'cases': 128, 'handoffs': 3072, 'question_tools': 1,
                      'SDK_seconds': question['SDK_reported_seconds'], 'audit': str(audit)}))


if __name__ == '__main__':
    main()
