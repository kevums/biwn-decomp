"""Sequential localhost role checks while native UI is locked; no Chat injection."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,fcntl,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
lock=(ROOT/'runs/.inference.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
out=ROOT/'runs'/('actor-local-review-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();system='You are a local game restoration analysis role. Use only supplied source. Be concise; identify uncertainty. Do not invent bytecode, execution, tool calls, source facts or independent verification. Original CPU comparison decides C acceptance.'
prompts=[('Analyst','ROLE: ANALYST. Supplied original13AE0: scan40entityrecords. On each record, D0 is the full slot byte offset (slot*206). If all40records are occupied, the last D0 is0x00001f62; D1 becomes40 andthecaller branches directly to return, without clearingD0 orcalling134DC. Does nonzeroD0 prove an actor was created? Explain under55words. Do not invent execution or bytecode.'),('Reviewer','ROLE: REVIEWER. Supplied original134DC: IDs4..118 index an inline jump table. Some entries target137CA, which clears the initialized record type andreturns; other entries target task-creation handlers, while137DA simply returns. Can the ID range test alone prove a task is spawned? Answer under50words, distinguishing valid table index from task creation. Original CPU checks decide acceptance.')]

rows=[]
try:
 for role,prompt in prompts:
  save(out/'status.json',{'status':'running','role':role});result=lab.generate('advertising',system,prompt,256,model='advertising-scholar');row={'role':role,'system':system,'prompt':prompt,**result};rows.append(row);save(out/(role+'.json'),row)
 save(out/'review.json',{'rows':rows,'scope':'Two sequential roles, same27Bbase, localhost API while UI locked. Not native Chat history; no model code accepted. Coordinator must review answers.'});(out/'prompts-and-responses.txt').write_text('LOCAL API — ACTOR REVIEW WHILE UI LOCKED\n\n'+ '\n\n'.join('ROLE\n'+r['role']+'\nSYSTEM\n'+r['system']+'\nUSER\n'+r['prompt']+'\nRESPONSE\n'+r['text'] for r in rows)+'\n');save(out/'status.json',{'status':'terminal_generated_review_pending'});save(ROOT/'verification/actor-local-review-current.json',{'directory':str(out),'status':'terminal_generated_review_pending'});print(json.dumps({'directory':str(out),'responses':[r['text']for r in rows]}))
except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
