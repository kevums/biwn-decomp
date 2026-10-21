"""One actual local Reviewer feedback pass, separate from the full team test."""
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat
import local_stream_inference_v1 as live
def save(path,data):Path(path).write_text(json.dumps(data,indent=2)+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    prior=json.loads((ROOT/'verification/native-advertising-team-handler-current.json').read_text());session=Path(prior['session']);record=json.loads((session/'session.json').read_text())
    assert [r['role']for r in record['roles']]==['Researcher','Educator','Reviewer']
    question=prior['question'];draft=(session/'3-Reviewer-response.txt').read_text();assert len(draft.split())==73
    helper=ROOT/'scripts/native_chat_team_context.py';request=dict(domain='advertising',query=question)
    p=subprocess.run([str(ROOT/'.venv/bin/python3.12'),str(helper)],input=json.dumps(request)+'\n',capture_output=True,text=True,timeout=60);assert p.returncode==0,p.stderr
    context=json.loads(p.stdout);assert context['status']=='ready'and context['roles'][-1][0]=='Reviewer'
    system=context['common']+'\nYour role: '+context['roles'][-1][1]
    user=json.dumps(dict(question=question,original_source_evidence=context['evidence'],source_brief=record['roles'][0],draft_to_audit=draft),indent=2)
    out=ROOT/'runs'/('Advertising-chronology-feedback-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    save(out/'evidence.json',context);save(out/'request.json',dict(system=system,input=user,prior_session=str(session),prior_session_sha256=sha(session/'session.json'),max_output_tokens=400,reasoning='off',temperature=0))
    state=dict(status='preparing',pid=os.getpid(),directory=str(out),actual_predictions=0,new_training=False,native_Chat_verified=False,full_native_team_retested=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/advertising-chronology-feedback-current.json',state)
    mark()
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);model=assistant_chat.ensure_model('advertising');state['status']='streaming';mark()
        try:
            result=live.generate('advertising',system,user,400,model,out);save(out/'response.json',result);(out/'response.txt').write_text(result['text'])
            (out/'prompts-and-responses.txt').write_text('ACTUAL LOCAL REVIEWER FEEDBACK — NOT A FULL NATIVE CHAT TEAM RETEST\n\nEXACT SYSTEM PROMPT\n'+system+'\n\nEXACT USER PROMPT\n'+user+'\n\nRAW RESPONSE\n'+result['text']+'\n')
            state.update(status='terminal_Reviewer_feedback_pending_source_review',actual_predictions=1,words=len(result['text'].split()),stream=result['stream'],source_sha256={str(path):sha(path)for path in [Path(__file__),helper,ROOT/'advertising_study2a_context_v1.py',out/'request.json',out/'response.json',out/'prompts-and-responses.txt']});mark()
        except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
