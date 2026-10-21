"""One finite continuation: wait for this trainer, evaluate, restore and report."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--trainer-pid',type=int,required=True);p.add_argument('--job',type=Path,required=True);a=p.parse_args()
 train=json.loads((ROOT/'verification/native-function-training-current.json').read_text());assert train['pid']==a.trainer_pid
 data=Path(train['dataset']);out=data/'finite-evaluation-followup';out.mkdir();state=dict(status='waiting_for_exact_trainer',pid=os.getpid(),trainer_pid=a.trainer_pid,job=str(a.job.resolve()),directory=str(out),commands=[],default_promoted=False,goal_complete=False)
 def save():
  state['recorded_at']=datetime.now(timezone.utc).isoformat()
  for path in [out/'protocol.json',ROOT/'verification/native-function-followup-current.json']:path.write_text(json.dumps(state,indent=2)+'\n')
 save();print(out,flush=True);deadline=time.monotonic()+3600
 try:
  while True:
   observed=subprocess.run(['ps','-p',str(a.trainer_pid),'-o','command='],capture_output=True,text=True)
   if observed.returncode:break
   assert 'run_native_function_training.py'in observed.stdout,'PID identity changed; do not follow unrelated process'
   job=json.loads((a.job/'training-result.json').read_text());state['training_job_status']=job['status']
   memory=a.job/'training-memory.jsonl'
   if memory.exists():state['completed_updates']=len(memory.read_text().splitlines())
   save();assert time.monotonic()<deadline,'Finite follow-up expired';time.sleep(10)
  terminal=json.loads((ROOT/'verification/native-function-training-current.json').read_text())
  assert terminal['pid']==a.trainer_pid and terminal['job']==str(a.job.resolve())
  assert terminal['status']=='terminal_training_completed'and terminal['daily_model_restored'],terminal
  fresh=json.loads((ROOT/'verification/native-function-fresh-case-current.json').read_text())
  script=ROOT/'scripts/evaluate_native_function_curriculum.py'
  phases=[('adapter_resource',[sys.executable,str(script),'--job',str(a.job.resolve())]),('base_fresh',[sys.executable,str(script),'--case-file',fresh['case_file']]),('adapter_fresh',[sys.executable,str(script),'--job',str(a.job.resolve()),'--case-file',fresh['case_file']]),('report',[sys.executable,str(ROOT/'scripts/report_native_function_trial.py')])]
  for name,command in phases:
   state['status']='running_'+name;row=dict(phase=name,command=command);state['commands'].append(row)
   with(out/(name+'.log')).open('w')as log:
    child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);row['pid']=child.pid;save();print(name,'PID',child.pid,flush=True);code=child.wait()
   row['exit_code']=code;save();assert code==0,(name,code)
  state['status']='terminal_native_function_trial_followup_completed';save();print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));save();raise
if __name__=='__main__':main()
