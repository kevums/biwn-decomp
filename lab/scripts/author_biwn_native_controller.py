"""Local Author/Reviewer for direct native controller C; coordinator supplies ABI/tests."""
from datetime import datetime,timezone
import fcntl,json,re,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,binary_tools,assistant_chat

def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    out=ROOT/'runs'/('local-native-controller-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    image=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();instructions,_=binary_tools.m68k_instructions(image[0xe4c0:0xe53c],0xe4c0)
    listing='\n'.join(f"{x['address']:06x} {x['bytes']} {x['assembly']}"for x in instructions)
    system='You are local Author. Return exactly one complete C99 source in a single c code fence. No explanations. Target freestanding M68000 GCC. Do not claim tests. No inline assembly, callbacks, structs, main, heap, global mutable state, or dependencies except stdint.h. Coordinator supplies native register/CCR wrapper separately.'
    user='Implement uint32_t biwn_native_controller_poll_body(void) from the original instructions below. Direct memory-mapped access is required on the target Jaguar: volatile uint16_t store then volatile uint32_t read at address0xF14000 for each row. Four row selectors in order810E,810D,810B,8107(hex). Every raw long read is ORed with0xF0FFFFFC, then rotatedROR32by4, ROR32by8, ROL32by12 (original twoROL6), ROL32by8 respectively; AND into accumulator initiallyFFFFFFFF, complement it to held. Read previousheld once from0x49BA4, store held there, then store and RETURN edge=(previous XOR held) AND held at0x49BAC. All accesses volatile, original widths/order, no validation or invented extra reads. Native function returns edge; wrapper will preserve every original register and derive original finalCCR while preserving incomingX. Use explicit uint32_t rotations with constant nonzero shifts (no shift32). Keep source concise.\nORIGINAL:\n'+listing
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),roles=[],native_Chat=False,new_training=False,same_model_weights=True,independent_model_validation=False,coordinator_supplied_full_algorithm_ABI_plan=True,system=system,user=user,original_disassembly=listing)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-controller-active.json',state)
    mark()
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('game')
            state['status']='author_running';mark();author=lab.generate('game',system,user,1100);save(out/'author-response.json',author);(out/'author-response.txt').write_text(author['text'])
            blocks=re.findall(r'```c\s*\n(.*?)```',author['text'],re.S);assert len(blocks)==1,'One complete C code fence required'
            source=out/'controller-native.c';source.write_text(blocks[0].strip()+'\n');state['roles'].append(dict(role='local Author',seconds=author['seconds'],response=str(out/'author-response.txt'),source=str(source)))
            rs='You are local Reviewer, same weights as Author, not independent validation. Review ONLY the C body against ordered volatile accesses, widths, rotations and edge formula. Native ABI/CCR wrapper is separate. Reply as JSON with keys accepted (boolean), issues (array of concise strings), no code and no test claims. Under100words.'
            ru=user+'\nAUTHOR C:\n'+source.read_text();save(out/'reviewer-request.json',dict(system=rs,user=ru));state['status']='reviewer_running';mark();reviewer=lab.generate('game',rs,ru,420);save(out/'reviewer-response.json',reviewer);(out/'reviewer-response.txt').write_text(reviewer['text']);state['roles'].append(dict(role='local Reviewer',seconds=reviewer['seconds'],response=str(out/'reviewer-response.txt')))
        (out/'prompts-and-responses.txt').write_text('AUTHOR SYSTEM\n'+system+'\nAUTHOR USER\n'+user+'\nAUTHOR RESPONSE\n'+author['text']+'\nREVIEWER SYSTEM\n'+rs+'\nREVIEWER USER\n'+ru+'\nREVIEWER RESPONSE\n'+reviewer['text']+'\n')
        state.update(status='terminal_native_controller_draft_pending_compile_CPU_and_bus_gates',candidate=str(source),candidate_sha256=binary_tools.sha(source),raw_model_C_unchanged=True,reviewer_response=reviewer['text']);mark();save(ROOT/'verification/local-native-controller-current.json',state);print(state['status'],state['roles'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise

if __name__=='__main__':main()
