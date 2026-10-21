"""Guided local assembly author/reviewer for the existing18byte scan repair."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat,binary_tools

def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    out=ROOT/'runs'/('local-native-word-scan-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0]
    system='You are local assembly Author. Return exactly one complete GNU M68000 assembly source in an asm code fence. No prose, test claims, raw opcodes, .byte/.word/.long/.incbin/.org, or numeric branch encodings. Coordinator supplies the exact recovered repair plan and linker targets.'
    user='Author the source for an existing18byte BIWN restoration fragment at0x1B0EE. It must define .text, .globl biwn_marker_word_scan, and label biwn_marker_word_scan. Emit exactly these six instructions in order using GNU percent-register syntax: CMP.L (A2)+,D2; BEQ.S biwn_marker_run; SUBQ.L #2,A2; CMPA.L #0x1C7FFF,A2; BCS.S biwn_marker_word_scan; BRA.W biwn_marker_scan_failure. Linker symbols biwn_marker_run=0x1B100 and biwn_marker_scan_failure=0x1B122 are external and supplied separately. Do not define them or add padding. This scans candidate starts every2bytes after a mismatch rather than every4. Existing downstream16long marker-run/payload guard remains original code. This is a repair fragment, not a whole new function or a generally bounds-safe parser. Output source only.'
    state=dict(status='prepared',directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat(),system=system,user=user,roles=[],new_training=False,native_Chat=False,same_weights=True,independent_validation=False,coordinator_supplied_full_instruction_plan=True,legacy_patch=patch)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-word-scan-active.json',state)
    mark()
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('game');state['status']='author_running';mark()
            author=lab.generate('game',system,user,450);save(out/'author-response.json',author);blocks=re.findall(r'```(?:asm|assembly)\s*\n(.*?)```',author['text'],re.S);assert len(blocks)==1
            source=out/'marker-word-scan.S';source.write_text(blocks[0].strip()+'\n');state['roles'].append(dict(role='local Author',seconds=author['seconds'],source=str(source)))
            rs='You are local Reviewer using the same weights, not independent validation. In at most110words explain only this fragment: candidate stride, targets, and one bound/behavior limitation. No test claims, no whole-game claims, no code changes. Do not call it fully bounds-safe: the long read occurs before the candidate bound check and the downstream marker-run reads remain original.'
            ru='Source at1B0EE, run target1B100, failure target1B122:\n'+source.read_text()+'\nOriginal continuation confirms16matching longs then checks A2<=1C8000 before allowing a payload pointer. This does not prevent every read beyond the input window. Describe the limited repair accurately.'
            state['status']='reviewer_running';mark();reviewer=lab.generate('game',rs,ru,330);save(out/'reviewer-response.json',reviewer);state['roles'].append(dict(role='local Reviewer',seconds=reviewer['seconds']))
        (out/'prompts-and-responses.txt').write_text('AUTHOR SYSTEM\n'+system+'\nAUTHOR USER\n'+user+'\nAUTHOR RESPONSE\n'+author['text']+'\nREVIEWER SYSTEM\n'+rs+'\nREVIEWER USER\n'+ru+'\nREVIEWER RESPONSE\n'+reviewer['text']+'\n')
        state.update(status='terminal_word_scan_source_pending_assembly',candidate=str(source),candidate_sha256=binary_tools.sha(source),raw_model_assembly_unchanged=True,reviewer_response=reviewer['text']);mark();save(ROOT/'verification/local-native-word-scan-current.json',state);print(state['status'],state['roles'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
