"""Exercise the normal Advertising launcher after the separate training test."""
import fcntl,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';LMS='/Users/kevin/.lmstudio/bin/lms'
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def ps():return json.loads(subprocess.check_output([LMS,'ps','--json'],text=True))
def main():
 p=Path(json.loads((V/'portable-sdk-workbench-current.json').read_text())['package']);out=V/'portable-advertising-launcher'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),package=str(p),new_training=False,native_Chat_verified=False)
 def mark():save(out/'protocol.json',state);save(V/'portable-advertising-launcher-current.json',state)
 command=[str(p/'Run Advertising Assistant.command'),'For Schreiner2026 Study2A, in exactly two sentences and at most 100 words, identify what was experimentally manipulated and when AI aversion was measured. Cite the supplied PDF page numbers; do not treat it as a pretreatment baseline.'];save(out/'command.json',command);mark()
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);before=ps();save(out/'before-models.json',before);assert len(before)==1 and before[0]['identifier']=='advertising-scholar'and before[0]['status']=='idle'and before[0].get('queued',0)==0
  try:
   with(out/'launcher.log').open('w')as log:
    child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']});state.update(status='running_actual_advertising_launcher',child_pid=child.pid);mark();code=child.wait(timeout=600)
   state['exit_code']=code;mark();assert code==0;result=json.loads((p/'portable-advertising-latest.json').read_text());save(out/'result.json',result);state['prediction_directory']=result['directory']
  except BaseException as error:state.update(status='terminal_advertising_launcher_failed',error=repr(error));mark();raise
  finally:
   loaded=ps();bindings=json.loads((p/'portable-model-bindings.json').read_text());allowed={'local/advertising-qwen38',*[x['model_key']for x in bindings['models'].values()]};assert all(x['modelKey']in allowed and x['status']=='idle'and x.get('queued',0)==0 for x in loaded)
   with(out/'restore.log').open('w')as log:
    subprocess.run([LMS,'unload','--all'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120);subprocess.run([LMS,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
   loaded=ps();save(out/'after-models.json',loaded);assert len(loaded)==1 and loaded[0]['identifier']=='advertising-scholar'and loaded[0]['contextLength']==32768 and loaded[0]['parallel']==1;state['daily_default_restored']=True;mark()
 state.update(status='terminal_normal_advertising_launcher_prediction_returned_pending_quality_review',new_predictions=1);mark();print(json.dumps(state))
if __name__=='__main__':main()
