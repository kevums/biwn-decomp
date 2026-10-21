"""Actual moved-package inference and one unpromoted copied training update.
Serialize model changes; keep live MCP bytes and restore the live daily model.
"""
import fcntl,json,hashlib,subprocess,os,shutil,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';LMS=Path.home()/'.lmstudio/bin/lms'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ps():return json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True,timeout=30))
def main():
 package=Path(read(V/'portable-current-setup-moved-current.json')['package']);assert read(package/'portable-server-test-current.json')['status']=='terminal_current_moved_four_MCP_servers_GPU_arena_and_source_status_pass';out=V/'portable-current-workflows'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 frozen=package/'workbench/verification/current-biwn-latest-publication-current.json';mcp=Path.home()/'.lmstudio/mcp.json';before=sha(mcp);state=dict(status='prepared_current_portable_workflows',pid=os.getpid(),directory=str(out),package=str(package),jobs=[],new_training=False,new_predictions=0,live_MCP_sha256=before,daily_base_restored=False,quality_gain_claim=False,native_Chat_verified=False)
 def mark():save(out/'protocol.json',state);save(V/'portable-current-workflows-active.json',state)
 def run(name,command,timeout=600):
  log=out/(name+'.log');state['status']='running_'+name;record=dict(name=name,command=command,log=str(log));state['jobs'].append(record);mark();start=time.monotonic()
  with log.open('w')as stream:
   child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,env={k:v for k,v in os.environ.items()if k not in['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']},start_new_session=True);state['child_pid']=child.pid;mark()
   try:code=child.wait(timeout=timeout)
   except subprocess.TimeoutExpired:
    import signal
    os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10);raise
  record.update(exit_code=code,seconds=round(time.monotonic()-start,2));mark();print(name,code,record['seconds'],'seconds',flush=True);assert code==0,(name,str(log));return record
 py=str(package/'runtime/.venv/bin/python');basepy=str(package/'runtime/python/bin/python3.12');workbench=package/'workbench'
 # Copy reviewed training input files without rewriting source/split/manifest bytes.
 source=Path(read(V/'game-source-v4b-run-current.json')['dataset']['directory']);data=workbench/source.relative_to(ROOT);data.mkdir(parents=True,exist_ok=True);input_rows=[]
 for path in[*source.glob('*'),ROOT/'models.lock.json',ROOT/'candidate-models.lock.json']:
  if not path.is_file():continue
  target=workbench/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():assert sha(target)==sha(path)
  else:shutil.copy2(path,target)
  input_rows.append(dict(relative=str(path.relative_to(ROOT)),sha256=sha(target)))
 save(out/'training-inputs.json',input_rows);prior_jobs=set((data/'jobs').glob('*'))if(data/'jobs').exists()else set();mark()
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);loaded=ps();save(out/'before-models.json',loaded);assert all(x['status']=='idle'and x.get('queued',0)==0 for x in loaded),'Preserve active prediction'
  try:
   run('register-and-load-copied-base',[basepy,str(workbench/'portable_models_current.py'),'--load','daily_base'],timeout=360);bindings=read(package/'portable-model-bindings.json');save(out/'actual-model-bindings.json',bindings);loaded=ps();save(out/'copied-base-loaded.json',loaded);assert len(loaded)==1 and loaded[0]['modelKey']==bindings['models']['daily_base']['model_key'] and loaded[0]['identifier']=='advertising-scholar'
   run('game-assistant',[py,'-u',str(workbench/'portable_ask.py'),'game','In two sentences,state what the latest experimental build verifies and what still prevents a complete same-console source rebuild.','--max-tokens','450'])
   run('gpu-output-test',[py,'-u',str(workbench/'portable_current.py'),'gpu','--cold-test'])
   run('Advertising-study-card-roles',[py,'-u',str(workbench/'portable_current.py'),'cards','--packet','schreiner-2026-2a'])
   task='Prepare a20minute undergraduate lesson on Schreiner et al.(2026),Study2A. Distinguish recruitment,between-person and within-person factors,randomized presentation order,and timing of measured AI aversion. Include one learning objective,a full20minute schedule,fourquestions with matching one-point answer criteria(zero otherwise),and source filename/PDF-page citations. Explain one causal limitation of a measured variable. Do not invent empirical effect results.'
   run('Advertising-general-desk',[py,'-u',str(workbench/'portable_current.py'),'advertising',task])
   run('copied-training-update',[py,'-u',str(workbench/'scripts/train.py'),'game',str(data),'--repo','lmstudio-community/Qwen3.8-27B-MLX-6bit','--iters','1','--num-layers','2','--max-seq-length','1024','--learning-rate','0.00001','--reasoning-off','--cache-limit-gb','2','--wall-budget-seconds','180'],timeout=300)
   new_jobs=set((data/'jobs').glob('*'))-prior_jobs;assert len(new_jobs)==1;job=new_jobs.pop();result=read(job/'training-result.json');assert result['status']=='pilot_adapter_created_unpromoted' and result['exit_code']==0;audit=[json.loads(line)for line in(job/'training-batches.jsonl').read_text().splitlines()];batches=[x for x in audit if x['kind']=='train'];assert len(batches)==1 and max(x['shape'][1]for x in batches)<=1024
   for path,h in result['adapter_files'].items():assert sha(job/path)==h
   state.update(training_job=str(job),new_training=True,actual_training_updates=1,max_train_padded_tokens=max(x['shape'][1]for x in batches),adapter_default_promoted=False);save(out/'training-result.json',result);mark()
   gpu=read(workbench/'verification/easy-gpu-arena-recovery-current.json');cards=read(workbench/'verification/advertising-study-card-spans-workflow-current.json');desk=read(workbench/'verification/advertising-research-desk-sections-current.json');game=read(package/'portable-game-latest.json');state.update(gpu_trial_status=gpu['status'],gpu_trial_component_pass=gpu.get('component_pass',False),new_predictions=1+gpu['new_predictions']+cards['new_predictions']+desk['rounds']+int((Path(desk['directory'])/'review-response.json').exists()),role_runs=dict(game=game,gpu=gpu,cards=cards,desk=desk),scope=__doc__);mark()
  except BaseException as error:state.update(status='terminal_current_portable_workflows_failed',error=repr(error));mark();raise
  finally:
   loaded=ps();save(out/'before-live-restore-models.json',loaded);assert all(x['status']=='idle'and x.get('queued',0)==0 for x in loaded),'Do not interrupt an active prediction during restore'
   run('restore-live-unload',[str(LMS),'unload','--all'],timeout=120);run('restore-live-load',[str(LMS),'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],timeout=360);loaded=ps();save(out/'live-models-restored.json',loaded);assert len(loaded)==1 and loaded[0]['modelKey']=='local/advertising-qwen38'and loaded[0]['identifier']=='advertising-scholar'and loaded[0]['contextLength']==32768 and loaded[0]['parallel']==1;assert sha(mcp)==before;state['daily_base_restored']=True;mark()
 state.update(status='terminal_current_moved_workflow_predictions_and_one_training_update_pending_quality_review');mark();save(V/'portable-current-workflows-current.json',state);print({k:state[k]for k in['status','new_predictions','actual_training_updates','daily_base_restored']})
if __name__=='__main__':main()
