"""Publish the exact compiler variant, complete scoped checks and local use."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))


def read(path):return json.loads(Path(path).read_text())
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-string-ccr-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    bp=ROOT/'verification/native-ccr-format-bundle-current.json';bundle=read(bp)
    prep=read(ROOT/'verification/native-string-ccr-preparation-current.json');full=read(Path(prep['directory'])/'full-gate/native-format-string-current.json')
    assert full['source_accepted']and full['native_cases']==1945 and full['changing_read_cases']==16
    negative=read(Path(prep['directory'])/'preflight-negative/native-format-string-active.json');mismatch=read(Path(negative['directory'])/'mismatch.json')
    assert negative['status']=='terminal_failed'and mismatch['case']==1 and mismatch['original_CPU'][17]!=mismatch['compiled_CPU'][17]
    gates={kind:read(ROOT/'verification'/('native-ccr-format-'+kind+'-current.json'))for kind in ['pad','string','callers']}
    for gate in gates.values():assert gate['source_accepted']and gate['binary_sha256']==bundle['binary_sha256']
    integration=read(ROOT/'verification/native-ccr-format-integration-current.json');assert len(integration['full_gates'])==19
    assert all(integration['jobs'][key]['status']=='terminal_pass'for key in integration['full_gates'])
    build=read(ROOT/'verification/native-ccr-format-disc-build-current.json');assert build['linked_component_bytes']==8482 and build['component_bytes']==9216
    assert build['linked_component']==bundle['binary']and sha(bundle['binary'])==bundle['binary_sha256']
    deck=read(ROOT/'verification/native-ccr-format-selector-deck-pair-current.json');obs=deck['observations']['candidate']
    assert obs['compiled_format_calls']==obs['format_entries']==obs['format_returns']==[5787,127]
    assert obs['format_stack_outside']==[0,0]and obs['format_pending_at_finish']==obs['format_tracking_errors']==0
    route=read(ROOT/'verification/native-ccr-format-long-route-current.json');route_out=Path(route['directory'])
    reports={lane:read(route_out/lane/'report.json')for lane in ['parent','ccr']}
    a,b=reports['parent']['frames'],reports['ccr']['frames'];assert len(a)==len(b)==29791
    fields=['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word','video_sha256','cumulative_nonzero_audio_samples','CPU','GPU','DSP','GPU_R31_banks']
    comparisons={k:sum(x[k]!=y[k]for x,y in zip(a,b))for k in fields};assert not any(comparisons.values())
    assert all(x['navigation']==y['navigation']for x,y in zip(a,b))
    pcm_equal=sha(route_out/'parent/frontend-PCM.s16le')==sha(route_out/'ccr/frontend-PCM.s16le');assert pcm_equal
    assert all(r['merchant_reached']and r['completed_outdoor_hold']for r in route['results'].values())
    cost=read(ROOT/'verification/native-format-optimization-replay-CCR-O2-lean-current.json');assert cost['completed']==84 and cost['live_return_CPU_all_match']and cost['live_written_bytes_all_match']
    assert cost['summary']['string']['compiled_cycles']==87152
    agent_path=ROOT/'verification/native-ccr-agent-current.json';agent=read(agent_path)
    assert agent['status']=='terminal_verified_optimizer_output_pending_review'and not agent['answer_review_flags']and agent['expected_tool_sequence']
    assert len(agent['calls'])==2 and len(agent['answer'].split())<150
    regression=read(ROOT/'verification/native-ccr-workflow-check-current.json')
    assert regression['model_visible_results_unchanged_after_cost_binding']and regression['old_certificate_unchanged']
    agent.update(coordinator_review='accepted_exact_raw_compiler_workflow_answer',review_scope='Grounded fixed-tool orchestration; not source authorship, new training or a fresh CPU test in the model turn.')
    save(Path(agent['directory'])/'protocol.json',agent);save(agent_path,agent)
    certificate=read(ROOT/'verification/native-string-ccr-certificate-current.json')
    deps={};snapshots={}
    def bind(path,snapshot=False):
        path=Path(path).resolve();deps[str(path)]=sha(path)
        if snapshot:
            target=out/'snapshots'/(hashlib.sha256(str(path).encode()).hexdigest()[:16]+'-'+path.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target);snapshots[str(path)]=str(target)
    # Core semantic proof closure, kept independent of UI settings/current
    # launcher result pointers. No need to invalidate game evidence on a UI edit.
    parent_publication=ROOT/'verification/native-optimized-format-publication-current.json'
    for path,digest in read(parent_publication)['dependencies_sha256'].items():assert sha(path)==digest,path;bind(path)
    for proof in [prep,bundle,certificate,cost]:
        for table in ['dependencies_sha256','source_sha256']:
            values=proof.get(table,{})
            if isinstance(values,dict):
                for path,digest in values.items():assert sha(path)==digest,path;bind(path)
    for data in [full,*gates.values(),build,route,deck]:
        bind(Path(data['directory'])/'protocol.json'if(Path(data['directory'])/'protocol.json').exists()else Path(data['directory'])/'build.json')
        for table in ['source_sha256','artifacts_sha256']:
            values=data.get(table,{})
            if isinstance(values,dict):
                for path,digest in values.items():assert sha(path)==digest,path;bind(path)
    for key,job in integration['jobs'].items():
        assert job['status']=='terminal_pass';bind(job['proof']);assert sha(job['proof'])==job['proof_sha256']
        proof=read(job['proof'])
        for table in ['source_sha256','artifacts_sha256','execution_dependencies_sha256']:
            values=proof.get(table,{})
            if isinstance(values,dict):
                for path,digest in values.items():assert sha(path)==digest,path;bind(path)
        if proof.get('directory'):
            for path in Path(proof['directory']).rglob('*'):
                if path.is_file():bind(path)
    for pointer in ['native-ccr-format-bundle-current.json','native-ccr-format-integration-current.json','native-ccr-format-pad-current.json','native-ccr-format-string-current.json',
                    'native-ccr-format-callers-current.json','native-ccr-format-disc-build-current.json','native-ccr-format-selector-deck-pair-current.json',
                    'native-ccr-format-long-route-current.json','native-format-optimization-replay-CCR-O2-lean-current.json',
                    'native-string-ccr-preparation-current.json','native-string-ccr-certificate-current.json']:
        bind(ROOT/'verification'/pointer,True)
    for folder in [Path(bundle['directory']),Path(full['directory']),Path(negative['directory']),Path(deck['directory']),route_out,Path(cost['directory'])]:
        for path in folder.rglob('*'):
            if path.is_file():bind(path)
    bind(build['derived_disc']);bind(parent_publication,True)
    # The current-status result intentionally covers only this bound binary,
    # its scoped tests and finite routes; this is not goal completion.
    core_deps=dict(deps)
    assert all(Path(p).is_relative_to(ROOT)for p in core_deps)
    manifest=read(build['patch_manifest']);redirects=sum(bytes.fromhex(p['replacement'])[:2]==b'\x4e\xf9'and bundle['base']<=int.from_bytes(bytes.fromhex(p['replacement'])[2:6],'big')<bundle['base']+bundle['reserved_bytes']for p in manifest['patches'])
    assert redirects==25
    summary=('Latest separately tested mixed original/new Jaguar CD experiment uses an8482byte resident bundle in the same9216byte reservation. '
        'A deterministic per-bit CCR compiler pass reduces the string helper flag-calculation sites23to8; it passed full1945native/ordered cases plus16changing-read cases. '
        'The linked pad and formatter/caller gates and19install/component/resource checks pass. '
        'On26captured string calls, emulated test cycles fall56.4percent from199680to87152, still6.9times original assembly. '
        'The repaired2600frame Deck run observes127compiled string returns with no stack violation. '
        'A separate fresh29791frame merchant/floor0/outdoor route matches the previous compiled build in every recorded selected game/video/processor-PC field,navigation decision and rawPCMbytes. '
        'These finite checks are not whole-game timing,full machine-state equivalence,physical-console or audio-quality proof. '
        '25stageJMPredirects are not a recovered-function total or completion percentage. No default preview or new weight promotion; full recovery/training/futurehardware remain incomplete.')
    status=dict(project='Black Ice White Noise, Atari Jaguar CD',status='terminal_CCR_compiler_bundle_gameplay_and_local_workflow_published',recorded_at=now.isoformat(),
        checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,
        proof=str(ROOT/'verification/native-string-ccr-publication-current.json'),
        experimental_build=dict(compiled_binary=bundle['binary'],binary_sha256=bundle['binary_sha256'],resident_bytes=8482,reserved_bytes=9216,heap_start=bundle['heap_start'],
             derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],declared_resident_redirects=25,
             redirect_count_scope='Stage JMP redirects into resident code; not all recovered functions or a decompilation percentage.',
             source_origin='Coordinator deterministic typed-IR compiler with per-bit CCR liveness; not local-model-authored C.'),
        string_source=prep['source'],static_flag_sites_before=23,static_flag_sites_after=8,
        scoped_install_component_resource_full_gates=integration['full_gates'],
        helper_gates={k:{f:v for f,v in g.items()if f in ['status','native_cases','ordered_cases','changing_read_cases','helper_returns','original_instruction_coverage','scope']}for k,g in gates.items()},
        sampled_string_cost=dict(cases=26,previous_compiled_cycles=199680,new_compiled_cycles=87152,original_assembly_cycles=12636,cycle_reduction_percent=56.354166666666664,
            scope='Offline previously captured entries with IRQ disabled. Emulated test cycles, not hardware timing or whole-game FPS.'),
        repaired_Deck=dict(frames_per_lane=2600,compiled_helper_entries=obs['compiled_format_calls'],returns=obs['format_returns'],stack_outside=obs['format_stack_outside'],headroom=obs['format_min_headroom'],comparisons_to_original_helpers=deck['comparisons'],
            scope='Both discs carry shared38byte selector/count repairs. This is the measured live string path; finite scope.'),
        long_route=dict(frames_per_lane=29791,selected_frame_differences=comparisons,navigation_equal=True,raw_PCM_equal=True,merchant_floor0_outdoor_hold_both=True,
            nonzero_audio_samples=route['results']['ccr']['nonzero_audio_samples'],
            scope='Separate ordinary-button adaptive route, no added Deck selector repairs. Resource observer does not count string calls here; string activity is demonstrated in the separate Deck run.'),
        local_inference_example=dict(role='Coordinator with deterministic compiler tools',seconds=agent['seconds'],tool_calls=2,local_model_authored_C=False,prior_exact_CPU_receipts_reused=True,fresh_CPU_tests_in_model_call=False,
            launcher=str(ROOT/'BIWN Verified Optimizer.command'),preset='BIWN Verified Optimizer',native_Chat_verified=False),
        job_status_scope='This publication records completed finite checks; unrelated live jobs are not scanned.',
        this_lookup_executes_game_tests=False,new_training=False,default_promoted=False,whole_game_complete=False,goal_complete=False,physical_console_verified=False,
        whole_game_speedup_demonstrated=False,physical_audio_or_quality_verified=False,
        remaining=['Recover/link remaining game/platform behavior; isolate earlier scheduling and broader timing fidelity.',
                   'Verify physical Jaguar CD authentication/boot and audio quality.','Reliable general local C authorship and advertising research/education training remain open.',
                   'Future256GBhardware not tested.'],available_evidence_topics=['frame_runtime','boot_loader','world_input_rendering','local_code_authorship','local_training','scene_loading','controls'])
    report=ROOT/'reports/native-string-ccr-compiler-and-local-workflow.txt'
    status['report']=str(report)
    report.write_text('BIWN VERIFIED CCR COMPILER / LOCAL WORKFLOW\n'+now.isoformat()+'\n\n'+summary+'\n\n'
        'USE IT\nDesktop → Local AI Lab → BIWN Verified Optimizer.command. The local Coordinator calls the two fixed compilerMCPtools and saves exact prompts/responses. '
        'Native preset: BIWN Verified Optimizer. In an LM Studio game chat enable biwn-compiler-workbench; the preset alone does not enable integrations. '
        'The localSDKrun is verified; no fresh nativeChatwindow generation was verified.\n\n'
        'WHO DID WHAT\nCodex coordinator wrote the per-bit backward CFG liveness pass and verifier orchestration. '
        'The compiler tool generated the complete supported helper; originalCPU/ordered-memory checks supplied independent semantic evidence. '
        'The local model orchestrated fixedtools; it did not authorC,runnewCPUtests or train weights. '
        'One actual local Coordinator generation,'+str(round(agent['seconds'],2))+'seconds,twoMCPcalls; raw answer accepted after review.\n\n'
        'SOURCE / BUILD\n'+prep['source']+'\n8482linked bytes,down560from9042;734bytes padding;heap0x1611C0unchanged. '
        'The unchanged libgcc multiply helper moved with the shorter body; three verifiedJSRrelocations explain all earlier-prefix byte differences. '
        'The first builder assertion expected literal prefix identity and rejected those relocations; its source/build retained. '
        'An install metadata reader initially treated a scalar sourcehash as a dependency map; fixed before configuration/model use. '
        'Cost validation was subsequently bound to original receipts; freshMCPresults exactly repeat the model-visible facts.\n\n'
        'CHECKS\nStandalone1945native+1945ordered+16changing; exact linked pad1668/1668+16 andstring1945/1945+16; '
        'complete formatter/callers1654cases,5161helperreturns;19component/install/resource gates. '
        'Deliberately dropping required returnNZVCflags fails originalCPUcase1; full optimization passes. '
        'Standalone binary918bytes versus prior1136; linked bundle8482versus9042. '
        '26captured string calls:87152emulated cycles versus199680previouscompiled/12636original. No whole-game FPS claim.\n\n'
        'LIVE ROUTES\nRepaired2600frame Deck pair:5787pad/127string entries andreturns,no stack violation/pending/tracking error; '
        'minimum observed headroom602/580bytes. Compared with same-layout original helpers,video differs642frames,X45,Z81;scene/mode/floor agree. '
        'Raw longer route: both29791frames,merchant→floor0→outdoor120framehold; selected game/video/processorPC fields,navigation andrawPCMrepeat exactly versusprior9042byteparent. '
        'The long observer counts resource contracts,not string activity. Final observed fields do not establish all machine-state/instruction-timing equivalence.\n\n'
        'EXACT LOCAL MODEL OUTPUT\n'+agent['answer']+'\n\nPROMPTS / TOOL RESPONSES\n'+agent['directory']+'/prompts-and-responses.txt\n\n'
        'Existing stringrecovery and advertising retrieval/rubricMCPregression pass. Rubric3.25/5is supplied-arithmetic transport,not grading validity or broad research quality. '
        'No new weights or defaultpreviewpromotion. Full goal remains active.\n')
    # Add workflow/config evidence separately from the core status closure.
    for name in ['scripts/publish_ccr_string_workflow.py','native_format_evidence.py','scripts/ask_biwn_current_status.py','scripts/run_biwn_status_reader.py',
                 'native_ccr_workbench.py','ccr_mcp_bridge.py','scripts/native_ccr_chat_tools.py','scripts/run_biwn_verified_optimizer.py','scripts/install_ccr_compiler_workflow.py','BIWN Verified Optimizer.command',
                 'verification/native-ccr-agent-current.json','verification/native-ccr-workflow-check-current.json','verification/native-ccr-workflow-install-current.json']:
        bind(ROOT/name,True)
    for path in Path(agent['directory']).rglob('*'):
        if path.is_file():bind(path,True)
    for path in [Path.home()/'.lmstudio/mcp.json',Path.home()/'.lmstudio/config-presets/BIWN Verified Optimizer.preset.json',Path.home()/'.lmstudio/local-ai-lab/native_format_evidence.py']:
        bind(path,True)
    history=[p for p in (ROOT/'verification/native-string-ccr-bundle').iterdir()if(p/'builder-as-failed.py').exists()]
    history+=[p for p in (ROOT/'verification/native-ccr-workflow-install').iterdir()if(p/'workbench-as-first-model-run.py').exists()]
    history.append(Path(read(ROOT/'verification/native-ccr-workflow-install-current.json')['directory']))
    for folder in sorted(set(history)):
        for p in folder.rglob('*'):
            if p.is_file():bind(p,True)
    for name in ['native-ccr-workflow-install.log','native-ccr-workflow-install-corrected.log','native-ccr-workflow-install-bound-cost.log']:
        bind(ROOT/'runs'/name,True)
    bind(report,True)
    proof=dict(status='terminal_CCR_compiler_bundle_gameplay_and_local_workflow_published',recorded_at=now.isoformat(),directory=str(out),report=str(report),
        current_status=status,status_dependencies_sha256=core_deps,dependencies_sha256=deps,snapshots=snapshots,
        local_LLM_calls=1,local_model_authored_C=False,new_training=False,default_promoted=False,native_Chat_verified=False,whole_game_complete=False,goal_complete=False)
    save(out/'report.json',proof);save(ROOT/'verification/native-string-ccr-publication-current.json',proof)
    head='CURRENT VERIFIED COMPILER / LOCAL WORKFLOW — '+now.isoformat()+'\n\n'+summary+'\nReport: '+str(report)+'\nLauncher: BIWN Verified Optimizer.command\n\nEARLIER RECORDS\n\n'
    for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
        path=ROOT/name;path.write_text(head+path.read_text())
    watch=ROOT/'WATCH LOCAL AGENTS.txt';watch.write_text('LATEST CHECKED OPTIMIZER\nBIWN Verified Optimizer.command: one localCoordinator plus fixedcompilerMCPtools; exactprompts/output saved. '
        'Nativepreset BIWN Verified Optimizer requires biwn-compiler-workbench enabled in that gamechat. SDKtested; no newnativeChatgeneration verified.\n'+str(report)+'\n\n'+watch.read_text())
    ledger=ROOT/'verification/goal-continuation-current.json';goal=read(ledger);save(out/'goal-before.json',goal)
    goal.update(status='active_CCR_compiler_experimental_disc_and_local_workflow_verified_full_goal_incomplete',recorded_at=now.isoformat(),
        previous_goal_turn_classification='progress',current_goal_turn_classification='progress',current_goal_turn_progress='New typed CCR-liveness C passes full helper/caller/install/resource and finite gameplay checks; smaller8482byte bundle and56.4percent fewer sampled stringcycles. New localCoordinator/MCPcompiler workflow verified.',
        current_goal_turn_evidence=str(ROOT/'verification/native-string-ccr-publication-current.json'),latest_local_inference=agent['directory'],latest_experimental_disc=build['derived_disc'],
        latest_finite_jobs_running=False,new_training=False,whole_game_complete=False,goal_complete=False,native_Chat_this_continuation=False,
        next_actions=['Extend safe typed compiler/lowering to remaining game routines with originalCPU/access verification.',
                      'Continue native gameplay/platform recovery and earlier task/IRQ phase investigation; preserve scoped timing limits.',
                      'Validate new optimizer workflow in nativeChat when UIavailable; do not infer UIgeneration fromSDKlogs.',
                      'Improve representative game/advertising training and held-out reliability; physicalconsole/audio andfuture256GBhardware remain open.'])
    save(ledger,goal)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:
        stream.write(json.dumps(dict(time=now.isoformat(),action='CCR_compiler_and_local_workflow_published',coordinator='Typed compiler,build,originalCPU/orderedtests,finitefreshgameplay and local-output review',
            local_roles=['Coordinator'],local_LLM_calls=1,deterministic_tools_not_LLM_agents=True,local_model_authored_C=False,training_updates=0,native_Chat_verified=False,
            proof=str(ROOT/'verification/native-string-ccr-publication-current.json')))+'\n')
    print(json.dumps({k:proof[k]for k in ['status','report','local_LLM_calls','goal_complete']}))


if __name__=='__main__':main()
