"""Publish actual world/input fullCPU and generated actor timing, with callee limits."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();names=['biwn-world-cpu-checks.json','biwn-world-input-cpu-checks.json','biwn-disc-world-actors-checks.json'];proofs={n:read(ROOT/'verification'/n)for n in names};world,inputs,linked=proofs.values()
    assert world['CPU_cases']==inputs['CPU_cases']==1035 and world['CPU_instruction_coverage']==[281,281]and inputs['CPU_instruction_coverage']==[313,313]
    assert linked['cases']==16 and linked['task_handoffs']==2576 and linked['world_updates']==512 and not linked['shared_timestep_directly_scripted']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for proof in proofs.values():
        out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass'
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
        snapshot=out/'harness-snapshot';snapshot.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in ['check_biwn_world_cpu.py','check_biwn_world_input_cpu.py','check_biwn_disc_world_actors.py','check_biwn_disc_scene_actors.py','check_biwn_world_update.py','check_biwn_actor_full_movement_runtime.py','check_biwn_actor_lifecycle_runtime.py','check_biwn_scheduler.py','emulated_pad_input.py']]
        for path in files:shutil.copy2(path,snapshot/path.name)
        save(snapshot/'manifest.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files})
    rows=read(Path(linked['directory'])/'fixtures.json')
    linked.update(actor_helper_return_CPU_comparisons=sum(len(r['rebuilt']['helper_returns'])for r in rows),world_helper_incoming_CPU_comparisons=sum(len(r['rebuilt']['world_calls'])for r in rows),world_helper_return_CPU_comparisons=sum(len(r['rebuilt']['world_returns'])for r in rows),world_complete_return_CPU_comparisons=sum(len(r['rebuilt']['world_time_steps'])for r in rows),original_GPU_submit_entries=sum(r['original']['steps'].count(0xe220)for r in rows))
    assert linked['world_helper_return_CPU_comparisons']==linked['world_helper_incoming_CPU_comparisons']==3072 and linked['original_GPU_submit_entries']==1536
    save(ROOT/'verification/biwn-disc-world-actors-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    cases=read(Path(world['directory'])/'fixtures.json')
    negative=next(r for r in cases if [e[3]for e in r['trace']if e[:3]==['w',0x4c24c,4]]==[0xffffffff])
    clamp=next(r for r in cases if [e[3]for e in r['trace']if e[:3]==['w',0x4c24c,4]]==[0x7fffffff,30])
    scope=('The preserved 21-context scene ring now runs the actual full-CPU world caller/input poll, two actor contexts and two idle tasks. '
           'Sixteen cases match original CPU/GPU across 512 world updates, 1,024 actor iterations and 2,576 real handoffs. Both world and actor GPU movement is computed by real bodies. '
           'The world caller computes shared timestep4C24C from supplied clock samples and previous46252; the test no longer supplies the timestep directly. Clock increments0/1/8/30 and no-button input are controlled device inputs;12cases move andfourzero-clock casesstaystill. '
           'All registers/SR/USP/SSP, complete2MBRAM/privateframes,1,536originalGPUsubmitentries,3,072worldhelper incoming/returnCPUstates and512worldreturnCPUstates compare. Actor helpers have no scripts. '
           'Seven world-helper scripts are configured: inputdispatch191F4,inventoryredraw1B786,worldboundaries19F2C/19FDA,cameraF0FA,animationEB04,targeting20820. Only191F4/F0FA/EB04/20820 are reached,512times each; the otherthree areunreached. Their logical C implementations do not yet have the required full CPU/continuation interfaces here. '
           'Standalone full-CPU world caller/digit helper passes1,035cases/all281instructions/23guards; actual input-poll linkage passes1,035cases/all313instructions,1,317polls and5,268pinned joystick rowreads. '
           'The clock difference wraps32bits and is upper-clamped using a signedcomparison at30. Clock0 minusprevious1 leavesFFFFFFFF;7FFFFFFF clamps to1E. Negative results are not clamped tozero. '
           'This remains a phased bridge from checked CstartupRAM/CPU, with historical startup private-stack/formatter exclusions,16blockedcontexts includingrender, synchronousGPUcompletion, and externalclock/button samples. '
           'Actual-scene removal/reuse is not stimulated; the separate synthetic-scene lifecycle proof remains valid. Full loading switches, remaining tasks,3Ddraw/scanout/mainloop/scenes/audio/game/hardware are unfinished. Count remains106:104CPU/twoGPU; existing world/input/digit bodies are not recounted.')
    examples={'checked_world_actor_scope':scope,'checked_timestep_answer':'Yes, the actual world caller now computes the actors\' shared timestep from external clock samples and its previous-clock field in a16-case disc-scene task-ring proof. It is not written directly by the test. Seven world helper scripts are configured; four are reached (input dispatch, camera, animation, targeting), while actor helpers/input polling/world+actor GPU math/scheduler run actual bodies. Sixteen contexts including render remain blocked; phased startup, synchronousGPU/device inputs and fullgame limitations remain.',
              'checked_signed_clock_example':{'world_case':negative['case'],'clock':'0x00000000','previous':'0x00000001','timestep_writes':['0xffffffff'],'negative_is_not_lower_clamped':True},
              'checked_upper_clock_example':{'world_case':clamp['case'],'timestep_writes':['0x7fffffff','0x0000001e'],'signed_upper_limit_decimal':30},
              'checked_clock_answer':'Clock0 minusprevious1 wraps toFFFFFFFF and remains negative; this source only clamps signed results above30. A raw7FFFFFFF result is written, then replaced with0000001E. It does not clamp all values to0..30.'}
    save(ROOT/'verification/world-actor-checked-examples.json',examples)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==106
    validation.update(world_full_CPU_reconstruction=world,world_real_input_full_CPU=inputs,disc_world_actor_pipeline=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
    path=ROOT/'scripts/summarize_biwn_checks.py';text=path.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)"
    block="""    disc_world_path=root/'verification/biwn-disc-world-actors-checks.json'
    if disc_world_path.exists():
        linked=json.loads(disc_world_path.read_text())
        if linked['cases']!=16 or linked['task_handoffs']!=2576 or linked['shared_timestep_directly_scripted']:raise ValueError('Disc world/actor proof incomplete')
        runtime['world_full_CPU_reconstruction']={**json.loads((root/'verification/biwn-world-cpu-checks.json').read_text()),'report':str(root/'verification/biwn-world-cpu-checks.json')}
        runtime['world_real_input_full_CPU']={**json.loads((root/'verification/biwn-world-input-cpu-checks.json').read_text()),'report':str(root/'verification/biwn-world-input-cpu-checks.json')}
        runtime['disc_world_actor_pipeline']={**linked,'report':str(disc_world_path)}
        runtime['world_actor_checked_examples']=json.loads((root/'verification/world-actor-checked-examples.json').read_text())
"""
    assert 'disc_world_actor_pipeline'not in text;path.write_text(text.replace(needle,block+needle))
    path=ROOT/'chat_tools.py';text=path.read_text();needle="        proof=observed['actor_disc_scene_pipeline'];examples=observed['actor_disc_scene_checked_examples']"
    block="""        if 'disc_world_actor_pipeline' in observed:
            proof=observed['disc_world_actor_pipeline'];examples=observed['world_actor_checked_examples']
            checks=json.loads((folder/'boot-slice-validation.json').read_text())
            compact={'project':'Black Ice White Noise, Atari Jaguar CD','whole_game_decompilation':'incomplete','working_game_reconstruction':False,'physical_hardware_validation':False,
                     'checked_components':checks['portable_C_component_count'],'processor_components':checks['processor_component_counts'],
                     'current_world_actors':{k:proof[k]for k in ['report','cases','actor_iterations','world_updates','task_handoffs','created_contexts_preserved','runnable_world_actor_idle_contexts','blocked_contexts','world_caller_fullCPU_real','input_poll_fullCPU_real','world_and_actor_GPU_math_real','actor_helper_scripts','configured_world_helper_scripts','reached_world_helper_script_counts','shared_timestep_directly_scripted','world_caller_generates_actor_timestep','external_clock_step_inputs','external_button_input','cases_with_position_change','uninterrupted_startup_actor_execution','allCPU_SR_USP_SSP_complete2MBRAM_privateframes_compared','synchronous_GPU_completion','matched','limits']},**examples}
            return record('project_evidence',{'topic':topic},compact)
        proof=observed['actor_disc_scene_pipeline'];examples=observed['actor_disc_scene_checked_examples']"""
    assert needle in text;text=text.replace(needle,block,1)
    needle="        return compact\n    def latest_pipeline(compact,observed):"
    block="""        if 'disc_world_actor_pipeline' in observed:
            proof=observed['disc_world_actor_pipeline']
            compact['current_world_actors']={k:proof[k]for k in ['report','cases','actor_iterations','world_updates','task_handoffs','runnable_world_actor_idle_contexts','blocked_contexts','world_caller_generates_actor_timestep','shared_timestep_directly_scripted','configured_world_helper_scripts','reached_world_helper_script_counts','actor_helper_scripts','world_and_actor_GPU_math_real','external_clock_step_inputs','matched','limits']}
            compact.update(observed['world_actor_checked_examples'])
            compact['current_vs_historical']='Current_world_actors is newest: actual world now generates actor timing in the disc-scene ring; old actor-only bridge had direct timestep inputs and blocked world. Synthetic-scene removal/reuse and historical startup/render proofs retain their separate scope. Fullgame remains incomplete.'
            if topic in ['world_update','input_poll']:compact['world_full_CPU_reconstruction']=observed['world_full_CPU_reconstruction'];compact['world_real_input_full_CPU']=observed['world_real_input_full_CPU']
            if 'checked_current_summary' in compact:compact['checked_current_summary']=compact['checked_world_actor_scope']
            if 'startup_scope' in compact:compact['startup_scope']='Newest phased Cstartup disc-scene ring runs world/twoactors/twoidles, blocks16includingrender, and actual world computes timestep from externalclock samples. Historical144-case startup/render stillblocksactors; not uninterrupted fullgame.'
        return compact
    def latest_pipeline(compact,observed):"""
    assert needle in text;path.write_text(text.replace(needle,block,1))
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        path=ROOT/name;value=read(path);value.update(disc_world_actor_progress=scope,disc_world_actor_evidence=['verification/'+n for n in names])
        if name=='config.json':value['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':value['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':value['decomp_progress']=scope
        if name=='verification/setup-status.json':value['game_work']=scope
        if name=='verification/requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=scope
        save(path,value)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+scope+'\n\nNEXT\nReplace the reached world helper scripts with complete CPU interfaces, then connect render/loading/remaining tasks and fullgame systems. Full goal active and incomplete.\n')
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for name in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
    print(json.dumps({'components':106,'world_CPU_cases':1035,'real_input_cases':1035,'world_actor_cases':16,'world_updates':512,'handoffs':2576,'world_generates_timestep':True,'configured_world_scripts':7,'reached_world_scripts':4}))

if __name__=='__main__':main()
