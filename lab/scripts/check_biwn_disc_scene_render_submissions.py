"""Actual CPU projection/draw submissions link reconstructed GPU programs to the bounded disc scene.

Geometry retains a declared reset/RAM/seed fixture; the context thereafter is
inherited through actual CPU projection/draw commands, dispatcher and shaders.
"""
import argparse,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_disc_scene_actors as scene
ROOT=scene.ROOT;CPU=scene.CPU;get=scene.get;save=scene.save;WORLD=0xc2128
read=lambda p:json.loads(p.read_text())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',type=Path,required=True);ap.add_argument('--limit',type=int);ap.add_argument('--real-resources',action='store_true');ap.add_argument('--real-cd-wrappers',action='store_true');ap.add_argument('--loading-yields',action='store_true');ap.add_argument('--live-render-queue',action='store_true');ap.add_argument('--live-scene-draw',action='store_true');ap.add_argument('--live-geometry-records',action='store_true');ap.add_argument('--live-gpu-geometry',action='store_true');ap.add_argument('--integer-divider',action='store_true');opt=ap.parse_args();opt.integer_divider=True;capture=opt.capture.resolve();opt.live_gpu_geometry|=opt.integer_divider;opt.live_geometry_records|=opt.live_gpu_geometry;opt.live_scene_draw|=opt.live_geometry_records;opt.live_render_queue|=opt.live_scene_draw;opt.loading_yields|=opt.live_render_queue;opt.real_cd_wrappers|=opt.loading_yields;opt.real_resources|=opt.real_cd_wrappers;opt.real_memory=opt.real_resources
    phase='biwn-disc-world-render-submissions'if opt.integer_divider else'biwn-disc-world-gpu-geometry'if opt.live_gpu_geometry else'biwn-disc-world-geometry-records'if opt.live_geometry_records else'biwn-disc-world-scene-draw'if opt.live_scene_draw else'biwn-disc-world-render-queue'if opt.live_render_queue else'biwn-disc-world-loading-yields'if opt.loading_yields else'biwn-disc-world-cd-wrappers'if opt.real_cd_wrappers else'biwn-disc-world-resources'if opt.real_resources else'biwn-disc-world-yields'
    out=ROOT/'verification'/phase/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';previous=read(ROOT/'verification/biwn-disc-world-dispatch-checks.json');names=[n for n in previous['source_sha256']if n.endswith('.c')];library=out/'libdisc-world-yields.dylib'
    if opt.real_memory:names.append('biwn_resource_cpu.c')
    if opt.real_resources:names.append('biwn_cd_math.c')
    if opt.real_cd_wrappers:names.append('biwn_cd_cpu.c')
    if opt.live_render_queue:names.append('biwn_render_queue_cpu.c')
    if opt.live_scene_draw:names.append('biwn_scene_draw_cpu.c')
    if opt.live_geometry_records:names.append('biwn_geometry_records_cpu.c')
    if opt.live_gpu_geometry:names.extend(['biwn_gpu_geometry_submit_cpu.c','biwn_gpu_projection_submit_cpu.c','biwn_gpu_draw_submit_cpu.c'])
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    vectors=[(path,step,index)for path in sorted(capture.glob('startup-C-*.bin'))for step in [8,30]for index in [1,2]][:opt.limit or None]
    device_library=ROOT/('tools/libbiwn-scene-render-device.dylib'if opt.integer_divider else'tools/libbiwn-render-geometry-device.dylib');runtime=scene.Runtime(library,device_library)if opt.live_gpu_geometry else scene.Runtime(library); runtime.enable_animation();runtime.enable_camera();runtime.enable_targeting();runtime.enable_dispatch();runtime.enable_resource_fixture([[17,18],[],[17,18],[]]);rows=[]
    if opt.real_memory:runtime.enable_resource_memory()
    if opt.real_resources:runtime.enable_resource_disc()
    if opt.real_cd_wrappers:runtime.enable_cd_cpu()
    if opt.loading_yields:runtime.enable_loading_yields()
    if opt.live_render_queue:runtime.enable_render_queue()
    if opt.live_scene_draw:runtime.enable_scene_draw()
    if opt.live_geometry_records:runtime.enable_geometry_records()
    if opt.live_gpu_geometry:runtime.enable_GPU_geometry();runtime.enable_GPU_render_submissions()
    try:
        for i,(path,clock_step,index)in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});info=read(capture/f'startup-capture-{path.stem.split("-")[-1]}.json');ram=bytearray(path.read_bytes());assert hashlib.sha256(ram).hexdigest()==info['C_RAM_sha256']
            assert get(ram,0x49d5a,2)==0 and get(ram,0x49d2c+index*2,2)in [0x24,0x29]
            for ctx in scene.startup.CONTEXTS:ram[ctx+26:ctx+30]=(0 if ctx in scene.RUNNABLE|{WORLD}else 1).to_bytes(4,'big')
            if opt.live_render_queue:ram[scene.startup.RENDER+26:scene.startup.RENDER+30]=bytes(4)
            for a in [0x49d54,0x49d56]:ram[a:a+2]=index.to_bytes(2,'big')
            initial=CPU();initial.registers[:]=info['CPU']['registers'];initial.pc=info['CPU']['pc'];initial.sr=info['CPU']['sr'];initial.usp=info['CPU']['usp'];initial.ssp=info['CPU']['ssp'];runtime.enable_world(clock_step)
            # The historical assisted-startup fixture supplied SSP=1D0000,
            # inside the CD transfer window1C0000..200000. Real loading
            # switches would overwrite the stream at SSP-6. Supply a stack
            # outside the bounded transfer used here, on both paths.
            if opt.loading_yields:initial.ssp=0x1ff000
            left,expected,original=runtime.native(bytes(ram),initial,64);right,actual,rebuilt=runtime.translated(bytes(ram),initial,64)
            keys=['calls','movements','handoffs','yields','helper_returns','world_calls','world_returns','world_time_steps','world_poll_count','animation_requests','dispatcher_helper_calls','resource_fixture_calls']
            if opt.real_memory:keys.append('resource_body_calls')
            if opt.real_resources:keys+=['resource_IO_adapter_calls','disc_requests','disc_completions','disc_stops']
            if opt.real_cd_wrappers:keys.append('cd_body_calls')
            if opt.loading_yields:keys+=['loading_yield_calls','loading_completion_events']
            if opt.live_render_queue:keys+=['render_queue_calls','render_helper_calls']
            if opt.live_scene_draw:keys.append('scene_draw_calls')
            if opt.live_geometry_records:keys.append('geometry_record_calls')
            if opt.live_gpu_geometry:keys+=['GPU_geometry_CPU_calls','GPU_render_CPU_calls','GPU_submission_events']
            if left!=right or bytes(expected)!=bytes(actual)or any(original[k]!=rebuilt[k]for k in keys):
                save(out/'mismatch.json',{'case':i,'capture':str(path),'clock_step':clock_step,'inventory_index':index,'CPU_original':scene.live.prior.scheduler.cpu_dict(expected),'CPU_C':scene.live.prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:100],'original':original,'rebuilt':rebuilt});raise AssertionError(str(out/'mismatch.json'))
            sites={hex(ret):sum(y['context']==WORLD and y['return_PC']==ret for y in rebuilt['yields'])for ret in [0x194e6,0x1968e]};assert all(sites.values()),sites
            assert (not rebuilt['resource_fixture_calls']if opt.real_resources else rebuilt['resource_fixture_calls'])and all(r['time_step']==clock_step for r in rebuilt['world_time_steps'])
            assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']and original['device']['original_GPUExec1_calls']>0
            moved=any(any(bytes(ram)[0x49d6c+j*206+o:0x49d6c+j*206+o+w]!=right[0x49d6c+j*206+o:0x49d6c+j*206+o+w]for o,w in [(4,4),(8,2),(10,4)])for j in range(2))
            if opt.live_render_queue:
                assert rebuilt['device']['C_sprite_decodes']>0 and original['device']['original_GPU_sprite_decodes']==rebuilt['device']['C_sprite_decodes']
                assert runtime.render_last_sprite is not None
                import animation_renderer
                sprite=runtime.render_last_sprite;folder=out/'decoded-sprites'/f'case-{i:02d}';folder.mkdir(parents=True,exist_ok=True);(folder/'sprite.raw16be').write_bytes(sprite['raw']);(folder/'sprite.png').write_bytes(animation_renderer.image_png(sprite['raw'],sprite['width'],sprite['height']));save(folder/'sprite.json',sprite['metadata'])
            rows.append({'case':i,'capture':str(path),'capture_sha256':info['C_RAM_sha256'],'clock_step':clock_step,'inventory_index':index,'supplied_initial_SSP':hex(initial.ssp),'inventory_item':hex(get(ram,0x49d2c+index*2,2)),'source_inner_yield_return_counts':sites,'final_queue_count':get(right,0x112940,2),'positions_changed':moved,'final_output_handle':hex(get(right,0x49caa)),'final_output_data':hex(get(right,get(right,0x49caa))),'CPU':scene.live.prior.scheduler.cpu_dict(actual),'original':original,'rebuilt':rebuilt,'completeCPU_2MBRAM_private_world_dispatcher_animation_scheduler_frames_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
        assert len(rows)==16
        render_count=sum(len(r['rebuilt']['GPU_render_CPU_calls'])//2 for r in rows)
        gpu_stats={name:sum(r['rebuilt']['device']['scene_render'][name]for r in rows)for name in rows[0]['rebuilt']['device']['scene_render']}
        assert gpu_stats['geometry_commands']==gpu_stats['projection_commands']==gpu_stats['draw_commands']==render_count
        assert not gpu_stats['native_GPU_steps'] and not gpu_stats['forbidden_GPU_attempts']
        assert all(r['original']['GPU_submission_events']==r['rebuilt']['GPU_submission_events']for r in rows)
        scripts={hex(a):sum(sum(c['target']==a for c in r['rebuilt']['render_helper_calls'])for r in rows)for a in runtime.render_script_targets()}
        assert set(scripts)=={'0x181f8','0xe0f2','0xe148','0x185b2'}
        wrappers={hex(target):sum(sum(c['target']==target for c in r['rebuilt']['GPU_render_CPU_calls'])for r in rows)for target in [0xe19e,0xe202]}
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='bounded_disc_scene_actual_CPU_submissions_and_C_GPU_render_chain_match_original',directory=str(out),cases=len(rows),
            render_frames=render_count,CPU_submission_calls=wrappers,GPU_scene_stats=gpu_stats,
            world_updates=sum(len(r['rebuilt']['world_time_steps'])for r in rows),actor_iterations=sum(len(r['rebuilt']['movements'])for r in rows),task_handoffs=sum(len(r['rebuilt']['handoffs'])for r in rows),
            payloads_loaded=sum(sum('payload'in c for c in r['rebuilt']['resource_body_calls'])for r in rows),loaded_payload_bytes=sum(sum(c['payload']['bytes']for c in r['rebuilt']['resource_body_calls']if 'payload'in c)for r in rows),
            remaining_render_scripts=scripts,created_contexts=21,runnable_contexts=6,blocked_contexts=15,
            complete_CPU_main_RAM_private_frames_handoffs_and_GPU_submission_states_compared=True,GPU_submission_direct_PC_count_and_hash_compared=True,
            original_GPU_execution_during_C_submissions=0,CPU_E19E_and_E202_actual=True,geometry_reset_fixture_retained=True,context_inherited_from_geometry_through_projection_and_draw=True,global_GPU_context_across_movement_sprite_proved=False,
            new_components_pending_review=1,full_game_rebuilt=False,playable=False,
            startup_capture_directory=str(capture),compiler=command,source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},
            device_library_sha256=hashlib.sha256(device_library.read_bytes()).hexdigest(),GPU_RAM_fixture_sha256=hashlib.sha256((ROOT/'render-assets/biwn-geometry-GPU-RAM-fixture.bin').read_bytes()).hexdigest(),
            matched=['Actual CPU E19E/E202 submission and E098 wait bodies replace two scripts; original CPU/GPU and reconstructed C paths compare each full CPU wrapper, all main RAM/private frames, scheduler/world/actor/loading events, and each completed GPU command architecture/RAM and direct PC count/hash.',
                     'C geometry/projection/dispatcher/setup/consumer/material/resident programs execute under an original GPUExec guard. The pinned original blitter remains the shared device.'],
            limits=['Geometry entry still resets/seeds GPU banks and supplies a fixed captured 4KB RAM fixture on both paths; context after that entry is inherited within the render frame. Movement and sprite providers retain their separate high-level C/isolated native adapters. This is not uninterrupted boot or global cross-kernel GPU context.',
                    'Four rendering scripts remain configured, with reached counts listed; fifteen other contexts blocked. BIOS303C/3042, supplied disc completion events, assisted startup, clock increments, synchronous GPU completion, inventory selections and pad inputs remain declared fixtures.',
                    'Experimental resident renderer still has unexercised source paths in its standalone coverage proof. This bounded scene run is not complete-game equivalence, display scanout, audio, physical FPS or hardware accuracy.'])
        save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification'/(phase+'-checks.json'),report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
if __name__=='__main__':main()
