"""Local author/reviewer produce readable source from an observed contract."""
import fcntl
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab


def main():
    out=ROOT/'runs'/(lab.stamp()+'-local-portal-key')
    out.mkdir()
    contract='''Write one readable C99 function, including only <stdint.h>:
int biwn_local_portal_key(unsigned direction, uint16_t x, uint16_t z,
uint16_t min_x, uint16_t max_x, uint16_t min_z, uint16_t max_z,
uint8_t encoded_key, uint16_t *key_out).
This is a value-only translation of observed BIWN 1048C..104D0, not full CPU state.
For direction0 subtract x-min_x; direction1 max_x-x; direction2 max_z-z;
direction3 z-min_z. Wrap the subtraction to16bits. Arithmetic right shift that
16bit result by6, retaining a uint16 bit pattern: shift unsigned then fill
upper6 bits with0xFC00 if the original bit15 was set. Avoid signed right shift.
Store this entire16bit shifted key in key_out. Sign-extend encoded_key from8
to16 bits without relying on implementation-defined unsigned-to-signed casts.
Return1 exactly when (shifted_key&15) equals that sign-extended key, else0.
Directions>=4 or null key_out return-1 without changing output.
No flags, register banks, memory bus, timing, IO, allocation or extra functions.
Use only unsigned integer math, no assembly. Do not claim tests ran.
Return JSON only: source(string), limitations(string).'''
    protocol=dict(contract=contract,roles=['local Code Author','local Source Reviewer'],
                  same_weights_correlated=True,model=lab.CONFIG['models']['game']['identifier'],
                  native_Chat_verified=False,new_training=False,runtime_promoted=False)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    previous=[]
    print(out,flush=True)
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['author','reviewer']:
            system=lab.COMMON+'\n'+('Author the requested readable C helper.'if role=='author'else'Audit every contract clause. Return corrected complete C source; do not claim execution or successful validation.')
            result=lab.generate('game',system,json.dumps(dict(contract=contract,previous_drafts=previous)),1000)
            (out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            with (out/'prompts-and-responses.txt').open('a')as transcript:
                transcript.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
            previous.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']))
            print(role,result['seconds'],result['quality_flags'],flush=True)
    response=lab.parse_object(previous[-1]['text'])
    (out/'biwn_local_portal_key.c').write_text(response['source']+'\n')
    protocol.update(status='proposed_source_pending_compilation_and_original_checks',directory=str(out),results=previous,
                    raw_JSON_only=not previous[-1]['text'].lstrip().startswith('```'))
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (ROOT/'verification/local-portal-key-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')


if __name__=='__main__':main()
