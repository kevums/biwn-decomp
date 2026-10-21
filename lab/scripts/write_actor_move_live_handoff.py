"""Full four-part goal handoff after real-helper movement and offline restore pilot."""
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
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);pointer=V/'goal-continuation-current.json';state=read(pointer);shutil.copy2(pointer,out/'previous-handoff.json');review=read(V/'actor-move-integration-reviewed-current.json');migration=read(V/'evidence-restore-pilot-reviewed-current.json');delivery=read(V/'movement-status-readers-reviewed-current.json');pub=read(V/'current-biwn-latest-publication-current.json');index=read(V/'current-model-work-index-v4-current.json');assert review['resident_bytes']==pub['facts']['experimental_build']['resident_bytes']==26220 and review['live_monitor_pass']and delivery['actual_predictions']==4 and index['saved_prompt_or_transcript_records']==59 and pub['facts']['selector_outcomes']['actor']['successes']==14 and pub['facts']['dispatcher_routing_counts']['actor_routes']==12
 jobs=[]
 for name in ['candidate','control']:
  x=read(V/f'native-actor-move-{name}-current.json');assert x['status']=='terminal_native_actor_move_route_pending_review'and x['exit_code']==0 and x['live_monitor_pass'];ps=subprocess.run(['ps','-p',str(x['child_pid']),'-o','pid=,command='],capture_output=True,text=True);assert ps.returncode!=0,'A game child is still live';jobs.append(dict(kind=name,pid=x['pid'],child_pid=x['child_pid'],frames=x['frames'],status=x['status'],live_monitor_pass=True))
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt');text=f'''BIWN — CURRENT WORK
{now.isoformat()}

LATEST PUBLISHED GAMEPLAY-TESTED EXPERIMENT:26,220resident bytes.
Rebuilt actor movement13C9Anow runs alongside nativeactor/spritecreation routines.
Reservation28,544/free2,324;heap165D40/capacity369,344;stagingF7000/clear28,672ends
FE000, preserving Atari trailerFE520. Originaldisc unchanged. Defaultinteractive
preview is still the older verified sourceCPU/GPUcheckpoint, not this native
experiment. HoldC+Up to run;Ppauses/resumes. No preview/window/default changed.

NEW MOVEMENT CONTEXT AND REAL-HELPER RESULTS
Final13C9Acontext oracle5,248original/Croot executions(2,624cases each), four
calleeD2/helperX/savedcontext/taskboundary corruption controls reject. Snapshot
72bytes atrootSP-488;r15is logical originalworkingSP, so helper-entrycontextSP
must equalactualSP+4, notrootSP. Actual13440direction/E588division execute in
fixtures;GPU/collision effects remain prescribed there. Observerwritesneither
actualnativeCPU nor gameRAM; negative inputs alterdecodedCPU/RAMmirroronly.

Fresh actual-emulator candidate24,996frames/control29,804, bothreturnoutdoors and
hold120frames. Only8bytes13C9Aentry restored in control; shiftedstaging/reserve/
heap/unusedcode/nativecreation/priorfunctionscommon. Candidate13,898movement
entries/returns,allnative/zerooriginalbody steps;40,513,933native movement
instructions observed. Realdirection13,898/GPUsubmission13,898/outdoorcollision
3,949/indoorcollision0.31,745helpercalls/returns/context checks,zero reported
ABI/context/taskboundary errors. Movementprivate672/min246taskheadroom; finite
observedpaths only. Control16,689movement calls,1,854,731original steps and38,128
helpercalls,zero native movemententries;depth136/headroom798. Different emulated
instruction costs/schedules mean call/frame counts need not agree.

Bothretain13native dispatchreturns(12actor/1sprite),12nativeinitializers/16helpers,
1native spritecreator/3realposition-allocation-decode helpers. Contextchecks13
parent/16initializer/3sprite; all inheritedresource/cache/heap/geometry/door/
selector oracles reportzeroerrors. Actorselector14successes/0failures; sprite
selector0successes/1skippedfailure. TypedMCPfields now separate those14selector
successes from12actor dispatchroutes. Indoor movement13BB0, other helper outcome/
rollback partitions and modes,fullpools/animatedcallbacks/double-object/remaining
callback/resource/task paths still need broader live testing. A helper call is
not proof of every internal result. Retained native emulatorCPU/GPU/DSP/IRQand
platform/HLE services execute bothroutes; no newstrictCprocessorjob/physical
console proof applies to this disc.

MEDIA/STATE LIMITS
Alignedprefix24,996differs in22,826CPUframes,24,985RAMhashes,24,634GPUstate,
9,154DSPstate,21,683video,23,339navigation,478locomotion and606buttonrecords.
PCMhash/length differ79,987,200versus95,372,800bytes. Timing/video/audio/state
agreement and older scanner/initializer/creation discrepancies remain unresolved.
No whole-game speedup, complete readable same-console rebuild or physicalreadiness.

PRIOR MOVEMENT/LAYOUT CHECKS REMAIN SEPARATE
Original-facing movement2,960bytes at16489C,coordinator adapts existingportable
high-levelbody. Prototype/actual-direction/final matrices each2,624cases/all192
original sites;fullCPU/SR/banks/helperCPU/SP/args/public2MBRAM/orderedpublicaccess.
Fourmissing-body/helperX/fullD0-versuslowWORD/originaldelegation defects reject.
Newlayoutstartup96/heapinit192/nativeheapcopy-blitter3,392+ordered3,392/capacity36,
fullpayloadstartup96pass. Nine residentoperand/count relocations plusstartupJMP/
loadercopycount preserve94nonzero trailerbytes. No new logical-function count.

MIGRATION: REAL DIFFERENT-ROOT OFFLINE EVIDENCE RESTORE PILOT
Copied446canonical source/evidence/BIWNassets,3,773,677,391logicalbytes/446APFSclones.
Strictresolverchecks451artifactreadsinsidecopiedroot,withnoold-treefallback.
Standalone copiedsourceCLI passes withcurrenthostPython3.12. Outsideorigin,
parenttraversal,symlinkbacktosourcetree,andcorruptedcopiedevidence controls reject.
Originalhistoricalbytes/hashkeysremainunchanged; displayartifactpathsmaptocopy.
The pilot snapshot records23,260tested/26,220pending atcapture, notlivecurrent
status. Five terminalprocessorreceiptscapturedfromactualMCP, oldPIDsnotfollowed.
Models,fullruntime/toolchain/training/corpus/index/preset/historicalrun restoration,
fullinference/recompilationfromcopy/offmachinerestore/futurehardware remain
unverified.39model-resource46.80GBinventory/prior10shard audit are separate;
modelweightswerenotcopied,notnewlyfullyhashed. Fullworkbench migration unfinished.
Bundle:{migration['bundle_directory']}

LOCAL INFERENCE:4ACTUALPREDICTIONROUNDS THIS PASS,0NEWTRAINING
ActualmainmenuS(v12)143words/19.55seconds/2rounds/1configuredMCPcall gets numeric
component/startup/movement/selector counts correct but saysallcurrentdisccodeis
coordinatorwork,toosweeping:newmovement/creationroutinesarecoordinatorcode;
inheritedacceptedlocalhelpersandoriginalcode remain. Omitsretainedprocessors
anddetailedfullscope. Oneboundedclarification(v16)157words/21.13seconds/2rounds/
1toolcallfixesnewroutineattributionandfullscope/processors,butwronglyreports
12actorselectorsuccessesinsteadof14(confusesdispatchroutes). Rejected/notinstalled;
no furtherpromptretry. MainmenuSstillv12. TypedMCPselector_outcomesand
 dispatcher_routing_countsaddedandactualconfiguredreadverified14versus12.
This is data/workflow preparation,notprovenbettermodelanswer. Exactrawprompts/
responses/tools/statsretained;I59savedrecords,not59newpredictions. No newAuthor/
Reviewer/modelweights/defaultprofile/nativeChatUIattempt this pass. Prior7failed
Reader/AnalystReviewerpredictions remain recorded; same-weightreviews notindependent.
NativeChatpriorAX/pixel disagreement stillunverified;do notaskunlock.

FULL FOUR-PART GOAL REMAINS OPEN
Finishactualgamecode/interfaces/readablesameconsolerebuild,broader livebehavior
andtiming/media; makeeasy localfrontend/roles/models/trainingreliable. Game
native-repair-v3step32unpromotedafteroutputfailures. Advertisingoptionaltrained
step8Reviewerremainsexported/loadable,nosource-transfergainobserved;research/
teaching/review reliability unfinished. Completeportablemodels/runtime/workflows/
toolchain/workbenchrestoreandfuture256GBconfigurationpreparation. No completion
claim basedon these components or migrationpilot. No publicmessages/deployments.

Detailed movement integration:{review['report']}
Migration pilot review:{migration['report']}
Local status reviews:{delivery['report']}
Prompt viewer:{index['report']}
''';notes.write_text(text);shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 old=read(V/'actor-move-turn-integrity-current.json');hashes=dict(old['dependencies_sha256']);snap=out/'snapshots';snap.mkdir();aliases=[]
 def bind(path,h=None):
  path=Path(path).resolve();actual=sha(path);assert h is None or h==actual,(path,'changed')
  if path.name.endswith(('-current.json','-active.json')):
   dest=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name);shutil.copy2(path,dest);aliases.append(dict(mutable_pointer=str(path),immutable_exact_bytes=str(dest),sha256=actual));path=dest
  if str(path)in hashes:assert hashes[str(path)]==actual,path
  hashes[str(path)]=actual
 for obj in [review,pub]:
  for path,h in obj['dependencies_sha256'].items():bind(path,h)
 for obj in [migration,delivery]:
  for path,h in obj['source_sha256'].items():bind(path,h)
 candidate=read(V/'native-actor-move-candidate-current.json');image=Path(candidate['directory'])/'candidate/original-emulator-final-frame.png'
 extra=[Path(__file__),out/'previous-handoff.json',out/'previous-BIWN Latest Work.txt',out/'current-BIWN Latest Work.txt',Path(review['directory'])/'protocol.json',Path(migration['directory'])/'protocol.json',Path(delivery['directory'])/'protocol.json',Path(pub['directory'])/'publication.json',Path(index['directory'])/'manifest.json',Path(index['report']),Path(index['source_list_snapshot']),ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-move-readme.txt',V/'actor-move-current-MCP-read.json',image,V/'actor-move-integration-reviewed-current.json',V/'evidence-restore-pilot-reviewed-current.json',V/'movement-status-readers-reviewed-current.json']
 for path in extra:bind(path)
 def check(item):
  path,h=item
  try:return None if sha(path)==h else dict(path=path,error='hash changed')
  except OSError as e:return dict(path=path,error=str(e))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(check,hashes.items())if x]
 integrity=dict(status='terminal_movement_live_migration_and_inherited_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(hashes),issues=issues,dependencies_sha256=hashes,historical_mutable_pointer_resolutions=aliases,scope='Boundsource/binary/report/metadata/historicalsnapshots,notanewfullmodelweightaudit/wholegame/hardware/modelqualityproof.');save(out/'integrity.json',integrity);save(V/'actor-move-live-turn-integrity-current.json',integrity);assert not issues,issues
 preview=[]
 for pid in [233,235]:
  result=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True)
  if result.returncode==0:preview.append(dict(pid=pid,command=result.stdout.strip()))
 state.update(status='active_actor_movement_real_helpers_published_full_game_model_migration_remain',recorded_at=now.isoformat(),prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,previous_turn_classification='Progress:13C9AoriginalABI2960bytes/2624all192sites,28544shiftedlayout/trailer/heap/startup checks,new26220discstartup; livecontexts/realhelperspending.7localpredictionsrejected.',this_turn_classification='Progress:5248movementcontext executions/4corruption controls pass. Twoactualnative-emulatorroutes24996/29804returnedoutdoors,candidate13898movementreturns/31745realhelpers/canaries,3949outdoorcollision/0indoor,zeroABI/context/taskerrors.26220publishedwithmedia/state/timinglimits. Offline3.77GBevidence/BIWNclone446files/451inside-rootchecks/4negatives/standalonecopiedCLIpasses;fullrestore/modelsnotdone. ActualS143wordnumericrightbutoverbroadauthorship;v16157wordswrong12versus14selectorcount,rejected.TypedMCPcountsverified.59savedrecords;integrityverified.',latest_built_disc_resident_bytes=26220,latest_published_live_build_resident_bytes=26220,latest_built_disc_game_frames=24996,latest_actor_move_review=str(V/'actor-move-integration-reviewed-current.json'),latest_context_oracle=str(V/'actor-move-live-contexts-current.json'),latest_migration_review=str(V/'evidence-restore-pilot-reviewed-current.json'),latest_local_status_delivery=str(V/'movement-status-readers-reviewed-current.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(hashes),finite_jobs=[],finite_jobs_pending=0,completed_finite_jobs=jobs,completed_current_turn_sessions=[85207,35923,34558,88642,42392,96029,47863,47931,31092],local_model_work_this_continuation=dict(actual_prediction_rounds=4,Reader_deliveries=2,actual_MCP_calls=2,words=[143,157],seconds=[19.547724750009365,21.133273332961835],candidate_installed=False,new_code_Author_predictions=0,new_training=False,native_Chat_verified=False),local_model_work_since_previous_handoff=dict(total_actual_predictions=4,Reader_rounds=4,Author_Reviewer_predictions=0,accepted_new_local_code=False,weights_changed=False),interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='HoldC+Up;Ppauses/resumes',recipe='Older verified sourceCPU/GPUcheckpoint,notcurrent26220nativedisc'),last_native_game_frame=str(image),next_actions=['Continueactualgame-sourceinterfaces;13C9Acompletedreal-helperroutesbutfullreadablesameconsolebuild/remaininggamecodeunfinished. Consideroriginal-facingcollision13B5A/13BB0next; prototypeportablecollision/sourcefullGPUchecksarehistoricalandmustnotbesubstitutedfornewnativeABI/actualcallerproof.','Broadenmovement13BB0indoorcollision/liveoutcomepartitions/rollback,callback/fullpool/resource/taskpaths. Currentcandidate13898movementcalls/31745helpers includes3949outdoorand0indoor. Maxmovement672/minheadroom246isobservednotgeneralbound. Media/state/timingdifferenceunresolved; keepdefaultpreviewunchanged.','Migrationpilotfirstactualdifferentroot:446files3.773677391GB/451inside-rootchecks,4escape/corruptioncontrols,standalonecopiedCLIwithcurrentPython3.12. Historicalsnapshot23,260tested/26,220pending;noPIDfollowed/nosourcefallback. NextcoldrelocatedMCP/runtime/toolchain/corpus/index/presets/models/workflowrestorestillneeded;47GBweightsnotcopiedandnooffmachine/futurehardwareproof. Preservehashedhistoricalbytesandstrictpathmapping.','CurrentSstillv12. Latest143wordnumericcorrectbutall-codeattributionoverbroad; v16clarification157wordscorrectscopebutwrong12selectorversus14(rejected). NewtypedMCPselector_outcomes14/0and0/1skippedversusdispatcher12/1verified; useforthcomingautomatedfactchecks. No blindretries/defaultchanges/newweights. Sourcecodecurrentnewroutinescoordinator; inheritedlocalhelpers/originalgamecoderemain.','NativeChatpriorAX/pixelmismatchunverified; noUIattemptthisturn. Do notaskunlock/repeatidenticalactions. ContinueSDK/tools/savedpromptswhereallowed. Game step32unpromoted;Advertisingoptionalstep8loadablebutnogain/review-teachingreliabilityremain. Fullfourpartgoalactive.','Allfinitejobsthispasscompleted; donotrestartthem. CurrentpreviewPIDs233/235unchanged. CurrentMCPpublication26220containsactualmovementandseparatemigrationpilotfacts;5olderstrictCprocessorjobsremainterminalonlyownhashes.'],no_completion_claim=True,handoff_script_sha256=sha(Path(__file__)))
 state['current_entrypoints']['prompts_I']='59saved prompt/transcript records;4newReaderpredictionroundsthispass,not59newpredictions'
 state['full_goal_requirements'][0]['evidence']=delivery['report'];state['full_goal_requirements'][0]['remaining']='SDK/CLI/configuredMCPwork;currentS143wordnumericcorrectbutoverbroadauthorship;v16wrongselectorcount/rejected.Newtypedfieldsseparate14selectorfrom12routesbutbettermodeloutputnotproved.NativeChatstillunverified;easyreliablelocalinference/role/trainingunfinished.'
 state['full_goal_requirements'][1]['evidence']=review['report'];state['full_goal_requirements'][1]['remaining']='26,220nativeexperimentaldiscnowpassesactualmovementhelperroutes13898calls/31745helpers/canariesandzeroABI/context/taskerrors.Indoorcollision0andbroaderoutcomescomponent-only;media/state/timingdiffer.Fullreadablegame/sameconsolebuildandremainingactualsourceinterfacesunfinished.'
 state['full_goal_requirements'][3]['evidence']=migration['report'];state['full_goal_requirements'][3]['remaining']='Actualsamehostdifferentrootcanonicalevidence/BIWNrestore446files/3.77GB/451inside-rootchecks/4controls/standaloneCLIpasses.Historicalsnapshot,notfullruntime/models/toolchain/training/corpus/index/preset/workflowrestore/offmachineproof.Prior39resource46.80GBmodelinventory/10shardauditremainseparate.Future256GBpreparationunfinished.'
 save(out/'protocol.json',state);save(pointer,state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),event='native_movement_real_helpers_and_portable_evidence_pilot',coordinator='Movementoracle/negatives/realroutes/integration/review/publication/strictrelocatedevidencerestore/typedfields',local_models='ActualcurrentSReader2rounds+boundedv16Reader2rounds;numeric/scopefailuresretained,candidatenotinstalled',actual_predictions=4,new_training=False,published_resident_bytes=26220,frames=[24996,29804],movement_calls=13898,actual_helpers=31745,migration_copied_files=446,migration_verified_artifact_reads=451,full_migration=False,bound_files_verified=len(hashes),goal_complete=False))+'\n')
 print(json.dumps(dict(status=state['status'],bound_files=len(hashes),published=26220,pending_jobs=0,goal_complete=False,notes=str(notes))))
if __name__=='__main__':main()
