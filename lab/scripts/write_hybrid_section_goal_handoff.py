"""Keep all four goal requirements active after hybrid gameplay and advertising source work."""
import copy,json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();prior=read(V/'goal-continuation-current.json');save(out/'previous-handoff.json',prior)
 publication=read(V/'current-biwn-latest-publication-current.json');game=read(V/'navigation-hybrid-integration-reviewed-current.json');ad=read(V/'advertising-source-sections-reviewed-current.json');installed=read(V/'reference-section-frontend-installed-current.json');mcp=read(V/'hybrid-section-full-status-current.json');index=read(V/'current-model-work-index-v4-current.json');cold=read(V/'cold-runtime-model-reviewed-current.json');loaded=read(ROOT/'runs/hybrid-section-LM-Studio-model-state.json')
 assert publication['facts']['experimental_build']['resident_bytes']==mcp['response']['experimental_build']['resident_bytes']==30036 and game['comparison']['PCM_equal']
 assert mcp['response']['advertising_workflow_progress']['actual_local_predictions']==4 and ad['trained_Reviewer_false_pass']and index['saved_prompt_or_transcript_records']==68
 assert len(loaded)==1 and loaded[0]['modelKey']=='local/advertising-qwen38'and loaded[0]['contextLength']==32768 and loaded[0]['parallel']==1 and loaded[0]['status']=='idle'
 jobs=[]
 for name,needle in [('navigation-hybrid-live-observer-current.json','qualify_native_navigation_hybrid_observer'),('native-navigation-hybrid-candidate-current.json','run_biwn_navigation_hybrid_route'),('native-navigation-hybrid-control-current.json','run_biwn_navigation_hybrid_route'),('advertising-source-sections-team-current.json','run_source_section_advertising_team'),('advertising-source-sections-lesson-revision-current.json','revise_source_section_advertising_lesson')]:
  obj=read(V/name);assert obj['status'].startswith('terminal_');observations=[]
  for pid in [p for p in [obj.get('pid'),obj.get('child_pid')]if p]:
   r=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True);alive=r.returncode==0 and(needle in r.stdout or str(Path(obj['directory'])/'probe.py')in r.stdout);assert not alive,(name,pid);observations.append(dict(pid=pid,live_matching_worker=False,handle_missing=r.returncode!=0))
  jobs.append(dict(pointer=name,status=obj['status'],process_observations=observations))
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt')
 notes.write_text(f'''LOCAL AI LAB — CURRENT VERIFIED WORK
{now.isoformat()}

The full four-part goal remains active. Previous goal turn: progress; this turn:
progress through actual hybrid integration/gameplay, installed section retrieval,
four local advertising predictions and source review. No completion percentage.

LATEST GAMEPLAY-REVIEWED BIWN EXPERIMENT:30,036 NATIVE BYTES
The corrected local13F12 draft is integrated as explicitly attributed hybrid C:
3 coordinator corrections(writeD1,preserveearlyX,clearZonsuccess). The other3
navigation roots remain coordinator C; earlier inherited local helpers retain
attribution. No unchanged raw model output was adopted. No new game prediction
or weight training occurred this turn. Original/parent CDI hashes remain intact.
Only1,402 actual CDI bytes changed,within the declared navigation-tail/four-entry
regions. First28,448 resident bytes,heap/reservation/staging/loader/trailer unchanged.

Hybrid prototype/final groups each pass6,144 original-facing cases/all209 sites;
hybrid13F12 has1,536 cases per matrix. Actual remaining helpers are not prescribed
for these4leaf roots. CPU/SR/banks/public2MBRAM/ordereddataaccess compare tooriginal.
Valid stored computed targets only; privateframes/installation/returnPC exclusions.
New rendered monitor passes440 original/native executions and4 decoded-observation
negatives; full30,036byte payload startup passes96 cases. Prior same-floor heap/
capacity proofs remain valid through byte-identical preserved prefix. No new heap
change:30,080reserved/free44,heap166340,stagingF6C00..FE200;Atari trailer preserved.

Fresh candidate and original-navigation control EACH complete24,610frames and
return outdoors. Navigation native/original returns9/4/4/3;20 contextentries/20
returns;allmonitors pass. Native private depths180/136/176/176;minimumheadrooms
758/796/758/762. Sharedchain6,377movement/3,889outdoorcollision returns;indoor0;
maxprivate564/minliveheadroom370(tighterfixture354). Creation15routes(13actor/
2sprite),initializer13returns/18helpers,spritecreator2returns/6helpers. Selector
outcomes are different counts:14actor successes,2sprite failures(1skipped and
1non-skipped). Sprite success and actor failures remain component-only.

Fresh-pair captured PCM is byte-identical:78,752,000bytes each. Full DSP state
hashes match all24,610alignedframes. Differences remain:CPU6,974;RAM24,602;
GPU24,106;video1,404;navigation1,091;locomotion9;buttons8. FullRAM hashes include
intentional entrypatch/privateframe changes and do not alone locate an error.
Raw runner PCM_equal/frame_differences compare an OLDER HISTORICAL reference;
use the fresh-pair review.comparison for candidate-versus-current-control claims.
Different timing/adaptive inputs/inherited discrepancies remain. Retained native
emulatorCPU/GPU/DSP/IRQ/platform/HLE;no host processor replacement,physicalconsole
boot,wholegameaudio equality or whole-game speedup claim. Full readable game and
same-console source reconstruction remain unfinished. Earlier fixed-east-exit
failure remains retained; fresh routes use current room19FDA/1028E records and
ordinary buttons for the south exit. Different room selection vs smallerlayout
is not fully isolated. No RAM restore/position patch/host guest-memory write.
Game review:{game['report']}
Build:{V/'native-navigation-hybrid-disc-build-current.json'}

ADVERTISING SOURCE ACCESS / ACTUAL LOCAL ROLE OUTPUT TEST
Installed actual MCP entry:chat_tools_current_v10.py with reference_sections_v2.
Document-heading/study-ID selection supplies original design/procedure/measurement
pages;explicit page lists and ranges are supported(max6). Four positive actual
MCP queries for1PDF,out-of-range rejection,unchanged game search/status pass;
18tools stay registered. Entryv8 had a startup syntax error before liveconfig
changed;v9 corrected it;v10 handles page ranges. Failed files remain preserved.
Original supplied PDFs/indexes are unchanged. Config backup:{installed['configuration_backup']}
The actual configured MCP now serves both current30,036byte game status and
source sections. Native Chat display/provider adoption remains UNVERIFIED.

One base Researcher23.07s/base Educator24.21s/trained Reviewer10.16s run against
exposed Schreiner2026Study2A evidence;one informed base Educator revision19.36s.
Four actual predictions,not training. Researcher183words violates150limit and
calls aversion pre-existing;Educator repeats it and its original rubric scores
items not explicitly asked. Sourcep9 finally measures aversion after ads/follow-
ups;this is not an established pretreatment baseline. Timing does not prove the
ads changed aversion. Sourcep20:4seven-point items,reversecoded. Researcher also
calls ad attitude primary without support in the citedmethods;source listsother
outcomes. Trained Reviewer returns emptyissues/usabletrue:actual falsepass.

Local revision214words removes baseline wording but still bundles rubric facts
and uses broad causal wording. Coordinator final lesson199words has explicit
measurement timing,2questions and4single-point criteria,0for incorrect. It is
source-checked coordinator-edited material,not unchanged localoutput,independent
model review or evidence of weight-quality gain. All raw drafts/revision remain.
Lesson:{ad['friendly_lesson']}
Advertising review:{ad['report']}
General research/teaching/reviewer reliability and source-aware ordinaryCLI teams
remain open;avoid assuming the section lookup alone fixes model interpretation.
Schreiner is exposed reference material,not a new held-out evaluation source.

MODELS / PROMPTS / FRONTEND
Daily base27B6bit remains loaded32Kcontext/1worker,idle. Optional trained source
Reviewer step8 remains loadable/experimental;game step32 adapter remains unpromoted.
Related-weight role contexts are not independent review. No optimizer updates or
newweights/default-model promotion. Exact saved prompt/transcript records:68;
this turn adds4actualadvertising predictions. Refresh Model Prompts and Responses.command.
{index['report']}
The visible keyboard preview remains unchanged;click gamewindow,C+Up runs.
Local API/MCP outputs do not establish native LM Studio Chat-window streaming.
No new UI/unlock request or unsupported native display success is claimed.

FULL SCOPE / NEXT WORK
1.Make inference/visible local roles/ordinary source-aware CLI workflows reliable;
  prioritize source-method timing and quiz/rubric alignment,including Reviewer
  false negatives. NativeChat remains unverified,not a global headless blocker.
2.Continue readable actual game task/callgraph recovery and remaining outcomes;
  do not substitute whole-processor reimplementation. Preserve originalimages.
3.Advertising research/education:base+optionaltrainedReviewer are ready toload;
  one corrected lesson/general section tool is progress,not broadquality readiness.
4.Finish the portable SDK/CLI/toolchain/training/first-use package for future256GB
  use. Actual cold package:{cold['package']}
  Previous39resource/10shard copied-model loading and7of18MCPtoolkinds/4boundary
  controls remain scoped proofs. Copied CLI wrappers still route old source paths;
  SDK control client was original workbench. Cold package hasv7/26,220snapshot;
  newv10section modules/config still need inclusion. No fullportable workflow,
  off-machine execution or futurehardware benchmark is claimed. Prepare the
  portable256GBprofile here;do not treat an unavailable futureMac as evidence.
All finite jobs in this continuation are terminal;no permission question pending.
''');shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 deps=dict(read(V/'native-navigation-turn-integrity-current.json')['dependencies_sha256']);aliases=[]
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  mutable=(p.parent==V and p.name.endswith(('-current.json','-active.json')))or p in[notes,ROOT/'config/current-model-work-sources.json',ROOT/'reports/Advertising Source Lesson.txt']or not p.is_relative_to(ROOT)
  if mutable:
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name[-160:]);shutil.copy2(p,target);aliases.append(dict(original=str(p),snapshot=str(target),sha256=actual));p=target
  assert str(p)not in deps or deps[str(p)]==actual,str(p);deps[str(p)]=actual
 for obj in[publication,game,ad,cold]:
  for p,h in obj['dependencies_sha256'].items():bind(p,h)
 for obj in[installed,mcp]:
  for p,h in obj['source_sha256'].items():bind(p,h)
 for name in ['current-biwn-latest-publication-current.json','navigation-hybrid-integration-reviewed-current.json','native-navigation-hybrid-disc-build-current.json','navigation-hybrid-live-observer-current.json','navigation-hybrid-final-startup-current.json','advertising-source-sections-reviewed-current.json','reference-section-frontend-installed-current.json','hybrid-section-full-status-current.json','current-model-work-index-v4-current.json']:bind(V/name)
 for p in[Path(__file__),out/'previous-handoff.json',out/'previous-BIWN Latest Work.txt',out/'current-BIWN Latest Work.txt',notes,ROOT/'config/current-model-work-sources.json',ROOT/'reports/Advertising Source Lesson.txt',ROOT/'runs/hybrid-section-LM-Studio-model-state.json',Path(index['report']),Path(index['source_list_snapshot']),Path(index['directory'])/'manifest.json',Path.home()/'.lmstudio/mcp.json']:bind(p)
 def verify(row):
  p,h=row
  try:return None if sha(p)==h else dict(path=p,error='SHA mismatch')
  except Exception as error:return dict(path=p,error=repr(error))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(verify,deps.items())if x]
 integrity=dict(status='terminal_hybrid_section_inherited_integrity_pass'if not issues else'terminal_hybrid_section_integrity_failed',directory=str(out),unique_bound_files=len(deps),issues=issues,dependencies_sha256=deps,historical_mutable_pointer_resolutions=aliases,scope='Inherited2071bindings plus current hybrid/gameplay/source-section installation/localrole/lesson/MCP evidence. Mutable notes/config/pointers/friendlylesson frozen.');save(out/'integrity.json',integrity);save(V/'hybrid-section-turn-integrity-current.json',integrity);assert not issues,issues[:5]
 state=copy.deepcopy(prior);requirements=state['full_goal_requirements'];requirements[0].update(evidence=installed['directory'],remaining='ActuallocalAPI/MCP/modelroles and32Kdailybasework; installedgeneraloriginal-source sections improveaccess. NativeChat/easyfirstuse/genericCLI/source/reviewer reliability remainunfinished.4newlocalpredictions,nooptimizerupdates.');requirements[1].update(evidence=game['report'],remaining='30036nativebytes/hybrid13F12integrated;prototype/final6144each,96startup/440observer andfresh24610frame roundtrip/control pass. CapturedPCM/DSPequal,butvideo/state/navigation differ. Fullreadableactualgame/taskinterfaces/sameconsole sourcebuild andunobservedpaths remainunfinished;no physicalconsole claim.');requirements[2].update(evidence=ad['report'],remaining='Base+step8Reviewerloadable;general sectionretrievalinstalled,one199wordcoordinatorlessonchecked. Fourlocalrolecalls showbaseline/rubricerrors andtrainedReviewerfalsepass. Research/education/sourceinterpretation reliability remainsunfinished,noqualitygain/newweights.');requirements[3]['remaining']='Coldpackageruntime/copiedmodels scopedproofs retained;fullportableSDK/CLI/toolchain/training/sourcebuild/onboarding/alltoolbehaviors anddocumented256GBprofile remainunfinished. CopiedCLIoldpaths andv7snapshotneedrepair/newv10modules. No offmachine/futurehardwarebenchmarkclaim.'
 state.update(status='active_hybrid_navigation_gameplay_pass_section_frontend_and_advertising_review_full_goal_remains',recorded_at=now.isoformat(),previous_turn_classification='Progress:4native navigationroots/disclayout/live roundtrip andhybridprototype/finalcomponentverified; allfourrequirementsincomplete.',this_turn_classification='Progress:hybridlocal13F12integrated30036bytes;96startup/440observer/freshcandidate+control24610frame roundtrips pass;PCMbyteequal,DSPequal,videostill1404different. General originalPDFsectionretrievalv10 installed/actual18toolMCPverified;4actual advertisingpredictions/source review identifytrainedReviewerfalsepass andproduce199wordcoordinatorlesson.68savedrecords;allnew/inheritedbindingsverified.',prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,full_goal_requirements=requirements,latest_published_live_build_resident_bytes=30036,latest_built_disc_resident_bytes=30036,latest_built_disc_game_frames=24610,latest_native_navigation_build=str(V/'native-navigation-hybrid-disc-build-current.json'),latest_native_navigation_live_review=str(V/'navigation-hybrid-integration-reviewed-current.json'),hybrid_disc_integrated=True,latest_Advertising_review=str(V/'advertising-source-sections-reviewed-current.json'),latest_frontend_readiness=str(V/'reference-section-frontend-installed-current.json'),latest_local_status_delivery=str(V/'hybrid-section-full-status-current.json'),latest_model_work_index=str(V/'current-model-work-index-v4-current.json'),latest_integrity=str(V/'hybrid-section-turn-integrity-current.json'),finite_jobs=jobs,finite_jobs_pending=[],local_model_work_this_continuation=dict(actual_predictions=4,domain='advertising',role_seconds=[23.07,24.21,10.16,19.36],trainedReviewer_false_pass=True,source_checked_final_lesson_authorship='Coordinator',new_game_predictions=0,prior_local_game_draft_hybrid_integrated=True,new_training=False,saved_records=68),next_actions=['Complete portable SDK/CLI/toolchain/training/first-use restore andinclude livev10sections;oldabsoluteCLIpaths remain.','Improve method-focused retrieval/ordinarysource-awareteam andfield-leveltiming/rubric verification;trainedReviewerfalsepass retained.','Continue readableactualgame/taskcallgraph source andabsentoutcomes/indoorcollision;keepfutureprofile andAdvertising in scope.','Verify nativeChatwhenobservablestatepermits;no unlockrequests or unsupporteddisplayclaims.'],final_integrity_unique_files=len(deps),no_completion_claim=True)
 save(out/'handoff.json',state);save(V/'goal-continuation-current.json',state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),event='hybrid_gameplay_and_advertising_source_sections_verified',coordinator='Codex',game_hybrid_adopted=True,game_resident_bytes=30036,game_new_predictions=0,advertising_actual_predictions=4,roles=['Researcher','Educator','trainedSourceReviewer','Educator informedrevision'],trainedReviewer_false_pass=True,source_checked_lesson_authorship='Coordinator',live_MCP_entrypoint='v10',nativeChat_verified=False,new_training=False,goal_complete=False,integrity_files=len(deps),handoff=str(out/'handoff.json')))+'\n')
 print(json.dumps(dict(status=state['status'],goal_complete=False,resident_bytes=30036,new_predictions=4,integrity_files=len(deps),finite_jobs_pending=0)))
if __name__=='__main__':main()
