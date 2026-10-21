"""Publish six scene bodies and their actual-disc startup integration."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==83
 unit=read(ROOT/'verification/biwn-scene-loading-checks.json');linked=read(ROOT/'verification/biwn-render-scenes-runtime-checks.json');assert unit['CPU_cases']==1536 and unit['CPU_instruction_coverage']==[479,479]and unit['host_guards']==54
 assert linked['cases']==144 and linked['disc_read_requests']==1008 and linked['scene_rows_loaded']==720 and linked['outdoor_segments_parsed']==3600 and linked['real_allocations_total']==288
 back=ROOT/'verification/scene-checkpoint-backup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');back.mkdir(parents=True)
 for n in ['chat_tools.py','scripts/summarize_biwn_checks.py','config.json','CURRENT DECOMPILATION.txt','START HERE.txt','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
  dest=back/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,dest)
 for n in ['boot-slice-validation.json','emulator-runtime/summary.json']:
  dest=back/'session'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(session/n,dest)
 save(ROOT/'verification/scene-checkpoint-backup.json',{'directory':str(back),'recorded_at':now})
 unit['helper_incoming_D0_compared']=True;unit['matched'][0]+=' Incoming D0 at every logical helper call is also compared; other caller-saved registers remain excluded.'
 save(ROOT/'verification/biwn-scene-loading-checks.json',unit);save(Path(unit['directory'])/'report.json',unit)
 rows=read(Path(linked['directory'])/'fixtures.json');configured=linked['startup_nested_scripted_targets'];reached=sorted({hex(call[1])for row in rows for call in row['startup_calls']if hex(call[1])in configured})
 linked.update(startup_top_level_bodies_reconstructed=True,startup_nested_dependencies_fully_reconstructed=False,startup_MMIO_video_words_compared=4,sprite_queue_reset_by_original_EA20=True,animation_producers_executed=False,resource_memory_bodies_scripted=0,scene_bodies_reached=['0x20f78','0x20b2a','0x20c16','0x20aa0'],scene_bodies_standalone_only=['0x20cf8','0x20d7c'],startup_nested_scripted_targets_reached=reached,scene_heap_allocations=0,model_texture_disc_requests=288,scene_disc_requests=720)
 assert len(configured)==8 and len(reached)==7
 linked['matched']=['Original CPU and C execute render startup, resource/memory bodies, outdoor scene loading/parsing/texture-fixup/actor-record callers, RNG and task creation, then the real scheduled render/idle continuation. All98render caller and210earlier startup-service instructions, full startupCPU/SR/PC/SP, visibleRAM, public38byteheaders includingCCR, disc windows and selectedvideo/blitter registers match.', 'Across144cases, five scene rows and25segments percase produce720rows/3600segments and720scene reads. Model0/RTXT add288reads for1008total completion adapters. Model/output allocation remains144+144=288; scene loading borrows the shared buffer and performs no per-row heap allocation. Segment copies use actual memory kernels. Texture acquire/lookup, actor creation and position helpers remain scripts.', 'Four supplied plus17createdcontexts form21;18blocked and3bodies execute432real steady handoffs. LoadingDF60/BIOS transfers remain explicit completion/device adapters; no real loading task switches or fullboot are claimed. Both indoor and outdoor scene modes pass the separate1536case CPUproof; only outdoor mode is integrated into this startup fixture.']
 linked['limits']=['Eight nested startup targets are configured as scripts; seven are reached across this outdoor fixture (indoor10520 is not reached). Three previously remaining startup bodies1B786/18888/11E6C and five newly exposed deeper helpers1AC68/1AC3C/13AE0/102C4/10520 remain unported here. Six render services and15historical world services remain scripted. Script counts rose because the actual scene caller now exposes deeper work, not because scene completion is claimed.', 'Texture IDs/reference residency, actual actor/context creation and player scene positioning are not implemented by these helper scripts. Resulting fixture geometry is a partial caller pipeline, not a playable scene. The image-specific674byte stream phase, frozen code/TOC/heap/freepool and supplied contexts remain test boundaries.', 'Full startupCPU and38publiccontextbytes compare; private stacks, ten formatter bytes and finalA0/A1 remain excluded. EA20 clears the queue; producers remain blocked andno sprites decode here. Fullboot/live world-render-assets/17taskcallers/3Ddrawing/scanout/mainloop/scenes/audio/game/hardware unfinished.']
 save(ROOT/'verification/biwn-render-scenes-runtime-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
 for proof,checker in [(unit,'check_biwn_scene_loading.py'),(linked,'check_biwn_render_scenes_runtime.py')]:
  out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass';snap=out/'harness-snapshot';snap.mkdir(exist_ok=True);manifest={}
  scripts=['check_biwn_scene_loading.py','check_biwn_startup_services.py','check_biwn_boundary_handlers.py','check_biwn_world_update.py','check_biwn_render_display_runtime.py','check_biwn_render_scene.py','check_biwn_scheduler.py','check_biwn_overlay.py','check_biwn_resources.py','check_biwn_resources_native.py','check_biwn_memory.py','check_biwn_memory_native.py','check_biwn_rng.py','emulated_pad_input.py','biwn_disc_backend.py',checker]
  files=[ROOT/'scripts'/n for n in set(scripts)]+[ROOT/n for n in ['animation_renderer.py','inventory_renderer.py','binary_tools.py']]+[ROOT/'projects/black-ice-white-noise/restoration'/n for n in proof['source_sha256']]
  for src in files:shutil.copy2(src,snap/src.name);manifest[src.name]=hashlib.sha256(src.read_bytes()).hexdigest()
  save(snap/'manifest.json',manifest)
 shutil.copy2(Path(unit['directory'])/'libscene-loading.dylib',ROOT/'tools/libbiwn-scene-loading.dylib');shutil.copy2(Path(linked['directory'])/'librender-scenes.dylib',ROOT/'tools/libbiwn-render-scenes.dylib')
 validation.update(portable_C_component_count=89,processor_component_counts={'CPU':87,'GPU':2},latest_aggregate_update=now,scene_loading_reconstruction=unit,render_scene_loading_startup_pipeline=linked,component_count_scope='89 checked components:87CPU and2GPU. Six new scene caller/parsing bodies, independently checked andfour connected to outdoor startup. Counts are not full-game completion percentages.');save(session/'boot-slice-validation.json',validation)
 answers={'checked_scene_answer':'Six scene bodies pass1536CPU cases, all479instructions and54host guards, including incomingD0 at every helper boundary. The144case startup integration loads five outdoor rows andparses25segments percase:720rows/3600segments. Only four ofthe six bodies run inthis outdoor startup; indoor20CF8/20D7C are checked separately.', 'checked_allocation_answer':'Scene loading uses handle_pointer0 andreturns a borrowed payload pointer into the shared disc buffer. It copies to existing segment destinations, then clears47B80 before the next row. It makes no per-row heap allocation. The startup test still has144model plus144output allocations,288total. There are1008disc reads/completion adapters:720scene and288model/texture.', 'checked_remaining_answer':'Eight nested startup helper targets are configured, seven reached inoutdoor mode. 1B786/18888/11E6C plus texture acquire1AC68/lookup1AC3C, actor creation13AE0 andposition102C4/10520 remain scripts. LoadingDF60 completion/RTS andBIOS transfers are adapters. Only the later432render/idle handoffs execute real scheduler switches. Six render services,world/render/liveassets/remainingtasks/3Ddraw/scanout/mainloop/audio/fullgame/hardware remain unfinished.'}
 save(ROOT/'verification/scene-checked-examples.json',answers)
 p=ROOT/'scripts/summarize_biwn_checks.py';s=p.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)";block="""    scene_path=root/'verification/biwn-scene-loading-checks.json'
    scene_startup_path=root/'verification/biwn-render-scenes-runtime-checks.json'
    if scene_path.exists() and scene_startup_path.exists():
        scene=json.loads(scene_path.read_text());linked=json.loads(scene_startup_path.read_text())
        if scene['CPU_cases']!=1536 or scene['CPU_instruction_coverage']!=[479,479]or linked['disc_read_requests']!=1008:
            raise ValueError('Scene loading evidence incomplete')
        runtime['CPU_scene_loading_reconstruction']={**scene,'report':str(scene_path),**json.loads((root/'verification/scene-checked-examples.json').read_text())}
        runtime['render_scene_loading_startup_pipeline']={**linked,'report':str(scene_startup_path)}
""";assert needle in s;s=s.replace(needle,block+needle);p.write_text(s)
 p=ROOT/'chat_tools.py';s=p.read_text().replace("'render_startup', 'resources',", "'render_startup', 'scene_loading', 'resources',").replace("'render_startup','resources',", "'render_startup','scene_loading','resources',")
 s=s.replace('Get checked Black Ice White Noise evidence. Use resources', 'Get checked Black Ice White Noise evidence. Use scene_loading for20F78 two modes, scene segment parsing/relocation, texture fixup andactor-record callers, borrowed buffer/no scene heap allocation andnewly exposed deeper helpers. Use resources')
 s=s.replace("observed.get('render_resources_startup_pipeline',", "observed.get('render_scene_loading_startup_pipeline',observed.get('render_resources_startup_pipeline',")
 lines=s.splitlines()
 for i,line in enumerate(lines):
  if "observed.get('render_scene_loading_startup_pipeline'" in line:lines[i]=line+')'
 s='\n'.join(lines)+'\n';s=s.replace("'startup_yield_scope']if k in startup", "'startup_yield_scope','scene_rows_loaded','outdoor_segments_parsed','actor_creation_boundary_calls','texture_acquire_boundary_calls','texture_lookup_boundary_calls','scene_heap_allocations','startup_nested_scripted_targets_reached']if k in startup")
 needle="        return compact\n    if topic == 'resources':";block="""        if 'render_scene_loading_startup_pipeline' in observed:
            compact['scope']='Current144case startup parses25outdoor segments from5disc rows percase,720rows/3600segments. Scene loading uses a borrowed buffer, no per-row heap allocations;144model/144output allocations remain. Total1008disc completion adapters. Texture/actor/position helpers remain scripts:8configured startuptargets,7reached outdoors, plus6render services. Real loading task switches remain unverified; only432later scheduler handoffs run. Full startupCPU/publicheaders/RAM/disc/blitter compare. Partial scene caller pipeline; fullboot/world/render/liveassets/17taskcallers/3Ddraw/scanout/mainloop/scenes/audio/game/hardware unfinished.'
        return compact
    if topic == 'scene_loading':
        observed=common.get('emulator_runtime',{});proof=observed['CPU_scene_loading_reconstruction'];linked=observed['render_scene_loading_startup_pipeline']
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        compact.update({k:proof[k]for k in ['checked_scene_answer','checked_allocation_answer','checked_remaining_answer']})
        compact['CPU_scene_loading']={k:proof[k]for k in ['report','CPU_cases','CPU_instruction_coverage','host_guards','new_components','helper_incoming_D0_compared','original_bytes','intervals','matched','limits']}
        compact['scene_startup']={k:linked[k]for k in ['report','cases','scene_rows_loaded','outdoor_segments_parsed','disc_read_requests','real_model_allocations','real_output_allocations','scene_heap_allocations','actor_creation_boundary_calls','texture_acquire_boundary_calls','texture_lookup_boundary_calls','startup_nested_scripted_targets','startup_nested_scripted_targets_reached','startup_yield_scope']}
        compact=latest_pipeline(compact,observed);compact.pop('current_connected_pipeline',None)
        return record('project_evidence',{'topic':topic},compact)
    if topic == 'resources':""";assert needle in s;s=s.replace(needle,block)
 # Older resource answers retain their historical144case scope; label it explicitly.
 s=s.replace("compact.update({k:proof[k]for k in ['checked_null_handle_answer','checked_disc_answer','checked_startup_resource_answer','startup_example']})", "compact.update({k:proof[k]for k in ['checked_null_handle_answer','checked_disc_answer','checked_startup_resource_answer','startup_example']});compact['resource_checkpoint_scope']='These resource-only startup examples are historical. Current scene-loading startup reads more windows; use current render_task_startup_progress orscene_loading forlatestcounts.'")
 p.write_text(s)
 p=ROOT/'presets/Game Assistant.system.txt';s=p.read_text().replace('- resources:', '- scene_loading: two scene modes, segment relocation, texture fixups and actor-record callers, borrowed buffer/no per-row allocations, deeper remaining helpers.\n- resources:',1);p.write_text(s)
 p=ROOT/'presets/Game Assistant.preset.json';d=read(p)
 for f in d['operation']['fields']:
  if f['key']=='llm.prediction.systemPrompt':f['value']=s.strip()
 save(p,d);shutil.copy2(p,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for n in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/n)],check=True)
 print(json.dumps({'components':89,'scene_rows':720,'segments':3600,'configured_startup_scripts':len(configured),'reached_startup_scripts':len(reached),'prompt_characters':len(s.strip())}))
if __name__=='__main__':main()
