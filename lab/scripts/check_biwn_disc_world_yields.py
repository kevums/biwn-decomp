"""Real world/input/animation yields in the preserved disc-scene actor ring.

Four resource boundaries reuse captured model/output handles as explicit
scripts. Stage animation records/flags and input polling are real bodies.
"""
import argparse,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_disc_scene_actors as scene
ROOT=scene.ROOT;CPU=scene.CPU;get=scene.get;save=scene.save;WORLD=0xc2128
read=lambda p:json.loads(p.read_text())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',type=Path,required=True);ap.add_argument('--limit',type=int);ap.add_argument('--real-resources',action='store_true');ap.add_argument('--real-cd-wrappers',action='store_true');ap.add_argument('--loading-yields',action='store_true');ap.add_argument('--live-render-queue',action='store_true');ap.add_argument('--live-scene-draw',action='store_true');ap.add_argument('--live-geometry-records',action='store_true');ap.add_argument('--live-gpu-geometry',action='store_true');ap.add_argument('--integer-divider',action='store_true');opt=ap.parse_args();capture=opt.capture.resolve();opt.live_gpu_geometry|=opt.integer_divider;opt.live_geometry_records|=opt.live_gpu_geometry;opt.live_scene_draw|=opt.live_geometry_records;opt.live_render_queue|=opt.live_scene_draw;opt.loading_yields|=opt.live_render_queue;opt.real_cd_wrappers|=opt.loading_yields;opt.real_resources|=opt.real_cd_wrappers;opt.real_memory=opt.real_resources
    phase='biwn-disc-world-integer-gpu-geometry'if opt.integer_divider else'biwn-disc-world-gpu-geometry'if opt.live_gpu_geometry else'biwn-disc-world-geometry-records'if opt.live_geometry_records else'biwn-disc-world-scene-draw'if opt.live_scene_draw else'biwn-disc-world-render-queue'if opt.live_render_queue else'biwn-disc-world-loading-yields'if opt.loading_yields else'biwn-disc-world-cd-wrappers'if opt.real_cd_wrappers else'biwn-disc-world-resources'if opt.real_resources else'biwn-disc-world-yields'
    out=ROOT/'verification'/phase/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';previous=read(ROOT/'verification/biwn-disc-world-dispatch-checks.json');names=[n for n in previous['source_sha256']if n.endswith('.c')];library=out/'libdisc-world-yields.dylib'
    if opt.real_memory:names.append('biwn_resource_cpu.c')
    if opt.real_resources:names.append('biwn_cd_math.c')
    if opt.real_cd_wrappers:names.append('biwn_cd_cpu.c')
    if opt.live_render_queue:names.append('biwn_render_queue_cpu.c')
    if opt.live_scene_draw:names.append('biwn_scene_draw_cpu.c')
    if opt.live_geometry_records:names.append('biwn_geometry_records_cpu.c')
    if opt.live_gpu_geometry:names.append('biwn_gpu_geometry_submit_cpu.c')
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    vectors=[(path,step,index)for path in sorted(capture.glob('startup-C-*.bin'))for step in [8,30]for index in [1,2]][:opt.limit or None]
    device_library=ROOT/('tools/libbiwn-integer-render-device.dylib'if opt.integer_divider else'tools/libbiwn-render-geometry-device.dylib');runtime=scene.Runtime(library,device_library)if opt.live_gpu_geometry else scene.Runtime(library); runtime.enable_animation();runtime.enable_camera();runtime.enable_targeting();runtime.enable_dispatch();runtime.enable_resource_fixture([[17,18],[],[17,18],[]]);rows=[]
    if opt.real_memory:runtime.enable_resource_memory()
    if opt.real_resources:runtime.enable_resource_disc()
    if opt.real_cd_wrappers:runtime.enable_cd_cpu()
    if opt.loading_yields:runtime.enable_loading_yields()
    if opt.live_render_queue:runtime.enable_render_queue()
    if opt.live_scene_draw:runtime.enable_scene_draw()
    if opt.live_geometry_records:runtime.enable_geometry_records()
    if opt.live_gpu_geometry:runtime.enable_GPU_geometry()
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
            if opt.live_gpu_geometry:keys.append('GPU_geometry_CPU_calls')
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
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'disc_world_dispatcher_internal_yields_actual_animation_and_actor_ring_match_original','directory':str(out),'cases':len(rows),'world_updates':sum(len(r['rebuilt']['world_time_steps'])for r in rows),'actor_iterations':sum(len(r['rebuilt']['movements'])for r in rows),'task_handoffs':sum(len(r['rebuilt']['handoffs'])for r in rows),'dispatcher_inner_yields':sum(sum(r['source_inner_yield_return_counts'].values())for r in rows),'both_inner_yield_sites_in_every_case':True,'disc_world_dispatcher_continuations_verified':True,
                'animation_requests':sum(len(r['rebuilt']['animation_requests'])for r in rows),'animation_frame_flags_scripted':False,'animation_sequence_records_from_preserved_stage':True,'resource_fixture_call_count':sum(len(r['rebuilt']['resource_fixture_calls'])for r in rows),'resource_script_targets':['0x1b002','0x1af04','0x1545c','0x152a2'],
                'configured_top_world_helper_scripts':['0x1b786','0x19f2c','0x19fda'],'reached_top_world_helper_script_counts':{hex(a):sum(sum(c['target']==a for c in r['rebuilt']['world_calls'])for r in rows)for a in [0x1b786,0x19f2c,0x19fda]},
                'preserved_contexts':21,'runnable_contexts':5,'blocked_contexts':16,'original_CPU_GPU_oracles':True,'C_uses_original_CPU_GPU_execution':False,'queue_consumer_run':False,'new_components':0,
                'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'startup_capture_directory':str(capture),
                'matched':['Actual world caller now suspends inside both equipment animation waits and resumes its original1A26C continuation after the full input RTS. Actual scheduler runs two disc-scene actors/twoidles while private world/input/animation/JSR/exception frames persist. FullCPU/SR/USP/SSP/whole2MBRAM, all source helper boundaries and every handoff match original CPU/GPU.',
                           'Actual pinned joystick B+C press/release/repress, existing captured inventory items24/29 and original stage animation sequences/immutable frameflags drive both waits. Actual EB04/EAC4 produces queue requests; no scripted completion flag.'],
                'limits':['Four resource boundaries are explicit scripts returning the captured model/output handles; frees/releases/allocations/acquisitions and real weaponmodel lifetimes are not executed. Remaining11dispatcher service bodies are unsupported. Top-world redraw/boundary scripts remain configured; reachedcounts explicit.',
                          'Inventoryselection index1/2 is an explicit initial scenario input into captured inventory; table/items/sequences are not replaced. Phased startupbridge retains historical private-stack/formatterexclusions;16contexts includingrender blocked. Queueconsumer absent; no targetacquisition/crosshair/full3Ddraw/scanout/mainloop/audio/fullgame/hardware proof. Clock advances perinputpoll andGPUcompletion is synchronous, not real-time/concurrenthardware.'], 'compiler':command}
        if opt.real_memory:
            counts={hex(target):sum(sum(c['target']==target for c in r['rebuilt']['resource_body_calls'])for r in rows)for target in [0x1b002,0x1af04,0x1b044,0x1545c,0x152a2,0x15200,0xe3e0,0xe3ee]}
            report.update(status='disc_world_actual_release_free_allocate_with_acquire_script_matches_original',resource_script_targets=['0x1af04'],resource_memory_fullCPU_real=True,resource_body_call_counts=counts)
            assert report['resource_fixture_call_count']==(0 if opt.real_resources else 32)and all(counts[hex(a)]>=32 for a in [0x1b002,0x1545c,0x152a2])
            report['matched'].append('Actual release1B002/free1545C/allocate152A2 bodies replace three resource scripts, with all nested heap/save/JSR frames and free-list/handle changes compared. Compactor/copy are linked if reached; explicit counts state actual reach.')
            report['limits'][0]='Acquisition1AF04 remains one script returning the captured model handle,32calls. Weapon resource loading/reference increments/model ownership are not executed. Eleven other dispatcher services remain unsupported. Release/free/allocation bodies execute actual code; compaction/copy reach counts explicit. Top-world scripts remain configured with reachedcounts.'
        if opt.real_resources:
            payloads=[call['payload']for row in rows for call in row['rebuilt']['resource_body_calls']if 'payload'in call]
            report.update(status='disc_world_actual_resource_heap_loader_and_disc_payloads_match_original',resource_script_targets=[],resource_acquire_fullCPU_real=True,resource_loader_fullCPU_real=True,resource_IO_adapter_targets=['0xd206','0xd2f0','0xd306','0xdf60'],resource_IO_adapter_call_counts={hex(target):sum(sum(c['target']==target for c in row['rebuilt']['resource_IO_adapter_calls'])for row in rows)for target in [0xd206,0xd2f0,0xd306,0xdf60]},disc_transfer_requests=sum(len(row['rebuilt']['disc_requests'])for row in rows),disc_transfer_completions=sum(len(row['rebuilt']['disc_completions'])for row in rows),loaded_payloads=payloads,loaded_payload_bytes=sum(p['bytes']for p in payloads),loading_task_context_switches_verified=False,unsupported_resource_synchronization_targets=['0xdf8c','0xdf9c'])
            assert payloads and report['disc_transfer_requests']==report['disc_transfer_completions']==len(payloads)
            report['matched'].append('Actual acquisition1AF04/cache/heap and loader1B044/copy now load preserved-disc model payloads; every payload compares independently with normalized disc bytes. Four previous resource-body scripts are removed.')
            report['limits'][0]='CD offset/transfer/stop and loading-completion/yield are explicit adapters; loaderDF60 performs a completion/RTS adapter, not a scheduler switch. EquipmentDF60 still uses the actual scheduler. Resource synchronization DF8C/DF9C remains unsupported/unreached, as do11otherdispatcher services. No physicaldrive/async-loading claim. Top-world scripts and missing render/consumer/fullgame scope remain.'
        if opt.real_cd_wrappers:
            targets=[0x303c,0x3042,0xdf60]
            report.update(status='disc_world_actual_resource_CD_wrappers_and_payloads_match_original',new_components=2,cd_game_wrappers_fullCPU_real=True,cd_body_call_counts={hex(target):sum(sum(c['target']==target for c in row['rebuilt']['cd_body_calls'])for row in rows)for target in [0xd1e0,0xd206,0xd2f0,0xd306]},resource_IO_adapter_targets=[hex(a)for a in targets],resource_IO_adapter_call_counts={hex(target):sum(sum(c['target']==target for c in row['rebuilt']['resource_IO_adapter_calls'])for row in rows)for target in targets},configured_CD_game_wrapper_scripts=[],BIOS_transfer_adapters=['0x303c','0x3042'])
            assert set(report['resource_IO_adapter_call_counts'].values())==({0,32}if opt.loading_yields else{32})and set(report['cd_body_call_counts'].values())=={32}
            report['matched'].append('Actual D206 TOC/MSF with D1E0 division, D2F0 transfer wrapper and D306 stop wrapper replace game-level adapters. BIOS ABI adapters deliberately clobber A2; the real D2F0 save/restore preserves it. All nested CPU/privateframes and32disc payload hashes compare.')
            report['limits'][0]='BIOS303C/3042 transfer/stop and loaderDF60 completion remain explicit adapters. Loading DF60 still completes with RTS instead of switching tasks; equipment yields use the actual scheduler. Resource synchronization DF8C/DF9C and11otherdispatcher services remain unsupported/unreached. No physicaldrive/async-loading proof. Render/consumer/fullgame remain unfinished.'
        if opt.loading_yields:
            loading_count=sum(len(row['rebuilt']['loading_yield_calls'])for row in rows);events=[event for row in rows for event in row['rebuilt']['loading_completion_events']]
            assert loading_count==len(events)==32 and all(e['context']!=WORLD for e in events)
            report.update(status='disc_world_actual_loader_suspensions_and_scheduler_match_original',new_components=0,loading_task_context_switches_verified=True,loader_inner_yields=loading_count,loader_resume_PC='0x1b0da',loading_completion_events=events,loading_completion_event_count=len(events),resource_IO_adapter_targets=['0x303c','0x3042'],resource_IO_adapter_call_counts={k:v for k,v in report['resource_IO_adapter_call_counts'].items()if k!='0xdf60'},loading_completion_adapter_removed=True,supplied_initial_supervisor_stack='0x1ff000',historical_supplied_supervisor_stack='0x1d0000 overlaps CD payload window and is unsuitable for loading-switch tests',completion_delivery='Explicit external device tick after a real scheduler handoff away from the loading world context; supplied file bytes/progress, not physical BIOS timing.')
            report['matched'].append('Actual loader suspends at1B0D4→DF60 and resumes1B0DA through the real scheduler, retaining nested loader/acquisition/input/world source frames. File completion is delivered only after a real switch to another context; all32loading yields,completion events and privateframes match original CPU/GPU.')
            report['limits'][0]='BIOS303C/3042 remain transfer/stop adapters. Completion data/progress is an explicit external device event after a real loading scheduler switch, not reconstructed BIOS/drive timing. SynchronizationDF8C/DF9C and11otherdispatcher services remain unsupported/unreached. Render/consumer/fullgame remain unfinished; no physical-drive/real-time proof.'
        if opt.live_render_queue:
            consumer_calls=sum(sum(c['target']==0xea28 for c in r['rebuilt']['render_queue_calls'])for r in rows);decodes=sum(r['rebuilt']['device']['C_sprite_decodes']for r in rows)
            report.update(status='disc_world_live_render_task_queue_and_C_sprite_decode_match_original',queue_consumer_run=True,render_task_fullCPU_real=True,render_queue_fullCPU_real=True,render_queue_consumer_calls=consumer_calls,actual_C_sprite_decodes=decodes,render_scene_overlay_script_targets=[hex(a)for a in runtime.render_script_targets()],render_scene_overlay_script_call_counts={hex(a):sum(sum(c['target']==a for c in r['rebuilt']['render_helper_calls'])for r in rows)for a in runtime.render_script_targets()},runnable_contexts=6,blocked_contexts=15,sprite_preview_directory=str(out/'decoded-sprites'))
            assert consumer_calls>0 and decodes>0 and report['render_scene_overlay_script_call_counts']['0x181f8']==consumer_calls
            if not opt.live_scene_draw:assert report['render_scene_overlay_script_call_counts']['0x17e0e']==consumer_calls
            report['matched'].append('Actual render task now resumes17DCE, consumes live EB04/EAC4 requests through fullCPU EA28/E2B8/E098 and reconstructedGPU4B00decode, and continues real scheduler yields. Every sprite output/header/hash and completeRAM/CPU/privateframes match originalCPU/GPU; no originalGPUexecution onCside.')
            report['limits']=['Scene draw17E0E andoverlay181F8 are two explicit ABI-adversary scripts; no complete3Ddraw/viewport/scanout.15othercontexts remain blocked. BIOS303C/3042 and external file completion events remain. Synchronization still unexercised in this21-context scene, despite separate two-client readiness proof. Audio/uninterruptedboot/fullgame/hardware remain incomplete.',
                              'Captured assisted startup and declared initial inventoryselection1/2/emulatedpad B+C inputs, supplied clock increments and synchronous GPUcompletion remain controlled fixtures. Historical startup private-stack/formatter exclusions remain. Supplied supervisorstack1FF000 with4KB reserve stays outside current disc transfers. These counters are not measured physicalFPS/timing; raw sprite hashes are primary and PNGcolor conversion is a preview.']
        if opt.live_scene_draw:
            counts={hex(a):sum(sum(c['target']==a for c in r['rebuilt']['scene_draw_calls'])for r in rows)for a in [0x17e0e,0xe03a,0x17f14]}
            assert set(counts.values())=={report['render_queue_consumer_calls']}
            report.update(status='disc_world_live_scene_caller_clear_rotation_and_queue_match_original',scene_draw_caller_fullCPU_real=True,framebuffer_clear_fullCPU_real=True,buffer_rotation_fullCPU_real=True,scene_draw_body_call_counts=counts,full_scene_geometry_executed=False,full_game_viewport_proved=False,all_handoff_CPU_states_compared=True)
            report['matched'].append('Actual17E0E scene caller now executes mode selection, nestedE03A framebuffer clear with pinned blitter rasterization and17F14triplebuffer rotation. All caller/helper fullCPU/privateframes and completeRAM match original CPU/GPU in the live21-context scene.')
            report['limits'][0]='Scene caller/clear/rotation are actual fullCPU bodies, but six geometry/scene helpers plus185B2display-list and181F8overlay are eight configured ABI-adversary scripts; reached counts explicit. No complete3Dgeometry/viewport/scanout.15othercontexts remain blocked. BIOS303C/3042 and external file completion events remain. Synchronization still unexercised in this21-context scene. Audio/uninterruptedboot/fullgame/hardware remain incomplete.'
        if opt.live_geometry_records:
            counts={hex(a):sum(sum(c['target']==a for c in r['rebuilt']['geometry_record_calls'])for r in rows)for a in [0x170a0,0xe3e0,0xe220]}
            assert counts['0x170a0']==report['render_queue_consumer_calls']and counts['0xe3e0']>=counts['0x170a0']
            report.update(status='disc_world_live_geometry_records_actual_copy_and_scene_caller_match_original',new_components=1,geometry_record_builder_fullCPU_real=True,geometry_record_body_call_counts=counts,geometry_record_count_values=sorted({c['record_count']for r in rows for c in r['rebuilt']['geometry_record_calls']if c['target']==0x170a0}),geometry_nested_helper_scripts=[],full_scene_geometry_executed=False,full_game_viewport_proved=False)
            report['matched'].append('Actual170A0 builds camera/actor/static rendering records from captured disc-scene RAM, with actualE3E0copy and E220/E098/GPU4320providers if reached. FullnestedCPU/privateframes/recordcounts/completeRAM match originalCPU/GPU. Reached nested helper counts explicit.')
            report['limits'][0]='Rendering record builder170A0 is now actual fullCPU code with actual copy, but GPU4D80transform/submissionE0A6 and E0F2/E148/E19E/E202,185B2display-list and181F8overlay remain seven configured scripts; reached counts explicit. No complete3Dgeometry/viewport/scanout.15othercontexts remain blocked. BIOS/completion adapters and unexercised main-scene synchronization remain. Audio/uninterruptedboot/fullgame/hardware unfinished.'
        if opt.live_gpu_geometry:
            count=sum(r['rebuilt']['device']['C_GPU_geometry_calls']for r in rows);native_count=sum(r['original']['device']['original_GPU_geometry_calls']for r in rows)
            assert count==native_count==report['render_queue_consumer_calls']and all(not r['rebuilt']['device']['original_GPU_geometry_calls']for r in rows)
            session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);wrapper=read(session/'gpu-geometry-submit-fullCPU-generation.json');covered=set(pc for r in rows for pc in r['original']['steps'])
            assert all(row['address']in covered for row in wrapper['instructions_decoded'])
            report.update(status='disc_world_actual_GPU4D80_C_geometry_and_fullCPU_submission_match_original',new_components=1,GPU4D80_transform_C_real=True,GPU4D80_transform_live_calls=count,CPU_E0A6_submission_fullCPU_real=True,CPU_E0A6_live_calls=sum(len(r['rebuilt']['GPU_geometry_CPU_calls'])for r in rows),CPU_E0A6_source_instruction_coverage=[10,10],CPU_bus_physical_address_mask='0x00ffffff',C_CPU_bus_high_byte_aliases=sum(r['rebuilt']['device']['CPU_bus_high_byte_aliases']for r in rows),full_GPU_context_cross_kernel_proved=False,full_scene_geometry_executed=False,full_game_viewport_proved=False,device_bridge_sha256=hashlib.sha256(device_library.read_bytes()).hexdigest())
            report['source_sha256'].update({n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_gpu_geometry.c','biwn_gpu_geometry.h']})
            report['matched'].append('ActualE0A6CPUwrapper and GPU4D80geometry outputs replace that script. NativeGPU versusCkernel runs once perrenderconsumer, with fullCPU/privateframes and complete2MBRAM matching through actualscheduler/world/actors/loading. Cside executes no originalGPU/CPUgame instructions.')
            report['limits'][0]='GPU4D80 and its CPU submission execute actual code, but six lower rendering scripts remain configured:181F8overlay,E0F2,E148,E19E,E202,185B2display-list; reachedcounts explicit. Completegeometry/rasterization/viewport/scanout and15blockedtasks/audio/boot/fullgame/hardware remain incomplete. BIOS/completion adapters and unexercised main-scene synchronization remain.'
            report['limits'].append('CPUbus applies source Jaguar24bitphysical-address mask while preserving32bitregister/pointervalues. GPUkernel standalone compares fullbanks/flags/scratch; integrated proof comparesCPU/mainRAM and uses synchronous completion. Ckernel remainder is retained internally; core ROremainder/fullcross-kernelGPUcontext is not proved. GPUinitial untouchedRAM is supplied state, not reconstructed reset/boot.')
        if opt.integer_divider:
            assert all(r[side]['device']['GPU_division_control']==0 for r in rows for side in ['original','rebuilt'])
            report.update(status='source_consistent_integer_GPU4D80_live_C_scene_matches_original',new_components=0,GPU_division_control=0,host_divider_mode_correction=True,source_shader_behavior_changed=False,legacy_fractional_fixture_replaced_for_current_scene=True)
            report['limits'].append('Earlier live fixtures supplied fractionaldividercontrol1. This phase corrects onlyhostfixtureentry/controltointeger0, matchingGPUreset andsource4B00return. Earlierfractionalmathematicalproofs are retained fordeclaredinputs, notthecurrentrenderingconfiguration. OriginalCPU/GPUwritesunchanged; nofullboot/async/hardwareproof.')
        save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification'/(phase+'-checks.json'),report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
if __name__=='__main__':main()
