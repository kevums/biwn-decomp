"""Guided local scheduler selection C; coordinator retains native trap/ABI work."""
from datetime import datetime,timezone
from pathlib import Path
import fcntl,json,re,sys,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat,binary_tools
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    out=ROOT/'runs'/('local-native-scheduler-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    image=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();ins,_=binary_tools.m68k_instructions(image[0xde1c:0xde46],0xde1c)
    listing='\n'.join(f"{x['address']:06x} {x['bytes']} {x['assembly']}"for x in ins)
    system='You are local Author. Return exactly one freestanding C99 source in one c code fence, stdint.h only, for M68000 GCC. No inline assembly, callbacks, structs, main, mutable globals or test claims. Coordinator supplies assembly ABI/exception/trap and target write boundaries.'
    user='''Implement void biwn_native_scheduler_select(uint32_t *frame). Private frame[0] is incoming D0, frame[8] incoming A0/current or previous task, frame[15] an output flag. All target reads below are volatile uint32_t, at exact original widths/order; frame itself is private wrapper stack. No target RAM writes in this C body. Exact algorithm:
Set frame[15]=0. Set local task=frame[8]. Loop forever with no invented bound:
1. task=*(volatile uint32_t *)task (follow next pointer).
2. Read task+26; nonzero skips to next iteration immediately.
3. Read task+34; nonzero skips immediately.
4. Read task+22 once to test zero. If zero, accept this task without reading clock or changing frame[0].
5. If nonzero, read task+22 AGAIN into frame[0], then read0x778CC as uint32_t clock. If frame[0] > clock with UNSIGNED32 comparison, skip to next iteration. Keep frame[0] changed even when skipping. Otherwise set frame[15]=1 and accept.
On accept, set frame[8]=task and return. Coordinator assembly uses flag to perform the original MOVE.L #0,22(A0), then publishes current task and constructs the original RTE frame. It preserves the original outgoing registers except D0/A0/A1 as appropriate. Do not clear deadline in C: GCC CLR could add a target read the original immediate MOVE does not make. Do not cache the two deadline reads, sign compare, truncate pointers, read task fields out of order or introduce validation. This is guided source translation, not autonomous algorithm discovery.
ORIGINAL SELECT LOOP:\n'''+listing
    reviewer_system='You are local Reviewer using the same weights, not independent validation. Return only compact JSON with booleans ordered_volatile_reads, unsigned_compare, deadline_reread, D0_kept_on_skip, no_target_writes, plus issues array(max3shortitems). Compare source to supplied algorithm. No prose or tests. Under110words.'
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),coordinator_supplied_full_algorithm_and_ABI=True,native_Chat=False,new_training=False,same_model_weights=True,roles=[])
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-scheduler-active.json',state)
    mark()
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('game');state['status']='author_running';mark()
            a=lab.generate('game',system,user,1500);save(out/'author-response.json',a)
            blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
            candidate=out/'scheduler-native.c';candidate.write_text(blocks[0].strip()+'\n');state['roles'].append(dict(role='local Author',seconds=a['seconds']));state['status']='reviewer_running';mark()
            ru=user+'\nAUTHOR C:\n'+candidate.read_text();b=lab.generate('game',reviewer_system,ru,450);save(out/'reviewer-response.json',b);state['roles'].append(dict(role='local Reviewer',seconds=b['seconds']))
        (out/'prompts-and-responses.txt').write_text('AUTHOR SYSTEM\n'+system+'\nAUTHOR USER\n'+user+'\nAUTHOR RESPONSE\n'+a['text']+'\nREVIEWER SYSTEM\n'+reviewer_system+'\nREVIEWER USER\n'+ru+'\nREVIEWER RESPONSE\n'+b['text']+'\n')
        state.update(status='terminal_scheduler_C_draft_pending_native_gates',candidate=str(candidate),candidate_sha256=binary_tools.sha(candidate),raw_model_C_unchanged=True,reviewer_response=b['text'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-scheduler-current.json',state);print(state['status'],state['roles'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
