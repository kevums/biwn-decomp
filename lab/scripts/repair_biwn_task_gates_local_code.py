"""Typed-ABI guided local repair after rejected raw Author response."""
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lab

previous = json.loads((ROOT / 'verification/local-task-gates-author-current.json').read_text())
out = ROOT / 'runs' / ('local-task-gates-repair-' + lab.stamp()); out.mkdir()
header = ROOT / 'projects/black-ice-white-noise/restoration/biwn_world_update.h'
system = 'You are the local Game Restorer Remediator. Output only a complete portable C99 file, beginning with #include, no Markdown fences or commentary. You have no tools. Do not claim verification.'
prompt = previous['prompt'] + '''\nADDITIONAL TYPED BUS HEADER (missing from first prompt)\n''' + header.read_text() + '''\nREJECTED AUTHOR RESPONSE\n''' + previous['result']['text'] + '''\nREQUIRED REPAIRS\nThe raw response did not compile: Markdown fences were present and NULL had no defining header. Include <stddef.h> if using NULL. Every callback must receive bus->context as its first argument, never bus. The original prompt omitted the included bus type definitions, now supplied above. Preserve the two-read resume semantics and all other original/host contracts. Return code only. This is a guided repair, not an independent review.\n'''
state = dict(status='prepared', directory=str(out), pid=os.getpid(), role='Remediator', previous=str(Path(previous['directory']) / 'protocol.json'),
             initial_raw_source_accepted=False, guided=True, system=system, prompt=prompt, native_Chat=False, new_training=False)
def save():
    (out / 'protocol.json').write_text(json.dumps(state, indent=2) + '\n')
    (ROOT / 'verification/local-task-gates-repair-current.json').write_text(json.dumps(state, indent=2) + '\n')
save(); print(out, flush=True)
with (ROOT / 'runs/.inference.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    state['status'] = 'generating'; save()
    result = lab.generate('game', system, prompt, 2200, model='advertising-scholar')
    state.update(status='generated_unverified', result=result); save()
    (out / 'candidate.c').write_text(result['text'])
    (out / 'prompts-and-responses.txt').write_text('SYSTEM\n' + system + '\nUSER\n' + prompt + '\nRAW RESPONSE\n' + result['text'] + '\n')
    print(json.dumps(dict(status=state['status'], seconds=result['seconds'], flags=result['quality_flags'])), flush=True)
