"""Publish reviewed local resource answers and preserve their exact provenance."""
import hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from record_disc_camera_animation_checkpoint import samples

ROOT = Path(__file__).resolve().parents[1]
def read(path): return json.loads(path.read_text())
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    checkpoint = read(ROOT/'verification/disc-resource-cpu-checkpoint.json')
    mcp = read(ROOT/'verification/disc-resource-cpu-MCP-check.json')
    assert mcp['status'] == 'fresh_installed_actual_resource_CPU_and_disc_payload_evidence_passed'
    source = ROOT/'projects/black-ice-white-noise/restoration'
    linked = read(ROOT/'verification/biwn-disc-world-resources-checks.json')
    for name in ['biwn-resource-cpu-checks.json', 'biwn-disc-world-resources-checks.json']:
        proof = read(ROOT/'verification'/name)
        assert read(Path(proof['directory'])/'status.json')['status'] == 'terminal_pass'
        for file, digest in proof['source_sha256'].items():
            assert hashlib.sha256((source/file).read_bytes()).hexdigest() == digest
    pointer = read(ROOT/'verification/easy-disc-resources-cpu-current.json')
    protocol_path = Path(pointer['directory'])/'protocol.json'
    protocol = read(protocol_path)
    assert protocol['status'] == 'completed_pending_coordinator_review'
    reviewed = samples(protocol)
    assert len(reviewed) == 2 and [len(s['tool_calls']) for s in reviewed] == [1, 1]
    reviewed[0].update(verdict='bounded_current_resource_scope_correct', reason='Actual resource bodies and 32 verified preserved-disc payloads distinguished from four CD adapters, unproved loading switches, synchronization and game/render limits. Models here means game resource payloads, not LLM weights. About 170 words; useful but longer than an ideal quick answer.')
    reviewed[1].update(verdict='bounded_same_model_role_review_correct', reason='Accurate resource/CPU counts and unfinished scope. Queue consumer is absent from this integrated run, although separately reconstructed code exists. These two roles share weights and do not independently verify the program.')
    models = json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'), 'ps', '--json'], cwd=Path.home()/'.lmstudio', text=True))
    assert len(models) == 1 and models[0]['identifier'] == 'advertising-scholar' and models[0]['status'] == 'idle' and models[0]['queued'] == 0 and models[0]['contextLength'] == 32768
    audit = ROOT/'verification/disc-resource-cpu-review'/Path(linked['directory']).name
    audit.mkdir(parents=True, exist_ok=True)
    shutil.copy2(protocol_path, audit/'SDK-protocol.json')
    who = ('Codex authored the static resource CPU reconstruction, integration and checks. Original CPU/GPU execution and independent Unicorn CPU checks decide code acceptance; preserved-disc byte hashes check payloads. The local 27B base answered two SDK prompts, using one evidence call each. Analyst and Reviewer are sequential roles on that same model, not separate independent agents. No local-model-authored code, new training, model switch or default promotion occurred in this checkpoint. Native LM Studio Chat generation/provider adoption remains unverified; SDK logs are separate from native Chat history. No conversation files were edited.')
    corrections = [
        'The initial standalone run missed two copy-alignment instructions. Unequal alignments were added; all 506 instructions are now covered across 4,064 cases. Generated C behavior did not require repair.',
        'The partial memory integration invalidated a captured handle when real freeing ran. Acquisition and loading were then replaced with actual bodies; the invalid captured-handle fixture was not retained.',
        'The first full integration matched CPU/RAM but a Python variable shadowed actor-return logs. Renaming that variable fixed logging before the accepted 16-case run.',
        'The accepted integrated run has no resource-body scripts, 32 independently matched payloads totaling 3,080,416 bytes, and four explicit CD adapters. Equipment yields use the real scheduler; loading completion still uses an RTS adapter. Compaction is linked but unreached in this run.',
        'Two local replies passed bounded factual review, with one evidence call each and about 20 SDK-reported seconds each. This small sample does not establish general model reliability, latency or native Chat usability.'
    ]
    review = {'recorded_at': now, 'status': 'resource_CPU_disc_linkage_and_two_bounded_local_answers_passed', 'who_did_what': who, 'samples': reviewed, 'corrections': corrections, 'native_new_response_verified': False, 'native_provider_adoption_verified': False, 'new_training': False, 'default_promoted': False, 'model_idle': True, 'general_model_reliability_proved': False, 'directory': str(audit), 'payload_bytes_by_topic': mcp['payload_bytes_by_topic']}
    save(audit/'review.json', review)
    save(ROOT/'verification/disc-resource-cpu-review.json', review)
    transcript = 'RESOURCE CPU / DISC PAYLOADS — AUDIT\n\nWHO DID WHAT\n'+who+'\n\nCORRECTIONS AND LIMITS\n'+'\n'.join(corrections)+'\n\nEXACT SYSTEM / USER / TOOLS / RESPONSES\n'+json.dumps(protocol, ensure_ascii=False, indent=2)+'\n\nCOORDINATOR REVIEW\n'+json.dumps(reviewed, ensure_ascii=False, indent=2)+'\nFull goal active and incomplete.\n'
    (audit/'prompts-and-responses.txt').write_text(transcript)
    checkpoint.update(recorded_at=now, status=review['status'], local_answers_bounded_correct=2, SDK_reported_seconds=[s['SDK_reported_seconds'] for s in reviewed], known_compute_jobs='terminal', model_idle=True, new_training=False, default_promoted=False, native_new_response_verified=False, review=str(ROOT/'verification/disc-resource-cpu-review.json'), transcript=str(audit/'prompts-and-responses.txt'))
    checkpoint['evidence'] = list(dict.fromkeys(checkpoint['evidence']+['verification/disc-resource-cpu-MCP-check.json', 'verification/disc-resource-cpu-review.json', str((audit/'prompts-and-responses.txt').relative_to(ROOT))]))
    save(ROOT/'verification/disc-resource-cpu-checkpoint.json', checkpoint)
    for name in ['setup-status.json', 'current-runtime-state.json', 'everyday-inference.json', 'requirements-audit.json']:
        path = ROOT/'verification'/name
        value = read(path)
        value.update(disc_resource_cpu_checkpoint=checkpoint, disc_resource_cpu_review=review)
        if name == 'current-runtime-state.json':
            value.update(recorded_at=now, models=models, local_inference_jobs='Terminal: two bounded resource questions passed review; one evidence call and about 20 SDK seconds each. Native Chat unverified. Everyday base idle.', latest_API_ease_review=str(ROOT/'verification/disc-resource-cpu-review.json'))
        if name == 'requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']:
                    item['evidence'] = list(dict.fromkeys(item['evidence']+checkpoint['evidence']))
        save(path, value)
    summary = ('The reconstructed resource release, acquisition, freeing, allocation, loader and copy routines now execute together in the disc-scene test. All 16 cases match the original execution. They loaded 32 payloads totaling 3,080,416 bytes, each checked against the preserved disc data. The four resource-body mocks are removed. The separate CPU check passes 4,064 cases and covers all 506 instructions with 18 host guards.\n\nFour CD offset/transfer/stop/completion adapters remain. Equipment waits use the reconstructed scheduler, but loading-time task switches and resource synchronization are unfinished. Compaction is linked but was not reached in these disc cases. Rendering remains blocked and the live queue consumer is not connected. The game is not playable; rendering, remaining tasks, scene transitions, audio and full-game validation remain unfinished.\n\nTwo local assistant replies passed factual review, using one evidence call and about 20 SDK seconds each. These were local API exchanges, not newly verified native Chat messages. The everyday 27B base remains loaded at 32k context with one worker and is idle. No new training or default promotion occurred.\n')
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+summary+'\nEXACT PROMPTS, RESPONSES AND REVIEW\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n')
    note = '\nRESOURCE LOCAL INFERENCE REVIEW — '+now+'\n\n'+who+'\n\n'+summary+'\nExact exchanges: '+str(audit/'prompts-and-responses.txt')+'\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt', 'projects/black-ice-white-noise/restoration/READ ME.txt']:
        with (ROOT/name).open('a') as handle: handle.write(note)
    path = ROOT/'START HERE.txt'
    text = path.read_text()
    a = text.index('LATEST GAME RESULT\n')
    b = text.index('TRY ADVERTISING ASSISTANT\n', a)
    replacement = 'LATEST GAME RESULT\n'+summary.split('Two local assistant')[0]+'LOCAL INFERENCE RESULT\nTwo local API replies correctly described the new resource loading and remaining limits, with one evidence call and about 20 SDK seconds each. Native Chat adoption remains unverified. The model is idle; no new training/default promotion.\n\nTry: Are the four resource operations still stubs? Are models now loaded from my disc, and what is still unproved?\nHere, models means game assets, not LLM weights.\n\nExact prompts, tools, answers and reviews:\n'+str(audit/'prompts-and-responses.txt')+'\n\n'
    path.write_text(text[:a]+replacement+text[b:])
    subprocess.run([str(ROOT/'.venv/bin/python'), str(ROOT/'scripts/install_chat_runtime.py')], check=True)
    print(json.dumps({'resource_body_scripts': 0, 'disc_payloads': 32, 'local_answers_bounded_correct': 2, 'SDK_seconds': checkpoint['SDK_reported_seconds'], 'native_verified': False, 'model_idle': True, 'audit': str(audit)}))

if __name__ == '__main__': main()
