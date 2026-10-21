"""Publish full-CPU indexed RNG and latest separate actor integration."""
import collections,hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 now=datetime.now(timezone.utc).isoformat();unit=read(ROOT/'verification/biwn-rng-cpu-checks.json');linked=read(ROOT/'verification/biwn-actor-rng-runtime-checks.json')
 assert unit['CPU_cases']==6144 and unit['reachable_nonexception_instruction_coverage']==[120,120]and unit['host_guards']==19 and not unit['new_components']
 assert linked['cases']==128 and linked['task_handoffs']==3072 and linked['scripted_helpers']==['0x13c9a']
 source=ROOT/'projects/black-ice-white-noise/restoration'
 names=['check_biwn_rng_cpu.py','check_biwn_actor_rng_runtime.py','check_biwn_actor_navigation.py','check_biwn_actor_navigation_runtime.py',
        'check_biwn_actor_task.py','check_biwn_actor_creation.py','check_biwn_render_display_runtime.py','check_biwn_scene_loading.py',
        'check_biwn_startup_services.py','check_biwn_boundary_handlers.py','check_biwn_world_update.py','check_biwn_scheduler.py']
 for proof in [unit,linked]:
  folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snapshot=folder/'harness-snapshot';snapshot.mkdir(exist_ok=True)
  for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
  files=[ROOT/'scripts'/name for name in names]+[source/name for name in set(proof['source_sha256'])|{'biwn_scheduler.h','biwn_world_update.h'}]+[ROOT/name for name in ['animation_renderer.py','inventory_renderer.py']]
  for path in files:shutil.copy2(path,snapshot/path.name)
  save(snapshot/'manifest.json',{path.name:hashlib.sha256(path.read_bytes()).hexdigest()for path in files})
 rows=read(Path(linked['directory'])/'fixtures.json');counts=dict(collections.Counter(hex(e['target'])for row in rows for e in row['rebuilt']['navigation_returns']))
 assert counts=={'0xf368':686,'0x1a77c':561,'0x13f12':498,'0x13f7c':354,'0x13fea':276}
 linked.update(helper_return_CPU_comparisons=counts,helper_return_CPU_comparisons_total=2375,indexed_RNG_return_CPU_comparisons=561,
               navigation_helper_return_comparisons_total=1814)
 linked['matched']=['Original CPU and C execute actor caller, four navigation bodies, indexed RNG with real division/remainder/multiply, two idle loops and real TRAP0 scheduling. All CPU/SR/USP/SSP and the complete2MBRAM/private stacks/public headers match without masks.',
                    '128 cases produce1024actor iterations and3072handoffs; all2375helper-return CPU states match, including561indexed RNG returns.']
 linked['limits']=['Only movement13C9A remains scripted. Its coordinate/fraction/collision field changes are external test fixtures, not reconstructed physics. Geometry inputs are seeded fixtures.',
                   'This separate actor/two-idle proof does not run actors in the21-context startup. RemovalTRAP2, real loading switches, complete actors/world/render/assets, remaining tasks,3Ddrawing/scanout/scenes/audio/game/hardware remain unfinished. No original CPU/GPU/gameframes execute on the C side.']
 save(ROOT/'verification/biwn-actor-rng-runtime-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
 shutil.copy2(Path(unit['directory'])/'librng-cpu.dylib',ROOT/'tools/libbiwn-rng-cpu.dylib');shutil.copy2(Path(linked['directory'])/'libactor-runtime.dylib',ROOT/'tools/libbiwn-actor-rng-runtime.dylib')
 progress=('The indexed RNG and its remainder/division/multiply callees now expose complete CPU and stack effects. 6,144 original CPU comparisons pass all 120 nonexception instructions out of 122 total and 19 host guards. Full registers, materialized SR/CCR, returns, stack banks, complete RAM/private frames and ordered bus accesses match. '
           'Two original zero-divisor exception instructions are excluded; zero division returns an explicit host error. These routines were already counted, so the total remains 100 components (98 CPU and 2 GPU). '
           'In the separate 128-case actor/two-idle test, 1,024 actor iterations, 3,072 real scheduler handoffs and 2,375 helper return CPU states match, including 561 RNG returns. Only movement 13C9A remains scripted; movement and geometry data are external fixtures. '
           'Actor bodies remain blocked in the 21-context startup. Removal, real loading switches, complete AI/physics, remaining tasks, world/render/lifecycles, graphics/main loop/scenes/audio/game/hardware remain unfinished. No new weights or default model promotion.')
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==100
 backup=ROOT/'verification/rng-cpu-backup'/Path(linked['directory']).name;backup.mkdir(parents=True)
 paths=['chat_tools.py','scripts/summarize_biwn_checks.py','config.json','CURRENT DECOMPILATION.txt','START HERE.txt','corpus/game/project-intake.json','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json']
 for name in paths:
  target=backup/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 shutil.copy2(session/'boot-slice-validation.json',backup/'boot-slice-validation.json')
 validation.update(indexed_rng_full_CPU_reconstruction=unit,actor_rng_scheduler_integration=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
 path=ROOT/'scripts/summarize_biwn_checks.py';text=path.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)"
 block="""    rng_cpu_path=root/'verification/biwn-rng-cpu-checks.json'
    actor_rng_path=root/'verification/biwn-actor-rng-runtime-checks.json'
    if rng_cpu_path.exists() and actor_rng_path.exists():
        rng_cpu=json.loads(rng_cpu_path.read_text());linked=json.loads(actor_rng_path.read_text())
        if rng_cpu['CPU_cases']!=6144 or rng_cpu['host_guards']!=19 or linked['helper_return_CPU_comparisons_total']!=2375:
            raise ValueError('Full CPU RNG evidence incomplete')
        runtime['CPU_indexed_RNG_full_CPU']={**rng_cpu,'report':str(rng_cpu_path)}
        runtime['actor_rng_scheduler_integration']={**linked,'report':str(actor_rng_path)}
"""
 assert 'CPU_indexed_RNG_full_CPU'not in text;path.write_text(text.replace(needle,block+needle))
 path=ROOT/'chat_tools.py';text=path.read_text().replace('separate_actor_navigation_runtime','separate_actor_runtime')
 text=text.replace("observed['actor_navigation_scheduler_integration'][k]for k in", "observed.get('actor_rng_scheduler_integration',observed['actor_navigation_scheduler_integration'])[k]for k in")
 text=text.replace("compact['actor_navigation_scheduler_integration']=observed['actor_navigation_scheduler_integration']", "compact['actor_navigation_scheduler_integration']=observed.get('actor_rng_scheduler_integration',observed['actor_navigation_scheduler_integration'])")
 text=text.replace("compact['CPU_actor_task_scheduler_integration']=observed['actor_navigation_scheduler_integration']", "compact['CPU_actor_task_scheduler_integration']=observed.get('actor_rng_scheduler_integration',observed['actor_navigation_scheduler_integration'])\n        compact['CPU_indexed_RNG_full_CPU']=observed['CPU_indexed_RNG_full_CPU']")
 start=text.index("        compact['checked_actor_task_scope']=",text.index("    if topic == 'actor_task':"));end=text.index('\n',start);text=text[:start]+"        compact['checked_actor_task_scope']="+repr(progress)+text[end:]
 needle="        compact['CPU_rng']={k:proof[k]for k in ['recorded_at','report','CPU_cases','CPU_instruction_coverage','host_guards','portable_components','original_bytes','intervals','matched','limits','examples','checked_selector_answer']}"
 assert needle in text;text=text.replace(needle,needle+"\n        compact['CPU_indexed_RNG_full_CPU']=observed['CPU_indexed_RNG_full_CPU']\n        compact['actor_rng_scheduler_integration']=observed['actor_rng_scheduler_integration']\n        compact['checked_latest_RNG_scope']="+repr(progress))
 text=text.replace('RNG and movement remain scripted. This does not run actors in the 21-context startup.', 'Indexed RNG and its math callees now run real bodies; only movement remains scripted. This does not run actors in the 21-context startup.')
 text=text.replace('Use actor_navigation for the latest four real helper bodies and two remaining RNG/movement scripts.', 'Use rng for the full CPU indexed-RNG proof and actor_task for current actor integration; only movement remains scripted.')
 path.write_text(text)
 path=ROOT/'verification/actor-navigation-checked-examples.json';value=read(path);value['checked_navigation_scope']=progress;save(path,value)
 path=ROOT/'presets/Game Assistant.system.txt';text=path.read_text().replace('latest separate actor scheduler proof and two remaining scripts.', 'latest separate actor scheduler proof; indexed RNG is now real, movement remains scripted.').replace('- rng:', '- rng: Includes the latest full-CPU indexed RNG/math proof, nested private frames/flags, one remaining movement script and unchanged component count.\n- rng historical:',1);path.write_text(text)
 path=ROOT/'presets/Game Assistant.preset.json';preset=read(path)
 for field in preset['operation']['fields']:
  if field['key']=='llm.prediction.systemPrompt':field['value']=text.strip()
 save(path,preset);shutil.copy2(path,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for name in ['config.json','corpus/game/project-intake.json']+['verification/'+name for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
  path=ROOT/name;value=read(path);value.update(rng_full_CPU_progress=progress,rng_full_CPU_evidence=[str(ROOT/'verification/biwn-rng-cpu-checks.json'),str(ROOT/'verification/biwn-actor-rng-runtime-checks.json')])
  if name=='config.json':value['chat_frontend']['game']['status']=progress
  if name=='corpus/game/project-intake.json':value['latest_checked_status']=progress
  if name=='verification/setup-status.json':value['game_work']=progress
  if name=='verification/current-runtime-state.json':value['decomp_progress']=progress
  if name=='verification/requirements-audit.json':
   for item in value['requirements']:
    if 'decompilation test'in item['requirement']:item['state']=progress
  value['actor_navigation_progress']='Historical navigation checkpoint; latest actor helper scope is rng_full_CPU_progress. '+value.get('actor_navigation_progress','')
  save(path,value)
 (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+progress+'\n\nWHO DID WHAT\nCodex authored the full CPU interface and comparison harness. Original CPU execution decides acceptance. No local-model code draft or independent agent vote was used this turn. Native Chat remains inaccessible while locked; local API/SDK exchanges are saved separately.\n\nNEXT\nReconstruct movement13C9A and actor collision helpers13B5A/13BB0, connect existing GPU4320 movement math, then integrate complete actor behavior with larger startup/world/render tests. Full goal active and incomplete.\n')
 path=ROOT/'START HERE.txt';text=path.read_text();start=text.index('LATEST GAME RESULT\n');end=text.index('LOCAL INFERENCE RESULT\n',start);path.write_text(text[:start]+'LATEST GAME RESULT\n'+progress+'\n\n'+text[end:])
 for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
 print(json.dumps({'components':100,'CPU_cases':6144,'host_guards':19,'actor_scripted_helpers':1,'RNG_returns':561,'helper_return_CPUs':2375}))

if __name__=='__main__':main()
