"""Run reviewed pilot and always restore the daily LMStudio model."""
import subprocess,json,fcntl
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];dataset=json.loads((ROOT/'verification/game-source-v4b-dataset.json').read_text());lms=str(Path.home()/'.lmstudio/bin/lms');cmd=[sys.executable,str(ROOT/'scripts/train.py'),'game',dataset['directory'],'--repo','lmstudio-community/Qwen3.8-27B-MLX-6bit','--iters','64','--num-layers','2','--max-seq-length','1024','--learning-rate','0.00001','--reasoning-off','--cache-limit-gb','2','--wall-budget-seconds','1800'];record={'status':'starting','dataset':dataset,'command':cmd,'promotion':'unpromoted; native/code/scope evaluation required','daily_default_changed':False,'recovery_from':str(ROOT/'verification/game-source-v4-second-oom.json'),'recovery_scope':'New run from base with two layers, 1024-token sequences, exact target partitioning and 2GiB free-cache cap; not an optimizer continuation of either failed run'};pointer=ROOT/'verification/game-source-v4b-run-current.json';pointer.write_text(json.dumps(record,indent=2)+'\n')
try:
 result=subprocess.run(cmd,cwd=ROOT);record.update(status='training_completed'if result.returncode==0 else'training_failed',exit_code=result.returncode);pointer.write_text(json.dumps(record,indent=2)+'\n')
finally:
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',check=True);subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',check=True,timeout=300);record['daily_model_restored']=True;pointer.write_text(json.dumps(record,indent=2)+'\n')
raise SystemExit(record.get('exit_code',1))
