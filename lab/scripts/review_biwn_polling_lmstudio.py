"""Run sequential, separately prompted local roles on a bounded BIWN polling issue."""
import fcntl
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lab


def main():
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    current = json.loads((session / 'observed-call-entries-summary.json').read_text())
    export = Path(current['directory']) / 'export'
    for name in ['manifest.json', 'decompiled.c', 'listing.asm']:
        assert lab.sha(export / name) == current['artifact_sha256']['export/' + name]
    listing = '\n'.join(line for line in (export / 'listing.asm').read_text().splitlines()
                        if line[:8].isalnum() and line.startswith('0000e0') and int(line[:8], 16) >= 0xe098)
    source = (export / 'decompiled.c').read_text()
    begin = source.index('/* Address 0000e0a6 */')
    end = source.index('/* Address 0000e19e */', begin)
    evidence = [{'source': str(export / 'listing.asm'), 'chunk': 1, 'sha256': lab.sha(export / 'listing.asm'), 'text': listing},
                {'source': str(export / 'decompiled.c'), 'chunk': 1, 'sha256': lab.sha(export / 'decompiled.c'), 'text': source[begin:end]},
                {'source': 'coordinator-observations', 'chunk': 1,
                 'text': 'Current Ghidra imported stage spans0x4000..0x100000; external addresses0xf03200..0xf0321f are not imported as volatile memory. Original instruction bytes are retained; no physical hardware or rebuilt game has been validated. A separate-copy annotation experiment can map external memory as uninitialized volatile; its result is not known yet.'}]
    task = ('Analyze the mismatch between original instructions at0xe0a6..0xe0f0 and the supplied automatic C. '
            'Give one bounded hypothesis and a concrete reversible Ghidra annotation experiment, with verification criteria. '
            'Preserve initial/final calls to0xe098 and the repeated external-memory test at0xe0de; distinguish a polling loop from proven permanent nontermination. '
            'Do not invent device behavior, original symbols, ABI, executed fixes or hardware validation. Under150words.')
    out = ROOT / 'runs' / (lab.stamp() + '-game-polling-review')
    out.mkdir()
    request = {'task': task, 'evidence': evidence, 'model': 'local/advertising-qwen38',
               'interface': 'LM Studio localhost API; authorized post review while locked',
               'roles': ['analyst', 'restorer', 'reviewer'], 'fresh_context_per_role': True,
               'dependencies': 'Analyst/restorer receive original evidence independently; reviewer sees evidence plus both drafts. Same weights, correlated errors.'}
    (out / 'request.json').write_text(json.dumps(request, indent=2) + '\n')
    print(out, flush=True)
    lab.CONFIG['models']['game'] = lab.CONFIG['models']['advertising'].copy()
    results, transcript = [], ['BIWN POLLING — LOCAL ROLES', json.dumps(request, indent=2)]
    with (ROOT / 'runs/.inference.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        loaded = json.loads(subprocess.run([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'], cwd=Path.home() / '.lmstudio', check=True, capture_output=True, text=True).stdout)
        assert len(loaded) == 1 and loaded[0]['identifier'] == 'advertising-scholar' and loaded[0]['status'] == 'idle'
        for role in request['roles']:
            prior = '' if role != 'reviewer' else json.dumps([{'role': r['role'], 'text': r['text']} for r in results])
            result = lab.chat('game', role, task, evidence, prior, max_tokens=1200)
            results.append(result)
            (out / (role + '.json')).write_text(json.dumps(result, indent=2) + '\n')
            transcript.extend(['\nROLE: ' + role, 'SYSTEM:\n' + result['request']['system_prompt'],
                               'INPUT:\n' + result['request']['input'], 'RESPONSE:\n' + result['text']])
            (out / 'prompts-and-responses.txt').write_text('\n\n'.join(transcript) + '\n')
            (out / 'status.json').write_text(json.dumps({'status': 'running' if role != 'reviewer' else 'completed_drafts_pending_coordinator_review',
                'completed_roles': [r['role'] for r in results], 'quality_flags': {r['role']: r['quality_flags'] for r in results}}, indent=2) + '\n')
            print(role, result['seconds'], result['quality_flags'], flush=True)
    (ROOT / 'verification/biwn-local-polling-team.json').write_text(json.dumps({'directory': str(out), 'status': 'completed_drafts_pending_coordinator_review'}, indent=2) + '\n')


if __name__ == '__main__': main()
