"""Freeze the partial native Deck disc and explicitly bounded verification."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 pointer=V/'native-Deck-delivery-current.json';pub=Path(read(pointer)['directory']);review=read(V/'native-Deck-image-reviewed-current.json');b=read(V/'native-Deck-coordinate-disc-build-current.json');reader=read(V/'Deck-status-live-v7-reviewed-current.json');team=read(V/'native-native-Deck-team-reviewed-current.json')
 assert review['status']=='terminal_native_Deck_image_boot_heap_fresh_routes_reviewed'and reader['source_checked']and team['source_checked_facts']
 assert sha(b['derived_disc'])==b['derived_disc_sha256'];original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert sha(original)=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
 ps=subprocess.run(['/Users/kevin/.lmstudio/bin/lms','ps','--json'],capture_output=True,text=True,check=True);models=json.loads(ps.stdout);assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0;save(pub/'model-idle-final.json',models)
 names=['native-deck-coordinate-current.json','native-deck-coordinate-v2-current.json','native-deck-stack-watermark-current.json','native-deck-connected-current.json','native-deck-connected-v2-current.json','native-Deck-coordinate-disc-build-current.json','native-Deck-layout-startup-heap-initialize-current.json','native-Deck-layout-heap-operations-current.json','native-Deck-layout-capacity-witness-current.json','native-Deck-region-observer-current.json','native-Deck-image-reviewed-current.json','native-Deck-coordinate-quiescent-candidate-current.json','native-Deck-coordinate-quiescent-control-current.json','native-Deck-coordinate-v2-quiescent-candidate-current.json','native-Deck-coordinate-v2-quiescent-control-current.json','native-Deck-context-current.json','Deck-status-live-v6-reviewed-current.json','Deck-status-live-v7-reviewed-current.json','native-native-Deck-team-reviewed-current.json','current-model-work-index-v4-current.json']
 evidence=pub/'evidence';evidence.mkdir(exist_ok=True);sources=pub/'as-run-sources';sources.mkdir(exist_ok=True);bindings={};folders={}
 def bind(path,digest=None):
  p=Path(path);actual=sha(p)
  if digest is not None:assert actual==digest,str(p)
  key=str(p.resolve());target=sources/(hashlib.sha256(key.encode()).hexdigest()[:12]+'-'+p.name)
  # Large disc/frame records remain bound in their original immutable run
  # location; small source and proof inputs are snapshotted here.
  if p.stat().st_size<=8000000:
   if target.exists():assert sha(target)==actual,str(target)
   else:shutil.copy2(p,target)
   snapshot=str(target)
  else:snapshot=None
  bindings[key]=dict(sha256=actual,bytes=p.stat().st_size,snapshot=snapshot)
 for name in names:
  p=V/name;j=read(p);shutil.copy2(p,evidence/name)
  if j.get('directory'):folders.setdefault(j['directory'],name.removesuffix('-current.json'))
  for field in ['source_sha256','source_bindings']:
   values=j.get(field,{})
   if isinstance(values,dict):
    for path,digest in values.items():bind(path,digest)
  if j.get('payload'):bind(j['payload'],j.get('payload_sha256'))
 for directory,label in folders.items():
  source=Path(directory);dest=evidence/label;dest.mkdir(exist_ok=True)
  for p in source.rglob('*'):
   if p.is_file()and p.suffix!='.cdi'and p.stat().st_size<=8000000:
    target=dest/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert sha(target)==sha(p),str(target)
    else:shutil.copy2(p,target)
  # Preserve large raw frame reports by explicit immutable hash rather than
  # silently dropping their provenance from the publication.
  for p in source.rglob('report.json'):bind(p)
 for p in Path(team['session']).rglob('*'):
  if p.is_file():
   target=evidence/'actual-native-team-session'/p.relative_to(team['session']);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 for p in [Path(__file__),ROOT/'native_deck_source_context_v1.py',ROOT/'scripts/native_chat_team_context.py',ROOT/'scripts/run_deck_status_live_v6.py',ROOT/'scripts/run_deck_status_live_v7.py',ROOT/'config/current-model-work-sources.json',ROOT/'Live Local BIWN Briefing.command',ROOT/'Open Local AI Lab v6.command',Path(b['derived_disc']),Path(b['derived_stage']),Path(b['component']),Path(b['copy_component'])]:bind(p)
 bundle=Path(team['installed_bundle']);bind(bundle,team['installed_bundle_sha256']);save(pub/'source-bindings.json',bindings)
 assert 'run_deck_status_live_v7.py'in(ROOT/'Live Local BIWN Briefing.command').read_text();index=read(V/'current-model-work-index-v4-current.json');assert index['saved_prompt_or_transcript_records']==104
 note=Path(b['directory'])/'READ ME - Experimental Native Deck.txt';note.write_text('Partial native Jaguar CD experiment. Only recovered Deck coordinate11D1A is installed;five other recovered Deck callers remain hosted. Native68000compile/boot/heap/component/controlledDeck/freshordinaryroutes are reviewed. Ordinaryroute didnotreachcoordinate. Physicalconsole,fullsourcegamerebuild,timing/helper-suspension andcomposednativeGPU-family activation remainunverified. Defaultpreviewnotchanged.\n\nImage:\n'+b['derived_disc']+'\n\nImageSHA256:\n'+b['derived_disc_sha256']+'\n\nReview:\n'+str(ROOT/'reports/Native Deck Console Build Review.txt')+'\n')
 bind(note);save(pub/'source-bindings.json',bindings)
 report=f'''NATIVE DECK CONSOLE BUILD REVIEW

A separate experimental Jaguar CD image now contains the recovered coordinate-update caller at 11D1A compiled for the real 68000 instruction set. Its algorithm is the earlier local V6 Repair body plus ten explicit coordinator MOVE.L stack flag updates and one cached-read temporary. Native ABI, stack ownership, callbacks, compiler support, loader, checks and integration are coordinator work. There was no new model code draft or optimizer update in this turn. The other five recovered Deck callers remain hosted-only. The whole game is not rebuildable from recovered readable source.

Image:
{b['derived_disc']}
SHA-256: {b['derived_disc_sha256']}

The native module is 9,532 bytes, including its ABI and memory helpers. The new image contains 44,430 total native code/data-prefix bytes: the previous 34,784 plus this module and a 114-byte early finalizer. Total resident reservation is 174,208 bytes, including the existing 26,112-byte GPU arena, the new 103,424-byte Deck arena and alignment. Each original game task owns one 1,024-byte Deck slot. The loader copies 70,784 bytes and separately clears/guards the new arena before resuming original address 400A. This keeps each 16-bit copy/clear loop within its word-count limit. The initial heap starts at189640 and has223,680 bytes. The original CDI and its FE200 trailer are unchanged; the previous experimental image is preserved.

The native bridge captures the original registers and SR, runs C on the task's private arena stack, and switches to the original guest argument stack for fixed GPU/multiply helper calls. Its helper-return path uses only SP for the initial frame lookup, preserving helper outputs until captured on the private stack. It restores the original return word afterward. Both 78-byte native CPU layout and frame offsets are checked at compile time. Invalid task identities take an original-code prefix/continuation fallback. An initially missing freestanding memcpy definition was retained explicitly for the compiler's struct copies; final builds link and execute without external runtime dependencies for these copies.

The first576-case native comparison used distinct task identities. A second576-case comparison covered all101 identities with actual task-local guest stacks at three depths, including two-byte rather than four-byte alignment, both stack banks and all incoming CCR values. Final registers/SR/PC/USP/SSP and full2MBguest RAM outside the declared private arena match the original CPU. At helper entry, only the compiler return word is normalized to the original return address, alongside the private arena normalization; all other registers/arguments/guest RAM match. E540 runs its real original CPU body; GPU results are explicit component fixtures. All guards, other task arenas and source task headers remain intact. Three invalid-identity fallbacks match separately and intentionally execute original code. Eight additional witnesses measure266bytes of C-stack use with626bytes clear of the frame. An earlier minimum-SP value16 was a flag-neutral frame-address lookup using SP, not actual C-stack depth.

The connected controlled test executes both lanes on the actual CPU and GPU, with retained original helpers and scheduler code. It observes17 compiled coordinate calls,31 matching checkpoint pairs and149GPU commands, and verifies constructor loading, viewer exit/cache restoration and two world updates. It uses captured RAM, the experimental selector/count13 patch, supplied world entry/ring and reservations made by the original allocator. Compaction or lost reservations is rejected. Private arena bytes, the6-byte root redirect and an active compiler helper-return word are the declared RAM normalizations. No helper suspension occurred inside an active coordinate call. This controlled test retains the original GPU wrapper; activation of the installed coordinate together with the derived image's native GPU-family wrapper is still pending.

The actual disc layout passes six full-register boot-copy/clear comparisons and192 exact raised-boundary heap-initialization comparisons. Another3392 native allocator/compactor/copy-blitter cases and3392 ordered-access comparisons pass, followed by36 allocation capacity/boundary requests from freshly initialized RAM. Code/reservation/staging-copy sizes are recorded separately rather than treating mutable arenas as code.

Four fresh native gameplay runs cover the new image and a same-layout control, before and after an observer correction. Candidate and control both return outdoors. The final candidate runs24624frames; control runs24591. All16 retained monitor families and pending-call checks pass. The control restores62declared entry bytes across ten original roots (initializer,eight GPU commands,coordinate), so differences cannot be attributed solely to the new coordinate code. The processors,IRQ/DSP/device/HLE and frame input machinery are retained; there is no host CPU/GPU state seed, guest RAM write or snapshot restore in those fresh routes. Whole-state/video/timing differences remain and no performance or physical-console equivalence is claimed. The common PCM prefix matches.

The initial candidate reported one arena error. The old monitor compared a single contiguous44,430-byte code range, which now crossed the mutable GPU arena because the new code was appended after that arena. All403 changed bytes in that comparison were legitimate GPU arena data; the new Deck arena was untouched. The control, whose GPU wrappers are original, had no such false error. The corrected monitor compares both complete immutable ranges and separately checks GPU/Deck guards, ownership and unused slots. Eight compiled code/gap/guard/unused-slot corruption controls are rejected. Fresh reruns preserve every frame record, final RAM and PCM byte of each lane's initial run while the candidate's false error drops from1to0. No game bytes or monitor ABI predicates were relaxed to obtain this result.

The ordinary fresh route observes zero coordinate calls and still does not reach GPU rootE26C. All101Deck arenas remain unused and byte-identical there. Thus the disc's fresh route is a regression/boot/layout check, not natural gameplay coverage of the new function. Component and controlled17-call evidence must retain their separate scopes. Natural fresh-disc Deck activation, composed native-GPU-family interaction, actual helper suspension/reentrancy/IRQ behavior and physical hardware are unfinished. The substantial code/stack overhead is measured; CPU-cycle performance remains unverified.

The first local native-status Reader completed in8.09seconds but conflated the six hosted routines with one installed routine and attached total image bytes to the coordinate module. It was rejected before shortcut adoption. A smaller source-fact handoff produced a checked answer in4.63seconds,92message fragments and0.854seconds to first message. It names only11D1Aas installed, the other five as hosted,44430as total code and9532as the module, and17controlled calls versus ordinaryzero. This is one warm inference on the daily27Bbase, not training or a general/cold-start benchmark.

The installed backend also ran three actual local roles with current native facts: Analyst59words,Restorer JSON40words,Reviewer59words. Installation/test/full-game limits are correct. The Restorer gives a distinct unfinished engineering step; the Reviewer repeats the correct Analyst text. Agreement on shared weights is not independent verification. These tests use a mock UI controller; native LM Studio Chat selection/rendering remains unverified. No UI restart, unlock request or hidden conversation injection occurred. Exact prompts and raw responses for all five actual predictions are saved: two Readers and three team roles. No new model weights were produced. The existing Advertising models and their unresolved reliability work are unchanged.

Desktop Live BIWN Briefing and launcher option11now use the checked native Reader. Option7indexes104saved prompt/transcript records, not104predictions. Main menu v6 and MCPv18 remain. The current keyboard preview is unchanged and the experimental image is not promoted to its default. Native-code restoration, current native Chat, Advertising entailment/chronology/Reviewer quality, current-version portability and actual future-machine acceptance remain active requirements.

Next work: exercise the composed installed coordinate/native-GPU family from a restored fresh-derived machine and then from a natural fresh-disc Deck caller, test actual helper suspension and reentrancy, and qualify remaining Deck source for native integration. Resolve the original asset schema before claiming unpatched C-Space or whole-game reconstruction.

Exact current local prompts/responses:
{Path(reader['directory'])/'prompts-and-responses.txt'}
{Path(team['directory'])/'prompts-and-responses.txt'}

Evidence publication:
{pub}
'''
 friendly=ROOT/'reports/Native Deck Console Build Review.txt';friendly.write_text(report);(pub/'report.txt').write_text(report)
 audit=dict(full_objective_complete=False,requirements=dict(game='Partialnativecoordinateinstalled/compiled/booted. SixhostedDeckcallers1852originalbytes;only11D1Anative. Controlled17calls;ordinary0. Fullreadablegame/same-consolephysicalrebuild,timing/composedGPU/helperyield/remainingcode/assets unfinished.',local_frontend='OnecheckednativeReader4.63sec afterone rejected8.09secanswer. Threeactualbackendrolesfactschecked,mockUI;ReviewerrepeatscorrectAnalyst. NativeChatUIunverified,MCPv18/menuv6retained.',Advertising='Dailybase/optionaltrainedReviewerretained;earlierentailment/chronology/length/Reviewercopyfailures remain. NonewAdvertisingwork/trainingthisturn.',future_hardware='Testedportablev17retained;latestnative/source/helper/menuworknotmigrated. Actualfuture256GBhardwareunverified.'));save(pub/'requirement-audit.json',audit)
 state=dict(status='terminal_native_Deck_delivery_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(pub),native_build=str(V/'native-Deck-coordinate-disc-build-current.json'),native_disc=b['derived_disc'],native_disc_sha256=b['derived_disc_sha256'],code_bytes=44430,copy_bytes=70784,total_reservation_bytes=174208,initial_heap_bytes=223680,native_coordinate_installed=True,controlled_native_calls=17,ordinary_native_calls=0,all_16_retained_monitors_pass=True,source_checked_Reader_seconds=4.63,actual_predictions=5,new_training=False,default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,native_Chat_verified=False,ongoing_finite_workers=[],review=str(friendly),review_sha256=sha(friendly),integrity=str(pub/'integrity.json'))
 save(pub/'protocol.json',state);save(pointer,state)
 goalpath=V/'goal-continuation-current.json';goal=read(goalpath);goal.update(status='active_native_Deck_delivery_reviewed',recorded_at=state['recorded_at'],directory=str(pub),previous_goal_turn_classification='progress:facecontact/nativehybrid hosted source qualified',current_turn_classification='progress',full_objective_complete=False,blocked=False,ongoing_finite_workers=[],publication=str(pointer),review=str(friendly),integrity=str(pub/'integrity.json'),requirement_audit=str(pub/'requirement-audit.json'),resident_code_bytes=44430,reserved_arena_data_bytes=129536,total_reservation_bytes=174208,initial_heap_bytes=223680,live_GPU_returns=review['coverage']['ordinary_GPU_returns'],candidate_control_frames=[24624,24591],all16_monitor_families_pass=True,current_turn_predictions=5,new_training=False,saved_prompt_or_transcript_records=104,native_Deck_delivery=state)
 goal['remaining_requirements'].update(game=audit['requirements']['game'],local_LM_frontend=audit['requirements']['local_frontend'],portable_future256GB=audit['requirements']['future_hardware'])
 goal['next_actions']=['Qualifyinstallednativecoordinate+nativeGPUfamily togetherusingfreshderivedsnapshot/controlledDeck,then naturalfresh-discDeckactivation. Ordinaryfreshroutecoordinate0;controlled17usesoriginalGPUwrapper. Do notclaimcomposed/naturalcoverageyet.', 'Testactualhelper-suspension/reentrancy/IRQ andextendclosedDecksourcegroup/nativeABI;resolveoriginalasset schema/unpatchedmode3behavior. Fullgamerebuild remains incomplete.', 'Usequalifiedhybridcode/proof-mappedcurriculum forfuturelocaltraining whilekeepingrawfailedV6andtested/exposedcaseboundaries. No rawmodelsourceornewweightsacceptedthisturn.', 'ContinueAdvertisingentailment/chronology/length/Reviewerquality andactualnativeChatverification. Keepheadlesswhilelocked withoutunlockrequests.', 'Packagecurrentv18/newnative/source/frontendwithversionedacceptance;retainpassedportablev17 andtestactualfuturehardware.']
 save(goalpath,goal);shutil.copy2(goalpath,pub/'goal-state-final.json')
 files=[dict(path=str(p.relative_to(pub)),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(pub.rglob('*'))if p.is_file()and p!=pub/'integrity.json'];save(pub/'integrity.json',dict(status='terminal_all_published_file_hashes_verified',files=len(files),entries=files))
 for row in files:assert sha(pub/row['path'])==row['sha256']
 print(state['status']);print('Published files',len(files));print(friendly)
if __name__=='__main__':main()
