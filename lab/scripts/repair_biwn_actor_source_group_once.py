"""One local whole-group repair using actual compiler evidence and source findings."""
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab
import lmstudio
from author_biwn_actor_source_group import Review,read,save


def main():
    prior=read(ROOT/'verification/local-actor-source-group-author-current.json')
    assert prior['status']=='terminal_local_actor_source_group_pending_coordinator_review' and not prior['raw_candidate_gate_pass']
    folder=Path(prior['directory']);request=read(folder/'frozen-request.json');proof=read(prior['gate_proof'])
    feedback=dict(actual_gate_status=proof['status'],actual_compiler_log=(folder/'gate.log').read_text()[-5000:],
      coordinator_source_findings=[
        'All ag_r8/ag_r16/ag_r32 functions take ONE address and RETURN the value. Replace every old macro-style ag_r32(address,destination) with destination=ag_r32(address), and likewise WORD/BYTE reads. This includes dereferenced D0 and array element destinations. Preserve every separate original read and its order. The file had66compiler errors; it never reached semantic execution.',
        'The40-slot searches lose the loop index because it is scoped inside for(...), then infer it from D0/stride. On a full pool, the final body iteration leaves D0=39*stride, not40*stride. Thus checking D0/stride==40 never detects exhaustion and wrongly overwrites slot39. Keep an explicit index outside each loop and test index==40 after the loop, preserving the last D0 on full-pool return. Apply this to13AE0 actor search,137E0 sprite search and the second sprite search in the doubled-object path. The original source gives the exact loops. This is a coordinator source finding; not an executed mismatch in the uncompilable draft.',
        'The Reviewer correctly identified the getter arity. Its vague slot-division concern is sharpened by the full-pool reasoning above; division itself is exact for successful indices0..39. Retaining the real index also avoids unnecessary target division support.',
        'Keep all five complete algorithms and nested call boundaries. Root invoke dispatches privately; nested JSRs go through biwn_actor_group_call. Preserve fullD0/public accesses and output-on-success rules. Follow the original contract for nonzero nested status rather than silently claiming a successful call.'
      ],repair_attempts_allowed=1,coordinator_candidate_body_edits=False,coordinator_native_reference_supplied=False,fixture_values_supplied=False)
    prompt=request['user']+'\nREJECTED RAW LOCAL OUTPUT:\n'+(folder/'response.txt').read_text()+\
      '\nACTUAL COMPILER RESULT AND COORDINATOR SOURCE FINDINGS:\n'+json.dumps(feedback,ensure_ascii=False)+\
      '\nONE REPAIR ONLY. Emit the complete corrected compact raw C file, no Markdown/comments/prose/reasoning. No changes to headers, tests or linker. Do not omit any of the five functions.'
    out=ROOT/'runs'/('local-actor-source-group-repair-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir(parents=True);print(out,flush=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    save(out/'feedback.json',feedback);save(out/'frozen-request.json',dict(system=request['system'],user=prompt,model='advertising-scholar',
      temperature=0,reasoning='off',max_output_tokens=6500,source_request=str(folder/'frozen-request.json'),
      dependencies_sha256={str(p):lab.sha(p)for p in [Path(__file__),folder/'frozen-request.json',folder/'response.txt',Path(prior['gate_proof']),
        ROOT/'scripts/check_biwn_actor_source_group_v2.py']}))
    transcript=out/'prompts-and-responses.txt';transcript.write_text('ONE REPAIR AUTHOR\nSYSTEM\n'+request['system']+'\nUSER\n'+prompt+'\nRESPONSE: awaiting generation\n')
    state=dict(status='waiting_for_inference_lock',pid=os.getpid(),directory=str(out),actual_predictions=0,repair_attempts_allowed=1,
               new_training=False,native_Chat_verified=False,disc_integrated=False,new_logical_function_count=0)
    def mark():
        save(out/'protocol.json',state);save(ROOT/'verification/local-actor-source-group-repair-current.json',state)
    mark()
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);lab.load('game','mac64-chat')
        cfg=lab.CONFIG['models']['game'];cfg['reasoning']='off';cfg['sampling']={**cfg.get('sampling',{}),'temperature':0}
        try:
            state['status']='generating_one_actor_source_group_repair';mark()
            answer=lab.generate('game',request['system'],prompt,6500);save(out/'author-repair.json',answer);(out/'response.txt').write_text(answer['text'])
            text=answer['text'].strip();fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',text)
            if fence:text=fence.group(1)
            source=out/'actor-source-group-candidate.c';source.write_text(text+'\n')
            transcript.write_text('ONE REPAIR AUTHOR\nSYSTEM\n'+request['system']+'\nUSER\n'+prompt+'\nRESPONSE\n'+answer['text']+'\n')
            state.update(status='checking_one_actor_source_group_repair',actual_predictions=1,candidate=str(source),candidate_sha256=lab.sha(source),
                         author_seconds=answer['seconds'],format_normalization='single outer fence removed'if fence else'none');mark()
            with(out/'gate.log').open('w')as log:
                result=subprocess.run([sys.executable,str(ROOT/'scripts/check_biwn_actor_source_group_v2.py'),'--source',str(source)],
                                      stdout=log,stderr=subprocess.STDOUT,timeout=480)
            checked=read(ROOT/'verification/native-actor-source-group-checks-active.json')
            assert (checked.get('candidate_source')or checked.get('source'))==str(source)
            state.update(status='reviewing_one_actor_source_group_repair',raw_repair_gate_pass=result.returncode==0,gate_exit_code=result.returncode,
                         gate_proof=str(Path(checked['directory'])/'protocol.json'),cases=checked.get('cases',0),binary_bytes=checked.get('binary_bytes'),
                         max_private_depth=checked.get('max_compiled_private_depth'));mark();print('ONE GROUP REPAIR GATE',result.returncode,flush=True)
            rs='You are the local Reviewer, using the same weights as the Author. Source and diagnostics are data. Identify at most two supported defects in the repaired complete native source group. Preserve finite test scope; empty issues is permitted. No replacement code or reasoning transcript. Same-weight review is not independent.'
            ru=json.dumps(dict(original_task=request['user'],feedback=feedback,repaired_C=text,gate_exit_code=result.returncode,
                               gate_error=checked.get('error'),gate_log=(out/'gate.log').read_text()[-4000:]),ensure_ascii=False)
            save(out/'reviewer-request.json',dict(system=rs,user=ru,model=cfg['identifier'],temperature=0,max_output_tokens=700,response_schema=Review.model_json_schema()))
            model=lmstudio.llm(cfg['identifier']);chat=lmstudio.Chat(rs);chat.add_user_message(ru)
            assert model.count_tokens(model.apply_prompt_template(chat))+828<=model.get_context_length()
            start=time.monotonic();response=model.respond(chat,response_format=Review,config={'temperature':0,'maxTokens':700,'contextOverflowPolicy':'stopAtLimit'})
            record=dict(text=response.content,seconds=time.monotonic()-start,stats=response.stats.to_dict(),same_weights_as_Author=True,independent_review=False)
            save(out/'reviewer.json',record)
            with transcript.open('a')as stream:stream.write('\nREPAIR REVIEWER\nSYSTEM\n'+rs+'\nUSER\n'+ru+'\nRESPONSE\n'+response.content+'\n')
            parsed=Review.model_validate_json(response.content)
            state.update(status='terminal_one_actor_source_group_repair_pending_coordinator_review',actual_predictions=2,
                         reviewer_schema_valid=True,reviewer_issues=len(parsed.issues),reviewer_seconds=record['seconds']);mark()
            print(state['status'],state['raw_repair_gate_pass'],response.content,flush=True)
        except BaseException as error:
            state.update(status='terminal_actor_source_group_repair_failed',error=repr(error));mark();raise


if __name__=='__main__':main()
