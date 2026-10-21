"""One real copied-pipeline training update for migration capability only.
Uses the previously exercised, reviewed source-v4b dataset and copied 27B base.
No model promotion, new learning-quality claim or held-out-answer generation.
"""
import fcntl, hashlib, json, os, shutil, subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';LMS=Path('/Users/kevin/.lmstudio/bin/lms')
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ps():return json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True))
def main():
    package=Path(json.loads((V/'portable-sdk-workbench-current.json').read_text())['package']);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=V/'portable-training-update'/stamp;out.mkdir(parents=True)
    prior=json.loads((V/'game-source-v4b-run-current.json').read_text());source=Path(prior['dataset']['directory']);data=package/'workbench'/source.relative_to(ROOT);data.mkdir(parents=True,exist_ok=True);files=[]
    for p in [*source.glob('*'),ROOT/'models.lock.json',ROOT/'candidate-models.lock.json']:
        if not p.is_file():continue
        target=package/'workbench'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert sha(target)==sha(p),'Preserve different existing copied input'
        else:shutil.copy2(p,target)
        files.append(dict(relative=str(p.relative_to(ROOT)),sha256=sha(target),bytes=target.stat().st_size))
    save(out/'copied-training-inputs.json',files);shutil.copy2(__file__,out/Path(__file__).name)
    before_jobs=set((data/'jobs').glob('*'))if(data/'jobs').exists()else set()
    command=[str(package/'runtime/.venv/bin/python'),str(package/'workbench/scripts/train.py'),'game',str(data),'--repo','lmstudio-community/Qwen3.8-27B-MLX-6bit','--iters','1','--num-layers','2','--max-seq-length','1024','--learning-rate','0.00001','--reasoning-off','--cache-limit-gb','2','--wall-budget-seconds','180']
    save(out/'command.json',command);state=dict(status='prepared',pid=os.getpid(),directory=str(out),package=str(package),dataset=str(data),requested_updates=1,completed_updates=0,default_promoted=False,quality_improvement_claim=False)
    def mark():save(out/'protocol.json',state);save(V/'portable-training-update-current.json',state)
    mark()
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);loaded=ps();save(out/'before-models.json',loaded)
        assert len(loaded)==1 and loaded[0]['modelKey']=='local/advertising-qwen38'and loaded[0]['identifier']=='advertising-scholar'and loaded[0]['status']=='idle'and loaded[0].get('queued',0)==0
        code=None
        try:
            with(out/'training-launcher.log').open('w')as stream:
                child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']});state.update(status='running_copied_training_pipeline',child_pid=child.pid);mark();code=child.wait(timeout=270)
            state['exit_code']=code;mark();assert code==0,'See copied training launcher log'
            created=set((data/'jobs').glob('*'))-before_jobs;assert len(created)==1;job=created.pop();result=json.loads((job/'training-result.json').read_text());save(out/'training-result.json',result);state['job']=str(job)
            assert result['status']=='pilot_adapter_created_unpromoted'and result['exit_code']==0
            audit=[json.loads(x)for x in(job/'training-batches.jsonl').read_text().splitlines()];training=[x for x in audit if x['kind']=='train'];assert len(training)==1
            assert max(x['shape'][1]for x in training)<=1024
            adapters=result['adapter_files'];assert any(name.endswith('.safetensors')for name in adapters)
            for name,digest in adapters.items():assert sha(job/name)==digest
            state.update(completed_updates=1,actual_train_batches=1,max_train_padded_tokens=max(x['shape'][1]for x in training),new_unpromoted_adapter_files=adapters)
        except BaseException as error:
            state.update(status='terminal_copied_training_test_failed',error=repr(error));mark();raise
        finally:
            loaded=ps();save(out/'before-restore-models.json',loaded)
            assert all(x['modelKey']=='local/advertising-qwen38'and x['status']=='idle'and x.get('queued',0)==0 for x in loaded),'Preserve unrelated or active inference'
            if not loaded:
                with(out/'restore-model.log').open('w')as stream:
                    restored=subprocess.run([str(LMS),'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],stdout=stream,stderr=subprocess.STDOUT,timeout=300);assert restored.returncode==0
            after=ps();save(out/'after-models.json',after);assert len(after)==1 and after[0]['identifier']=='advertising-scholar'and after[0]['contextLength']==32768 and after[0]['parallel']==1;state['daily_default_restored']=True;mark()
    state.update(status='terminal_one_real_copied_training_update_pass_unpromoted',new_predictions=0,scope=__doc__);mark();print(json.dumps(state))
if __name__=='__main__':main()
