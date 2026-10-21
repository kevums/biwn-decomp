"""Freeze disc-scene actor phase and publish its exact bridge/time-input scope."""
import ast,hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
    now=datetime.now(timezone.utc).isoformat();proof=read(ROOT/'verification/biwn-disc-scene-actors-checks.json');out=Path(proof['directory']);capture=Path(proof['startup_capture_directory'])
    assert read(out/'status.json')['status']=='terminal_pass'
    assert proof['cases']==16 and proof['actor_iterations']==1024 and proof['task_handoffs']==2064
    assert proof['cases_with_position_change']==12 and proof['original_collision_entry_counts']=={'0x13b5a':40,'0x13bb0':0}
    rows=read(out/'fixtures.json');assert sum(len(r['rebuilt']['helper_returns'])for r in rows)==1108
    proof['full_helper_return_CPU_comparisons']=1108
    for row in rows:
        assert row['whole2MBRAM_allCPU_privateframes_match'] and not row['rebuilt']['device']['original_GPUExec1_calls']
        assert not row['rebuilt']['device']['game_frames_executed']
    save(out/'report.json',proof);save(ROOT/'verification/biwn-disc-scene-actors-checks.json',proof)
    source=ROOT/'projects/black-ice-white-noise/restoration'
    names=set(proof['source_sha256'])
    tree=ast.parse((ROOT/'scripts/check_biwn_render_actors_runtime.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='names'for t in node.targets)and isinstance(node.value,ast.List):
            values=ast.literal_eval(node.value);names.update(values);names.update(n.replace('.c','.h')for n in values)
    for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
    snapshot=out/'harness-snapshot';snapshot.mkdir(exist_ok=True)
    files=[source/n for n in sorted(names)]+[ROOT/'scripts'/n for n in ['check_biwn_disc_scene_actors.py','check_biwn_render_actors_runtime.py','check_biwn_actor_full_movement_runtime.py','check_biwn_actor_lifecycle_runtime.py','biwn_disc_backend.py','check_biwn_movement_submit_cpu.py','check_biwn_actor_collision.py','check_biwn_geometry_cpu.py','check_biwn_actor_task.py','check_biwn_actor_navigation.py','check_biwn_rng_cpu.py']]
    files+=[ROOT/'verification/biwn-disc-resources.json',capture/'librender-actors.dylib',Path(read(ROOT/'verification/biwn-actor-lifecycle-runtime-checks.json')['directory'])/'libactor-lifecycle.dylib']
    for path in files:shutil.copy2(path,snapshot/path.name)
    save(snapshot/'manifest.json',{path.name:hashlib.sha256(path.read_bytes()).hexdigest()for path in files})
    frozen=out/'startup-captures';frozen.mkdir(exist_ok=True)
    for path in capture.glob('startup-*'):
        if path.is_file():shutil.copy2(path,frozen/path.name)
    shutil.copy2(capture/'fixtures.json',frozen/'startup-verified-fixtures.json')
    save(frozen/'manifest.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in frozen.iterdir()if p.name!='manifest.json'})
    scope=('Two actors now run on the scene/room/tile/region and model/texture data produced by C startup from the preserved disc, retaining all 21 created/supplied contexts. '
           'Sixteen cases cover 1,024 actor iterations, 2,064 real scheduler handoffs and 1,108 full helper-return CPU comparisons; complete 2 MB RAM, private frames, all registers, SR, USP and SSP match the original CPU/GPU. '
           'Twelve cases change position; the four zero-time-step baselines stay stationary. Forty outdoor collision entries execute; no indoor collision entry occurs here. No synthetic grid or actor-helper scripts are used. '
           'This is a phased bridge: startup keeps its existing private-stack/formatter exclusions, then both actor paths start from the same checked C-startup RAM/CPU. '
           'Only two actors and two idle tasks run; 17 contexts, including world/render, are blocked after the initial render yield. The shared movement time step is explicitly supplied as 0, 1, 8 or 30; a world task does not generate it. GPU completion remains synchronous. '
           'The earlier 144-case startup/render proof still blocks actors; this new actor phase does not prove uninterrupted full startup/world/render execution. '
           'Removal/context reuse remains checked separately in synthetic scene fixtures. Full loading switches, remaining tasks, 3D drawing/scanout/main loop/scenes/audio/game/hardware are unfinished. Count stays 106 (104 CPU, two GPU); existing bodies are reused.')
    examples={'checked_actor_scene_scope':scope,'checked_actor_scene_answer':'Yes, actual C-startup disc scene data now drives both actors in a phased21-context test. Sixteen cases/1024actoriterations/2064handoffs match original CPU/GPU;12cases move and40outdoorcollisionentries execute. Four zero-time baselines stay stationary. Shared movement time0/1/8/30 is a host input because world remains blocked;17contexts are blocked, GPU completion synchronous, and the full startup/world/render/game is unfinished.'}
    save(ROOT/'verification/actor-scene-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==106
    validation.update(actor_disc_scene_pipeline=proof,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
    path=ROOT/'scripts/summarize_biwn_checks.py';text=path.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)"
    block="""    actor_scene_path=root/'verification/biwn-disc-scene-actors-checks.json'
    if actor_scene_path.exists():
        actor_scene=json.loads(actor_scene_path.read_text())
        if actor_scene['cases']!=16 or actor_scene['task_handoffs']!=2064 or actor_scene['cases_with_position_change']!=12:raise ValueError('Disc-scene actor proof incomplete')
        runtime['actor_disc_scene_pipeline']={**actor_scene,'report':str(actor_scene_path)}
        runtime['actor_disc_scene_checked_examples']=json.loads((root/'verification/actor-scene-checked-examples.json').read_text())
"""
    assert 'actor_disc_scene_pipeline'not in text;path.write_text(text.replace(needle,block+needle))
    path=ROOT/'chat_tools.py';text=path.read_text();needle="        if 'render_task_startup_progress' in compact:\n            compact['render_task_startup_progress'].update(implemented_captured_task_callers_total=6,other_captured_task_callers_unported=15,task_entry_coverage=examples['task_entry_coverage'])\n        return compact"
    block="""        if 'render_task_startup_progress' in compact:
            compact['render_task_startup_progress'].update(implemented_captured_task_callers_total=6,other_captured_task_callers_unported=15,task_entry_coverage=examples['task_entry_coverage'])
        if 'actor_disc_scene_pipeline' in observed:
            scene=observed['actor_disc_scene_pipeline']
            compact['current_disc_scene_actors']={k:scene[k]for k in ['report','cases','actor_iterations','task_handoffs','full_helper_return_CPU_comparisons','created_contexts_preserved','runnable_actor_and_idle_contexts','blocked_contexts','startup_C_scene_task_state_linked','uninterrupted_startup_actor_execution','geometry_replaced_by_synthetic_grid','actor_helper_scripts','shared_time_step_inputs','cases_with_position_change','original_collision_entry_counts','synchronous_GPU_completion','allCPU_SR_USP_SSP_complete2MBRAM_privateframes_compared','matched','limits']}
            compact.update(observed['actor_disc_scene_checked_examples'])
            compact['current_vs_historical']='Current_disc_scene_actors is the newer phased scene-data bridge; current_actor_lifecycle is the separate synthetic-scene removal/reuse proof. The historical144-case startup/render proof still blocks actors. No complete world/render/game is established.'
            if 'checked_current_summary' in compact:compact['checked_current_summary']+=' '+compact['checked_actor_scene_scope']
            if 'startup_scope' in compact:compact['startup_scope']='Historical144-case startup/render proof blocks18contexts including actors. New disc-scene actor phase starts from checked CstartupRAM/CPU and retains21contexts, runs twoactors/twoidles, blocks17includingworld/render, and explicitly supplies movementtime. Not uninterrupted startup/world/render/game.'
        return compact"""
    assert needle in text;path.write_text(text.replace(needle,block,1))
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path=ROOT/name;value=read(path);value.update(actor_disc_scene_progress=scope,actor_disc_scene_evidence=str(ROOT/'verification/biwn-disc-scene-actors-checks.json'))
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value['decomp_progress']=scope
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=scope
        save(path,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\nConnect actual world timing/input and actor bodies in the scene task ring, then render/loading/remaining tasks. Full goal active and incomplete.\n')
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps({'components':106,'disc_scene_cases':16,'actor_iterations':1024,'handoffs':2064,'position_change_cases':12,'outdoor_collision_calls':40}))

if __name__=='__main__':main()
