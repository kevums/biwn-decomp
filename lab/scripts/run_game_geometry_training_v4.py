"""Fresh-base error-correction pilot, validation selection, frozen native tests, daily restore."""
import argparse,fcntl,json,os,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from run_biwn_native_fast_gameplay_route import sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reuse-base',type=Path);args=ap.parse_args()
    curriculum=read(ROOT/'verification/game-geometry-curriculum-v4-current.json');data=Path(curriculum['directory']);decision=read(data/'training-decision.json')
    assert curriculum['status']=='terminal_game_geometry_curriculum_prepared_untrained'and curriculum['split_counts']==dict(train=17,valid=1,test=4)
    assert sha(data/'reviewed-source-examples.jsonl')==curriculum['source_sha256'][str(data/'reviewed-source-examples.jsonl')]
    assert decision['fresh_base']and not decision['previous_adapter_reused']and not decision['new_training_started']
    for name,status in [('target-chunk-loss-equivalence-current.json','target_chunk_loss_and_gradient_equivalence_pass'),('eager-target-training-equivalence-current.json','eager_compiled_target_training_toy_updates_match')]:assert read(ROOT/'verification'/name)['status']==status
    out=ROOT/'runs/game-geometry-training-v4'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),data=str(data),decision_sha256=sha(data/'training-decision.json'),phases=[],new_training=False,training_started=False,default_promoted=False,job=None,
        scope=curriculum['scope']+'64update fresh-base pilot;actual saved-checkpoint validation selection. No default promotion.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/game-geometry-training-v4-current.json',state)
    def run(phase,command):
        row=dict(phase=phase,command=command);state['phases'].append(row)
        with(out/(phase+'.log')).open('w')as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);row['pid']=child.pid;state.update(status=phase,child_pid=child.pid);mark();code=child.wait()
        row['exit_code']=code;mark();return code
    mark();print(out,flush=True)
    code=1
    try:
        # Controls precede weight updates. Freeze this orchestration before either.
        if args.reuse_base:
            base=read(args.reuse_base);assert base['status']=='terminal_frozen_base_controls_rescored_valid'and base['dataset']==str(data)and len(base['results'])==4 and base['daily_model_restored']
            for path,h in base['source_sha256'].items():assert sha(path)==h,path
            state['base_control_reused']=str(args.reuse_base);mark()
        else:
            assert run('base_control',[sys.executable,str(ROOT/'scripts/evaluate_game_geometry_curriculum_v4.py')])==0,'Control inference/checking driver failed'
            base=read(ROOT/'verification/game-geometry-v4-base-evaluation-current.json');assert base['status']=='terminal_code_evaluation'and len(base['results'])==4 and base['daily_model_restored']
        state['base_control']=str(args.reuse_base.resolve())if args.reuse_base else str(Path(base['directory'])/'protocol.json');mark()
        before=set((data/'jobs').glob('*'))if(data/'jobs').exists()else set()
        t=decision['training'];command=[sys.executable,str(ROOT/'scripts/train.py'),'game',str(data),'--repo','lmstudio-community/Qwen3.8-27B-MLX-6bit','--iters',str(t['iters']),'--num-layers',str(t['num_layers']),'--max-seq-length',str(t['max_seq_length']),'--learning-rate',str(t['learning_rate']),'--reasoning-off','--cache-limit-gb',str(t['cache_limit_gb']),'--target-head-chunk',str(t['target_head_chunk']),'--eager','--wall-budget-seconds',str(t['wall_budget_seconds'])]
        state.update(new_training=True,training_started=True);mark();code=run('training',command)
        created=set((data/'jobs').glob('*'))-before;assert len(created)==1;job=created.pop();state['job']=str(job);mark();assert code==0,'Training failed; preserve it without automatic retry'
        trained=read(job/'training-result.json');assert trained['status']=='pilot_adapter_created_unpromoted'
        state['checkpoint_selection']='Actual saved checkpoints will be rescored on validation before any adapter test generation';mark()
        code=run('adapter_evaluation',[sys.executable,str(ROOT/'scripts/evaluate_game_geometry_curriculum_v4.py'),'--job',str(job)]);assert code==0,'Adapter evaluation driver failed; no promotion'
        state.update(status='terminal_game_geometry_v4_training_and_evaluation_pending_review',new_training=True,default_promoted=False);mark()
    except BaseException as error:
        state.update(status='terminal_game_geometry_v4_trial_failed_unpromoted',error=repr(error));code=1;mark()
    finally:
        terminal=state['status']
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);lms=str(Path.home()/'.lmstudio/bin/lms')
            unloaded=subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=120)
            restored=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300)
            (out/'daily-model-restore.log').write_text(unloaded.stdout+unloaded.stderr+restored.stdout+restored.stderr);state.update(status=terminal if restored.returncode==0 else'terminal_game_geometry_v4_daily_restore_failed',daily_model_restored=restored.returncode==0);mark()
        print(state['status'],flush=True)
    raise SystemExit(code if state.get('daily_model_restored') else 1)

if __name__=='__main__':main()
