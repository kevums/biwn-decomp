"""Local task creation Author/Reviewer; coordinator owns ABI/exception gates."""
from datetime import datetime, timezone
from pathlib import Path
import fcntl, json, os, re, sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab, assistant_chat, binary_tools
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    out=ROOT/'runs'/('local-native-task-create-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    image=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    ins,_=binary_tools.m68k_instructions(image[0xde5c:0xdeb6],0xde5c)
    listing='\n'.join(f"{x['address']:06x} {x['bytes']} {x['assembly']}"for x in ins)
    system='You are local Author. Return one complete freestanding C99 source inside exactly one c code fence. Target M68000 GCC, stdint.h only. No inline assembly, callbacks, structs, main, mutable globals or tests. Coordinator supplies exact CPU register/CCR and ILLEGAL exception wrapper separately.'
    user='''Implement uint32_t biwn_native_task_create_body(uint32_t callback, uint32_t parameter, uint32_t *current_out). Direct target RAM access, every target read/store volatile at original width and order. Read current long at 0xC0920, free long at 0xC0924; write current once to private *current_out (wrapper stack, not target task memory). If free==0 return0 without any target writes; wrapper will raise original ILLEGAL at0xDEB4. Otherwise perform original linked list/task record operations below and return free pointer. Preserve the original rereads: free->next is read once before writing0xC0924, then after overwriting free->next with current->next reread free->next to locate successor. Do not cache across those operations. Callback goes to free+8 and+16, parameter to free+30, initial stack free+0x400 to free+12; clear16bits at+20, clear32bits in order+26,+22,+34. Use pointer casts at each original access, explicit uint32_t temporaries; no added validation, bounds guards or target reads. Compiler ABI preserves callee saved regs; wrapper reconstructs A0/A1, D0, D1 and final flags. This is source translation from supplied algorithm/disassembly, not independent reverse engineering. ORIGINAL:\n'''+listing
    review_system='You are local Reviewer, same model weights as Author and not independent validation. Check C target access width/order and rereads against original list/task writes. Private current_out store and wrapper ABI/ILLEGAL are separate. Return JSON accepted(boolean), issues(array), no code/test claims, under120words.'
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),roles=[],native_Chat=False,new_training=False,same_model_weights=True,coordinator_supplied_algorithm_and_ABI=True,system=system,user=user)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-task-create-active.json',state)
    mark()
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('game')
            state['status']='author_running';mark();a=lab.generate('game',system,user,1500);save(out/'author-response.json',a)
            blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
            source=out/'task-create-native.c';source.write_text(blocks[0].strip()+'\n')
            state['roles'].append(dict(role='local Author',seconds=a['seconds']));state['status']='reviewer_running';mark()
            ru=user+'\nAUTHOR C:\n'+source.read_text();b=lab.generate('game',review_system,ru,550);save(out/'reviewer-response.json',b)
            state['roles'].append(dict(role='local Reviewer',seconds=b['seconds']))
        (out/'prompts-and-responses.txt').write_text('AUTHOR SYSTEM\n'+system+'\nAUTHOR USER\n'+user+'\nAUTHOR RESPONSE\n'+a['text']+'\nREVIEWER SYSTEM\n'+review_system+'\nREVIEWER USER\n'+ru+'\nREVIEWER RESPONSE\n'+b['text']+'\n')
        state.update(status='terminal_task_create_draft_pending_native_gates',candidate=str(source),candidate_sha256=binary_tools.sha(source),raw_model_C_unchanged=True,reviewer_response=b['text'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-task-create-current.json',state)
        print(state['status'],state['roles'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
