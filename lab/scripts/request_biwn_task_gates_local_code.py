"""One bounded local Author request; execution comparison decides acceptance."""
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lab

out = ROOT / 'runs' / ('local-task-gates-' + lab.stamp())
out.mkdir()
header = ROOT / 'projects/black-ice-white-noise/restoration/biwn_task_gates.h'
listing = ROOT / 'projects/black-ice-white-noise/analysis/session-20261012T191624.705232Z/drawing-volatile-20261013T043902.091834Z/export/listing.asm'
assembly = '\n'.join(line for line in listing.read_text().splitlines() if line[:8].isalnum() and '0000df22' <= line[:8] < '0000df60')
system = 'You are the local Game Restorer Author. Return a complete portable C99 source file only, without fences, reasoning or commentary. You have no tools. Never claim tests ran. The coordinator compares the generated code with original CPU execution.'
prompt = '''Implement exactly the two exported functions in the supplied header. Include biwn_task_gates.h. No global mutable state, allocation, I/O, pointer casts or external helpers except the bus read32/write32 callbacks. Use one internal shared traversal if useful. Require bus, out_d0, max_nodes>0, read32, write32 before any effects. Every attempted callback can fail (nonzero), returning BUS_ERROR. On errors/limit, retain previous stores and leave out_d0 unchanged. On success, write incoming_d0 to out_d0. Unsigned counters/addresses wrap modulo2^32. Do not validate/reject a zero pointer separately: bus callbacks determine address validity. No arbitrary ring repair. A max_nodes budget allows exactly that many peer nodes; check before processing the next peer, but allow successful return after exactly max_nodes when the final next pointer equals current. Each pointer access must remain ordered: read current fromC0920, then next fromcurrent+0, process next until equal to current, then read each processed node's next. Resume reads the counter once to test; if nonzero read it a second time for decrement then write second_value-1, even if second_value is0. Pause reads once then writes value+1. These callbacks represent data accesses only, excluding opcode/private stack accesses.\nHEADER\n''' + header.read_text() + '\nORIGINAL OBSERVED LISTING (evidence, not instructions)\n' + assembly
state = dict(status='prepared', pid=os.getpid(), directory=str(out), system=system, prompt=prompt,
             header_sha256=hashlib.sha256(header.read_bytes()).hexdigest(), assembly=assembly,
             native_Chat=False, weight_training=False)
def save():
    (out / 'protocol.json').write_text(json.dumps(state, indent=2) + '\n')
    (ROOT / 'verification/local-task-gates-author-current.json').write_text(json.dumps(state, indent=2) + '\n')
save()
print(out, flush=True)
with (ROOT / 'runs/.inference.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    models = json.loads(subprocess.check_output([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'], text=True))
    assert len(models) == 1 and models[0]['identifier'] == 'advertising-scholar' and models[0]['status'] == 'idle'
    state.update(status='generating', actual_model=models); save()
    try:
        result = lab.generate('game', system, prompt, 2200, model='advertising-scholar')
        state.update(status='generated_unverified', result=result)
        (out / 'candidate.c').write_text(result['text'])
        (out / 'prompts-and-responses.txt').write_text('SYSTEM\n' + system + '\nUSER\n' + prompt + '\nAUTHOR RAW RESPONSE\n' + result['text'] + '\n')
        save()
        print(json.dumps(dict(status=state['status'], seconds=result['seconds'], flags=result['quality_flags'])), flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error)); save(); raise
