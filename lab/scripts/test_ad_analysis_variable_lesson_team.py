"""Native local Researcher/Educator/Reviewer test over supplied Olsen2001."""
import fcntl,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    task='Using only Lee and Koo (2016), create a short graduate advertising mini-lesson correcting the claim that random assignment of ad conditions makes the reported congruence-by-involvement interaction a causal effect of increasing involvement. Include an explicit learning objective, a concise source-based explanation distinguishing assigned conditions from the actual measured predictor/moderator and measurement timing, and one student question with a 5-point answer key: five distinct independently earned criteria worth one point each, zero for an incorrect criterion. Cite PDF pages. Flag the relevant methods/table/prose label discrepancy without inventing an erratum. Keep the final answer under240words.'
    retrieved=lab.retrieve('advertising','Lee Koo 2016 actual regression predictor average three congruence manipulation check items involvement after stimulus questionnaire analyses Table1',k=16)
    evidence=[e for e in retrieved if Path(e['source']).name=='Lee & Koo (2016).pdf'];assert len(evidence)>=6
    assert any('variable measuring congruence was computed' in e['text']for e in evidence)
    out=ROOT/'verification/advertising-analysis-variable-lesson-team'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    r=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='running',task=task,evidence=evidence,evidence_pages=sorted({e['page']for e in evidence}),model=lab.CONFIG['models']['advertising'],profile='mac64-chat',fresh_role_contexts=True,independent_models=False,trained_adapter=None,interface='Native localhost REST reasoning off; not visible Chat',roles=[])
    save(out/'request.json',r);print(out,flush=True)
    def role(value):
        r['roles'].append(value['role']);save(out/(value['role']+'.json'),value);save(out/'request.json',r)
        with(out/'prompts-and-responses.txt').open('a')as f:f.write(value['role'].upper()+'\nREQUEST\n'+json.dumps(value['request'],ensure_ascii=False,indent=2)+'\nRAW RESPONSE\n'+value['text']+'\nFLAGS\n'+json.dumps(value['quality_flags'])+'\n\n')
        print(json.dumps(dict(role=value['role'],seconds=value['seconds'],flags=value['quality_flags'])),flush=True)
        if value['role']=='reviewer'and 'final_answer'in value:(out/'final.txt').write_text(value['final_answer']+'\n')
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['status']=='idle'and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768 and models[0]['parallel']==1
            lab.advertising_team(task,evidence,1400,role)
        r.update(status='completed_pending_human_source_review',finished_at=datetime.now(timezone.utc).isoformat());save(out/'request.json',r);save(ROOT/'verification/advertising-analysis-variable-lesson-team-current.json',dict(directory=str(out),status=r['status']))
    except Exception as e:r.update(status='terminal_failed',error=repr(e));save(out/'request.json',r);raise
if __name__=='__main__':main()
