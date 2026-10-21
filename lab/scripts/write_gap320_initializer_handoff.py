"""Preserve full objective after the wider-gap live test and next native component."""
import json,hashlib,shutil,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);pointer=V/'goal-continuation-current.json';state=read(pointer);shutil.copy2(pointer,out/'previous-handoff.json')
 review=read(V/'actor-gap320-and-initializer-reviewed-current.json');delivery=read(V/'current-gap320-status-delivery-current.json');plan=read(V/'actor-initializer-layout-plan-current.json');overlap=read(V/'joint-actor-frame-overlap-negative-current.json');publication=read(V/'current-biwn-latest-publication-current.json');index=read(V/'current-model-work-index-v4-current.json')
 assert publication['facts']['experimental_build']['resident_bytes']==19460 and review['min_observed_context_clearance']==70 and delivery['actual_predictions']==2
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt')
 text='''BIWN — CURRENT WORK
'''+now.isoformat()+'''

LATEST PUBLISHED EXPERIMENTAL DISC:19460resident bytes,13AE0dispatcher with320byte private gap,572native bytes, unchanged20480reserve and heap163DC0,1020free. Coordinator body/ABI/layout/verifiers. No localAuthor code adopted for this dispatcher; earlier accepted local functions retain separate attribution.

DEFAULT INTERACTIVE PREVIEW IS UNCHANGED. Its existingPIDs233/235run the separately verified older sourceCPU/GPU checkpoint/overlay recipe, not this new native-disc build. HoldC+Up to run;Ppauses/resumes. No window was operated or restarted this turn.

DISPATCHER:856fullCPU/SR/banks/publicRAM/ordered cases/all38original sites at prototype/final address;96startup. Read-only oracle856original+856compiled fixtures, wrongD0/wrongchildX/context-overlap negatives. Fresh candidate24983frames/control24996bothreturnoutdoors.13calls each:12actor/1sprite,0fullpoolreturns. Actual child/rootABI, args, return and task/context checks pass. Candidate392private depth/390minimumtask headroom; actual originaldescendants194belowroot,70measured context bytes clear,0collisions. This is finite observed coverage, not a general stack bound.

Compared with prior256gap variant, both new routes preserve every recorded video/GPU/DSP/navigation/locomotion/button frame and full capturedPCM. CandidateCPUdiffers1frame/control0; RAMhashes differ24810/24823because changed code/private frames remain in full snapshots. Against the fresh original-dispatcher-entry control, candidate still differs17515video frames; PCMhash/length,CPU/RAM/GPU/DSP/navigation/input state differ. Timing/media equivalence remains unresolved. Fullpoollive path remains component-only; inherited selectors still14actor successes/1sprite skipped failure, other paths component-only. Oldscanner media limits persist.

NEXT SOURCE COMPONENT134DC: complete high-level C initializer with original-facing helper captures passes1024fullCPU/SR/banks/publicRAM/ordered cases/all148sites.1620bytes/private564,gap448. Joint native13AE0+134DCpasses856cases/max600private stack. Original10520executes; geometry102C4/taskDF6Cand other leaf helpers remain scripted in component proof. Three no-body/helperX/original134E0delegation controls reject. A diagnostic320gap initializer passes16isolated native cases but corrupts its caller when nested; exact fetch-error rejection and overlap of caller returnPCare recorded. Current448gap joint succeeds. Not disc-integrated or new logical-function recovery.

LAYOUT PLAN ONLY: initializer exceeds1020free by600. Read-only plan identifies7decoded heap-floor/+4/+8operands and loaderWORD27FF→2FDF for a possible24512reserve/heap164D80; newused21080/free3432/stagingtail24. Heap capacity377408→373376. No allocator/reserve/loader/disc layout change adopted. Needs full final-address/heap/resource/task/startup/live checks. ParentSP-only collision guard must become a context-canary/interval check for nested native frames that legitimately skip over parent state.

WHOLE-GROUP C ABI: separate3384byte13AE0/134DC/137E0/10520/105DAcomponent remains uninserted;2596coupled cases/native replays. Original-facing134DCsource is a separate later component; remaining137E0/interfaces/realhelpers/fullgame still unfinished.

C PROCESSORS: five older16872/17084/17812/18270/18888disc jobs are terminal/equal only for their own hashes.18888independently matches24996frames/all8fields/79987200PCMbytes/fullobserver. None applies to latest19460gap320. No new processor-emulator reconstruction/job was started.

EASY LOCAL INFERENCE: actual StartLocalAI→S used one configuredMCPcall,2localpredictionrounds,144words/19.19seconds. Core newbuild/routing/attribution/media/job-applicability claims correct, but retained-processor, component-only, Advertising/preview and other detailed scope is omitted; full report remains authoritative. Same localbase27B; no new codeAuthor calls or weight updates. Ishows52saved prompt/transcript records (current-reader pointer refreshed; not52newpredictions). Exact prompts/responses retained.

MODELS/FRONTEND: SDK/CLIand configuredMCPv7work; current nativeChat remains unverified after prior120.61sSkytimeout. No identicalUIretry or unlockrequest this turn. Prior native role display is separate. Game native-repair-v3completed64updates/step32selected but unpromoted failed code outputs. Advertising optionalstep8trainedReviewer is loadable; latest source-transfer test shows no observed gain overbase and remaining reliability limits. No new training this turn. Modeltransfer39files/46.80GB/10shard integrity exists; full-workbench relocation/future256GBhardware remain unverified. Full readable game/original-console rebuild remains unfinished.

Detailed source/live report: '''+review['report']+'''
Actual local status review: '''+delivery['report']+'''
Layout plan: '''+str(Path(plan['directory'])/'protocol.json')+'\n'
 notes.write_text(text);shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 old=read(V/'actor-dispatch-turn-integrity-current.json');hashes=dict(old['dependencies_sha256']);resolutions=[]
 candidates={str(V/'current-model-work-index-v4-current.json'):ROOT/'reports/model-work-index',str(V/'current-biwn-latest-publication-current.json'):V/'current-biwn-latest-publication'}
 for key,folder in candidates.items():
  if key in hashes and sha(key)!=hashes[key]:
   expected=hashes.pop(key);name='manifest.json'if'model-work' in str(folder)else'publication.json';matches=[p for p in folder.glob('*/'+name)if sha(p)==expected];assert matches,(key,'Exact old metadata unavailable');hashes[str(matches[0])]=expected;resolutions.append(dict(mutable_pointer=key,immutable_exact_bytes=str(matches[0]),sha256=expected))
 for obj in [review,publication]:hashes.update(obj['dependencies_sha256'])
 for obj in [delivery,plan,overlap]:
  for p,h in obj['source_sha256'].items():assert sha(p)==h,p
  hashes.update(obj['source_sha256'])
 extra=[Path(__file__),out/'current-BIWN Latest Work.txt',Path(review['directory'])/'protocol.json',Path(delivery['directory'])/'protocol.json',Path(plan['directory'])/'protocol.json',Path(overlap['directory'])/'protocol.json',Path(publication['directory'])/'publication.json',Path(index['directory'])/'manifest.json',Path(index['report']),Path(index['source_list_snapshot'])]
 for p in extra:hashes[str(p)]=sha(p)
 def check(item):
  p,h=item
  try:return None if sha(p)==h else dict(path=p,error='hash changed')
  except OSError as e:return dict(path=p,error=str(e))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(check,hashes.items())if x]
 integrity=dict(status='terminal_gap320_initializer_and_inherited_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(hashes),issues=issues,dependencies_sha256=hashes,historical_mutable_pointer_resolutions=resolutions,scope='Integrity and exact historical snapshots; not whole-game/model/hardware proof.')
 save(out/'integrity.json',integrity);save(V/'gap320-initializer-turn-integrity-current.json',integrity);assert not issues,issues
 preview=[]
 for pid in [233,235]:
  p=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True)
  if p.returncode==0:preview.append(dict(pid=pid,command=p.stdout.strip()))
 state.update(status='active_gap320_live_and134DC_component_ready_layout_integration_pending',recorded_at=now.isoformat(),prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,
  previous_turn_classification='Progress:19460gap256dispatcher component/startup/two real game routes pass13calls; observed6byte clearance estimate and media differences retained.18888C job independently completed. Local2prediction dispatcher trial rejected, one SFTexample prepared.',
  this_turn_classification='Progress:320gap keeps572code bytes and passes856fullABI/96startup; oracle1712cases/3negatives. Two new real routes preserve previous variant media/navigation, measure70context clearance/0collisions/392private/390headroom. New134DCnative highlevel initializer1620bytes passes1024cases/all148sites; joint2native routines856cases/600private. Three initializer negatives and isolated-valid-but-nested-corrupt320gap control reject;448joint passes. Read-only24512reserve/7heap operands/loader plan prepared, not adopted. Published current19460gap320via unchangedMCPschema; actual main-menuS2Readerrounds/one tool/144words19.19s core correct with scope omissions. No newCodeAuthor/weights/UIattempts;52saved records. Integrity verified.',
  latest_built_disc_resident_bytes=19460,latest_published_live_build_resident_bytes=19460,latest_actor_dispatch_build=str(V/'native-actor-dispatch-gap320-disc-build-current.json'),latest_actor_dispatch_review=str(V/'actor-gap320-and-initializer-reviewed-current.json'),latest_actor_initialize_component=str(V/'native-actor-initialize-current.json'),latest_joint_actor_component=str(V/'native-actor-dispatch-initialize-joint-current.json'),latest_initializer_layout_plan=str(V/'actor-initializer-layout-plan-current.json'),latest_local_status_delivery=str(V/'current-gap320-status-delivery-current.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(hashes),finite_jobs=[],finite_jobs_pending=0,completed_current_turn_sessions=[71063,37518,14811,2933,13538,12405,54909,3167,24154],
  local_model_work_this_continuation=dict(actual_prediction_rounds=2,role='CurrentstatusReader through actual mainmenuS/configuredMCPv7',seconds=delivery['seconds'],words=144,tool_calls=1,Editor=False,new_code_Author_predictions=0,new_training=False,native_Chat_verified=False),
  interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='HoldC+Up;Ppauses/resumes',recipe='Older verified sourceCPU/GPU checkpoint/overlay; not the latest native-disc build'),
  next_actions=[
   'Integrate actual134DCsource next:1620bytes exceed1020free. Read-only plan identifies7heap-floor/+4/+8operands and loader count;24512reserve/heap164D80fits existing staging clear with24tailbytes. Newinitializerfinaladdress1639C4,used21080/free3432. Do not adopt without byte provenance/final relink/nativeheap/resource/task/startup/live tests and appropriate layout/original-entry controls.',
   'Before joint gameplay, replace SP-only parent-context collision rule with actual parent-context canary/known interval checks. Native134DClegitimately skips below the parent frame. Current private448joint passes600depth; a320variant passes16isolated nativecases but nested context[-388,-312)overwrites caller returnPC[-344,-340), causing checkedUC_ERR_FETCH_UNMAPPED. Preserve that qualification and all as-run files.',
   'New initializer standalone1024cases/all148sites, real original10520 and scripted102C4/DF6C; three seeded no-op/helperX/original134E0delegation controls reject. Joint856cases cover134distinct sites across both routines, not all186possible combined sites. Original-facing137E0and remaining actualhelper/source-game reconstruction remain.',
   'Current published experiment is19460gap320, still default_promotedFalse. Two live routes24983/24996each13dispatches12actor1sprite/0fullpool. Measuredactualhelperdepth194leaves70contextclearance; candidate392private/390taskheadroom. Newvsoldgap media/navigation unchanged, but freshoriginal-entry control video/PCM/state/navigation discrepancies persist. Oldscanner media limits and component-onlypaths remain.',
   'All5namedstrictCprocessorjobs terminal onlyon16872/17084/17812/18270/18888; none applies to19460gap320. No new whole-emulator provider effort needed to port next actual game function.',
   'MainmenuSactualSDKReader144words19.19seconds/2rounds/1MCPcall, corefactsaccurate with explicitly retained omissions; I52saved records. NativeChatlastSkytimeout is a separate unverified surface; do not repeat identical UI attempts or ask an unlock. No newcodeAuthor/trainingthisturn.',
   'Preserve full objective: easylocalfrontend/roles and effective game/admodels,complete readable game/same-console build,fullmigration/future256GBpreparation. Existing game step32 unpromoted; Advertising optionalstep8loadable/noobservedtransfergain. Fullworkbenchrelocation and futurehardwareunverified. CurrentpreviewPIDs233/235remain oldercheckpoint/sourceoverlay, not newnative19460disc; do not silently restart it.'
  ],no_completion_claim=True,handoff_script_sha256=sha(Path(__file__)))
 state['current_entrypoints']['prompts_I']='52saved records; reader pointer refreshed, not52newpredictions'
 state['full_goal_requirements'][1]['evidence']=review['report'];state['full_goal_requirements'][1]['remaining']='Latest19460gap320dispatcher live-tested13calls with70measuredcontextclearance.134DC1620byte original-ABI component/joint prototype passes, not yet disc-integrated; requiresmemorylayout and real nested-frame/helper validation. Remaining137E0/fullreadablegame/original-console rebuild/timing/mediaunfinished.'
 save(out/'protocol.json',state);save(pointer,state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),event='gap320_live_safety_and134DC_native_source_progress',coordinator='Allcode/ABI/fixtures/contextoracle/layoutplan/integration/review/publication',local_model='StatusReader2rounds/oneactualMCPcall',actual_predictions=2,new_code_Author_predictions=0,new_training=False,report=review['report'],status_review=delivery['report'],published_resident_bytes=19460,initializer_disc_integrated=False,bound_files_verified=len(hashes),goal_complete=False))+'\n')
 print(json.dumps(dict(status=state['status'],verified_files=len(hashes),pending_jobs=0,published=19460,initializer_bytes=1620,goal_complete=False)))

if __name__=='__main__':main()
