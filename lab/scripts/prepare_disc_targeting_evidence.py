"""Publish full targeting ABI and live scan/filter, without claiming acquisition."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn-targeting-cpu-checks.json','biwn-disc-world-targeting-checks.json'];targeting,linked=[read(ROOT/'verification'/n)for n in names]
    assert targeting['CPU_cases']==1026 and targeting['CPU_instruction_coverage']==[183,183]and targeting['host_guards']==18
    assert linked['cases']==16 and linked['targeting_calls']==512 and linked['task_handoffs']==2576 and linked['world_updates']==512
    assert len(linked['configured_world_helper_scripts'])==4 and sum(n>0 for n in linked['reached_world_helper_script_counts'].values())==1
    assert linked['reached_world_helper_script_counts']['0x191f4']==512 and not any(linked['targeting_direct_math_call_counts'].values())and not any(linked['targeting_final_active_flags'])
    # These facts derive from the accepted trace, not a new code run.
    linked['targeting_live_acquisition_proved']=False
    linked['limits'][-1]='All16scene cases reach only targeting scan/filter: no direct targeting math calls or activeflag. Both captured active actors start with targetabilityword0. Standalone syntheticcandidatefixtures cover acquisition/projection/radius separately. No live target acquisition, visible crosshair or rendered target validation is proved.'
    rows=read(Path(linked['directory'])/'fixtures.json');linked.update(world_helper_incoming_CPU_comparisons=sum(len(r['rebuilt']['world_calls'])for r in rows),world_helper_return_CPU_comparisons=sum(len(r['rebuilt']['world_returns'])for r in rows),world_complete_return_CPU_comparisons=sum(len(r['rebuilt']['world_time_steps'])for r in rows))
    assert linked['world_helper_incoming_CPU_comparisons']==linked['world_helper_return_CPU_comparisons']==3584
    save(ROOT/'verification/biwn-disc-world-targeting-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    for proof in [targeting,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass'
        for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
        target=folder/'publication-snapshot';target.mkdir(exist_ok=True);files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['check_biwn_targeting_cpu.py','check_biwn_camera_cpu.py','check_biwn_targeting.py','check_biwn_camera.py','check_biwn_disc_world_actors.py','check_biwn_disc_scene_actors.py','check_biwn_actor_full_movement_runtime.py','check_biwn_actor_lifecycle_runtime.py','check_biwn_world_cpu.py']]
        for path in files:shutil.copy2(path,target/path.name)
        save(target/'manifest.json',{'recorded_at':now,'scope':'Accepted code hashes; harness snapshot at publication, with added trace-derived acquisition limits.','sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    scope=('Targeting now runs actual reconstructed full CPU code alongside camera, animation, world, two actors and two idles in the disc-loaded test. All 16 cases match original CPU/GPU: 512 world updates, 1,024 actor iterations and 2,576 task handoffs. '
           'Targeting is called 512 times but only scans/filters; both captured active actors start with eligibility word zero. There are zero direct targeting math calls and zero final active flags. Live target acquisition and a visible crosshair are not proved. '
           'Separately, 1,026 synthetic candidate/matrix cases cover all 183 targeting instructions, actual direction/multiply/division, scoring, projection, cursor changes and radius. All CPU registers, SR/USP/SSP, complete 2MB RAM, private frames and ordered bus accesses match two CPU oracles; 18 host guards pass. '
           'Four world helper scripts remain configured: input dispatch 191F4, inventory redraw 1B786, outdoor boundary 19F2C and indoor boundary 19FDA. Only input dispatch is reached, 512 times; the other three are unreached. All actor helpers, camera, animation and targeting run actual bodies. '
           'Animation makes 16 queue requests; the consumer and render task do not run. World code computes movement time from supplied clock samples. Clock increments 0/1/8/30, no-button input and synchronous GPU completion remain controlled inputs/models. '
           'The phased bridge from checked C startup retains historical startup private-stack/formatter exclusions and a 21-context ring; 16 contexts including render are blocked. Full boot/loading switches, remaining tasks, 3D drawing/scanout, main loop/scenes, audio and hardware validation are unfinished. The game is not playable. Count remains 106: 104 CPU and two GPU; no recount of existing components.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_timestep_answer='Actual world code computes movement time from supplied clock samples. Camera, animation and targeting now run actual bodies. Four scripts are configured; only input dispatch is reached. Targeting scans/skips the captured actors and has no live acquisition. Rendering/queue consumption, remaining tasks and full game remain unfinished.',checked_targeting_answer='The full targeting function is rebuilt and its standalone scoring/projection/radius cases pass, but the actual disc-scene test only scans/filters. It makes512calls with no targeting math and no active flag; captured active actors have eligibilityword0. Live acquisition/crosshair is unproved.')
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==106
    validation.update(world_targeting_full_CPU=targeting,disc_world_actor_pipeline=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
    checkpoint={'recorded_at':now,'status':'code_passed_local_inference_review_pending','published_components':106,'new_components':0,'targeting_CPU_cases':1026,'targeting_instruction_coverage':[183,183],'host_guards':18,'combined_cases':16,'targeting_calls':512,'world_updates':512,'actor_iterations':1024,'task_handoffs':2576,'configured_world_scripts':4,'reached_world_scripts':1,'targeting_live_acquisition_proved':False,'targeting_live_math_calls':0,'native_new_response_verified':False,'full_goal_status':'active incomplete','evidence':['verification/'+n for n in names],
                'next_work':'Add full CPU input dispatcher and real continuation/yield behavior, then connect render/queue consumption/loading switches/remaining tasks and actual scene target producers. Verify ordinary local inference and native Chat when accessible.'}
    save(ROOT/'verification/disc-targeting-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path=ROOT/name;value=read(path);value.update(disc_world_actor_progress=scope,disc_world_actor_evidence=checkpoint['evidence'],disc_targeting_checkpoint=checkpoint)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:1026targetingCPU/all183instructions/18guards and16combinedscene cases passed; targeting scan/filter only.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: full targeting CPU and actual live scan/filter linked; four configured/one reached world script. No live target acquisition claim. Full goal incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(path,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n')
    note='\nTARGETING CHECKPOINT — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored the full CPU targeting interface and integration; original native CPU and Unicorn decide acceptance. No local-model code, new training or model promotion. Initial1026codecases andcoveragepassed; helperfailurefixturewrongly selectednesteddivisioninside direction. Correctedfixtureselects targetingownJSR; final1026cases/18guards passed with no Cbehaviorchange.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
