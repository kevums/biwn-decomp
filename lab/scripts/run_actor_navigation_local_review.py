"""Sequential localhost role checks while native UI is locked; no Chat injection."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,fcntl,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
lock=(ROOT/'runs/.inference.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
out=ROOT/'runs'/('actor-navigation-local-review-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();system='You are a local game restoration analysis role. Use only supplied source. Be concise; identify uncertainty. Do not invent bytecode, execution, tool calls, source facts or independent verification. Original CPU comparison decides C acceptance.'
prompts=[('Analyst','ROLE: ANALYST. Supplied M68000 F368: MOVE.L A2,-(A7); MOVE.L D2,-(A7); MOVEA.L12(A7),A1; CLR.W D0; MOVE.B111(A1),D0. Heading1 takes the early return. Return sequence MOVE.L(A7)+,D2; MOVEA.L(A7)+,A2; RTS. Incoming D0=0xAABBCCDD,D2=0x80000000,SR=0x0011. Report final full D0, SR, D2 and whether final N/Z follow D0 or restored D2. Under65words. Do not invent execution.'),('Reviewer','ROLE: REVIEWER. Supplied waypoint arithmetic: MOVE.L coordinate,D0; ANDI.W0xFC00,D0; MOVE.W extent,D1; ASL.W6,D1; MOVEA.L D0,A2; LEA(A2,D1.W),A2; MOVE.L A2,D0; MOVEQ32,D2; OR.L D2,D0. Does masking clear the upper16coordinate bits? Does the shifted extent sign-extend from16or32bits? Answer under50words. Use only supplied instructions; no execution claims.')]


rows=[]
try:
 for role,prompt in prompts:
  save(out/'status.json',{'status':'running','role':role});result=lab.generate('advertising',system,prompt,256,model='advertising-scholar');row={'role':role,'system':system,'prompt':prompt,**result};rows.append(row);save(out/(role+'.json'),row)
 save(out/'review.json',{'rows':rows,'scope':'Two sequential roles, same27Bbase, localhost API while UI locked. Not native Chat history; no model code accepted. Coordinator must review answers.'});(out/'prompts-and-responses.txt').write_text('LOCAL API — ACTOR REVIEW WHILE UI LOCKED\n\n'+ '\n\n'.join('ROLE\n'+r['role']+'\nSYSTEM\n'+r['system']+'\nUSER\n'+r['prompt']+'\nRESPONSE\n'+r['text'] for r in rows)+'\n');save(out/'status.json',{'status':'terminal_generated_review_pending'});save(ROOT/'verification/actor-navigation-local-review-current.json',{'directory':str(out),'status':'terminal_generated_review_pending'});print(json.dumps({'directory':str(out),'responses':[r['text']for r in rows]}))
except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
