"""Publish verified native25 free/init derivative; preserve native23 and preview pins."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab';sys.path.insert(0,str(ROOT))
def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 prev_path=ROOT/'verification/native-copy-publication-current.json';previous=read(prev_path)
 for rel,d in previous['dependencies_sha256'].items():assert sha(ROOT/rel)==d,rel
 names=['native-free-disc-build','native-free-disc-entry','native-free-route','native-free-route-analysis','native-free-bundle','native-free-bundle-initialize','native-free-lifecycle','native-free-bundle-copy','native-free-bundle-heap','native-free-bundle-controller','native-free-bundle-rng','native-free-bundle-tasks','native-free-bundle-scheduler','native-free-bundle-heap-blitter-witness','local-native-free','native-free-coder','native-free-reasoning-budget-review']
 paths=[ROOT/'verification'/(name+'-current.json')for name in names[:-1]]+[ROOT/'verification/native-free-reasoning-budget-review.json']
 objects=[read(p)for p in paths];build,entry,route,analysis,free,init,lifecycle,copy,heap,controller,rng,tasks,scheduler,witness,author,coder,reasoning=objects
 assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(paths[0])
 assert route['build_proof_sha256']==sha(paths[0])and analysis['route_proof_sha256']==sha(paths[2])and analysis['both_completed']
 assert analysis['native23_repeat_full_rows_different']==0 and analysis['native23_repeat_PCM_equal']
 assert free['source_accepted']and free['native_cases']==free['trace_cases']==1411 and free['changing_read_native_cases']==4
 assert init['source_accepted']and init['native_cases']==init['trace_cases']==192 and init['byte_identical_to_original_with_same_heap_floor']
 assert lifecycle['source_accepted']and lifecycle['native_call_pairs']==216
 assert copy['source_accepted']and copy['native_cases']==copy['trace_cases']==3260 and copy['raw_count_prefix_cases']==12
 assert heap['source_accepted']and heap['native_cases']==heap['trace_cases']==3392
 assert controller['native_cases']==1216 and controller['trace_cases']==1024 and not controller['limit']
 assert rng['cpu_cases']==1682 and rng['trace_cases']==298 and not rng['limit']and rng['phase']=='both'
 assert tasks['source_accepted']and tasks['native_cases']==tasks['trace_cases']==1280
 assert scheduler['source_accepted']and scheduler['native_cases']==1664 and scheduler['trace_cases']==896
 assert witness['component_proof_sha256']==sha(paths[8])and witness['payload_bytes_checked']==232
 assert all(x['compiled_binary_sha256']==build['linked_component_sha256']for x in [free,init,lifecycle,copy,heap,controller,rng,tasks,scheduler])
 assert build['linked_component_bytes']==5746 and build['component_bytes']==build['heap_bytes_reserved']==6144 and build['staging_bytes_cleared']==8192 and build['native_rebuilt_entries']==25
 for obj in objects:
  for field in ['source_sha256','execution_dependencies_sha256']:
   if isinstance(obj.get(field),dict):
    for p,d in obj[field].items():assert sha(p)==d,p
 assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['original_disc'])==build['original_disc_sha256']
 native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';assert sha(native/'free-native.c')==author['source_sha256']==sha(author['source']) and author['source_accepted']
 assert coder['status']=='terminal_rejected_compile_and_semantic_review'and not coder['source_accepted']
 obs=route['results']['native25_repaired']['observation'];assert obs['old_free_body_steps']==obs['old_initialize_body_steps']==obs['old_copy_body_steps']==0
 assert obs['native_C_free_calls']==obs['free_entries']>0 and obs['native_initialize_calls']==obs['initialize_entries']>0
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  recipe=read(ROOT/'verification'/name)
  for p,d in recipe['hashes'].items():assert sha(p)==d,p
  pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-free-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshots=out/'snapshots';snapshots.mkdir();deps=dict(previous['dependencies_sha256']);index={};observed={}
 def pin(p,snapshot=False):
  p=Path(p).resolve();assert p.is_relative_to(ROOT),str(p);rel=str(p.relative_to(ROOT));digest=sha(p)
  if snapshot:
   dest=snapshots/(hashlib.sha256(rel.encode()).hexdigest()[:12]+'-'+p.name)
   if not dest.exists():shutil.copy2(p,dest)
   assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;index[rel]=dict(snapshot=str(dest.relative_to(ROOT)),sha256=digest)
  else:deps[rel]=digest
 for p in [prev_path,*paths,Path(__file__),ROOT/'native_restoration_evidence.py',ROOT/'assistant_chat.py',ROOT/'scripts/native_chat_team_context.py',ROOT/'scripts/reveal_biwn_native_disc.py']:pin(p,True)
 for obj in objects:
  for field in ['source_sha256','execution_dependencies_sha256']:
   if isinstance(obj.get(field),dict):
    for p in obj[field]:pin(p,True)
 for p in native.iterdir():
  if p.is_file()and(p.suffix in ['.c','.h','.S','.ld']or p.name.startswith('Makefile')):observed[str(p.relative_to(ROOT))]=sha(p);pin(p,True)
 for p in [build['derived_disc'],build['component'],build['linked_component'],build['derived_stage'],build['fixed_runtime_binary']]:pin(p)
 for d in [author['directory'],coder['directory'],reasoning['directory']]:
  for p in Path(d).iterdir():
   if p.is_file():pin(p,True)
 for obj in [free,init,copy,heap]:
  for p in Path(obj['directory']).glob('*.json'):pin(p)
  pin(Path(obj['directory'])/'disassembly.txt')
 pin(Path(lifecycle['directory'])/'results.json')
 for name in ['entry-cases.json','component-cases.json']:pin(Path(entry['directory'])/name)
 for lane in route['lanes']:
  folder=Path(route['directory'])/lane
  for name in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le','original-emulator-final-frame.png','video-final.xrgb8888']:pin(folder/name)
 facts=dict(previous['facts']);previous_authorship=facts['authorship'];previous_results=facts['repaired_route_results'];startup=read(Path(entry['directory'])/'entry-cases.json')[0]
 heap_facts=dict(facts['heap_management']);heap_facts.update(allocator_C_function_calls=obs['native_C_allocate_calls'],compactor_C_function_calls=obs['native_C_compact_calls'],scope=heap['scope'])
 task=dict(facts['task_creation']);task['naturally_observed_native_ABI_entry_calls']=obs['native_task_entries']
 sched=dict(facts['scheduler']);sched.update(C_select_function_calls=obs['native_C_select_calls'],assembly_dispatch_entry_calls=obs['native_dispatch_calls'],assembly_remove_entry_calls=obs['native_remove_calls'],native_RTE_instruction_hits=obs['native_scheduler_RTEs'],yield_stub_hits=obs['scheduler_yield_entries'],remove_trap_hits=obs['scheduler_remove_traps'])
 copy_facts=dict(facts['native_copy']);copy_facts['fresh_gameplay_observation']=dict(source_first_entry_hits=obs['copy_entries'][0],destination_first_entry_hits=obs['copy_entries'][1],compiled_C_body_entry_hits=obs['native_C_copy_entry_observations'],old_copy_body_instructions=obs['old_copy_body_steps'])
 facts.update(status_label='experimental_native25_free_initializer_and_scan',entries=25,new_entry_contracts=2,new_C_algorithm_bodies=1,
  entry_count_definition='25 source-backed ABI entry contracts, not25Cfunctions or a completion percentage. Added one guided local-model C free/coalescing body and one coordinator source-assembled initializer. Other original engine/providers remain.',
  current_result='Native25 diagnostic replaces free-handle/coalescing and heap initializer as well as the preceding23entry contracts. Both fresh native23/native25 runs complete merchant→2→1→0→outdoor clearance→120idleframes. Read-only counters record actual compiled free/initializer entries and zero original bodies. See separate component and coupled lifecycle checks; timing/video/PCM differences are not whole-game equivalence.',
  linked_resident_bytes=5746,resident_padding_bytes=398,heap_bytes_removed_vs_native23=0,heap_management=heap_facts,task_creation=task,scheduler=sched,native_copy=copy_facts,
  native_free=dict(component_checks=dict(native_CPU_cases=1411,ordered_access_cases=1411,changing_read_native_cases=4,original_instruction_coverage_count=len(free['original_instruction_coverage']),full_CPU='D0-D7/A0-A7/PC/SR/USP/SSP',public_stack_save_bytes=8,scope=free['scope']),fresh_gameplay_observation=dict(public_entry_hits=obs['free_entries'],compiled_C_body_hits=obs['native_C_free_calls'],old_body_instructions=obs['old_free_body_steps']),algorithm='Sorted unsigned free-list insertion; adjacent coalescing; wrapped size/free-counter sums; original handle and list rereads; conditional CLR.L handle; full D0/D1/A0/A1/SR/X and original A2/A3 save/restore slots.'),
  heap_initializer=dict(native_CPU_cases=192,ordered_access_cases=192,source_assembled_bytes=72,byte_identical_with_same_relocated_heap_floor=True,coordinator_authored=True,fresh_public_entry_hits=obs['initialize_entries'],fresh_source_entry_hits=obs['native_initialize_calls'],old_body_instructions=obs['old_initialize_body_steps'],scope=init['scope']),
  coupled_heap_lifecycle=dict(native_call_pairs=lifecycle['native_call_pairs'],sequences=lifecycle['variants'],known_payload_byte_comparisons=lifecycle['payload_byte_comparisons'],compiled_free_calls=lifecycle['compiled_free_body_calls'],compiled_initializer_calls=lifecycle['compiled_initializer_calls'],compiled_copy_calls=lifecycle['compiled_copy_body_calls'],scope=lifecycle['scope']),
  loader={**facts['loader'],'startup_instructions':startup['new_instruction_count'],'startup_emulated_CPU_cycles':startup['new_entry_cycles'],'scope':'Same6144resident reservation/8192temporary cleanup as native23;96entry and5151keypad cases. Source initializer and coupled native memory routines protect payload. Physical boot/timing unverified.'},
  repaired_route_results=route['results'],prior_native23_results=previous_results,native23_deterministic_repeat=dict(full_recorded_rows=analysis['native23_repeat_frames'],different_rows=0,PCM_equal=True),final_video_equal=analysis['final_raw_video_equal'],audio=dict(nonzero_samples={k:x['nonzero_audio_samples']for k,x in route['results'].items()},PCM_equal=analysis['final_PCM_equal'],listening_verified=False,bursts=analysis['audio_bursts'],comparison_scope=analysis['audio_comparison_scope']),naturally_observed_controller_calls=obs['controller_entries'],
  authorship=dict(roles=[dict(role='Local Author reasoning medium',seconds=reasoning['reported_seconds'],outcome='Exhausted7999reasoning tokens with no C output'),dict(role='Local guided Author reasoning off',seconds=author['reported_seconds'],outcome='Raw guided C accepted unchanged in stated native/coupled/game scope'),dict(role='Local coder30B comparison reasoning off',seconds=coder['reported_seconds'],outcome='Rejected compile and semantic errors; no native cases executed')],accepted_C_body_role='Local guided Author',raw_guided_model_C_unchanged=True,manual_C_edits=0,coordinator_supplied_full_algorithm_and_disassembly=True,coordinator_role='Supplied complete branch algorithm and ABI/flag contract; authored native wrapper/helpers, initializer assembly, build/link/loader, gates and read-only observers.',accepted_model='local/advertising-qwen38',same_27B_weights=True,Reviewer_executed=False,independent_model_validation=False,comparison_scope=coder['comparison_scope']),prior_copy_authorship=previous_authorship,route_phase_frames=analysis['phase_frames'],first_same_frame_differences=analysis['first_same_frame_differences'],
  matched_state_scope=free['scope'],execution_scope='Target-compiled C/assembly executes in the retained emulated M68000 core. Original engine/GPU/DSP/CD/HLE and Jaguar device models remain; no physical-console or complete source-built game proof.',
  workflow_corrections='Reasoning-medium output budget yielded no code. Guided daily-model Author C passed unchanged after coordinator supplied full algorithm. Installed coder30B made a fast but unusable C draft under assembly/ABI-only input; rejected without editing its C or weakening gates. Daily model restored; no new training or promotion.',
  remaining='Complete remaining CPU/GPU/DSP engine and source link/package/provider replacement; broader routes and fixed-input/IRQ/concurrency/timing/busfault/arbitrary-alias tests; authenticated physical boot/listening. Native23/native25 frame/video/PCM differences remain scoped to observed results. Native LM Chat UI/cancellation and future256GBhardware testing remain unverified.',new_training=False,native_Chat=False)
 artifacts=dict(previous['relative_artifact_fields']);artifacts.update(derived_disc=str(Path(build['derived_disc']).relative_to(ROOT)),compiled_binary=str(Path(build['linked_component']).relative_to(ROOT)),proof=str((out/'publication.json').relative_to(ROOT)),canonical_copy_C=artifacts['canonical_C'],canonical_C=str((native/'free-native.c').relative_to(ROOT)),heap_initializer_assembly=str((native/'heap-initialize.S').relative_to(ROOT)),exact_author_prompts=str((Path(author['directory'])/'prompts-and-responses.txt').relative_to(ROOT)),coder_comparison_protocol=str(paths[15].relative_to(ROOT)),final_outdoor_PNG=str((Path(route['directory'])/'native25_repaired/original-emulator-final-frame.png').relative_to(ROOT)))
 manifest=dict(schema_version=1,status='published_native_free_with_remaining_limits',recorded_at=now.isoformat(),directory=str(out),facts=facts,relative_artifact_fields=artifacts,dependencies_sha256=deps,source_snapshots=index,observed_game_source_sha256=observed,preview_pins=pins,derived_disc=build['derived_disc'],original_disc_unchanged=True,whole_game_complete=False)
 save(out/'publication.json',manifest);save(ROOT/'verification/native-free-publication-current.json',manifest)
 for name in ['native_restoration_evidence.py','assistant_chat.py']:shutil.copy2(ROOT/name,RT/name)
 print(json.dumps(dict(publication=str(out),dependencies=len(deps),source_snapshots=len(index),entries=25,preview_pins=pins)),flush=True)
if __name__=='__main__':main()
