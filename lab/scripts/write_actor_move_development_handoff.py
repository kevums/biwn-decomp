"""Keep full goal active after13C9Acomponent/layout progress and failed local drafts."""
import json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);p=V/'goal-continuation-current.json';state=read(p);shutil.copy2(p,out/'previous-handoff.json');review=read(V/'actor-move-development-reviewed-current.json');pub=read(V/'current-biwn-latest-publication-current.json');index=read(V/'current-model-work-index-v4-current.json');assert review['latest_built_resident_bytes']==26220 and pub['facts']['experimental_build']['resident_bytes']==23260 and pub['facts']['next_component_development']['gameplay_tested']is False and index['saved_prompt_or_transcript_records']==58
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt');text=f'''BIWN — CURRENT WORK
{now.isoformat()}

LATEST GAMEPLAY-TESTED DISC: 23,260 resident bytes, 24,512 reservation, heap0x164D80.
The reviewed actor/sprite creation integration from the preceding pass remains
published as tested. Candidate29,787/control29,790frames returned outdoors;
17,114video frames and PCM/state differ. Default keyboard preview is unchanged,
older sourceCPU/GPUcheckpoint. HoldC+Up to run;Ppauses/resumes.

NEW DEVELOPMENT DISC: 26,220resident bytes, 28,544reservation, heap0x165D40.
The new actor-movement13C9A body is readable high-level C with original-facing
helper/packed-stack ABI. It selects animation, submits GPU work, updates integer
and fractional coordinates, and rolls back selected coordinates when the
lowWORD collision result is zero.2,960native bytes; all192original sites covered.
Prototype, actual-direction prototype and final-address0x16489Cmatrices each
pass2,624cases/fullCPU/SR/banks/helper-entryCPU/SP/SR/args/publicRAM/orderedaccess.
The latter two execute actual13440direction/E588signed division. GPU E220and
collision13B5A/13BB0remain prescribed. Maxfixture private672bytes; this is not
live task-stack proof. Four missing-body/helper-X/full-D0/original-delegation
controls reject. Native helper-X is independently checked even when final
registers/RAM/ordered trace match. Source/ABI/fixtures/layout are coordinator work;
no new local Author code adopted. Portable movement already existed; no new
logical-function recovery count.

LAYOUT / CHECKED TRAILER PRESERVATION
Naively growing oldF8000staging would overwrite94nonzero bytes atFE520,
ATARI APPROVED DATA TAILER. Newlayout moves staging toF7000andclears28,672bytes
endingFE000. OriginalF7000..F8000was zero; bytesFE000onward stay identical.
Seven heap-floor/+4/+8operands plus finalizerLEA/clearcount change with provenance;
startupJMPandloadercopycount also change. Heapcapacity369,344, reduction4,032.
Layout-onlyclone changes25,208actualCDIbytes; parentdisc unchanged.
Layoutstartup96/heapinitializer192pass; nativeheap/copy-blitter3,392andordered
3,392cases pass;36fresh-constructor capacity requests pass. Movement final-address
2,624cases pass. New26,220disc adds2,960codebytes/13C9Aentryredirect, changes2,463
actualCDIbytes versuslayout-only, leaves2,324free. Fullpayload96startup cases pass.

NOT YET DONE FOR26,220DISC
Saved-context canary qualification with its actual original-facing captures,
real GPU/collision/task/helper frame behavior, and full gameplay candidate/control.
Do not transfer the preceding creation-context8672proof to movement. Do not
promote this disc as gameplay-tested/default. CurrentMCPstatus explicitly
separates tested23,260from pending26,220development; actual configuredMCPread
verified that distinction. Timing/media/state disagreements remain unresolved.

LOCAL OUTPUT TESTS:7actualpredictions,0newweights,0adoptedsource/drafts
Three structured status attempts are retained: v13=243words/15.78s, wrong122
instead of1,228cases and too long; v14=132words/10.70s, counts correct but fragments
and ambiguous function-call/gameplay-route wording/incomplete scope; v15=75words/
7.20s, correct1,228/96andbothtestsreturnoutdoors but too short/missinglimits.
None installed. Main-menuSstillusesv12. This is output testing, not an achieved
simple-status improvement. No new nativeChatUIretry; priorAX/pixel disagreement
remains unverified.

Local movement Analyst+same-weightReviewer received source instructions and a
checked X diagnostic. Unlabeledtuples: both reversed X=0instead of16and falsely
saidWORDmoves clearX. LabeledoriginalSR310/defectiveC300retest: expected16correct,
but preserve-incoming-X repair still wrong. A literal interpretation was actually
compiled and native-tested; helperSRstill300versusoriginal310. ASL.L#6 computesX
from bit26ofsign-extendedview; it does not preserve arbitrary incomingX. Reviewer
accepted/copied the wrong explanation twice. Diagnostic-label clarity improved;
repairquality/independentverification did not. Adaptive/supplied evidence, not
heldoutmodelbenchmark. Exactprompts/finalresponses/stats saved; I58saved records,
not58newpredictions. No cloudsubagents, no acceptedlocalcode, no defaultmodelchange.

FULL FOUR-PART GOAL STAYS OPEN
1. Easy localLMfrontend/roles/models/training:SDK/CLI/MCPwork, currentnativeChat
unverified; actual output/review reliability remains inadequate. Game step32
trainedmodel unpromoted. This turn did not claim new training.
2. BIWN restoration/porting/modding and readable same-console rebuild: pending
movementcontexts/realhelpers/gameplay and remaining actual game source/interfaces;
broader paths/resources/stacks and timing/media unresolved. Physicalconsole
readiness/full rebuild unproven. Currentpreviewunchanged.
3. Advertising: optionaltrainedstep8Reviewer remains exported/loadable; latest
source-transfer comparison showed no gain overbase. Review/teaching/research
reliability needs work; same-weightroles are not independent verification.
4. Future256GBconfiguration/migration:39file46.80GBinventory/prior10shard audit and
currenthostcoldruntimeinstall exist; fullworkbenchrelocation/restore unfinished.
No fresh full-weight audit or futurehardware performance claim.

Detailed movement/source/layout/local-output review: {review['report']}
Prompt viewer: {index['report']}
''';notes.write_text(text);shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 old=read(V/'sprite-integration-turn-integrity-current.json');hashes=dict(old['dependencies_sha256']);snap=out/'snapshots';snap.mkdir();aliases=[]
 def bind(path,h=None):
  path=Path(path).resolve();actual=sha(path);assert h is None or h==actual,(path,'changed')
  if path.name.endswith(('-current.json','-active.json')):
   dest=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name);shutil.copy2(path,dest);aliases.append(dict(mutable_pointer=str(path),immutable_exact_bytes=str(dest),sha256=actual));path=dest
  if str(path)in hashes:assert hashes[str(path)]==actual,path
  hashes[str(path)]=actual
 for obj in [review,pub]:
  for path,h in obj['dependencies_sha256'].items():bind(path,h)
 for path in [Path(__file__),out/'previous-handoff.json',out/'previous-BIWN Latest Work.txt',out/'current-BIWN Latest Work.txt',Path(review['directory'])/'protocol.json',Path(pub['directory'])/'publication.json',Path(index['directory'])/'manifest.json',Path(index['report']),Path(index['source_list_snapshot']),V/'actor-move-development-reviewed-current.json',V/'native-actor-move-disc-build-current.json']:bind(path)
 def check(item):
  path,h=item
  try:return None if sha(path)==h else dict(path=path,error='hash changed')
  except OSError as e:return dict(path=path,error=str(e))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(check,hashes.items())if x]
 integrity=dict(status='terminal_actor_move_and_inherited_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(hashes),issues=issues,dependencies_sha256=hashes,historical_mutable_pointer_resolutions=aliases,scope='Bound source/binary/report/metadata integrity, not new fullweights/gameplay/hardware/model-quality proof.');save(out/'integrity.json',integrity);save(V/'actor-move-turn-integrity-current.json',integrity);assert not issues,issues
 preview=[]
 for pid in [233,235]:
  result=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True)
  if result.returncode==0:preview.append(dict(pid=pid,command=result.stdout.strip()))
 state.update(status='active_actor_movement_component_layout_ready_real_helpers_pending',recorded_at=now.isoformat(),prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,previous_turn_classification='Progress: original-facing137E0C/ABI1228cases/all184sites,2084triplecases,8672canaryexecutions,96startup,two real routes29787/29790,23,260published; full goal open.',this_turn_classification='Progress: complete original-facing13C9AC2960bytes passes2624cases/all192sites, actual13440/E588variant2624andfinal-address2624; four source/binary defects reject. Preserved AtariFE520trailer by shiftedF7000staging;28544layoutstartup96/heapinit192/native+ordered3392each/capacity36; new26220disc/fullpayloadstartup96. Movementcontext/realGPUcollision/gameplaypending,23,260remainslatesttested. Sevenlocalpredictions rejected/notadopted; exactlabeledXmaskcorrectbutactualcompiledsuggestionstillfails; Reviewerfalseacceptance.58savedrecords; integrityverified.',latest_built_disc_resident_bytes=26220,latest_published_live_build_resident_bytes=23260,latest_built_disc_game_frames=0,latest_actor_move_component=str(V/'native-actor-move-linked-current.json'),latest_actor_move_layout=str(V/'actor-move-layout-materialized-current.json'),latest_actor_move_build=str(V/'native-actor-move-disc-build-current.json'),latest_actor_move_review=str(V/'actor-move-development-reviewed-current.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(hashes),finite_jobs=[],finite_jobs_pending=0,completed_current_turn_sessions=[87089,66113,48749,38879,29138,24452,79387,89451,30150,28072,86163,73835,62225],local_model_work_this_continuation=dict(actual_predictions=7,status_candidates=3,Analyst_Reviewer_trials=2,Analyst_Reviewer_predictions=4,accepted_status_candidates=0,accepted_source=False,new_training=False,native_Chat_verified=False),interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='HoldC+Up;Ppauses/resumes',recipe='OlderverifiedsourceCPU/GPUcheckpoint,not23260or26220experimentaldisc'),next_actions=['Qualify13C9Aoriginal-facing own-context canary/native captures before real-helper/gameplay adoption. ContextatrootSP-488,72bytesr0..17;r15trackslogicaloriginalworkingSP,sohelperentrycontextSPmust equalcurrentSP+4,notrootSP. Original40savedbytes; captureargs4direction/20GPU/10outdoor/10indoor. Fourcallsactualtargets13440/E220/13B5A/13BB0; nativeJSRreturnPCs in build.actor_move_helper_returns. Nativebodyfixturemax672notlivebound.','New26220disc built only. Wholepayloadstartup96,finaladdress2624actualdirection/E588andnewheap3392+3392/192/36pass. ActualGPU/collision/taskframes and candidate/controlwholegame stillpending. Useonly13C9Aentry-restoredsame-layoutcontrol, keepothernativecreationfunctionscommon; retainalloldtiming/media limits anddo notpromotepreview.','MovedstagingF8000toF7000,copyreserve28544/clear28672endFE000toavoidATARIAPPROVEDDATATAILERatFE520. Preserve94nonzero trailerbytesandparentdisc. Sevenheaprefs+finalizerLEA/clearcountchanged,initialJMPandloadercopycounttoo. Newheap165D40/cap369344,free2324. Do not revertto naiveF8000growth.','CurrentoperationalSremainsv12. Structuredv13/14/15failednumeric/format/semanticrequirements; noneinstalled. Sevennewlocalpredictionslogged, sameweightReviewerwrongtwice. Explicitdiagnosticlabelshelpedread16butpreserve-incomingXrepairfailsactualCPU. No newsourceadoption/weights or blindpromptretry; improve input/workflow/modeladaptation with faithful output checks.','CurrentMCPgenericstatusseparatestested23260andpending26220next_component_development. Keep specificactor_movementtopic historic scope distinct untilappropriatelyupdated. CurrentnativeChatAX/pixelsunverified; no repeatedidenticalUIorunlockrequest.','Preservefullgoal: remainingsource/readableoriginalconsolerebuild/timing/media, easyreliablelocalroles/gametraining,Advertisingoptionalstep8loadablebutreliability/nogainlimits,fullworkbenchrestore/future256GBpreparation. Existingpreview233/235unchanged; C+Upruns. Allfinitejobscompleted; do not restartexistingtests.'],no_completion_claim=True,handoff_script_sha256=sha(Path(__file__)))
 state['current_entrypoints']['prompts_I']='58saved prompt/transcript records,7newpredictions this continuation; not58newpredictions'
 state['full_goal_requirements'][0]['remaining']='SDK/CLI/MCPworking. Structuredstatusalternatives3rejected/notinstalled; localdiagnostic2sameweightpairsfailedcorrectrepair despiteclarifiedbitmask. NativeChatstillunverified. Model/role/reliableeasyinferenceunfinished.'
 state['full_goal_requirements'][1]['evidence']=review['report'];state['full_goal_requirements'][1]['remaining']='Publishedgameplay-tested23260creationdisc; new13C9Aoriginal-facingmovement2960bytes/2624all192sites,shifted28544layoutchecks and26220discstartup96pass. Contextqualification/realGPUcollision/tasks/gameplaypending. Fullreadablegame/sameconsolerebuild/remaininginterfaces/broaderpaths/timing/mediaunfinished.'
 save(out/'protocol.json',state);save(p,state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),event='actor_movement_original_ABI_and_shifted_layout_progress',coordinator='Source/ABI/fullCPUandhelperreplays/negatives/trailerpreservinglayout/heapstartup/finalbuild/localoutputreview',local_models='3Readerpredictions+2AnalystReviewertrials=7actualpredictions,0acceptedoutputs',new_training=False,latest_tested_resident_bytes=23260,latest_built_resident_bytes=26220,movement_gameplay_verified=False,report=review['report'],bound_files_verified=len(hashes),goal_complete=False))+'\n')
 print(json.dumps(dict(status=state['status'],bound_files=len(hashes),tested=23260,built=26220,pending_jobs=0,goal_complete=False,notes=str(notes))))
if __name__=='__main__':main()
