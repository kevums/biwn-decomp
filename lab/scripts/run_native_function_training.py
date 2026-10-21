"""Finite native ABI LoRA pilot, guarded baseline and daily-model restoration."""
import argparse,fcntl,hashlib,json,subprocess,sys,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--num-layers',type=int,choices=[1,2],default=2);options=parser.parse_args()
 dataset=json.loads((ROOT/'verification/native-function-curriculum-current.json').read_text());data=Path(dataset['directory'])
 baseline=json.loads((ROOT/'verification/native-function-base-evaluation-current.json').read_text())
 assert baseline['dataset']==str(data)and baseline['status']=='terminal_code_evaluation'and len(baseline['results'])==3
 assert baseline['daily_model_restored']
 assert json.loads((data/'ABI-sidecar-audit.json').read_text())['status']=='all_native_curriculum_ABI_sidecars_bound'
 for name,status in [('target-chunk-loss-equivalence-current.json','target_chunk_loss_and_gradient_equivalence_pass'),('eager-target-training-equivalence-current.json','eager_compiled_target_training_toy_updates_match')]:assert json.loads((ROOT/'verification'/name).read_text())['status']==status
 pointer=ROOT/'verification/native-function-training-current.json'
 recovery=None
 if options.num_layers==1:
  prior=json.loads(pointer.read_text());assert prior['status']=='terminal_training_failed'and prior['daily_model_restored']
  recovery=prior['job'];assert 'Insufficient Memory'in(Path(recovery)/'training.log').read_text()
  (data/'two-layer-failed-launcher.json').write_text(json.dumps(prior,indent=2)+'\n')
 command=[sys.executable,str(ROOT/'scripts/train.py'),'game',str(data),'--repo','lmstudio-community/Qwen3.8-27B-MLX-6bit','--iters','32','--num-layers',str(options.num_layers),'--max-seq-length',str(dataset['max_seq_length']),'--learning-rate','0.00001','--reasoning-off','--cache-limit-gb','0.5','--target-head-chunk','128','--eager','--wall-budget-seconds','1800']
 state=dict(status='starting',pid=os.getpid(),recorded_at=datetime.now(timezone.utc).isoformat(),dataset=str(data),baseline=str(Path(baseline['directory'])/'protocol.json'),command=command,num_layers=options.num_layers,recovery_from=recovery,optimizer_resume=False,default_promoted=False,scope='32-update rank8 LoRA from the locked27B6bit base. Full examples,8960context,128token suffix-head chunks,512MiB cache,process-local eager execution. Earlier whole-function pilot failed holdout. This changed native ABI curriculum trial is unpromoted; actual generated resource C decides quality, not loss. Scheduling validation shares task concepts with training; resource test is the primary development gate, not fresh independent evaluation. A one-layer retry follows a recorded two-layer first-update Metal OOM, with no truncation or test changes.')
 def save():pointer.write_text(json.dumps(state,indent=2)+'\n')
 save();print('starting native training',flush=True)
 try:
  with(data/'training-launcher.log').open('w')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  jobs=sorted((data/'jobs').glob('*'));state.update(status='terminal_training_completed'if r.returncode==0 else'terminal_training_failed',exit_code=r.returncode,job=str(jobs[-1])if jobs else None);save()
 finally:
  with(ROOT/'runs/.inference.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);lms=str(Path.home()/'.lmstudio/bin/lms')
   unload=subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=120)
   reload=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300)
   (data/'training-daily-reload.log').write_text(unload.stdout+unload.stderr+reload.stdout+reload.stderr);state['daily_model_restored']=reload.returncode==0;save()
 print(state['status'],state.get('job'),flush=True)
 raise SystemExit(state.get('exit_code',1))
if __name__=='__main__':main()
