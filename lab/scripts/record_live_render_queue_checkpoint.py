"""Record live render acceptance and actual SDK/native Chat observations."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from record_disc_camera_animation_checkpoint import samples

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(path.read_text())

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    checkpoint = read(ROOT / 'verification/live-render-queue-checkpoint.json')
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for name in ['biwn-render-queue-cpu-checks.json', 'biwn-disc-world-render-queue-checks.json']:
        proof = read(ROOT / 'verification' / name)
        assert read(Path(proof['directory']) / 'status.json')['status'] == 'terminal_pass'
        for filename, expected in proof['source_sha256'].items():
            assert hashlib.sha256((source / filename).read_bytes()).hexdigest() == expected
    original_path = ROOT / 'verification/easy-live-render-queue/20261013T222033.052003Z/protocol.json'
    repaired_path = ROOT / 'verification/easy-live-render-routing/20261013T222416.550154Z/protocol.json'
    original, repaired = read(original_path), read(repaired_path)
    before, after = samples(original), samples(repaired)
    assert len(before) == len(after) == 2
    assert before[1]['prompt'] == after[0]['prompt']
    before[0]['verdict'] = 'bounded_queue_scope_answer_correct'
    before[1]['verdict'] = 'rejected_image_misroute_SDK_serialization_error_and_unexecuted_tool_text'
    after[0]['verdict'] = 'bounded_same_question_role_answer_correct_after_general_routing_change'
    after[1]['verdict'] = 'explicit_frame_5_caption_correct_metadata_only_SDK_PNG_retained_separately'

    native_path = Path.home() / '.lmstudio/conversations/1791930588865.conversation.json'
    native = read(native_path)
    assert native['name'] == 'Game Assistant — Live Queue Checkpoint'
    native_samples = []
    for message in native['messages']:
        version = message['versions'][message['currentlySelected']]
        if version['role'] == 'user':
            native_samples.append({'prompt': ''.join(b.get('text', '') for b in version['content'])})
        else:
            blocks = [b for step in version['steps'] for b in step.get('content', [])]
            native_samples[-1].update(
                answer=''.join(b.get('text', '') for b in blocks if b['type'] == 'text'),
                tool_calls=[b for b in blocks if b['type'] == 'toolCallRequest'],
                generation_stats=[step['genInfo']['stats'] for step in version['steps'] if step.get('genInfo', {}).get('stats')],
            )
    assert len(native_samples) == 3 and all(s.get('answer') for s in native_samples)
    assert len(native_samples[0]['tool_calls']) == 1 and native_samples[0]['tool_calls'][0]['name'] == 'project_evidence'
    assert not native_samples[1]['tool_calls']  # Uses the current preceding evidence in the same chat.
    assert len(native_samples[2]['tool_calls']) == 1 and native_samples[2]['tool_calls'][0]['name'] == 'render_animation_preview'
    assert native_samples[2]['tool_calls'][0]['parameters'] == {'frame': 5}
    native_samples[0]['verdict'] = 'bounded_current_queue_facts_correct'
    native_samples[1]['verdict'] = 'bounded_same_model_roles_factually_correct_but_verbose_reuses_preceding_evidence'
    native_samples[2]['verdict'] = 'native_frame_5_image_and_exact_verified_caption_visible'
    assert native_samples[2]['answer'].split('\n\n')[-1].strip() == 'Reconstructed C consumed an animation request and decoded frame 5 of 72 (32×88). This is a sprite preview; the complete game is unfinished.'
    canonical = read(ROOT / 'presets/Game Assistant.preset.json')
    canonical_prompt = next(f['value'] for f in canonical['operation']['fields'] if f['key'] == 'llm.prediction.systemPrompt')
    native_prompt = next(f['value'] for f in native['perChatPredictionConfig']['fields'] if f['key'] == 'llm.prediction.systemPrompt')
    assert canonical_prompt == native_prompt
    models = json.loads(subprocess.check_output([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'], cwd=Path.home() / '.lmstudio', text=True))
    assert len(models) == 1 and models[0]['identifier'] == 'advertising-scholar'
    assert models[0]['status'] == 'idle' and models[0]['queued'] == 0 and models[0]['contextLength'] == 32768

    audit = ROOT / 'verification/live-render-queue-review/20261013T221101.626810Z'
    audit.mkdir(parents=True, exist_ok=True)
    for path, name in [(original_path, 'original-SDK.json'), (repaired_path, 'repaired-routing-SDK.json'), (native_path, 'native-conversation-read-only-snapshot.json')]:
        shutil.copy2(path, audit / name)
    image_version = native['messages'][-1]['versions'][native['messages'][-1]['currentlySelected']]
    image_result = next(b for step in image_version['steps'] for b in step.get('content', []) if b['type'] == 'toolCallResult')
    image_blocks = json.loads(image_result['content'])
    image_text = image_blocks[0]['text']
    metadata = json.loads(image_text.split('\\n\\n', 1)[1].replace('\\"', '"')) if '\\n\\n' in image_text else json.loads(image_text.split('\n\n', 1)[1])
    image_path = Path(metadata['image_path'])
    assert any(b['type'] == 'image' for b in image_blocks)
    assert hashlib.sha256(image_path.read_bytes()).hexdigest() == metadata['png_sha256']
    shutil.copy2(image_path, audit / 'native-frame-5.png')
    save(audit / 'native-frame-5-metadata.json', metadata)
    who = (
        'Codex authored the full CPU renderer/queue/mailbox/wait C, differential tests and live scene integration. '
        'Original pinned CPU/GPU execution validates full CPU, ordered bus, complete RAM, private frames and live handoffs; independent Unicorn also checks supported standalone CPU cases. '
        'The local 27B base answered through localhost SDK and the native LM Studio Chat window. Analyst and Reviewer are sequential roles on the same model, not independent agents or verification. '
        'No subagents, local-model-authored game code, new training or model/weight promotion occurred. '
        'Codex fixed the SDK image-result adapter and general explicit-image versus evidence routing, updated the saved Game Assistant prompts, then selected the incoming preset and submitted ordinary questions through the native UI. '
        'Native conversation files were read and copied only after UI creation, never injected or edited.'
    )
    limits = [
        '370 standalone cases cover all 78 instructions and 20 guards, including 320 C sprite decodes. The live 16-case scene executes 720 world updates, 2048 actor iterations, 1008 consumers and 160 C sprite decodes; all 6144 task handoffs compare full CPU state. Final queues empty.',
        'Scene draw 17E0E and overlay 181F8 remain explicit ABI-adversary scripts, each reached 1008 times. Six contexts runnable, 15 blocked. Three configured world helper scripts were not reached. Synchronous GPU completion, supplied clock/button inputs, phased startup and BIOS/completion adapters remain.',
        'Two-client resource synchronization is separately verified but not yet exercised by the 21-context game scene. Complete scene drawing, viewport/scanout, audio, uninterrupted boot, physical timing and playable full game remain incomplete.',
        'The first SDK role question misrouted to an image tool; raw MCP CallToolResult failed SDK JSON serialization, then the model emitted unexecuted tool markup. The failed exchange is preserved. The same exact question passed after a general routing change and image adapter repair.',
        'The SDK frame-5 sample retains verified PNG bytes but forwards metadata only to the model. It uses the earlier frozen 72-frame preview, not the latest live queue buffer. No SDK vision claim.',
        'Two fresh native Chat evidence/role answers and a frame-5 image request were visibly observed. The role answer reuses the preceding current evidence and is factually correct but verbose. Current system prompt adoption and live queue facts were verified. Native frame-5 preview uses the earlier frozen 72-frame resource, not the latest live buffer. Small samples do not prove general reliability or speed.',
    ]
    review = dict(recorded_at=now, status='live_queue_CPU_and_disc_checks_passed_bounded_SDK_and_native_Chat_answers_correct_game_incomplete', who_did_what=who,
                  original_SDK_samples=before, repaired_SDK_samples=after, native_samples=native_samples, limits=limits,
                  native_new_response_verified=True, native_provider_adoption_verified=True, native_preset_adoption_verified=True,
                  native_chat_name=native['name'], native_conversation_source=str(native_path), native_UI_verified=True,
                  native_image=str(audit / 'native-frame-5.png'), native_image_sha256=metadata['png_sha256'],
                  same_model_roles=True, independent_local_agents=False, general_model_reliability_proved=False,
                  new_training=False, weight_default_promoted=False, general_tool_routing_prompt_updated=True,
                  model_idle=True, directory=str(audit))
    save(audit / 'review.json', review)
    save(ROOT / 'verification/live-render-queue-review.json', review)
    transcript = 'LIVE RENDER QUEUE / LOCAL INFERENCE AUDIT\n\nWHO DID WHAT\n' + who
    transcript += '\n\nLIMITS / FAILURES RETAINED\n' + '\n'.join(limits)
    transcript += '\n\nEXACT SDK SYSTEM / USER / TOOLS / RESPONSES — ORIGINAL\n' + json.dumps(original, ensure_ascii=False, indent=2)
    transcript += '\n\nREPAIRED SDK ROUTING / IMAGE METADATA\n' + json.dumps(repaired, ensure_ascii=False, indent=2)
    transcript += '\n\nNATIVE CHAT — UI SUBMITTED, READ-ONLY FILE SNAPSHOT\nSYSTEM\n' + native_prompt + '\n' + json.dumps(native_samples, ensure_ascii=False, indent=2)
    transcript += '\n\nCOORDINATOR REVIEW\n' + json.dumps(review, ensure_ascii=False, indent=2)
    transcript += '\n\nNEXT\n' + checkpoint['next_work'] + '\nFull goal active and incomplete.\n'
    (audit / 'prompts-and-responses.txt').write_text(transcript)
    checkpoint.update(recorded_at=now, status=review['status'], native_new_response_verified=True, native_provider_adoption_verified=True,
                      native_chat_name=native['name'], local_general_reliability_proved=False, model_idle=True, known_compute_jobs='terminal',
                      new_training=False, weight_default_promoted=False, general_tool_routing_prompt_updated=True,
                      review=str(ROOT / 'verification/live-render-queue-review.json'), transcript=str(audit / 'prompts-and-responses.txt'))
    checkpoint['evidence'] = list(dict.fromkeys(checkpoint['evidence'] + ['verification/live-render-queue-MCP-check.json', 'verification/live-render-queue-review.json', str((audit / 'prompts-and-responses.txt').relative_to(ROOT))]))
    save(ROOT / 'verification/live-render-queue-checkpoint.json', checkpoint)
    routing = ROOT / 'verification/live-render-tool-routing/20261013T222415.851795Z/change.json'
    route = read(routing)
    route.update(native_Chat_adoption_verified=True, native_conversation_source=str(native_path))
    save(routing, route)
    for name in ['setup-status.json', 'current-runtime-state.json', 'everyday-inference.json', 'requirements-audit.json']:
        path = ROOT / 'verification' / name
        value = read(path)
        value.update(live_render_queue_checkpoint=checkpoint, live_render_queue_review=review)
        if name == 'current-runtime-state.json':
            value.update(recorded_at=now, models=models, local_inference_jobs='Terminal: bounded SDK and two native Chat evidence/role answers factually correct; roles verbose. Native frame-5 image/caption verified. Original failed SDK image routing retained. Everyday base idle.', latest_API_ease_review=str(ROOT / 'verification/live-render-queue-review.json'))
        if name == 'requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']:
                    item['evidence'] = list(dict.fromkeys(item['evidence'] + checkpoint['evidence']))
        save(path, value)
    summary = 'LIVE RENDER QUEUE — CURRENT CHECKPOINT\n\n' + '\n'.join(limits)
    summary += '\n\nLOCAL INFERENCE\nOpen LM Studio Chat: Game Assistant — Live Queue Checkpoint. Current evidence/role answers and a frame-5 preview are visible there. Same-model Analyst/Reviewer roles are not independent agents, and the role response is verbose. General ease/reliability is not proved by these samples. Everyday base idle; no new training or weight promotion.\n\nWHO DID WHAT / EXACT PROMPTS AND RESPONSES\n' + str(audit / 'prompts-and-responses.txt')
    summary += '\n\nNEXT\n' + checkpoint['next_work'] + '\nFull goal active and incomplete.\n'
    (ROOT / 'CURRENT DECOMPILATION.txt').write_text(summary)
    for name in ['POST REVIEW.txt', 'projects/black-ice-white-noise/restoration/READ ME.txt']:
        with (ROOT / name).open('a') as handle:
            handle.write('\n' + summary)
    path = ROOT / 'START HERE.txt'
    text = path.read_text()
    start, end = text.index('LOCAL INFERENCE RESULT\n'), text.index('TRY ADVERTISING ASSISTANT\n')
    text = text[:start] + 'LOCAL INFERENCE RESULT\nLM Studio Chat now shows current-evidence answers and frame-5 image in Game Assistant — Live Queue Checkpoint, including Analyst/Reviewer roles on one local model. The role response is factual but verbose. The live render queue passes 16 cases with 160 sprite decodes; scene draw and overlay remain stubbed, full game unfinished. Earlier SDK image routing/serialization failure retained and repaired. General image/evidence routing prompt updated; no new training or weight promotion. Everyday model idle.\n\nTry: Does the animation queue now run under the real renderer task?\n\nExact exchanges and review:\n' + str(audit / 'prompts-and-responses.txt') + '\n\n' + text[end:]
    text = text.replace('Choose Game Assistant — Disc Scene Checkpoint or Advertising Assistant — Research & Teaching.', 'Choose Game Assistant — Live Queue Checkpoint or Advertising Assistant — Research & Teaching.')
    path.write_text(text)
    print(json.dumps({'status': review['status'], 'audit': str(audit), 'native_chat': native['name'], 'model_idle': True}))

if __name__ == '__main__':
    main()
