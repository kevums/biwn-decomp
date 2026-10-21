"""Reasoning-medium local Author/Reviewer, original assembly plus ABI contract.

No existing portable C or full branch-by-branch algorithm supplied here.
Coordinator supplies frame, volatile helpers and derived final flag contract.
"""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,sys,os,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    out=ROOT/'runs'/('local-native-free-'+lab.stamp());out.mkdir();print(out,flush=True)
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';image=ROOT/'render-assets/biwn-inventory-baseline.bin'
    listing=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-D','-b','binary','-m','m68k:68000','--start-address=0x1545c','--stop-address=0x1557a',str(image)],text=True)
    system='You are local C Author. Return exactly one complete freestanding C99 file in one c code fence, including "free-native.h". Implement only void biwn_native_free_body(uint32_t *r). No asm, libc, mutable globals, host guards/budgets, simulated tool calls or test claims. Derive the actual control/data flow from the supplied original assembly; gotos are allowed to preserve rereads and exact branches.'
    request='Coordinator header and frame helpers:\n'+(native/'free-native.h').read_text()+'''\nPreserve the original full caller state. D0/D1/A0/A1 must reflect only actual original instructions; initialize locals from those exact frame cells. Track original local A2/A3 for the routine, but restore their final values from the two public original save slots, not from the private frame. Target reads/writes are volatile32 and must preserve original order and rereads. Every original CLR.L uses biwn_native_free_clear32(address), not FW32zero and not a manually added extra read. That helper's hardware A0clobber is private; never substitute it for the original frame's A0 state.
Coordinator-derived flag contract: every path ends with Z=1,N=V=C=0; X is preserved from the last actual ADD.L (memory or D0) on that path, or incoming X on early null/empty-handle paths. ADD.L may wrap: biwn_free_add returns wrapped sum and updates X. ADDAs, SUBQ to address registers, CMPA, TST, CLR and MOVEA do not modify X. Preserve saved SR above the low5bits. Final r[16]=(incomingSR&0xffe0u)|X|4u. Do not accidentally change X on address arithmetic, loop comparisons or branch instructions. The original head/next pointer comparisons use unsigned BCC, not signed ordering. Both reads of the handle cell near entry are separate and can differ in ordered tests. Do not cache target rereads.
This is the complete original routine. Do not add list-validation, null/range guards absent from original, rollback, or bounded traversal in C. Do not assume nonzero handle implies nonzero payload without the actual TST. On every exit perform the two public save-slot reads in the stated order.\nOriginal assembly:\n'''+listing
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),reasoning='medium',same_weights=True,independent_model_validation=False,coordinator_supplied_full_algorithm=False,coordinator_supplied_disassembly_ABI_and_flag_helpers=True,new_training=False,source_accepted=False,native_Chat=False,roles=[])
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-free-active.json',state)
    mark();(out/'prepared-author.json').write_text(json.dumps({'system':system,'user':request,'reasoning':'medium','max_output_tokens':8000},indent=2))
    transcript='AUTHOR SYSTEM\n'+system+'\nUSER\n'+request+'\n';(out/'prompts-and-responses.txt').write_text(transcript)
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game')
            # Per-process API setting only; do not alter saved daily defaults.
            lab.CONFIG['models']['game']['reasoning']='medium'
            state['status']='reasoning_author_running';mark();a=lab.generate('game',system,request,8000);save(out/'author-response.json',a)
            blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
            p=out/'free-native.c';p.write_text(blocks[0].strip()+'\n');state['roles'].append(dict(role='local reasoning Author',seconds=a['seconds'],usage=a['usage']))
            transcript+='RESPONSE\n'+a['text']+'\n';(out/'prompts-and-responses.txt').write_text(transcript)
            rs='You are local Reviewer using the same weights, not independent validation. Audit supplied original assembly/ABI versus candidate C. Return JSON with issues array(max6concreteitems), frame_mapping, unsigned_pointer_order, target_rereads, coalescing_links, last_ADD_carry_X, final_public_restores booleans. Branches do not set flags. No code or test claims. Under200words.'
            ru=request+'\nCANDIDATE C\n'+p.read_text();state['status']='reasoning_reviewer_running';mark();b=lab.generate('game',rs,ru,4000);save(out/'reviewer-response.json',b);state['roles'].append(dict(role='same-weight reasoning Reviewer',seconds=b['seconds'],usage=b['usage']))
            transcript+='REVIEWER SYSTEM\n'+rs+'\nUSER\n'+ru+'\nRESPONSE\n'+b['text']+'\n';(out/'prompts-and-responses.txt').write_text(transcript)
        state.update(status='terminal_reasoning_free_draft_pending_native_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_model_C_unchanged=True,reviewer_response=b['text'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-free-current.json',state);print(state['status'],state['roles'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
