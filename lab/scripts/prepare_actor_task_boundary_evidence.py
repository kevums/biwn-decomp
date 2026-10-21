"""Expose actor caller boundary proof while retaining the96component runtime checkpoint."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 proof=read(ROOT/'verification/biwn-actor-task-boundary-checks.json');assert proof['CPU_cases']==512 and proof['reachable_instruction_coverage']==[191,191]and proof['host_guard_checks']==15
 out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass_boundary_comparisons_integration_pending';snap=out/'harness-snapshot';snap.mkdir(exist_ok=True);manifest={}
 files=[ROOT/'scripts'/n for n in ['check_biwn_actor_task.py','check_biwn_actor_creation.py','check_biwn_scene_loading.py','check_biwn_startup_services.py','check_biwn_boundary_handlers.py','check_biwn_world_update.py','check_biwn_scheduler.py']]+[ROOT/'projects/black-ice-white-noise/restoration'/n for n in ['biwn_actor_task.c','biwn_actor_task.h','biwn_scheduler.h','biwn_world_update.h']]
 for p in files:shutil.copy2(p,snap/p.name);manifest[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 save(snap/'manifest.json',manifest);shutil.copy2(out/'libactor-task.dylib',ROOT/'tools/libbiwn-actor-task.dylib')
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==96
 back=ROOT/'verification/actor-task-boundary-backup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');back.mkdir(parents=True)
 for n in ['chat_tools.py','scripts/summarize_biwn_checks.py','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json']:
  p=back/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p)
 shutil.copy2(session/'boot-slice-validation.json',back/'boot-slice-validation.json');validation['actor_task_boundary_reconstruction']=proof;save(session/'boot-slice-validation.json',validation)
 p=ROOT/'scripts/summarize_biwn_checks.py';s=p.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)";block="""    actor_task_path=root/'verification/biwn-actor-task-boundary-checks.json'
    if actor_task_path.exists():
        actor_task=json.loads(actor_task_path.read_text())
        if actor_task['CPU_cases']!=512 or actor_task['reachable_instruction_coverage']!=[191,191]:raise ValueError('Actor task boundary proof incomplete')
        runtime['CPU_actor_task_boundary_reconstruction']={**actor_task,'report':str(actor_task_path)}
""";assert needle in s;s=s.replace(needle,block+needle);p.write_text(s)
 p=ROOT/'chat_tools.py';s=p.read_text().replace("'render_startup', 'actor_creation',", "'render_startup', 'actor_task', 'actor_creation',").replace("'render_startup','actor_creation',", "'render_startup','actor_task','actor_creation',")
 s=s.replace('Get checked Black Ice White Noise evidence. Use actor_creation', 'Get checked Black Ice White Noise evidence. Use actor_task forF4D8persistent AI caller,512CPU boundary tests/fullregisters/CCR/stack, pendingDF60/DF7A andunintegrated steering/movement/scheduler scope; itdoesnot mean actors nowrun in startup. Use actor_creation')
 needle="    if topic == 'actor_creation':";insert="""    if topic == 'actor_task':
        observed=common.get('emulator_runtime',{});proof=observed['CPU_actor_task_boundary_reconstruction']
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        compact['CPU_actor_task_boundary']=proof
        compact['checked_actor_task_scope']='F4D8caller controlflow matches512originalCPU cases, all191reachable instructions outof193, allregisters/materializedSR/CCR, PC/SP andcompleteRAM/privateframes. TheDF60scheduler andDF7Aremoval traps are onlypending boundaries. Steering/RNG/waypoint/movement helpers remain scripted; onlyDFA6getter isreal. This isnot liveactor task-ring integration. Current96component startup stillblocksactor taskbodies. No newpublishedcomponent orfullgame completion isclaimed.'
        compact=latest_pipeline(compact,observed);compact.pop('current_connected_pipeline',None)
        return record('project_evidence',{'topic':topic},compact)
    if topic == 'actor_creation':""";assert needle in s;s=s.replace(needle,insert);p.write_text(s)
 p=ROOT/'presets/Game Assistant.system.txt';s=p.read_text().replace('- actor_creation:', '- actor_task: F4D8 caller boundary proof, full CPU/flags/stack checks, pending scheduler/removal and scripted helpers; not live actor integration.\n- actor_creation:',1);p.write_text(s)
 p=ROOT/'presets/Game Assistant.preset.json';d=read(p)
 for f in d['operation']['fields']:
  if f['key']=='llm.prediction.systemPrompt':f['value']=s.strip()
 save(p,d);shutil.copy2(p,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for n in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/n)],check=True)
 print(json.dumps({'published_components':96,'boundary_cases':512,'reachable':[191,191],'actor_task_ring_integration':'pending','backup':str(back)}))
if __name__=='__main__':main()
