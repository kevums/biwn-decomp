"""Review the saved local question about retained merchant-to-renderer continuity."""
import hashlib
import json
import plistlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())
save = lambda p, v: p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')


def main():
    raw = Path(read(ROOT / 'verification/easy-retained-merchant-renderer-scope-pointer.json')['directory'])
    protocol = read(raw / 'protocol.json')
    assert protocol['status'] == 'completed_pending_coordinator_review'
    item = protocol['results'][0]
    assert not item['quality_flags'] and item['words'] < 150
    assert all(s['stats']['stopReason'] == 'eosFound' for s in item['prediction_stats'])
    checkpoint = read(ROOT / 'verification/retained-merchant-renderer-checkpoint.json')
    assert checkpoint['retained_trigger_movie_post_dialogue_context']
    assert not checkpoint['intermediate_trigger_capture_or_peripheral_reset']
    assert checkpoint['source_next_boundary'] == '0xef88'
    # Coordinator checks the exact unedited answer against the saved source
    # comparison, including all supplied capture/task/device/clock categories.
    assert checkpoint['animation_after_dialogue_verified'] and checkpoint['movement_after_dialogue_verified']
    assert checkpoint['source_post_dialogue_scheduler_yield_verified']
    assert all(t in item['answer'] for t in ['EF88','17DCE','two queued sprites','ready-world','quiescent','file-backed','nominal','synchronous','Not yet playable'])
    assert checkpoint['renderer_after_dialogue_verified'] and not checkpoint['renderer_geometry_GPU_reset']
    semantic = ('Accurate merchant-to-renderer retained context, no geometry reseed, two source sprite commands, '
                'interior geometry/projection/draw and yield back to merchant explanation. Names the material '
                'capture/input/quiescence/startup/disc/BIOS/clock/synchronous GPU provider categories. '
                'Correctly says the game is not yet playable and retains full boot/globalworld/choices/collision/scanout/timing limits. '
                'Specific renderer unblocking and each clock event remain in the checkpoint; this is a summary, not an exhaustive schedule. '
                'Accepted for this scoped question; general reliability and native Chat remain unverified.')
    item['semantic_review'] = semantic
    protocol['status'] = 'accepted_for_scoped_question'
    save(raw / 'protocol.json', protocol)
    root = plistlib.loads(subprocess.check_output(['ioreg', '-a', '-n', 'Root', '-d', '1']))
    roots = root if isinstance(root, list) else [root]
    states = [s.get('CGSSessionScreenIsLocked') for r in roots for s in r.get('IOConsoleUsers', []) if isinstance(s, dict)]
    now = datetime.now(timezone.utc)
    out = ROOT / 'verification/retained-merchant-renderer-inference-review' / now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    files = [raw / 'protocol.json', raw / 'prompts-and-responses.txt',
             ROOT / 'verification/retained-merchant-renderer-MCP-check.json',
             ROOT / 'verification/retained-merchant-renderer-checkpoint.json',
             ROOT / 'scripts/test_retained_merchant_renderer_chat_scope.py',
             ROOT / 'scripts/check_retained_merchant_renderer_mcp.py',
             Path(__file__), ROOT / 'chat_tools.py']
    manifest = []
    for p in files:
        target = out / p.name
        shutil.copy2(p, target)
        manifest.append(dict(source=str(p), snapshot=str(target), sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    review = dict(recorded_at=now.isoformat(), status=protocol['status'], directory=str(out),
                  model=protocol['model'], interface=protocol['interface'], words=item['words'],
                  seconds=item['seconds'], quality_flags=[], coordinator_semantic_review=semantic,
                  complete_provider_disclosure=True, screen_locked=any(x is True for x in states) if states else None,
                  native_Chat_verified=False, new_training=False, model_defaults_changed=False,
                  broader_reliability_established=False, whole_goal_complete=False, files=manifest)
    save(out / 'review.json', review)
    save(ROOT / 'verification/retained-merchant-renderer-inference-review.json', review)
    note = ('LATEST LOCAL QUESTION — MERCHANT RESUMES SOURCE RENDERER\n' + now.isoformat() + '\n\n'
            'The everyday 27B 6-bit model answered in 105 words / 20.22 seconds using one project_evidence call. '
            'Both prediction rounds ended naturally; no mechanical output flags. Coordinator accepted the source '
            'continuation facts and complete supplied-provider disclosure for this scoped question. Same 32K context '
            'and one worker; no weights/default changes. SDK tested; native Chat and general reliability remain unverified.\n\n'
            'USER PROMPT\n' + protocol['questions'][0]['user'] + '\n\nEXACT LOCAL ANSWER\n' + item['answer'] + '\n\n'
            'EXACT PROMPTS, TOOL CALLS AND RESPONSES\n' + str(out / 'prompts-and-responses.txt') + '\n\n'
            'REVIEW\n' + str(out / 'review.json') + '\n\n')
    p = ROOT / 'CURRENT LOCAL INFERENCE.txt'
    p.write_text(note + p.read_text())
    p = ROOT / 'START HERE.txt'
    p.write_text('Latest test: the source merchant runs message60 movie187 frames/125 audio enqueues, then '
                 'state2/facing/animation/movement and a real task handoff into one source renderer iteration. '
                 'Two queued sprites,6AE0/6DA0 geometry,52E0 projection and57A0 draw, then source yield back to merchantEF88. '
                 'No intermediate device reset or geometry GPU reseed. Sprite full-state244 cases matched198/214 classified '
                 'instructions;16 unreached rows remain explicit. Initial ready capture, task inputs/quiescence/unblocking, '
                 'source startup and disc/clock/BIOS/synchronous GPU providers remain. Fullboot/globalworld/otherbranches/physicalscanout/gameplay unfinished.\n'
                 'Local question:105 words /20.22 seconds, accurate scoped facts and material provider categories. '
                 'New saved post-dialogue plane verified through fresh MCP. SDK tested; visible native Chat remains unverified.\nAudit: '
                 + str(out) + '\n\n' + p.read_text())
    (out / 'readable-results.txt').write_text(note)
    print(json.dumps({k: review[k] for k in ['directory', 'status', 'seconds', 'complete_provider_disclosure', 'screen_locked']}))


if __name__ == '__main__':
    main()
