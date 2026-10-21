"""Publish verified memory management, preserving earlier partial-copy reports."""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==77
 back=ROOT/'verification/memory-checkpoint-backup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');back.mkdir(parents=True)
 for n in ['chat_tools.py','scripts/summarize_biwn_checks.py','config.json','CURRENT DECOMPILATION.txt','START HERE.txt','POST REVIEW.txt','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
  dest=back/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,dest)
 for n in ['boot-slice-validation.json','emulator-runtime/summary.json']:
  dest=back/'session'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(session/n,dest)
 save(ROOT/'verification/memory-checkpoint-backup.json',{'directory':str(back),'recorded_at':now})
 memory=read(ROOT/'verification/biwn-memory-checks.json');native=read(ROOT/'verification/biwn-memory-native-checks.json');linked=read(ROOT/'verification/biwn-render-memory-runtime-checks.json');assert memory['CPU_cases']==2816 and memory['CPU_instruction_coverage']==[257,257]and native['cases']==656 and linked['real_output_allocations']==144
 native['CPU_instruction_coverage']=[257,257];save(ROOT/'verification/biwn-memory-native-checks.json',native);save(Path(native['directory'])/'report.json',native)
 linked.update(startup_top_level_bodies_reconstructed=True,startup_nested_dependencies_fully_reconstructed=False,startup_MMIO_video_words_compared=4,sprite_queue_reset_by_original_EA20=True,animation_producers_executed=False)
 linked['matched']=['Original native CPU and C execute complete render startup plus real output allocation152A2, RNG, task creation and scheduled render/idle continuation. All 98 render-caller and 210 startup-service instructions are covered; full startup CPU/SR/PC/SP, visible RAM, four emulated video words and all 38 public context bytes including saved CCR match.', 'Four supplied plus17created contexts form21, with18blocked and3bodies executing. Real allocator supplies144output buffers; source model loading1AF04 still returns a captured model handle through a declared script. EA20 clears the seeded queue, so no animation producers or sprite decodes execute in this integration.', 'Final A0/A1, private stacks and ten formatter scratch bytes remain excluded. Six nested startup resource/scene services and six render services remain scripted; whole world/render/asset lifecycles, remaining callers, 3D drawing/scanout/main loop/scenes/audio/game/hardware are unfinished.']
 save(ROOT/'verification/biwn-render-memory-runtime-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
 for proof,checker in [(memory,'check_biwn_memory.py'),(native,'check_biwn_memory_native.py'),(linked,'check_biwn_render_memory_runtime.py')]:
  out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass';snap=out/'harness-snapshot';snap.mkdir(exist_ok=True);manifest={}
  sources=[ROOT/'scripts'/checker,ROOT/'scripts/check_biwn_memory.py',ROOT/'scripts/check_biwn_render_display_runtime.py',ROOT/'scripts/check_biwn_startup_services.py',ROOT/'scripts/check_biwn_rng.py',ROOT/'scripts/emulated_pad_input.py',ROOT/'animation_renderer.py']+[ROOT/'projects/black-ice-white-noise/restoration'/n for n in proof['source_sha256']]
  for src in sources:shutil.copy2(src,snap/src.name);manifest[src.name]=hashlib.sha256(src.read_bytes()).hexdigest()
  save(snap/'manifest.json',manifest)
 shutil.copy2(Path(native['directory'])/'libmemory.dylib',ROOT/'tools/libbiwn-memory.dylib');shutil.copy2(Path(linked['directory'])/'librender-memory.dylib',ROOT/'tools/libbiwn-render-memory.dylib')
 validation.update(portable_C_component_count=79,processor_component_counts={'CPU':77,'GPU':2},latest_aggregate_update=now,memory_reconstruction=memory,memory_native_pipeline=native,render_memory_startup_pipeline=linked,component_count_scope='79 checked components:77 CPU and2 GPU. Two new allocator/compactor bodies; two existing partial-copy components upgraded, not counted again. Standalone and connected proofs, not a game completion percentage.');save(session/'boot-slice-validation.json',validation)
 rows=read(Path(linked['directory'])/'fixtures.json');example=rows[0];examples=read(ROOT/'verification/memory-checked-examples.json');examples['startup_output_example']={'handle':hex(example['output_handle']),'data_pointer':hex(example['output_data_pointer']),'source_report':str(ROOT/'verification/biwn-render-memory-runtime-checks.json')};save(ROOT/'verification/memory-checked-examples.json',examples)
 p=ROOT/'scripts/summarize_biwn_checks.py';s=p.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)";block="""    memory_path=root/'verification/biwn-memory-checks.json'
    memory_native_path=root/'verification/biwn-memory-native-checks.json'
    memory_startup_path=root/'verification/biwn-render-memory-runtime-checks.json'
    if memory_path.exists() and memory_native_path.exists() and memory_startup_path.exists():
        memory=json.loads(memory_path.read_text());native=json.loads(memory_native_path.read_text());linked=json.loads(memory_startup_path.read_text())
        if memory['CPU_cases']!=2816 or memory['CPU_instruction_coverage']!=[257,257]or native['cases']!=656 or linked['real_output_allocations']!=144:
            raise ValueError('Memory management evidence incomplete')
        runtime['CPU_memory_reconstruction']={**memory,'report':str(memory_path),**json.loads((root/'verification/memory-checked-examples.json').read_text())}
        runtime['memory_native_pipeline']={**native,'report':str(memory_native_path)}
        runtime['render_memory_startup_pipeline']={**linked,'report':str(memory_startup_path)}
""";assert needle in s;s=s.replace(needle,block+needle);p.write_text(s)
 p=ROOT/'chat_tools.py';s=p.read_text().replace("'render_startup', 'rng',","'render_startup', 'memory', 'rng',").replace("'render_startup','rng',","'render_startup','memory','rng',")
 s=s.replace('Get checked Black Ice White Noise evidence. Use rng','Get checked Black Ice White Noise evidence. Use memory for allocator152A2, compactor15200, E3E0/E3EE copy, exact wrapped sizes, handle exhaustion and original/native blitter scope. Use rng')
 s=s.replace("observed.get('render_services_startup_pipeline',observed.get('render_rng_startup_pipeline',observed['render_task_startup_pipeline']))","observed.get('render_memory_startup_pipeline',observed.get('render_services_startup_pipeline',observed.get('render_rng_startup_pipeline',observed['render_task_startup_pipeline'])))")
 s=s.replace("'animation_producers_executed']if k in startup","'animation_producers_executed','real_output_allocations']if k in startup")
 needle="        return compact\n    if topic == 'rng':";insert="""        if 'render_memory_startup_pipeline' in observed:
            compact['scope']='Current startup/render proof executes real output allocation152A2, all startup bodies, RNG andtask creation in144native/C cases; six nested startup andsixrender services remain scripted. Four supplied plus17created contexts form21,18blocked and3bodies execute. Model loading remains a captured-handle script; live resources/world/render integration,17othercallers,3Ddrawing/scanout/main loop/scenes/audio/fullgame/hardware remain unfinished. EA20 clears the animation queue; this test has zero sprite decodes. Full startup CPU/public38byteheaders compare; finalA0/A1,private stacks/tenformatterbytes excluded.'
        return compact
    if topic == 'memory':
        observed=common.get('emulator_runtime',{});proof=observed['CPU_memory_reconstruction'];native=observed['memory_native_pipeline']
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        compact['checked_arithmetic_answer']=proof['checked_arithmetic_answer']
        compact['CPU_memory']={k:proof[k]for k in ['report','CPU_cases','CPU_instruction_coverage','host_guards','raw_large_count_prefix_cases','new_components','upgraded_existing_copy_components','source_entry_points','matched','limits','startup_output_example']}
        compact['native_memory']={k:native[k]for k in ['report','cases','CPU_instruction_coverage','C_blitter_commands','compaction_calls','copy_dependency_calls','nested_scripted_helpers','matched','limits']}
        compact=latest_pipeline(compact,observed);compact.pop('current_connected_pipeline',None)
        return record('project_evidence',{'topic':topic},compact)
    if topic == 'rng':""";assert needle in s;s=s.replace(needle,insert)
 s=s.replace("observed.get('render_services_startup_pipeline',observed.get('render_rng_startup_pipeline',observed.get('render_task_startup_pipeline',observed.get('scheduled_render_display_pipeline',observed.get('scheduled_render_overlay_pipeline',observed['scheduled_render_continuation_pipeline'])))))","observed.get('render_memory_startup_pipeline',observed.get('render_services_startup_pipeline',observed.get('render_rng_startup_pipeline',observed.get('render_task_startup_pipeline',observed.get('scheduled_render_display_pipeline',observed.get('scheduled_render_overlay_pipeline',observed['scheduled_render_continuation_pipeline']))))))")
 s=s.replace("compact['checked_scope']='All top-level startup bodies execute real source code, but seven nested startup dependencies and six render dependencies remain scripted. The full game is unfinished.'", "compact['checked_scope']=f\"All top-level startup bodies execute real source code, but {len(proof.get('startup_nested_scripted_targets',[]))} nested startup dependencies and six render dependencies remain scripted. The full game is unfinished.\"")
 p.write_text(s)
 p=ROOT/'presets/Game Assistant.system.txt';s=p.read_text().replace('- rng:','- memory: allocator152A2, compactor15200, full copyE3E0/E3EE, raw size arithmetic, handle exhaustion and live allocation linkage.\n- rng:',1);p.write_text(s)
 p=ROOT/'presets/Game Assistant.preset.json';d=read(p)
 for f in d['operation']['fields']:
  if f['key']=='llm.prediction.systemPrompt':f['value']=s.strip()
 save(p,d);shutil.copy2(p,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True)
 print(json.dumps({'components':79,'output_example':examples['startup_output_example'],'prompt_characters':len(s.strip())}))
if __name__=='__main__':main()
