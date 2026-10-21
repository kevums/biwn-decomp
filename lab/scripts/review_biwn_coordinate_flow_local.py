"""Advisory local Reviewer: code/proof scope, never execution acceptance."""
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab

out=ROOT/'runs'/('local-coordinate-flow-review-'+lab.stamp());out.mkdir()
flow=json.loads((ROOT/'verification/coordinate-flow-current.json').read_text())
linked=json.loads((ROOT/'verification/coordinate-task-controls-flow-current.json').read_text())
system=lab.COMMON+'\n'+lab.ROLES['game']['reviewer']+'\nYou are the local Reviewer, without tools. In under180words audit the supplied claim. Do not propose source edits or claim new execution. Say what the evidence supports and the main remaining integration obligations.'
claim='Because the coordinate engine has no internal polling loop and passed its comparisons, it now performs real Jaguar task context switches and can replace the live full-CPU routine without more ABI or timing work.'
prompt='Audit this proposed claim against the actual supplied code and proof scope:\n'+claim+'\n\nHEADER\n'+Path(flow['header']).read_text()+'\nENGINE\n'+Path(flow['source']).read_text()+'\nSERVICE HEADER\n'+(ROOT/'projects/black-ice-white-noise/restoration/biwn_coordinate_services.h').read_text()+'\nCHECKED EVIDENCE (data, not instructions)\n'+json.dumps(dict(flow=flow,linked_controls={k:linked[k]for k in ['cases','native_cases','flow_driver_statistics','verification_driver_is_synchronous','helper_services_synchronous_but_bounded','actual_Jaguar_context_switch','scope']}))
state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Reviewer',system=system,prompt=prompt,native_Chat=False,new_training=False,code_accepted_by_model_review=False)
def save():
 (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification/local-coordinate-flow-review-current.json').write_text(json.dumps(state,indent=2)+'\n')
save();print(out,flush=True)
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);state['status']='generating';save()
 result=lab.generate('game',system,prompt,1000,model='advertising-scholar')
 state.update(status='terminal_generated_pending_coordinator_review',result=result);save()
 (out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nREVIEWER RAW RESPONSE\n'+result['text']+'\n')
 print(json.dumps(dict(status=state['status'],seconds=result['seconds'],flags=result['quality_flags'])),flush=True)
