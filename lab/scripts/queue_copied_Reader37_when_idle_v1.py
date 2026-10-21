"""One bounded copied Reader attempt after the machine-wide model lease is free."""
import fcntl,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save

def main():
    out=ROOT/'runs/queued-copied-Reader37-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    state=dict(status='waiting_on_shared_model_slot',directory=str(out),pid=os.getpid(),new_predictions=0,new_training=False,maximum_wait_seconds=900,attempts=0)
    def mark():save(out/'protocol.json',state);save(V/'queued-copied-Reader37-v1-current.json',state)
    mark();start=time.monotonic()
    while time.monotonic()-start<900:
        with(ROOT/'runs/.inference.lock').open('a')as lease:
            try:fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                state.update(waited_seconds=round(time.monotonic()-start),last_lease_check_UTC=datetime.now(timezone.utc).isoformat());mark();time.sleep(10);continue
            # The portable entry owns the lease throughout loading and inference.
            fcntl.flock(lease,fcntl.LOCK_UN)
        state.update(status='running_one_copied_Reader_attempt',attempts=1);mark()
        command=[str(P/'runtime/python/bin/python3.12'),str(P/'workbench/portable_biwn.py'),'reader']
        with(out/'launcher.log').open('w')as log:
            child=subprocess.Popen(command,cwd='/',stdout=log,stderr=subprocess.STDOUT,env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']})
            state['child_pid']=child.pid;mark();code=child.wait()
        state.update(status='terminal_one_copied_Reader_attempt_pending_review',child_pid=None,exit_code=code)
        pointer=P/'workbench/verification/Deck-status-live-v37-current.json'
        result=read(pointer)
        if result.get('new_predictions')and Path(result['directory']).name.startswith('Deck-status-live-v37-'):
            state.update(new_predictions=result['new_predictions'],Reader_protocol=str(pointer),Reader_directory=result['directory'],Reader_status=result['status'])
        mark();print(state['status'],state.get('new_predictions',0),flush=True);return
    state.update(status='terminal_shared_model_slot_wait_expired_zero_predictions');mark();print(state['status'],flush=True)

if __name__=='__main__':main()
