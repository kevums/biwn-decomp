"""Freeze reviewed native23 copy results; retain original and both previews."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab';sys.path.insert(0,str(ROOT))
def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    import binary_tools
    prev_path=ROOT/'verification/native-heap-publication-current.json';previous=read(prev_path)
    for rel,d in previous['dependencies_sha256'].items():assert sha(ROOT/rel)==d,rel
    names=['native-copy-disc-build-current.json','native-copy-disc-entry-current.json','native-copy-route-current.json','native-copy-route-analysis-current.json','native-copy-bundle-current.json','native-copy-bundle-heap-current.json','native-copy-bundle-controller-current.json','native-copy-bundle-rng-current.json','native-copy-bundle-tasks-current.json','native-copy-bundle-scheduler-current.json','native-copy-bundle-heap-blitter-witness-current.json','local-native-copy-current.json']
    paths=[ROOT/'verification'/n for n in names];build,entry,route,analysis,copy,heap,controller,rng,tasks,scheduler,witness,author=[read(p)for p in paths]
    assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(paths[0])
    assert route['build_proof_sha256']==sha(paths[0])and analysis['route_proof_sha256']==sha(paths[2])and analysis['both_completed']
    assert analysis['native21_repeat_full_rows_different']==0 and analysis['native21_repeat_PCM_equal']
    assert copy['source_accepted']and copy['native_cases']==copy['trace_cases']==3260 and copy['raw_count_prefix_cases']==12
    assert heap['source_accepted']and heap['native_cases']==heap['trace_cases']==3392
    assert controller['native_cases']==1216 and controller['trace_cases']==1024 and not controller['limit']
    assert rng['cpu_cases']==1682 and rng['trace_cases']==298 and rng['phase']=='both'and not rng['limit']
    assert tasks['source_accepted']and tasks['native_cases']==tasks['trace_cases']==1280
    assert scheduler['source_accepted']and scheduler['native_cases']==1664 and scheduler['trace_cases']==896
    assert witness['component_proof_sha256']==sha(paths[5])and witness['payload_bytes_checked']==232
    assert witness['profiles'][1]['compiled_copy_body_calls']==2 and witness['profiles'][1]['old_copy_body_steps']==0
    assert all(x['compiled_binary_sha256']==build['linked_component_sha256']for x in [copy,heap,controller,rng,tasks,scheduler])
    assert build['linked_component_bytes']==4726 and build['component_bytes']==build['heap_bytes_reserved']==6144 and build['staging_bytes_cleared']==8192
    objects=[build,entry,route,analysis,copy,heap,controller,rng,tasks,scheduler,witness]
    for obj in objects:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p,d in obj.get(field,{}).items():assert sha(p)==d,p
    assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['original_disc'])==build['original_disc_sha256']
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    assert sha(native/'copy-native.c')==author['source_sha256']and sha(author['source'])==author['source_sha256']
    image=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();ins,_=binary_tools.m68k_instructions(image[0xe3e0:0xe4aa],0xe3e0)
    assert {x['address']for x in ins}==set(copy['original_instruction_coverage'])and len(ins)==57
    obs=route['results']['native23_repaired']['observation'];assert obs['old_copy_body_steps']==0 and obs['native_C_copy_entry_observations']==obs['copy_entries'][0]+obs['copy_entries'][1]>0
    pins={}
    for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=read(ROOT/'verification'/name)
        for p,d in recipe['hashes'].items():assert sha(p)==d,p
        pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-copy-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshots=out/'snapshots';snapshots.mkdir();deps=dict(previous['dependencies_sha256']);index={};observed={}
    def pin(p,copy_file=False):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);relative=str(p.relative_to(ROOT));digest=sha(p)
        if copy_file:
            dest=snapshots/(hashlib.sha256(relative.encode()).hexdigest()[:12]+'-'+p.name)
            if not dest.exists():shutil.copy2(p,dest)
            assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;index[relative]=dict(snapshot=str(dest.relative_to(ROOT)),sha256=digest)
        else:deps[relative]=digest
    for p in [prev_path,*paths,Path(__file__),ROOT/'native_restoration_evidence.py',ROOT/'assistant_chat.py',ROOT/'scripts/native_chat_team_context.py']:pin(p,True)
    for obj in objects:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p in obj.get(field,{}):pin(p,True)
    for p in native.iterdir():
        if p.is_file()and(p.suffix in ['.c','.h','.S','.ld']or p.name.startswith('Makefile')):observed[str(p.relative_to(ROOT))]=sha(p);pin(p,True)
    for p in [build['derived_disc'],build['component'],build['linked_component'],build['derived_stage'],build['fixed_runtime_binary']]:pin(p)
    for directory in [Path(author['directory']),Path(author['previous']['directory'])]:
        for p in directory.iterdir():
            if p.is_file():pin(p,True)
    for component in [copy,heap]:
        for name in ['fixtures.json','native-results.json','trace-results.json','disassembly.txt','symbols.json']:pin(Path(component['directory'])/name)
    pin(Path(copy['directory'])/'raw-count-prefixes.json')
    for name in ['entry-cases.json','component-cases.json']:pin(Path(entry['directory'])/name)
    for lane in route['lanes']:
        folder=Path(route['directory'])/lane
        for name in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le','original-emulator-final-frame.png','video-final.xrgb8888']:pin(folder/name)
    facts=dict(previous['facts']);old_authorship=facts['authorship'];old_results=facts['repaired_route_results'];startup=read(Path(entry['directory'])/'entry-cases.json')[0]
    original_author=author['previous'];roles=[{**row,'outcome':'CPU-rejected draft'if i==0 else'Incorrect same-weight review; not validation'}for i,row in enumerate(original_author['roles'])]
    roles.append(dict(role='Local Repair Author',seconds=author['seconds'],outcome='Guided rewrite accepted unchanged after CPU/bus/blitter/route tests'))
    heap_facts=dict(facts['heap_management']);heap_facts.update(allocator_C_function_calls=obs['native_C_allocate_calls'],compactor_C_function_calls=obs['native_C_compact_calls'],old_allocator_body_instructions=0,old_compactor_body_instructions=0,native_dependency='Both copy ABI entries redirect to target-compiled C; native component/coupled payload witness and fresh game execute it with emulated blitter.',scope=heap['scope'])
    task=dict(facts['task_creation']);task['naturally_observed_native_ABI_entry_calls']=obs['native_task_entries']
    sched=dict(facts['scheduler']);sched.update(C_select_function_calls=obs['native_C_select_calls'],assembly_dispatch_entry_calls=obs['native_dispatch_calls'],assembly_remove_entry_calls=obs['native_remove_calls'],native_RTE_instruction_hits=obs['native_scheduler_RTEs'],yield_stub_hits=obs['scheduler_yield_entries'],remove_trap_hits=obs['scheduler_remove_traps'])
    facts.update(status_label='experimental_native23_copy_and_scan',entries=23,new_entry_contracts=2,new_C_algorithm_bodies=1,
     entry_count_definition='23 source-backed ABI entry contracts, not23Cfunctions or a completion percentage. New source-first and destination-first copy wrappers share one guided model C body. Original blitter hardware behavior is still supplied by the retained emulator.',
     current_result='Separate native23 diagnostic replaces both public original CPU copy entry paths with target-compiled C. Native21/native23 complete fresh merchant→two descents→outdoor clearance→120idleframes. New run observes compiled copy body28026times and zero old copy-body instructions; no natural destination-first entry observed. Other original engine/provider and timing differences remain.',
     resident_bytes=6144,linked_resident_bytes=4726,resident_padding_bytes=1418,reserved_bytes=6144,heap_bytes_removed_vs_native21=0,heap_start=build['heap_start'],heap_management=heap_facts,task_creation=task,scheduler=sched,
     native_copy=dict(component_checks=dict(native_CPU_cases=3260,ordered_access_cases=3260,original_instruction_coverage=[57,57],raw_count_three_unit_prefix_cases=12,raw_huge_count_full_returns_claimed=False,full_CPU='D0-D7/A0-A7/PC/SR/USP/SSP',public_original_stack_save_bytes=12,all_byte_counts_below128_and_forward_overlap=True,large_phrase_offsets='All8source×8destination offsets;128/129/65535/65536/65537/131071/131072/131073counts and overlap cases.',actual_native_blitter_effects=True,ordered_access_engine_MMIO='Ordinary mapped storage; not device behavior or CCR oracle.',coupled_compactor_known_payload_bytes=232,coupled_copy_sizes=[128,128],scope=copy['scope']),fresh_gameplay_observation=dict(source_first_entry_hits=obs['copy_entries'][0],destination_first_entry_hits=obs['copy_entries'][1],compiled_C_body_entry_hits=obs['native_C_copy_entry_observations'],old_copy_body_instructions=obs['old_copy_body_steps'],entry_scope='Read-only original public ABI and compiled C first-instruction hits in this fresh route, separate from component cases.'),retained_dependency='Emulated M68000 CPU, Jaguar blitter/device model, original engine/GPU/DSP/CD/HLE paths; no physical or full source-built game proof.',algorithm='Forward byte path preserves overlapping writes; larger path preserves wrapped subtraction-N thresholds, ordered blitter setup and chunks, original12byte public register saves/restores and final full ABI flags. No replacement host memcpy or game-state execution owner.'),
     loader=dict(staging_start=build['staging_address'],staging_end=build['staging_end'],staging_bytes_restored=8192,startup_instructions=startup['new_instruction_count'],startup_emulated_CPU_cycles=startup['new_entry_cycles'],entry_cases=96,keypad_ABI_cases=5151,temporary_original_bytes_all_zero=True,adjacent_FE000_original_bytes_preserved=True,scope='Same6144resident reservation and8192temporary cleanup as native21; full entryCPU/publicRAM and heap init/allocation/compaction protect the new payload. No physical boot/timing claim.'),
     repaired_route_results=route['results'],prior_native21_results=old_results,native21_deterministic_repeat=dict(full_recorded_rows=analysis['native21_repeat_frames'],different_rows=0,PCM_equal=True),final_video_equal=analysis['final_raw_video_equal'],audio=dict(nonzero_samples={k:x['nonzero_audio_samples']for k,x in route['results'].items()},PCM_equal=analysis['final_PCM_equal'],listening_verified=False),
     naturally_observed_controller_calls=obs['controller_entries'],authorship=dict(roles=roles,accepted_C_body_role='Local Repair Author',raw_guided_model_C_unchanged=True,manual_C_edits=0,coordinator_supplied_full_algorithm_and_disassembly=True,coordinator_role='Supplied complete repair algorithm/flags/ABI and wrote native frame, header, linker/build/loader adaptations, CPU/bus/device tests and read-only game observers.',same_27B_weights=True,independent_model_validation=False),prior_heap_authorship=old_authorship,
     matched_state_scope=copy['scope'],execution_scope='Actual target-compiled code runs inside the retained emulated M68000 core; fixed original engine/GPU/DSP/HLE/CD/device providers remain. Native compilation is separate from physical console execution.',
     workflow_corrections='First Author mapped registers/constants/flags incorrectly; same-weight Reviewer falsely approved. Zero-count fullCPU preflight rejected it. Coordinator supplied complete repair algorithm and added exact public stack restore reads to contract; raw Repair Author C then passed unchanged. No new weights trained.',
     remaining='Complete remaining CPU/GPU/DSP engine/source link/package/provider replacement, other copy/internal call paths, fixed-input/IRQ/concurrency/timing/busfault/arbitrary alias behavior, physical authenticated boot/listening. Native21/native23 routes differ in frames/video/PCM. Existing RNG/scan limits, native LM Chat rendering/cancellation and future256GBhardware remain open.',new_training=False,native_Chat=False)
    artifacts=dict(previous['relative_artifact_fields']);artifacts.update(derived_disc=str(Path(build['derived_disc']).relative_to(ROOT)),compiled_binary=str(Path(build['linked_component']).relative_to(ROOT)),proof=str((out/'publication.json').relative_to(ROOT)),canonical_C=str((native/'copy-native.c').relative_to(ROOT)),copy_assembly=str((native/'copy-shims.S').relative_to(ROOT)),exact_author_prompts=str((Path(author['directory'])/'prompts-and-responses.txt').relative_to(ROOT)),initial_failed_author_prompts=str((Path(author['previous']['directory'])/'prompts-and-responses.txt').relative_to(ROOT)),final_outdoor_PNG=str((Path(route['directory'])/'native23_repaired/original-emulator-final-frame.png').relative_to(ROOT)))
    manifest=dict(schema_version=1,status='published_native_copy_with_remaining_limits',recorded_at=now.isoformat(),directory=str(out),facts=facts,relative_artifact_fields=artifacts,dependencies_sha256=deps,source_snapshots=index,observed_game_source_sha256=observed,preview_pins=pins,derived_disc=build['derived_disc'],original_disc_unchanged=True,whole_game_complete=False)
    save(out/'publication.json',manifest);save(ROOT/'verification/native-copy-publication-current.json',manifest)
    for name in ['native_restoration_evidence.py','assistant_chat.py']:shutil.copy2(ROOT/name,RT/name)
    print(json.dumps(dict(publication=str(out),dependencies=len(deps),source_snapshots=len(index),entries=23,preview_pins=pins)),flush=True)
if __name__=='__main__':main()
