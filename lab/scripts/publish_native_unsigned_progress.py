"""Publish exact binary evidence and current status; goal remains incomplete."""
import datetime,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc);out=ROOT/'verification/native-unsigned-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
parent_path=ROOT/'verification/native-string-ccr-publication-current.json';parent=read(parent_path)
checks={
 'standalone':ROOT/'verification/native-unsigned-division-current.json',
 'linked':ROOT/'verification/native-unsigned-division-linked-current.json',
 'bundle':ROOT/'verification/native-unsigned-bundle-current.json',
 'disc':ROOT/'verification/native-unsigned-format-disc-build-current.json',
 'integration':ROOT/'verification/native-unsigned-format-integration-current.json',
 'pad':ROOT/'verification/native-unsigned-format-pad-current.json',
 'string':ROOT/'verification/native-unsigned-format-string-current.json',
 'callers':ROOT/'verification/native-unsigned-format-callers-current.json',
 'deck':ROOT/'verification/native-unsigned-math-selector-deck-pair-current.json',
 'route':ROOT/'verification/native-unsigned-format-long-route-current.json',
 'route_analysis':ROOT/'verification/native-unsigned-route-analysis-current.json',
 'Author':ROOT/'verification/native-unsigned-local-author-current.json',
 'Author_review':ROOT/'verification/native-unsigned-local-author-reviewed-current.json',
 'negative':ROOT/'verification/native-unsigned-division-bad-X-active.json'}
r={k:read(p) for k,p in checks.items()};bundle=r['bundle'];disc=r['disc'];route=r['route'];deck=r['deck'];author=r['Author']
assert bundle['binary_bytes']==8956 and bundle['existing_prefix_bytes_exact']==8482 and bundle['reserved_bytes']==9216 and bundle['heap_start']==0x1611c0
for key in ['standalone','linked']:
 assert r[key]['native_cases']==r[key]['ordered_cases']==3592 and r[key]['zero_cases']==512 and r[key]['original_instruction_addresses']==43
 assert r[key]['status']=='terminal_native_unsigned_full_CPU_public_accesses_zero_fault_pass'
assert r['negative']['status']=='terminal_failed' and "'CPU'" in r['negative']['error']
assert len(r['integration']['full_gates'])==19 and all(r['integration']['jobs'][k]['status']=='terminal_pass' for k in r['integration']['full_gates'])
assert r['pad']['native_cases']==1668 and r['pad']['changing_read_cases']==16
assert r['string']['native_cases']==1945 and r['string']['changing_read_cases']==16
assert r['callers']['native_cases']==r['callers']['ordered_cases']==1654 and r['callers']['helper_returns']==24421
assert r['callers']['helper_entry_counts']=={'0x1b160':5140,'0xe67c':9630,'0xe61c':9630,'0x1b1a8':21}
a=deck['observations']['candidate'];assert a['compiled_unsigned_calls']==a['unsigned_returns']==[1228,1228] and a['old_unsigned_body_steps']==a['unsigned_stack_outside']==[0,0] and a['unsigned_tracking_errors']==a['unsigned_pending_at_finish']==0
assert r['route_analysis']['route_complete_both'] and not r['route_analysis']['raw_PCM_equal']
assert route['results']['parent']['executed_frames']==29791 and route['results']['unsigned']['executed_frames']==24958
assert r['Author_review']['accepted'] is False and r['Author_review']['compile_or_CPU_gate_run'] is False
original=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(original)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
patches=read(disc['patch_manifest'])['patches'];redirects=sum(bytes.fromhex(p['replacement']).startswith(b'\x4e\xf9') and bundle['base']<=int.from_bytes(bytes.fromhex(p['replacement'])[2:6],'big')<bundle['base']+bundle['binary_bytes'] for p in patches)
assert redirects==27
report=ROOT/'reports/native-unsigned-arithmetic-restoration.txt';native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
summary=('Latest mixed original/new Jaguar CD experiment uses an8956byte resident payload in the unchanged9216byte reservation. Two new coordinator-written C unsigned arithmetic entries passed3592native/ordered cases and512zero-divisor cases, covering all43original instruction addresses with declared fault-PC relocation. Exact-linked checks,1654formatter callers and19install/resource gates passed. A separate2600frame repaired Deck run observed1228completed calls to each new helper without stack violations. Both fresh adaptive merchant/floor0/outdoor routes completed: parent29791frames,new24958. Player/video and movie/audio records differ; the shorter route is not a speedup or frame-equivalence result. Prior8482payload bytes remain exact. The local Author\'s incomplete C was rejected. Original engine/emulator/firmware/device providers remain; full source recovery,interrupt/timing equivalence,physical-console boot and audio quality are unverified. No preview or weight promotion.')
helper_keys=['status','native_cases','ordered_cases','changing_read_cases','original_instruction_coverage','scope']
current=dict(project='Black Ice White Noise, Atari Jaguar CD',status='terminal_unsigned_arithmetic_bundle_and_finite_gameplay_published',recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,proof=str(ROOT/'verification/native-unsigned-publication-current.json'),report=str(report),
 experimental_build=dict(compiled_binary=bundle['binary'],binary_sha256=bundle['binary_sha256'],resident_bytes=8956,reserved_bytes=9216,heap_start=bundle['heap_start'],derived_disc=disc['derived_disc'],derived_disc_sha256=disc['derived_disc_sha256'],declared_resident_redirects=redirects,redirect_count_scope='Stage JMP redirects, not recovered-function total or completion percentage.',source_origin='New unsigned arithmetic C/ABI is coordinator-authored. Exact8482byte prefix retains its previous source attribution.'),
 unsigned_source=str(native/'unsigned-division-native.c'),unsigned_original_entries=['0xE61C quotient/remainder','0xE67C remainder wrapper'],
 helper_gates={**{k:{a:v for a,v in r[k].items() if a in helper_keys} for k in ['pad','string']},'unsigned':dict(native_cases=3592,ordered_cases=3592,zero_divisor_cases=512,original_instruction_coverage=[43,43],linked_tail_retested=True,source_accepted=True,scope=r['linked']['scope']),'callers':{k:r['callers'][k] for k in ['native_cases','ordered_cases','helper_returns','helper_entry_counts','scope']}},
 scoped_install_component_resource_full_gates=r['integration']['full_gates'],
 repaired_Deck=dict(frames_per_lane=2600,compiled_unsigned_calls=a['compiled_unsigned_calls'],unsigned_returns=a['unsigned_returns'],old_unsigned_body_steps=a['old_unsigned_body_steps'],task_stack_violations=a['unsigned_stack_outside'],minimum_task_stack_headroom_bytes=a['unsigned_min_headroom'],pending_at_finish=a['unsigned_pending_at_finish'],tracking_errors=a['unsigned_tracking_errors'],comparisons=deck['comparisons'],scope='Same two declared selector/count repairs in both discs, same fixed ordinary pad schedule. Control restores only unsigned redirects; payload/heap/pad/string identical. Finite frame records differ.'),
 long_route=dict(parent_frames=29791,unsigned_frames=24958,frame_difference_new_minus_parent=-4833,both_merchant_reached=True,both_returned_floor0_and_completed_outdoor_hold=True,parent_nonzero_audio_samples=route['results']['parent']['nonzero_audio_samples'],unsigned_nonzero_audio_samples=route['results']['unsigned']['nonzero_audio_samples'],raw_PCM_equal=False,same_adaptive_policy_not_identical_inputs=True,scope='Both raw experimental discs, no shared selector repairs. Different late movie-flag intervals and audio. No fixed-input, whole-state or speedup claim.'),
 local_inference_example=dict(role='Author',seconds=author['seconds'],accepted=False,reason='Incomplete C at output limit; no compilation or CPU gate run.',prompts_and_responses=str(Path(author['directory'])/'prompts-and-responses.txt'),native_Chat_verified=False),
 prior_isolated_string_cost=dict(**parent['current_status']['sampled_string_cost'],reuse_scope='Inherited prior isolated test; string code and all8482prefix bytes are exact. Not a new whole-game benchmark.'),
 job_status_scope='Published finite tests are terminal; unrelated processes are not scanned.',this_lookup_executes_game_tests=False,this_lookup_invokes_model_or_training=False,new_training=False,default_promoted=False,whole_game_complete=False,goal_complete=False,physical_console_verified=False,whole_game_speedup_demonstrated=False,physical_audio_or_quality_verified=False,
 remaining=['Full source reconstruction and rebuild of remaining original engine code','IRQ/timing and arbitrary aliasing/exception-handler behavior beyond scoped fixtures','Whole-game content/behavior preservation and complete source-owned console runtime','Physical Jaguar CD boot/performance/audio verification','Reliable local source-generation and advertising training quality gains'],available_evidence_topics=parent['current_status']['available_evidence_topics'])
report.write_text(f'''BIWN unsigned arithmetic source restoration - {now.isoformat()}

Two additional original arithmetic entry contracts now have native C implementations: E61C unsigned quotient/remainder and E67C remainder wrapper. The new code is coordinator-authored, not accepted local-model output:
{native/'unsigned-division-native.c'}
The shared C numerical body has no original arithmetic calls or runtime CPU decoder. The assembly captures/restores registers and executes a new DIVU-by-zero path. Stable stack arguments are an explicit ABI premise.

Complete isolated evidence
Standalone and exact relocated474byte tail each passed3592normal native-CPU cases,3592ordered public-access comparisons and512divide-by-zero cases. All43original instruction addresses were reached. Full D/A,PC,SR,USP,SSP and public RAM match, including E67C public pushes and savedE686read. Candidate-private C stack is excluded; original accesses there are rejected on normal traces. A declared inert RTE handler handles zero faults; trap CPU/savedSR and final CPU match with expected saved-fault-PC relocation. Arbitrary handlers,asynchronous stack mutation,IRQ timing and physical console remain unproved.
A deliberate X-flag mutation failed normalcase4 with expectedSR8 versus actualSR24. This negative control was not installed.

Compiled mixed build
{disc['derived_disc']}
Payload8956bytes; reservation9216; padding260; heapstart0x1611C0; temporary staging remains12288bytes atFB000..FE000. All prior8482payload bytes and symbols remain exact. Two new stage redirects yield27total stageJMPredirects, not a recovered-function total or decompilation percentage. OriginalCDI and defaultpreview are unchanged.
Exact new linked pad1668native/ordered+16changing, string1945native/ordered+16changing, formatter/callers1654native/ordered with24421outer helper returns (5140pad,21string,9630unsignedquotient,9630unsignedremainder) pass. Original remainder's nested quotient is observed at the outer helper boundary because compiled C shares a C body; each direct entry is separately covered by its full matrix.
All19 installation/component/resource gates pass on the exact8956byte payload, including96startup/5151installed key ABI cases and heap,resource,lifecycle,readiness checks. Their individual scope limits remain; this does not recover the original formatter core or whole engine.

Fresh finite gameplay
The2600frame same-input repaired Deck pair differs only in the two arithmetic redirects (11actual changedCDIbytes across12declared redirect bytes). Both share the same38declared-byte selector/count repair. Candidate observed1228calls and1228returns for each new entry,zero original unsigned body instructions,zero task-stack violations,zero tracking errors/pending calls; minimum observed headroom532/492bytes. Position/video records differ and mode differs on one frame. No frame-equivalence claim.
Both separate raw-disc adaptive merchant/floor0/outdoor routes complete. Parent:29791frames and7324788nonzero captured samples. New:24958frames and1609492samples. Final selected player/scene fields agree, but positions/video/movie-flag intervals and PCM differ. In particular, the parent's long late movie/audio sequence does not occur in the new route. The4833fewerframes do not demonstrate speedup; same adaptive policy is not the same recorded input stream, and the cause of this content/timing divergence is not isolated by this run. Audio quality/physicalaudibility remain unverified.

Local model output test
The local27B6bit Author received all43original instruction records plus the native ABI contract in a fresh SDK context. It took{author['seconds']:.2f}seconds and reached its3500token output limit while still inside the first required function. It misread the stack high-word test as a low-word test, used a32bit instead of16bit volatile read, and placed remainder-wrapper pushes in the quotient zero path. The incomplete raw candidate was rejected before compilation; it was not repaired or installed.
Exact model prompts/responses: {Path(author['directory'])/'prompts-and-responses.txt'}
Deterministic compiler/tests are not LLM agents. No cloud subagents, training updates, accepted new model-written C or native Chat generation occurred in this source step.

Rebuild the same payload from this workspace
Working directory: {native}
make -f {Path(bundle['directory'])/'Makefile'} format-bundle BUILD=/tmp/biwn-unsigned-rebuild
Standalone new arithmetic: make -f Makefile.unsigned-division unsigned-division BUILD=/tmp/biwn-unsigned-standalone
The original formatter/engine, other original routines, retained emulator,HLE firmware/device providers and physical-console limitations remain. The current status shortcut is being connected to this publication; its local Reader validation is recorded separately after publication. No default preview or weights are promoted. Full goal remains incomplete.
''')
# Merge the parent's GAME evidence only, not mutable UI settings/status readers.
core=dict(parent['status_dependencies_sha256']);files=set(checks.values())|{parent_path,Path(__file__),original,report}
for name,h in list(core.items()):assert sha(name)==h,name
for key,obj in r.items():
 for field in ['source_sha256','dependencies_sha256','artifacts_sha256','execution_dependencies_sha256']:
  table=obj.get(field,{})
  if isinstance(table,dict):
   for p,h in table.items():
    if isinstance(p,str) and Path(p).is_absolute() and isinstance(h,str):assert sha(p)==h,p;files.add(Path(p))
 directory=obj.get('directory')
 if directory:
  files.update(p for p in Path(directory).rglob('*') if p.is_file())
# Direct component gate snapshots retain the actual test hashes/scope.
for job in r['integration']['jobs'].values():
 if job.get('proof'):files.add(Path(job['proof']))
for p in files:
 p=p.resolve();assert p.is_relative_to(ROOT),p;core[str(p)]=sha(p)
# Report/UI may gain a separately recorded Reader followup; game core is immutable.
core.pop(str(report.resolve()),None)
for p in [native/'unsigned-division-native.c',native/'unsigned-division-native.h',native/'unsigned-division-shim.S',native/'unsigned-division.ld',native/'Makefile.unsigned-division']:
 (out/p.name).write_bytes(p.read_bytes())
state=dict(status=current['status'],recorded_at=now.isoformat(),directory=str(out),report=str(report),binary_sha256=bundle['binary_sha256'],linked_bytes=8956,reserved_bytes=9216,heap_start=bundle['heap_start'],derived_disc=disc['derived_disc'],derived_disc_sha256=disc['derived_disc_sha256'],declared_resident_redirects=27,current_status=current,status_dependencies_sha256=core,dependencies_sha256={**core,str(report):sha(report)},new_training=False,default_promoted=False,goal_complete=False,proofs={k:str(p) for k,p in checks.items()},parent_gameplay_publication=str(parent_path))
save(out/'publication.json',state);save(ROOT/'verification/native-unsigned-publication-current.json',state)
ledgerp=ROOT/'verification/goal-continuation-current.json';ledger=read(ledgerp);save(out/'goal-continuation-before.json',ledger);ledger.update(status='active_two_new_native_unsigned_entries_verified_finite_gameplay_diverges_goal_incomplete',recorded_at=now.isoformat(),goal_complete=False,previous_goal_turn_classification='progress',current_goal_turn_progress='Two new coordinator C arithmetic entries pass3592normal/ordered+512zero cases and43/43source addresses; exact8956byte bundle,1654callers/24421returns,19gates andfreshDeck/routes pass within scopes. Gameplay/audio differ; no speedup/frame-equivalence/default promotion. LocalAuthor incompleteC rejected.',current_goal_turn_evidence=str(ROOT/'verification/native-unsigned-publication-current.json'),latest_native_unsigned_publication=str(ROOT/'verification/native-unsigned-publication-current.json'),latest_experimental_disc=disc['derived_disc'],latest_finite_jobs_running=False,latest_finite_job_status='All isolated,linked,caller,component,Deck andlong-route jobs terminal. Current status Reader verification follows publication.',new_training=False)
save(ledgerp,ledger)
with (ROOT/'runs/agent-work-audit.jsonl').open('a') as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),role='Codex coordinator',action='native unsigned arithmetic recovery and scoped execution publication',publication=str(ROOT/'verification/native-unsigned-publication-current.json'),new_training=False,goal_complete=False))+'\n')
assert all(sha(p)==h for p,h in core.items())
print(json.dumps(dict(status=state['status'],report=str(report),linked_bytes=8956,stage_redirects=27,core_files=len(core),integrity_mismatches=0,goal_complete=False),indent=2))
