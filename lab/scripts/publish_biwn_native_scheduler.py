"""Publish immutable native19 scheduler evidence only after component/route review."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    previous_path=ROOT/'verification/native-task-create-publication-current.json';previous=read(previous_path)
    for rel,d in previous['dependencies_sha256'].items():assert sha(ROOT/rel)==d,rel
    names=['native-scheduler-disc-build-current.json','native-scheduler-disc-entry-current.json','native-scheduler-route-current.json','native-scheduler-route-analysis-current.json','native-scheduler-bundle-current.json','native-scheduler-bundle-controller-current.json','native-scheduler-bundle-rng-current.json','native-scheduler-bundle-tasks-current.json','local-native-scheduler-current.json']
    paths=[ROOT/'verification'/n for n in names];build,entry,route,analysis,scheduler,controller,rng,tasks,author=[read(p)for p in paths]
    assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(paths[0])
    assert route['build_proof_sha256']==sha(paths[0]) and analysis['route_proof_sha256']==sha(paths[2])
    assert analysis['both_completed']and analysis['native15_repeat_full_rows_different']==0 and analysis['native15_repeat_PCM_equal']
    assert scheduler['source_accepted']and scheduler['native_cases']==1664 and scheduler['trace_cases']==896
    assert scheduler['original_instruction_locations']==36
    assert build['linked_component_bytes']==3090 and build['component_bytes']==3516 and build['heap_bytes_reserved']==3520
    assert controller['native_cases']==1216 and controller['trace_cases']==1024 and not controller['limit']
    assert rng['cpu_cases']==1682 and rng['trace_cases']==298 and rng['phase']=='both'and not rng['limit']
    assert tasks['native_cases']==1280 and tasks['trace_cases']==1280 and tasks['empty_pool_exception_cases']==128 and tasks['source_accepted']
    assert all(x['compiled_binary_sha256']==build['linked_component_sha256']for x in [scheduler,controller,rng,tasks])
    for obj in [build,entry,route,analysis,scheduler,controller,rng,tasks]:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p,d in obj.get(field,{}).items():assert sha(p)==d,p
    assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['original_disc'])==build['original_disc_sha256']
    results=route['results'];candidate=results['native19_repaired'];obs=candidate['observation']
    assert obs['native_C_select_calls']>0 and obs['native_dispatch_calls']>0 and obs['native_remove_calls']>0
    assert obs['old_scheduler_steps']==obs['old_remove_steps']==obs['old_task_steps']==obs['old_controller_steps']==obs['old_rng_steps']==obs['old_keypad_steps']==0
    assert obs['native_C_select_calls']<=obs['native_dispatch_calls']+obs['native_remove_calls']
    assert obs['native_dispatch_calls']+obs['native_remove_calls']-obs['native_C_select_calls']<=1
    pins={}
    for n in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=read(ROOT/'verification'/n)
        for p,d in recipe['hashes'].items():assert sha(p)==d,p
        pins[n]=dict(files=len(recipe['hashes']),all_hashes_match=True)
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-scheduler-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshots=out/'snapshots';snapshots.mkdir();deps=dict(previous['dependencies_sha256']);index={};observed={}
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    def pin(p,copy=False):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);relative=str(p.relative_to(ROOT));digest=sha(p)
        if copy:
            dest=snapshots/(hashlib.sha256(relative.encode()).hexdigest()[:12]+'-'+p.name)
            if not dest.exists():shutil.copy2(p,dest)
            assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;index[relative]=dict(snapshot=str(dest.relative_to(ROOT)),sha256=digest)
        else:deps[relative]=digest
    for p in [previous_path,*paths,Path(__file__),ROOT/'native_restoration_evidence.py',ROOT/'assistant_chat.py',ROOT/'scripts/native_chat_team_context.py']:pin(p,True)
    for obj in [build,entry,route,analysis,scheduler,controller,rng,tasks]:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p in obj.get(field,{}):pin(p,True)
    for p in native.iterdir():
        if p.is_file()and(p.suffix in ['.c','.h','.S','.ld']or p.name.startswith('Makefile')):observed[str(p.relative_to(ROOT))]=sha(p);pin(p,True)
    for p in [build['derived_disc'],build['component'],build['linked_component'],build['derived_stage'],build['fixed_runtime_binary']]:pin(p)
    for p in Path(author['directory']).iterdir():
        if p.is_file():pin(p,True)
    for n in ['fixtures.json','native-results.json','trace-results.json','disassembly.txt','symbols.json']:pin(Path(scheduler['directory'])/n)
    for lane in route['lanes']:
        folder=Path(route['directory'])/lane
        for n in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le','original-emulator-final-frame.png','video-final.xrgb8888']:pin(folder/n)
    transcript=Path(author['directory'])/'prompts-and-responses.txt';facts=dict(previous['facts'])
    facts.pop('new_complete_function_entries',None);facts.pop('new_stack_argument_entry_wrappers',None)
    old_authorship=facts.pop('authorship');old_status=facts.pop('model_status_development_case',None)
    task=dict(facts['task_creation']);task.pop('naturally_observed_native_body_entries',None);task.update(naturally_observed_native_ABI_entry_calls=obs['native_task_entries'],entry_counter_symbol='biwn_native_task_create (assembly ABI entry)',GCC_C_body_entry_separately_counted=False,original_task_body_instructions=obs['old_task_steps'])
    native_rows=read(Path(scheduler['directory'])/'native-results.json');simple=next(x for x in native_rows if x['entry']=='0xde08')
    facts.update(status_label='experimental_native19_scheduler_and_scan',entries=19,new_entry_contracts=4,new_C_algorithm_bodies=1,
        entry_count_definition='19 source-backed ABI entry contracts, not19new C functions. This pass adds dispatch/removal handlers sharing one C selection loop and two byte-identical same-address yield/removal trap stubs. Previous native15 components remain.',
        current_result='Separate native19 diagnostic CDI adds target-compiled scheduler selection and source assembly dispatch/removal/yield/trap boundaries. Native15 and native19 both finish fresh merchant→two descents→outdoor clearance→120idleframes. Timing/audio differences remain; full game and physical boot are unproved.',
        resident_bytes=build['component_bytes'],linked_resident_bytes=build['linked_component_bytes'],reserved_bytes=build['heap_bytes_reserved'],task_creation=task,
        scheduler=dict(native_CPU_cases=1664,ordered_pre_RTE_bus_cases=896,original_instruction_coverage=[36,36],entry_case_counts=scheduler['entry_case_counts'],C_select_function_calls=obs['native_C_select_calls'],assembly_dispatch_entry_calls=obs['native_dispatch_calls'],assembly_remove_entry_calls=obs['native_remove_calls'],native_RTE_instruction_hits=obs['native_scheduler_RTEs'],yield_stub_hits=obs['scheduler_yield_entries'],remove_trap_hits=obs['scheduler_remove_traps'],original_dispatch_body_instructions=obs['old_scheduler_steps'],original_remove_body_instructions=obs['old_remove_steps'],source_assembled_same_address_trap_bytes=14,trap_bytes_identical=True,simple_dispatch_cycles_original=simple['original_cycles'],simple_dispatch_cycles_candidate=simple['compiled_cycles'],cycle_scope='One synchronous component fixture including CDI entry JMP; not a game FPS/IRQ/equivalence measurement.',scope=scheduler['scope']),
        matched_state_scope=scheduler['scope'],prior_native15_task_creation_results=facts['repaired_route_results'],repaired_route_results=results,
        native15_deterministic_repeat=dict(full_recorded_rows=analysis['native15_repeat_frames'],different_rows=0,PCM_equal=True),
        final_video_equal=analysis['final_raw_video_equal'],audio=dict(nonzero_samples={k:x['nonzero_audio_samples']for k,x in results.items()},PCM_equal=analysis['final_PCM_equal'],listening_verified=False),
        naturally_observed_controller_calls=obs['controller_entries'],
        authorship=dict(roles=author['roles'],raw_model_C_unchanged=True,manual_C_edits=0,coordinator_supplied_full_algorithm_and_disassembly=True,coordinator_role='Designed frame interface and wrote native assembly ABI/trap/write boundaries, build, execution checks, observer and input-policy harness.',same_27B_weights=True,independent_model_validation=False),
        prior_task_creation_authorship=old_authorship,prior_task_status_development_case=old_status,
        workflow_corrections='Current scheduler C passed unchanged from the first local Author draft. Reviewer returned compact booleans; actual acceptance depends on native CPU/bus/game checks. Coordinator reserved scratch below the original six-byte exception frame to keep that frame outside private RAM exclusion. Future inference labels ABI-entry and GCC-C-body counters separately.',
        remaining='Complete native engine/source modules, full-game link/package and remaining original/provider paths. Scheduler increases component cycle cost; IRQ/concurrency/timing equivalence, all-blocked rings, trace/bus faults and fixed-input whole-game fidelity remain unverified. RNG divisor/scan read limits remain. Physical authenticated boot, listening, native LM Chat rendering/cancellation and future256GB hardware tests remain unverified.',new_training=False,native_Chat=False)
    artifacts=dict(previous['relative_artifact_fields']);artifacts.update(derived_disc=str(Path(build['derived_disc']).relative_to(ROOT)),compiled_binary=str(Path(build['linked_component']).relative_to(ROOT)),proof=str((out/'publication.json').relative_to(ROOT)),canonical_C=str((native/'scheduler-native.c').relative_to(ROOT)),scheduler_assembly=str((native/'scheduler-shims.S').relative_to(ROOT)),exact_author_prompts=str(transcript.relative_to(ROOT)),final_outdoor_PNG=str((Path(route['directory'])/'native19_repaired/original-emulator-final-frame.png').relative_to(ROOT)))
    manifest=dict(schema_version=1,status='published_native_scheduler_with_remaining_limits',recorded_at=now.isoformat(),directory=str(out),facts=facts,relative_artifact_fields=artifacts,dependencies_sha256=deps,source_snapshots=index,observed_game_source_sha256=observed,preview_pins=pins,derived_disc=build['derived_disc'],original_disc_unchanged=True,whole_game_complete=False)
    save(out/'publication.json',manifest);save(ROOT/'verification/native-scheduler-publication-current.json',manifest);shutil.copy2(ROOT/'native_restoration_evidence.py',RT/'native_restoration_evidence.py')
    reveal=ROOT/'scripts/reveal_biwn_native_disc.py';text=reveal.read_text()
    if "'native-scheduler-publication-current.json'"not in text:reveal.write_text(text.replace("'native-task-create-publication-current.json'","'native-scheduler-publication-current.json','native-task-create-publication-current.json'"))
    guide=f'''BLACK ICE WHITE NOISE — NATIVE SCHEDULER DIAGNOSTIC
Updated {now.isoformat()}

The separate diagnostic CDI has19 source-backed ABI entry contracts. The new scheduler dispatch/removal handlers share one locally authored C selection loop. Yield and removal TRAP stubs assemble to the exact14original bytes at DF60/DF7A, preserving saved return PCs. The previous native15 RNG/keypad/controller/task-creation/math components and on-disc marker repair remain. This is a partial native rebuild; most game code and emulator CPU/GPU/DSP/HLE/CD/device providers remain. Entry counts are not a decompilation percentage.

Local Author: {author['roles'][0]['seconds']} seconds. Local Reviewer: {author['roles'][1]['seconds']} seconds, same27B weights. C accepted unchanged from the first draft; no manual C edits or new weight training. Coordinator supplied the complete algorithm/disassembly and private frame design, and wrote assembly boundaries/build/tests/observer. This measures guided translation, not autonomous reverse engineering or independent model review.

NATIVE EXECUTION CHECKS
1,664 full CPU/RAM/exception-frame cases cover dispatch, user TRAP0 yield, task removal and user TRAP2 removal, selected user/supervisor tasks, warm/fresh continuations, full CCR values and unsigned wake times. All36original instruction starts are covered. Separate896Unicorn supervisor prefixes compare ordered public reads/writes with changing deadline/clock rereads before RTE. Actual RTE/USP/SSP behavior is checked by the retained native CPU, not Unicorn. Supervisor scratch below the six-byte exception frame is excluded; that frame itself is compared. No host CPU-state transplant or context-emulation callback.

The same3090-byte linked image passes controller1,216CPU/1,024MMIO, RNG1,682CPU/298access, task creation1,280CPU/1,280access including128empty-pool ILLEGAL cases, startup/heap96 and installed keypad5,151cases.426padding bytes retain3516resident bytes and3520heap reserve. The diagnostic differs from the original in{build['changed_disc_bytes']}CDI bytes; all undeclared bytes/metadata and the original are unchanged. One simple dispatch fixture costs{simple['compiled_cycles']}candidate versus{simple['original_cycles']}original emulated CPU cycles, including the entry JMP. This is a real overhead, not an FPS or IRQ-equivalence result.

FRESH GAMEPLAY
'''
    for lane,x in results.items():guide+=f"{lane}: {x['executed_frames']} frames; merchant reached={x['merchant_reached']}; outdoor120-framehold={x['completed_outdoor_hold']}; final fields={x['final_fields']}; nonzero PCM samples={x['nonzero_audio_samples']}.\n"
    guide+=f'''Both follow real preceding floor2→1→0 transitions and reach outdoor clearance (13056,42400), tolerance8. Native15 repeats all{analysis['native15_repeat_frames']}prior recorded rows and PCM exactly. Native19 naturally executes the GCC C selection entry{obs['native_C_select_calls']}times, dispatch assembly{obs['native_dispatch_calls']}times and removal assembly{obs['native_remove_calls']}times. It executes zero old dispatch/removal/task/controller/RNG/keypad body instructions. The source-assembled trap stubs retain original bytes. Both resident code signatures also remain unchanged at the end. Final raw video equality={analysis['final_raw_video_equal']}; PCM equality={analysis['final_PCM_equal']}. These are feedback-policy routes, not identical fixed-input or whole-game equivalence tests. Fresh CDI/HLE loads, normal pad input and read-only observers only; no checkpoint restore, guest memory/code writes or source execution ownership.

Exact prompts and responses:
{transcript}
C source: {native/'scheduler-native.c'}
Assembly boundaries: {native/'scheduler-shims.S'}
Rebuild: make -f Makefile.scheduler-bundle scheduler-bundle (from native-m68k)
Diagnostic CDI: {build['derived_disc']}
Frozen evidence: {out}
Show BIWN Native Disc.command reveals this diagnostic. Your current preview and P/O112/84pinned files remain unchanged. Click preview; C+Up runs. Arrows move/turn, Z=A, X=B, C=C, P pause, M mute, Esc close.

REMAINING
Full native engine/source link/package, remaining CPU/GPU/DSP/game/provider paths, fixed-input and timing/IRQ fidelity, physical authenticated console boot and audible listening remain unfinished. All-blocked rings, trace and bus faults are outside these scheduler fixtures. Existing RNG zero-divisor and scan-window read limitations remain. Fresh native LM Chat rendering/cancellation and future256GB hardware measurements remain unverified. Advertising daily base/retrieval/copyediting and prior trained/rejected adapters are unchanged; see CURRENT ADVERTISING.txt. The overall goal is incomplete.
'''
    for root,label in [(ROOT,'workspace'),(RT,'installed')]:
        for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(root/name,out/(label+'-previous-'+name))
        (root/'CURRENT DECOMPILATION.txt').write_text(guide)
        (root/'CURRENT LOCAL INFERENCE.txt').write_text('LOCAL AI LAB — CURRENT INFERENCE\nUpdated '+now.isoformat()+'\n\nThe shared27B local model remains loaded through LM Studio as advertising-scholar. Saved game/advertising assistants and visible local team use the same weights sequentially. Native Chat UI rendering/cancellation remains unverified.\n\nCurrent native19 scheduler source: local Author12.21s, Reviewer3.65s; raw C accepted unchanged after native CPU/bus and fresh-game checks. Coordinator supplied algorithm and assembly/test harness. Exact prompts/responses:\n'+str(transcript)+'\n\nThe frozen native19 result is available to the saved game evidence helper on a fresh query. Both native15/native19 complete merchant→two descents→outdoor clearance→120idleframes; cycle/audio/timing differences and full-game/physical-console limits remain. See CURRENT DECOMPILATION.txt. The previous SDK status-answer tests required evidence/prompt corrections and coordinator qualifications; this pass does not prove general model reliability or new native Chat rendering. No weights trained here. Advertising workflows and reviewed teaching example remain described in CURRENT ADVERTISING.txt and ADVERTISING WRITING.txt. Overall goal remains incomplete.\n')
    (native/'README.txt').write_text('NATIVE M68000 PARTIAL SOURCE — SCHEDULER DIAGNOSTIC\nUpdated '+now.isoformat()+'\n\nmake -f Makefile.scheduler-bundle scheduler-bundle BUILD=build-scheduler\n\n19ABIentrycontracts;3090linked bytes+426padding;3520heapreserve. Locally authored C scheduler selection plus coordinator native dispatch/removal boundaries and same-address source TRAP stubs join native15components. Native CPU/bus/exception and fresh-game gates pass with cycle/timing/audio differences; source/original/emulatorproviders remain. Not a whole source-built game or physical-console boot proof.\n\n'+build['derived_disc']+'\n')
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),role='coordinator',action='published reviewed native scheduler diagnostic',publication=str(out/'publication.json'),new_weights_trained=False,whole_game_complete=False))+'\n')
    print(json.dumps(dict(publication=str(out),dependencies=len(deps),source_snapshots=len(index),entries=19,preview_pins=pins)),flush=True)
if __name__=='__main__':main()
