"""Retain failed fixed-exit runs and distinguish missing coverage from errors."""
import json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'native-navigation-fixed-exit-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};runs={}
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);p=target
  deps[str(p)]=actual
 for label in ['candidate','control']:
  p=V/('native-actor-navigation-'+label+'-current.json');o=read(p);bind(p);assert o['status']=='terminal_native_actor_navigation_route_pending_review'and o['exit_code']==0 and not o['returned_outdoors']and not o['live_monitor_pass']
  assert subprocess.run(['ps','-p',str(o['child_pid']),'-o','command='],capture_output=True).returncode!=0
  for p,h in o['source_sha256'].items():bind(p,h)
  folder=Path(o['directory'])/'candidate';r=read(folder/'report.json');a=o['observations'];assert a['geometry_entries']==0 and a['geometry_errors']==0 and o['navigation_monitor_pass']and o['actor_chain_monitor_pass']
  for file in ['report.json','gameplay-observation.json','RAM-final.bin','original-emulator-final-frame.png']:bind(folder/file)
  last=r['frames'][-1];assert last['player_mode_word']==2 and last['floor_word']==0
  runs[label]=dict(frames=o['frames'],native_navigation=a['an_native'],navigation_returns=a['an_returns'],navigation_errors=a['an_errors'],navigation_context_errors=a['an_context_errors'],navigation_stack_errors=a['an_stack_outside'],last_navigation=last['navigation'],geometry_entries=0,geometry_errors=0,room_pointer='0x15b7e6',bounds=[11008,11648,41344,41664],source_exit_key=25,source_exit_direction=1,corrected_waypoints=[[11296,41376],[11296,41312]],original_fixed_waypoints=[[12864,42416],[13024,42416]])
 report=out/'review.txt';report.write_text('''FIXED-EXIT ROUTE DID NOT COMPLETE — RETAINED NEGATIVE RESULT

Candidate34577frames/control34564; both exhausted the configured post-entry
window in mode2/floor0,steering into the east wall of room15B7E6. Neither returned
outdoors. All4 navigation roots returned in both:4/2/2/2. Candidate bodies/context
are native; control bodies original. Navigation/context/task errors0; inherited
creation/selector/scan/door/chain gates pass. The aggregate live_monitor_pass is
false:outside-geometry routine1028E was reached0times,which fails its required
coverage gate. geometry_errors is0; this is missing coverage,not a witnessed
geometry-output disagreement. No successful-roundtrip publication for this image.

The fixed east exit points belong to a previously observed different room. Current
read-only RAM/source records show room bounds11008..11648/41344..41664,width10,
depth5 and terminal boundary key25/flags9400/targetFFFF. Recovered19FDA/1028Earithmetic
maps key25 to south exit stripX11264..11328; aim11296,41376 then11296,41312. Both
saved RAM snapshots independently produce that plan. New fresh controller uses
current parsed room records,not saved RAM restoration or guest writes. All native
code/disc bytes remain identical. The cause of selecting a different room than
the smaller prior layout has not been isolated; timing/seed/layout effects remain
open. Changing controller policy does not establish whole-game equivalence.

Latest fully reviewed roundtrip publication remains28448bytes. Expanded29876build
has finite component/layout and reached-boundary evidence only until fresh dynamic
exit runs complete and are reviewed. Raw failed runs and their reports retained.
''');bind(report);bind(Path(__file__))
 state=dict(status='terminal_native_navigation_fixed_exit_route_failed_missing_outdoor_coverage',directory=str(out),report=str(report),resident_bytes=29876,runs=runs,new_predictions=0,new_training=False,default_promoted=False,whole_game_complete=False,dependencies_sha256=deps,scope=__doc__);save(out/'protocol.json',state);save(V/'native-navigation-fixed-exit-reviewed-current.json',state);print(state['status'])
if __name__=='__main__':main()
