"""Draft the complete coordinate-entry caller using local Author/Reviewer roles.

The screen may be locked. This API run saves exact prompts and responses;
it does not fabricate or import a native LM Studio conversation.
"""
from datetime import datetime, timezone
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import sys

import capstone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lab

HEADER = '''#ifndef BIWN_COORDINATE_ENTRY_H
#define BIWN_COORDINATE_ENTRY_H
#include "biwn_world_update.h"
typedef int (*biwn_coordinate_write8)(void *, uint32_t, uint8_t);
/* Analyst API for original 18E92..190B8: ordered global bus accesses and
 * logical helper calls. Helpers remain external and preserve callee saves.
 * Excludes private CPU stack, caller-saved registers/CCR and task timing.
 * max_operations counts each attempted bus/helper callback, including the
 * write8 callback. Exhaustion returns4 before the next callback. Errors
 * retain all earlier effects. No original timeout is inferred.
 * Every declared callback and nonzero budget is required before effects.
 */
enum biwn_coordinate_status { BIWN_COORDINATE_OK=0,
 BIWN_COORDINATE_BAD_ARGUMENT=1, BIWN_COORDINATE_BUS_ERROR=2,
 BIWN_COORDINATE_DEPENDENCY_ERROR=3, BIWN_COORDINATE_LIMIT=4 };
enum biwn_coordinate_status biwn_coordinate_entry(struct biwn_world_bus *,
 biwn_coordinate_write8, uint32_t max_operations);
#endif
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--retry-from', type=Path)
    parser.add_argument('--max-output-tokens', type=int, default=12000)
    args = parser.parse_args()
    assert 2000 <= args.max_output_tokens <= 12000
    out = ROOT / 'runs' / ('local-coordinate-entry-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    print(out, flush=True)
    atlas = ROOT / 'verification/zero-warm-startup-instruction-atlas.bin'
    memory = atlas.read_bytes()
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
    rows = [dict(address=hex(i.address), bytes=i.bytes.hex(), instruction=i.mnemonic + ' ' + i.op_str)
            for i in decoder.disasm(memory[0x18e92:0x190b8], 0x18e92)]
    assert sum(len(bytes.fromhex(x['bytes'])) for x in rows) == 0x190b8 - 0x18e92
    evidence = dict(entry='0x18e92', end_exclusive='0x190b8', instructions=rows,
        atlas=str(atlas), atlas_sha256=hashlib.sha256(memory).hexdigest(),
        source_bytes_sha256=hashlib.sha256(memory[0x18e92:0x190b8]).hexdigest(), header=HEADER,
        helper_arguments={'0x12620': ['word:1'], '0xe4c0': [], '0x1b718': ['long:held_buttons'],
                          '0x20e8c': [], '0xdf60': [], '0xdf22': [], '0x20f78': ['word:1'], '0xdf3e': []},
        contract='Implement every path as readable portable C99. Preserve width/order of every global read/write, including repeated pointer reads. Helpers return full D0 via bus.call, but this semantic API deliberately has no caller-saved-register output. Preserve guest unsigned32 clock comparison and wrapping, word/byte wrapping and signed word comparisons. Implement ASR with unsigned arithmetic/sign fill or equivalent defined C99 math; do not rely on signed right shift. No direct guest pointers, IO, allocation, assembly, libc calls, mutable globals or CPU instruction interpreter. Static helpers permitted. Validate every callback declared by the header and bus read8/read16/read32/write16/write32/call before any effect. Host max_operations counts every attempted bus/helper callback, including write8; exhaustion before a callback returns4. Bus/write8 errors return2; call errors return3; previous effects are retained. Helpers are external logical calls, including DF60: no claim of real scheduling. Read the supplied assembly rather than assuming behavior from routine labels. Return JSON only: source string and limitations string. Include exactly biwn_coordinate_entry.h. Do not add markdown fences.')
    if args.retry_from:
        previous = json.loads((args.retry_from / 'protocol.json').read_text())
        assert previous['status'] == 'terminal_failed'
        evidence['previous_attempt'] = dict(directory=str(args.retry_from), result='Author and Reviewer each exhausted6500tokens with incomplete JSON/source. No code accepted. Broken drafts intentionally omitted from this fresh attempt.')
    arithmetic = ROOT / 'verification/coordinate-backspace-exhaustive-current.json'
    if arithmetic.exists():
        observation = json.loads(arithmetic.read_text())
        assert observation['source_bytes_sha256'] == hashlib.sha256(memory[0x18ff2:0x1901c]).hexdigest()
        evidence['provided_execution_observation'] = observation
        evidence['arithmetic_guidance'] = 'Original backspace block18FF2..1901C lowD4 result equals signed16-to-int division by10 with C99 truncation towardzero, for all65536word values. The analogous second-coordinate block is the same operations with D5. You may use defined C99 int division instead of reproducing this arithmetic instruction by instruction. Explicit signed16 conversion: word<32768?word:(int32_t)word-65536.'
    evidence['style_contract'] = 'Use concise semantic C, with shared static helpers for callback budgeting/errors and repeated operations. Target under180nonblank lines. Do not add per-instruction address comments, a register interpreter, redundant unused helpers or repeated explanations. Preserve all166instructions effects via structured logic. Macros are allowed if useful. Complete the entire function and JSON object.'
    (out / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    (out / 'biwn_coordinate_entry.h').write_text(HEADER)
    state = dict(status='authoring', directory=str(out), pid=__import__('os').getpid(),
                 same_weights=True, independent_review=False, native_Chat_verified=False,
                 new_training=False, drafts=[], coordinator_contribution='Byte-decoded evidence, API/scope contract and independent execution harness. No accepted source yet.')
    state.update(output_budget_per_role=args.max_output_tokens, previous_attempt=str(args.retry_from) if args.retry_from else None,
                 provided_exhaustive_arithmetic_observation=arithmetic.exists())
    (out / 'author-script.py').write_text(Path(__file__).read_text())
    def save():
        text = json.dumps(state, indent=2) + '\n'
        (out / 'protocol.json').write_text(text)
        (ROOT / 'verification/local-coordinate-entry-author-current.json').write_text(text)
    save()
    try:
        with (ROOT / 'runs/.inference.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            for role in ['Author', 'Reviewer']:
                system = lab.COMMON + '\n' + ('Write the complete semantic C implementation from supplied instructions and header, compactly with loops/shared helpers rather than a per-instruction transcript.' if role == 'Author' else 'Review the COMPLETE draft against every instruction, especially the75tick unsigned clock wait, signed word backspace arithmetic, pointer rereads, coordinate bounds and helper sequence. Return compact complete corrected source and limitations in JSON. Do not add per-PC comments or unused helpers. You have not executed tests.')
                user = json.dumps(dict(evidence=evidence, prior_same_model_drafts=state['drafts']))
                state['status'] = 'generating_' + role
                save()
                result = lab.generate('game', system, user, args.max_output_tokens)
                (out / (role + '.json')).write_text(json.dumps(result, indent=2) + '\n')
                with (out / 'prompts-and-responses.txt').open('a') as log:
                    log.write(role + '\nREQUEST\n' + json.dumps(result['request'], indent=2) + '\nRESPONSE\n' + result['text'] + '\n\n')
                state['drafts'].append(dict(role=role, text=result['text'], seconds=result['seconds'], quality_flags=result['quality_flags']))
                save()
                print(role, result['seconds'], result['quality_flags'], flush=True)
                # Never spend another role on a truncated/incomplete draft.
                parsed = lab.parse_object(result['text'])
                assert isinstance(parsed.get('source'), str) and parsed['source'].strip()
                assert isinstance(parsed.get('limitations'), str)
                (out / (role + '-complete.c')).write_text(parsed['source'] + '\n')
            parsed = lab.parse_object(state['drafts'][-1]['text'])
            (out / 'biwn_coordinate_entry.c').write_text(parsed['source'] + '\n')
            state.update(status='proposed_source_pending_execution_checks', limitations=parsed['limitations'])
            save()
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error)); save(); raise


if __name__ == '__main__':
    main()
