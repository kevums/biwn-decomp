"""Two fresh unpromoted updates to verify the moved game's training runtime.
Use the reviewed full geometry curriculum without truncation or held-out scoring.
This proves copied training capability, not model quality or completed training.
"""
import argparse,fcntl,hashlib,json,os,signal,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
PACKAGE=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preflight-only',action='store_true');args=ap.parse_args();w=PACKAGE/'workbench';out=w/'runs/copied-game-training-check-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='preparing',directory=str(out),pid=os.getpid(),optimizer_updates=0,new_training=False,base_weights_modified=False,adapter_promoted=False,quality_evaluated=False,scope=__doc__)
 def mark():save(out/'protocol.json',state);save(w/'verification/copied-game-training-check-v1-current.json',state)
 mark();origin=read(PACKAGE/'origin.json');old=Path(origin['original_workbench'])/'runs/.inference.lock';coordination=old if old.is_file()else PACKAGE/'.machine-inference.lock';lms=Path.home()/'.lmstudio/bin/lms'
 def cli(*items):return json.loads(subprocess.check_output([str(lms),*items],text=True,cwd='/',timeout=60))
 with coordination.open('a')as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:state.update(status='terminal_shared_slot_busy_zero_updates',coordination_lock=str(coordination));mark();return
  with(w/'runs/.inference.lock').open('a')as local:
   try:fcntl.flock(local,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:state['status']='terminal_package_slot_busy_zero_updates';mark();return
  before=cli('ps','--json');save(out/'loaded-models-before.json',before);bindings=read(PACKAGE/'portable-model-bindings.json')['models']['daily_base'];allowed={'local/advertising-qwen38',bindings['model_key']}
  assert len(before)<=1 and all(m['modelKey']in allowed and m['status']=='idle'and m.get('queued',0)==0 for m in before),'Preserve active or unrelated loaded models'
  data=w/'training/game/geometry-v4-20261020T164053.588459Z';manifest=read(data/'split-manifest.json');assert manifest['domain']=='game'and manifest['tokenizer_settings']['enable_thinking']is False
  for split,digest in manifest['split_sha256'].items():assert sha(data/(split+'.jsonl'))==digest
  groups=[set(manifest['source_groups'][name])for name in ['train','valid','test']];assert all(not(groups[i]&groups[j])for i in range(3)for j in range(i+1,3))
  preflight=read(data/'token-preflight.json');maximum=max(row['tokens']for row in preflight);assert maximum<=8960
  weights=PACKAGE/bindings['relative_weights'];files=sorted(weights.glob('*.safetensors'));assert len(files)==5;digests={str(path):sha(path)for path in files};save(out/'base-resource-hashes-before.json',digests)
  python=PACKAGE/'runtime/.venv/bin/python3.12';command=[str(python),str(w/'scripts/train.py'),'game',str(data),'--repo','lmstudio-community/Qwen3.8-27B-MLX-6bit','--iters','2','--num-layers','1','--max-seq-length','8960','--learning-rate','1e-5','--reasoning-off','--cache-limit-gb','2','--target-head-chunk','64','--eager','--wall-budget-seconds','600']
  state.update(status='preflight_pass',coordination_lock=str(coordination),package=str(PACKAGE),copied_weights=str(weights),data=str(data),training_command=command,maximum_complete_example_tokens=maximum,model_state_before=before);mark()
  if args.preflight_only:state['status']='terminal_copied_training_preflight_pass_zero_updates';mark();print(state['status']);return
  jobs=data/'jobs';prior=set(jobs.iterdir())if jobs.exists()else set();env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']};env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HOME=str(PACKAGE/'runtime/cache/huggingface'),XDG_CACHE_HOME=str(PACKAGE/'runtime/cache'))
  child=None;failure=None
  try:
   with(out/'training-run.log').open('w')as log:
    child=subprocess.Popen(command,cwd='/',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);state.update(status='training',child_pid=child.pid,new_training=True);mark();code=child.wait(timeout=675)
   created=set(jobs.iterdir())-prior;assert len(created)==1;job=created.pop();result=read(job/'training-result.json');state['job']=str(job);assert code==0 and result['status']=='pilot_adapter_created_unpromoted',result
   reports=[json.loads(line)for line in (job/'training-memory.jsonl').read_text().splitlines()];iterations=[row.get('iteration')for row in reports];assert iterations==[1,2],iterations
   adapters=list((job/'adapters').glob('*.safetensors'));assert adapters and result['adapter_files'];after={str(path):sha(path)for path in files};assert after==digests,'Base weights changed';save(out/'base-resource-hashes-after.json',after);save(out/'training-result.json',result)
   state.update(status='terminal_copied_training_two_updates_unpromoted',optimizer_updates=2,training_reports=reports,adapters={str(path):sha(path)for path in adapters},base_weights_modified=False)
  except BaseException as error:
   failure=error
   if child is not None and child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
   state.update(status='terminal_copied_training_failed_unpromoted',error=repr(error))
  finally:
   state['child_pid']=None;loaded=cli('ps','--json')
   if not loaded and before:
    model=before[0];restore=subprocess.run([str(lms),'load',model['modelKey'],'--identifier',model['identifier'],'--context-length',str(model['contextLength']),'--parallel',str(model['parallel']),'--ttl','3600','--yes'],capture_output=True,text=True,cwd='/',timeout=300);(out/'model-restore.log').write_text(restore.stdout+restore.stderr);state['previous_model_restored']=restore.returncode==0;assert restore.returncode==0,restore.stderr
   else:state['previous_model_restored']=not before and not loaded
   state['loaded_models_after']=cli('ps','--json');mark()
  print(state['status'],flush=True)
  if failure:raise failure
if __name__=='__main__':
 try:main()
 except BaseException as error:
  pointer=PACKAGE/'workbench/verification/copied-game-training-check-v1-current.json'
  if pointer.exists():
   state=read(pointer)
   if state.get('pid')==os.getpid()and not state['status'].startswith('terminal_'):
    state.update(status='terminal_copied_training_preflight_failed_zero_updates'if not state['new_training']else'terminal_copied_training_failed_unpromoted',error=repr(error));save(pointer,state);save(Path(state['directory'])/'protocol.json',state)
  raise
