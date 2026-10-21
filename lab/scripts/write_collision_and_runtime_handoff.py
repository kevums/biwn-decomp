"""Preserve all four goal requirements after collision and runtime progress."""
import hashlib
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'verification'


def read(p):
    return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def save(p,x):
    Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    now=datetime.now(timezone.utc)
    out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer=V/'goal-continuation-current.json'
    state=read(pointer)
    shutil.copy2(pointer,out/'previous-handoff.json')
    publication=read(V/'current-biwn-latest-publication-current.json')
    review=read(V/'actor-collision-integration-reviewed-current.json')
    boundary=read(V/'relocated-runtime-boundaries-current.json')
    models=read(V/'relocated-model-copy-current.json')
    outputs=read(V/'relocated-advertising-output-reviewed-current.json')
    corpus=read(V/'advertising-reference-expansion-current.json')
    index=read(V/'current-model-work-index-v4-current.json')
    current=read(V/'collision-current-MCP-read-current.json')
    assert publication['facts']['experimental_build']['resident_bytes']==review['resident_bytes']==current['response']['experimental_build']['resident_bytes']==28380
    assert review['live_monitor_pass'] and index['saved_prompt_or_transcript_records']==61
    assert models['weight_shards']==10 and models['logical_bytes']==46796200858
    jobs=[]
    for label in ['candidate','control']:
        job=read(V/('native-actor-collision-'+label+'-current.json'))
        assert job['status']=='terminal_native_actor_collision_route_pending_review' and job['exit_code']==0 and job['live_monitor_pass']
        assert subprocess.run(['ps','-p',str(job['child_pid']),'-o','command='],capture_output=True).returncode!=0
        jobs.append(dict(kind=label,pid=job['pid'],child_pid=job['child_pid'],status=job['status'],frames=job['frames'],live_monitor_pass=True))
    notes=ROOT/'BIWN Latest Work.txt'
    shutil.copy2(notes,out/'previous-BIWN Latest Work.txt')
    text=f'''BIWN / LOCAL AI LAB — CURRENT WORK
{now.isoformat()}

LATEST REVIEWED AND PUBLISHED NATIVE EXPERIMENT:28,380resident bytes.
Adds original-facing outdoor13B5A/indoor13BB0collision C to native movement,
actor/spritecreation and earlier routines.28,544reservation/free164;heap165D40,
stagingF7000 unchanged. Atari trailer preserved; original CDI unchanged.
Default interactive preview remains the older verified sourceCPU/GPU checkpoint.
HoldC+Up to run;Ppauses/resumes. No preview restart/window/default switch.

NEW COLLISION AND COMPOSITION
Coordinator adapts existing high-level portable collision C, with original-facing
packed arguments/fullCPU/SR/helper capture bridges.2,160native bytes at16542C;
private reserve704 protects the parent movement C frame. All four actual geometry
helpers execute:1039C,102C4,1028E,10652. No prescribed helper in direct collision.
Prototype and final-address matrices each5,120cases/all109original sites,2,560cases
per root, maxprivate840. Ordered public accesses/public2MBRAM/returnedCPU/SR/banks
and physical helper-entry CPU/SP/SR/arguments match. Five deliberate missing-body,
helperX,fullD0-clear and original-delegation defects reject.

Movement+bothcollision native composition2,560cases passes,522outdoor/572indoor
entries; only E220GPU effects prescribed. Final native composition/context oracle
5,120original/C executions preserves the movement context and task-header plus
lower128byte canaries. Maxnestedprivate894; minimum24bytes headroom at the tighter
synthetic root matching an earlier observed live minimum. Four decodedCPU/mirror
context negatives reject. A512reserve variant passes32standalone collision cases
but fails actual nested movement execution;704positive on that fixture passes.
These finite cases do not establish arbitrary recursion/interrupt/concurrent-input
stack bounds. Current ABI glue still needs source-owned callgraph/stack optimization
for broader native-console readiness; do not treat the small margin as general safety.

NEW DISC / ACTUAL GAMEPLAY
New CDI changes1,864actual bytes within declared append/entry regions; first26,220
resident bytes identical to the checked parent. Full28,380payload startup96cases pass.
Fresh candidate29,797frames/control24,996both return outdoors/hold120frames.
Only14declared bytes at the two collision entries restored in control; native
movement/priorfunctions/reservation/staging/heap/unusednewcode common.
Candidate3,868outdoor collision entries/returns/allnative,0originalcollisionsteps,
1,771,144nativecollisioninstructions. Control3,949outdoorreturns/82,886original
collisionsteps/0nativecollisionentries. Indoor collision0in both: live indoor and
per-outcome/rollback coverage unfinished, not inferred from helper counts.

Candidate movement13,872returns/31,612actualhelpers/contextchecks; zero reported
movementABI/context/task-boundary errors; maxprivate894/minliveheadroom40.
Control movement13,898returns/31,745helpers;depth672/headroom246. Both have13native
dispatchreturns(12actor/1sprite),12initializers/16helpers,1spritecreator/3helpers.
Actorselector14successes/0failures;spriteselector0successes/1skippedfailure.
Retained native emulatorCPU/GPU/DSP/IRQ/platform/HLE execute both routes. Five
older strictCprocessorjobs remain terminal only for their own older disc hashes.
No new strictprocessor/physicalconsole/complete-readable-game proof applies.

Aligned24,996prefix differs:CPU22,262/RAM24,985/GPU23,184/DSP9,123/video17,150/
navigation18,476/locomotion318/buttons321. PCM differs95,350,400versus79,987,200bytes.
Instruction costs/schedules and adaptive controller paths differ. Older inherited
discrepancies remain unresolved; no whole-game performance or timing/media equality.
Review:{review['report']}

MIGRATION PROGRESS — ACTUAL CURRENT FRONTEND, SAME HOST/DIFFERENT ROOT
Fresh isolated v9frontend/Python/26moduleclosure install succeeds. A3,549file,
3,723,726,092logical-byte workbench/evidence/source subset was APFS-cloned, plus
three task-dataset files. The existing18tools register. Seven tool kinds pass:
functiontask,advertisingsearch,currentstatus,rubric,bootdecode,native68000fixture,
inventoryimage. Actual copied-native-worker child and parent audit receipts exist.
Historical source/evidence bytes and hash keys remain on disk unchanged; declared
absolute path values/dictionary keys map in memory. Originworkbench/runtime reads,
symlinkbacktosource and corruptedcopiedevidence reject. Corruption restored exactly.
Path adapterv1missed directPathliteral construction underPython3.12; v2fixesinit.
Earlier failure receipts remain. Latest successful7toolattempt isMCP-attempt-v3.
No original-tree fallback in those guarded tests. This hook is a test guard, not a
security sandbox; all18toolbehaviors/fullworkbench/toolchain/launchers/training/
off-machine or futurehardware restoration not established. Bundle preserves the
26,220canonical publication at capture; it is not a live mirror of current28,380.
Runtime:{boundary['runtime']}

39model files/10weightshards/46,796,200,858bytes are now materialized in isolated
LMStudiohome and SHA256-verified against frozen inventory: dailybase plus optional
trainedstep8Reviewer. Live model/default/config not switched. These copied weights
have not been loaded for inference. Original loaded daily27Bbase remains active.
Next: cold-move/recreatevenv and launcher paths, test actual source rebuild and
complete selected workflow/toolchain/adapter/corpus dependencies; test copied-weight
inference and eventual off-machine restore. Current scripts/venv/wrappers still
have installation/path assumptions; seven MCPcalls are not fullmigration proof.
Model copy receipt:{Path(models['directory'])/'protocol.json'}

LOCAL OUTPUT / ADVERTISING
Two actual Researcher requests via relocatedMCP/currentloadedbase:16.64and8.19s,
two predictionrounds/one realsearch each. Firstmissingpaper correctlydeclines.
Second sees newly indexed paper, stilldeclinescreative-mindsetpremise. Coordinator
used a construct from another study: question withdrawn, neither run is a valid
quality benchmark or successful substantive research answer. No modelgain/code
adoption/newtraining/nativeChatUIclaim. Actualsource-method retrieval omitted the
specificdesignpages; improve general methods-page access with valid source-checked
questions instead of blind prompt retries. Exactprompts/responses nowI61savedrecords,
not61newpredictions. Ordinary corpus nowincludes already-evaluatedSchreiner2026
unchangedPDF in source/liveRuntime/restoredRuntime. Frozen evaluation unchanged;
fromnow it is exposed reference material, not a freshheldoutsource.
Output review:{outputs['report']}
Prior optionaltrainedReviewer remains loadable but no source-transfergain observed.
Game native-repair-v3step32 remains unpromoted after code failures. No optimizer
updates/newweights this continuation. Same-weight roles are not independent review.

FULL ORIGINAL FOUR-PART GOAL REMAINS ACTIVE
1.Easy reliable LMStudiofront/roles/inference/training:partial; nativeChatUI and
first-use reliability remain unverified. CurrentSstillv12; no newstatusprediction.
2.BIWNdecompile/readable same-console rebuild:partial; newcollisioncompletedabove,
remaining game source/interfaces,indoorlivebehavior,stack/performance/media/timing,
andphysicalconsole/source-owned native build unfinished.
3.Advertisingresearch/education model/roles/training:base/optionaltrainedmodel and
workflows exist; validsource-grounded research/teaching/review reliability unfinished.
4.Portableworkbench/models/workflows/future256GBconfiguration:models copied and
bounded currentMCP/runtime proof above; full coldrestore/rebuild/inference/offmachine
verification and futurehardwareconfiguration preparation unfinished.
No unlock request/no external messages/no new Codex chats/cloudsubagents.
All finite jobs from this continuation terminal. Default preview preserved.
'''
    notes.write_text(text)
    shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
    dependencies=dict(read(V/'actor-move-live-turn-integrity-current.json')['dependencies_sha256'])
    snapshots=out/'snapshots';snapshots.mkdir()
    aliases=[]

    def bind(p,expected=None):
        p=Path(p).resolve();digest=sha(p)
        assert expected is None or digest==expected,str(p)
        if p.name.endswith(('-current.json','-active.json')) or p==notes or p==ROOT/'config/current-model-work-sources.json':
            target=snapshots/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name)
            shutil.copy2(p,target);aliases.append(dict(original=str(p),snapshot=str(target),sha256=digest));p=target
        assert str(p)not in dependencies or dependencies[str(p)]==digest,str(p)
        dependencies[str(p)]=digest

    for obj in [publication,review,boundary,models,outputs]:
        for p,h in obj.get('dependencies_sha256',obj.get('source_sha256',{})).items():
            bind(p,h)
    for name in ['current-biwn-latest-publication-current.json','actor-collision-integration-reviewed-current.json','relocated-runtime-active.json','relocated-runtime-boundaries-current.json','relocated-model-copy-current.json','relocated-advertising-output-reviewed-current.json','advertising-reference-expansion-current.json','collision-current-MCP-read-current.json','current-model-work-index-v4-current.json']:
        bind(V/name)
    extra=[Path(__file__),out/'previous-handoff.json',out/'previous-BIWN Latest Work.txt',out/'current-BIWN Latest Work.txt',notes,ROOT/'config/current-model-work-sources.json',Path(index['report']),Path(index['directory'])/'manifest.json',Path(index['source_list_snapshot'])]
    for row in outputs['runs']:
        extra.extend([Path(row['directory'])/'protocol.json',Path(row['directory'])/'prompts-and-responses.txt',Path(row['directory'])/'answer.txt'])
    for name in ['origin.json','workbench-files.json','closure-extension-task-dataset.json','MCP-attempt-v3/MCP-protocol.json','MCP-attempt-v3/MCP-call-summaries.json']:
        extra.append(Path(boundary['runtime']).parent/name)
    for p in extra:
        bind(p)
    with ThreadPoolExecutor(max_workers=4)as pool:
        issues=list(pool.map(lambda item:None if sha(item[0])==item[1]else item[0],dependencies.items()))
    issues=[p for p in issues if p]
    integrity=dict(status='terminal_collision_runtime_and_inherited_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(dependencies),issues=issues,dependencies_sha256=dependencies,historical_mutable_pointer_resolutions=aliases,scope='Source/binary/reports/metadata/snapshots integrity, not whole-game/model-quality/physical-console/fullmigration verification. Copied weights use their separate full-shard copy audit.')
    save(out/'integrity.json',integrity);save(V/'collision-runtime-turn-integrity-current.json',integrity)
    assert not issues,issues
    preview=[]
    for pid in [233,235]:
        ps=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True)
        if ps.returncode==0:preview.append(dict(pid=pid,command=ps.stdout.strip()))
    state.update(status='active_native_collision_published_runtime_models_copied_full_goal_remains',recorded_at=now.isoformat(),goal_complete=False,prior_state_archive=str(out/'previous-handoff.json'),previous_turn_classification='Progress: original-facingcollision5120andmovementcomposition2560 passed; isolatedfrontendinstallcompleted. Those terminal receipts were revalidated before continuing.',this_turn_classification='Progress: final collision5120/all109sites/5defects,5120composition-context executions with taskcanaries and24byte finite headroom; smallerreserve negative demonstrates nestedfailure.28380disc/96startup/fresh29797and24996routes returnedoutdoors with3868candidateoutdoor collisionreturns,0indoor/0contextstackerrors. Published and actualconfiguredMCPverified. Existing18tool relocatedruntime7toolkinds/4boundarynegatives pass;39modelresources46.80GB/10shards copied andhashed. Two localResearcherrequests4predictionrounds/2MCPcalls retained;coordinatorwrongconstructquestionwithdrawn,noqualityclaim. Actualresearchcorpus adds evaluatedsource;I61records.',latest_built_disc_resident_bytes=28380,latest_published_live_build_resident_bytes=28380,latest_built_disc_game_frames=29797,latest_collision_review=str(V/'actor-collision-integration-reviewed-current.json'),latest_context_oracle=str(V/'actor-move-collision-contexts-current.json'),latest_migration_review=str(V/'relocated-runtime-boundaries-current.json'),latest_model_copy=str(V/'relocated-model-copy-current.json'),latest_local_output_review=str(V/'relocated-advertising-output-reviewed-current.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(dependencies),finite_jobs=[],finite_jobs_pending=0,completed_finite_jobs=jobs,local_model_work_this_continuation=dict(actual_prediction_rounds=4,actual_MCP_calls=2,Researcher_requests=2,seconds=[16.63941975007765,8.189392208936624],valid_quality_benchmark=False,coordinator_question_withdrawn=True,new_code_Author_predictions=0,new_training=False,new_weights=False,native_Chat_verified=False,restored_weights_loaded=False),interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='HoldC+Up;Ppauses/resumes',recipe='Older verified sourceCPU/GPUcheckpoint,notcurrent28380nativeexperimentaldisc'),last_native_game_frame=review['image'],no_completion_claim=True,next_actions=['Continue actual high-level game-source/interfaces, likely next original-facing actor navigation/state callbacks. Do not recreate whole processors instead of remaining game functions. Newcollision13B5A/13BB0completedfinite/nativeoutdoorliveproof,notwholegame.','Broaden actual indoor13BB0movement/liveoutcome/rollback/callback/pool/resource/taskbehavior. Indoor0livecalls;24finite/40liveheadroom not general bound. Optimize source-owned C callgraph/ABI bridges before nativeconsole readiness; resolve inherited media/state/timing differences. Default preview unchanged.','Cold-move/recreate Pythonvenv/launchers/bootstrap from copiedpackage,complete toolchain/source/workflow/training/corpus prerequisites and actualrebuild/copied-weightinference. Existing7of18toolkinds test is not fullrestore.26,220canonical snapshot retained while livepublication28,380.47GBmodelsnowcopied/10shardhashpass,notloadedfromcopy/offmachine/futurehardware. Keep historical rawhashbytes intact.','Advertising probequestion usedwrongconstructcreative-mindsetinSchreiner;withdrawn. Bothrawrequests retained,2x2rounds withactualrelocatedMCP,notmodelgain/substantiveanswerproof. Paper nowordinaryexposedRAGreference,notfreshheldout. Improve general method/design-page retrieval with valid source-checked questions and then evaluate research/teaching/review. Do not blindretry or train on exposedholdout while claimingnovelgeneralization.','NativeChatUI/latestadoption unverified;do not askunlock/repeatstaleAXactions. SDK/headlessallowed. CurrentSstillv12;newpublicationtypedcounts correct butno newReaderqualityclaim. Game step32 unpromoted;Advertisingoptionalstep8loadablebutnogain. Fullfourpartgoalactive.','All finite workers now terminal;do not restartthem. Preserve currentpreview and exactprompts/responses I61records. Review newgame image/report at savedpaths; no physicalconsole/fullreadablegame completionclaim.'])
    state['current_entrypoints']['prompts_I']='61saved exactprompt/transcript records;4new predictionrounds/2Researcherrequests this continuation,invalidcoordinatorquestionnotqualitybenchmark'
    state['full_goal_requirements'][0]['evidence']=outputs['report']
    state['full_goal_requirements'][0]['remaining']='CurrentSDK/localmodel/relocatedMCPconnection works;substantiveprobequestioninvalid.NativeChat/easyfirstuse/robustresearchandgameinference/roletrainingreliabilityunfinished.CurrentSstillv12.'
    state['full_goal_requirements'][1]['evidence']=review['report']
    state['full_goal_requirements'][1]['remaining']='28380nativeexperimentaldisc completes both fresh routes,3868nativeoutdoorcollisionreturns;indoor0live. Fullreadablegame/source-ownedsameconsolebuild,broadbehavior,stackmargin/performance/media/timing/physicalconsoleunfinished.'
    state['full_goal_requirements'][2]['remaining']='DailybaseandoptionaltrainedReviewerloadable;47GBbothpackagesnowcopiedandhashverified.SeparateResearcherRAGprobequestioninvalid;method-pageaccess/validresearchteachingreviewreliabilityunfinished.No newtraining/gain. EvaluatedSchreinerpaperaddedtoreferences,sofutureheldoutstatusrevoked.'
    state['full_goal_requirements'][3]['evidence']=str(Path(boundary['directory'])/'protocol.json')
    state['full_goal_requirements'][3]['remaining']='Current18toolfrontend26moduleclosurecoldinstalledinsandbox,differentrootworkbenchsubset3549clones+3datasetfiles,7toolkinds/4escapeintegritycontrols pass.Model39files46.80GB10shardsnowcloned/hashed. Copiedweightsinference,coldmovedvenv/launchers/fulltoolchain/training/workflow/sourcebuild/offmachine/future256GBconfigurationunfinished.'
    save(out/'protocol.json',state);save(pointer,state)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:
        stream.write(json.dumps(dict(recorded_at=now.isoformat(),event='native_collision_and_relocated_runtime_model_package',coordinator='CollisionC/ABI/finitefixtures/negativecontrols/taskcanaries/disc/freshroutes/review/publication,portable18toolruntime/pathguard and modelcopy',local_models='Two actualResearcherrequests throughrelocatedMCP;coordinatorwrongconstructquestionwithdrawn,notqualitybenchmark',actual_prediction_rounds=4,actual_MCP_calls=2,new_training=False,published_resident_bytes=28380,frames=[29797,24996],outdoor_collision_calls=3868,indoor_collision_calls=0,registered_tools=18,tested_tool_kinds=7,model_files_copied=39,model_bytes_verified=46796200858,full_migration=False,full_game=False,bound_files_verified=len(dependencies),goal_complete=False))+'\n')
    print(json.dumps(dict(status=state['status'],bound_files=len(dependencies),published=28380,pending_jobs=0,goal_complete=False,notes=str(notes))))


if __name__=='__main__':
    main()
