"""Local C Author and same-weight Reviewer for the retained copy dependency.

Coordinator supplies disassembly, target ABI and derived flags/stack contract;
model authors the C body. CPU/device checks, not agreement, decide acceptance.
"""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,sys,os,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    out=ROOT/'runs'/('local-native-copy-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    image=ROOT/'render-assets/biwn-inventory-baseline.bin'
    listing=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-D','-b','binary','-m','m68k:68000','--start-address=0xe3e0','--stop-address=0xe4aa',str(image)],text=True)
    system='You are the local C Author. Return one complete freestanding C99 file in one c code fence. Include "copy-native.h". Implement only void biwn_native_copy_body(uint32_t *r). No asm, libc, callbacks, mutable globals, new guards/budgets, test claims or prose. This is guided target translation with coordinator ABI/flag conclusions, not autonomous decompilation.'
    request='Coordinator supplied header:\n'+(native/'copy-native.h').read_text()+'''\nOriginal complete disassembly follows. Preserve uint32 wrap arithmetic and volatile access order/width. Read public argument0 then argument1 then count from originalSP+4/+8/+12, exactly once each. r[17] selects source-first versus destination-first ordering. Preserve all other frame registers. Nonzero small counts copy forward, byte-by-byte (including overlap); never use memmove or memcpy. Large path programs the real hardware registers; do not copy its payload in software or poll/invent completion reads.
Coordinator-derived ABI details: zero count loads A0/A1/D1 but leaves D0 unchanged; final CCR is incoming X plus Z. Small nonzero return leaves D0 unchanged, D1=0, advanced A0/A1, CCR=Z only. Large path writes flags0x4020toF02204 thenF02228, then must write the original D2,D3,D4 to originalSP-4,-8,-12 respectively before its loop. The wrapper otherwise does not touch those12bytes. Final large D0 is final blitter command, D1=0, A0/A1 advanced by full count. D2..D7/A2..A6 remain original. Final large CCR: N/Z from original D2; V=C=0; X is the low bit of source phrase-byte offset before final chunk. Preserve saved SR above low5bits for every path. Do not use signed-overflow C arithmetic. Original BMI checks wrapped-subtraction N only, not signed less-than. Count/chunk ASR must preserve sign for high-bit raw counts. Do not clamp/reject raw values. The normal finite tests cover valid RAM and bounded counts; separate raw-count prefix probes may stop without return.
Original listing:\n'''+listing
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),roles=[],coordinator_supplied_disassembly_ABI_flags_and_stack_contract=True,model_C_algorithm=True,native_Chat=False,new_training=False,same_weights=True,source_accepted=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-copy-active.json',state)
    mark();transcript=''
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game')
            state['status']='author_running';mark();a=lab.generate('game',system,request,3300);save(out/'author-response.json',a)
            blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
            p=out/'copy-native.c';p.write_text(blocks[0].strip()+'\n');state['roles'].append(dict(role='local C Author',seconds=a['seconds']))
            transcript+='AUTHOR SYSTEM\n'+system+'\nUSER\n'+request+'\nRESPONSE\n'+a['text']+'\n';(out/'prompts-and-responses.txt').write_text(transcript)
            rs='You are local Reviewer using the same weights, not independent verification. Audit original assembly against C. Return JSON with issues array(max4shortitems), original_BMI_N_only, MMIO_order, forward_overlap, large_stack_saves, return_flags booleans. No code or execution claims. Under140words.'
            ru=request+'\nRAW AUTHOR C\n'+p.read_text();state['status']='reviewer_running';mark();b=lab.generate('game',rs,ru,650);save(out/'reviewer-response.json',b);state['roles'].append(dict(role='local Reviewer',seconds=b['seconds']))
            transcript+='REVIEWER SYSTEM\n'+rs+'\nUSER\n'+ru+'\nRESPONSE\n'+b['text']+'\n';(out/'prompts-and-responses.txt').write_text(transcript)
        state.update(status='terminal_native_copy_draft_pending_CPU_device_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_model_C_unchanged=True,reviewer_response=b['text'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-copy-current.json',state);print(state['status'],state['roles'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
