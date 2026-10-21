"""Freeze tested scan-restoration evidence and publish a read-only LM context.
Active test pointers are not dependencies of the published result. Small
proof/source/runtime files are copied; large versioned run/image files remain
hash-pinned. Working native source changes are disclosed separately.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'

def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    bp=ROOT/'verification/native-word-scan-build-current.json';build=read(bp);baseline=read(build['baseline_proof']);gate=read(ROOT/'verification/native-word-scan-current.json')
    first=read(ROOT/'verification/native-word-scan-route-current.json');analysis=read(ROOT/'verification/native-word-scan-route-analysis-current.json')
    follow=read(ROOT/'verification/native-word-scan-clearance-long-route-current.json');final=read(ROOT/'verification/native-word-scan-clearance-analysis-current.json');prefix=read(ROOT/'verification/native-word-scan-prefix-current.json')
    author=read(build['author_proof'])
    assert gate['build_proof_sha256']==sha(bp) and gate['native_cases']==512 and final['both_completed']
    assert follow['build_proof_sha256']==first['build_proof_sha256']==sha(bp)
    assert all(x['full_recorded_rows_different']==0 and x['PCM_prefix_equal']for x in prefix['results'].values())
    assert analysis['results']['native_repaired']['continuous_merchant_to_outdoor']
    assert not analysis['results']['native']['continuous_merchant_to_outdoor'] and not analysis['results']['original']['continuous_merchant_to_outdoor']
    for obj in [build,baseline,gate,first,follow,analysis,final,prefix]:
        for field in ['source_dependencies_sha256','source_sha256','execution_dependencies_sha256']:
            values=obj.get(field,{})
            if isinstance(values,dict):
                for p,digest in values.items():assert sha(p)==digest,p
    for lane,row in final['results'].items():
        obs=row['observation'];assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']) and obs['word_scan_repaired']==1
        if lane=='native_repaired':assert obs['old_rng_steps']==obs['old_keypad_steps']==obs['old_controller_steps']==0
        x=row['final_fields'];assert x['player_mode_word']==1 and x['floor_word']==0 and x['scene_word']==312
        assert (x['raw_player_X']-13056)**2+(x['raw_player_Z']-42400)**2<=64
    pins={}
    for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=read(ROOT/'verification'/name)
        for p,digest in recipe['hashes'].items():assert sha(p)==digest,p
        pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
    assert sha(baseline['original_disc'])==baseline['original_disc_sha256']
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-word-scan-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    snapshots=out/'snapshots';snapshots.mkdir();deps={};source_index={};observed_native={}
    def pin(path,copy=False):
        path=Path(path).resolve();assert path.is_relative_to(ROOT),path
        digest=sha(path);relative=str(path.relative_to(ROOT))
        if copy:
            dest=snapshots/(hashlib.sha256(relative.encode()).hexdigest()[:12]+'-'+path.name);shutil.copy2(path,dest);assert sha(dest)==digest
            deps[str(dest.relative_to(ROOT))]=digest;source_index[relative]=dict(snapshot=str(dest.relative_to(ROOT)),sha256=digest)
        else:deps[relative]=digest
        if path.parent==ROOT/'projects/black-ice-white-noise/restoration/native-m68k' and(path.suffix in ['.c','.h','.S','.ld']or path.name.startswith('Makefile')):observed_native[relative]=digest
    paths=[bp,ROOT/'verification/native-word-scan-current.json',ROOT/'verification/native-word-scan-route-current.json',ROOT/'verification/native-word-scan-route-analysis-current.json',ROOT/'verification/native-word-scan-clearance-long-route-current.json',ROOT/'verification/native-word-scan-clearance-analysis-current.json',ROOT/'verification/native-word-scan-prefix-current.json',Path(build['baseline_proof']),Path(build['author_proof']),Path(__file__),ROOT/'native_restoration_evidence.py',ROOT/'verification/native-controller-lean-rng-current.json',ROOT/'verification/native-controller-lean-bundle-current.json']
    for p in paths:pin(p,True)
    for obj in [build,baseline,gate,first,follow,analysis,final,prefix]:
        for field in ['source_dependencies_sha256','source_sha256','execution_dependencies_sha256']:
            values=obj.get(field,{})
            if isinstance(values,dict):
                for p in values:pin(p,True)
    pin(ROOT/'verification/zero-warm-startup-instruction-atlas.bin',True)
    for p in [baseline['original_disc'],baseline['derived_disc'],baseline['component'],baseline['linked_component'],build['binary'],build['ELF']]:pin(p)
    for lane,row in build['images'].items():assert sha(row['disc'])==row['sha256'];pin(row['disc'])
    for group in [first,follow]:
        for lane in group['lanes']:
            folder=Path(group['directory'])/lane
            for name in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','state-final.bin','frontend-PCM.s16le','original-emulator-final-frame.png','video-final.xrgb8888']:pin(folder/name)
    for p in [Path(gate['directory'])/'cases.json',Path(gate['directory'])/'original_vs_repaired.json',Path(author['directory'])/'prompts-and-responses.txt']:pin(p,True)
    a=final['results']['original_repaired'];b=final['results']['native_repaired'];native_folder=Path(follow['directory'])/'native_repaired';original_folder=Path(follow['directory'])/'original_repaired'
    video_equal=sha(original_folder/'video-final.xrgb8888')==sha(native_folder/'video-final.xrgb8888');PCM_equal=sha(original_folder/'frontend-PCM.s16le')==sha(native_folder/'frontend-PCM.s16le')
    facts=dict(status_label='experimental_native13_source_assembled_scan_restoration',current_result='Published diagnostic CDI combines native13entry components with the existing marker-scan repair assembled from unchanged guided local-model source.18bytefragment/14actualchangedbytes; not a14thcompletefunction or a whole source-built game. Both repaired images complete the fresh merchant→two descents→outdoorclearance→120idleframes itinerary.',
        entries=13,repair_fragment_bytes=18,repair_actual_changed_bytes=14,new_complete_function_entries=0,target_CPU=68000,resident_bytes=baseline['component_bytes'],linked_resident_bytes=baseline['linked_component_bytes'],reserved_bytes=baseline['heap_bytes_reserved'],
        scan_native_cases=gate['native_cases'],scan_test_scope='All32CCRvalues/user-supervisor, explicit wordphase/full16marker-run/endboundary/partialrun fixtures, fullCPU/RAM/cycles vslegacyrepair. Original4bytestride fails2bytephase fixture while assembledrepair finds it. Not a complete loader or hardware oracle.',known_scan_read_limit=gate['known_limitation'],
        matched_state_scope=f"Fresh repaired original runs{a['executed_frames']}frames, native{b['executed_frames']}frames. Both reach merchant/floor2, descend2→1→0 and clear the doorway before120idleoutdoorframes. FinalX13049matches; finalZ differs({a['final_fields']['raw_player_Z']}vs{b['final_fields']['raw_player_Z']}). No per-frame or whole-machine equivalence claim.",
        repaired_route_results={lane:{key:row[key]for key in ['executed_frames','first_scene_change','merchant_reached','nonzero_audio_samples','final_fields','last_outdoor_hold','observed_floor_transitions','continuous_merchant_to_outdoor']}for lane,row in final['results'].items()},
        first_four_arm_controls={lane:{key:analysis['results'][lane][key]for key in ['executed_frames','merchant_reached','final_fields','observed_floor_transitions','continuous_merchant_to_outdoor']}for lane in ['original','native']},
        control_scope='First fourarm experiment used the same feedback policy with original/native x repair/no-repair. Both unmodified controls remain loadingfloor1atfinitecutoff. Native repaired completedroute/120hold. Original repaired reachedoutdoorlate; cutoffleft53holdframes. Followup reran onlytwo repairedlanes with morebudget and post-entryclearance. Negativecontrols neverreached thechangedbranch; they were retained, not rerun.',
        deterministic_prefixes=prefix['results'],final_video_equal=video_equal,audio=dict(original_nonzero_samples=a['nonzero_audio_samples'],native_nonzero_samples=b['nonzero_audio_samples'],total_PCM_equal=PCM_equal,listening_test=False,physical_console_audio=False),
        actor_scope='New feedback runs do not establish full actor/video/PCM equivalence. The prior unrepaired13entry fixed-input replay differed407of413actor snapshots and missed the building; that is a separate image/profile, not a fixed-input test of this repaired CDI.',
        previous_unrepaired_fixed_input_profile=dict(frames=24738,actor_sample_differences=407,actor_samples=413,video_different_frames=22456,route_pass=False),latest_repaired_fixed_input_equivalence_tested=False,
        naturally_observed_controller_calls=b['observation']['controller_entries'],native_original_controller_RNG_keypad_body_instructions=0,
        authorship='Local Author4.05s and Reviewer5.46s on same27Bweights under a full coordinator instruction plan. Author used bareuppercase registers despite requested percent syntax; documented GNU register-prefix-optional assembles unchanged source. Coordinator linker initially aligned to1B0F0; exactbytegate rejected it before anyCDIcopy, then explicit1B0EE/SUBALIGN2fixed it. Coordinator wrote build/tests/feedbackpolicies and source review. No new weights or independent model validation.',
        workflow_corrections='First route classifier missed floor2because Down changed it within the sampledframe; corrected analysis uses precedingstate and2→1→0transitions. Original repaired latearrival was a cutoff issue, not observed instability. One insufficient-budget followup was stopped early; boundedlongerfollowup preserved.',
        execution_scope='Ordinary fresh CDI/HLE load and normal padinputs; no checkpointrestore, hostguestRAM/codewrites, player/sceneinjection, CPU reseed or host markerpatch. Repair already resides on disc and is checked at400Aand every scanentry. Native13residentpayload unchanged; arithmetic still source-assembled at oldaddresses. Original game/emulatorCPU/GPU/DSP/HLE/CD/device providers remain.',
        remaining='Complete source/native modules/full-game link/provider work; investigate timing, actor/audio and fixed-input differences. This preserves existing scan read limitations. Physical/authenticated boot, audible listening, fullgame equivalence, fresh nativeChat rendering/cancellation and futurehardware benchmarks remain unverified.',
        previews='Running preview and P/O112/84pins preserved; repaired CDI is a separate diagnostic artifact.',new_training=False,native_Chat=False)
    relative_artifacts=dict(derived_disc=str(Path(build['images']['native_repaired']['disc']).relative_to(ROOT)),original_repaired_disc=str(Path(build['images']['original_repaired']['disc']).relative_to(ROOT)),compiled_binary=str(Path(baseline['linked_component']).relative_to(ROOT)),proof=str((out/'publication.json').relative_to(ROOT)),canonical_assembly=str(Path(build['canonical_source']).relative_to(ROOT)),exact_author_prompts=str((Path(author['directory'])/'prompts-and-responses.txt').relative_to(ROOT)),final_outdoor_PNG=str((native_folder/'original-emulator-final-frame.png').relative_to(ROOT)))
    manifest=dict(schema_version=1,status='published_native_word_scan_restoration_with_remaining_limits',recorded_at=now.isoformat(),directory=str(out),facts=facts,relative_artifact_fields=relative_artifacts,dependencies_sha256=deps,source_snapshots=source_index,observed_game_source_sha256=observed_native,preview_pins=pins,original_disc_unchanged=True,whole_game_complete=False)
    save(out/'publication.json',manifest);save(ROOT/'verification/native-word-scan-publication-current.json',manifest)
    # Install the frozen reader first; then prefer it over mutable work pointers.
    shutil.copy2(ROOT/'native_restoration_evidence.py',RT/'native_restoration_evidence.py')
    for root in [ROOT,RT]:
        p=root/'chat_tools.py';s=p.read_text();start=s.index('        import native_rng_evidence\n');end=s.index('        if rng_summary:\n',start);block=s[start:end]
        replacement='        import native_restoration_evidence\n        rng_summary=native_restoration_evidence.load(frame_test_jobs.workspace())\n        if not rng_summary:\n'+''.join('    '+line if line.strip()else line for line in block.splitlines(True))
        p.write_text(s[:start]+replacement+s[end:])
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    for root,label in [(ROOT,'workspace'),(RT,'installed')]:
        for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(root/name,out/(label+'-previous-'+name))
    decomp=f'''BLACK ICE WHITE NOISE — ON-DISC SOURCE-ASSEMBLED SCAN RESTORATION
Updated {now.isoformat()}

RESULT
Both repaired images now complete a fresh building/merchant→two elevator descents→outdoorclearance→120idleoutdoorframes route. Native repaired:24,979frames, finalX13049/Z42402/mode1/floor0/retainedscene312. Repaired original:29,784frames, finalX13049/Z42401/mode1/floor0/scene312. Final raw video matches: {video_equal}. Audio totals and timings differ; this is not whole-machine or per-frame equivalence.
The18byte source-assembled repair changes14bytes relative to each preserved original/native13baseline. It is a fragment inside the existing loader, not a14thcompletefunction. Native13stillcontains8C RNG entries,C keypad,C controllerpoll and3source-assembled arithmetic helpers. Broader hostedC restoration/preview work remains separate;13is not totaldecompcoverage or completionpercentage. Original game/emulatorCPU/GPU/DSP/HLE/CD/device providers remain. Full-game source rebuilding, authenticated/physicalconsole boot and listening remain unverified.

CONTROLLED EXECUTION
Firstfourfreshlanes used one feedback policy. Unmodified original and native13both reachedthemerchant but did notfinish the firstdescent before finitecutoffs29,538/29,536frames; they remained loadingfloor1/scene313. Repairednative completedreturn+120hold in24,809frames. Repairedoriginal enteredoutdoor29,499but cutoff29,552left53holdframes. This was not verifiedinstability.
Thefollowup reran onlythetwo repairedimages, continuingto clearancepoint13056,42400(tolerance8)before120idleframes and extendingthefinitebudget. Both passed. Their fullrecorded state dictionaries and exactPCM prefixes reproduce the firstruns through outdoorentry(29,499original/24,689native), withzerodifferences. Earlier unmodified controls neverreached the changedbranch; they were retained, notrerun.
Allgameplaystarts with ordinaryCDI/HLEload and normalpadinput. No checkpointrestores, hostguestmemory/codewrites, position/sceneinjection or CPUreseeds. Repair is ondisc beforeload; read-only code signatures are checked at400Aand eachscanentry. Native candidate runszerooriginal controller/RNG/keypad bodyinstructions; arithmetic atoriginaladdresses is source-assembled code. Audio capturednonzerosamples: original7,324,936/native1,609,492. Differentroute lengths/states mean this isnot anisolated audio-enginecomparison or listeningtest.

ASSEMBLY / COMPONENTS / LIMITS
Theunchanged localmodelsource assembles to the exactlegacy18byte repair at1B0EE, targeting1B100and1B122. It checks candidate starts every2bytes after mismatch ratherthan4.512current-nativeCPUfixtures cover all32CCRvalues/userandsupervisor, wordphase,16marker-run, exactend, overrun andpartialrun cases. FullCPU/RAM/cycles match thelegacy repairedbytes atdeclaredcontinuations; original4bytestride fails the2bytephase fixture.
This isnot a generallybounds-safe parser: candidate longread occurs before thelimitcheck; no-marker/partial-run fixtures readacross1C8000, and a16longrunpastend isreadbefore its payloadpointer isrejected. Existing downstreamguard remains; do notclaim allreadsarebounded.
The underlying native13component gates remain separate:1,216fullCPU/RAM/flags/stackbankcontroller cases,1,024orderedrawMMIOcases,1,682RNGCPU/298accesscases,96entry/heapcleanup and5,151postheapkeypadcases. RNGzero-divisor behavior remains unverified. Native13code2694bytes+padded822to3516; heapreserve3520; loader7625instructions/84126cycles. Controllednativecontrollercost554cycles includingCDIJMP versusoriginal510; noFPSclaim.

WHO / PROMPTS
LocalAuthor4.05seconds, Reviewer5.46seconds, same27Bweights and noindependentvalidation. Coordinator supplied thefull six-instruction plan. Author ignoredpercent-register syntax, but unchanged sourceassembles with documentedGNU --register-prefix-optional. Coordinator linker firstalignedtextto1B0F0; exactbytechecks rejectedthat beforeCDIcopy. Explicit1B0EEoutputaddress/SUBALIGN2nowverified. No manualassembly edits or newweighttraining.
Coordinator built images/tests/feedbackpolicies and corrected ananalysisbug: thefirstDown changesfloor2to1within the sampledframe, so thevalidcriterion uses the precedingstate and2→1→0transitions. One insufficient-budgetfollowup wasstoppedearly; itslogs/reason remain. These were hostharness issues, not newgamecode failures.
Exact Author/Reviewer prompts/responses:
{ROOT/relative_artifacts['exact_author_prompts']}
Frozen publication andsource/proof snapshots:
{out}
The LM evidence reader verifies immutablepublished artifacts, not active mutabletestpointers. Workingnative-source edits are reportedseparately anddo notturn oldpublished results into claimsabout untestednewsource.

USE / REBUILD
Latest diagnostic native13+scan CDI:
{ROOT/relative_artifacts['derived_disc']}
Original+scan comparison:
{ROOT/relative_artifacts['original_repaired_disc']}
Source:{native/'marker-word-scan.S'}
Buildscript:{ROOT/'scripts/build_biwn_native_word_scan.py'}
Itassembles thefragment andderivestwoCDIs from accepted baselines; component/freshroutegates areseparate. This isnot acompletegamesource build. AllotherCDIbytes/metadata and bothbaselines werecheckedunchanged. Prior unrepaired13fixed-input24738route failed(407/413actorsamples,22456videoframesdifferent); thatdoesnot serveasa fixed-inputtestofthisrepairedCDI.
Desktop/Local AI Lab/Show BIWN Native Disc.command reveals thisdiagnostic. Yourrunningpreview andP/O112/84pins remain unchanged. Clickinsidepreview; C+Up runs,arrowsmove/turn,Z=A,X=B,C=C,Ppause,Mmute,Escclose.

NEXT
Continue actualsource/nativeengine/link/provider work andtiming/actor/audio fidelity, beyond thisrepairfragment. Advertisingbase/retrieval isinstalled; two unattended two-paperpipelines remain rejected, witha241word guided/coordinator-qualified teachingdraft saved. SeeCURRENTADVERTISING.txt. FreshnativeChatrendering/cancellation andfuture256GBhardwarebenchmarks remainunverified. Fullgoal is incomplete.
'''
    inference=f'''LOCAL AI — CURRENT WORKFLOW
Updated {now.isoformat()}

Start Local AI.command:1GameAssistant,2AdvertisingAssistant,3game team,4advertising team,5LMStudioChat,Pmainpreview,Ooutdoorpreview. Daily27B6bit advertising-scholar,32Kcontext/onesharedworker. Rolesrun sequentially onsameweights, notindependentvalidation.

LATEST GAME OUTPUT
LocalAuthor4.05s/Reviewer5.46s produced/explained thesourcefor acoordinator-planned18byte marker-scanrepair.512nativefixtures pass; a14byteCDIdelta lets thenative13image complete thefresh merchant→two descents→outdoorclearance→120idleframes route in24,979frames. Repairedoriginal alsofinishes in29,784frames. Finalrawvideo matches; timing/finalZ/audio differ. No whole-game/physicalconsole proof. Promptsandcomplete scopes areinCURRENT DECOMPILATION.txt.
Gameevidence now reads immutablepublishedsource/proof snapshots. Active testpointerchanges do not invalidate oldpublishedoutput; editednative sources aremarked asuntestedrelative tothatimage. BackendnativeChatcontext ischeckedseparately; nofresh nativeUIgeneration/render/cancellation observation or fabricatedhistory.

ADVERTISING
Choose2: Correct grammar only: [text] invokes CopyEditor→CopyReviewer; /newreturnstoresearch. Choose4for Researcher→Educator→Reviewer. Latesttwo-paperwork fixed missingoriginalmethodpages andover-shortrepairguidance, but broadunattendedpipelines remainrejected. Reviewed241wordteachingdraft andexactprompts areinCURRENT ADVERTISING.txt. Baseplusretrieval preferred; V6/V7adapters quality-rejected. No newweighttraininghere.

Yourrunningpreview ispreserved; holdC+Up torun. Wholegamesource/link/provider work, fidelity, physicalconsole andfuturehardwarebenchmarks remainunfinished.
'''
    for root in [ROOT,RT]:(root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
    reveal=ROOT/'scripts/reveal_biwn_native_disc.py';s=reveal.read_text();marker="for name in ['native-controller-publication-current.json',";assert s.count(marker)==1;reveal.write_text(s.replace(marker,"for name in ['native-word-scan-publication-current.json','native-controller-publication-current.json',"))
    # Existing reveal utility expects a top-level derived_disc; facts reader uses relative fields.
    manifest['derived_disc']=str(ROOT/relative_artifacts['derived_disc']);save(out/'publication.json',manifest);save(ROOT/'verification/native-word-scan-publication-current.json',manifest)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),action='published_source_assembled_on_disc_scan_restoration',publication=str(out/'publication.json'),native_entries=13,repair_fragment_bytes=18,actual_extra_changed_bytes=14,fresh_native_route_frames=24979,fresh_original_repaired_route_frames=29784,new_training=False,native_Chat=False,whole_goal_complete=False))+'\n')
    print('Published',out);print('Final video equal',video_equal,'PCM equal',PCM_equal);print('Frozen dependencies',len(deps),'source snapshots',len(source_index));print('Previews preserved',pins)
if __name__=='__main__':main()
