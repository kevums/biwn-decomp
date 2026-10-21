"""Publish movement caller/direction/GPU proofs while collision and task integration remain pending."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 now=datetime.now(timezone.utc).isoformat()
 names=['biwn-actor-movement-boundary-checks.json','biwn-actor-direction-checks.json','biwn-actor-movement-direction-checks.json','biwn-movement-submit-cpu-checks.json','biwn-actor-movement-gpu-checks.json']
 proofs={name:read(ROOT/'verification'/name)for name in names};caller,direction,connected,submit,gpu=[proofs[name]for name in names]
 assert caller['CPU_cases']==2048 and caller['CPU_instruction_coverage']==[192,192]and caller['host_guards']==17
 assert direction['CPU_cases']==2048 and direction['reachable_instruction_coverage']==[61,61]and direction['host_guards']==13
 assert connected['CPU_cases']==2048 and connected['CPU_instruction_coverage']==[192,192]
 assert submit['cases']==128 and submit['CPU_instruction_coverage']==[14,14]and submit['host_guards']==14
 assert gpu['CPU_cases']==256 and gpu['CPU_instruction_coverage']==[192,192]and gpu['scripted_services']==['0x13b5a','0x13bb0']and not gpu['GPU_output_words_scripted']
 source=ROOT/'projects/black-ice-white-noise/restoration'
 scripts=['check_biwn_actor_movement.py','check_biwn_actor_direction.py','check_biwn_actor_movement_direction.py','check_biwn_movement_submit_cpu.py','check_biwn_actor_movement_gpu.py',
          'check_biwn_rng_cpu.py','check_biwn_actor_navigation.py','check_biwn_actor_task.py','check_biwn_world_movement_pipeline.py','check_biwn_inventory_frame.py','check_unicorn_sr_observation.py']
 for name,proof in proofs.items():
  folder=Path(proof['directory']);assert read(folder/'status.json')['status']in['terminal_pass','terminal_pass_services_pending'];snapshot=folder/'harness-snapshot';snapshot.mkdir(exist_ok=True)
  for filename,digest in proof['source_sha256'].items():assert hashlib.sha256((source/filename).read_bytes()).hexdigest()==digest
  files=[ROOT/'scripts'/filename for filename in scripts]+[source/filename for filename in set(proof['source_sha256'])|{'biwn_scheduler.h','biwn_world_update.h','biwn_actor_task.h'}]
  for path in files:shutil.copy2(path,snapshot/path.name)
  save(snapshot/'manifest.json',{path.name:hashlib.sha256(path.read_bytes()).hexdigest()for path in files})
  proof['report']=str(ROOT/'verification'/name)
 shutil.copy2(Path(gpu['directory'])/'libactor-movement.dylib',ROOT/'tools/libbiwn-actor-movement-gpu.dylib')
 scope=('The movement caller 13C9A is translated and matches 2,048 original CPU cases, all 192 instructions and 17 host guards, including registers, flags, full returns, private frames, complete RAM and ordered data/helper accesses. '
        'Direction 13440 gains a full CPU interface with real division: 2,048 cases, all 61 reachable instructions of 62 total and 13 guards. Its default branch is unreachable after four fixed sign cases. '
        'The GPU submission interface E220/E098 passes 128 original CPU/GPU comparisons against C CPU code and the existing C GPU4320 matrix algorithm. '
        'A separate 256-case movement integration links real direction, CPU submission and GPU movement math, covering all 192 caller instructions. Matrix and fraction output words are computed rather than scripted. '
        'Only collision helpers 13B5A/13BB0 remain scripted in that movement test. Geometry/collision inputs and synchronous GPU completion are explicit fixtures/models. '
        'This movement caller is not linked into the actor task-ring test yet: that earlier test still scripts 13C9A. Actors remain blocked in the 21-context startup. '
        'The count stays at 100 components (98 CPU and 2 GPU); movement and actor callers remain pending promotion. Complete collision/physics/AI, loading switches, remaining tasks, world/render/assets, graphics/main loop/scenes/audio/game/hardware are unfinished.')
 examples={'checked_movement_scope':scope,
  'checked_rollback_answer':'The caller tests the low16 bits of a collision return. D0=0x00010000 therefore triggers rollback. It restores X/Y/Z and the three coordinate fractions at object offsets4,8,10,14,16,18. It retains animation-selection writes, GPU matrix/fraction output, collision metadata and helper effects. This does not prove the scripted collision helpers are implemented.',
  'checked_pending_answer':'Direction, signed division, E220/E098 and GPU4320 math now run real code in a separate256-case movement test.13B5A/13BB0 collision helpers remain scripts. The actor scheduler test still scripts the whole13C9A call; the21-context startup still blocks actors. Component count100is unchanged.',
  'observation_repair':read(ROOT/'verification/unicorn-SR-read-side-effect.json')}
 save(ROOT/'verification/actor-movement-checked-examples.json',examples)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==100
 backup=ROOT/'verification/actor-movement-backup'/Path(gpu['directory']).name;backup.mkdir(parents=True)
 for name in ['chat_tools.py','scripts/summarize_biwn_checks.py','config.json','CURRENT DECOMPILATION.txt','START HERE.txt','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json','corpus/game/project-intake.json']:
  target=backup/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 shutil.copy2(session/'boot-slice-validation.json',backup/'boot-slice-validation.json')
 validation.update(actor_movement_caller_reconstruction=caller,actor_direction_full_CPU=direction,actor_movement_direction_pipeline=connected,movement_submit_full_CPU=submit,actor_movement_GPU_pipeline=gpu,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
 path=ROOT/'scripts/summarize_biwn_checks.py';text=path.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)"
 block="""    actor_movement_path=root/'verification/biwn-actor-movement-gpu-checks.json'
    if actor_movement_path.exists():
        reports={name:json.loads((root/'verification'/name).read_text())for name in ['biwn-actor-movement-boundary-checks.json','biwn-actor-direction-checks.json','biwn-actor-movement-direction-checks.json','biwn-movement-submit-cpu-checks.json','biwn-actor-movement-gpu-checks.json']}
        caller,direction,connected,submit,gpu=reports.values()
        if caller['CPU_cases']!=2048 or gpu['CPU_cases']!=256 or gpu['GPU_output_words_scripted']:
            raise ValueError('Actor movement evidence incomplete')
        runtime['CPU_actor_movement_reconstruction']={**caller,'report':str(root/'verification/biwn-actor-movement-boundary-checks.json')}
        runtime['CPU_actor_direction_full_CPU']={**direction,'report':str(root/'verification/biwn-actor-direction-checks.json')}
        runtime['CPU_movement_submit_full_CPU']={**submit,'report':str(root/'verification/biwn-movement-submit-cpu-checks.json')}
        runtime['actor_movement_GPU_pipeline']={**gpu,'report':str(actor_movement_path),**json.loads((root/'verification/actor-movement-checked-examples.json').read_text())}
"""
 assert 'CPU_actor_movement_reconstruction'not in text;path.write_text(text.replace(needle,block+needle))
 path=ROOT/'chat_tools.py';text=path.read_text().replace("'actor_task', 'actor_navigation',","'actor_task', 'actor_movement', 'actor_navigation',").replace("'actor_task','actor_navigation',","'actor_task','actor_movement','actor_navigation',")
 text=text.replace('Get checked Black Ice White Noise evidence. Use actor_navigation','Get checked Black Ice White Noise evidence. Use actor_movement for13C9A coordinate/fraction updates, selective rollback, low-word returns, new fullCPU direction/GPU submission and realGPU matrix output, two scripted collision helpers and unlinked actor-task scope. Use actor_navigation',1)
 needle="        return compact\n    if topic == 'actor_navigation':"
 insert="""        if 'actor_movement_GPU_pipeline' in observed:
            compact['separate_actor_movement_progress']={k:observed['actor_movement_GPU_pipeline'][k]for k in ['report','CPU_cases','CPU_instruction_coverage','scripted_services','GPU_output_words_scripted','direction13440_and_division_real','synchronous_dispatch_completion_model']}
        return compact
    if topic == 'actor_movement':
        observed=common.get('emulator_runtime',{})
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        compact['CPU_movement_caller']=observed['CPU_actor_movement_reconstruction']
        compact['CPU_direction']=observed['CPU_actor_direction_full_CPU']
        compact['CPU_GPU_submission']=observed['CPU_movement_submit_full_CPU']
        compact['movement_GPU_pipeline']=observed['actor_movement_GPU_pipeline']
        for key in ['checked_movement_scope','checked_rollback_answer','checked_pending_answer']:compact[key]=compact['movement_GPU_pipeline'][key]
        return record('project_evidence',{'topic':topic},compact)
    if topic == 'actor_navigation':"""
 assert needle in text;text=text.replace(needle,insert)
 needle="            current=concise\n        return record('project_evidence',{'topic':topic},current)"
 replace="""            if 'separate_actor_movement_progress' in current:
                concise['separate_actor_movement_progress']=current['separate_actor_movement_progress']
                concise['checked_current_summary']+=' A separate256-case movement caller test now computes GPU output with real direction and GPU math; two collision helpers remain scripted and this is not yet linked to the actor task test.'
            current=concise
        return record('project_evidence',{'topic':topic},current)"""
 assert needle in text;text=text.replace(needle,replace);path.write_text(text)
 path=ROOT/'presets/Game Assistant.system.txt';text=path.read_text().replace('- actor_task:', '- actor_movement:13C9A movement/fractions and selective rollback; real direction/GPU math in a separate256-case test, two collision scripts, pending actor-task linkage.\n- actor_task:',1);path.write_text(text)
 path=ROOT/'presets/Game Assistant.preset.json';preset=read(path)
 for field in preset['operation']['fields']:
  if field['key']=='llm.prediction.systemPrompt':field['value']=text.strip()
 save(path,preset);shutil.copy2(path,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for name in ['config.json','corpus/game/project-intake.json']+['verification/'+filename for filename in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
  path=ROOT/name;value=read(path);value['actor_movement_progress']=scope;value['actor_movement_evidence']=[str(ROOT/'verification'/name)for name in proofs]
  if name=='config.json':value['chat_frontend']['game']['status']=scope
  if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
  if name=='verification/current-runtime-state.json':value['decomp_progress']=scope
  if name=='verification/setup-status.json':value['game_work']=scope
  if name=='verification/requirements-audit.json':
   for item in value['requirements']:
    if 'decompilation test'in item['requirement']:item['state']=scope
  save(path,value)
 (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored accepted movement/direction/GPU CPU interfaces and comparison harnesses. Original CPU/GPU execution decides acceptance. GPU matrix algorithm was already reconstructed and verified. No local-model code or independent agent votes used this turn. Native Chat remains unverified while locked; API/SDK logs are separate.\n\nOBSERVATION CORRECTION\nDirect Unicorn SR read committed stale flags before a later materialization probe. A tiny reproduction and corrected no-early-SR-read harness are saved. No game code changed to match stale flags.\n\nNEXT\nImplement actor collision13B5A/13BB0 with actual geometry effects, then connect movement into actor/task scheduler tests and the larger startup/world/render pipeline. Full goal active and incomplete.\n')
 path=ROOT/'START HERE.txt';text=path.read_text();start=text.index('LATEST GAME RESULT\n');end=text.index('LOCAL INFERENCE RESULT\n',start);path.write_text(text[:start]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[end:])
 for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
 print(json.dumps({'components':100,'movement_caller_CPU_cases':2048,'direction_CPU_cases':2048,'GPU_submit_cases':128,'movement_GPU_cases':256,'collision_scripts':2}))

if __name__=='__main__':main()
