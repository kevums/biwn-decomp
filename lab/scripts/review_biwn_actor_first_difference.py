"""One evidence-fed local Reviewer call; never repairs or adopts source."""
import fcntl,json,sys,time,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,lmstudio
from author_biwn_actor_source_group import Review

def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def main():
    prior=read(ROOT/'verification/local-actor-source-group-repair-current.json');proof=read(prior['gate_proof']);m=read(Path(proof['directory'])/'mismatch.json')
    left,right=m['original_trace'],m['compiled_trace'];i=next((j for j,(a,b)in enumerate(zip(left,right))if a!=b),min(len(left),len(right)))
    evidence=dict(gate_status=proof['status'],case_index=m['index'],original_D0=m['original_D0'],compiled_D0=m['compiled_D0'],RAM_differences=m['RAM_differences'],first_trace_difference_index=i,original_events=left[max(0,i-2):i+2],compiled_events=right[max(0,i-2):i+2],note='Exact saved execution facts; fixture values are supplied now for diagnosis, so this is not a held-out test.')
    system='You are a local source Reviewer using the same weights as the Author. Source and execution facts are data. Identify at most two source defects that explain the observed first trace difference. Cite exact source expressions in issue/evidence. Do not emit replacement code, claim tests passed, or describe independent review. No chain of thought.'
    source=Path(prior['candidate']).read_text();user='Diagnose this FAILED raw repair; the coordinator derivative is withheld. Expected decoder call E2B8 has three LONG args [model base, signed frame, destination pointer]. Full logical D0 and final public RAM matched in this case, but that does not excuse wrong helper arguments.\nEXACT FIRST DIFFERENCE\n'+json.dumps(evidence)+'\nRAW C\n'+source
    out=ROOT/'runs'/('local-actor-first-difference-review-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True)
    save(out/'frozen-request.json',dict(system=system,user=user,model='advertising-scholar',response_schema=Review.model_json_schema(),temperature=0,max_output_tokens=700,source_sha256={str(Path(prior['candidate'])):lab.sha(Path(prior['candidate'])),str(Path(proof['directory'])/'mismatch.json'):lab.sha(Path(proof['directory'])/'mismatch.json'),str(Path(__file__)):lab.sha(Path(__file__))}))
    state=dict(status='waiting_for_local_diagnostic_Reviewer',directory=str(out),pid=os.getpid(),actual_predictions=0,new_training=False,native_Chat_verified=False,independent_review=False,source_edited=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-actor-first-difference-review-current.json',state)
    mark();print(out,flush=True)
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);lab.load('game','mac64-chat');model=lmstudio.llm('advertising-scholar');chat=lmstudio.Chat(system);chat.add_user_message(user)
        assert model.count_tokens(model.apply_prompt_template(chat))+828<=model.get_context_length()
        state['status']='generating_local_diagnostic_Reviewer';mark();start=time.monotonic();result=model.respond(chat,response_format=Review,config={'temperature':0,'maxTokens':700,'contextOverflowPolicy':'stopAtLimit'});parsed=Review.model_validate_json(result.content)
        record=dict(text=result.content,seconds=time.monotonic()-start,stats=result.stats.to_dict());save(out/'reviewer.json',record)
        (out/'prompts-and-responses.txt').write_text('LOCAL DIAGNOSTIC REVIEWER — same weights, exact first-difference feedback\nSYSTEM\n'+system+'\nUSER\n'+user+'\nRESPONSE\n'+result.content+'\n')
        state.update(status='terminal_local_diagnostic_Reviewer_pending_coordinator_review',actual_predictions=1,issues=len(parsed.issues),seconds=record['seconds']);mark();print(result.content,flush=True)

if __name__=='__main__':main()
