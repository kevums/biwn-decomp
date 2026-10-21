"""Reproducible, unpromoted pilot training; serialized against workbench inference."""
import argparse
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import os
import signal

ROOT=Path(__file__).resolve().parent.parent

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('domain',choices=['game','advertising']);p.add_argument('data',type=Path)
 p.add_argument('--repo',help='Explicit base repository from an installed model lock; otherwise domain default')
 p.add_argument('--iters',type=int,default=200);p.add_argument('--max-seq-length',type=int,default=1024)
 p.add_argument('--num-layers',type=int,default=2);p.add_argument('--learning-rate',type=float,default=1e-5)
 p.add_argument('--reasoning-off',action='store_true',help='Render dataset with enable_thinking=False in a process-local tokenizer wrapper')
 p.add_argument('--cache-limit-gb',type=float,help='Process-local MLX free-cache cap; requires reasoning-off wrapper')
 p.add_argument('--wall-budget-seconds',type=int,default=1800)
 p.add_argument('--target-head-chunk',type=int,help='Experimental batch1 full-context suffix loss with checkpointed output-head chunks')
 p.add_argument('--eager',action='store_true',help='Process-local MLX_DISABLE_COMPILE=1 for the experimental full-context pilot')
 a=p.parse_args()
 if a.target_head_chunk is not None and (a.target_head_chunk<1 or not a.reasoning_off):raise ValueError('Head chunk requires positive size and reasoning-off wrapper')
 if a.eager and a.target_head_chunk is None:raise ValueError('Eager profile currently requires validated target-head loss')
 if a.cache_limit_gb is not None and (a.cache_limit_gb<0 or not a.reasoning_off):raise ValueError('Cache cap must be nonnegative and use the process-local reasoning-off wrapper')
 data=a.data.expanduser().resolve()
 if min(a.iters,a.max_seq_length,a.num_layers,a.wall_budget_seconds)<=0 or a.learning_rate<=0:raise ValueError('Training settings must be positive')
 config=json.loads((ROOT/'config.json').read_text())
 repo=a.repo or config['models'][a.domain]['repo']
 locked=list({(m['repo'],m['revision']):m for name in ['models.lock.json','candidate-models.lock.json'] for m in json.loads((ROOT/name).read_text()) if m['repo']==repo}.values())
 if len(locked)!=1:raise ValueError('Base must occur exactly once in installed model locks')
 model=Path.home()/'.lmstudio/models'/repo
 if not (model/'config.json').is_file():raise ValueError('Base model is not installed')
 for name in ['split-manifest.json','train.jsonl','valid.jsonl','test.jsonl']:
  if not (data/name).is_file() or not (data/name).stat().st_size:raise ValueError('Prepare reviewed data with lab prepare-training first')
 manifest=json.loads((data/'split-manifest.json').read_text())
 if manifest['domain']!=a.domain:raise ValueError('Dataset domain mismatch')
 if manifest.get('tokenizer_settings',{}).get('enable_thinking') is False and not a.reasoning_off:
  raise ValueError('This dataset requires explicit --reasoning-off rendering')
 groups=[set(manifest['source_groups'][k]) for k in ['train','valid','test']]
 if any(groups[i]&groups[j] for i in range(3) for j in range(i+1,3)):raise ValueError('Source-group leakage')
 for name,digest in manifest['split_sha256'].items():
  if sha(data/f'{name}.jsonl')!=digest:raise ValueError('Prepared dataset changed after splitting')
 preflight=data/'token-preflight.json'
 if preflight.exists():
  lengths=json.loads(preflight.read_text());maximum=max(row['tokens']for row in lengths)
  if maximum>a.max_seq_length:raise ValueError(f'Prepared examples reach {maximum} tokens, exceeding requested {a.max_seq_length}. No truncation allowed: partition complete targets or use an explicitly tested larger training profile.')
 if a.cache_limit_gb is None and a.reasoning_off:a.cache_limit_gb=2
 run=data/'jobs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 run.mkdir(parents=True)
 command=[sys.executable,'-m','mlx_lm','lora','--model',str(model),'--train','--data',str(data),
          '--adapter-path',str(run/'adapters'),'--batch-size','1','--num-layers',str(a.num_layers),
          '--max-seq-length',str(a.max_seq_length),'--iters',str(a.iters),'--learning-rate',str(a.learning_rate),
          '--grad-checkpoint','--mask-prompt','--seed','17','--steps-per-report','1',
          '--steps-per-eval','8','--val-batches','-1','--save-every','8']
 if a.reasoning_off:
  command=[sys.executable,str(ROOT/'scripts/mlx_lora_reasoning_off.py')]+command[4:]
 metadata={'base':locked[0],'domain':a.domain,'data':str(data),'dataset_manifest_sha256':sha(data/'split-manifest.json'),
           'model_config_sha256':sha(model/'config.json'),'command':command,'status':'waiting_for_inference_lock',
           'review_kinds':manifest.get('review_kinds',[]),'promotion':'Unpromoted pilot; compare base and adapter on held-out tasks before any default switch.'}
 metadata.update(cache_limit_bytes=None if a.cache_limit_gb is None else int(a.cache_limit_gb*1024**3),reasoning_off=a.reasoning_off,wall_budget_seconds=a.wall_budget_seconds)
 metadata['target_head_chunk']=a.target_head_chunk
 metadata['MLX_DISABLE_COMPILE']=a.eager
 if a.target_head_chunk is not None:
  metadata['target_loss_sha256']=sha(ROOT/'scripts/target_chunk_loss.py')
  metadata['longest_training_example_first']=True
 if a.reasoning_off:metadata['tokenizer_wrapper_sha256']=sha(ROOT/'scripts/mlx_lora_reasoning_off.py')
 def status(value):
  metadata['status']=value;(run/'training-result.json').write_text(json.dumps(metadata,indent=2))
 status('waiting_for_inference_lock');print(run,flush=True)
 with (ROOT/'runs/.inference.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  subprocess.run([str(Path.home()/'.lmstudio/bin/lms'),'unload','--all'],cwd=Path.home()/'.lmstudio',check=True,timeout=120)
  status('training')
  with (run/'training.log').open('w') as log:
   process_env=dict(os.environ)
   if a.reasoning_off:process_env['LOCAL_AI_BATCH_AUDIT_PATH']=str(run/'training-batches.jsonl')
   if a.target_head_chunk is not None:
    process_env['LOCAL_AI_TARGET_HEAD_CHUNK']=str(a.target_head_chunk)
    process_env['LOCAL_AI_LONGEST_FIRST']='1'
   if a.eager:process_env['MLX_DISABLE_COMPILE']='1'
   if metadata['cache_limit_bytes']is not None:process_env['LOCAL_AI_TRAIN_CACHE_BYTES']=str(metadata['cache_limit_bytes'])
   process=subprocess.Popen(command,env=process_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,start_new_session=True)
   metadata['pid']=process.pid;status('training')
   def expire():
    if process.poll() is None:
     metadata['wall_budget_expired']=True
     try:os.killpg(process.pid,signal.SIGTERM)
     except ProcessLookupError:return
     try:process.wait(timeout=5)
     except subprocess.TimeoutExpired:
      try:os.killpg(process.pid,signal.SIGKILL)
      except ProcessLookupError:pass
   timer=threading.Timer(a.wall_budget_seconds,expire);timer.daemon=True;timer.start()
   try:
    for line in process.stdout:
     print(line,end='',flush=True);log.write(line);log.flush()
    code=process.wait()
   finally:timer.cancel()
  metadata['exit_code']=code
  if code:
   status('training_failed');raise SystemExit(code)
  metadata['adapter_files']={str(p.relative_to(run)):sha(p) for p in (run/'adapters').glob('*') if p.is_file()}
  status('pilot_adapter_created_unpromoted')

if __name__=='__main__':main()
