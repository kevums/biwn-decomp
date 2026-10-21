"""Publish static dispatcher ABI, separate real-yield ring and no-button scene."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn-input-dispatch-cpu-checks.json','biwn-input-dispatch-yield-checks.json','biwn-disc-world-dispatch-checks.json'];abi,yielded,linked=[read(ROOT/'verification'/n)for n in names]
    assert abi['CPU_cases']==1890 and abi['CPU_instruction_coverage']==[816,816]and abi['host_guards']==38
    assert yielded['cases']==25 and yielded['task_handoffs']==225 and yielded['dispatcher_inner_yields']==75
    assert linked['cases']==16 and linked['dispatcher_calls']==512 and linked['task_handoffs']==2576 and linked['dispatcher_nested_helper_call_count']==0
    assert len(linked['configured_world_helper_scripts'])==3 and not any(linked['reached_world_helper_script_counts'].values())and len(linked['unsupported_dispatcher_helper_targets'])==15
    for proof in [abi,yielded,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snapshot=folder/'publication-snapshot';snapshot.mkdir(exist_ok=True)
        for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['generate_biwn_input_dispatch_cpu.py','check_biwn_input_dispatch_cpu.py','check_biwn_input_dispatch_yield.py','check_biwn_disc_scene_actors.py','check_biwn_disc_world_actors.py','check_biwn_input_dispatch.py','check_biwn_camera_cpu.py']]
        for path in files:shutil.copy2(path,snapshot/path.name)
        save(snapshot/'manifest.json',{'recorded_at':now,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}})
    scope=('Input dispatch now runs source-specific static C alongside world, camera, animation, targeting, two actors and two idles. All 16 no-button disc-scene cases match original CPU/GPU: 512 world updates and dispatcher calls, 1,024 actor iterations and 2,576 handoffs, complete CPU/SR/USP/SSP and 2MB RAM/private frames. '
           'Three world-helper scripts remain configured, all unreached: inventory redraw 1B786 and boundaries 19F2C/19FDA. No helper scripts execute in this phase, but this does not mean the game has no scripts or missing services. Fifteen nested dispatcher helper bodies lack full CPU interfaces; reaching them fails explicitly. The no-button scene reaches zero nested dispatcher services and zero internal yields. '
           'Separately, 1,890 dispatcher cases cover all 816 instructions/13 states and 38 guards against native CPU and Unicorn ordered bus, with 19 scripted helper boundaries. A separate synthetic three-task ring uses the actual scheduler and two real idle tasks: 25 cases, both internal yield sites, 75 suspensions and 225 handoffs, with 18 other helpers still scripted. Dispatcher yields under the real world caller are unverified. '
           'Static C has no runtime instruction decoding or original CPU calls; the readable logical C is retained. Animation produces 16 queue requests, but consumer/render remain blocked. Targeting only scans/filters; no live acquisition/crosshair is proved. '
           'The phased startup bridge retains historical private-stack/formatter exclusions and blocks 16 of 21 contexts. Clock increments 0/1/8/30, no-button input and synchronous GPU completion are controlled inputs/models. Full boot/loading switches, remaining tasks, 3D drawing/scanout, main loop/scenes, audio/game/hardware remain unfinished. The game is not playable. Count remains106:104CPU/twoGPU.')
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_timestep_answer='The actual world computes movement time from supplied clock samples. Input dispatch/camera/animation/targeting now run actual C in the no-button disc scene. Three top-level scripts are configured but none reached;15nested dispatcher services remain unsupported. Its yields pass separately in a synthetic ring, not under this world caller. Full game/render/consumer remain unfinished.',checked_dispatcher_answer='All816dispatcher instructions/13states pass1890fullCPU cases with19helper scripts. Both internal yields pass separately in25syntheticring cases/75suspensions/225actualhandoffs with18otherhelperscripted. In the16no-button discscene, dispatcher runs512times but reaches no nestedhelpers/yields. Fifteenservices and realworld-stack yield continuation remain unverified.')
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==106
    validation.update(world_dispatch_full_CPU=abi,dispatcher_scheduled_yields=yielded,disc_world_actor_pipeline=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
    path=session/'input-dispatch-fullCPU-generation.json';generation=read(path);generation.update(status='accepted_static_CPU_and_separate_yield_proofs',evidence=names,whole_game_complete=False);save(path,generation)
    checkpoint={'recorded_at':now,'status':'code_passed_local_review_pending','published_components':106,'new_components':0,'dispatcher_cases':1890,'instruction_coverage':[816,816],'host_guards':38,'yield_cases':25,'inner_yields':75,'yield_handoffs':225,'disc_cases':16,'dispatcher_calls':512,'disc_handoffs':2576,'configured_world_scripts':3,'reached_world_scripts':0,'unsupported_dispatcher_helpers':15,'disc_nested_dispatcher_calls':0,'disc_dispatcher_yields':0,'disc_dispatcher_continuations_verified':False,'full_goal_status':'active incomplete','evidence':['verification/'+n for n in names],
                'next_work':'Connect dispatcher internal yields under the real world caller and nested animation/poll/resource bodies; exercise actual inputs, render/queue consumption/loading switches and remaining tasks. Keep native Chat and everyday inference verification separate.'}
    save(ROOT/'verification/disc-dispatch-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path=ROOT/name;value=read(path);value.update(disc_world_actor_progress=scope,disc_world_actor_evidence=checkpoint['evidence'],disc_dispatch_checkpoint=checkpoint)
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:1890staticdispatcherCPU cases,25realyield cases and16no-buttondiscscene cases passed.')
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            value.update(recorded_at_utc=now,this_goal_turn_classification='Progress: static fullCPUdispatcher and separate realyield ring accepted; no-buttondiscscene has3unreachedtopscripts/15unsupportednestedservices. Realworldcaller suspension and fullgame incomplete.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(path,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n')
    note='\nSTATIC DISPATCHER / YIELD CHECKPOINT — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored the staticC generator/interfaces and harnesses; twoCPUoracles decide acceptance. No localmodel code/training/defaultpromotion. Initial yieldrun all25cases matched, but harness expected32 when only25eligible existingfixtures existed; correctedcount to25, retaining bothsites/75yields/225handoffs. No sourcebehavior repair.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
