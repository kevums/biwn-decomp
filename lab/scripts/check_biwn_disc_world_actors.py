"""Disc scene actors share actual world-generated timing in the21-context ring."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_disc_scene_actors as scene
ROOT=scene.ROOT;CPU=scene.CPU;get=scene.get;save=scene.save;WORLD=0xc2128
read=lambda p:json.loads(p.read_text())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',type=Path,required=True);ap.add_argument('--limit',type=int);ap.add_argument('--real-animation',action='store_true');ap.add_argument('--real-camera',action='store_true');ap.add_argument('--real-targeting',action='store_true');ap.add_argument('--real-dispatch',action='store_true');opt=ap.parse_args();capture=opt.capture.resolve()
    assert not opt.real_camera or opt.real_animation,'Camera phase includes actual animation; pass both flags.'
    assert not opt.real_targeting or opt.real_camera,'Targeting phase includes camera; pass all three flags.'
    assert not opt.real_dispatch or opt.real_targeting,'Dispatcher phase includes targeting; pass all four flags.'
    assert read(capture/'status.json')['status']in ['terminal_preflight','terminal_pass']
    phase='biwn-disc-world-dispatch'if opt.real_dispatch else'biwn-disc-world-targeting'if opt.real_targeting else'biwn-disc-world-camera'if opt.real_camera else'biwn-disc-world-animation'if opt.real_animation else'biwn-disc-world-actors'
    out=ROOT/'verification'/phase/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';old=read(ROOT/'verification/biwn-actor-lifecycle-runtime-checks.json')
    names=[n for n in old['source_sha256']if n.endswith('.c')]+['biwn_world_cpu.c','biwn_input_poll_cpu.c'];library=out/'libdisc-world-actors.dylib'
    if opt.real_animation:names.append('biwn_animation_cpu.c')
    if opt.real_camera:names.append('biwn_camera_cpu.c')
    if opt.real_targeting:names.append('biwn_targeting_cpu.c')
    if opt.real_dispatch:names.append('biwn_input_dispatch_cpu.c')
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    vectors=[(p,step)for p in sorted(capture.glob('startup-C-*.bin'))for step in [0,1,8,30]][:opt.limit or None];assert vectors
    runtime=scene.Runtime(library);rows=[]
    if opt.real_animation:runtime.enable_animation()
    if opt.real_camera:runtime.enable_camera()
    if opt.real_targeting:runtime.enable_targeting()
    if opt.real_dispatch:runtime.enable_dispatch()
    try:
        for i,(path,clock_step)in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});index=path.stem.split('-')[-1];info=read(capture/f'startup-capture-{index}.json');assert info['startup_fullCPU_visibleRAM_match']
            ram=bytearray(path.read_bytes());assert hashlib.sha256(ram).hexdigest()==info['C_RAM_sha256']
            assert get(ram,WORLD+8)==0x1a544 and get(ram,0x4c24c)==0
            for ctx in scene.startup.CONTEXTS:ram[ctx+26:ctx+30]=(0 if ctx in scene.RUNNABLE|{WORLD}else 1).to_bytes(4,'big')
            initial=CPU();initial.registers[:]=info['CPU']['registers'];initial.pc=info['CPU']['pc'];initial.sr=info['CPU']['sr'];initial.usp=info['CPU']['usp'];initial.ssp=info['CPU']['ssp']
            runtime.enable_world(clock_step);left,expected,original=runtime.native(bytes(ram),initial,32);right,actual,rebuilt=runtime.translated(bytes(ram),initial,32)
            keys=['calls','movements','handoffs','yields','helper_returns','world_calls','world_returns','world_time_steps','world_poll_count']
            if opt.real_animation:keys.append('animation_requests')
            if opt.real_dispatch:keys.append('dispatcher_helper_calls')
            if left!=right or bytes(expected)!=bytes(actual)or any(original[k]!=rebuilt[k]for k in keys):
                save(out/'mismatch.json',{'case':i,'capture':str(path),'clock_step':clock_step,'CPU_original':scene.live.prior.scheduler.cpu_dict(expected),'CPU_C':scene.live.prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:100],'original':original,'rebuilt':rebuilt});raise AssertionError(str(out/'mismatch.json'))
            assert len(rebuilt['movements'])==64 and len(rebuilt['handoffs'])==161
            assert len(rebuilt['world_time_steps'])==rebuilt['world_poll_count']==32 and all(r['time_step']==clock_step for r in rebuilt['world_time_steps'])
            assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']and original['device']['original_GPUExec1_calls']>0
            moved=any(any(bytes(ram)[0x49d6c+j*206+o:0x49d6c+j*206+o+w]!=right[0x49d6c+j*206+o:0x49d6c+j*206+o+w]for o,w in[(4,4),(8,2),(10,4)])for j in range(2))
            rows.append({'case':i,'startup_capture':str(path),'startup_capture_sha256':info['C_RAM_sha256'],'external_clock_step':clock_step,'direct_timestep_fixture':False,
                         'positions_changed':moved,'animation_queue_count':get(right,0x112940,2),'targeting_active_flag':get(right,0x49d5c,2),'targeting_selected_slot':get(right,0x49d60,2),'targeting_cursor':[get(right,0x49d68,2),get(right,0x49d6a,2)],'CPU':scene.live.prior.scheduler.cpu_dict(actual),'original':original,'rebuilt':rebuilt,'whole2MBRAM_allCPU_privateframes_match':True})
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
    save(out/'fixtures.json',rows)
    if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
    moved=sum(r['positions_changed']for r in rows);assert moved==12
    scripts=[0x191f4,0x1b786,0x19f2c,0x19fda,0xf0fa,0xeb04,0x20820]
    if opt.real_animation:scripts.remove(0xeb04)
    if opt.real_camera:scripts.remove(0xf0fa)
    if opt.real_targeting:scripts.remove(0x20820)
    if opt.real_dispatch:scripts.remove(0x191f4)
    reached={hex(target):sum(sum(call['target']==target for call in row['rebuilt']['world_calls'])for row in rows)for target in scripts}
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'disc_world_generates_actor_timing_with_real_input_GPU_and_scheduler_matches_original',
            'directory':str(out),'cases':len(rows),'actor_iterations':1024,'world_updates':512,'task_handoffs':2576,'created_contexts_preserved':21,'runnable_world_actor_idle_contexts':5,'blocked_contexts':16,
            'world_context':hex(WORLD),'world_caller_fullCPU_real':True,'input_poll_fullCPU_real':True,'world_and_actor_GPU_math_real':True,'actor_helper_scripts':[],
            'configured_world_helper_scripts':[hex(a)for a in scripts],'reached_world_helper_script_counts':reached,
            'shared_timestep_directly_scripted':False,'world_caller_generates_actor_timestep':True,'external_clock_step_inputs':[0,1,8,30],'external_button_input':'No buttons; actual pinned joystick row select/read implementation.',
            'cases_with_position_change':moved,'startup_C_scene_task_state_linked':True,'uninterrupted_startup_actor_execution':False,'geometry_replaced_by_synthetic_grid':False,
            'allCPU_SR_USP_SSP_complete2MBRAM_privateframes_compared':True,'synchronous_GPU_completion':True,'new_components':0,
            'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'startup_capture_directory':str(capture),
            'matched':['Actual world1A544/1A188 and twoF4D8actor/twoidle bodies now execute in the preserved21-context ring after the initial render yield. World consumes actualE4C0 emulatedpad polling and externalclock samples, computes4C24C itself, and actors consume that shared timestep.',
                       'Both world and actorE220/E098 andGPU4320math execute original/C bodies. Actors use Cstartupdisc-loaded room/tile/region/model/texture data. CompleteCPU/RAM/privateframes and all actor/world helper boundary fullstates/returns/handoffs match.'],
            'limits':['Seven world helper bodies are configured scripts: inputdispatch,inventoryredraw,two worldboundaryhandlers,camera,animation,targeting; report gives reachedcounts. Actorhelpers have no scripts. Their existing logicalC bodies do not yet supply fullCPU/task-continuation interfaces for this combined proof.',
                      'Phased bridge seeded from common checkedCstartupRAM/CPU; historicalstartupprivate-stack/formatterexclusions retained. Sixteencontexts deliberatelyblocked, includingrenderafterinitialyield; loadingcompletion/BIOSadapters/startupHUDscripts andfullrender/fullgame remain unfinished.',
                      'Externalclock/button samples andsynchronousGPUcompletion are explicit device inputs/models, not physicalcontroller/timing orconcurrentdispatcher. No actual-scene removal/reuse stimulus; separate synthetic-scene lifecycle proof remains. Full3Ddraw/scanout/mainloop/scenes/audio/game/hardware unfinished.'],
            'compiler':command}
    if opt.real_animation:
        requests=sum(len(row['rebuilt']['animation_requests'])for row in rows);assert requests and all(0<row['animation_queue_count']<=40 for row in rows)
        report.update(status='disc_world_actors_with_actual_animation_and_queue_match_original',world_animation_fullCPU_real=True,animation_queue_real=True,
                      animation_request_calls=requests,animation_request_arguments_compared=True,final_queue_counts=[row['animation_queue_count']for row in rows],queue_consumer_run=False)
        report['matched'].append('Actual EB04 world-player animation and nested EAC4 queue now execute original/C bodies, including full CPU returns/private frames and every queue-call argument. No script creates these requests; no consumer/render is run.')
        report['limits'][0]='Six world-helper scripts are configured: inputdispatch,inventoryredraw,two worldboundaryhandlers,camera,targeting. Report gives reachedcounts. Worldanimation/queue andallactorhelpers runactualbodies. Remaining logical Chelpers lack completeCPU/continuation interfaces here.'
    if opt.real_camera:
        report.update(status='disc_world_actors_with_actual_camera_animation_and_GPU_match_original',world_camera_fullCPU_real=True,camera_multiply_direction_GPU_real=True,
                      camera_calls=sum(r['original']['steps'].count(0xf0fa)for r in rows),original_GPU_submit_entries=sum(r['original']['steps'].count(0xe220)for r in rows))
        assert report['camera_calls']==512 and report['original_GPU_submit_entries']==2048
        report['matched'].append('Actual F0FA camera caller with E540 multiply,13440 direction and E220/E098/GPU4320 now runs in the world task. Camera full CPU/private frames and resulting camera/view globals participate in complete comparison.')
        report['limits'][0]='Five world-helper scripts are configured: inputdispatch,inventoryredraw,two worldboundaryhandlers,targeting. Report gives reachedcounts. Camera/animation/queue and all actor helpers run actual bodies. Remaining logical Chelpers lack completeCPU/continuation interfaces here.'
    if opt.real_targeting:
        direct={hex(target):sum(sum(row['original']['steps'].count(pc)for pc in pcs)for row in rows)for target,pcs in [(0x13440,[0x208a4]),(0xe540,[0x208ce,0x208d8,0x208e4,0x20a7e]),(0xe588,[0x20950,0x2096a])]}
        report.update(status='disc_world_actual_targeting_camera_animation_actors_match_original',world_targeting_fullCPU_real=True,targeting_calls=sum(row['original']['steps'].count(0x20820)for row in rows),targeting_direct_math_call_counts=direct,targeting_final_active_flags=[row['targeting_active_flag']for row in rows],targeting_final_selected_slots=[row['targeting_selected_slot']for row in rows],targeting_live_acquisition_proved=False)
        assert report['targeting_calls']==512
        report['matched'].append('Actual20820 targeting now runs in the world task, including full CPU/private frames and all resulting targeting/cursor globals. Standalone proof covers scoring/projection/radius with actual math; reached integration math counts are explicit.')
        report['limits'][0]='Four world-helper scripts are configured: inputdispatch,inventoryredraw,two worldboundaryhandlers. Report gives reachedcounts. Targeting/camera/animation/queue and all actor helpers run actual bodies. Remaining logical Chelpers lack completeCPU/continuation interfaces here.'
        report['limits'].append('All16scene cases reach only targeting scan/filter: no direct targeting math calls or activeflag. Both captured active actors start with targetabilityword0. Standalone syntheticcandidatefixtures cover acquisition/projection/radius separately. No live target acquisition, visible crosshair or rendered target validation is proved.')
    if opt.real_dispatch:
        report.update(status='disc_world_actual_dispatch_targeting_camera_animation_actors_match_original',world_dispatch_fullCPU_real=True,dispatcher_calls=sum(row['original']['steps'].count(0x191f4)for row in rows),dispatcher_nested_helper_call_count=sum(len(row['rebuilt']['dispatcher_helper_calls'])for row in rows),dispatcher_inner_yields_in_disc_scene=sum(sum(y['context']==WORLD and y['return_PC']in [0x194e6,0x1968e]for y in row['rebuilt']['yields'])for row in rows),dispatcher_continuations_in_disc_scene_verified=False,
                      unsupported_dispatcher_helper_targets=[hex(a)for a in scene.dispatch_logic.HELPERS if a not in [0xe4c0,0xeb04,0xe588,0xdf60]])
        assert report['dispatcher_calls']==512 and report['dispatcher_nested_helper_call_count']==0
        report['matched'].append('Actual191F4 dispatcher staticC now executes in the world task. No-buttons scene reaches no nested dispatcher services/yields. Complete CPU/privateframes/RAM match; no helper scripts are invoked during this phase.')
        report['limits'][0]='Three world-helper scripts configured, all unreached: inventoryredraw and two worldboundaryhandlers. Dispatcher/camera/animation/targeting and actor helpers run actual bodies in this no-button scene. Fifteen nested dispatcher service bodies lack fullCPU interfaces; reaching them fails explicitly. Inner dispatcher yields are separately tested in a synthetic3context ring, not this disc-world continuation.'
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification'/(phase+'-checks.json'),report);print(json.dumps(report))

if __name__=='__main__':main()
