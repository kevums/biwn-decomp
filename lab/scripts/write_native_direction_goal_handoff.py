"""Record verified native direction progress while preserving all four goals."""
import copy,hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();previous=read(V/'goal-continuation-current.json');save(out/'previous-handoff.json',previous);review=read(V/'native-direction-integration-reviewed-current.json');publication=read(V/'current-biwn-latest-publication-current.json');mcp=read(V/'current-native-direction-MCP-current.json');index=read(V/'current-model-work-index-v4-current.json');build=read(V/'native-actor-direction-disc-build-current.json')
 assert review['live_monitor_pass']and review['resident_bytes']==publication['facts']['experimental_build']['resident_bytes']==mcp['resident_bytes']==30834 and index['saved_prompt_or_transcript_records']==73
 loaded=json.loads(subprocess.check_output(['/Users/kevin/.lmstudio/bin/lms','ps','--json'],text=True));save(out/'loaded-models.json',loaded);assert len(loaded)==1 and loaded[0]['identifier']=='advertising-scholar'and loaded[0]['contextLength']==32768 and loaded[0]['parallel']==1 and loaded[0]['status']=='idle'
 jobs=[]
 for name,needle in [('native-actor-direction-current.json','check_native_actor_direction_v3.py'),('native-actor-direction-contexts-current.json','check_native_actor_direction_contexts.py'),('native-actor-direction-final-current.json','check_native_actor_direction_final.py'),('actor-direction-live-observer-current.json','qualify_native_actor_direction_observer.py'),('actor-direction-native-Author-current.json','run_actor_direction_native_author.py'),('actor-direction-native-Repair-current.json','review_repair_actor_direction_local.py'),('native-actor-direction-candidate-current.json','run_biwn_native_actor_direction_route.py'),('native-actor-direction-control-current.json','run_biwn_native_actor_direction_route_v2.py'),('native-actor-direction-quiescent-candidate-current.json','run_biwn_native_actor_direction_quiescent_route.py'),('native-actor-direction-quiescent-control-current.json','run_biwn_native_actor_direction_quiescent_route.py'),('direction-route-pointer-repair-current.json','repair_direction_route_pointer_when_terminal.py')]:
  state=read(V/name);assert state['status'].startswith('terminal_');observations=[]
  for pid in [x for x in [state.get('pid'),state.get('child_pid')]if x]:
   p=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True);matches=p.returncode==0 and(needle in p.stdout or str(Path(state['directory'])/'probe.py')in p.stdout);assert not matches,(name,pid);observations.append(dict(pid=pid,matching_worker_live=False,handle_missing=p.returncode!=0))
  jobs.append(dict(pointer=name,status=state['status'],process_observations=observations))
 assert read(V/'native-navigation-hybrid-candidate-current.json')['frames']==24610
 preview=[line.strip()for line in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()if 'run_biwn_interactive.py'in line or('probe_biwn_frame_CPU_owner.py'in line and '--live-window'in line)]
 summary=f'''BIWN — ACTOR DIRECTION UPDATE
{now.isoformat()}

The latest reviewed experimental disc has 30,834 native bytes. Actor heading
function 0x13440 now executes a complete 798-byte C implementation with the
original signed-division helper. This is another compiled game function;
it is not a complete game-source rebuild or a physical-console release.

Both fresh routes returned outdoors with all live monitors passing and zero
pending calls. The candidate completed 24,634 frames and 12,474 checked direction
returns; its original-direction control completed 24,628 frames and 14,255 returns.
Both extended their first recordings by one normal frame to finish pending calls.
Each run's earlier frames and audio prefix stayed identical to its first attempt.

Fresh-pair audio matches over the 78,809,600-byte common prefix; complete capture
lengths differ by six frames. All 24,628 aligned DSP states match. Video, CPU,
RAM, navigation and adaptive-input differences remain; timing is unresolved.
No whole-game audio, speedup, full-state equivalence or hardware claim.

Tests: 2,560 prototype + 2,560 final component cases, all 61 reachable original
root instruction sites; 2,560 caller-context cases with eight bytes of observed
clearance; four semantic defects and one deliberately overlapping context reject.
The read-only monitor passed 306 qualification executions and four observation
negatives. Startup: 96 cases; heap initializer: 192; heap/copy: 3,392 native plus
3,392 ordered cases; capacity requests: 36. Reserve 31,104 bytes, 270 spare;
heap 0x166740, staging 0xF6800..0xFE200. Original disc/trailer preserved.

Who did what:
• Codex prepared the ABI bridge, source adaptation, compiler/emulator gates,
  read-only observer, layout and integration review.
• The local 27B Author took 61.73 seconds; the same-weight Reviewer took 32.84;
  one informed Author repair took 89.80. These are sequential contexts, not
  independent models. Both proposals compiled after one outer fence was removed,
  but failed the first fixture. Neither proposal was adopted.
• The first proposal used stale helper context and entered a zero-divisor path.
  The repair still wrote before decrementing SP and overwrote its return slot.
  The Reviewer ended mid-sentence at 599 output tokens against a 600-token limit;
  no finish reason was reported. One verified development SFT record is prepared
  but untrained. No optimizer step or default-model promotion occurred this turn.

Exact prompts, inputs and raw responses (73 saved records):
{index['report']}

LM Studio's installed v11 MCP still exposes 18 tools. The existing task/verifier
tools now accept actor_direction: an actual bad local candidate is rejected and
the coordinator reference passes the bounded 2,560-case/context check. Actual
source retrieval still returns Advertising PDF pages 9/20. Current status also
returns the 30,834-byte build and its limits. Native Chat inspection timed out
without window/AX state; native Chat display/adoption remains unverified.
Daily 27B model remains at 32K context, one worker, idle. Advertising's prior
base/experimental Reviewer loadability and interpretation limits remain unchanged.

Where to find it:
• Desktop → Local AI Lab → Show BIWN Native Disc.command now selects the latest
  published, hash-checked disc rather than an older resource build.
• The keyboard preview is unchanged on its prior recipe: click it, hold C + Up
  to run, P to pause/resume.
• Source: {build['direction_source']}
• From that source directory, make -f Makefile.actor-direction-ready actor-direction
  builds the checked prototype component with no source override. A clean build
  produced the exact verified 798-byte binary. This is a component build.
• Detailed reviewed evidence: {review['report']}

All finite workers are terminal. A temporary status-pointer naming collision in
the first new runner was isolated after it finished; the old navigation pointer
was restored from its immutable receipt. No game job was restarted for that fix.
The later quiescent runs use dedicated pointers and preserve the earlier cutoffs.

The full four-part goal remains active: readable game/task/callgraph recovery,
same-console full source build, unobserved outcomes and timing differences;
native Chat and ordinary workflow reliability; Advertising interpretation and
adaptation quality; and remaining portable/latest-tool setup. The previously
tested moved package remains frozen at v10/30,036 bytes; new v11/30,834 work is
not claimed copied/retested there. Future 256 GB capacity remains unbenchmarked;
prepare the profile here, then measure it when that hardware is available.
'''
 friendly=ROOT/'reports/Native Actor Direction.txt';friendly.write_text(summary);shutil.copy2(friendly,out/'Native Actor Direction.txt');notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt');notes.write_text(summary+'\nPREVIOUS DETAILED HANDOFF (PRESERVED)\n\n'+(out/'previous-BIWN Latest Work.txt').read_text());shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 deps=dict(read(V/'portable-sdk-turn-integrity-current.json')['dependencies_sha256']);aliases=[]
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  mutable=not p.is_relative_to(ROOT)or(p.parent==V and p.name.endswith(('-current.json','-active.json')))or p in [notes,friendly,ROOT/'config/current-model-work-sources.json',ROOT/'Show BIWN Native Disc.command']
  if mutable:
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:14]+'-'+p.name[-140:]);shutil.copy2(p,target);aliases.append(dict(original=str(p),snapshot=str(target),sha256=actual));p=target
  assert str(p)not in deps or deps[str(p)]==actual,str(p);deps[str(p)]=actual
 for p,h in publication['dependencies_sha256'].items():bind(p,h)
 pointers=['native-direction-integration-reviewed-current.json','native-actor-direction-current.json','native-actor-direction-final-current.json','native-actor-direction-disc-build-current.json','native-actor-direction-contexts-current.json','native-actor-direction-negatives-current.json','actor-direction-layout-startup-heap-initialize-current.json','actor-direction-layout-heap-operations-current.json','actor-direction-layout-capacity-witness-current.json','actor-direction-live-observer-current.json','actor-direction-native-Author-current.json','actor-direction-native-Repair-current.json','actor-direction-local-proposal-reviewed-current.json','actor-direction-local-repair-reviewed-current.json','native-actor-direction-candidate-current.json','native-actor-direction-control-current.json','native-actor-direction-quiescent-candidate-current.json','native-actor-direction-quiescent-control-current.json','direction-route-pointer-repair-current.json','actor-direction-frontend-v11-current.json','configured-actor-direction-frontend-current.json','current-native-direction-MCP-current.json','native-direction-development-SFT-current.json','native-direction-easy-build-current.json','native-disc-launcher-fix-current.json','current-biwn-latest-publication-current.json','native-direction-status-publication-current.json','current-model-work-index-v4-current.json']
 for name in pointers:
  p=V/name;state=read(p);bind(p)
  for name,digest in state.get('source_sha256',{}).items():bind(name,digest)
  directory=state.get('directory')
  if directory:
   for f in Path(directory).glob('*'):
    if f.is_file():bind(f)
 for f in [Path(__file__),friendly,notes,ROOT/'config/current-model-work-sources.json',ROOT/'Show BIWN Native Disc.command',Path.home()/'.lmstudio/mcp.json',ROOT/'actor_direction_workbench.py',ROOT/'chat_tools_current_v11.py']:bind(f)
 nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 for f in [*nd.glob('actor-direction*'),*nd.glob('Makefile.actor-direction*')]:
  if f.is_file():bind(f)
 for f in (ROOT/'scripts').glob('*direction*.py'):bind(f)
 for f in (ROOT/'scripts').glob('*direction*.c'):bind(f)
 for f in (ROOT/'runs').glob('*direction*.log'):
  if f.name!='native-direction-goal-handoff.log':bind(f)
 for name in ['actor-direction-native-Author-current.json','actor-direction-native-Repair-current.json']:
  state=read(V/name)
  for f in Path(state['directory']).rglob('*'):
   if f.is_file():bind(f)
 for f in Path(index['directory']).glob('*'):
  if f.is_file():bind(f)
 for f in out.glob('*'):
  if f.is_file():bind(f)
 def verify(row):
  p,h=row
  try:return None if sha(p)==h else dict(path=p,error='SHA mismatch')
  except Exception as error:return dict(path=p,error=repr(error))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(verify,deps.items())if x]
 integrity=dict(status='terminal_native_direction_full_turn_bound_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(deps),dependencies_sha256=deps,issues=issues,mutable_snapshots=aliases);save(out/'integrity.json',integrity);assert not issues,str(issues[:5]);save(V/'native-direction-turn-integrity-current.json',integrity)
 state=copy.deepcopy(previous);state.update(status='active_native_direction_integrated_and_live_checked_full_goal_remains',recorded_at=now.isoformat(),previous_turn_classification='Progress: moved copiedSDK/three assistant launchers/model hashes/nativecomponent build andone unpromoted realtrainingupdate verified.',this_turn_classification='Progress: complete13440native798bytecomponent,prototype/final2560each/callercontexts/all61sites,4semantic+overlap+4observernegatives,96startup/192heapinit/3392native+orderedheap/36capacity,30834bytefreshcandidate24634/control24628roundtrips/allmonitors/pending0;3actuallocalrolecallsrejectedandv11task/verifierinstalled.73records;fullgoalnotcomplete.',goal_complete=False,prior_state_archive=str(out/'previous-handoff.json'),latest_published_live_build_resident_bytes=30834,latest_built_disc_resident_bytes=30834,latest_built_disc_game_frames=24634,latest_native_direction_build=str(V/'native-actor-direction-disc-build-current.json'),latest_native_direction_review=str(V/'native-direction-integration-reviewed-current.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(deps),latest_local_status_delivery=str(V/'current-native-direction-MCP-current.json'),latest_native_UI_attempt=read(V/'native-direction-status-publication-current.json')['native_UI_attempt'],latest_model_work_index=str(V/'current-model-work-index-v4-current.json'),latest_migration_review=str(V/'portable-sdk-workbench-reviewed-current.json'),latest_cold_package=previous['portable_package'],latest_Advertising_review=str(V/'portable-sdk-workbench-reviewed-current.json'),finite_jobs=[],finite_jobs_pending=0,completed_finite_jobs=jobs,local_model_work_this_continuation=dict(actual_prediction_rounds=3,roles=['Author','same-weightReviewer','informedAuthorRepair'],seconds=[61.73,32.84,89.8],new_training=False,new_weights=False,unchanged_direction_source_adopted=False,quality_gain_demonstrated=False,native_Chat_verified=False,default_daily_restored=True),interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='Hold C + Up; P pauses/resumes',recipe='Existing older preview,not latestnativeexperimentaldisc'),no_completion_claim=True)
 state['full_goal_requirements'][0].update(state='incomplete',evidence=str(friendly),remaining='Installedv11fixedactor_directiontask/verifieractual18toolMCPpositive/rejection/source/statuspass. NativeChatinspectiontimedout/noAXstate;visualadoption/easyordinaryrole reliabilityremainunfinished.')
 state['full_goal_requirements'][1].update(state='incomplete',evidence=review['report'],remaining='30834nativebytes/798byte13440integrated;fullcomponentandfreshrouteproofspass. ActualE588/GPUsubmitE220andotheroriginalservicesremain;video/state/timing differ. Fullreadablegame/callgraph/sameconsole sourcebuildandunobservedpaths/hardwareunfinished.')
 state['full_goal_requirements'][2].update(state='partially_implemented_reliability_incomplete',remaining='Existingbase+optionaltrainedstep8Reviewermodelreadytoload;actualsourcePDF9/20retrievalpreserved. PriorAdtiming/beneficiaryomissionsremain;newgamecodeAuthor/repairfailuresnotAdqualitybenchmark. No newAdvertisingtraining/qualitygain.')
 state['full_goal_requirements'][3].update(state='incomplete',remaining='Prior movedpackagecopiedSDK/three launchers/sourcecomponent/oneactualtrainingupdatetests retained atv10/30036. Currentnewv11/30834notyetcopied/retestedthere;remainingportableworkflows/latesttools/onboardingneedwork. Prepare256GBprofilehere;actualfuturecapacitymeasurementisdeferred,notaheadlessblocker.')
 state['next_actions']=['Continueactualgame-source/callgraphrecovery andsame-console sourcebuild;likelynextoriginal-facingGPUsubmitE220/E2B8orremainingtaskcode. Do notreplacewholeprocessorsinstead ofremaininggamefunctions.','Preserveallpassed13440/native/liveproofs andoriginalimages;broadenunobservedoutcomes/IRQ/timing oroptimizeactualsourceABIbridgeonlywithnewvalidationreason. No whole-game/media/speedup/hardwareclaim.','ImprovecurrentnativeLMStudioChat/visibleprompt/tooladoption whenUIbridgeevidencechanges;do notaskunlockorrepeatunchangedtimed-outAXrequests. Newfixedtask/verifieravailableheadlessly.','AddressAdvertisingresearch/teaching/reviewerinterpretationwithsource-adjudicatedtasks;currentsuppliedsourcesareexposed,notnewheldout. PreparedgameSFTexampleisdevelopmentdata,untrained/unpromoted.','Advanceportablelatestcode/v11tools/workflow/training/first-usepackagewithoutclaimingitsoldfrozenv10proofcoversnew30834build. Futureprofilecanbepreparednow;noactual256GBbenchmarkclaim.','Allfiniteworkersareterminal;do notrestartthem. Existingkeyboardpreviewunchanged;ShowBIWNNativeDiscnowselectspublished30834. Reviewall73savedprompt/transcriptrecords.']
 save(out/'handoff.json',state);save(V/'goal-continuation-current.json',state);print(json.dumps(dict(status=state['status'],directory=str(out),integrity_files=len(deps),goal_complete=False)))
if __name__=='__main__':main()
