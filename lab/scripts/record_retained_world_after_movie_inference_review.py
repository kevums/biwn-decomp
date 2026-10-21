"""Review the saved local question about retained movie-to-world/input task cycles after a routing repair."""
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
    raw = Path(read(ROOT / 'verification/easy-retained-world-after-movie-scope-pointer.json')['directory'])
    protocol = read(raw / 'protocol.json')
    assert protocol['status'] == 'completed_pending_coordinator_review'
    item = protocol['results'][0]
    assert not item['quality_flags'] and item['words'] < 150
    assert all(s['stats']['stopReason'] == 'eosFound' for s in item['prediction_stats'])
    checkpoint = read(ROOT / 'verification/retained-world-after-movie-checkpoint.json')
    assert checkpoint['retained_trigger_movie_post_dialogue_context']
    assert not checkpoint['intermediate_trigger_capture_or_peripheral_reset']
    assert checkpoint['source_next_boundary'] == '0xef88'
    # Coordinator checks the exact unedited answer against the saved source
    # comparison, including all supplied capture/task/device/clock categories.
    assert checkpoint['animation_after_dialogue_verified'] and checkpoint['movement_after_dialogue_verified']
    assert checkpoint['source_post_dialogue_scheduler_yield_verified']
    assert all(t in item['answer'] for t in ['Twelve','12 emulated input polls','60 scheduler handoffs','42400','42398','15 quiescent','8-unit','cannot boot and play'])
    assert checkpoint['source_world_iterations']==checkpoint['source_renderer_iterations']==checkpoint['source_NPC_iterations']==12
    semantic = ('Correct latest after-movie world/input/NPC/renderer/idle counts, source handoffs and player coordinates. '
                'Material initial capture, controlled inputs/quiescence/startup/disc/BIOS/clock/synchronous GPU categories disclosed. '
                'Correctly preserves boot/global clocks/remaining tasks/other branches/physical scanout/playability limits. '
                'Same-question replay after source routing repair; prior stale answer remains rejected. '
                'No general reliability or native Chat claim.')
    item['semantic_review'] = semantic
    protocol['status'] = 'accepted_for_scoped_question'
    save(raw / 'protocol.json', protocol)
    root = plistlib.loads(subprocess.check_output(['ioreg', '-a', '-n', 'Root', '-d', '1']))
    roots = root if isinstance(root, list) else [root]
    states = [s.get('CGSSessionScreenIsLocked') for r in roots for s in r.get('IOConsoleUsers', []) if isinstance(s, dict)]
    now = datetime.now(timezone.utc)
    out = ROOT / 'verification/retained-world-after-movie-inference-review' / now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    files = [raw / 'protocol.json', raw / 'prompts-and-responses.txt',
             ROOT / 'verification/retained-world-after-movie-MCP-check.json',
             ROOT / 'verification/retained-world-after-movie-checkpoint.json',
             ROOT / 'scripts/test_retained_world_after_movie_chat_scope.py',
             ROOT / 'scripts/check_retained_world_after_movie_mcp.py',
             Path(__file__), ROOT / 'chat_tools.py', ROOT/'verification/stale-world-after-movie-inference-rejection.json']
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
                  broader_reliability_established=False, whole_goal_complete=False, targeted_world_status_routing_repair_verified=True, prior_stale_answer_rejected=True, files=manifest)
    save(out / 'review.json', review)
    save(ROOT / 'verification/retained-world-after-movie-inference-review.json', review)
    note = ('LATEST LOCAL QUESTION — WORLD AND INPUT TASKS CONTINUE AFTER MOVIE\n' + now.isoformat() + '\n\n'
            'The everyday 27B 6-bit model answered in 89 words / 13.43 seconds using one project_evidence call. '
            'Both prediction rounds ended naturally; no mechanical output flags. Coordinator accepted the source '
            'continuation facts and complete supplied-provider disclosure for this scoped question. Same 32K context '
            'and one worker; no weights/default changes. SDK tested; native Chat and general reliability remain unverified.\n\n'
            'USER PROMPT\n' + protocol['questions'][0]['user'] + '\n\nEXACT LOCAL ANSWER\n' + item['answer'] + '\n\n'
            'EXACT PROMPTS, TOOL CALLS AND RESPONSES\n' + str(out / 'prompts-and-responses.txt') + '\n\n'
            'REVIEW\n' + str(out / 'review.json') + '\n\n')
    p = ROOT / 'CURRENT LOCAL INFERENCE.txt'
    p.write_text(note + p.read_text())
    p = ROOT / 'START HERE.txt'
    p.write_text('Latest test: source movie187 frames/125 audio enqueues then12 world/NPC/renderer cycles with both '
                 'idle contexts,12 emulated input polls and60 scheduler handoffs on retained state. Player X12832 unchanged; '
                 'Z42400 to42398. Source camera/targeting and repeated GPU movement/rendering execute. No intermediate device reset or '
                 'geometry GPU reseed. Initial ready capture, controlled input/task/clock/disc/BIOS/GPU completion providers and '
                 '15 quiescent contexts remain. Fullboot/globalworld timing/remaining branches/physicalscanout/gameplay unfinished.\n'
                 'Local question first failed: older world phase counts reported as current. Source status/world_input_rendering '
                 'routing now leads with latest checkpoint. Same-question replay:89 words /13.43 seconds, accepted scoped facts; '
                 'first answer preserved/rejected. No weights/default/training changes or general reliability claim. '
                 'SDK tested; visible native Chat remains unverified.\nAudit: '+str(out)+'\n\n'+p.read_text())
    (out / 'readable-results.txt').write_text(note)
    rejected=read(ROOT/'verification/stale-world-after-movie-inference-rejection.json');failure=Path(rejected['raw_directory'])
    for name in ['protocol.json','prompts-and-responses.txt']:shutil.copy2(failure/name,out/('rejected-'+name))
    save(out/'rejected-transcript-hashes.json',{name:hashlib.sha256((out/('rejected-'+name)).read_bytes()).hexdigest() for name in ['protocol.json','prompts-and-responses.txt']})
    print(json.dumps({k: review[k] for k in ['directory', 'status', 'seconds', 'complete_provider_disclosure', 'screen_locked']}))


if __name__ == '__main__':
    main()
