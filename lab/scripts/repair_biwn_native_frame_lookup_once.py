"""One local Author repair using actual stride failure;previous output retained."""
import fcntl,json,os,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    previous=json.loads((ROOT/'verification/local-native-frame-lookup-author-current.json').read_text());assert previous['status']=='terminal_local_lookup_kernel_and_review_pending_coordinator_review' and not previous['raw_kernel_gate_pass'];prior=Path(previous['directory']);request=json.loads((prior/'frozen-request.json').read_text());feedback=json.loads((prior/'raw-stride-diagnostic.json').read_text())
    for p,h in request['source_sha256'].items():assert lab.sha(Path(p))==h
    out=ROOT/'runs'/('local-native-frame-lookup-repair-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);print(out,flush=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    prompt=request['user']+'\nPREVIOUS RAW CANDIDATE:\n'+(prior/'response.txt').read_text()+'\nACTUAL VERIFIER FEEDBACK:\n'+json.dumps(feedback,ensure_ascii=False)+'\nOne repair attempt:output the complete corrected scalar C source only. Correct the cause of the concrete access mismatch. Do not modify the supplied ABI,verifier orsource contract.'
    frozen=dict(system=request['system'],user=prompt,model='advertising-scholar',temperature=0,reasoning='off',max_output_tokens=1600,previous=str(prior),previous_response_sha256=lab.sha(prior/'response.txt'),feedback_sha256=lab.sha(prior/'raw-stride-diagnostic.json'),source_sha256={str(p):lab.sha(p) for p in [Path(__file__),ROOT/'scripts/check_biwn_native_frame_lookup_v2.py']},new_training=False,scope='One verifier-feedback development repair of a scalar kernel;ABI is coordinator-supplied. Not an independent test ortraining-gain comparison.')
    save(out/'frozen-request.json',frozen);state=dict(status='waiting_for_lock',pid=os.getpid(),directory=str(out),new_training=False,default_promoted=False,native_Chat_window=False,repair_attempts_allowed=1)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-frame-lookup-repair-current.json',state)
    mark()
    with (ROOT/'runs/.inference.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);lab.load('game','mac64-chat');cfg=lab.CONFIG['models']['game'];cfg['reasoning']='off';cfg['sampling']={**cfg.get('sampling',{}),'temperature':0}
        try:
            state['status']='generating_one_local_repair';mark();result=lab.generate('game',request['system'],prompt,1600);save(out/'author-repair.json',result);(out/'response.txt').write_text(result['text']);source_text=result['text'].strip();m=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',source_text)
            if m:source_text=m.group(1)
            source=out/'frame-lookup-candidate.c';source.write_text(source_text+'\n');state.update(status='checking_raw_repair',candidate=str(source),candidate_sha256=lab.sha(source),author_seconds=result['seconds'],format_normalization='single outer fence removed' if m else 'none');mark()
            with (out/'gate.log').open('w') as log:check=subprocess.run([sys.executable,str(ROOT/'scripts/check_biwn_native_frame_lookup_v2.py'),'--source',str(source),'--no-publish'],stdout=log,stderr=subprocess.STDOUT,timeout=300)
            proof=json.loads((ROOT/'verification/native-frame-lookup-active.json').read_text());assert proof['source']==str(source);state.update(gate_exit_code=check.returncode,raw_repair_gate_pass=check.returncode==0,gate_proof=str(Path(proof['directory'])/'protocol.json'),gate_status=proof['status'],native_cases=proof.get('native_cases',0),changing_tag_cases=proof.get('changing_tag_cases',0));mark()
            review_system='You are the local Code Reviewer. Critique the scalar kernel only against its declared contract andthe recorded access failure. Do not rewrite C. Return JSON issues with line,problem,contract_basis,or {"issues":[]} ifnone. The ABI maps scalar36tooriginal miss outputs;do not call that a bug. Test passing has only its recorded scope.'
            review_prompt=json.dumps(dict(original_task=request['user'],previous_failure=feedback,repaired_kernel=source_text,actual_gate_exit_code=check.returncode,actual_gate_log=(out/'gate.log').read_text()[-8000:]),ensure_ascii=False);save(out/'reviewer-request.json',dict(system=review_system,user=review_prompt,temperature=0,reasoning='off',max_output_tokens=1000));state['status']='generating_local_review_of_repair';mark();review=lab.generate('game',review_system,review_prompt,1000);save(out/'reviewer.json',review)
            (out/'prompts-and-responses.txt').write_text('CODE AUTHOR REPAIR\nSYSTEM:\n'+request['system']+'\nUSER:\n'+prompt+'\nRESPONSE:\n'+result['text']+'\n\nCODE REVIEWER\nSYSTEM:\n'+review_system+'\nUSER:\n'+review_prompt+'\nRESPONSE:\n'+review['text']+'\n')
            state.update(status='terminal_one_local_lookup_repair_pending_coordinator_review',reviewer_seconds=review['seconds']);mark();print(state['status'],state['raw_repair_gate_pass'],review['text'],flush=True)
        except BaseException as e:state.update(status='terminal_local_lookup_repair_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
