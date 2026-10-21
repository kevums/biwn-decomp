"""Publish current exact-layout number recovery; retain each proof's scope."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-number-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 names=dict(standalone='native-format-number',linked='native-number-format-number',math='native-number-format-math-linked',pad='native-number-format-pad',string='native-number-format-string',callers='native-number-format-callers',integration='native-number-format-integration',bundle='native-number-format-bundle',disc='native-number-format-disc-build',deck='native-number-entry-selector-deck-pair',routes='native-number-format-long-route',negative='native-format-number-negative',lowering='native-format-number-lowering',preparation='native-number-format-preparation',gameplay_preparation='native-number-gameplay-preparation')
 paths={k:ROOT/'verification'/(v+'-current.json')for k,v in names.items()};r={k:read(p)for k,p in paths.items()}
 b=r['bundle'];disc=r['disc'];deck=r['deck'];routes=r['routes'];native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 assert(b['binary_bytes'],b['reserved_bytes'],b['heap_start'])==(11224,11264,0x1619c0)
 assert sha(b['binary'])==b['binary_sha256'] and sha(disc['derived_disc'])==disc['derived_disc_sha256']
 for kind in ['standalone','linked']:
  p=r[kind];assert p['source_accepted'] and (p['native_cases'],p['ordered_cases'],p['zero_cases'],p['original_instruction_coverage'])==(1196,1196,256,[50,50])
 assert r['linked']['binary_sha256']==b['binary_sha256']
 assert(r['math']['native_cases'],r['math']['ordered_cases'],r['math']['zero_cases'])==(3592,3592,512)
 for kind,count in [('pad',1668),('string',1945)]:assert(r[kind]['native_cases'],r[kind]['ordered_cases'],r[kind]['changing_read_cases'])==(count,count,16)and r[kind]['binary_sha256']==b['binary_sha256']
 assert(r['callers']['native_cases'],r['callers']['ordered_cases'],r['callers']['helper_returns'])==(1654,1654,8815)
 assert r['callers']['helper_entry_counts']=={'0x1b160':5140,'0x1b212':3654,'0x1b1a8':21}
 assert len(r['integration']['full_gates'])==19
 assert all(r['integration']['jobs'][k]['status']=='terminal_pass'for k in r['integration']['full_gates'])
 a=deck['observations']['candidate'];control=deck['observations']['control']
 assert a['number_entries']==a['compiled_number_calls']==a['number_returns']==[445]
 assert a['old_number_body_steps']==a['number_stack_outside']==[0] and a['number_tracking_errors']==a['number_pending_at_finish']==0
 assert a['number_min_headroom']==[444]
 assert control['compiled_number_calls']==[0] and control['number_returns']==control['number_entries']==[837]
 assert routes['status']=='terminal_fresh_base_optimized_adaptive_routes_classified'
 for lane in ['parent','number']:
  result=routes['results'][lane];assert result['merchant_reached'] and result['completed_outdoor_hold'] and result['return_floor_values']==[0,1]
 assert r['negative']['status']=='terminal_deliberate_wrong_return_rejected'
 patches=read(disc['patch_manifest'])['patches'];redirects=sum(bytes.fromhex(p['replacement']).startswith(b'\x4e\xf9')and b['base']<=int.from_bytes(bytes.fromhex(p['replacement'])[2:6],'big')<b['base']+b['binary_bytes']for p in patches);assert redirects==28
 parentp=ROOT/'verification/native-unsigned-publication-current.json';parent=read(parentp)
 report=ROOT/'reports/native-number-restoration.txt'
 summary=('Latest BIWN mixed original/new Jaguar CD experiment has an11,224byte native resident payload with11,264bytes reserved and heapstart0x1619C0. The new number-to-text C routine passed1,196normal CPU/ordered-access cases,256zero-divisor cases and all50original instruction addresses; complete formatter callers matched3,654number returns. All19installation/component/resource gates passed on this exact new layout. A2,600frame repaired Deck comparison observed445compiled number calls/returns,zero original number-body instructions or task-stack violations,and444bytes minimum observed headroom. Both raw-disc adaptive merchant/floor0/outdoor routes complete: parent24,958frames,new24,974. Position,video and audio records differ; no speedup or frame-equivalence result. This is coordinator-generated source-specific C,not accepted model-authored C or original source. Original engine/emulator/firmware/device providers remain. Full decompilation,complete source console rebuild,IRQ timing,physical boot and audio quality remain unverified. No default preview or model-weight promotion.')
 current=dict(project='Black Ice White Noise, Atari Jaguar CD',status='terminal_native_number_bundle_and_finite_gameplay_published',recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,proof=str(ROOT/'verification/native-number-publication-current.json'),report=str(report),
  experimental_build=dict(compiled_binary=b['binary'],binary_sha256=b['binary_sha256'],resident_bytes=b['binary_bytes'],reserved_bytes=b['reserved_bytes'],heap_start=b['heap_start'],derived_disc=disc['derived_disc'],derived_disc_sha256=disc['derived_disc_sha256'],declared_resident_redirects=redirects,redirect_count_scope='StageJMP redirects, not recovered-function count/completion percentage.',source_origin='Coordinator deterministic lowering of pinned recovered instruction semantics; arithmetic C inherited. New source is not local-model-authored.',previous_prefix_change_count=len(b['previous_prefix_changes']),previous_prefix_change_scope='Seven byte changes in heap-address literals; heapstart moves2048bytes. Previous function symbols retained; full exact-layout matrices rerun.'),
  number_source=str(native/'format-number-native.c'),number_original_entry='0x1B212..0x1B29C',
  helper_gates=dict(number={k:r['linked'][k]for k in ['native_cases','ordered_cases','zero_cases','changing_cases','original_instruction_coverage','scope']},arithmetic={k:r['math'][k]for k in ['native_cases','ordered_cases','zero_cases','original_instruction_addresses','scope']},pad={k:r['pad'][k]for k in ['native_cases','ordered_cases','changing_read_cases','scope']},string={k:r['string'][k]for k in ['native_cases','ordered_cases','changing_read_cases','scope']},callers={k:r['callers'][k]for k in ['native_cases','ordered_cases','helper_returns','helper_entry_counts','scope']}),
  scoped_install_component_resource_full_gates=r['integration']['full_gates'],
  repaired_Deck=dict(frames_per_lane=2600,compiled_number_calls=a['compiled_number_calls'],number_returns=a['number_returns'],old_number_body_steps=a['old_number_body_steps'],task_stack_violations=a['number_stack_outside'],minimum_task_stack_headroom_bytes=a['number_min_headroom'],pending_at_finish=a['number_pending_at_finish'],tracking_errors=a['number_tracking_errors'],control_number_calls=control['number_entries'],comparisons=deck['comparisons'],scope='Same fixed pad schedule, same38declared-byte selector/count repairs in both discs. Control restores only the6byte number-conversion redirect; same resident payload/heap/compiled arithmetic. Finite observed gameplay differs.'),
  long_route=dict(parent_frames=routes['results']['parent']['executed_frames'],number_frames=routes['results']['number']['executed_frames'],frame_difference_new_minus_parent=16,both_merchant_reached=True,both_returned_floor0_and_completed_outdoor_hold=True,parent_nonzero_audio_samples=routes['results']['parent']['nonzero_audio_samples'],number_nonzero_audio_samples=routes['results']['number']['nonzero_audio_samples'],same_adaptive_policy_not_identical_inputs=True,final_fields={lane:routes['results'][lane]['final_fields']for lane in ['parent','number']},scope='Separate raw experimental discs; no Deck selector repair. Same adaptive controller, not identical recorded inputs. Selected finalX/scene/mode/floor agree; finalZdiffers1. No cycle/audio/frame-equivalence or speedup claim.'),
  local_workflow=dict(source_recovery_role='Codex coordinator',compiler_and_tests_are_agents=False,local_LLM_authored_new_C=False,native_Chat_this_source_step=False,native_UI_observation='Computer-use request timedout120.6605seconds; no lock-state inference. Headless continuation authorized.',new_training=False),
  this_lookup_executes_game_tests=False,this_lookup_invokes_model_or_training=False,job_status_scope='Published finite jobs terminal; lookup does not scan unrelated processes.',new_training=False,default_promoted=False,whole_game_complete=False,goal_complete=False,physical_console_verified=False,whole_game_speedup_demonstrated=False,physical_audio_or_quality_verified=False,available_evidence_topics=parent['current_status']['available_evidence_topics'],remaining=['Remaining original game/formatter/platform source recovery and integration','IRQ/cycle behavior and arbitrary alias/exception-handler coverage beyond declared fixtures','Whole-game content/audio and authentic physical JaguarCD boot','Reliable local authorship and representative game/advertising training gains','Future256GB hardware configuration verification'])
 report.write_text(f'''BIWN native number conversion — {now.isoformat()}

New source-specific C reconstruction
Original1B212..1B29C number-to-text body is lowered from pinned recovered instruction semantics into static C labels/branches, volatile guest accesses and native arithmetic C callees. The new code has no runtime CPUdecoder or original helper execution. It preserves original stack saves, register upperbits, the shared15B7A0 digit buffer and liveCCR requirements. This is deterministic coordinator source recovery, not recovered original source or accepted local-model C.
Source: {native/'format-number-native.c'}
Generator: {ROOT/'scripts/lower_biwn_format_number_native.py'}

Standalone and exact linked verification
Each passed1196normal nativeCPU cases,1196ordered public native-width access comparisons,16controlled changing-remaining traces and256radixzero cases with two realDIVU faults per case. All50original instruction addresses reached. Both stack modes/all32CCR covered; fullD/A,PC,SR,USP,SSP and public2MBRAM compared, including original56byte maximum public stack effects and digit scratch. Zero faults use a declared inertRTEhandler, compare trapCPU/savedSR and finalCPU with savedPC relocation. No arbitrary handlers,aliases,asynchronous argument mutation,nonterminating radix1/nonzero,IRQ/cycle/physical proof. Padding fixtures have bounded positive output; two initial original-code fixture runs hit the instruction budget on width0x8000/count0x7FFF wrapping into long padding. Their failed snapshots are retained. The matrix bounds that case to254remaining and separately checks0x7FFFremaining with width0. No C change was needed for those harness failures.
Minimum observed compiled realSP was0x1DFF08,248bytes below callerSP; zero-bridge private bookkeeping begins at least540bytes below callerSP. This finite observation supplements compiler stack-usage records; it is not an arbitrary call-depth/interrupt proof.
A deliberate C mutation toggled the final result bit: originalD0=0,badD0=1. The unmodified comparator rejected it; badcode was not installed.
Exact linked unsigned helpers separately pass3592normalCPU/ordered and512zero cases,43/43source addresses. Pad1668+16changing and string1945+16changing also pass.
1654complete original formatter/core calls match finalCPU/publicRAM/ordered sequence and8815outer helper returns:5140pad,3654number,21string. Nested math is observed at the number boundary; full direct arithmetic/number matrices are separate.

New compiled mixed disc
{disc['derived_disc']}
Payload11224bytes,reservation11264,padding40,heapstart0x1619C0. Heapstart moves2048bytes. Seven previous-prefix bytes change in address literals; every previous function symbol stays in place. All19exact-layout component/install/resource gates pass, including96startup/5151installed keyABIcases, heap init/allocation/compaction,loader,resource,lifecycle and readiness. Staging remains12KB atFB000..FE000; entry+reservation is11304bytes.28stageJMPredirects is not a recovered-routine total or decompilation percentage.

Fresh gameplay
Separate2600frame Deckpair shares38declared-byte selector/count repairs and the same fixed ordinary pad schedule. Control restores ONLYthe6byte number-entryJMP, with identical payload/heap/arithmetic. Candidate445calls=445returns,old number-body steps0,task-stack violations0,trackingerrors0,pending0,minimum observed headroom444bytes. Control837original-number calls/returns. PositionX differs1968frames,Z1960,video1988; scene/mode/floor match. Different call counts and frames are not a speedup or algorithm-equivalence proof.
Separate raw-disc adaptive routes,without selectorrepairs, both reach merchant,descendfloor0 andholdoutdoors. Immediateparent24958frames versus new24974; firstscene8549 versus8547. Both finalX13049/scene312/mode1/floor0; finalZ42401 versus42402. Capturednonzeroaudio1609492 versus1609490samples. Same policy is not identical inputs; no cycle/frame/PCM/listening-quality equivalence. The earlier missing late media relative to an older ancestor is not resolved by this small parent comparison.

Local inference and scope
No localLLMsourceAuthor or training update was invoked for this lowering step. Compiler/checkers are deterministic tools, not agents. The LMStudioChat computer-use call timedout120.6605seconds; no screen-lock inference or unlock request. Prior nativeChat demonstrations remain historical. The current status shortcut is updated and tested separately after this publication, with actual prompt/tool/response logs. OriginalCDI,defaultpreview and weights remain unchanged. Advertising research/education training reliability and the larger256GB deployment remain active goal requirements.

Rebuild from {native}
make -f {Path(b['directory'])/'Makefile'} format-bundle BUILD=/tmp/biwn-number-rebuild
Original engine code, retained emulator/HLEfirmware and devices remain. Complete source-owned console rebuild/physical boot is not achieved.
''')
 core=dict(parent['status_dependencies_sha256']);files={Path(__file__),parentp,report,*paths.values()}
 for p,h in core.items():assert sha(p)==h,p
 for k,obj in r.items():
  for table in ['source_sha256','dependencies_sha256','artifacts_sha256','execution_dependencies_sha256']:
   values=obj.get(table,{})
   if isinstance(values,dict):
    for p,h in values.items():
     if isinstance(p,str)and Path(p).is_absolute()and isinstance(h,str):assert sha(p)==h,p;files.add(Path(p))
  directory=obj.get('directory')
  if directory:files.update(p for p in Path(directory).rglob('*')if p.is_file())
 # Include complete original-budget failure evidence, not only passing runs.
 for stamp in ['20261018T183737.293401Z','20261018T183759.668143Z']:
  files.update(p for p in (ROOT/'verification/native-format-number'/stamp).rglob('*')if p.is_file())
 repair=ROOT/'verification/native-format-number-compiler-repair'
 if repair.exists():files.update(p for p in repair.rglob('*')if p.is_file())
 files.update(Path(j['proof'])for j in r['integration']['jobs'].values()if j.get('proof'))
 for p in files:
  p=p.resolve();assert p.is_relative_to(ROOT),p;core[str(p)]=sha(p)
 for p in [native/'format-number-native.c',native/'format-number-native.h',native/'format-number-shim.S',native/'semantic-divide-zero.S']:(out/p.name).write_bytes(p.read_bytes())
 state=dict(status=current['status'],recorded_at=now.isoformat(),directory=str(out),report=str(report),linked_bytes=11224,reserved_bytes=11264,heap_start=b['heap_start'],binary_sha256=b['binary_sha256'],derived_disc=disc['derived_disc'],derived_disc_sha256=disc['derived_disc_sha256'],current_status=current,status_dependencies_sha256=core,dependencies_sha256=dict(core),proofs={k:str(p)for k,p in paths.items()},parent_publication=str(parentp),new_training=False,default_promoted=False,goal_complete=False)
 save(out/'publication.json',state);save(ROOT/'verification/native-number-publication-current.json',state)
 ledgerp=ROOT/'verification/goal-continuation-current.json';ledger=read(ledgerp);save(out/'goal-continuation-before.json',ledger)
 ledger.update(status='active_native_number_C_integrated_finite_gameplay_verified_goal_incomplete',recorded_at=now.isoformat(),goal_complete=False,previous_goal_turn_classification='progress:generated number lowering and standalone compiler build; preview sprint question answered from actual mapping.',this_turn_classification='progress',current_goal_turn_progress='New1B212number C passes1196CPU/ordered+256zero and50/50source addresses;11224byte bundle in11264reservation,19fullgates,1654callers/3654numberreturns. Fresh445numbercalls/returns with444byteheadroom; bothmerchant/outdoor routes complete but frames/audio differ. No source/model/defaultpromotion.',current_goal_turn_evidence=str(ROOT/'verification/native-number-publication-current.json'),latest_native_number_publication=str(ROOT/'verification/native-number-publication-current.json'),latest_experimental_disc=disc['derived_disc'],latest_finite_jobs_running=False,latest_finite_job_status='All new isolated,linked,caller,component,Deck andlong-route jobs terminal; currentstatusReader follows publication.',native_Chat_this_continuation=False,native_UI_latest_observation='Sky timedout120.6605seconds; no lock-state conclusion.',new_training=False)
 save(ledgerp,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),role='Codex coordinator',action='deterministic native number lowering/CPU and gameplay publication',publication=str(ROOT/'verification/native-number-publication-current.json'),local_LLM_source_authorship=False,compiler_tests_are_agents=False,new_training=False,goal_complete=False))+'\n')
 assert all(sha(p)==h for p,h in core.items())
 print(json.dumps(dict(status=state['status'],core_files=len(core),integrity_mismatches=0,report=str(report),goal_complete=False)))
if __name__=='__main__':main()
