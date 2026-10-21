"""Review the saved local question about connected loading/creation/movie/world and remaining captures."""
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
    raw = Path(read(ROOT / 'verification/easy-continuous-loading-movie-world-scope-pointer.json')['directory'])
    protocol = read(raw / 'protocol.json')
    assert protocol['status'] == 'completed_pending_coordinator_review'
    item = protocol['results'][0]
    assert not item['quality_flags'] and item['words'] < 150
    assert all(s['stats']['stopReason'] == 'eosFound' for s in item['prediction_stats'])
    checkpoint = read(ROOT / 'verification/continuous-loading-movie-world-checkpoint.json')
    assert checkpoint['retained_trigger_movie_post_dialogue_context']
    assert not checkpoint['intermediate_trigger_capture_or_peripheral_reset']
    assert checkpoint['source_next_boundary'] == '0xef88'
    # Coordinator checks the exact unedited answer against the saved source
    # comparison, including all supplied capture/task/device/clock categories.
    assert checkpoint['animation_after_dialogue_verified'] and checkpoint['movement_after_dialogue_verified']
    assert checkpoint['source_post_dialogue_scheduler_yield_verified']
    assert all(t in item['answer'] for t in ['ready-merchant','187','125','12','earlier startup','EE20','Full boot','unverified'])
    assert not checkpoint['ready_merchant_capture_supplied'] and checkpoint['earlier_startup_capture_supplied']
    assert checkpoint['source_loading_creation_coldinit_connected']
    semantic = ('Correct removal of ready-merchant capture, source loading/task reuse/creation/coldinit/movie/world '
                'continuity and explicit remaining earlier startup capture/fullboot/playability limits. '
                'Names controlled entry/pose/near-player/startup/CD/BIOS/clock/synchronous GPU providers. '
                'Provider summary omits task quiescence and the emulated button sequence/specific8-unit clock step; '
                'accepted for core source/capture/scope facts, not a complete provider inventory. '
                'No general reliability or native Chat claim.')
    item['semantic_review'] = semantic
    protocol['status'] = 'accepted_core_scope_with_provider_summary_limit'
    save(raw / 'protocol.json', protocol)
    root = plistlib.loads(subprocess.check_output(['ioreg', '-a', '-n', 'Root', '-d', '1']))
    roots = root if isinstance(root, list) else [root]
    states = [s.get('CGSSessionScreenIsLocked') for r in roots for s in r.get('IOConsoleUsers', []) if isinstance(s, dict)]
    now = datetime.now(timezone.utc)
    out = ROOT / 'verification/continuous-loading-movie-world-inference-review' / now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    files = [raw / 'protocol.json', raw / 'prompts-and-responses.txt',
             ROOT / 'verification/continuous-loading-movie-world-MCP-check.json',
             ROOT / 'verification/continuous-loading-movie-world-checkpoint.json',
             ROOT / 'scripts/test_continuous_loading_movie_world_chat_scope.py',
             ROOT / 'scripts/check_continuous_loading_movie_world_mcp.py',
             Path(__file__), ROOT / 'chat_tools.py']
    manifest = []
    for p in files:
        target = out / p.name
        shutil.copy2(p, target)
        manifest.append(dict(source=str(p), snapshot=str(target), sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    review = dict(recorded_at=now.isoformat(), status=protocol['status'], directory=str(out),
                  model=protocol['model'], interface=protocol['interface'], words=item['words'],
                  seconds=item['seconds'], quality_flags=[], coordinator_semantic_review=semantic,
                  complete_provider_disclosure=False, screen_locked=any(x is True for x in states) if states else None,
                  native_Chat_verified=False, new_training=False, model_defaults_changed=False,
                  broader_reliability_established=False, whole_goal_complete=False, files=manifest)
    save(out / 'review.json', review)
    save(ROOT / 'verification/continuous-loading-movie-world-inference-review.json', review)
    note = ('LATEST LOCAL QUESTION — CONNECTED LOADING/CREATION/MOVIE/WORLD\n' + now.isoformat() + '\n\n'
            'The everyday 27B 6-bit model answered in 83 words / 19.80 seconds using one project_evidence call. '
            'Both prediction rounds ended naturally; no mechanical output flags. Coordinator accepted the source '
            'continuation facts and remaining earlier capture/fullboot limits for this scoped question. Provider summary omits task quiescence/buttons/specific8-unit clock step; complete inventory remains in the source checkpoint. Same 32K context '
            'and one worker; no weights/default changes. SDK tested; native Chat and general reliability remain unverified.\n\n'
            'USER PROMPT\n' + protocol['questions'][0]['user'] + '\n\nEXACT LOCAL ANSWER\n' + item['answer'] + '\n\n'
            'EXACT PROMPTS, TOOL CALLS AND RESPONSES\n' + str(out / 'prompts-and-responses.txt') + '\n\n'
            'REVIEW\n' + str(out / 'review.json') + '\n\n')
    p = ROOT / 'CURRENT LOCAL INFERENCE.txt'
    p.write_text(note + p.read_text())
    p = ROOT / 'START HERE.txt'
    p.write_text('Latest test: earlier startup capture plus controlled doorway/stairs312->313->314 now drive source '
                 'loading/task reuse/creation/NPC coldinit directly into187-frame125-enqueue movie and12 world/NPC/renderer '
                 'cycles with two idles. No ready-merchant capture, intermediate CPU/GPU/DSP reset or standalone frame RAM '
                 'clear.6 loading transfers349804 bytes/35 loading handoffs;14 world polls total (2 before/12 after) and '
                 '60 postmovie handoffs match original snapshots. Earlier startup/controlled entries/poses/world-loop restore '
                 'and input/task/CD/BIOS/clock/GPU completion providers remain. Fullboot/globalclocks/remaining tasks/branches/physicalscanout/gameplay unverified.\n'
                 'Local question:83 words /19.80 seconds, accepted core scope/capture facts. Provider summary omitted '
                 'task quiescence/buttons/specific8-unit step; full details preserved in checkpoint. No training/default '
                 'changes or general reliability claim. SDK tested; visible native Chat remains unverified.\nAudit: '
                 +str(out)+'\n\n'+p.read_text())
    (out / 'readable-results.txt').write_text(note)
    print(json.dumps({k: review[k] for k in ['directory', 'status', 'seconds', 'complete_provider_disclosure', 'screen_locked']}))


if __name__ == '__main__':
    main()
