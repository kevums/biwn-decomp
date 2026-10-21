"""Publish checked resource bodies and disc-backed startup; keep old checkpoints."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==79
 back=ROOT/'verification/resources-checkpoint-backup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');back.mkdir(parents=True)
 for n in ['chat_tools.py','scripts/summarize_biwn_checks.py','config.json','CURRENT DECOMPILATION.txt','START HERE.txt','POST REVIEW.txt','presets/Game Assistant.system.txt','presets/Game Assistant.preset.json','corpus/game/project-intake.json']+['verification/'+n for n in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']]:
  target=back/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,target)
 for n in ['boot-slice-validation.json','emulator-runtime/summary.json']:
  target=back/'session'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(session/n,target)
 save(ROOT/'verification/resources-checkpoint-backup.json',{'recorded_at':now,'directory':str(back)})
 resource=read(ROOT/'verification/biwn-resources-checks.json');native=read(ROOT/'verification/biwn-resources-native-checks.json');linked=read(ROOT/'verification/biwn-render-resources-runtime-checks.json')
 assert resource['CPU_cases']==1920 and resource['CPU_instruction_coverage']==[201,201]and resource['host_guards']==33
 assert native['cases']==66 and native['active_models_full_payload_checked']==50 and native['disc_read_requests']==54 and native['C_blitter_commands']==112
 assert linked['cases']==144 and linked['real_allocations_total']==288 and linked['real_output_allocations']==144 and linked['disc_read_requests']==288 and len(linked['startup_nested_scripted_targets'])==4
 linked.update(startup_top_level_bodies_reconstructed=True,startup_nested_dependencies_fully_reconstructed=False,startup_MMIO_video_words_compared=4,sprite_queue_reset_by_original_EA20=True,animation_producers_executed=False,resource_memory_bodies_scripted=0)
 linked['matched']=['Original CPU and C execute render startup, all four resource bodies reached by the acquire/texture path, real allocation/copy/CD-position helpers, RNG and task creation, followed by real scheduled render/idle continuation. All 98 render caller and 210 startup-service instructions, full startup CPU/SR/PC/SP, visible RAM, four video words, seven blitter registers, disc windows/hashes and 38 public context-header bytes including saved CCR match. Resource release is checked separately, not reached by this startup path.', 'Across 144 cases: 144 model allocations plus 144 output allocations, 288 actual disc windows/completion ticks, full model0 payload96350B and full RTXT122880B hashes checked per case. Four supplied plus17created contexts form21;18thenblocked, only3bodies execute432actual steady-loop handoffs. Loading yields are explicit completion/RTS adapters, not scheduler switches.', 'Four nested startup scene services and six render services remain scripted. EA20 clears the animation queue; no producers or sprite decodes run here. FinalA0/A1, private stacks and ten formatter scratch bytes excluded. Frozen code/TOC/heap/freepool and image-specific674byte stream phase remain fixtures; full boot/world/render/assets/scenes/3Ddraw/scanout/audio/game/hardware unfinished.']
 # No release call occurs during startup: avoid counting it as a reached body.
 linked['matched'][0]=linked['matched'][0].replace('all four resource bodies reached by the acquire/texture path','resource acquire, loader and texture bodies')
 save(ROOT/'verification/biwn-render-resources-runtime-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
 common=['check_biwn_resources.py','check_biwn_resources_native.py','check_biwn_memory.py','check_biwn_memory_native.py','check_biwn_render_display_runtime.py','check_biwn_startup_services.py','check_biwn_rng.py','emulated_pad_input.py','biwn_disc_backend.py','inspect_biwn_disc_resources.py','check_biwn_boundary_handlers.py','check_biwn_world_update.py','check_biwn_render_scene.py','check_biwn_overlay.py','check_biwn_scheduler.py']
 for proof,checker in [(resource,'check_biwn_resources.py'),(native,'check_biwn_resources_native.py'),(linked,'check_biwn_render_resources_runtime.py')]:
  out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass';snap=out/'harness-snapshot';snap.mkdir(exist_ok=True);manifest={}
  sources=[ROOT/'scripts'/n for n in set(common+[checker])]+[ROOT/'animation_renderer.py',ROOT/'inventory_renderer.py',ROOT/'binary_tools.py']+[ROOT/'projects/black-ice-white-noise/restoration'/n for n in proof['source_sha256']]
  for source in sources:
   assert source.exists(),source
   shutil.copy2(source,snap/source.name);manifest[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
  save(snap/'manifest.json',manifest)
 shutil.copy2(Path(native['directory'])/'libresources-native.dylib',ROOT/'tools/libbiwn-resources-native.dylib');shutil.copy2(Path(linked['directory'])/'librender-resources.dylib',ROOT/'tools/libbiwn-render-resources.dylib')
 validation.update(portable_C_component_count=83,processor_component_counts={'CPU':81,'GPU':2},latest_aggregate_update=now,resource_reconstruction=resource,resource_native_pipeline=native,render_resources_startup_pipeline=linked,component_count_scope='83 checked components:81CPU and2GPU. Four new resource acquire/release/loader/texture bodies; standalone and connected proofs, not a game completion percentage.');save(session/'boot-slice-validation.json',validation)
 rows=read(Path(linked['directory'])/'fixtures.json');example=rows[0]
 answers={'checked_null_handle_answer':'In loader1B044, A4=0 returns the current payload pointer in fullD0. It leaves47B80=1 and does not update completionA5. With A4=0x00110000, CMPA.W compares the full address register against sign-extended zero: BNE is taken and the copy branch runs. A zero low word does not make a nonzero pointer null.','checked_disc_answer':'All50active model payloads and122880RTXT texture bytes match verified disc bytes in66nativeCPU/C cases; three cache reuse/release/release/reload sequences pass. Stream phase674 is supported by an exact32768byte capturedCDbuffer match, not universalCD/BIOS timing.', 'checked_startup_resource_answer':'The current144case startup proof loads model0(96350bytes) andRTXT(122880bytes) from disc bytes, not a captured model handle. There are288allocations:144model and144output. LoadingDF60uses an explicit completion/RTS adapter; only the subsequent432render/idle handoffs execute the real scheduler. Four nested startup scene services andsixrender services remain scripted.', 'startup_example':{k:example[k]for k in ['model_handle','model_pointer','output_handle','output_data_pointer','model_payload_sha256','texture_payload_sha256']}}
 save(ROOT/'verification/resources-checked-examples.json',answers)
 p=ROOT/'scripts/summarize_biwn_checks.py';s=p.read_text();needle="    save(folder / 'emulator-runtime/summary.json', runtime)"
 block="""    resources_path=root/'verification/biwn-resources-checks.json'
    resources_native_path=root/'verification/biwn-resources-native-checks.json'
    resources_startup_path=root/'verification/biwn-render-resources-runtime-checks.json'
    if all(p.exists()for p in [resources_path,resources_native_path,resources_startup_path]):
        resource=json.loads(resources_path.read_text());native=json.loads(resources_native_path.read_text());linked=json.loads(resources_startup_path.read_text())
        if resource['CPU_cases']!=1920 or resource['CPU_instruction_coverage']!=[201,201]or native['cases']!=66 or linked['disc_read_requests']!=288:
            raise ValueError('Resource evidence incomplete')
        runtime['CPU_resources_reconstruction']={**resource,'report':str(resources_path),**json.loads((root/'verification/resources-checked-examples.json').read_text())}
        runtime['resources_native_pipeline']={**native,'report':str(resources_native_path)}
        runtime['render_resources_startup_pipeline']={**linked,'report':str(resources_startup_path)}
"""
 assert needle in s;s=s.replace(needle,block+needle);p.write_text(s)
 p=ROOT/'chat_tools.py';s=p.read_text().replace("'render_startup', 'memory',", "'render_startup', 'resources', 'memory',").replace("'render_startup','memory',", "'render_startup','resources','memory',")
 s=s.replace('Get checked Black Ice White Noise evidence. Use memory','Get checked Black Ice White Noise evidence. Use resources for acquire1AF04, release1B002, loader1B044, texture1AA40, actual disc payloads, full-pointer/null-handle semantics and completion-versus-scheduler scope. Use memory')
 s=s.replace("observed.get('render_memory_startup_pipeline',", "observed.get('render_resources_startup_pipeline',observed.get('render_memory_startup_pipeline',")
 # Three expressions gain an opening parenthesis, close each at its statement end.
 lines=s.splitlines()
 for i,line in enumerate(lines):
  if "observed.get('render_resources_startup_pipeline'" in line:lines[i]=line+')'
 s='\n'.join(lines)+'\n'
 s=s.replace("'real_output_allocations']if k in startup", "'real_output_allocations','real_model_allocations','real_allocations_total','disc_read_requests','IO_completion_yield_adapters','BIOS_IO_device_adapters','startup_yield_scope']if k in startup")
 needle="        return compact\n    if topic == 'memory':"
 insert="""        if 'render_resources_startup_pipeline' in observed:
            compact['scope']='Current144case startup/render proof loads complete model0 andRTXT from disc through real resource/memory bodies,288allocations(144model/144output). Four nested startup scene andsixrender services remain scripted; BIOS transfers andloadingDF60completion/RTS are explicit adapters. Loading task-context switches are not tested. Four supplied plus17created contexts form21;18blocked and3bodies execute432real steady-loop handoffs. Zero sprite decodes after queue reset. Full startupCPU/public38byteheaders/discbytes/blitter compare; private stacks/finalA0/A1/formatterbytes excluded. Full boot/world/render/lifecycles/17callers/3Ddraw/scanout/scenes/audio/game/hardware remain unfinished.'
        return compact
    if topic == 'resources':
        observed=common.get('emulator_runtime',{});proof=observed['CPU_resources_reconstruction'];native=observed['resources_native_pipeline']
        compact={key:common[key]for key in ['project','source','whole_game_decompilation','physical_hardware_validation','working_game_reconstruction','isolated_cpu_and_portable_C_checks']}
        compact.update({k:proof[k]for k in ['checked_null_handle_answer','checked_disc_answer','checked_startup_resource_answer','startup_example']})
        compact['CPU_resources']={k:proof[k]for k in ['report','CPU_cases','CPU_instruction_coverage','host_guards','new_components','original_bytes','intervals','matched','limits']}
        compact['native_resources']={k:native[k]for k in ['report','cases','active_models_full_payload_checked','inactive_ids_return_zero','texture_payload_bytes','reuse_release_reload_sequences','disc_read_requests','disc_completion_ticks','C_blitter_commands','scripted_game_resource_or_memory_bodies','BIOS_IO_device_adapters','yield_completion_boundary','matched','limits']}
        compact=latest_pipeline(compact,observed);compact.pop('current_connected_pipeline',None)
        return record('project_evidence',{'topic':topic},compact)
    if topic == 'memory':"""
 assert needle in s;s=s.replace(needle,insert)
 s=s.replace('Reconstruct nested startup resource/allocator/scene services andGPU/3Ddraw services;', 'Reconstruct loading task continuations and four remaining nested startup scene services plusGPU/3Ddraw services;')
 p.write_text(s)
 # Existing native Chat keeps its current prompt; the tool description routes resources immediately.
 p=ROOT/'presets/Game Assistant.system.txt';s=p.read_text().replace('- memory:', '- resources: acquire/release/loader/texture, actual disc payloads, full-pointer/null-handle semantics, loading completion adapter versus real scheduler.\n- memory:',1);p.write_text(s)
 p=ROOT/'presets/Game Assistant.preset.json';d=read(p)
 for field in d['operation']['fields']:
  if field['key']=='llm.prediction.systemPrompt':field['value']=s.strip()
 save(p,d);shutil.copy2(p,Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json')
 for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True)
 print(json.dumps({'components':83,'startup':answers['startup_example'],'prompt_characters':len(s.strip())}))
if __name__=='__main__':main()
