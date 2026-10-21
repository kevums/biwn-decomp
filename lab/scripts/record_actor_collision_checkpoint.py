"""Freeze verified collision, connected actor work and genuine native Chat audit."""
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
    names = ['biwn-geometry-cpu-checks.json', 'biwn-actor-collision-checks.json',
             'biwn-actor-movement-collision-checks.json', 'biwn-actor-full-movement-runtime-checks.json']
    proofs = {name: read(ROOT / 'verification' / name) for name in names}
    geometry, collision, movement, actor = proofs.values()
    assert geometry['CPU_cases'] == 1024 and collision['CPU_cases'] == 4096
    assert movement['CPU_cases'] == 256 and not movement['scripted_services']
    assert actor['cases'] == 128 and actor['task_handoffs'] == 3072
    assert not actor['scripted_helpers'] and not actor['removal_TRAP2_executed']
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for proof in proofs.values():
        assert read(Path(proof['directory']) / 'status.json')['status'] in ['terminal_pass', 'terminal_pass_services_pending']
        for name, digest in proof['source_sha256'].items():
            assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    native_path = Path.home() / '.lmstudio/conversations/1791916630539.conversation.json'
    native = read(native_path)
    assert native['name'] == 'Game Assistant — Live Actor Checkpoint'
    assert native['preset'] == '@local:game-assistant-2'
    preset_path = Path.home() / '.lmstudio/config-presets/Game Assistant (2).preset.json'
    preset = read(preset_path)
    system = next(f['value'] for f in preset['operation']['fields'] if f['key'] == 'llm.prediction.systemPrompt')
    assert system.strip() == (ROOT / 'presets/Game Assistant.system.txt').read_text().strip()
    native_rows = []
    for message in native['messages']:
        version = message['versions'][message['currentlySelected']]
        if version['role'] != 'assistant':
            continue
        blocks = [c for step in version['steps'] for c in step.get('content', [])]
        calls = [c for c in blocks if c['type'] == 'toolCallRequest']
        results = [c for c in blocks if c['type'] == 'toolCallResult']
        answer = '\n'.join(c['text'] for c in blocks if c['type'] == 'text')
        assert len(calls) == len(results) == 1
        assert calls[0]['name'] == 'project_evidence'
        assert '103' in results[0]['content'] and '3072' in results[0]['content']
        stats = [s['genInfo']['stats'] for s in version['steps'] if 'genInfo' in s]
        assert stats and all(s['stopReason'] == 'eosFound' for s in stats)
        native_rows.append({'tool_calls': calls, 'answer': answer, 'generation_stats': stats})
    assert len(native_rows) == 2
    first, roles = native_rows
    assert first['tool_calls'][0]['parameters']['topic'] == 'actor_movement'
    assert all(t in first['answer'] for t in ['128-case', 'blocked', 'boundary-checked', 'not executed'])
    assert len(first['answer'].split()) < 95
    assert roles['tool_calls'][0]['parameters']['topic'] == 'actor_collision'
    assert all(t in roles['answer'] for t in ['Analyst', 'Reviewer', '0xFFFF0000'])
    assert len(roles['answer'].split()) < 110
    sdk_dir = Path(read(ROOT / 'verification/easy-actor-collision-current.json')['directory'])
    protocol = read(sdk_dir / 'protocol.json')
    question = protocol['questions'][0]
    calls = [b['toolCallRequest'] for e in question['events'] for b in e['content'] if b['type'] == 'toolCallRequest']
    assert len(calls) == 1 and calls[0]['arguments'] == {'topic': 'actor_task'}
    models = json.loads(subprocess.check_output([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'], cwd=Path.home() / '.lmstudio', text=True))
    assert len(models) == 1 and models[0]['identifier'] == 'advertising-scholar'
    assert models[0]['status'] == 'idle' and models[0]['queued'] == 0
    audit = ROOT / 'verification/actor-collision-review' / Path(actor['directory']).name
    audit.mkdir(parents=True, exist_ok=True)
    shutil.copy2(native_path, audit / 'native-conversation.json')
    shutil.copy2(preset_path, audit / 'native-preset.json')
    shutil.copy2(sdk_dir / 'protocol.json', audit / 'SDK-protocol.json')
    who = ('Codex authored the accepted C geometry/collision interfaces and comparison harnesses, and linked existing movement/navigation/RNG/GPU/scheduler code. '
           'Original CPU/GPU execution decides acceptance. The local 27B base model answered one SDK question and two genuine native Chat turns, the second containing labeled Analyst/Reviewer roles. '
           'These same-model roles are correlated, not independent agents, code authors or acceptance votes. No new training or default promotion. Native Chat was operated through the UI; its saved conversation was read and copied only for audit, never injected or edited.')
    review = {'recorded_at': now, 'status': 'SDK_and_native_scope_questions_and_native_role_example_correct',
              'who_did_what': who, 'native_chat': native['name'], 'native_conversation_path': str(native_path),
              'native_conversation_sha256': hashlib.sha256(native_path.read_bytes()).hexdigest(),
              'native_preset_identifier': native['preset'], 'native_UI_final_visible_verified': True,
              'native_prompt_and_current_evidence_adoption_verified': True, 'native_turns': native_rows,
              'SDK_reported_seconds': question['SDK_reported_seconds'], 'SDK_tool_calls': calls,
              'scope': 'Bounded evidence-grounded examples, not a general accuracy or speed benchmark. Native generation stats are per generation, not measured end-to-end latency.',
              'UI_correction': 'LM Studio cached the old Game Assistant preset. Imported the current preset through UI, chose incoming system prompt, refreshed tools, and verified current103-component evidence in actual native results.',
              'directory': str(audit)}
    save(audit / 'review.json', review)
    save(ROOT / 'verification/actor-collision-review.json', review)
    transcript = 'ACTOR COLLISION AND LIVE ACTOR CHECKPOINT\n\nWHO DID WHAT\n' + who
    transcript += '\n\nNATIVE SYSTEM PROMPT\n' + system + '\n\nNATIVE MESSAGES, EXACT CONTENT\n'
    transcript += json.dumps(native['messages'], ensure_ascii=False, indent=2)
    transcript += '\n\nSDK EXACT SYSTEM, QUESTION, TOOLS AND RESPONSE\n' + json.dumps(protocol, ensure_ascii=False, indent=2)
    transcript += '\n\nLIMITS\nSynthetic bounded geometry and synchronous GPU completion. Removal/TRAP2 not executed; actor bodies still blocked in separate21-context startup. Whole game, loading switches, remaining tasks/render/assets/scenes/audio/hardware unfinished. Full goal active.\n'
    (audit / 'prompts-and-responses.txt').write_text(transcript)
    evidence = ['verification/' + n for n in names] + ['verification/actor-collision-MCP-check.json', 'verification/actor-collision-review.json', str((audit / 'prompts-and-responses.txt').relative_to(ROOT))]
    checkpoint = {'recorded_at': now, 'published_components': 103, 'processor_components': {'CPU': 101, 'GPU': 2},
                  'geometry_CPU_cases': 1024, 'collision_CPU_cases': 4096, 'movement_connected_cases': 256,
                  'actor_runtime_cases': 128, 'actor_iterations': 1024, 'task_handoffs': 3072,
                  'helper_return_CPU_comparisons': 2671, 'actor_helper_scripts': 0,
                  'whole2MBRAM_private_stacks_and_fullCPU_compared': True, 'synthetic_scene_geometry': True,
                  'synchronous_GPU_completion': True, 'startup21_actor_bodies_executed': 0,
                  'removal_TRAP2_executed': False, 'pending_actor_caller_components': 1,
                  'native_UI': 'Verified current prompt/tools and two completed visible native Chat turns.',
                  'model_idle': True, 'known_compute_jobs': 'terminal', 'new_training': False,
                  'model_defaults_unchanged': True, 'full_goal_status': 'active incomplete', 'evidence': evidence,
                  'next_work': 'Implement and compare actual task removal/TRAP2, then connect actors with original startup/world/render/assets and remaining game systems.'}
    save(ROOT / 'verification/actor-collision-checkpoint.json', checkpoint)
    for name in ['setup-status.json', 'current-runtime-state.json', 'everyday-inference.json', 'requirements-audit.json']:
        path = ROOT / 'verification' / name
        value = read(path)
        value.update(actor_collision_checkpoint=checkpoint, actor_collision_review=review)
        if name == 'current-runtime-state.json':
            value.update(recorded_at=now, models=models, local_inference_jobs='Terminal: one SDK and two native Chat turns passed. Model idle.', emulator_jobs='Terminal: geometry1024, collision4096, complete movement256 and actor128cases/3072handoffs passed.', latest_API_ease_review=str(ROOT / 'verification/actor-collision-review.json'))
        if name == 'requirements-audit.json':
            value.update(recorded_at_utc=now, this_goal_turn_classification='Progress: real geometry/collision/movement linked to actor scheduling, count103; genuine native Chat and role exchange verified.', next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']:
                    item['evidence'] = list(dict.fromkeys(item['evidence'] + evidence))
        save(path, value)
    note = '\nACTOR COLLISION AND NATIVE CHAT CHECKPOINT — ' + now + '\n\n' + read(ROOT / 'config.json')['actor_collision_progress'] + '\n\n' + who + '\n\nExact prompts/responses/tools: ' + str(audit / 'prompts-and-responses.txt') + '\n\nNEXT\n' + checkpoint['next_work'] + '\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt', 'projects/black-ice-white-noise/restoration/READ ME.txt', 'CURRENT DECOMPILATION.txt']:
        with (ROOT / name).open('a') as handle:
            handle.write(note)
    path = ROOT / 'START HERE.txt'
    text = path.read_text().replace('Game Assistant — Memory Checkpoint or', 'Game Assistant — Live Actor Checkpoint or')
    start = text.index('LOCAL INFERENCE RESULT\n')
    end = text.index('TRY ADVERTISING ASSISTANT\n', start)
    text = text[:start] + ('LOCAL INFERENCE RESULT\nCurrent native Chat prompt and evidence tools verified. One ordinary actor scope question and a labeled Analyst/Reviewer exchange completed correctly, one evidence call each. Open Game Assistant — Live Actor Checkpoint to see both prompts and responses. Same-model roles are not independent verification. SDK sample also passed in about19seconds; this is not a general benchmark.\n\nTry: Do actors now move with real collision, and what remains before the game is finished?\n\n') + text[end:]
    path.write_text(text)
    print(json.dumps({'components': 103, 'native_chat': native['name'], 'native_turns': 2, 'model_idle': True, 'audit': str(audit)}))

if __name__ == '__main__':
    main()
