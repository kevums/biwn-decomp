"""Preserve the full goal after source-owned ABI and cold-copy inference progress."""
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

V=ROOT/'verification'


def read(p):return json.loads(Path(p).read_text())


def main():
    now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'goal-continuation-current.json';state=read(pointer);shutil.copy2(pointer,out/'previous-handoff.json')
    chain=read(V/'actor-chain-development-reviewed-current.json');cold=read(V/'cold-runtime-model-reviewed-current.json');publication=read(V/'current-biwn-latest-publication-current.json');current=read(V/'chain-pending-current-MCP-read-current.json');index=read(V/'current-model-work-index-v4-current.json')
    assert chain['latest_built_resident_bytes']==28448 and not chain['gameplay_tested']
    assert publication['facts']['experimental_build']['resident_bytes']==current['response']['experimental_build']['resident_bytes']==28380
    assert current['response']['next_component_development']['latest_built_resident_bytes']==28448
    assert cold['copied_model_final_responses']==2 and cold['default_model_restored']and index['saved_prompt_or_transcript_records']==63
    # All finite workers must be terminal, and no state file alone proves that.
    worker_names=['native-actor-chain-current.json','native-actor-chain-final-current.json','actor-chain-contexts-current.json','cold-runtime-move-active.json','cold-copied-model-inference-active.json']
    jobs=[]
    for name in worker_names:
        obj=read(V/name);assert obj['status'].startswith('terminal_'),name
        pid=obj.get('pid');live=subprocess.run(['ps','-p',str(pid or 0),'-o','command='],capture_output=True,text=True)
        assert live.returncode!=0 or not any(s in live.stdout for s in ['check_native_actor_chain','check_actor_chain_contexts','prepare_cold_runtime_move','run_copied_model_inference']),name
        jobs.append(dict(pointer=name,pid=pid,status=obj['status'],worker_not_live=True))
    notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt')
    notes.write_text(f'''BIWN / LOCAL AI LAB — CURRENT WORK
{now.isoformat()}

LATEST GAMEPLAY-TESTED PUBLISHED DISC:28,380native bytes.
It remains the reviewed collision/movement/creation build:29,797candidateframes/
24,996controlframes,bothreturnedoutdoors.3,868candidateoutdoorcollisionreturns;
0indoorlivecalls. RetainednativeemulatorCPU/GPU/DSP/IRQ/platform/HLE;media/state/
timingdifferences remain. Defaultvisiblepreview older/unchanged;C+Up runs,Ppauses.

NEW DEVELOPMENT DISC:28,448BYTES — COMPONENT/STARTUP PASS, GAMEPLAY PENDING
Three already-reconstructed roots13C9A/13B5A/13BB0now share an80byte context.
Movement calls collision through C ABI instead of leaving C for the public
68000collision wrapper and entering a second private C frame. Original public
roots and actualremaining direction/GPU/geometry boundaries retain original ABI.
This refactors recovered functions; it does not add new recovered game functions.
InternalCcollisionentry uses shadowCPUstate,not physicalCABIregister equality.

Sharedgroup5,188bytes at16489C,rootprivategap320. Prototype andfinalmatrices each
7,680cases(5,120directcollision+2,560movement)coverall301originalinstructionsites.
FullreturnedCPU/SR/banks/public2MBRAM/orderedpublicaccess and remaining physical
helperCPU/SP/SR/arguments match; internalcollision shadowentry matches original
physicalentry. Directcollisionhasnoprescribedhelpers; E220GPUeffects prescribed
in movementfixtures. Physical direction/division/geometry execute actualcode.

15,360original/C native executions qualify context/taskheader/lower166byte guards.
8,969physicalcontextchecks/1,094virtualcollisionchecks. Maxnativeprivate564,
minimumfixtureheadroom354 atsame918rootallowance,versusprior894/24. Five decoded
observation negatives reject withoutchangingnativeCPU/RAM. Actualcompiledwrong
virtualJSRwidth andwronggeometryanchor defects reject under boundedguestexecution;
correctfixture also matchesoriginalnativeCPU. These are finitebounds,notgeneral
interrupt/concurrency/recursion/invalidinput guarantees.
Matched2,560movementfixtures:10,791,949oldwrapperinstructions versus10,740,988shared
chain,about0.47%fewer;no liveFPS/wholegame speedupclaim. Compilerlayout/flags change,
so freshactualgameplay is required before promotion.

NewCDI28,448used/28,544reservation/free96;first23,260residentbytes preserved;
heap165D40/stagingF7000/clearFE000/trailer unchanged.4,511actualCDIbyteschanged
onlyindeclaredtail/entryregions;parentandoriginalCDIunchanged.96fullpayloadstartup
casespass. No newheaplayoutchange,so priorunchangedprefix/heap/reservationproofs
remainseparate. Fullgame/sameconsolerelease/physicalconsoleboot stillunfinished.
USE NORMALIZED BUILD METADATA:
{chain['normalized_build']}
The as-run build receipt inherited obsolete standalonecollisionrange/helper-return
fields; separate normalizedreceipt removes them,setsprivate320/netgrowth68/source
correctly,without rewriting originalimage or startupreceipt. Oldmovementmonitor
assumes72bytes/rootSP-488 andphysicalcollisionentry:donotreuseunchanged. NewM
context80bytes/rootSP-360;internalcall/return symbols andactor_chain_helpers describe
the realboundaries. Next:implement/qualifyread-only sharedcontext/virtualCmonitor,
thenfreshcandidate/control route restoringallthreepublicoriginalentries(22declared
bytes)forcontrol. Do not claim gameplay for this development image yet.
Development review:{chain['report']}

COLD RESTORE / ACTUAL COPIED MODEL LOAD AND INFERENCE
Actual package outsideworkbench:
{cold['package']}
8,080files/14symlinks/50,756,643,153logicalbytes APFScloned. BundledPythonrepairs
venvhome/relativePythonlink/MCPentry;mutableSQLitegame/advertising sourcecolumns
rebasedwithbackups. RestoreLocalAILab.command is inpackage. Historicalorigin/source/
evidencebytes unchanged;canonicalpublication inpackage is26,220snapshot,notlive
28,380or28,448. Sevenkindsofexisting18MCPtools passaftermove,includingnativeCPU
child andinventoryimage. Actualnewparent/workeraudits distinguishedfromcopied
oldaudits. Copiedevidencecorruption/rawoldR/runtime/symlinkorigin controlsreject,
thenexactbytesrestore; nooriginfallbackintheseguardedtests. Samehost/testguard,
not general securitysandbox or full18toolbehavior/offmachine proof.

39selectedmodelresources/10weightshards fullySHAverifiedaftercoldcopy. Bothactual
copieddailybaseandtrainedstep8Reviewer loadthroughLMStudio viatemporarylocal
resourcealiases resolvingcopiedpaths. Firstpreparationwronginventorylabel ran0
predictions; retained. Rawweightfolder profiles load but returnonly399reasoningtokens
and0finalwords at17.32/18.67s. Failedfinaloutputtest,not brokenweightcopy.
Copiedmodeldefinitions providecustomthinkingdefaults: same2prompts/copyweights,
reasoningoff/0reasoningtokens,finalanswers2.61/2.85s,loads5.43/6.07s,8Kcontext/1worker.
Currentdailybase27Brestored32K/1worker;temporarylinks/definitionsremoved.

Quality limits:Researcher correctlyidentifiesassigned/measuredvariablesbutcausal
wordingcould imply a nonzeroeffect withoutresults. Reviewer correctlyrejects
measured-aversioncausality/inventedresults,butreturns3sentenceswhen2requested.
This provesload/finalgeneration withcopiedconfigs,not broadqualitygain/independent
multiagentreview or a heldoutstudybenchmark. Two raw+two configured actualpredictions;
no newweights/optimizersteps/gameAuthoradoption. Exactprompts/rawresponses nowI63
savedrecords,not63newpredictions. ActualSDKcontrolclient wasoriginalworkbench.
CopiedPython hasMCPdeps,notfullSDK/CLI/trainingenvironment. CopiedCLIwrappers still
routeoldsourcepaths;fullportableworkflows/toolchain/sourcebuild/adapter/training/
onboarding/nativeChatUI/offmachine/future256GBverification remainunfinished.
Cold restore/model review:{cold['report']}

FULL ORIGINAL FOUR-PART GOAL REMAINS ACTIVE
1.EasyLMStudiofront/models/visiblelocalroles/training:partial;copiedmodelconfig
load/generationworks,butnativeChatUI andfirst-use/fullCLI/taskreliability unverified.
2.BIWNdecompile/port/mod/restoration/sameconsole:partial;newsharedCchainpendinglive
monitor/gameplay;remaininggameinterfaces/code/indoorlivecoverage/media/timing/
performance/physicalconsole andfullreadablebuildunfinished. Continue actual game
source after qualifying thiscallgraph;do not substitute wholeprocessor recreation.
3.Advertisingresearch/education:dailybase/optionaltrainedReviewerreadyandnowcopy-
loadtested;source-basedresearch/teaching/review andformatreliability remainopen.
Priorwrongcreative-mindsetquestionwithdrawn;Schreinerpaperisnowordinary exposedRAG,
not freshheldoutsource. Improve generalmethod/design-pageaccesswithvalidtasks.
4.Portablefutureconfiguration:actualcoldMCP7/18andcopiedmodelsproofabove;notfull
workbench/SDK/CLI/toolchain/training/sourcebuild/offmachine/futurehardwareproof.
Game native-repair-v3step32 remainsunpromoted;Advertisingstep8stillnogainobserved.
No newCodexchats/cloudsubagents/automations/externalmessages/unlockrequests.
Allfiniteworkerscurrentlyterminal;donotrestartcompletedjobs.Defaultpreviewpreserved.
''')
    shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
    dependencies=dict(read(V/'collision-runtime-turn-integrity-current.json')['dependencies_sha256']);snapshots=out/'snapshots';snapshots.mkdir();aliases=[]
    def bind(p,h=None):
        p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
        if not p.is_relative_to(ROOT)or p.name.endswith(('-current.json','-active.json'))or p in[notes,ROOT/'config/current-model-work-sources.json']:
            target=snapshots/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases.append(dict(original=str(p),snapshot=str(target),sha256=actual));p=target
        assert str(p)not in dependencies or dependencies[str(p)]==actual,str(p);dependencies[str(p)]=actual
    for obj in[publication,chain,cold]:
        for p,h in obj['dependencies_sha256'].items():bind(p,h)
    for name in['actor-chain-development-reviewed-current.json','native-actor-chain-build-normalized-current.json','actor-chain-contexts-current.json','cold-runtime-model-reviewed-current.json','cold-runtime-boundaries-current.json','chain-pending-current-MCP-read-current.json','current-model-work-index-v4-current.json','cold-copied-model-raw-profile-current.json','cold-copied-model-configured-current.json']:
        bind(V/name)
    for p in[Path(__file__),out/'previous-handoff.json',out/'previous-BIWN Latest Work.txt',out/'current-BIWN Latest Work.txt',notes,ROOT/'config/current-model-work-sources.json',Path(index['report']),Path(index['source_list_snapshot']),Path(index['directory'])/'manifest.json']:
        bind(p)
    with ThreadPoolExecutor(max_workers=4)as pool:
        issues=[row for row in pool.map(lambda item:None if sha(item[0])==item[1]else item[0],dependencies.items())if row]
    integrity=dict(status='terminal_actor_chain_cold_move_inherited_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(dependencies),issues=issues,dependencies_sha256=dependencies,historical_mutable_pointer_resolutions=aliases,scope='Bound source/binary/report/snapshot integrity,notfullgame/modelquality/fullrestore/hardwareproof. Weightshards have separateactualcoldcopyfullhashverification.')
    save(out/'integrity.json',integrity);save(V/'actor-chain-cold-move-turn-integrity-current.json',integrity);assert not issues,issues
    preview=[]
    for pid in[233,235]:
        ps=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True)
        if ps.returncode==0:preview.append(dict(pid=pid,command=ps.stdout.strip()))
    state.update(status='active_shared_C_chain_startup_pass_cold_models_loaded_full_goal_remains',recorded_at=now.isoformat(),goal_complete=False,prior_state_archive=str(out/'previous-handoff.json'),previous_turn_classification='Progress:28380nativecollisiondisc/actualroutespublished;18toolisolatedfrontend7tooltests/39modelresourcecopyhashpass;invalidcoordinatoradvertisingquestionretained.',this_turn_classification='Progress:source-ownedmovement/collisionCABI5188bytes,prototype/final7680caseseach/all301sites,15360nativecontext/canaryexecutions,max564/min354versus894/24;5observer+2compiledsource defectsreject.28448disc/96startup,notgameplaytested;normalizedmetadataavailable.Publishedpendingstatuswithoutpromotinggameplay. Actual8080filecoldmoveoutsideR/venv+indexrepair/7of18tools+4controls/10shardhashpass. Bothcopiedmodelsload;rawfolders2reasoning-onlyresponses, copieddefinitions2finals2.61/2.85s,format/causalwordinglimitsretained.Daily32Krestored,I63records,integrityverified.',latest_built_disc_resident_bytes=28448,latest_published_live_build_resident_bytes=28380,latest_built_disc_game_frames=0,latest_actor_chain_development_review=str(V/'actor-chain-development-reviewed-current.json'),latest_actor_chain_build=str(V/'native-actor-chain-build-normalized-current.json'),latest_context_oracle=str(V/'actor-chain-contexts-current.json'),latest_migration_review=str(V/'cold-runtime-model-reviewed-current.json'),latest_cold_package=cold['package'],latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(dependencies),finite_jobs=[],finite_jobs_pending=0,completed_finite_jobs=jobs,local_model_work_this_continuation=dict(actual_prediction_rounds=4,actual_MCP_calls=0,requests=4,raw_profile_blank_final_responses=2,configured_final_responses=2,configured_seconds=[2.61,2.85],valid_quality_gain_benchmark=False,new_code_Author_predictions=0,new_training=False,new_weights=False,native_Chat_verified=False,copied_weights_loaded=True,default_daily_restored=True),interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='HoldC+Up;Ppauses/resumes',recipe='OlderverifiedsourceCPU/GPUcheckpoint,not28380or28448nativedisc'),no_completion_claim=True,next_actions=['Implement/qualifyactualshared-C-chainread-onlyliveobserver. New80bytecontext/rootSP-360/reserve320; internalcollisionCcall/return usevirtualshadowCPU,notphysicaloriginalentry. Use actor_chain_helpers andCvirtualmarkersfrom normalizedbuild. Old72byte/rootSP-488Mmonitor andstandalonecollisionranges areinvalidhere. Thenfreshcandidate/controlroutes;restoreallthreeoriginalpublicentries22declaredbytesincontrol. No current28448gameplayclaim.','Continueactualremaininggame-source/interfaces,likelyactornavigation/statecallbacks,aftersharedABIintegrated. Newsharedchainrefactorsalreadyrecovered301sites,notnewfunctions; keepfullreadablegame/sameconsolegoal. Source-ownedcallgraphwillneedfurtherremaininghelper/kernelinterfaces,nativeperformance/broadtask/interrupt/concurrency/resourcevalidation. Indoorcollision0liveandmedia/state/timinglimitsremain.','ColdpackageactualoutsideR,8080files14symlinks50.76GB. BundledPythonvenv/indexrepair+7of18tools/4controls pass,10shardhashes. Copiedweightsload+finalgenerationverifiedwithcopiedmodeldefinitions;rawfoldersdefaultreasoning-only399tokens. RemainingSDK/fullCLIlaunchers/toolchain/training/adapter/sourcebuild/onboarding/alltoolbehavior/offmachine/future256GBconfigurationunfinished. Guardisatestmechanism,notgeneral sandbox. Coldcanonicalpubsnapshot26220,notlive28380/new28448.','Fouractualmodelpredictions(twoRawblank,twoConfiguredfinals)retained;prepwronginventorylabel0predictionsretained. Researchercausalwordingambiguous,Reviewer3vs2sentences,notqualitygain/heldoutbenchmark/independentmultiagentreview. Copieddefinitionthinkingdefaultsneeded;no blindpromptretry/newweighttraining. Originaldaily27B32K/1workerrestored,tempregistrationsremoved. I63savedrecords.','NativeChatlatestuseunverified;do notaskunlock/repeatstaleAXactions. CurrentSstillv12;actualMCPverifiedpublished28380/pending28448/coldmodelscope,nonewReaderpredictionorqualityclaim.Advertisingstep8loadablebutnogain;Gamenative-repair-v3step32unpromoted. Improvegeneralmethod/designpageretrievalwithvalidsourcecheckedquestions;SchreinerisordinaryexposedRAG,notfreshheldout.','Allfiniteworkerscompleted;donotrestart. OriginalCDIandpublished28380gameplayreceipts preserved,defaultpreviewunchanged. Currentnormalized28448buildremovesobsoleteinheritedstandalonefields;asrunbuild/startupproofsunchanged.Fullfourpartgoalactive.'])
    state['current_entrypoints']['prompts_I']='63savedprompt/transcriptrecords;4newcopied-weightpredictions(twoRawblank/twoConfiguredfinals),not63newpredictions'
    state['full_goal_requirements'][0].update(evidence=cold['report'],remaining='Actualcopiedweights+copieddefinitionsload/finalgenerationwork;nativeChat/easyfirstuse/fullCLI/taskformat/reliabilityunfinished.Rawdirectoryprofilefailed,noqualitygain.CurrentSstillv12.')
    state['full_goal_requirements'][1].update(evidence=chain['report'],remaining='Latestgameplaytested28380.New28448source-ownedCchainmaxstack564/minfixture354passes7680prototype+7680finalcases/15360nativecontextchecks/96startup,butneedsnewmonitor/freshgameplay. Remaininggamecode/interfaces/fullsameconsolerebuild/indoorlivebehavior/media/timing/physicalconsoleunfinished.')
    state['full_goal_requirements'][2].update(evidence=cold['report'],remaining='DailybaseandtrainedReviewerexportready;bothactualcoldcopiedweightsloadandproducefinalswithcopieddefinitions.Noobservedqualitygain;ReviewerformatandResearchercausalwordinglimits.Validsourcegroundedresearchteachingreview/generalmethodpageaccessunfinished.No newoptimizersteps.')
    state['full_goal_requirements'][3].update(evidence=cold['report'],remaining='Actualcoldmoveoutsideworkbench8080files50.76GB,bundledPythonvenv/indexpathrepair,7of18toolkinds/4controls,39modelresources10shardsverified,andcopiedweightsinferencewithoriginalSDKclientpass.FullSDK/CLI/toolchain/training/workflow/sourcebuild/onboarding/alltools/offmachine/future256GBconfigurationunfinished.')
    save(out/'protocol.json',state);save(pointer,state)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:
        stream.write(json.dumps(dict(recorded_at=now.isoformat(),event='source_owned_C_chain_and_cold_moved_model_inference',coordinator='CABIsharedcontext/negativecontrols/28448developmentdisc/startup/metadata-normalization; actualpackagecoldmove/pathrepair/toolcontrols/copiedmodeldefinitionsinference',local_models='Fouractualcopiedweightpredictions:twoRawreasoningonly,twoConfiguredfinals;format/causalwordinglimitsretained',actual_predictions=4,new_training=False,gameplay_tested_bytes=28380,development_bytes=28448,development_gameplay_frames=0,source_C_max_private=564,fixture_min_headroom=354,model_files_copied=39,copied_model_final_responses=2,full_migration=False,goal_complete=False,bound_files_verified=len(dependencies)))+'\n')
    print(json.dumps(dict(status=state['status'],bound_files=len(dependencies),published=28380,pending_development=28448,pending_jobs=0,goal_complete=False)))


if __name__=='__main__':main()
