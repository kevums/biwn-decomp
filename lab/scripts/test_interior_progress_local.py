"""Sequential local Analyst/Reviewer output test; not native Chat or code authorship."""
import fcntl,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main():
 out=ROOT/'verification/interior-local-output'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 evidence=json.loads((ROOT/'verification/biwn-gpu-interior-checks.json').read_text());protocol=dict(status='running',interface='localhost native REST reasoning off; not LM Studio Chat',model='advertising-scholar',same_model_sequential_roles=True,weights_trained=False,code_authorship='coordinator; local roles only explain and review supplied evidence',evidence=evidence,roles=[]);save(out/'protocol.json',protocol);print(out,flush=True)
 task='In under80words, answer Kevin: Does this result mean the rebuilt game interiors are playable now? Explain the new test result and the next required step in plain language. Do not invent elapsed time, a completion percentage or an ETA. The existing main checkpoint remains130components; these two standalone GPU candidates are not added to it. Native LM Studio Chat is still unverified.'
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0 and models[0]['contextLength']==32768,models
  prior=''
  for role in ['analyst','reviewer']:
   system=lab.COMMON+'\n'+lab.ROLES['game'][role]
   user=task+'\n\nSUPPLIED DETERMINISTIC TEST EVIDENCE:\n'+json.dumps(evidence)
   if role=='reviewer':user+='\n\nDRAFT TO CHECK, NOT AUTHORITY:\n'+prior+'\nReturn only a corrected final answer meeting the task. Explicitly correct any unsupported claim.'
   result=lab.generate('advertising',system,user,400,model='advertising-scholar');result.update(role=role,system=system,user=user,word_count=len(result['text'].split()));maximum=lab.requested_maximum_words(task)
   if result['word_count']>maximum:result['quality_flags'].append('word_limit_exceeded')
   prior=result['text'];protocol['roles'].append(result);save(out/f'{role}.json',result);save(out/'protocol.json',protocol);print(role,result['seconds'],result['word_count'],result['quality_flags'],flush=True)
 protocol['status']='mechanical_flags_require_review'if any(x['quality_flags']for x in protocol['roles'])else'completed_pending_coordinator_semantic_review';save(out/'protocol.json',protocol)
 (out/'prompts-and-responses.txt').write_text(protocol['interface']+'\nSame27Bweights in two fresh contexts; not independent models.\n\n'+'\n\n'.join(x['role'].upper()+'\nSYSTEM:\n'+x['system']+'\nUSER:\n'+x['user']+'\nRESPONSE:\n'+x['text']for x in protocol['roles'])+'\n');save(ROOT/'verification/interior-local-output-current.json',dict(directory=str(out),status=protocol['status']))
if __name__=='__main__':main()
