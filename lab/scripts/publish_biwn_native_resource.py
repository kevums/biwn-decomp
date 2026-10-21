"""Freeze native26 resource-release CDI, preserving negative inherited control."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 previous_path=ROOT/'verification/native-free-publication-current.json';previous=json.loads(previous_path.read_text());paths={};objects={}
 names=['native-resource-disc-build','native-resource-disc-entry','native-resource-route','native-resource-route-analysis','native-resource-bundle-free','native-resource-bundle-initialize','native-resource-lifecycle','native-resource-bundle-copy','native-resource-bundle-heap','native-resource-bundle-controller','native-resource-bundle-rng','native-resource-bundle-tasks','native-resource-bundle-scheduler','native-resource-bundle-heap-blitter-witness','native-resource-release-bundle','native-resource-release-component-publication','local-native-resource-release','native-free-fixed-followup','native-free-prefix-isolation','native-free-live-return-analysis']
 for name in names:p=ROOT/'verification'/(name+'-current.json');paths[name]=p;objects[name]=json.loads(p.read_text())
 b=objects[names[0]];entry=objects[names[1]];route=objects[names[2]];analysis=objects[names[3]];free=objects[names[4]];init=objects[names[5]];life=objects[names[6]];release=objects[names[14]];component=objects[names[15]];author=objects[names[16]]
 assert b['native_rebuilt_entries']==26 and b['linked_component_bytes']==5986 and b['component_bytes']==6144 and b['fixed_input_equivalence']is None
 assert entry['entry_cases']==96 and entry['component_cases']==5151 and entry['build_proof_sha256']==sha(paths[names[0]])
 assert route['build_proof_sha256']==sha(paths[names[0]])and analysis['route_proof_sha256']==sha(paths[names[2]])and analysis['both_completed']and analysis['native25_repeat_full_rows_different']==0 and analysis['native25_repeat_PCM_equal']
 assert free['source_accepted']and free['native_cases']==free['trace_cases']==1411 and free['changing_read_native_cases']==4
 assert init['source_accepted']and init['native_cases']==init['trace_cases']==192
 assert life['source_accepted']and life['native_call_pairs']==240 and life['compiled_resource_release_C_calls']==16
 assert release['source_accepted']and release['native_cases']==release['trace_cases']==768 and release['free_C_entry_hits']==9024
 expected={'native-resource-bundle-copy':(3260,3260),'native-resource-bundle-heap':(3392,3392),'native-resource-bundle-controller':(1216,1024),'native-resource-bundle-tasks':(1280,1280),'native-resource-bundle-scheduler':(1664,896)}
 for name,(native,ordered)in expected.items():assert objects[name]['native_cases']==native and objects[name]['trace_cases']==ordered
 assert objects['native-resource-bundle-rng']['cpu_cases']==1682 and objects['native-resource-bundle-rng']['trace_cases']==298
 assert objects['native-resource-bundle-heap-blitter-witness']['payload_bytes_checked']==232
 gates=[objects[n]for n in names[4:13]]+[release]
 assert all(g['compiled_binary_sha256']==b['linked_component_sha256']for g in gates)
 for obj in [b,entry,route,analysis,*gates]:
  for field in ['source_sha256','execution_dependencies_sha256']:
   for p,d in obj.get(field,{}).items():assert sha(p)==d,p
 for obj in [previous,component,*[objects[n]for n in names[17:]]]:
  for rel,d in obj['dependencies_sha256'].items():assert sha(ROOT/rel)==d,rel
 assert sha(b['original_disc'])==b['original_disc_sha256']and sha(b['derived_disc'])==b['derived_disc_sha256']
 native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';assert sha(native/'resource-release-native.c')==author['source_sha256']==sha(author['source'])
 obs=route['results']['native26_repaired']['observation'];assert obs['native_C_resource_release_calls']==obs['resource_release_entries']==9 and obs['old_resource_release_body_steps']==0
 assert obs['native_C_free_calls']==19 and obs['old_free_body_steps']==obs['old_initialize_body_steps']==obs['old_copy_body_steps']==0
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  recipe=json.loads((ROOT/'verification'/name).read_text())
  for p,d in recipe['hashes'].items():assert sha(p)==d,p
  pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-resource-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshot_dir=out/'snapshots';snapshot_dir.mkdir();deps={};snapshots={};observed={}
 for obj in [previous,component,*[objects[n]for n in names[17:]]]:deps.update(obj['dependencies_sha256'])
 def pin(p,snapshot=False):
  p=Path(p).resolve();assert p.is_relative_to(ROOT);rel=str(p.relative_to(ROOT));digest=sha(p)
  if snapshot:
   dest=snapshot_dir/(hashlib.sha256(rel.encode()).hexdigest()[:12]+'-'+p.name)
   if not dest.exists():shutil.copy2(p,dest)
   assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;snapshots[rel]=dict(snapshot=str(dest.relative_to(ROOT)),sha256=digest)
  else:deps[rel]=digest
 for p in [previous_path,*paths.values(),Path(__file__),ROOT/'native_restoration_evidence.py',ROOT/'assistant_chat.py',ROOT/'scripts/reveal_biwn_native_disc.py',ROOT/'scripts/native_chat_team_context.py']:pin(p,True)
 for obj in [b,entry,route,analysis,*gates]:
  for field in ['source_sha256','execution_dependencies_sha256']:
   for p in obj.get(field,{}):pin(p,True)
 for p in native.iterdir():
  if p.is_file()and(p.suffix in ['.c','.h','.S','.ld']or p.name.startswith('Makefile')):observed[str(p.relative_to(ROOT))]=sha(p);pin(p,True)
 for p in [b['derived_disc'],b['component'],b['linked_component'],b['derived_stage'],b['fixed_runtime_binary']]:pin(p)
 for g in [free,init,release,objects['native-resource-bundle-copy'],objects['native-resource-bundle-heap']]:
  for p in Path(g['directory']).glob('*.json'):pin(p)
  pin(Path(g['directory'])/'disassembly.txt')
 pin(Path(life['directory'])/'results.json')
 for name in ['entry-cases.json','component-cases.json']:pin(Path(entry['directory'])/name)
 for lane in route['lanes']:
  for name in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le','original-emulator-final-frame.png','video-final.xrgb8888']:pin(Path(route['directory'])/lane/name)
 facts=dict(previous['facts']);free_authorship=facts['authorship'];cf=component['facts'];authorship=dict(roles=cf['attempts'],accepted_C_body_role='Fully guided Author',coordinator_supplied_full_algorithm_and_disassembly=True,coordinator_role=cf['coordinator_scope'],raw_guided_model_C_unchanged=True,manual_C_edits=0,independent_model_validation=False)
 resource={**cf,'new_disc_built':True,'game_integration_verified':True,'other_relinked_bundle_components_reverified':True,'game_scope':'Nine compiled-body entries in fresh adaptive native26route; no current26fixed-input or physical proof.','fresh_gameplay_observation':dict(public_entry_hits=9,compiled_C_body_hits=9,old_body_instructions=0),'component_proof':str(paths['native-resource-release-component-publication']),'proof':str(out/'publication.json')}
 heap={**facts['heap_management'],'allocator_C_function_calls':obs['native_C_allocate_calls'],'compactor_C_function_calls':obs['native_C_compact_calls']};task={**facts['task_creation'],'naturally_observed_native_ABI_entry_calls':obs['native_task_entries']};scheduler={**facts['scheduler'],'C_select_function_calls':obs['native_C_select_calls'],'assembly_dispatch_entry_calls':obs['native_dispatch_calls'],'assembly_remove_entry_calls':obs['native_remove_calls'],'native_RTE_instruction_hits':obs['native_scheduler_RTEs'],'yield_stub_hits':obs['scheduler_yield_entries'],'remove_trap_hits':obs['scheduler_remove_traps']}
 native_copy={**facts['native_copy'],'fresh_gameplay_observation':dict(source_first_entry_hits=obs['copy_entries'][0],destination_first_entry_hits=obs['copy_entries'][1],compiled_C_body_entry_hits=obs['native_C_copy_entry_observations'],old_copy_body_instructions=0)}
 facts.update(status_label='experimental_native26_resource_release_and_scan',entries=26,new_entry_contracts=1,new_C_algorithm_bodies=1,entry_count_definition='26source-backed ABI entry contracts, not26Cfunctions or a completion percentage. Added one fully coordinator-guided resource-release C body; other original engine/providers remain.',current_result='Native26adds compiled resource release and completes a fresh adaptive merchant→2→1→0→outdoorclearance→120hold route. Nine compiled release entries,19compiled free calls and zero old bodies are observed. Native25baseline repeats its earlier game rows/PCM exactly. Current26fixed-input replay is untested. The unchanged compiled free dependency retains native25failed equal-duration fixed-input evidence and its measured OP-progress timing mechanism; adaptive success does not establish equivalent gameplay.',linked_resident_bytes=5986,resident_padding_bytes=158,resource_release=resource,heap_management=heap,task_creation=task,scheduler=scheduler,native_copy=native_copy,authorship=authorship,authorship_by_component={'free':free_authorship,'resource_release':authorship},repaired_route_results=route['results'],prior_native25_results=previous['facts']['repaired_route_results'],native25_deterministic_repeat=dict(full_recorded_rows=analysis['native25_repeat_frames'],different_rows=0,PCM_equal=True),final_video_equal=analysis['final_raw_video_equal'],audio=dict(nonzero_samples={k:x['nonzero_audio_samples']for k,x in route['results'].items()},PCM_equal=analysis['final_PCM_equal'],bursts=analysis['audio_bursts'],listening_verified=False),naturally_observed_controller_calls=obs['controller_entries'],coupled_heap_lifecycle=dict(native_call_pairs=240,sequences=8,compiled_resource_release_C_calls=16,known_payload_byte_comparisons=life['payload_byte_comparisons'],scope=life['scope']),fixed_input_equivalence=None,current_disc_fixed_input_tested=False,inherited_fixed_input_failure=True,fixed_input_failure_profile=25,latest_fixed_input_control=objects['native-free-fixed-followup']['analysis'],latest_free_timing_isolation=objects['native-free-prefix-isolation']['analysis'],latest_live_free_returns=objects['native-free-live-return-analysis']['analysis'],remaining='Current26fixed-input behavior and shared display-device timing remain unproven. Live native25first-two-call returns matchCPU but OPdescriptors advance extra scanlines; broader calls/IRQ/physical timing remain open. Complete remaining CPU/GPU/DSPengine,source link/package/provider replacement and physical authenticated boot/listening. NativeLMChatUI and future256GBhardware remain unverified.',execution_scope='Target compiled C/assembly executes in retained emulated M68000core; original engine/GPU/DSP/CD/HLE/Jaguar device models remain. Native-target compilation is separate from physical execution.',new_training=False,native_Chat=False)
 facts['native_free']={**facts['native_free'],'fresh_gameplay_observation':dict(public_entry_hits=19,compiled_C_body_hits=19,old_body_instructions=0),'original_entry_hex':'0x1545C'}
 facts['heap_initializer']={**facts['heap_initializer'],'fresh_public_entry_hits':obs['initialize_entries'],'fresh_source_entry_hits':obs['native_initialize_calls'],'old_body_instructions':0,'original_entry_hex':'0x1557A'}
 facts['loader']={**facts['loader'],'scope':'96entry/5151keypad checks install5986byte code with158padding inside6144reserve, clear8192temporary bytes; coupled240calls include resource retain/unload. No physical boot/timing proof.'}
 artifacts=dict(previous['relative_artifact_fields']);artifacts.update(derived_disc=str(Path(b['derived_disc']).relative_to(ROOT)),compiled_binary=str(Path(b['linked_component']).relative_to(ROOT)),proof=str((out/'publication.json').relative_to(ROOT)),canonical_free_C=artifacts['canonical_C'],canonical_C=str((native/'resource-release-native.c').relative_to(ROOT)),exact_author_prompts=str((Path(author['directory'])/'prompts-and-responses.txt').relative_to(ROOT)),final_outdoor_PNG=str((Path(route['directory'])/'native26_repaired/original-emulator-final-frame.png').relative_to(ROOT)))
 manifest=dict(schema_version=1,status='published_native_resource_with_remaining_limits',recorded_at=now.isoformat(),directory=str(out),facts=facts,relative_artifact_fields=artifacts,dependencies_sha256=deps,source_snapshots=snapshots,observed_game_source_sha256=observed,preview_pins=pins,derived_disc=b['derived_disc'],original_disc_unchanged=True,whole_game_complete=False)
 save(out/'publication.json',manifest);save(ROOT/'verification/native-resource-publication-current.json',manifest)
 for name in ['native_restoration_evidence.py','assistant_chat.py']:shutil.copy2(ROOT/name,Path.home()/'.lmstudio/local-ai-lab'/name)
 print(json.dumps({'publication':str(out),'entries':26,'dependencies':len(deps),'snapshots':len(snapshots),'fixed_input_current26':'untested','inherited25failure':True,'preview_pins':pins}),flush=True)
if __name__=='__main__':main()
