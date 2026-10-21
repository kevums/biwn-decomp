"""Save scoped audio/native Chat evidence without changing conversations or weights."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    now = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup = ROOT / 'config-backups' / stamp / 'audio-native-checkpoint'
    paths = ['START HERE.txt', 'TRY ADVERTISING PILOT.txt', 'POST REVIEW.txt', 'config.json',
             'generated-models.lock.json', 'corpus/game/project-intake.json',
             *['verification/' + n for n in ['setup-status.json', 'current-runtime-state.json',
               'requirements-audit.json', 'everyday-inference.json']]]
    package_status = Path.home() / '.lmstudio/models/local/advertising-source-pilot-v1/PILOT STATUS.txt'
    for name in paths:
        dest = backup / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dest)
    shutil.copy2(package_status, backup / 'PILOT STATUS.txt')

    conversation = Path.home() / '.lmstudio/conversations/1791860011452.conversation.json'
    doc = read(conversation)
    assert doc['name'] == 'Game Assistant — Quick Start'
    selected = [m['versions'][m['currentlySelected']] for m in doc['messages']]
    assert len(selected) == 4 and selected[-1]['role'] == 'assistant'
    user, assistant = selected[-2:]
    blocks = [c for s in assistant['steps'] for c in s.get('content', [])]
    answer = '\n'.join(c['text'] for c in blocks if c['type'] == 'text')
    calls = [c for c in blocks if c['type'] == 'toolCallRequest']
    assert len(calls) == 1 and calls[0]['name'] == 'project_evidence'
    assert 'not a reconstructed build' in answer and len(answer.split()) < 80
    out = ROOT / 'verification/native-game-audio-summary' / stamp
    out.mkdir(parents=True)
    shutil.copy2(conversation, out / conversation.name)
    native = dict(recorded_at=now, status='completed_saved_native_chat_coordinator_reviewed',
                  chat=doc['name'], conversation_snapshot=str(out / conversation.name),
                  snapshot_sha256=hashlib.sha256(conversation.read_bytes()).hexdigest(),
                  prompt=user['content'], answer=answer, words=len(answer.split()), tool_calls=calls,
                  tool_results=[c for c in blocks if c['type'] == 'toolCallResult'],
                  stats=[s['genInfo']['stats'] for s in assistant['steps'] if 'genInfo' in s],
                  UI_scope='Prompt submitted through native UI; final completion read from app-saved conversation after screen locked. Final answer not visually inspected.',
                  review='Bounded pass: active DSP, zero output over observed interval, limited supplied-button result, original/emulated versus rebuilt distinction and unresolved cause retained. No whole-game or hardware validation.')
    save(out / 'review.json', native)
    save(ROOT / 'verification/native-game-audio-summary-review.json', native)
    (out / 'prompts-and-responses.txt').write_text(json.dumps(native, ensure_ascii=False, indent=2) + '\n')

    audio = read(ROOT / 'verification/biwn-audio-path-review.json')
    commands = read(ROOT / 'verification/biwn-audio-commands-review.json')
    pilot = read(ROOT / 'verification/advertising-pilot-native-chat-review.json')
    guard = read(ROOT / 'verification/advertising-native-statistical-guard-review.json')
    assert audio['status'] == 'coordinator_reviewed_zero_output_path'
    assert commands['inputs_core_unchanged']
    models = json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'), 'ps', '--json'], cwd=Path.home()/'.lmstudio', text=True))
    assert len(models) == 1 and models[0]['modelKey'] == 'local/advertising-qwen38'
    assert models[0]['status'] == 'idle' and models[0]['contextLength'] == 32768 and models[0]['parallel'] == 1
    frontend = ('Game Assistant — Quick Start is the new short native Chat. Updated Game Assistant and Advertising Assistant presets applied and tested. Fresh CPU fixture answered correctly with one tool call; sum of reported model/tool durations9.057sec, not measured user latency or a general benchmark. Native audio summary completed with one project_evidence call; final saved answer reviewed after lock. Advertising Source Pilot v1 ran three visible role prompts at32k/oneworker. Everyday27B restored idle32k/oneworker. API work while locked remains separately logged.')
    game = ('Ten isolated portable C components checked, including528 GPU-command CPU/scripted-bus fixtures and13host guards; complete reconstruction remains unfinished. Read-only900frame DSP probes show active output stores containing only zeros during game frames622–900 in HLE and assisted-BIOS stack experiments. Record counts285964/285960 are16bit bus records, not stereo sample pairs. Output ring remains zero despite nonzero gain. Supplied A/B/C presses in the bounded assisted-BIOS experiment leave framebuffer/DSP-PC/command/audio observations unchanged; no watched game-phase mailbox/stream writes. These tests narrow the mixer/command-input investigation but establish neither root cause nor absence of sound assets. Original-game emulator experiments, not rebuilt-game or hardware validation; core/CDI/BIOS unchanged.')
    advertising = ('Actual32step QLoRA pilot remains experimental. Native trained-model researcher correctly distinguished measured involvement/manipulated congruence but invented1984 for the scale: retrieved paper says1994 revised PII. Educator exceeded80words; final reviewed59word lesson meets the bounded objective/question/rubric check. Three sequential roles share one conversation/model and are not independent agents. Updated everyday statistical guard required two coordinator repairs: initial unsupported test suggestion, then unsupported claim about the paper; final36word general comparison is correct. No default promotion or broad research-accuracy claim. Two source/correction reference files added; no weight updates.')
    next_work = ('Find original producers/references for DSP mailbox F1BADC and command stream3BCE0; test additional original-game interactions and continue isolated CPU reconstruction. Broaden source-grounded advertising evaluation and improve evidence/word-limit adherence before training/promoting another model. Full goal active and incomplete.')
    evidence = ['verification/biwn-audio-path-review.json', 'verification/biwn-audio-commands-review.json',
                'verification/biwn-audio-local-review.json', 'verification/native-chat-quick-start-review.json',
                'verification/native-game-audio-summary-review.json', 'verification/advertising-pilot-native-chat-review.json',
                'verification/advertising-native-statistical-guard-review.json', 'verification/advertising-statistical-reference-addition.json']
    for name in ['setup-status.json', 'current-runtime-state.json', 'everyday-inference.json', 'requirements-audit.json']:
        path = ROOT / 'verification' / name
        value = read(path)
        if name == 'setup-status.json':
            value.update(updated_at_utc=now, game_work=game, frontend=frontend, advertising_workflow=advertising, pending=next_work)
        elif name == 'current-runtime-state.json':
            value.update(recorded_at=now, model_state_refreshed_at=now, models=models, visible_chat=frontend,
                         decomp_progress=game, advertising_progress=advertising,
                         local_inference_jobs='All known jobs terminal: native Chat tests and local audio role review completed; no background training/inference job claimed.',
                         emulator_jobs='All four new900frame audio observer/command runs terminal; inputs and core preserved.',
                         MCP_updated_evidence='Ten components and audio path/command observations; advertising corpus now7files99chunks including source correction and statistical reference.')
        elif name == 'everyday-inference.json':
            value.update(updated_at=now, frontend=frontend, model=models, model_state_refreshed_at=now,
                         screen_unlock='Native tests completed while unlocked; screen locked again at final audio answer check. File/API work continues as authorized.',
                         experimental_advertising_candidate=advertising,
                         latest_native_fixture_review=str(ROOT/evidence[3]),
                         latest_native_audio_review=str(ROOT/evidence[4]), latest_advertising_review=str(ROOT/evidence[6]),
                         latest_native_advertising_pilot=str(ROOT/evidence[5]))
        else:
            value.update(recorded_at_utc=now, previous_goal_turn_classification=value['this_goal_turn_classification'],
                         this_goal_turn_classification='progress: two DSP/audio observer runs, command A/B runs, fresh native game checks, trained pilot three native roles and reviewed everyday statistical repair',
                         next_safe_work=next_work)
            for item in value['requirements']:
                title = item['requirement']
                if 'Configure LM frontend' in title:
                    item['state'] = frontend
                elif 'decompilation test' in title:
                    item['state'] = game
                elif 'Advertising research' in title:
                    item['state'] = advertising
                else:
                    continue
                item['evidence'] = list(dict.fromkeys(item['evidence'] + evidence))
        save(path, value)
    config = read(ROOT/'config.json')
    config['chat_frontend']['game'].update(chat='Game Assistant — Quick Start', historical_chat='Game Assistant — BIWN', status=frontend+' '+game)
    config['chat_frontend']['advertising']['status'] = advertising
    config['experimental_models']['advertising_pilot'].update(status='native Chat tested32k/oneworker; source error and reviewed final lesson retained; unpromoted', native_chat='Advertising Pilot — Experimental')
    save(ROOT/'config.json', config)
    intake = read(ROOT/'corpus/game/project-intake.json')
    intake.update(latest_checked_status=game, latest_checked_at=now, latest_audio_path_review=str(ROOT/evidence[0]), latest_audio_command_review=str(ROOT/evidence[1]))
    save(ROOT/'corpus/game/project-intake.json', intake)
    (ROOT/'START HERE.txt').write_text('LOCAL AI — DAILY USE\n\n1. Open LM Studio.\n2. Choose Game Assistant — Quick Start or Advertising Assistant — Research & Teaching from Chats.\n3. Reload the last used model if needed, then ask normally. Expand tool calls to inspect evidence.\n\nTry: Where are we with Black Ice White Noise?\nTry: Using Lee & Koo (2016), was involvement measured or manipulated?\n\n'+frontend+'\n\n'+game+'\n\n'+advertising+'\n\nThe older Game Assistant — BIWN chat is preserved. For a fresh task, start a new Chat and apply the matching saved preset. Both everyday assistants use Advertising Qwen38 at32kcontext/oneworker with thinking off. Generated code and research claims still require review. Same-model roles are supervised drafting, not independent verification.\n\nWhile locked, work uses the localhost API as authorized; API requests do not appear automatically in native Chat. POST REVIEW.txt records who did what and links exact prompts/responses, failures and corrections.\n\nThe verified CDI working copy is internal. Eject SHiN TiTAN in Finder before unplugging; current work does not need it.\n\nFor the experimental trained model, see TRY ADVERTISING PILOT.txt.\n')
    guide = ROOT/'TRY ADVERTISING PILOT.txt'
    text = guide.read_text().replace('NativeAPI outputs were tested, native Chat UI interaction with this candidate is pending.', 'NativeAPI and native Chat were tested. Open Advertising Pilot — Experimental to see the three role prompts and responses. In model load settings use32768context and one worker; the picker initially used8192/four and was corrected before testing.')
    guide.write_text(text+'\nLATEST NATIVE TEST — '+now+'\n'+advertising+'\nExact native prompts/responses: '+str(Path(pilot['conversation_snapshot']).parent/'prompts-and-responses.txt')+'\nCoordinator review: '+str(ROOT/evidence[5])+'\n')
    package_status.write_text(guide.read_text())
    lock = read(ROOT/'generated-models.lock.json')
    entry = next(m for m in lock['models'] if m['path'] == str(package_status.parent))
    entry['files_sha256']['PILOT STATUS.txt'] = hashlib.sha256(package_status.read_bytes()).hexdigest()
    entry['native_chat_UI_verified'] = 'Three native role passes completed; bounded final lesson pass, researcher citation-year error and educator length failure retained.'
    lock['recorded_at'] = now
    save(ROOT/'generated-models.lock.json', lock)
    post = ROOT/'POST REVIEW.txt'
    text = post.read_text()
    text = text.replace('Fresh-chat timing and advertising preset/candidate UI checks remain pending.', 'Historical pending items completed in the later AUDIO / NATIVE CHAT checkpoint below.')
    text += '\nAUDIO / NATIVE CHAT CHECKPOINT — '+now+'\n'+game+'\n'+frontend+'\n'+advertising+'\nWHO DID WHAT: Codex wrote read-only lab observers, checked900frame streams against prior baselines, decoded observed DSP boundaries, compared mailbox/stream traces, and reviewed all outputs. Actual local analyst→reviewer used separate contexts on the same27B weights; reviewer copied analyst and both mislocated dispatch words, omitted separate run counts and exceeded160words. Their unsupported claims were rejected. Native trained pilot researcher→educator→reviewer used one conversation, with explicit role prompts; final lesson passed only after review. Everyday base statistical repair required two coordinator corrections. No Codex subagents.\n'
    for name in evidence:
        text += name+': '+str(ROOT/name)+'\n'
    text += 'Exact native pilot prompts/responses: '+str(Path(pilot['conversation_snapshot']).parent/'prompts-and-responses.txt')+'\nExact everyday advertising prompts/responses: '+str(Path(guard['conversation_snapshot']).parent/'prompts-and-responses.txt')+'\nExact native game audio prompt/tool/answer: '+str(out/'prompts-and-responses.txt')+'\nExact fresh fixture prompt/tool/answer: '+str(Path(read(ROOT/evidence[3])['conversation_snapshot']).parent/'prompts-and-responses.txt')+'\nExact local audio analyst/reviewer prompts/responses: '+str(ROOT/'runs/20261013T025056.144246Z-game-audio-path-review/prompts-and-responses.txt')+'\n'+next_work+'\nAll known compute jobs terminal at this checkpoint. Screen locked; no unlock request needed. Original sources and weights unchanged except generated pilot status documentation.\n'
    post.write_text(text)
    save(ROOT/'verification/audio-native-checkpoint.json', dict(recorded_at=now, backup=str(backup), models=models, full_goal_status='active incomplete', known_compute_jobs='terminal', evidence=evidence, next_work=next_work))
    print(json.dumps({'checkpoint':now, 'native_audio_words':len(answer.split()), 'model_status':models[0]['status'], 'backup':str(backup)}))


if __name__ == '__main__':
    main()
