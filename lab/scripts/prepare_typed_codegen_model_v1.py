"""Warm the configured local base for the one-click typed code workflow;no prediction."""
import fcntl,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat

def main():
 qualification=json.loads((ROOT/'verification/typed-deck-primitives-v1-current.json').read_text());assert qualification['completed']==8320
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise SystemExit('Another local model job is active. Retry when it finishes.')
  lms=str(Path.home()/'.lmstudio/bin/lms');catalog=json.loads(subprocess.check_output([lms,'ps','--json'],cwd='/',text=True));assert all(x['status']=='idle'and x.get('queued',0)==0 for x in catalog),'Preserve the active model request'
  expected=assistant_chat.lab.CONFIG['models']['advertising']['model_key'];selected=[x for x in catalog if x['modelKey']==expected and x['contextLength']==32768 and x['parallel']==1]
  if len(selected)!=1:assistant_chat.ensure_model('advertising')
  assistant_chat.lab.ensure_server();catalog=json.loads(subprocess.check_output([lms,'ps','--json'],cwd='/',text=True));selected=[x for x in catalog if x['modelKey']==expected and x['contextLength']==32768 and x['parallel']==1];assert len(selected)==1
  state=dict(status='terminal_local_typed_code_model_ready_no_prediction',recorded_at=datetime.now(timezone.utc).isoformat(),model_key=expected,identifier=selected[0]['identifier'],context_length=32768,parallel=1,typed_primitive_cases=8320,new_predictions=0,new_training=False,source_or_model_promotion=False)
  (ROOT/'verification/typed-code-model-ready-v1-current.json').write_text(json.dumps(state,indent=2)+'\n');print('Local code model ready. The complete test uses Author, CPU/RAM checks, and at most one Repair. No automatic source or weight promotion.',flush=True)
if __name__=='__main__':main()
