"""Local Route Planner proposes grounded waypoints, kept as an audited draft."""
import fcntl,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import lmstudio,sdk_thinking_override_probe
sdk_thinking_override_probe.install();out=ROOT/'runs'/('local-doorway-route-planner-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);print(out,flush=True)
system='You are the local Route Planner for a source-verified restoration test. Return only the requested JSON. Do not claim execution, reachability or test results. Do not invent positions, controls or game semantics.'
prompt='''Choose two waypoint centers from these original disc collision records. The player begins at X24256,Z27360. Three connected rectangles form a north/south corridor: record0 X[24128,24384),Z[27072,27648); record1 X[24128,24384),Z[27008,27072); record3 X[24128,24384),Z[26624,27008). Source edges connect record0 to1 to3. The only direction-valid building doorway is portal0, at record3's east X boundary24384. It leads to indoor scene41. Its direction2/east condition requires floor((27008-playerZ)/64)==3. Thus the matching door Z strip is (26752,26816]; select its midpoint. First waypoint: corridor X center and this Z midpoint. Second waypoint: X32 beyond that east boundary at the same Z. No actor relocation; these are read-only steering targets for ordinary pad input. Planner itself does not execute or force positions.
Return exactly a JSON object with "waypoints":[{"X":integer,"Z":integer},{"X":integer,"Z":integer}],"position_tolerance":8,"opening_A_frames":9,"stop_scene_mode":2. No markdown or prose.'''
record=dict(role='local Route Planner',model='advertising-scholar',system=system,prompt=prompt,status='pending',new_training=False);(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\n')
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'
 chat=lmstudio.Chat(system);chat.add_user_message(prompt);started=time.monotonic();response=lmstudio.llm('advertising-scholar').respond(chat,config={'temperature':0.1,'maxTokens':400,'raw':{'fields':[{'key':'llm.prediction.reasoning.enableThinking','value':False},{'key':'ext.virtualModel.customField.enableThinking','value':False},{'key':'ext.virtualModel.customField.preserveThinking','value':False}]}});record['seconds']=time.monotonic()-started;raw=response.content
 (out/'raw-response.txt').write_text(raw)
 with(out/'prompts-and-responses.txt').open('a')as f:f.write('\nASSISTANT\n'+raw+'\n')
 plan=json.loads(raw);assert plan==dict(waypoints=[dict(X=24256,Z=26784),dict(X=24416,Z=26784)],position_tolerance=8,opening_A_frames=9,stop_scene_mode=2),plan
 (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');record.update(status='grounded_waypoint_arithmetic_passed_execution_pending',directory=str(out),plan=plan);(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(ROOT/'verification/local-doorway-route-plan-current.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'],seconds=record['seconds'],plan=plan)),flush=True)
