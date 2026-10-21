"""Publish actual collision/geometry and live bounded actor movement, retaining removal limits."""
import collections,hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 now=datetime.now(timezone.utc).isoformat();names=['biwn-geometry-cpu-checks.json','biwn-actor-collision-checks.json','biwn-actor-movement-collision-checks.json','biwn-actor-full-movement-runtime-checks.json'];proofs={name:read(ROOT/'verification'/name)for name in names};geometry,collision,movement,actor=proofs.values()
 assert geometry['CPU_cases']==1024 and geometry['CPU_instruction_coverage']==[170,170]and geometry['host_guards']==14
 assert collision['CPU_cases']==4096 and collision['CPU_instruction_coverage']==[109,109]and collision['host_guards']==15 and collision['nested_helper_scripts']==0
 assert movement['CPU_cases']==256 and movement['CPU_instruction_coverage']==[192,192]and not movement['scripted_services']and movement['collision_helpers_real']
 assert actor['cases']==128 and actor['task_handoffs']==3072 and not actor['scripted_helpers']and actor['movement_and_collision_real']
 source=ROOT/'projects/black-ice-white-noise/restoration';scripts=['check_biwn_geometry_cpu.py','check_biwn_actor_collision.py','check_biwn_actor_movement_collision.py','check_biwn_actor_full_movement_runtime.py',
  'check_biwn_actor_rng_runtime.py','check_biwn_actor_movement_gpu.py','check_biwn_actor_movement.py','check_biwn_actor_direction.py','check_biwn_movement_submit_cpu.py',
  'check_biwn_geometry.py','check_biwn_rng_cpu.py','check_biwn_actor_navigation.py','check_biwn_actor_task.py','check_biwn_world_movement_pipeline.py','check_biwn_inventory_frame.py',
  'check_biwn_actor_creation.py','check_biwn_scene_loading.py','check_biwn_startup_services.py','check_biwn_boundary_handlers.py','check_biwn_world_update.py','check_biwn_scheduler.py','check_biwn_render_display_runtime.py']
 for proof in proofs.values():
  folder=Path(proof['directory']);assert read(folder/'status.json')['status']in['terminal_pass','terminal_pass_services_pending'];snapshot=folder/'harness-snapshot';snapshot.mkdir(exist_ok=True)
  for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
  files=[ROOT/'scripts'/name for name in scripts]+[source/name for name in set(proof['source_sha256'])|{'biwn_scheduler.h','biwn_world_update.h','biwn_actor_task.h'}]+[ROOT/name for name in ['animation_renderer.py','inventory_renderer.py']]
  for path in files:shutil.copy2(path,snapshot/path.name)
  save(snapshot/'manifest.json',{path.name:hashlib.sha256(path.read_bytes()).hexdigest()for path in files})
 rows=read(Path(actor['directory'])/'fixtures.json');counts=dict(collections.Counter(hex(e['target'])for r in rows for e in r['rebuilt']['navigation_returns']));assert sum(counts.values())==2671 and counts['0x13c9a']==1024
 moved=sum(any([p['X'],p['Y'],p['Z']]!=[r['rebuilt']['movements'][0]['X'],r['rebuilt']['movements'][0]['Y'],r['rebuilt']['movements'][0]['Z']]for p in r['rebuilt']['movements'][1:])for r in rows);assert moved==101
 assert all(r['original']['device']['original_GPUExec1_calls']>0 and not r['rebuilt']['device']['original_GPUExec1_calls']and not r['rebuilt']['device']['game_frames_executed']for r in rows)
 gpu_entries=sum(r['original']['steps'].count(0xe220)for r in rows);assert gpu_entries==1024
 actor.update(helper_return_CPU_comparisons=counts,helper_return_CPU_comparisons_total=2671,navigation_helper_return_comparisons_total=1289,indexed_RNG_return_CPU_comparisons=358,
              movement_return_CPU_comparisons=1024,position_change_cases_observed=101,position_change_observation_scope='Across recorded movement-entry positions, after up to seven prior real movement calls; not a full-scene performance benchmark.',original_GPU_submit_entries=gpu_entries)
 actor['matched']=['The original native CPU/GPU and reconstructed C execute the F4D8 regular actor path with actual RNG, navigation, movement, direction, GPU math, collision, geometry and two idle tasks. Full CPU/SR/USP/SSP and complete2MBRAM/private frames/public38byteheaders match without masks.',
                   '128 cases produce1024actor iterations,3072actualTRAP0/RTE handoffs,2671fullhelper-returnCPU comparisons and1024originalGPU submit entries. Position changes are observed in101cases; allC-side originalGPU/gameframe counters remainzero.']
 actor['limits']=['Synthetic bounded outdoor grid/scene data, seeded contexts/clock and synchronousGPU completion are explicit inputs/device model. No actor helper bodies are scripts in this fixture, but it is not original21-context startup/world/render/assets or full game execution.',
                  'The actor removal branch/TRAP2 remains boundary-checked only; it is not executed here. Real loading switches, task teardown/reuse, remaining task bodies, full graphics/scanout/mainloop/scenes/audio/game/hardware remain unfinished.']
 save(ROOT/'verification/biwn-actor-full-movement-runtime-checks.json',actor);save(Path(actor['directory'])/'report.json',actor)
 movement.update(pending_components=0,published_new_components=1,actor_task_movement_now_linked_in_separate_proof=True)
 movement['limits'][0]='Direction, division, E220/E098, GPU4320 math, bothcollision helpers andfourgeometry routines execute real code. No service scripts remain in this bounded256-case movement proof. Scene geometry is synthetic and GPU completion is synchronous. A separate128-case actor proof now links this movement path; full startup/world/render is still unlinked.'
 save(ROOT/'verification/biwn-actor-movement-collision-checks.json',movement);save(Path(movement['directory'])/'report.json',movement)
 for proof,libname,target in [(collision,'libactor-collision.dylib','libbiwn-actor-collision.dylib'),(movement,'libactor-movement.dylib','libbiwn-actor-movement-collision.dylib'),(actor,'libactor-runtime.dylib','libbiwn-actor-full-movement.dylib')]:shutil.copy2(Path(proof['directory'])/libname,ROOT/'tools'/target)
 partial=next(r for r in read(Path(collision['directory'])/'fixtures.json')if r['CPU']['registers'][0]and not r['CPU']['registers'][0]&65535)
 assert partial['CPU']['registers'][0]==0xffff0000
 scope=('103 checked components: 101 CPU and two GPU. Two collision routines 13B5A/13BB0 pass 4,096 original CPU comparisons, all 109 instructions and 15 host guards, with real geometry and no nested scripts. '
        'Four existing geometry routines gain full CPU/stack interfaces: 1,024 cases, all 170 instructions and 14 guards. The complete movement caller adds one component; 256 GPU-connected cases cover all 192 caller instructions with real direction, GPU math, collision and geometry. '
        'A separate 128-case actor/two-idle runtime now executes all six actor helper bodies as real code: 1,024 actor iterations, 3,072 actual scheduler handoffs and 2,671 full helper-return CPU comparisons match. Position changes are observed in 101 cases. All registers, SR, USP/SSP and complete RAM/private stacks/public headers match without masks. '
        'The scene grid is synthetic and GPU completion synchronous. Actor removal/TRAP2 is still only boundary-checked; the actor caller remains pending promotion. This proof is separate from the 21-context startup, where actor bodies remain blocked. '
        'Full startup/world/render/assets, loading switches, teardown/reuse, remaining tasks, graphics/scanout/main loop/scenes/audio/game/hardware remain unfinished. Counts are not completion percentages.')
 examples={'checked_collision_scope':scope,'checked_partial_return_answer':'Nonzero fullD0 is not uniform success. Original CPU/C case2 of13B5A returns0xFFFF0000: its low16bits arezero, so the movement caller treats it as failure and rolls back position fields. Real source geometry is executed; this value is not a scripted helper return.',
           'checked_partial_return_example':{'case':partial['case'],'entry':hex(partial['parameters']['entry']),'full_D0':hex(partial['CPU']['registers'][0]),'low_word':0,'report':str(ROOT/'verification/biwn-actor-collision-checks.json')},
           'checked_actor_runtime_answer':'Yes, actors now execute real movement/collision/geometry in the separate128-case actor/two-idle test with3072real handoffs andno actor-helper scripts. No, this does not run actors in the21-context startup: they are still blocked there. Synthetic geometry/synchronousGPU completion, removalTRAP2, startup/world/render/assets/scenes/audio/game/hardware remain limitations.'}
 save(ROOT/'verification/actor-collision-checked-examples.json',examples)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==100
 backup=ROOT/'verification/actor-collision-backup'/Path(actor['directory']).name;backup.mkdir(parents=True)
 for name in ['chat_tools.py','scripts/summarize_biwn_checks.py','config.json','CURRENT DECOMPILATION.txt','START HERE.txt','corpus/game/project-intake.json','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json']:
  target=backup/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 shutil.copy2(session/'boot-slice-validation.json',backup/'boot-slice-validation.json')
 validation.update(portable_C_component_count=103,processor_component_counts={'CPU':101,'GPU':2},latest_aggregate_update=now,
  geometry_full_CPU_reconstruction=geometry,actor_collision_reconstruction=collision,actor_complete_movement_pipeline=movement,actor_full_movement_runtime=actor,
  component_count_scope='103components:101CPU/2GPU. Two newcollision bodies plusmovement13C9A; already-counted geometry/direction/GPU/math reused. ActorF4D8regularpath hasrealhelpers butremoval/TRAP2remains pending, soitscaller isnotyet counted. Not a gamecompletionpercentage.')
 save(session/'boot-slice-validation.json',validation)
 path=ROOT/'scripts/summarize_biwn_checks.py';text=path.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)"
 block="""    actor_collision_path=root/'verification/biwn-actor-collision-checks.json'
    actor_full_path=root/'verification/biwn-actor-full-movement-runtime-checks.json'
    if actor_collision_path.exists() and actor_full_path.exists():
        collision=json.loads(actor_collision_path.read_text());actor=json.loads(actor_full_path.read_text())
        if collision['CPU_cases']!=4096 or collision['CPU_instruction_coverage']!=[109,109]or actor['helper_return_CPU_comparisons_total']!=2671:
            raise ValueError('Actor collision/live movement evidence incomplete')
        runtime['CPU_geometry_full_CPU']={**json.loads((root/'verification/biwn-geometry-cpu-checks.json').read_text()),'report':str(root/'verification/biwn-geometry-cpu-checks.json')}
        runtime['CPU_actor_collision_reconstruction']={**collision,'report':str(actor_collision_path),**json.loads((root/'verification/actor-collision-checked-examples.json').read_text())}
        runtime['actor_complete_movement_pipeline']={**json.loads((root/'verification/biwn-actor-movement-collision-checks.json').read_text()),'report':str(root/'verification/biwn-actor-movement-collision-checks.json')}
        runtime['actor_full_movement_runtime']={**actor,'report':str(actor_full_path)}
"""
 assert 'CPU_actor_collision_reconstruction'not in text;path.write_text(text.replace(needle,block+needle))
 path=ROOT/'chat_tools.py';text=path.read_text().replace("'actor_task', 'actor_movement',","'actor_task', 'actor_collision', 'actor_movement',").replace("'actor_task','actor_movement',","'actor_task','actor_collision','actor_movement',")
 text=text.replace('Get checked Black Ice White Noise evidence. Use actor_movement','Get checked Black Ice White Noise evidence. Use actor_collision for13B5A/13BB0, real geometry/fullCPU, partial nonzero failureD0 and latest no-helper-script actor movement/scheduler scope. Use actor_movement',1)
 old="observed.get('actor_rng_scheduler_integration',observed['actor_navigation_scheduler_integration'])";new="observed.get('actor_full_movement_runtime',observed.get('actor_rng_scheduler_integration',observed['actor_navigation_scheduler_integration']))";text=text.replace(old,new)
 text=text.replace("compact['movement_GPU_pipeline']=observed['actor_movement_GPU_pipeline']", "compact['movement_GPU_pipeline']={**observed.get('actor_complete_movement_pipeline',observed['actor_movement_GPU_pipeline']),**{key:observed['actor_movement_GPU_pipeline'][key]for key in ['checked_movement_scope','checked_rollback_answer','checked_pending_answer']}}\n        compact['actor_full_movement_runtime']=observed['actor_full_movement_runtime']")
 start=text.index("        compact['checked_actor_task_scope']=",text.index("    if topic == 'actor_task':"));end=text.index('\n',start);text=text[:start]+"        compact['checked_actor_task_scope']="+repr(scope)+text[end:]
 needle="    if topic == 'actor_movement':";insert="""    if topic == 'actor_collision':
        observed=common.get('emulator_runtime',{});proof=observed['CPU_actor_collision_reconstruction']
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        compact['CPU_actor_collision']={key:proof[key]for key in ['report','CPU_cases','CPU_instruction_coverage','host_guards','new_components','nested_helper_scripts','geometry_entries_reached','matched','limits']}
        compact['CPU_geometry_full_CPU']=observed['CPU_geometry_full_CPU']
        compact['actor_complete_movement_pipeline']=observed['actor_complete_movement_pipeline']
        compact['actor_full_movement_runtime']=observed['actor_full_movement_runtime']
        compact.update({key:proof[key]for key in ['checked_collision_scope','checked_partial_return_answer','checked_partial_return_example','checked_actor_runtime_answer']})
        return record('project_evidence',{'topic':topic},compact)
    if topic == 'actor_movement':"""
 assert needle in text;text=text.replace(needle,insert)
 text=text.replace("observed['actor_movement_GPU_pipeline'][k]for k in", "observed.get('actor_complete_movement_pipeline',observed['actor_movement_GPU_pipeline'])[k]for k in")
 text=text.replace('Indexed RNG and its math callees now run real bodies; only movement remains scripted. This does not run actors in the 21-context startup.', 'All six actor helpers now execute real code in the separate actor test. Removal/TRAP2 remains pending; this does not run actors in the 21-context startup.')
 text=text.replace('A separate256-case movement caller test now computes GPU output with real direction and GPU math; two collision helpers remain scripted and this is not yet linked to the actor task test.', 'The separate256-case movement test now has real collision/geometry and no service scripts, and is linked into a128-case actor/two-idle runtime. Removal and21-context startup linkage remain pending.')
 path.write_text(text)
 path=ROOT/'verification/actor-movement-checked-examples.json';value=read(path);value['checked_movement_scope']=scope;value['checked_pending_answer']=examples['checked_actor_runtime_answer'];save(path,value)
 path=ROOT/'verification/actor-navigation-checked-examples.json';value=read(path);value['checked_navigation_scope']=scope;save(path,value)
 path=ROOT/'presets/Game Assistant.system.txt';text=path.read_text().replace('- actor_task:', '- actor_collision: real13B5A/13BB0/geometry, nonzero fullD0 with zero low word, current actor movement/scheduler with no helper scripts; pending removal/startup/world/render.\n- actor_task:',1);text=text.replace('two collision scripts, pending actor-task linkage.', 'real collision/geometry, now linked into the separate actor task test; pending removal/startup linkage.');path.write_text(text)
 path=ROOT/'presets/Game Assistant.preset.json';preset=read(path)
 for field in preset['operation']['fields']:
  if field['key']=='llm.prediction.systemPrompt':field['value']=text.strip()
 save(path,preset);shutil.copy2(path,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for name in ['config.json','corpus/game/project-intake.json']+['verification/'+filename for filename in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
  path=ROOT/name;value=read(path);value.update(actor_collision_progress=scope,actor_collision_evidence=[str(ROOT/'verification'/filename)for filename in names])
  if name=='config.json':value['chat_frontend']['game']['status']=scope
  if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
  if name=='verification/current-runtime-state.json':value['decomp_progress']=scope
  if name=='verification/setup-status.json':value['game_work']=scope
  if name=='verification/requirements-audit.json':
   for item in value['requirements']:
    if 'decompilation test'in item['requirement']:item['state']=scope
  save(path,value)
 (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored accepted collision/fullCPU geometry interfaces and native/C tests. Original CPU/GPU execution decides acceptance. No local-model code or independent agent vote was used this turn. API/SDK logs are separate from native Chat.\n\nNEXT\nImplement and verify actual task removal/TRAP2, then connect actors with original startup/world/render/assets and remaining systems. Full goal active and incomplete.\n')
 path=ROOT/'START HERE.txt';text=path.read_text();start=text.index('LATEST GAME RESULT\n');end=text.index('LOCAL INFERENCE RESULT\n',start);path.write_text(text[:start]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[end:])
 for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
 print(json.dumps({'components':103,'CPU':101,'GPU':2,'collision_CPU_cases':4096,'geometry_CPU_cases':1024,'actor_iterations':1024,'handoffs':3072,'actor_helper_scripts':0,'removal_pending':True}))

if __name__=='__main__':main()
