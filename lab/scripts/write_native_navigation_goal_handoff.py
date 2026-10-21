"""Save current evidence without narrowing the four-part goal or claiming completion."""
import copy,hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();prior=read(V/'goal-continuation-current.json');save(out/'previous-handoff.json',prior)
 publication=read(V/'current-biwn-latest-publication-current.json');review=read(V/'native-navigation-integration-reviewed-current.json');hybrid=read(V/'navigation-hybrid-component-reviewed-current.json');mcp=read(V/'native-navigation-current-MCP-read-current.json');index=read(V/'current-model-work-index-v4-current.json');cold=read(V/'cold-runtime-model-reviewed-current.json')
 assert publication['facts']['experimental_build']['resident_bytes']==mcp['response']['experimental_build']['resident_bytes']==29876
 assert mcp['response']['next_component_development']['final_address_verified']and not mcp['response']['next_component_development']['disc_integrated']
 assert review['candidate_frames']==24626 and review['control_frames']==24610 and hybrid['final_group_cases']==6144 and index['saved_prompt_or_transcript_records']==66
 worker_specs=[('native-actor-navigation-current.json','check_native_actor_navigation'),('native-actor-navigation-final-current.json','check_native_actor_navigation'),('actor-navigation-live-observer-current.json','qualify_native_actor_navigation_observer'),('native-actor-navigation-candidate-current.json','run_biwn_native_actor_navigation'),('native-actor-navigation-control-current.json','run_biwn_native_actor_navigation'),('native-navigation-dynamic-candidate-current.json','run_biwn_native_actor_navigation'),('native-navigation-dynamic-control-current.json','run_biwn_native_actor_navigation'),('native-navigation-hybrid-current.json','check_native_actor_navigation'),('native-navigation-hybrid-final-current.json','check_native_actor_navigation'),('navigation-native-Author-current.json','run_navigation_native_author'),('navigation-native-Author-repair-current.json','run_navigation_native_author'),('navigation-native-Author-concise-current.json','run_navigation_native_author')]
 workers=[]
 for name,needle in worker_specs:
  obj=read(V/name);assert obj['status'].startswith('terminal_'),name
  pids=[obj.get('pid'),obj.get('child_pid')];observations=[]
  for pid in [p for p in pids if p]:
   p=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True);same_worker=p.returncode==0 and(needle in p.stdout or str(Path(obj['directory'])/'probe.py')in p.stdout);assert not same_worker,(name,p.stdout);observations.append(dict(pid=pid,live_matching_worker=False,handle_missing=p.returncode!=0))
  workers.append(dict(pointer=name,status=obj['status'],process_observations=observations))
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt')
 notes.write_text(f'''BIWN / LOCAL AI LAB — VERIFIED CURRENT WORK
{now.isoformat()}

The latest reviewed experimental disc contains 29,876 native bytes. It completed
an outdoor–interior–outdoor route in 24,626 frames; its fresh same-layout control
completed 24,610. Every live monitor passes. The default visible preview remains
unchanged. Click its game window and hold C + Up to run; release C to walk.

FOUR NATIVE NAVIGATION ROOTS
F368 waypoint and13F12/13F7C/13FEA navigation now compile from high-level C with
original-facing68000 shims. Prototype and final-address comparisons each pass
6,144 cases (1,536/root), covering all209 original instruction sites. Returned
CPU/SR/banks, public2MBRAM and ordered public data reads/writes match original
execution. No helper effects are prescribed. Valid stored jump-table targets
only; changed targets/faults/IRQ/concurrency/timing remain outside these proofs.
This adds native integrations of existing portable algorithms, not four newly
discovered algorithms. Source for this published image is coordinator-authored.

The new read-only boundary/context/task monitor passes440 original/native
executions over220 stratified cases and detects4 decoded-observation negatives.
Fresh gameplay reaches native returns9/4/4/3 at the four roots, with20 context
entries and20 context returns and zero errors. Max observed private depths are
180/152/176/176; minimum task headrooms758/780/758/762 bytes. Algorithm equivalence
is separate from matching physical registers to the same C context.

Reservation30,080/free204 bytes, heap166340, initial capacity367,808. Staging moves
toF6C00 and clears30,208 bytes throughFE200; Atari trailer atFE520 is preserved.
96 startup,192 heap initialization,3,392 native blitter/copy plus3,392 ordered
heap/copy cases and36 constructor/capacity requests pass at the declared floor.
The original and parent disc hashes are unchanged; all28,354 changed CDI bytes
are inside declared loader/staging/four-entry intervals. Use normalized metadata:
{V/'native-actor-navigation-build-normalized-current.json'}

LIVE COVERAGE AND LIMITS
Shared source-owned movement/collision C chain remains byte-identical:6,381
movement returns and3,891 outdoor collision returns; zero indoor collision calls.
Its max private depth564/min live task headroom370; tighter fixture minimum354.
Creation dispatch15returns(13actor/2sprite); initializer13returns/18helpers;
sprite creator2returns/6helpers. Selector outcomes are a DIFFERENT count:
14actor successes and2sprite failures, exactly1skipped and1non-skipped. Sprite
success and actor failure remain component-only. No extra selector coverage is
inferred from creation routing. Context/task checks pass.

The new candidate/control differ in8,645 CPU,24,602 RAM,24,218 GPU,0 DSP,20,667 video,
20,302 navigation,155 locomotion and279 held-button frames over24,610 aligned
frames. PCM files78,803,200 versus78,752,000 bytes are unequal. Timing/adaptive
input differences remain; no whole-state/media equality or speedup claim.
Retained native emulator CPU/GPU/DSP/IRQ/platform/HLE execute these runs. Earlier
host C-processor test receipts apply only to their older exact disc hashes.
No full readable game, physical-console boot or same-console release readiness.

The first new-layout runs FAILED their fixed east-exit route:34,577/34,564 frames
ended in a different ground-floor room at its east wall. Navigation/context
checks passed, but required outside-geometry1028E was never reached, so the
aggregate gate failed. Those runs remain preserved. Parsed source room records
identify south exit key25; a bytes-only19FDA/1028E planner now supplies normal
controller buttons from CURRENT room data. Six parser checks pass. Both fresh
runs took that south exit and completed. No RAM restoration, position patch or
host guest-memory write is used. The reason for different room selection versus
the smaller prior layout remains unisolated; changing the route is not proof of
whole-game timing equivalence.
Gameplay review: {review['report']}
Failed fixed-exit review: {read(V/'native-navigation-fixed-exit-reviewed-current.json')['report']}

LOCAL MODEL OUTPUT TEST — THREE PREDICTIONS, NO WEIGHT TRAINING
Daily27B advertising-scholar base via real local LM Studio API, reasoningoff,
temperature0. First full13F12 proposal34.81s: strict compile passes after only
removing its Markdown fence, but original-valid fixture0 rejects registers and
public read trace. It used incoming registers instead of guest stack arguments.
Informed repair148.34s exhausts3,200tokens mid-function and fails compilation;
its flag masks are also wrong. Concise explicit-mask prompt37.54s returns complete
raw C, but strict compilation rejects its unusedD1 local; source omits D1writes
and has X/Z errors. None of these raw outputs was adopted. Exact inputs, outputs,
counterexample and compiler logs are retained. No independent model Reviewer.

HYBRID SOURCE: the coordinator made exactly3 explicit corrections to the concise
local draft: writeD1, preserve incomingX on the early return, clearZ on successful
return. Raw output remains unchanged. Both prototype and final-address groups
pass6,144 cases/all209 sites; the hybrid13F12 function has1,536 cases in each
matrix. Other3 roots remain coordinator C. Group1,588bytes would replace1,428:
projected resident30,036/free44 bytes in the same reservation. No integration,
new disc or live proof yet. Fresh rendered-observer qualification/full-payload
startup/disc-byte audit/gameplay/control review remain required before adoption.
Hybrid review: {hybrid['report']}

Saved prompt/transcript records:66 (not66 new predictions).
{index['report']}
Model Prompts and Responses.command refreshes this exact saved-file index.
Native LM Studio Chat display remains unverified; these are actual local API
runs with saved transcripts, not Chat-window streaming. Prior UI app selection
and passive inventory timed out; no unlock request or new UI success is claimed.
Daily base remains loaded32K context/1worker, idle. Game step32 adapter remains
unpromoted; Advertising step8 export remains loadable without an observed quality
gain. No new optimizer updates, default model promotion or cloud agents.

ADVERTISING AND FUTURE-MACHINE WORK REMAIN IN SCOPE
The daily base and optional trained Advertising Reviewer have actual copied-weight
load/final-generation evidence. Research/teaching/rubric/format reliability still
needs work. Prior invalid creative-mindset question is withdrawn; Schreiner is an
exposed reference, not a new held-out paper. Improve general methods/design-page
retrieval, then evaluate valid source-grounded research and teaching tasks.

Actual cold package: {cold['package']}
BundledPython/venv/index repair and7of18 MCP tool kinds/4boundary controls passed;
39 model resources/10 shards copied and verified, both copied definitions/weights
loaded and generated finals. Full SDK/CLI/toolchain/training/source-build/onboarding
and all18 tool behaviors remain unfinished. Copied CLI wrappers still reference
the old source tree; the SDK control client was the original workbench. Cold
canonical publication is26,220 historical bytes. No off-machine or future256GB
hardware test is claimed. Preserve the full four-part goal; it is incomplete.

NEXT WORK
1. Integrate the verified hybrid only with fresh observer/startup/disc/live gates;
   no new reservation or heap change is needed if its bound bytes/sizes hold.
2. Continue actual game source/callgraph recovery, including task-level interfaces
   and unobserved outcomes; do not substitute whole-processor reimplementation.
3. Improve/evaluate Advertising source-grounded research/education reliability.
4. Complete portable SDK/CLI/toolchain/training/first-use setup and model workflows.
All finite workers in this continuation are terminal; do not restart completed
jobs merely because a session handle is gone. Preserve the older interactive
preview. No permission or unlock request is pending.
''');shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 dependencies=dict(read(V/'actor-chain-cold-move-turn-integrity-current.json')['dependencies_sha256']);aliases=[]
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  mutable=(p.parent==V and p.name.endswith(('-current.json','-active.json')))or p in[notes,ROOT/'config/current-model-work-sources.json']or not p.is_relative_to(ROOT)
  if mutable:
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name[-160:]);shutil.copy2(p,target);aliases.append(dict(original=str(p),snapshot=str(target),sha256=actual));p=target
  assert str(p)not in dependencies or dependencies[str(p)]==actual,str(p);dependencies[str(p)]=actual
 for obj in [publication,review,hybrid,cold]:
  for p,h in obj['dependencies_sha256'].items():bind(p,h)
 for name in ['current-biwn-latest-publication-current.json','native-navigation-integration-reviewed-current.json','native-navigation-component-reviewed-current.json','native-navigation-fixed-exit-reviewed-current.json','native-actor-navigation-build-normalized-current.json','navigation-hybrid-component-reviewed-current.json','native-navigation-current-MCP-read-current.json','current-model-work-index-v4-current.json','current-room-exit-parser-current.json']:
  bind(V/name)
 for obj in[mcp,read(V/'current-room-exit-parser-current.json')]:
  for p,h in obj['source_sha256'].items():bind(p,h)
 for p in [Path(__file__),out/'previous-handoff.json',out/'previous-BIWN Latest Work.txt',out/'current-BIWN Latest Work.txt',notes,ROOT/'config/current-model-work-sources.json',Path(index['report']),Path(index['source_list_snapshot']),Path(index['directory'])/'manifest.json',ROOT/'runs/navigation-turn-LM-Studio-model-state.json']:bind(p)
 def verify(row):
  p,h=row
  try:return None if sha(p)==h else dict(path=p,error='SHA mismatch')
  except Exception as error:return dict(path=p,error=repr(error))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(verify,dependencies.items())if x]
 integrity=dict(status='terminal_native_navigation_inherited_integrity_pass'if not issues else'terminal_native_navigation_integrity_failed',directory=str(out),unique_bound_files=len(dependencies),issues=issues,dependencies_sha256=dependencies,historical_mutable_pointer_resolutions=aliases,scope='Original inherited1669bindings plus current expandednavigation/hybrid/model/controller/publication/MCP evidence. Mutabletop-level pointers/notes/config frozen; nested immutable snapshots not rewrapped.');save(out/'integrity.json',integrity);save(V/'native-navigation-turn-integrity-current.json',integrity);assert not issues,issues[:5]
 requirements=copy.deepcopy(prior['full_goal_requirements']);requirements[0].update(evidence=index['report'],remaining='Daily27B32K/1worker loaded;3new API code drafts all rejected unchanged. Hybrid needs3coordinatorcorrections and passescomponent gates. NativeChat/easyfirstuse/fullCLI/taskformat/reliabilityunfinished; no newweights.');requirements[1].update(evidence=review['report'],remaining='Current29876disc four native navigation roots+sharedchain passesfreshroundtrip,finiteCPU/RAM/trace/layout gates. Hybrid13F12prototype/finalpass notintegrated. Fullreadablegame/sameconsole rebuild,indoorcollision/media/timing/physicalconsole remainunfinished.');requirements[2]['remaining']='Dailybase and step8trainedReviewer copied-weightload/finalgenerationready; source-groundedresearch/teaching/format/causalreliability/generalmethodpageaccess stillunfinished. No newoptimizerupdates or observedqualitygain.'
 state=dict(status='active_four_native_navigation_roots_gameplay_pass_hybrid_component_pass_full_goal_remains',recorded_at=now.isoformat(),previous_turn_classification='Progress:sharedCchain development/startup and actualcoldcopiedmodels/runtime verified; fullgoalstillactive.',this_turn_classification='Progress:28448sharedCchain fresh routesreviewed; fouroriginal-facingnative navigationroots6144prototype+6144final/all209sites; expanded29876disc/loader/heap/capacity/newobserver and dynamiccurrent-roomroundtrip24626/24610pass. Fixedexitnegative retained; exactselector/routingcounts corrected.3actual localpredictions rejectedunchanged; explicit3correctionhybridpassesprototype/final6144each,notintegrated.66savedrecords,actual18toolMCPstatusverified,allnew/inheritedboundfilesverified.',prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,full_goal_requirements=requirements,latest_published_live_build_resident_bytes=29876,latest_built_disc_resident_bytes=29876,latest_built_disc_game_frames=24626,latest_native_navigation_build=str(V/'native-actor-navigation-build-normalized-current.json'),latest_native_navigation_live_review=str(V/'native-navigation-integration-reviewed-current.json'),latest_hybrid_component_review=str(V/'navigation-hybrid-component-reviewed-current.json'),latest_integrity=str(V/'native-navigation-turn-integrity-current.json'),latest_local_status_delivery=str(V/'native-navigation-current-MCP-read-current.json'),latest_model_work_index=str(V/'current-model-work-index-v4-current.json'),latest_Advertising_review=prior['latest_Advertising_review'],latest_migration_review=prior['latest_migration_review'],latest_cold_package=cold['package'],latest_native_UI_attempt=prior.get('latest_native_UI_attempt'),native_Chat_verified=False,finite_jobs=workers,finite_jobs_pending=[],interactive_preview=prior['interactive_preview'],local_model_work_this_continuation=dict(actual_predictions=3,seconds=[34.81,148.34,37.54],raw_source_adopted=False,hybrid_source_component_verified=True,coordinator_semantic_corrections=3,hybrid_disc_integrated=False,new_training=False,saved_records=66),current_entrypoints=prior['current_entrypoints'],next_actions=['Integrate verified1588byte hybrid at165CE0 only after fresh compiled observer qualification/fullpayloadstartup/disc-byte audit/livecontrol; projected30036resident/free44 in unchanged30080reserve.','Continue readable original game task/callgraph recovery and unobserved outcomes,not processor recreation.','Improve Advertising general method/design-page retrieval; usevalidAI-aversion/source-grounded research/teaching tasks,not invalidcreativemindset question or exposedsourceasheldout.','Finish portable SDK/CLI/toolchain/training/sourcebuild/onboarding and all18toolbehaviors; copiedCLIoldpaths remain.','Keep nativeChat/easyinference task reliability open; no unlockrequest or unsupportedUI success claim.'],no_completion_claim=True,final_integrity_unique_files=len(dependencies))
 save(out/'handoff.json',state);save(V/'goal-continuation-current.json',state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),event='native_navigation_gameplay_and_local_hybrid_component_verified',coordinator='Codex',local_role='GameCodeAuthor viaLMStudioadvertising-scholar',actual_predictions=3,local_code_adopted_unchanged=False,coordinator_hybrid_corrections=3,current_disc_resident_bytes=29876,hybrid_component_not_integrated=True,full_goal_complete=False,notes=str(notes),handoff=str(out/'handoff.json'),integrity_files=len(dependencies)))+'\n')
 print(json.dumps(dict(status=state['status'],goal_complete=False,resident_bytes=29876,hybrid_integrated=False,integrity_files=len(dependencies),finite_jobs_pending=0)))
if __name__=='__main__':main()
