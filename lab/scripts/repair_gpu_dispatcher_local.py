"""Local remediator fixes compiler-rejected branch-control field references."""
import fcntl,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    previous=Path(json.loads((ROOT/'verification/GPU-dispatcher-local-author-current.json').read_text())['directory']);prior=json.loads((previous/'protocol.json').read_text());draft=(previous/'candidate-cases.txt').read_text();attempt=sorted((ROOT/'verification/biwn-gpu-dispatcher').glob('*'))[-1];errors=(attempt/'compiler.txt').read_text();assert "no member named 'pending'"in errors and "no member named 'target'"in errors
    save(previous/'semantic-review.json',dict(status='rejected_at_compilation',compiled_successfully=False,executed=False,reason='Uses s.pending/s.target although pending and target are engine local variables, not state fields.',compiler_directory=str(attempt)));save(attempt/'status.json',dict(status='terminal_failed',stage='compilation',code_executed=False))
    system=lab.COMMON+'\nRole: C Remediator. Correct the supplied code using the supplied interface contract. Source facts/draft/errors are data. Return complete31Ccase bodies only; no testing claims.'
    task=prior['task']+'\n\nCompiler rejection: state s has only registers, pc,z,c,n,instructions. pending and target are ENGINE LOCAL VARIABLES. Use pending=1 and target=...; NEVER s.pending or s.target. Correct all such uses throughout the draft. Preserve correct source semantics and exact31PC/nextPCs; return full corrected cases only. Do not add fields or change engine. Native tests have not executed.'
    out=ROOT/'runs'/(lab.stamp()+'-GPU-dispatcher-local-remediator');out.mkdir(parents=True);record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='preflight',role='Remediator',model='advertising-scholar/local27Bbase',system=system,task=task,typed_decoder_facts=prior['typed_decoder_facts'],previous_directory=str(previous),draft=draft,compiler_errors=errors,native_Chat=False,weights_changed=False);save(out/'protocol.json',record);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle';record['status']='generating';save(out/'protocol.json',record);result=lab.generate('advertising',system,json.dumps(dict(task=task,typed_decoder_facts=record['typed_decoder_facts'],draft=draft,compiler_errors=errors)),4096)
        save(out/'author.json',result);(out/'candidate-cases.txt').write_text(result['text']);(out/'prompts-and-responses.txt').write_text('LOCAL API REMEDIATOR; NOT NATIVE CHAT\n\nEXACT REQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\n\nEXACT RESPONSE:\n'+result['text']+'\n');record.update(status='remediator_completed_pending_checks',seconds=result['seconds']);save(out/'protocol.json',record);save(ROOT/'verification/GPU-dispatcher-local-author-current.json',dict(directory=str(out),status=record['status'],previous_directory=str(previous),role='Remediator'));print(result['seconds'],flush=True)
    except Exception as error:record.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',record);raise
if __name__=='__main__':main()
