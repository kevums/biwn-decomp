"""Publish verified actual camera and animation in the disc-world actor phase."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration'
    names=['biwn-animation-cpu-checks.json','biwn-camera-cpu-checks.json','biwn-disc-world-camera-checks.json'];animation,camera,linked=[read(ROOT/'verification'/n)for n in names]
    assert animation['CPU_cases']==1538 and animation['CPU_instruction_coverage']==[101,101]
    assert camera['CPU_cases']==768 and camera['CPU_instruction_coverage']==[144,144]
    assert linked['cases']==16 and linked['task_handoffs']==2576 and linked['world_updates']==512 and linked['camera_calls']==512 and linked['animation_request_calls']==16
    assert len(linked['configured_world_helper_scripts'])==5 and sum(n>0 for n in linked['reached_world_helper_script_counts'].values())==2
    assert linked['world_camera_fullCPU_real']and linked['world_animation_fullCPU_real']and not linked['queue_consumer_run']
    scripts=['check_biwn_camera_cpu.py','check_biwn_animation_cpu.py','check_biwn_camera.py','check_biwn_animation.py','check_biwn_disc_world_actors.py','check_biwn_disc_scene_actors.py','check_biwn_actor_full_movement_runtime.py','check_biwn_actor_lifecycle_runtime.py','check_biwn_world_cpu.py','check_biwn_rng_cpu.py','check_biwn_actor_direction.py','check_biwn_movement_submit_cpu.py']
    for proof in [animation,camera,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass'
        for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
        target=folder/'publication-snapshot';target.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in scripts]
        for path in files:shutil.copy2(path,target/path.name)
        save(target/'manifest.json',{'recorded_at':now,'scope':'Sources match accepted proof digests; harness snapshot at publication includes optional camera mode added after animation-only proof. Existing modes retained.', 'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    rows=read(Path(linked['directory'])/'fixtures.json')
    linked.update(world_helper_incoming_CPU_comparisons=sum(len(r['rebuilt']['world_calls'])for r in rows),world_helper_return_CPU_comparisons=sum(len(r['rebuilt']['world_returns'])for r in rows),world_complete_return_CPU_comparisons=sum(len(r['rebuilt']['world_time_steps'])for r in rows),actor_helper_return_CPU_comparisons=sum(len(r['rebuilt']['helper_returns'])for r in rows))
    assert linked['world_helper_incoming_CPU_comparisons']==linked['world_helper_return_CPU_comparisons']==3584
    save(ROOT/'verification/biwn-disc-world-camera-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    scope=('Camera and animation now execute actual reconstructed bodies in the disc-loaded world-and-actor test. All 16 cases match the original CPU/GPU across 512 world updates, 1,024 actor iterations and 2,576 task handoffs. '
           'The camera uses actual multiply, direction and GPU math. Animation produces 16 real queue requests, one per case; the queue consumer and render task do not run. '
           'Five world helper scripts remain configured: input dispatch 191F4, inventory redraw 1B786, outdoor boundary 19F2C, indoor boundary 19FDA and targeting 20820. Only input dispatch and targeting are reached, 512 times each. Actor helpers have no scripts. '
           'World code computes the shared movement timestep from external clock samples; no direct timestep fixture. Clock increments 0/1/8/30 and no-button input remain controlled inputs. Twelve cases move; four zero-clock cases stay still. '
           'All CPU registers, SR, USP/SSP, complete 2MB RAM and private frames match. There are 2,048 original GPU submissions and 3,584 world helper incoming/return state comparisons. '
           'Standalone animation passes 1,538 cases and all 101 instructions; standalone camera passes 768 cases and all 144 instructions with actual math/GPU and a second CPU oracle. '
           'This is a phased bridge from checked C startup state, retaining historical startup private-stack/formatter exclusions. The 21-context ring runs world, two actors and two idles; 16 contexts including render are blocked. Synchronous GPU completion is a device model. '
           'Full boot/loading switches, remaining tasks, 3D drawing, scanout, main loop, scenes, audio and hardware validation remain unfinished. The game is not rebuilt or playable. Count remains 106: 104 CPU and two GPU; previously counted bodies are not counted again.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_timestep_answer='Yes. Actual world code computes movement time from supplied clock samples. Camera, animation and queue producers now run actual bodies. Five world scripts are configured, but only input dispatch and targeting are reached. Three boundary/redraw scripts are unreached. External clock/buttons, synchronous GPU and phased startup remain controlled; 16 tasks including render stay blocked. Queue consumption and the full game are unfinished.')
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==106
    validation.update(world_animation_full_CPU=animation,world_camera_full_CPU=camera,disc_world_actor_pipeline=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
    evidence=['verification/'+n for n in names]
    checkpoint={'recorded_at':now,'status':'code_passed_inference_review_pending','published_components':106,'new_components':0,'animation_CPU_cases':1538,'animation_instruction_coverage':[101,101],'camera_CPU_cases':768,'camera_instruction_coverage':[144,144],'combined_cases':16,'world_updates':512,'actor_iterations':1024,'task_handoffs':2576,'camera_calls':512,'animation_requests':16,'queue_consumer_run':False,'configured_world_scripts':5,'reached_world_scripts':2,'actor_helper_scripts':0,'blocked_contexts':16,'native_new_response_verified':False,'full_goal_status':'active incomplete','evidence':evidence,'next_work':'Replace input dispatch and targeting with full CPU interfaces, connect render and queue consumption, loading switches and remaining tasks. Verify native Chat and ordinary local inference scope.'}
    save(ROOT/'verification/disc-camera-animation-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path=ROOT/name;value=read(path);value.update(disc_world_actor_progress=scope,disc_world_actor_evidence=evidence,disc_camera_animation_checkpoint=checkpoint)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal: animation1538, camera768 and16combinedworld/camera/animation/actorcases passed; inference review pending.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: actual camera and animation linked in disc-world actor test; five configured/two reached world scripts remain. Full goal incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+evidence)))
        save(path,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n')
    who='Codex authored the full CPU camera/animation interfaces and integration. Original CPU/GPU and the independent Unicorn CPU decide code acceptance. Local-model role labels remain correlated; no local code was accepted and no new training/default promotion occurred. Native Chat access timed out; SDK fallback will be recorded separately.'
    note='\nCAMERA / ANIMATION CHECKPOINT — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\n'+who+'\n\nEVIDENCE\n'+'\n'.join(evidence)+'\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))

if __name__=='__main__':main()
