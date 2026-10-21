"""Finite frozen base/train/selected-adapter trial, optionally waiting for the live game job."""
import argparse,fcntl,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--after-game-pipeline',type=int);args=parser.parse_args()
    frozen_state=read(ROOT/'verification/advertising-v10-frozen-cases-current.json');evaluation=Path(frozen_state['directory']);data=Path(frozen_state['dataset'])
    assert sha(evaluation/'frozen-cases.json')==frozen_state['frozen_cases_sha256']
    protocol=read(evaluation/'frozen-protocol.json');assert sha(data/'train.jsonl')==protocol['train_sha256']and protocol['adaptation']['iters']==64
    manifest=read(data/'split-manifest.json');assert manifest['split_counts']==dict(train=11,valid=3,test=6)
    assert not (ROOT/'verification/advertising-v10-training-current.json').exists(),'Inspect the prior trial; do not silently repeat it'
    out=ROOT/'runs/advertising-v10-training'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    sources=[Path(__file__),ROOT/'scripts/evaluate_advertising_v10.py',ROOT/'scripts/select_advertising_v10_checkpoint.py',ROOT/'scripts/train.py',ROOT/'scripts/mlx_lora_reasoning_off.py',ROOT/'scripts/target_chunk_loss.py']
    for source in sources:shutil.copy2(source,out/source.name)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),dataset=str(data),evaluation=str(evaluation),frozen_cases_sha256=frozen_state['frozen_cases_sha256'],phases=[],training_started=False,default_promoted=False,job=None,execution_scripts_sha256={str(s):sha(s)for s in sources},
       scope='Fixed11passage-based training records,3development targets,6full-source test tasks from2test papers. Raw outputs require coordinator source adjudication. No broad reliability or automatic promotion.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/advertising-v10-training-current.json',state)
    def run(phase,command):
        # Use the exact snapshotted implementation; reject an unnoticed edit before dispatch.
        assert all(sha(s)==state['execution_scripts_sha256'][str(s)]for s in sources)
        row=dict(phase=phase,command=command);state['phases'].append(row)
        with(out/(phase+'.log')).open('w')as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);row['pid']=child.pid;state.update(status=phase,child_pid=child.pid);mark();code=child.wait()
        row['exit_code']=code;mark();assert code==0,phase+' failed; no automatic retry'
    mark();print(out,flush=True);code=1;model_phase_started=False
    try:
        if args.after_game_pipeline:
            state.update(status='waiting_for_game_pipeline',waiting_for_pid=args.after_game_pipeline);mark()
            while True:
                observation=subprocess.run(['ps','-p',str(args.after_game_pipeline),'-o','pid=,command='],capture_output=True,text=True)
                if not observation.stdout.strip():break
                assert 'run_native_repair_training.py'in observation.stdout,'PID reused; inspect before model work'
                state['last_live_game_observation']=dict(recorded_at=datetime.now(timezone.utc).isoformat(),process=observation.stdout.strip());mark();time.sleep(5)
            game=read(ROOT/'verification/native-repair-training-current.json');assert game['status'].startswith('terminal_')and game.get('daily_model_restored'),'Waited game pipeline must be terminal with daily model restored'
            state['preceding_game_terminal_state']=game['status'];mark()
        model_phase_started=True
        run('base_control',[sys.executable,str(ROOT/'scripts/evaluate_advertising_v10.py')])
        base=read(ROOT/'verification/advertising-v10-base-evaluation-current.json');assert base['status']=='terminal_raw_outputs_pending_source_review'and len(base['results'])==6 and base['daily_model_restored']
        state['base_control']=str(Path(base['directory'])/'protocol.json');mark()
        before=set((data/'jobs').glob('*'))if(data/'jobs').exists()else set();a=protocol['adaptation']
        command=[sys.executable,str(ROOT/'scripts/train.py'),'advertising',str(data),'--repo',a['base'],'--iters',str(a['iters']),'--num-layers',str(a['num_layers']),'--max-seq-length',str(a['max_seq_length']),'--learning-rate',str(a['learning_rate']),'--reasoning-off','--cache-limit-gb',str(a['cache_limit_gb']),'--target-head-chunk',str(a['target_head_chunk']),'--eager','--wall-budget-seconds',str(a['wall_budget_seconds'])]
        state['training_started']=True;mark();run('training',command)
        created=set((data/'jobs').glob('*'))-before;assert len(created)==1;job=created.pop();state['job']=str(job);mark()
        run('adapter_evaluation',[sys.executable,str(ROOT/'scripts/evaluate_advertising_v10.py'),'--job',str(job)])
        state.update(status='terminal_advertising_v10_trial_pending_source_review',checkpoint_selection=str(job/'checkpoint-selection.json'));mark();code=0
    except BaseException as error:state.update(status='terminal_advertising_v10_trial_failed_unpromoted',error=repr(error));mark()
    finally:
        if model_phase_started:
            with(ROOT/'runs/.inference.lock').open('a')as lock:
                fcntl.flock(lock,fcntl.LOCK_EX);lms=str(Path.home()/'.lmstudio/bin/lms')
                unloaded=subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=120)
                restored=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300)
                (out/'daily-model-restore.log').write_text(unloaded.stdout+unloaded.stderr+restored.stdout+restored.stderr);state['daily_model_restored']=restored.returncode==0;mark()
        print(state['status'],flush=True)
    raise SystemExit(code)

if __name__=='__main__':main()
