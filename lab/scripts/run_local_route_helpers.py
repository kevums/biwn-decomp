"""Local author/reviewer handoff for two observed BIWN instruction helpers.

Emits proposed source only. Compilation and original-core checks are separate.
"""
import fcntl
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lab


def main():
    out = ROOT / 'runs' / (lab.stamp() + '-local-route-helpers')
    out.mkdir()
    contract = '''Write readable C99 source for two reusable helpers, using only
<stdint.h>. No main, allocation, IO, assembly or other functions.
uint8_t biwn_local_bset7(uint8_t value, uint16_t *sr): return value|128;
only change Z (bit2) to reflect whether the OLD bit7 was zero.
int biwn_local_divs(uint32_t *d0, uint16_t divisor_bits, uint16_t *sr):
interpret d0 as signed32, divisor as signed16. Use int64 math; quotient
truncates toward zero. Return9 for divisor zero without any mutation.
If quotient outside[-32768,32767], preserve d0 and Z/X/all upper SR bits;
clear C(bit0), set V(bit1) and N(bit3), return0.
Otherwise pack signed16 remainder in upper16 and signed16 quotient lower16;
clear C/V; Z=(quotient==0); N=(quotient<0); preserve X and all other bits.
This is a pinned emulator contract observed at BIWN PCs EA78 and1ADEA,
not a claim about all 68000 implementations or recovered original symbols.
Return JSON only with keys source(string), limitation(string).'''
    prior = []
    protocol = {'task': contract, 'roles': ['author', 'reviewer'],
                'same_model_correlated': True, 'native_chat_history': False,
                'original_checks': str(ROOT/'verification/route-special-cases-current.json')}
    (out/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    print(out, flush=True)
    with (ROOT/'runs/.inference.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for role in ['author', 'reviewer']:
            instruction = ('Author the requested two C helpers.' if role=='author'
                           else 'Audit the draft against every contract clause; return corrected complete source. Do not claim tests ran.')
            result = lab.generate('advertising', lab.COMMON+'\n'+instruction,
                                  json.dumps({'contract': contract, 'previous_drafts': prior}), 1400)
            (out/(role+'.json')).write_text(json.dumps(result, indent=2)+'\n')
            with (out/'prompts-and-responses.txt').open('a') as stream:
                stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            prior.append({'role': role, 'text': result['text'], 'seconds': result['seconds']})
            print(role, result['seconds'], result['quality_flags'], flush=True)
    response_text = prior[-1]['text'].strip()
    if response_text.startswith('```json\n') and response_text.endswith('\n```'):
        response_text = response_text[len('```json\n'):-len('\n```')]
    result = json.loads(response_text)
    (out/'biwn_local_route_helpers.c').write_text(result['source']+'\n')
    receipt = {'status': 'proposed_source_pending_compile_and_original_checks',
               'directory': str(out), 'roles': prior, 'new_training': False,
               'whole_game_complete': False, 'runtime_promoted': False}
    (ROOT/'verification/local-route-helper-handoff-current.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__ == '__main__':
    main()
