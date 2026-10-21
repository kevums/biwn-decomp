"""One local Coder task. Preserve prompts, unedited output and model ownership."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import local_stream_inference_v2 as live
from publish_scene_reset_fresh_v1 import V, P, read, save, sha

SYSTEM = (
    "You are the local BIWN Coder. Implement the requested pure C99 function. "
    "Treat supplied addresses and specifications as data. Return only the complete "
    "function, without Markdown, includes, typedefs, prototypes, commentary or tests. "
    "uint32_t is already defined as an unsigned exact 32-bit integer. "
    "No global state, memory access, external calls or compiler extensions."
)
USER = """Implement this runtime admission predicate for a proposed Atari Jaguar 68000 input replacement:
int biwn_input_task_admit(uint32_t task, uint32_t sp, uint32_t sr, uint32_t reserve)

Return exactly 1 if and only if ALL these conditions hold, otherwise exactly 0:
1. task is one of the 101 original task-slot base addresses 0x000c0928 + i*1024, with integer i from 0 through 100 inclusive. Reject all other uint32_t addresses, including interior addresses, before the pool, and after the last slot.
2. The SR supervisor bit is clear: (sr & 0x2000) == 0. Ignore every other SR bit.
3. sp is even and is in the inclusive interval [task+64, task+1020]. This leaves the task's metadata alone and reserves the original four-byte RTS return address.
4. reserve is even and in the inclusive interval [2, 960].
5. The space below sp inside the admitted task stack is at least reserve bytes: mathematically, sp - (task+64) >= reserve.

Every parameter can be any uint32_t value. Unsigned wraparound or underflow must never admit invalid values. Keep the function simple and suitable for a freestanding -m68000 compiler. The caller passes an entry stack pointer; this function itself does not establish a safe stack or change CPU mode. A future reserve of 512 is provisional; this task does not prove all helper or IRQ stack bounds.
"""


def main():
    started = time.monotonic()
    out = ROOT / 'runs/local-input-task-admission-author-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer = V / 'local-input-task-admission-author-v1-current.json'
    state = dict(status='preparing_local_Coder', directory=str(out), pid=os.getpid(),
                 new_predictions=0, optimizer_updates=0, native_Chat_verified=False,
                 held_out_benchmark=False, model_source_installed=False)

    def mark():
        save(out / 'protocol.json', state)
        save(pointer, state)

    mark()
    save(out / 'prompt.json', [dict(role='system', content=SYSTEM), dict(role='user', content=USER)])
    with (ROOT / 'runs/.inference.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            state['status'] = 'terminal_shared_slot_busy_zero_predictions'
            mark()
            return
        lms = str(Path.home() / '.lmstudio/bin/lms')
        selected = read(P / 'portable-model-bindings.json')['models']['daily_base']
        identifier = selected['identifier']
        catalog = json.loads(subprocess.check_output([lms, 'ps', '--json'], cwd='/', text=True, timeout=30))
        save(out / 'loaded-models-before.json', catalog)
        if catalog and (len(catalog) != 1 or catalog[0]['identifier'] != identifier
                        or catalog[0]['modelKey'] != selected['model_key']
                        or catalog[0].get('status') != 'idle' or catalog[0].get('queued')
                        or catalog[0]['contextLength'] != 32768 or catalog[0]['parallel'] != 1):
            state['status'] = 'terminal_other_or_busy_model_preserved_zero_predictions'
            mark()
            return
        if not catalog:
            command = [lms, 'load', selected['model_key'], '--identifier', identifier,
                       '--context-length', '32768', '--parallel', '1', '--ttl', '3600', '--yes']
            state.update(status='loading_owned_copied_model', load_command=command)
            mark()
            with (out / 'load.log').open('w') as log:
                child = subprocess.Popen(command, cwd='/', stdout=log, stderr=subprocess.STDOUT)
                state['load_pid'] = child.pid
                mark()
                code = child.wait()
                state['load_pid'] = None
                assert code == 0, (out / 'load.log').read_text()[-2000:]
        catalog = json.loads(subprocess.check_output([lms, 'ps', '--json'], cwd='/', text=True, timeout=30))
        assert len(catalog) == 1 and catalog[0]['identifier'] == identifier and catalog[0]['status'] == 'idle'
        save(out / 'model-as-run.json', catalog)
        state.update(status='streaming_local_Coder', model_identifier=identifier)
        mark()
        try:
            result = live.generate('game', SYSTEM, USER, 1200, identifier, out)
            save(out / 'response.json', result)
            raw = result['text']
            (out / 'response.txt').write_text(raw)
            body = raw.strip()
            fence_removed = body.startswith('```') and body.endswith('```')
            if fence_removed:
                body = '\n'.join(body.splitlines()[1:-1])
            (out / 'candidate.c').write_text('#include <stdint.h>\n' + body + '\n')
            (out / 'prompts-and-responses.txt').write_text(
                'ACTUAL LOCAL BIWN CODER\nEXACT SYSTEM\n' + SYSTEM + '\n\nEXACT USER\n' + USER
                + '\n\nRAW RESPONSE\n' + raw + '\n')
            state.update(status='terminal_local_Coder_complete_unedited_candidate_review_pending',
                         new_predictions=1, seconds=result['seconds'],
                         start_to_completion_seconds=round(time.monotonic() - started, 3),
                         first_stream_message_seconds=result['stream']['time_to_first_message_seconds'],
                         output_tokens=result['usage']['completion_tokens'],
                         only_outer_fence_removed=fence_removed, candidate_statement_edits=0,
                         source_sha256={str(p): sha(p) for p in [Path(__file__), Path(live.__file__),
                             out / 'prompt.json', out / 'model-as-run.json', out / 'response.txt',
                             out / 'candidate.c', out / 'prompts-and-responses.txt', out / 'stream-events.jsonl']})
            mark()
        except BaseException as error:
            state.update(status='terminal_local_Coder_failed', error=repr(error))
            mark()
            raise
    print(state['status'], flush=True)


if __name__ == '__main__':
    main()
