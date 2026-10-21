"""Sequential visible-audit local roles; same model, not independent validation."""
import fcntl,json,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
out=ROOT/'verification/TOC-origin-local-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
source=json.loads((ROOT/'verification/BIWN-TOC-origin-match-current.json').read_text());C=json.loads((ROOT/'verification/BIWN-TOC-local-C-current.json').read_text())
evidence=dict(origin_match=source,C_validation={k:C[k]for k in ['cases_count','baseline_block_checkpoints','null_guards','scope','authorship']},original_game_instruction_case_bodies=171,separate_semantic_firmware_functions=1,new_weight_training=False)
roles=[('Researcher','Explain what this TOC checksum match establishes and what must be checked next. Distinguish the local-model C contribution from the coordinator work. At most120words.'),('Reviewer','Check the previous explanation against supplied evidence. State any unsupported claims and give a corrected plain-English status under90words. Matching a checksum must not imply successful normal boot, hardware validation, or new weight training.')]
rows=[]
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 state=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(state)==1 and state[0]['identifier']=='advertising-scholar'and state[0]['status']=='idle'
 for role,task in roles:
  system=f'You are the local {role} role. You have no tools. Use only supplied evidence, and do not claim execution. Same weights are used for these sequential roles; your review is not independent proof.'
  prompt=task+'\nEVIDENCE\n'+json.dumps(evidence,indent=2)
  if rows:prompt+='\nPRIOR RESEARCHER RESPONSE\n'+rows[-1]['result']['text']
  result=lab.generate('game',system,prompt,768,model='advertising-scholar');row=dict(role=role,system=system,prompt=prompt,result=result,actual_model=state);rows.append(row);(out/(role+'.json')).write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(role=role,seconds=result['seconds'],flags=result['quality_flags'],text=result['text'])),flush=True)
report=dict(directory=str(out),status='generated_coordinator_review_pending',roles=rows,same_weights=True,new_weight_training=False,native_Chat=False)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(out/'prompts-and-responses.txt').write_text('\n\n'.join('ROLE '+x['role']+'\nSYSTEM\n'+x['system']+'\nUSER\n'+x['prompt']+'\nRESPONSE\n'+x['result']['text']for x in rows));(ROOT/'verification/TOC-origin-local-review-current.json').write_text(json.dumps(report,indent=2)+'\n')
