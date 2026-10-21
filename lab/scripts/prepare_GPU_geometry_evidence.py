"""Publish accepted GPU4D80/CPUwrapper linkage and remaining draw boundaries."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=ROOT/'projects/black-ice-white-noise/restoration'
    validation=read(session/'boot-slice-validation.json');gpu=read(ROOT/'verification/biwn-gpu-geometry-checks.json');linked=read(ROOT/'verification/biwn-disc-world-gpu-geometry-checks.json');wrapper=read(session/'gpu-geometry-submit-fullCPU-generation.json')
    assert gpu['GPU_cases']==128 and gpu['source_instruction_coverage']==[434,434]and gpu['host_guards']==13 and not gpu['original_GPU_core_calls_on_C_side']
    assert linked['cases']==16 and linked['GPU4D80_transform_live_calls']==linked['CPU_E0A6_live_calls']==1008 and linked['task_handoffs']==6144 and linked['C_CPU_bus_high_byte_aliases']==870
    assert linked['CPU_E0A6_source_instruction_coverage']==[10,10]and linked['geometry_record_count_values']==[4,59]
    assert linked['render_scene_overlay_script_call_counts']=={'0x181f8':1008,'0xe0f2':0,'0xe148':0,'0xe19e':1008,'0xe202':1008,'0x185b2':1008}
    for key,value in validation['disc_world_actor_pipeline'].items():linked.setdefault(key,value)
    rows=read(Path(linked['directory'])/'fixtures.json');assert all(r['final_queue_count']==0 and all('CPU'in h for h in r['rebuilt']['handoffs'])for r in rows)
    gpu_counts=sorted({c['record_count_after_GPU']for r in rows for c in r['rebuilt']['GPU_geometry_CPU_calls']});added=sorted({(c['record_count']-c['record_count_before'])&0xffffffff for r in rows for c in r['rebuilt']['geometry_record_calls']if c['target']==0x170a0})
    assert gpu_counts==[0,55]and added==[4]
    total=sum(r['original']['steps'].count(0xe220)for r in rows);world=sum(sum(c['target']==0xe220 for c in r['rebuilt']['world_calls'])for r in rows);assert total==3488 and world==1440
    linked.update(GPU_geometry_record_counts=gpu_counts,record_builder_added_record_counts=added,full_scene_draw_executed=False,overlay_executed=False,full_scene_geometry_executed=False,full_game_viewport_proved=False,original_GPU_submit_entries=total)
    linked['movement_matrix_scope']={'whole_scene_E220_submissions':total,'world_recorded_E220_calls':world,'geometry_record_builder_E220_calls':0,'actor_E220_calls_by_difference':total-world,'geometry_record_builder_E220_provider_linked':True,'geometry_record_builder_E220_branch_executed':False,'scope':'GPU4320movement is separate fromGPU4D80geometry. Whole-scene3488movement submissions execute in world/actors; zero is only the nested170A0branch, whose actual provider is linked but unreached. Actorcount is totalminusmatchedworldcalls.'}
    previews=[]
    for i,row in enumerate(rows):
        folder=Path(linked['sprite_preview_directory'])/f'case-{i:02d}';meta=read(folder/'sprite.json');assert hashlib.sha256((folder/'sprite.raw16be').read_bytes()).hexdigest()==meta['raw_sha256']
        assert [c['output']for c in row['rebuilt']['render_queue_calls']if 'output'in c][-1]==meta
        previews.append(dict(case=i,png=str(folder/'sprite.png'),png_sha256=hashlib.sha256((folder/'sprite.png').read_bytes()).hexdigest(),raw=str(folder/'sprite.raw16be'),**meta))
    linked['decoded_sprite_previews']=previews
    gpu.update(initial_GPU_RAM_supplied=True,initial_GPU_RAM_input_files_retained=True)
    gpu['limits'][0]+=' Initial4KBGPUlocalRAM is captured before execution and supplied unchanged to C, including otherwise random unused reset bytes; inputs/outputs retained. Reset/bootRAMcontents are not reconstructed.'
    for row in read(Path(gpu['directory'])/'fixtures.json'):
        assert hashlib.sha256(Path(row['initial_GPU_RAM']).read_bytes()).hexdigest()==row['initial_GPU_RAM_sha256']and hashlib.sha256(Path(row['final_GPU_RAM']).read_bytes()).hexdigest()==row['state']['local_RAM_sha256']
    save(ROOT/'verification/biwn-gpu-geometry-checks.json',gpu);save(Path(gpu['directory'])/'report.json',gpu)
    save(ROOT/'verification/biwn-disc-world-gpu-geometry-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
    scripts=['generate_biwn_gpu_geometry.py','generate_biwn_gpu_geometry_submit_cpu.py','check_biwn_gpu_geometry.py','check_biwn_disc_scene_actors.py','check_biwn_disc_world_yields.py','check_biwn_actor_full_movement_runtime.py','check_biwn_world_movement_pipeline.py','biwn_render_geometry_device_bridge.c','biwn_geometry_probe_bridge.c','biwn_movement_device_bridge.c','biwn_inventory_device_bridge.c']
    for proof in [gpu,linked]:
        folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass';snap=folder/'publication-snapshot';snap.mkdir(exist_ok=True)
        files=[source/n for n in proof['source_sha256']]+[ROOT/'scripts'/n for n in scripts]
        for name,expected in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
        for p in files:shutil.copy2(p,snap/p.name)
        save(snap/'manifest.json',dict(recorded_at=now,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}))
    assert read(ROOT/'verification/render-geometry-device-build.json')['shader_source_sha256']==gpu['source_sha256']['biwn_gpu_geometry.c']
    assert hashlib.sha256((ROOT/'tools/libbiwn-render-geometry-device.dylib').read_bytes()).hexdigest()==linked['device_bridge_sha256']
    shutil.copy2(ROOT/'tools/libbiwn-render-geometry-device.dylib',Path(linked['directory'])/'publication-snapshot/libbiwn-render-geometry-device.dylib')
    if 'GPU_geometry_program'not in validation:
        assert validation['portable_C_component_count']==113 and validation['processor_component_counts']=={'CPU':111,'GPU':2};validation['portable_C_component_count']=114;validation['processor_component_counts']['GPU']=3
    assert validation['portable_C_component_count']==114 and validation['processor_component_counts']=={'CPU':111,'GPU':3}
    validation.update(GPU_geometry_program=gpu,disc_world_actor_pipeline=linked,disc_world_GPU_geometry_pipeline=linked,latest_aggregate_update=now,component_count_scope='One newGPU4D80program. ExistingE0A6CPUsubmission nowfullCPU, not recounted.114selectedcomponents111CPU/3GPU, not completion percentage.')
    save(session/'boot-slice-validation.json',validation)
    for p in [session/'gpu-geometry-overlay/C-generation.json',session/'gpu-geometry-submit-fullCPU-generation.json']:
        v=read(p);v.update(status='accepted_standalone_GPU_and_live_CPU_GPU4D80_linkage',whole_game_complete=False,evidence=['verification/biwn-gpu-geometry-checks.json','verification/biwn-disc-world-gpu-geometry-checks.json']);save(p,v)
    scope='The reconstructed GPU routine at 0x4D80 and its full CPU wrapper at 0xE0A6 now execute 1,008 times in 16 live disc-scene cases. The standalone proof passes 128 cases, all 434 GPU instructions and 13 guards, comparing both register banks, flags, matrix/divider state, GPU scratch RAM, complete main RAM, execution order and external bus shapes/stores. Initial GPU RAM is supplied before execution; untouched random reset bytes are preserved, not predicted. The CPU wrapper covers all 10 instructions. The integrated test retains 720 world updates, 2,048 actor iterations, 6,144 full CPU handoffs, 160 sprite decodes and 32 disc payloads totaling 3,080,416 bytes. GPU 4D80 leaves the record counter at 0 or 55; the record builder adds 4, giving absolute final counters of 4 or 59. Its 1,008 calls and 3,024 copies are real. GPU 4320 movement is separate: 3,488 whole-scene submissions run through world/actors; the nested record-builder branch is linked but unexercised, with zero calls. Six rendering scripts remain configured. Four run 1,008 times each: overlay 181F8, later submissions E19E/E202 to GPU programs 52E0/57A0, and display-list 185B2. E0F2/E148 remain unreached. Complete drawing, viewport/scanout, audio, uninterrupted boot, full game and physical timing remain unfinished; 15 other contexts are blocked. The CPU bus now masks physical addresses to 24 bits, covering 870 flagged accesses while retaining full 32-bit pointers. The prior 16-case pipeline also passes. BIOS/completion adapters, assisted startup, supplied clock/pad/inventory inputs and synchronous GPU completion remain fixtures. Full GPU context continuity between kernels and the core read-only remainder are not proved. Main-scene resource synchronization remains unexercised. The game is not playable. There are 114 selected components: 111 CPU and 3 GPU; this is not a completion percentage.'
    examples=read(ROOT/'verification/world-actor-checked-examples.json');examples.update(checked_world_actor_scope=scope,checked_render_queue_answer='GPU4D80geometry and E0A6wrapper nowactual1008livecalls; standalone128cases/all434GPUinstructions/fullGPUstate passed. GPUcounter0/55 plus4builderrecords gives final4/59. Sixrender scripts remain/fourreached181F8,E19E,E202,185B2each1008;E0F2/E148unreached. Fullviewport/gameunfinished. GPU4320movement3488whole-scene calls is separate; builderE220providerlinkedbutunreached0.',checked_dispatcher_answer='World/input/loading/renderqueue/scene/recordbuilder/GPU4D80 runtogether with6144fullCPUhandoffs;15contextsblocked. Remainingdrawkernels52E0/57A0,display-list/overlay,main-scene sync/fullgameunfinished.',checked_resource_answer='Resource/heap/loader/CD32disc payloads3080416bytes stillverified with actualGPU4D80renderer. BIOS/completion adapters andmain-scene synchronization/fullgame remain incomplete.');save(ROOT/'verification/world-actor-checked-examples.json',examples)
    checkpoint=dict(recorded_at=now,status='code_passed_local_scope_review_pending',published_components=114,new_GPU_components=1,GPU_cases=128,GPU_instruction_coverage=[434,434],host_guards=13,disc_cases=16,live_GPU4D80_calls=1008,live_CPU_E0A6_calls=1008,CPU_wrapper_instruction_coverage=[10,10],CPU_bus_high_byte_aliases=870,GPU_counter_values=[0,55],record_builder_additions=[4],final_record_counter_values=[4,59],whole_scene_GPU4320_calls=3488,builder_GPU4320_branch_calls=0,configured_render_scripts=6,reached_render_scripts=4,full_viewport_proved=False,full_GPU_context_cross_kernel_proved=False,full_goal_status='active incomplete',next_work='Reconstruct GPU52E0 andGPU57A0 reached draw kernels and fullCPU E19E/E202wrappers; fullCPU185B2display-list/181F8overlay and dependencies. Continue remaining tasks/scenes/audio/uninterruptedboot, resource game waits, fullgame/hardware and easy local/ad workflows.',evidence=['verification/biwn-gpu-geometry-checks.json','verification/biwn-disc-world-gpu-geometry-checks.json','verification/render-geometry-device-build.json'])
    save(ROOT/'verification/GPU-geometry-checkpoint.json',checkpoint)
    for name in ['config.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
        p=ROOT/name;v=read(p);v.update(GPU_geometry_checkpoint=checkpoint,disc_world_actor_progress=scope)
        if name=='config.json':v['chat_frontend']['game']['status']=scope
        if name=='corpus/game/project-intake.json':v['latest_checked_status']=scope
        if name=='verification/current-runtime-state.json':v.update(recorded_at=now,decomp_progress=scope,emulator_jobs='Terminal:128GPUcases and16liveGPUgeometrycases passed; previous16case configuration regression passed.')
        if name=='verification/setup-status.json':v['game_work']=scope
        if name=='verification/requirements-audit.json':
            v.update(recorded_at_utc=now,this_goal_turn_classification='Progress:434instructionGPU4D80/C and fullCPUsubmission execute in live scene. Proper24bitCPUbus corrected; remainingdraw/fullgame unfinished.',next_safe_work=checkpoint['next_work'])
            for item in v['requirements']:
                if 'decompilation test'in item['requirement']:item.update(state=scope,evidence=list(dict.fromkeys(item['evidence']+checkpoint['evidence'])))
        save(p,v)
    note='GPU4D80GEOMETRY — '+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex authored fixedGPUC/CPUwrapper/bridge/tests. OriginalGPU/nativeCPU validate selectedeffects. FirstGPUmathalreadymatchedregisters/flags/mainRAM/bus; untouchedrandomGPUresetRAM exposed missinginitial-state contract, correctedbycapturingpreexecutionRAM. Firstliveactorfailure atflagged8015CCD8 exposedCPUbusadaptermissing24bitmask; fixedadapter,sourcegameintegerbehaviorunchanged. Previous16casepipeline passed; strengthenedrecordcounterbefore/afterlogging and repeated16casespassed. No subagents/local-model-authoredcode/newtraining/defaultpromotion.\n\nNEXT\n'+checkpoint['next_work']+'\nFullgoalactiveandincomplete.\n';(ROOT/'CURRENT DECOMPILATION.txt').write_text(note)
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write('\n'+note)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LATEST GAME RESULT\n');b=text.index('LOCAL INFERENCE RESULT\n',a);p.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True,stdout=subprocess.DEVNULL)
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
