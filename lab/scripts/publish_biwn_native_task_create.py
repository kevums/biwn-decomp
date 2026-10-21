"""Freeze a reviewed native15 diagnostic result; preserve prior publication.

Small source/proof files are snapshots. Large versioned gameplay artifacts
remain hash pinned. This does not change preview profiles or model weights.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    old_path=ROOT/'verification/native-word-scan-publication-current.json';old=read(old_path)
    for rel,d in old['dependencies_sha256'].items():assert sha(ROOT/rel)==d,rel
    bp=ROOT/'verification/native-task-create-disc-build-current.json';build=read(bp)
    ep=ROOT/'verification/native-task-create-disc-entry-current.json';entry=read(ep)
    rp=ROOT/'verification/native-task-create-route-current.json';route=read(rp)
    ap=ROOT/'verification/native-task-create-route-analysis-current.json';analysis=read(ap)
    assert analysis['route_proof_sha256']==sha(rp) and analysis['native13_repeat_full_rows_different']==0 and analysis['native13_repeat_PCM_equal']
    assert all(x['previous_floor']==2 and [t[:2]for t in x['transitions']]==[[2,1],[1,0]]and x['last120_rows_all_outdoor']for x in analysis['results'].values())
    assert entry['status']=='terminal_native_entry_heap_and_component_pass' and entry['build_proof_sha256']==sha(bp)
    assert route['status']=='terminal_fresh_native13_native15_routes_classified' and route['build_proof_sha256']==sha(bp)
    gate_paths=[ROOT/'verification'/n for n in ['native-task-create-bundle-current.json','native-task-bundle-controller-current.json','native-task-bundle-rng-current.json']]
    gates=[read(p)for p in gate_paths];task,controller,rng=gates
    assert task['native_cases']==1280 and task['trace_cases']==1280 and task['empty_pool_exception_cases']==128 and task['source_accepted']
    assert controller['native_cases']==1216 and controller['trace_cases']==1024 and not controller['limit']
    assert rng['cpu_cases']==1682 and rng['trace_cases']==298 and rng['phase']=='both' and not rng['limit']
    assert all(g['compiled_binary_sha256']==build['linked_component_sha256']for g in gates)
    for obj in [build,entry,route,*gates]:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p,d in obj.get(field,{}).items():assert sha(p)==d,p
    assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['original_disc'])==build['original_disc_sha256']
    results=route['results']
    for lane,x in results.items():
        f=x['final_fields'];assert x['merchant_reached']and x['completed_outdoor_hold']and {0,1}<=set(x['return_floor_values'])
        assert f['player_mode_word']==1 and f['floor_word']==0 and f['scene_word']==312
        assert (f['raw_player_X']-13056)**2+(f['raw_player_Z']-42400)**2<=64
    candidate=results['native15_repaired'];obs=candidate['observation']
    assert obs['native_task_entries']>0 and obs['old_task_steps']==0 and obs['task_empty_exceptions']==0
    pins={}
    for n in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        p=read(ROOT/'verification'/n)
        for f,d in p['hashes'].items():assert sha(f)==d,f
        pins[n]=dict(files=len(p['hashes']),all_hashes_match=True)
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-task-create-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    snapshots=out/'snapshots';snapshots.mkdir();deps=dict(old['dependencies_sha256']);index={};observed={}
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    def pin(p,copy=False):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);rel=str(p.relative_to(ROOT));d=sha(p)
        if copy:
            dest=snapshots/(hashlib.sha256(rel.encode()).hexdigest()[:12]+'-'+p.name)
            if not dest.exists():shutil.copy2(p,dest)
            assert sha(dest)==d
            deps[str(dest.relative_to(ROOT))]=d;index[rel]=dict(snapshot=str(dest.relative_to(ROOT)),sha256=d)
        else:deps[rel]=d
    for p in [old_path,bp,ep,rp,ap,*gate_paths,Path(__file__),ROOT/'native_restoration_evidence.py',ROOT/'assistant_chat.py',ROOT/'chat_tools.py',ROOT/'scripts/native_chat_team_context.py',ROOT/'verification/local-native-task-create-current.json',ROOT/'verification/local-native-task-create-repair-current.json']:
        pin(p,True)
    for obj in [build,entry,route,*gates]:
        for field in ['source_sha256','execution_dependencies_sha256']:
            for p in obj.get(field,{}):pin(p,True)
    # These are reviewed canonical build inputs, not a claim about all hosted C.
    for p in native.iterdir():
        if p.is_file()and(p.suffix in ['.c','.h','.S','.ld']or p.name.startswith('Makefile')):
            observed[str(p.relative_to(ROOT))]=sha(p);pin(p,True)
    for p in [build['derived_disc'],build['component'],build['linked_component'],build['fixed_runtime_binary'],build['derived_stage']]:pin(p)
    author=read(ROOT/'verification/local-native-task-create-current.json');repair=read(ROOT/'verification/local-native-task-create-repair-current.json')
    transcript=out/'task-creation-prompts-and-responses.txt'
    transcript.write_text((Path(author['directory'])/'prompts-and-responses.txt').read_text()+'\nTARGETED REPAIR\n'+(Path(repair['directory'])/'prompts-and-responses.txt').read_text());pin(transcript)
    for directory in [author['directory'],repair['directory']]:
        for p in Path(directory).iterdir():
            if p.is_file():pin(p,True)
    for p in [Path(task['directory'])/'fixtures.json',Path(task['directory'])/'native-results.json',Path(task['directory'])/'trace-results.json',Path(task['directory'])/'disassembly.txt']:pin(p,True)
    for lane in route['lanes']:
        folder=Path(route['directory'])/lane
        for n in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le','original-emulator-final-frame.png','video-final.xrgb8888']:pin(folder/n)
    folder=Path(route['directory'])/'native15_repaired';control_folder=Path(route['directory'])/'native13_repaired'
    facts=dict(old['facts'])
    facts.update(status_label='experimental_native15_task_creation_and_scan',entries=15,new_complete_function_entries=1,new_stack_argument_entry_wrappers=1,new_entry_contracts=2,
        current_result='A separate diagnostic CDI adds target-compiled C task creation and a source assembly stack-argument entry to the native13+scan image. Native15 and native13 comparison both complete fresh merchant, two descents, outdoor clearance and120idleframes. This is a partial native rebuild, not the whole game.',
        linked_resident_bytes=build['linked_component_bytes'],resident_bytes=build['component_bytes'],reserved_bytes=build['heap_bytes_reserved'],
        task_creation=dict(C_bodies=1,entry_contracts=2,stack_argument_wrappers=1,native_CPU_cases=1280,ordered_bus_cases=1280,empty_pool_exception_cases=128,original_ILLEGAL_PC='0xDEB4',exception_behavior='128 isolated empty-pool CPU fixtures preserve the original ILLEGAL instruction at0xDEB4 and its exception frame. Zero empty-pool exceptions occurred during the game route.',naturally_observed_native_body_entries=obs['native_task_entries'],original_task_body_instructions=obs['old_task_steps'],empty_pool_exceptions_during_route=obs['task_empty_exceptions'],standalone_binary_bytes=216,scope=task['scope']),
        matched_state_scope=task['scope'],repaired_route_results=results,
        prior_original_vs_native13_repair_results=old['facts']['repaired_route_results'],
        native13_deterministic_repeat=dict(full_recorded_rows=24979,different_rows=0,PCM_equal=True),
        final_video_equal=sha(folder/'video-final.xrgb8888')==sha(control_folder/'video-final.xrgb8888'),
        audio=dict(nonzero_samples={k:v['nonzero_audio_samples']for k,v in results.items()},PCM_equal=sha(folder/'frontend-PCM.s16le')==sha(control_folder/'frontend-PCM.s16le'),listening_verified=False),
        naturally_observed_controller_calls=obs['controller_entries'],
        authorship=dict(roles=[dict(role='local Author',seconds=author['roles'][0]['seconds'],result='Wrote initial C; rejected by native CPU gate.'),dict(role='local Reviewer',seconds=author['roles'][1]['seconds'],result='Truncated unusable review; did not repair code.'),dict(role='local Repairer',seconds=repair['seconds'],result='Applied exactly two coordinator-diagnosed C edits. Accepted C is unchanged from this response.')],repair_role='local Repairer',coordinator_role='Supplied full algorithm/disassembly, diagnosed two errors, and wrote wrapper/build/tests/observer.',same_27B_weights=True,independent_model_validation=False,coordinator_supplied_algorithm_and_ABI=True,raw_author_rejected_by_native_CPU=True,raw_reviewer_truncated_unusable=True,model_repair_applied_exactly_two_coordinator_edits=True,manual_C_edits=0),
        workflow_corrections='Author incorrectly truncated address-register comparison to16bits and omitted current_out on empty pool. Native gate rejected it; guided local repair made exactly two edits. Reviewer was truncated and not accepted. A premature host preflight reused rejected raw source; checker now requires terminal repair proof. No new weights or native Chat UI observation.',
        execution_scope='Fresh CDI/HLE loads, ordinary pad inputs, read-only observers returning0. No checkpoint restore, host guest RAM/code writes, CPU reseed or execution ownership. Retained game/emulatorCPU/GPU/DSP/HLE/CD/device providers remain.',
        remaining='Full native game engine/source link and remaining modules/providers; timing, actor/audio and fixed-input fidelity. Empty-pool exception is component-verified; interrupts/concurrent mutation/bus faults are not. Scan read limits remain. Full-game equivalence, physical authenticated boot, listening, fresh native Chat rendering/cancellation and future hardware benchmarks remain unverified.',
        native_Chat=False,new_training=False,
        entry_count_definition='15 source-backed ABI entry contracts, not15 newly decompiled C functions. This pass adds one C task-creation body and one assembly stack-argument wrapper; both route through the same body.',
        model_status_development_case='First installed three-role SDK status response copied the same draft three times, misattributed repair to Reviewer and called body+wrapper two complete functions. Rejected. Evidence metadata clarified; this is a development correction, not held-out model validation.')
    artifacts=dict(old['relative_artifact_fields'])
    artifacts.update(derived_disc=str(Path(build['derived_disc']).relative_to(ROOT)),compiled_binary=str(Path(build['linked_component']).relative_to(ROOT)),proof=str((out/'publication.json').relative_to(ROOT)),canonical_C=str((native/'task-create-native.c').relative_to(ROOT)),exact_author_prompts=str(transcript.relative_to(ROOT)),final_outdoor_PNG=str((folder/'original-emulator-final-frame.png').relative_to(ROOT)))
    manifest=dict(schema_version=1,status='published_native_task_creation_with_remaining_limits',recorded_at=now.isoformat(),directory=str(out),facts=facts,relative_artifact_fields=artifacts,dependencies_sha256=deps,source_snapshots=index,observed_game_source_sha256=observed,preview_pins=pins,derived_disc=build['derived_disc'],original_disc_unchanged=True,whole_game_complete=False)
    save(out/'publication.json',manifest);save(ROOT/'verification/native-task-create-publication-current.json',manifest)
    shutil.copy2(ROOT/'native_restoration_evidence.py',RT/'native_restoration_evidence.py')
    reveal=ROOT/'scripts/reveal_biwn_native_disc.py';s=reveal.read_text()
    if "'native-task-create-publication-current.json'"not in s:s=s.replace("'native-word-scan-publication-current.json'","'native-task-create-publication-current.json','native-word-scan-publication-current.json'");reveal.write_text(s)
    guide=f'''BLACK ICE WHITE NOISE — NATIVE TASK CREATION DIAGNOSTIC
Updated {now.isoformat()}

The separate diagnostic image now has15 source-backed entry contracts:8 C RNG entries, C keypad, C controller scan, C task creation, its source assembly stack-argument entry and3 source-assembled arithmetic helpers. It retains the exact18-byte/14-changed-byte on-disc marker scan repair. This is a partial native rebuild. Most original game code and retained emulator CPU/GPU/DSP/HLE/CD/device providers remain. Entry counts are not a completion percentage.

Task creation removes one free task, links it after the current task, initializes callback/parameter/stack/readiness fields, and preserves original rereads. The native wrapper restores all original register/CCR effects. An empty pool branches to original DEB4 ILLEGAL, preserving its exception PC and frame. Full native CPU/register/PC/SR/USP/SSP and public RAM match in1,280cases; separate ordered public memory access tests also pass1,280cases, including controlled rereads.128native cases exercise empty-pool exceptions. Private working stack/new code are excluded from RAM identity, but exception frames are explicitly compared. Interrupts, concurrent mutation and bus-error equivalence are untested.

The relinked2910-byte resident binary passes the existing controller1,216CPU/1,024ordered-MMIO and RNG1,682CPU/298ordered-access gates. It is padded by606bytes to3516, retaining the3520-byte heap reservation and original startup copy length.96entry/heap cases and5,151installed keypad ABI cases pass. Original CDI and every undeclared disc byte/track metadata are unchanged; diagnostic differs in{build['changed_disc_bytes']}CDI bytes, including native layout and the existing scan repair.

FRESH GAMEPLAY COMPARISON
'''
    for lane,x in results.items():guide+=f"{lane}: {x['executed_frames']}frames; merchant={x['merchant_reached']}; floor2→1→0, outdoor clearance and120idleframes={x['completed_outdoor_hold']}; final={x['final_fields']}; nonzero PCM samples={x['nonzero_audio_samples']}.\n"
    guide+=f'''Native task creation executes naturally {obs['native_task_entries']}times. It executes zero original task/controller/RNG/keypad body instructions. No empty-pool exception occurred on the route. Ordinary fresh CDI/HLE loads and pad inputs only; no checkpoint restore, host guest writes, CPU reseed or source execution ownership. Native13/native15 final raw video equality={facts['final_video_equal']}; PCM equality={facts['audio']['PCM_equal']}. This does not prove whole-game, per-frame or physical-console equivalence. Earlier original-vs-native13 scan results remain in the frozen prior publication.

WHO DID WHAT
Local Author19.71s produced raw C; native CPU rejected a wrong16-bit address comparison and missing empty-pool private output. Local Reviewer24.51s produced a truncated, unusable review. Local Repairer19.28s applied exactly two coordinator-specified edits; accepted C contains no manual edits. All roles share the same27B model. Coordinator supplied algorithm/disassembly and wrote ABI/exception wrapper, build, tests and route observer. These results do not measure autonomous reverse engineering or independent model review. One premature host preflight selected rejected raw C; selector now requires the finished repair proof. All failed records remain.
Exact prompts/responses: {transcript}
Canonical C: {native/'task-create-native.c'}
Build: make -f Makefile.task-create-bundle task-bundle (from native-m68k directory)
Diagnostic CDI: {build['derived_disc']}
Frozen proof/source snapshots: {out}
Show BIWN Native Disc.command reveals this diagnostic. Your running preview and P/O112/84pins are preserved. Click preview; hold C+Up to run. Arrows move/turn, Z=A, X=B, C=C, P pause, M mute, Esc close.

LIMITS / NEXT
Continue actual source/native engine modules, full-game linking and provider replacement. Timing, actor/audio and fixed-input fidelity remain open. RNG zero-divisor behavior and scan reads across the input-window end retain earlier limits. Physical/authenticated console boot, audible listening, full-game equivalence and new native LM Chat rendering/cancellation remain unverified. No model weights were trained during this task-creation pass. Advertising base/retrieval remains installed; see CURRENT ADVERTISING.txt for rejected unattended teaching runs and the reviewed241-word example. The full goal remains incomplete.
'''
    for root,label in [(ROOT,'workspace'),(RT,'installed')]:
        for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(root/name,out/(label+'-previous-'+name))
        (root/'CURRENT DECOMPILATION.txt').write_text(guide)
        (root/'CURRENT LOCAL INFERENCE.txt').write_text('LOCAL AI LAB — CURRENT INFERENCE\nUpdated '+now.isoformat()+'\n\nLM Studio runs the shared27B local model (advertising-scholar). Game and advertising roles run sequentially on the same weights. Fresh native Chat UI rendering/cancellation is not verified. Native helper reads the frozen native15 task-creation+scan result on a new game source/status turn.\n\nTask-creation Author19.71s, Reviewer24.51s (truncated/rejected), targeted Repairer19.28s. Exact prompts/responses:\n'+str(transcript)+'\n\nThe new diagnostic CDI is partial; task CPU/bus and relinked controller/RNG gates pass. Both native13/native15 fresh routes reach merchant, descend twice and hold outdoors120frames. Native task execution observed; details and differences in CURRENT DECOMPILATION.txt. Your preview remains unchanged; C+Up runs.\n\nAdvertising research/education and two-pass copyediting remain available. CURRENT ADVERTISING.txt and ADVERTISING WRITING.txt describe practical limits and the reviewed241-word teaching example. No new weights were trained in this pass. Full game/native rebuild and overall goal remain incomplete.\n')
    (native/'README.txt').write_text('NATIVE M68000 PARTIAL SOURCE — TASK CREATION DIAGNOSTIC\nUpdated '+now.isoformat()+'\n\nmake -f Makefile.task-create-bundle task-bundle BUILD=build-task-creation\n\n15entry contracts,2910linked bytes+606padding;3520heap reserve. C task creation plus assembly stack entry joins8C RNG,C keypad,C controller and3same-address arithmetic assembly helpers. Separate on-disc18byte marker scan repair remains. See CURRENT DECOMPILATION.txt for native CPU/bus/exception and fresh gameplay evidence, exact model prompts and limits. Original/emulator providers remain; not a full game rebuild or physical console proof.\n\n'+build['derived_disc']+'\n')
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),role='coordinator',action='published reviewed native task-creation diagnostic',publication=str(out/'publication.json'),new_training=False,whole_game_complete=False))+'\n')
    print(json.dumps(dict(publication=str(out),dependencies=len(deps),source_snapshots=len(index),facts=facts['status_label'],entries=15,preview_pins=pins)),flush=True)
if __name__=='__main__':main()
