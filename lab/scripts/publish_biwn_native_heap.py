"""Freeze reviewed native21 heap/expanded-loader results; retain original/previews."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    previous_path=ROOT/'verification/native-scheduler-publication-current.json';previous=read(previous_path)
    for rel,d in previous['dependencies_sha256'].items():assert sha(ROOT/rel)==d,rel
    names=['native-heap-disc-build-current.json','native-heap-disc-entry-current.json','native-heap-route-current.json','native-heap-route-analysis-current.json','native-heap-bundle-current.json','native-heap-bundle-controller-current.json','native-heap-bundle-rng-current.json','native-heap-bundle-tasks-current.json','native-heap-bundle-scheduler-current.json','native-heap-bundle-blitter-witness-current.json','local-native-heap-current.json']
    paths=[ROOT/'verification'/n for n in names];build,entry,route,analysis,heap,controller,rng,tasks,scheduler,witness,author=[read(p)for p in paths]
    assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(paths[0])
    assert route['build_proof_sha256']==sha(paths[0])and analysis['route_proof_sha256']==sha(paths[2])and analysis['both_completed']
    assert analysis['native19_repeat_full_rows_different']==0 and analysis['native19_repeat_PCM_equal']
    assert heap['source_accepted']and heap['native_cases']==3392 and heap['trace_cases']==3392 and heap['phase']=='both'
    assert controller['native_cases']==1216 and controller['trace_cases']==1024 and not controller['limit']
    assert rng['cpu_cases']==1682 and rng['trace_cases']==298 and rng['phase']=='both'and not rng['limit']
    assert tasks['source_accepted']and tasks['native_cases']==1280 and tasks['trace_cases']==1280
    assert scheduler['source_accepted']and scheduler['native_cases']==1664 and scheduler['trace_cases']==896
    assert witness['component_proof_sha256']==sha(paths[4])and witness['payload_bytes_checked']==232
    assert all(x['compiled_binary_sha256']==build['linked_component_sha256']for x in [heap,controller,rng,tasks,scheduler])
    assert build['linked_component_bytes']==4162 and build['component_bytes']==6144 and build['heap_bytes_reserved']==6144 and build['staging_bytes_cleared']==8192
    for obj in [build,entry,route,analysis,heap,controller,rng,tasks,scheduler,witness]:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p,d in obj.get(field,{}).items():assert sha(p)==d,p
    assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['original_disc'])==build['original_disc_sha256']
    results=route['results'];candidate=results['native21_repaired'];obs=candidate['observation'];assert obs['native_C_allocate_calls']>0 and obs['old_allocate_steps']==obs['old_compact_steps']==0
    assert obs['heap_base']==build['heap_start']and not(obs['errors']or obs['copy_errors']or obs['repair_code_errors'])
    pins={}
    for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=read(ROOT/'verification'/name)
        for p,d in recipe['hashes'].items():assert sha(p)==d,p
        pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-heap-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshots=out/'snapshots';snapshots.mkdir();deps=dict(previous['dependencies_sha256']);index={};observed={}
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    def pin(p,copy=False):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);relative=str(p.relative_to(ROOT));digest=sha(p)
        if copy:
            dest=snapshots/(hashlib.sha256(relative.encode()).hexdigest()[:12]+'-'+p.name)
            if not dest.exists():shutil.copy2(p,dest)
            assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;index[relative]=dict(snapshot=str(dest.relative_to(ROOT)),sha256=digest)
        else:deps[relative]=digest
    for p in [previous_path,*paths,Path(__file__),ROOT/'native_restoration_evidence.py',ROOT/'assistant_chat.py',ROOT/'scripts/native_chat_team_context.py']:pin(p,True)
    for obj in [build,entry,route,analysis,heap,controller,rng,tasks,scheduler,witness]:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p in obj.get(field,{}):pin(p,True)
    for p in native.iterdir():
        if p.is_file()and(p.suffix in ['.c','.h','.S','.ld']or p.name.startswith('Makefile')):observed[str(p.relative_to(ROOT))]=sha(p);pin(p,True)
    for p in [build['derived_disc'],build['component'],build['linked_component'],build['derived_stage'],build['fixed_runtime_binary']]:pin(p)
    for p in Path(author['directory']).iterdir():
        if p.is_file():pin(p,True)
    for n in ['fixtures.json','native-results.json','trace-results.json','disassembly.txt','symbols.json']:pin(Path(heap['directory'])/n)
    for n in ['entry-cases.json','component-cases.json']:pin(Path(entry['directory'])/n)
    for lane in route['lanes']:
        folder=Path(route['directory'])/lane
        for n in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le','original-emulator-final-frame.png','video-final.xrgb8888']:pin(folder/n)
    transcript=Path(author['directory'])/'prompts-and-responses.txt';facts=dict(previous['facts']);facts.pop('model_status_development_case',None)
    for key in ['prior_native15_task_creation_results','prior_task_status_development_case','prior_task_creation_authorship','prior_original_vs_native13_repair_results']:
        facts.pop(key,None)
    old_authorship=facts['authorship'];old_results=facts['repaired_route_results'];native_rows=read(Path(heap['directory'])/'native-results.json');startup=read(Path(entry['directory'])/'entry-cases.json')[0]
    task=dict(facts['task_creation']);task.update(naturally_observed_native_ABI_entry_calls=obs['native_task_entries']);sched=dict(facts['scheduler']);sched.update(C_select_function_calls=obs['native_C_select_calls'],assembly_dispatch_entry_calls=obs['native_dispatch_calls'],assembly_remove_entry_calls=obs['native_remove_calls'],native_RTE_instruction_hits=obs['native_scheduler_RTEs'],yield_stub_hits=obs['scheduler_yield_entries'],remove_trap_hits=obs['scheduler_remove_traps'])
    facts.update(status_label='experimental_native21_heap_and_scan',entries=21,new_entry_contracts=2,new_C_algorithm_bodies=2,
        entry_count_definition='21 source-backed ABI entry contracts, not21new C functions. This pass adds allocator152A2 and compactor15200 with guided model C bodies and coordinator register/CCR wrappers. Previous native19 components remain; originalE3E0copy and emulated blitter are retained dependencies.',
        current_result='Separate native21 diagnostic CDI adds target-compiled allocator and compactor, expands resident reservation to6144bytes and consumes/restores8KBtemporary staging atFC000..FE000. Both native19/native21 complete fresh merchant→two descents→outdoor clearance→120idleframes. Not full game source, physical boot or timing equivalence.',
        resident_bytes=6144,linked_resident_bytes=4162,resident_padding_bytes=1982,reserved_bytes=6144,heap_bytes_removed_vs_native19=2624,heap_start=build['heap_start'],
        heap_management=dict(native_CPU_cases=3392,ordered_access_cases=3392,original_instruction_coverage=[200,200],allocator_C_function_calls=obs['native_C_allocate_calls'],compactor_C_function_calls=obs['native_C_compact_calls'],natural_compaction_observed=obs['native_C_compact_calls']>0,old_allocator_body_instructions=obs['old_allocate_steps'],old_compactor_body_instructions=obs['old_compact_steps'],native_dependency='Retained original E3E0 native copy/emulated blitter, executed for full nativeCPU cases and fresh game. Not a newly source-built copy/device.',ordered_access_copy_dependency_scripted=True,blitter_payload_witness_bytes=232,blitter_witness_copy_sizes=[128,128],host_shim_blit_commands_is_not_native_counter=True,algorithm='Signed wrapped fit/split, reverse256handle scan/exhaustion and one compaction retry. Compactor preserves original unsigned tag/limit comparisons and rereads, relocates handles and rebuilds tail. Coordinator flag helpers/native capture wrappers preserve exposed D0/D1/A0/A1/CCR.',scope=heap['scope']),
        loader=dict(staging_start=build['staging_address'],staging_end=build['staging_end'],staging_bytes_restored=8192,startup_instructions=startup['new_instruction_count'],startup_emulated_CPU_cycles=startup['new_entry_cycles'],entry_cases=96,keypad_ABI_cases=5151,temporary_original_bytes_all_zero=True,adjacent_FE000_original_bytes_preserved=True,scope='Native fixture copy/cleanup before400A with fullCPU/publicRAM comparison, actual initialized heap allocations/compaction preserve resident bytes. Not physical firmware/device concurrency or cycle equivalence.'),
        task_creation=task,scheduler=sched,matched_state_scope=heap['scope'],repaired_route_results=results,prior_native19_results=old_results,
        native19_deterministic_repeat=dict(full_recorded_rows=analysis['native19_repeat_frames'],different_rows=0,PCM_equal=True),final_video_equal=analysis['final_raw_video_equal'],audio=dict(nonzero_samples={k:x['nonzero_audio_samples']for k,x in results.items()},PCM_equal=analysis['final_PCM_equal'],listening_verified=False),
        naturally_observed_controller_calls=obs['controller_entries'],authorship=dict(roles=author['roles'],raw_model_C_unchanged=True,manual_C_edits=0,coordinator_supplied_full_algorithm_and_disassembly=True,coordinator_role='Supplied full algorithms/register-frame plan and wrote shared flag header, native register/CCR/copy captures, clear boundary, expanded loader/linker, tests/observer/harness.',same_27B_weights=True,independent_model_validation=False),prior_scheduler_authorship=old_authorship,
        workflow_corrections='Both heap C drafts accepted unchanged after tests. Model clears private unused NZVC bits while setting initial allocatorX; only final exposed CPU/flags are claimed, not per-instruction identity. Coordinator first checked FE0008KBstaging and found94original nonzero bytes; chose verified zeroFC000..FE000 instead. A host-shim blit counter waszero for CPU-origin commands; knownpayload witness proves actual retained-blitter relocation without misreading thatcounter.',
        remaining='Complete native engine/source link/package and remaining originalCPU/GPU/DSP/game/provider paths. Original copy/blitter retained; expanded loader and heap cost extra bytes/cycles. IRQ/concurrency/busfault/general malformedheap, fixed-input/per-frame/wholegame equivalence, physical authenticated boot/listening remain unverified. Existing RNG divisor/scan read limits, fresh LM nativeChat rendering/cancellation and future256GBhardware tests remain open.',new_training=False,native_Chat=False)
    artifacts=dict(previous['relative_artifact_fields']);artifacts.update(derived_disc=str(Path(build['derived_disc']).relative_to(ROOT)),compiled_binary=str(Path(build['linked_component']).relative_to(ROOT)),proof=str((out/'publication.json').relative_to(ROOT)),canonical_C=str((native/'heap-allocate-native.c').relative_to(ROOT)),canonical_compactor_C=str((native/'heap-compact-native.c').relative_to(ROOT)),heap_assembly=str((native/'heap-shims.S').relative_to(ROOT)),exact_author_prompts=str(transcript.relative_to(ROOT)),final_outdoor_PNG=str((Path(route['directory'])/'native21_repaired/original-emulator-final-frame.png').relative_to(ROOT)))
    manifest=dict(schema_version=1,status='published_native_heap_with_remaining_limits',recorded_at=now.isoformat(),directory=str(out),facts=facts,relative_artifact_fields=artifacts,dependencies_sha256=deps,source_snapshots=index,observed_game_source_sha256=observed,preview_pins=pins,derived_disc=build['derived_disc'],original_disc_unchanged=True,whole_game_complete=False)
    save(out/'publication.json',manifest);save(ROOT/'verification/native-heap-publication-current.json',manifest);shutil.copy2(ROOT/'native_restoration_evidence.py',RT/'native_restoration_evidence.py')
    reveal=ROOT/'scripts/reveal_biwn_native_disc.py';t=reveal.read_text()
    if "'native-heap-publication-current.json'"not in t:reveal.write_text(t.replace("'native-scheduler-publication-current.json'","'native-heap-publication-current.json','native-scheduler-publication-current.json'"))
    guide=f'''BLACK ICE WHITE NOISE — NATIVE HEAP DIAGNOSTIC
Updated {now.isoformat()}

The separate native21 diagnostic adds target-compiled C allocator152A2 and compactor15200 to the previous native19 components.21is an ABI entry count, not a completion percentage or21new C functions. Original E3E0 copy, emulated blitter and many other original game/CPU/GPU/DSP/HLE/CD/device providers remain. This is a partial source/native rebuild.

Local Author allocate:{author['roles'][0]['seconds']}seconds; Author compact:{author['roles'][1]['seconds']}seconds; same-weight Reviewer:{author['roles'][2]['seconds']}seconds. Both raw C drafts passed unchanged. Coordinator supplied full algorithms/disassembly/frame plan and wrote flag helper header, native assembly register/copy captures, expanded loader, linker and tests. Not autonomous decompilation or independent model review; no weights trained.

COMPONENT AND LOADER EVIDENCE
3,392native cases compare full D/A/PC/SR/USP/SSP, public2MBRAM, seven blitter registers and nested call arguments. Actual retained native E3E0/emulated blitter executes; no host copy during those runs. Separate3,392ordered-access Unicorn cases exercise changing reads and explicit scripted copy effects/varied helper registers/CCR; these are not the blitter proof.200/200original heap instruction starts covered. Tests include split/whole/middle allocation, reverse256handle search/exhaustion, compaction retry, wrapped/signed requests and counter flags. Private8KBstack/newcode/redirects excluded from RAM identity; original RTS/arguments included. Only final exposed CPU/flags are claimed, not per-instruction register identity. A separate native witness moves two known116-byte payloads through128-byte copies and verifies handles/fullRAM/CPU/hardware. Host-shim blit_commands is not a CPU-origin command counter.

Relinked controller1,216CPU/1,024MMIO; RNG1,682CPU/298access; task1,280CPU/1,280access; scheduler1,664CPU/896access all pass on the same4162-byte binary.1,982padding bytes make6144resident/reserved bytes,2624more heap bytes than native19. The linker heap floor is{hex(build['heap_start'])}. The temporary zero window isFC000..FE000(8192bytes), restored before400A. FE000contains94original nonzero bytes and was deliberately kept outside the new window.96entry cases preserve original CPU/RAM boundaries; actual initialized-heap allocation/compaction protects resident code;5,151keypad ABI cases pass. Startup:{startup['new_instruction_count']}instructions/{startup['new_entry_cycles']}emulated CPU cycles, not a physical/FPS result. All other CDIbytes/metadata and original image preserved; diagnostic has{build['changed_disc_bytes']}changedCDI bytes.

FRESH GAMEPLAY
'''
    for lane,x in results.items():guide+=f"{lane}: {x['executed_frames']}frames; merchant={x['merchant_reached']}; outdoor120hold={x['completed_outdoor_hold']}; final={x['final_fields']}; nonzeroPCM={x['nonzero_audio_samples']}.\n"
    guide+=f'''The preceding floor2→1→0transitions and outdoor clearance/120hold are reviewed. Native19 reproduces all{analysis['native19_repeat_frames']}prior rows and PCM exactly. Native21 observed GCC allocator entry{obs['native_C_allocate_calls']}times and compactor entry{obs['native_C_compact_calls']}times. Natural compaction observed={obs['native_C_compact_calls']>0}; component proof remains separate. Zero old allocator/compactor/task/controller/RNG/keypad/scheduler-handler body instructions execute. Retained copy entry calls={obs['retained_copy_entries']}. Resident bytes match at entry and finish. Fresh CDI/HLE loads, normal pad and read-only observers only; no checkpoint restore, guest RAM/code writes, CPU reseed or source execution owner. Final raw video equal={analysis['final_raw_video_equal']}; PCM equal={analysis['final_PCM_equal']}. Timing/pose/audio differences remain; not fixed-input or fullgame equivalence.

Exact prompts/responses: {transcript}
Allocator source: {native/'heap-allocate-native.c'}
Compactor source: {native/'heap-compact-native.c'}
Rebuild: make -f Makefile.heap-bundle heap-bundle (from native-m68k)
Diagnostic CDI: {build['derived_disc']}
Frozen proof/source snapshots: {out}
Show BIWN Native Disc.command reveals this diagnostic. Your current preview and P/O112/84pins are preserved. Click preview; C+Up runs. Arrows move/turn, Z=A, X=B, C=C, P pause, M mute, Esc close.

REMAINING
Full native engine/source link/package and original/provider replacement, IRQ/timing/fixed-input fidelity, physical authenticated console boot and listening remain unverified. General malformed heaps/bus faults and arbitrary aliases are outside finite fixtures. Existing scan/RNG limits remain. Native LM Chat rendering/cancellation and future256GBhardware tests remain unverified. Advertising daily base/retrieval/copyediting and prior adapter-quality limits are unchanged; see CURRENT ADVERTISING.txt. Overall goal remains incomplete.
'''
    for root,label in [(ROOT,'workspace'),(RT,'installed')]:
        for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(root/name,out/(label+'-previous-'+name))
        (root/'CURRENT DECOMPILATION.txt').write_text(guide)
        (root/'CURRENT LOCAL INFERENCE.txt').write_text('LOCAL AI LAB — CURRENT INFERENCE\nUpdated '+now.isoformat()+'\n\nShared27Blocal model advertising-scholar remains available. Native21heap source Author41.38s/25.32s, Reviewer11.9s; raw C accepted unchanged after native CPU/bus/device and fresh-game checks. Coordinator supplied algorithms/frame/header/assembly/tests. Same-weight roles are not independent validation. No new weights trained.\nExact prompts/responses: '+str(transcript)+'\n\nSaved game evidence now selects frozen native21for a fresh native heap/allocator/compactor question.4162linked bytes,6144resident reserve,8KBtemporary startup window; full game/provider/IRQ/physical boot limits remain. Current preview is preserved. Native Chat UI rendering/cancellation remains unverified. Previous saved-assistant development status test produced104words in28.73s after host scope-review fixes; that is not a new heap-model benchmark or general reliability proof. Advertising workflows remain in CURRENT ADVERTISING.txt/ADVERTISING WRITING.txt. Overall goal remains incomplete.\n')
    (native/'README.txt').write_text('NATIVE M68000 PARTIAL SOURCE — HEAP DIAGNOSTIC\nUpdated '+now.isoformat()+'\n\nmake -f Makefile.heap-bundle heap-bundle BUILD=build-heap\n\n21ABIentries;4162linked bytes+1982padding;6144heapreserve. Guided local C allocator/compactor join native19components. Retained original E3E0/emulated blitter.8KBzero temporary FC000..FE000is restored before400A. See CURRENT DECOMPILATION.txt for CPU/bus/device/loader/game evidence and limits. Not fullgame/native/physical boot equivalence.\n\n'+build['derived_disc']+'\n')
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),role='coordinator',action='published native heap diagnostic',publication=str(out/'publication.json'),new_weights_trained=False,whole_game_complete=False))+'\n')
    print(json.dumps(dict(publication=str(out),dependencies=len(deps),source_snapshots=len(index),entries=21,preview_pins=pins)),flush=True)
if __name__=='__main__':main()
