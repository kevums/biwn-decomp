"""Preserve a running candidate; isolate its misnamed mutable pointer on exit.
The newv2runner uses a dedicated namespace. No game/test process is restarted.
"""
import json,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 wrong=V/'native-navigation-hybrid-candidate-current.json';own=V/'native-actor-direction-candidate-current.json';current=read(wrong);assert 'native-actor-direction-route'in current['directory'];pid=current['pid'];old=V/'native-navigation-hybrid-route/20261019T114659.020997Z-candidate-65970/protocol.json';previous=read(old);assert previous['status']=='terminal_native_actor_navigation_route_pending_review'and previous['frames']==24610
 out=V/'direction-route-pointer-repair'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'running-direction-state.json',current);save(out/'retained-navigation-state.json',previous);state=dict(status='waiting_for_specific_running_direction_controller',pid=os.getpid(),directory=str(out),controller_pid=pid,controller_directory=current['directory'],game_process_restarted=False)
 def mark():save(out/'protocol.json',state);save(V/'direction-route-pointer-repair-current.json',state)
 mark()
 while True:
  observation=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
  current=read(Path(current['directory'])/'protocol.json')
  if current['status'].startswith('terminal_'):
   assert observation.returncode!=0 or 'run_biwn_native_actor_direction_route.py'not in observation.stdout,'Wait for final controller exit'
   break
  assert observation.returncode==0 and 'run_biwn_native_actor_direction_route.py'in observation.stdout,'Inspect missing controller; do not infer terminal from observation failure'
  state['observed_live_controller']=observation.stdout.strip();state['last_observed_UTC']=datetime.now(timezone.utc).isoformat();mark();save(own,current);time.sleep(10)
 save(out/'terminal-direction-state.json',current);save(own,current);assert read(wrong)['directory']==current['directory'];save(wrong,previous);state.update(status='terminal_direction_pointer_isolated_previous_navigation_pointer_restored',direction_status=current['status'],restored_navigation_directory=previous['directory']);mark();print(json.dumps(state))
if __name__=='__main__':main()
