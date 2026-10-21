"""Review the saved local question; preserve its incomplete provider disclosure."""
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
    raw = Path(read(ROOT / 'verification/easy-retained-merchant-scope-pointer.json')['directory'])
    protocol = read(raw / 'protocol.json')
    assert protocol['status'] == 'completed_pending_coordinator_review'
    item = protocol['results'][0]
    assert not item['quality_flags'] and item['words'] < 150
    assert all(s['stats']['stopReason'] == 'eosFound' for s in item['prediction_stats'])
    checkpoint = read(ROOT / 'verification/retained-merchant-checkpoint.json')
    assert checkpoint['retained_trigger_movie_post_dialogue_context']
    assert not checkpoint['intermediate_trigger_capture_or_peripheral_reset']
    assert checkpoint['source_next_boundary'] == '0xeb04'
    # Coordinator source review: the answer accurately states the retained
    # context, state 2/facing, and unverified animation/world/firmware scope.
    # It does not explicitly name the initial ready capture, file-backed disc,
    # nominal clock, or quiescent other tasks, so disclosure is incomplete.
    semantic = ('Accurate retained-context and post-dialogue boundary explanation. '
                'Incomplete supplied-provider disclosure: initial ready-world capture, '
                'quiescent other tasks, file-backed disc and nominal clocks were omitted. '
                'Accepted only for the context/boundary facts, not a complete provider list.')
    item['semantic_review'] = semantic
    protocol['status'] = 'accepted_context_and_boundary_facts_with_provider_disclosure_limit'
    save(raw / 'protocol.json', protocol)
    root = plistlib.loads(subprocess.check_output(['ioreg', '-a', '-n', 'Root', '-d', '1']))
    roots = root if isinstance(root, list) else [root]
    states = [s.get('CGSSessionScreenIsLocked') for r in roots for s in r.get('IOConsoleUsers', []) if isinstance(s, dict)]
    now = datetime.now(timezone.utc)
    out = ROOT / 'verification/retained-merchant-inference-review' / now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    files = [raw / 'protocol.json', raw / 'prompts-and-responses.txt',
             ROOT / 'verification/retained-merchant-MCP-check.json',
             ROOT / 'verification/retained-merchant-checkpoint.json',
             ROOT / 'scripts/test_retained_merchant_chat_scope.py',
             ROOT / 'scripts/check_retained_merchant_mcp.py',
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
    save(ROOT / 'verification/retained-merchant-inference-review.json', review)
    note = ('LATEST LOCAL QUESTION — RETAINED MERCHANT CONTEXT\n' + now.isoformat() + '\n\n'
            'The everyday 27B 6-bit model answered in 75 words / 31.82 seconds using one project_evidence call. '
            'Both prediction rounds ended naturally; no mechanical output flags. Context and state 2/facing/EB04 '
            'boundary facts are accurate, but its provider list omitted the initial ready-world capture, '
            'quiescent other tasks, file-backed disc and nominal clocks. This is a scoped result with an explicit '
            'disclosure limitation, not general reliability or native Chat validation. No weights/default changes.\n\n'
            'USER PROMPT\n' + protocol['questions'][0]['user'] + '\n\nEXACT LOCAL ANSWER\n' + item['answer'] + '\n\n'
            'EXACT PROMPTS, TOOL CALLS AND RESPONSES\n' + str(out / 'prompts-and-responses.txt') + '\n\n'
            'REVIEW\n' + str(out / 'review.json') + '\n\n')
    p = ROOT / 'CURRENT LOCAL INFERENCE.txt'
    p.write_text(note + p.read_text())
    p = ROOT / 'START HERE.txt'
    p.write_text('Latest test: the source merchant retains one context through choosing message 60, '
                 '187 movie frames / 125 audio enqueues, state 2 and facing; next boundary EB04 animation. '
                 'Initial ready capture, task quiescence, disc/clock/BIOS providers and wider world/gameplay limits remain.\n'
                 'Local question: 75 words / 31.82 seconds; context/boundary facts accurate, provider disclosure incomplete. '
                 'SDK tested; visible native Chat remains unverified.\nAudit: ' + str(out) + '\n\n' + p.read_text())
    (out / 'readable-results.txt').write_text(note)
    print(json.dumps({k: review[k] for k in ['directory', 'status', 'seconds', 'complete_provider_disclosure', 'screen_locked']}))


if __name__ == '__main__':
    main()
