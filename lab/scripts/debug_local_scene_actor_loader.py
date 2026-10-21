"""One evidence-directed local repair; preserve original drafts and mismatch."""
import fcntl
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab
def main():
    prior=json.loads((ROOT/'verification/local-scene-actor-author-current.json').read_text())
    parent=Path(prior['directory']);evidence=json.loads((parent/'evidence.json').read_text())
    mismatch=json.loads((parent/'mismatch.json').read_text())
    out=ROOT/'runs'/(lab.stamp()+'-local-scene-actor-debug');out.mkdir()
    compact_mismatch={k:mismatch[k]for k in ['status','expected','actual','errors']}
    compact_mismatch.update(original_trace_first12=mismatch['original_trace'][:12],
                            C_trace_first12=mismatch['C_trace'][:12],
                            full_original_event_count=len(mismatch['original_trace']),
                            full_C_event_count=len(mismatch['C_trace']),
                            complete_receipt=str(parent/'mismatch.json'))
    prompt=dict(evidence=evidence,failed_source=(parent/'biwn_local_scene_actor_loader.c').read_text(),
                actual_comparison=compact_mismatch,
                debugger_notes='''The reviewer duplicated the broken author source.
Reconstruct register effects from disassembly. 20ABA moves D5word into D0,
20ABC SIGN extends D0 to32, 20ABE shifts2, then20AC0 READS A32POINTER from
0x15ECE2+index; it does NOT interpret the pointer-table address as a record.
Every branch BGE/BLT/BLE/BGT compares SIGNED16 bits; use xor0x8000 comparison
or positive word condition (nonzero and bit15clear). MOVEA.W sign extends.
Mode1 failure leads to a SECOND global mode read for CMP#2. Actual helper arg
order is type(D3word),X(D2),Y(A1word),Z(D1),extra(D0word). Before callback D0
lowword changes, highword retained. out pointer to callback must contain thatD0.
Original first count comparison and bottom count comparison are distinct:
when bottom says continue it jumps20ABA without an extra top count read.
Return COMPLETE corrected C source, not explanation or old draft.''')
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        result=lab.generate('game',lab.COMMON+'\nYou are a debugger. Use the actual original-code mismatch to repair the complete source. Return JSON source and limitations.',json.dumps(prompt),2600)
    (out/'debugger.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'prompts-and-responses.txt').write_text('DEBUGGER\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
    parsed=lab.parse_object(result['text']);(out/'biwn_local_scene_actor_loader.c').write_text(parsed['source']+'\n')
    protocol=dict(status='proposed_debug_source_pending_checks',directory=str(out),parent_failed_draft=str(parent),roles=['local Code Author','local Source Reviewer','local Debugger'],same_weights_correlated=True,new_training=False,native_Chat_verified=False,drafts=prior['drafts']+[dict(role='debugger',text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags'])])
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (ROOT/'verification/local-scene-actor-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n');print(out,result['seconds'],flush=True)
if __name__=='__main__':main()
