"""Wait for the existing qualified image,then fresh pair,review and portable delivery."""
import os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save

def main():
 out=V/'record-stride-fresh-delivery-worker-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='waiting_existing_readonly_qualification',directory=str(out),pid=os.getpid(),children={},results={},new_predictions=0,new_training=False)
 def mark():save(out/'protocol.json',state);save(V/'record-stride-fresh-delivery-worker-v1-current.json',state)
 def launch(name,args):
  stream=(out/(name+'.log')).open('w');p=subprocess.Popen([str(ROOT/'.venv/bin/python3.12'),*args],cwd=str(ROOT),stdout=stream,stderr=subprocess.STDOUT);state['children'][name]=p.pid;mark();return p,stream
 def finish(name,pair):
  p,stream=pair;code=p.wait(timeout=1200);stream.close();state['children'].pop(name,None);state['results'][name]=dict(exit_code=code,log=str(out/(name+'.log')));mark()
  assert code==0,(name,(out/(name+'.log')).read_text()[-4000:])
 def run(name,script):finish(name,launch(name,[str(ROOT/'scripts'/script)]))
 mark()
 try:
  deadline=time.monotonic()+900
  while True:
   q=read(V/'record-stride-image-qualification-pipeline-v2-current.json')
   if q['status']=='terminal_record_stride_exact_image_and_readonly_observers_qualified':break
   if q['status'].startswith('terminal_'):raise RuntimeError(q)
   os.kill(q['pid'],0)
   if time.monotonic()>=deadline:raise TimeoutError('Existing qualification still needs observation;do not restart it')
   time.sleep(10)
  state['status']='running_fresh_candidate_and_control';mark()
  script=ROOT/'scripts/run_native_record_strides_route_v1.py';jobs={name:launch(name,[str(script),*(['--control']if name=='control'else[])])for name in ['candidate','control']}
  for name,pair in jobs.items():finish(name,pair)
  state['status']='reviewing_and_delivering';mark();run('review','review_record_strides_fresh_v1.py');run('publish','publish_record_strides_fresh_v1.py');run('MCP','check_record_strides_fresh_current_MCP_v1.py')
  for name,cmd in [('Root-status',[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_native_status_v7.py'),'--brief'])]:
   with(out/(name+'.txt')).open('w')as log:q=subprocess.run(cmd,cwd='/',stdout=log,stderr=subprocess.STDOUT,timeout=180)
   assert q.returncode==0
  state['status']='terminal_v34_fresh_review_and_current_portable_delivery_verified';mark();print(state['status'],flush=True)
 except BaseException as error:
  state.update(status='observation_timeout_workers_may_be_live'if isinstance(error,subprocess.TimeoutExpired)else'terminal_record_stride_fresh_delivery_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
