"""Fresh-base error-correction pilot, validation selection, frozen native tests, daily restore."""
import fcntl,json,os,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from run_biwn_native_fast_gameplay_route import sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    curriculum=read(ROOT/'verification/native-repair-curriculum-current.json');data=Path(curriculum['directory']);decision=read(data/'training-decision.json')
    assert curriculum['status']=='terminal_native_repair_curriculum_prepared_untrained'and curriculum['split_counts']==dict(train=13,valid=1,test=3)
    assert sha(data/'reviewed-source-examples.jsonl')==curriculum['records_sha256']and sha(data/'training-decision.json')==curriculum['decision_sha256']
    assert decision['fresh_base']and not decision['previous_adapter_reused']and not decision['new_training_started']
    for name,status in [('target-chunk-loss-equivalence-current.json','target_chunk_loss_and_gradient_equivalence_pass'),('eager-target-training-equivalence-current.json','eager_compiled_target_training_toy_updates_match')]:assert read(ROOT/'verification'/name)['status']==status
    out=ROOT/'runs/native-repair-training'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),data=str(data),decision_sha256=sha(data/'training-decision.json'),phases=[],new_training=False,training_started=False,default_promoted=False,job=None,
        scope='Finite changed data/64update adaptation. Fresh same-base controls and exact3resource tasks; select solely on scheduler validation loss. Adaptive development holdout with prior exposure/shared dependencies, not independent generalization. Preserve complete examples; no default promotion.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-repair-training-current.json',state)
    def run(phase,command):
        row=dict(phase=phase,command=command);state['phases'].append(row)
        with(out/(phase+'.log')).open('w')as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);row['pid']=child.pid;state.update(status=phase,child_pid=child.pid);mark();code=child.wait()
        row['exit_code']=code;mark();return code
    mark();print(out,flush=True)
    code=1
    try:
        # Controls precede weight updates. Freeze this orchestration before either.
        assert run('base_control',[sys.executable,str(ROOT/'scripts/evaluate_native_repair_curriculum.py')])==0,'Control inference/checking driver failed'
        base=read(ROOT/'verification/native-repair-base-evaluation-current.json');assert base['status']=='terminal_code_evaluation'and len(base['results'])==3 and base['daily_model_restored']
        state['base_control']=str(Path(base['directory'])/'protocol.json');mark()
        before=set((data/'jobs').glob('*'))if(data/'jobs').exists()else set()
        t=decision['training'];command=[sys.executable,str(ROOT/'scripts/train.py'),'game',str(data),'--repo','lmstudio-community/Qwen3.8-27B-MLX-6bit','--iters',str(t['iters']),'--num-layers',str(t['num_layers']),'--max-seq-length',str(t['max_seq_length']),'--learning-rate',str(t['learning_rate']),'--reasoning-off','--cache-limit-gb',str(t['cache_limit_gb']),'--target-head-chunk',str(t['target_head_chunk']),'--eager','--wall-budget-seconds',str(t['wall_budget_seconds'])]
        state.update(new_training=True,training_started=True);mark();code=run('training',command)
        created=set((data/'jobs').glob('*'))-before;assert len(created)==1;job=created.pop();state['job']=str(job);mark();assert code==0,'Training failed; preserve it without automatic retry'
        trained=read(job/'training-result.json');assert trained['status']=='pilot_adapter_created_unpromoted'
        clean=re.sub(r'\x1b\[[0-9;]*m','',(job/'training.log').read_text());scores=[(int(m[1]),float(m[2]))for m in re.finditer(r'^\s*(\d+)\s+val\s+([0-9.]+)',clean,re.M)if(job/'adapters'/f'{int(m[1]):07d}_adapters.safetensors').is_file()]
        assert scores;step,loss=min(scores,key=lambda x:(x[1],x[0]));selected=job/'selected-adapter';selected.mkdir();shutil.copy2(job/'adapters'/f'{step:07d}_adapters.safetensors',selected/'adapters.safetensors');shutil.copy2(job/'adapters/adapter_config.json',selected/'adapter_config.json')
        selection=dict(selected_step=step,validation_loss=loss,validation_checkpoints=scores,selected_adapter=str(selected),adapter_sha256=sha(selected/'adapters.safetensors'),test_generated_before_selection=False,policy=decision['checkpoint_selection']);save(job/'checkpoint-selection.json',selection);state['checkpoint_selection']=selection;mark()
        code=run('adapter_evaluation',[sys.executable,str(ROOT/'scripts/evaluate_native_repair_curriculum.py'),'--job',str(job)]);assert code==0,'Adapter evaluation driver failed; no promotion'
        state.update(status='terminal_native_repair_training_and_evaluation_pending_review',new_training=True,default_promoted=False);mark()
    except BaseException as error:
        state.update(status='terminal_native_repair_trial_failed_unpromoted',error=repr(error));code=1;mark()
    finally:
        terminal=state['status']
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);lms=str(Path.home()/'.lmstudio/bin/lms')
            unloaded=subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=120)
            restored=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300)
            (out/'daily-model-restore.log').write_text(unloaded.stdout+unloaded.stderr+restored.stdout+restored.stderr);state.update(status=terminal if restored.returncode==0 else'terminal_native_repair_daily_restore_failed',daily_model_restored=restored.returncode==0);mark()
        print(state['status'],flush=True)
    raise SystemExit(code if state.get('daily_model_restored') else 1)

if __name__=='__main__':main()
