"""Wait for the shared model slot, then make one ordinary copied Reader attempt.
No model is loaded or changed while the shared lease is held by another job.
Output quality remains pending coordinator review; no optimizer updates.
"""
import fcntl,json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 out=ROOT/'runs/portable-Reader36-queued-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='waiting_for_machine_model_slot',directory=str(out),pid=os.getpid(),new_predictions=0,new_training=False,native_Chat_verified=False,wait_limit_seconds=900)
 def mark():save(out/'protocol.json',state);save(V/'portable-Reader36-queued-v1-current.json',state)
 mark();print(out,flush=True);start=time.monotonic();lock=(ROOT/'runs/.inference.lock').open('a');owned=False
 try:
  while time.monotonic()-start<900:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);owned=True
   except BlockingIOError:owned=False
   if owned:break
   state['seconds_remaining']=max(0,900-int(time.monotonic()-start));mark();time.sleep(5)
  if not owned:state['status']='terminal_model_slot_wait_expired_zero_predictions';mark();return
  fcntl.flock(lock,fcntl.LOCK_UN);owned=False
  before=P/'workbench/verification/Deck-status-live-v36-current.json';prior=read(before)if before.exists()else None
  state.update(status='running_one_ordinary_portable_Reader_attempt',source_script_sha256=sha(P/'workbench/scripts/run_deck_status_live_v36.py'));mark()
  command=[str(P/'runtime/python/bin/python3.12'),str(P/'workbench/portable_biwn.py'),'reader'];state['command']=command
  with(out/'portable-reader.log').open('w')as log:
   child=subprocess.Popen(command,cwd='/',stdout=log,stderr=subprocess.STDOUT,start_new_session=True);state['child_pid']=child.pid;mark();code=child.wait(timeout=600)
  state['child_pid']=None;current=read(before)if before.exists()else None;new=current is not None and(prior is None or current['directory']!=prior['directory'])
  state.update(status='terminal_ordinary_portable_Reader_attempt_pending_review',exit_code=code,Reader_result=current if new else None,new_predictions=current.get('new_predictions',0)if new else 0,new_model_output_approved=False,source_sha256={str(p):sha(p)for p in [Path(__file__),P/'workbench/scripts/run_deck_status_live_v36.py',P/'workbench/portable_biwn.py',out/'portable-reader.log']});mark();print(state['status'],state['new_predictions'],flush=True)
 except BaseException as error:state.update(status='terminal_queued_Reader_attempt_failed',error=repr(error));mark();raise
 finally:
  if owned:fcntl.flock(lock,fcntl.LOCK_UN)
  lock.close()
if __name__=='__main__':main()
