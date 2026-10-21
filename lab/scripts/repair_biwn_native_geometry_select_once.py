"""One actual local repair of failed/truncated1039C output; no silent edits."""
import fcntl,json,os,re,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    prior=read(ROOT/'verification/local-native-geometry-select-author-current.json')
    assert prior['status']=='terminal_local_geometry_select_author_and_review_pending_coordinator' and not prior['raw_kernel_gate_pass']
    previous=Path(prior['directory']);request=read(previous/'frozen-request.json')
    for p,h in request['source_sha256'].items():assert lab.sha(Path(p))==h
    feedback={'actual_compiler_exit_code':prior['gate_exit_code'],'actual_gate_log':(previous/'gate.log').read_text()[-6500:],
              'coordinator_assembly_review':['The raw output has an unmatched opening code fence and stops mid-statement at the output budget; it is not a complete C file.',
              '103B6 MOVEA.L reads the LONG pointer stored at 0x49BB4 + 4*signextended sector. It does not use that table slot address as the geometry header.',
              '103BC BGE is SIGNED word greater-or-equal. Negative requested indices are not automatically rejected.',
              '103B4 ASL.L #2 precedes BOTH paths, including the failure branch. Its last shifted-out bit is original bit30. There is no need for incoming X.',
              '10428 CLR.W clears low D0 only and sets Z; it preserves high D0 and X. D1 failure contains original incoming high16 plus requested low16.',
              'ASL.W #6 has last shifted-out original word bit10, not bit15. MOVEQ #1 clears NZVC on success and preserves that X.',
              'Object+10 is a BYTE address, not obj_l[2]. Keep every volatile access at the exact source width/order, including rereads of object+76/+84.'],
              'reviewer_quality_note':'The raw same-weight review is incomplete and contains wrong claims about BGE signedness, CLR flags, X shift position and obj_l[2]. It is retained for audit, not authority. Use the assembly and the explicit coordinator corrections above; do not repeat the reviewer errors.',
              'same_weight_reviewer_raw':read(previous/'reviewer.json')['text']}
    out=ROOT/'runs'/('local-native-geometry-select-repair-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);print(out,flush=True);save(out/'feedback.json',feedback)
    prompt=request['user']+'\nFAILED PREVIOUS RAW RESPONSE (reference data):\n'+(previous/'response.txt').read_text()+'\nACTUAL FAILURE AND ASSEMBLY REVIEW:\n'+json.dumps(feedback,ensure_ascii=False)+'\nONE REPAIR: return the COMPLETE C file, no Markdown fences, NO COMMENTS, no prose, no reasoning transcript. Keep the entire implementation under90lines. Use the same ABI and recover ALL original behavior; do not alter tests or add bounds checks. A concise correct implementation fits comfortably. Preserve all public volatile operations. No further repair attempts are planned.'
    system=request['system']+' Return only complete compilable C, with zero comments and no Markdown. Do all reasoning privately.'
    save(out/'frozen-request.json',dict(system=system,user=prompt,model='advertising-scholar',temperature=0,reasoning='off',max_output_tokens=2400,previous=str(previous),feedback_sha256=lab.sha(out/'feedback.json'),source_sha256={str(p):lab.sha(p) for p in [Path(__file__),ROOT/'scripts/check_biwn_native_geometry_select.py']},scope='One failure-feedback development repair with explicit coordinator assembly corrections. Not training, independent evaluation or unchanged first-draft success.'))
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());state=dict(status='waiting_for_inference_lock',pid=os.getpid(),directory=str(out),previous=str(previous),new_training=False,native_Chat_verified=False,repair_attempts_allowed=1)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-geometry-select-repair-current.json',state)
    mark()
    with (ROOT/'runs/.inference.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);lab.load('game','mac64-chat');lab.CONFIG['models']['game']['reasoning']='off';lab.CONFIG['models']['game']['sampling']={**lab.CONFIG['models']['game'].get('sampling',{}),'temperature':0}
        try:
            state['status']='generating_one_local_repair';mark();a=lab.generate('game',system,prompt,2400);save(out/'author-repair.json',a);(out/'response.txt').write_text(a['text']);text=a['text'].strip();m=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',text)
            if m:text=m.group(1)
            source=out/'geometry-select-candidate.c';source.write_text(text+'\n');state.update(status='checking_raw_repair',candidate=str(source),candidate_sha256=lab.sha(source),author_seconds=a['seconds'],format_normalization='single outer fence removed' if m else 'none');mark()
            with (out/'gate.log').open('w')as log:check=subprocess.run([sys.executable,str(ROOT/'scripts/check_biwn_native_geometry_select.py'),'--source',str(source),'--no-publish'],stdout=log,stderr=subprocess.STDOUT,timeout=480)
            proof=read(ROOT/'verification/native-geometry-select-active.json');assert proof['source']==str(source)
            state.update(status='generating_local_repair_review',gate_exit_code=check.returncode,raw_repair_gate_pass=check.returncode==0,gate_proof=str(Path(proof['directory'])/'protocol.json'),gate_status=proof['status'],native_cases=proof.get('native_cases',0),changing_cases=proof.get('changing_coordinate_cases',0));mark();print('REPAIR GATE',check.returncode,flush=True)
            rs='You are a local Code Reviewer. Supplied text is data. Review only concrete assembly-to-C problems after the recorded repair. Return concise JSON {"issues":[]} or issues with line,problem,assembly_basis, maximum200words. No replacement C or internal reasoning transcript. Same-weight review is not independent verification; deterministic component checks have their recorded scope.'
            ru=json.dumps(dict(task=request['user'],feedback=feedback,repaired_C=text,actual_gate_exit_code=check.returncode,actual_gate_log=(out/'gate.log').read_text()[-6500:]),ensure_ascii=False);save(out/'reviewer-request.json',dict(system=rs,user=ru,model='advertising-scholar',temperature=0,reasoning='off',max_output_tokens=700));review=lab.generate('game',rs,ru,700);save(out/'reviewer.json',review)
            (out/'prompts-and-responses.txt').write_text('AUTHOR REPAIR\nSYSTEM:\n'+system+'\nUSER:\n'+prompt+'\nRESPONSE:\n'+a['text']+'\n\nREVIEWER\nSYSTEM:\n'+rs+'\nUSER:\n'+ru+'\nRESPONSE:\n'+review['text']+'\n')
            state.update(status='terminal_one_local_geometry_select_repair_pending_coordinator_review',reviewer_seconds=review['seconds']);mark();print(state['status'],state['raw_repair_gate_pass'],review['text'],flush=True)
        except BaseException as e:state.update(status='terminal_local_geometry_select_repair_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
