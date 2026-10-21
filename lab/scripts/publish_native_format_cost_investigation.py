"""Publish captured-context semantics/cost evidence and rejected local authors."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-format-cost-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);deps={};snapshots={}
    def bind(p,snapshot=False):
        p=Path(p).resolve();deps[str(p)]=sha(p)
        if snapshot:
            target=out/'snapshots'/(hashlib.sha256(str(p).encode()).hexdigest()[:16]+'-'+p.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target);snapshots[str(p)]=str(target)
    def tree(directory):
        for p in Path(directory).rglob('*'):
            if p.is_file():bind(p)
    prior_path=ROOT/'verification/native-format-resource-live-publication-current.json';prior=read(prior_path)
    assert all(sha(p)==h for p,h in prior['dependencies_sha256'].items());bind(prior_path,True)
    cp=ROOT/'verification/native-format-live-capture-current.json';capture=read(cp);assert capture['status']=='terminal_bounded_real_format_call_capture_complete';bind(cp,True);tree(capture['directory'])
    for p,h in capture['source_sha256'].items():assert sha(p)==h;bind(p)
    for lane,x in capture['captures'].items():assert x['selected_pairs']==42 and all(v==0 for v in x['repeat_differences_vs_prior_same_lane'].values())
    rp=ROOT/'verification/native-format-live-replay-current.json';replay=read(rp);bind(rp,True)
    assert replay['status']=='terminal_identical_real_helper_entry_CPU_RAM_ordered_replays_pass'and replay['completed']==84
    assert replay['live_return_CPU_all_match']and replay['live_written_bytes_all_match']
    for p,h in replay['dependencies_sha256'].items():assert sha(p)==h;bind(p)
    tree(replay['directory'])
    # Pin the existing replay backend/source closure without changing completed results.
    certificate_path=ROOT/'verification/native-string-source-certificate-current.json';certificate=read(certificate_path);bind(certificate_path,True)
    for p,h in certificate['dependencies_sha256'].items():assert sha(p)==h;bind(p)
    for p in [ROOT/'scripts/check_biwn_scheduler.py',ROOT/'scripts/check_biwn_world_movement_pipeline.py',ROOT/'scripts/check_biwn_inventory_frame.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']:bind(p)
    cases=read(Path(replay['directory'])/'results.json');hit=next(x for x in cases if x['lane']=='candidate'and x['kind']==0 and x['ordinal']==11)
    assert hit['entry_frame']==210 and hit['first_supervisor_PC']==0xe7d4 and hit['supervisor_excursions']==1
    memory=Path(capture['captures']['candidate']['directory'])/'0-11-entry.ram';assert int.from_bytes(memory.read_bytes()[0x100:0x104],'big')==0xe7d4
    core_root=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source'
    jaguar=core_root/'src/core/jaguar.c';interface=core_root/'src/m68000/m68kinterface.c';bind(jaguar,True);bind(interface,True)
    assert 'return 64;'in jaguar.read_text() and 'newPC = m68k_read_memory_32(vector << 2);'in interface.read_text()
    bp=ROOT/'verification/native-format-optimization-builds-current.json';builds=read(bp);bind(bp,True);variants={}
    for row in builds['candidates']:
        assert row['exit_code']==0
        vp=ROOT/'verification'/('native-format-optimization-replay-'+row['kind']+'-current.json');v=read(vp);bind(vp,True)
        assert v['status']=='terminal_optimization_live_fixture_CPU_RAM_ordered_pass'and v['completed']==84
        assert v['live_return_CPU_all_match']and v['live_written_bytes_all_match']and not v['fresh_game_run']
        for p,h in v['dependencies_sha256'].items():assert sha(p)==h;bind(p)
        tree(v['directory']);bundle=read(row['bundle_proof']);bind(row['bundle_proof'],True)
        for p,h in bundle['source_sha256'].items():assert sha(p)==h;bind(p)
        variants[row['kind']]=dict(binary_sha256=row['binary_sha256'],binary_bytes=row['binary_bytes'],summary=v['summary'],counterfactual_fixture_replay=True,fresh_game_run=False)
    best=variants['O2-lean'];assert best['binary_bytes']==9042
    helper_checks={}
    for kind,name in [('pad','native-optimized-format-pad-current.json'),('string','native-optimized-format-string-current.json'),('callers','native-optimized-format-callers-current.json')]:
        path=ROOT/'verification'/name;gate=read(path);bind(path,True)
        assert gate['binary_sha256']==best['binary_sha256']and gate['source_accepted']
        assert gate['native_cases']=={'pad':1668,'string':1945,'callers':1654}[kind]
        for p,h in gate['source_sha256'].items():assert sha(p)==h;bind(p)
        tree(gate['directory']);helper_checks[kind]={k:v for k,v in gate.items()if k in ['status','native_cases','ordered_cases','changing_read_cases','helper_returns','original_instruction_coverage','scope']}
    authors={}
    for role in ['author','repair']:
        path=ROOT/'verification'/f'native-string-optimization-{role}-current.json';a=read(path);bind(path,True)
        assert a['status']=='terminal_local_Author_candidate_unverified'and not a['C_target_supplied']and not a['new_training']
        preflight=Path(a['directory'])/'preflight/native-format-string-active.json';gate=read(preflight);assert gate['status']=='terminal_failed'
        mismatch=read(Path(gate['directory'])/'mismatch.json');assert mismatch['case']==0
        differences=[dict(register_index=i,original=x,candidate=y)for i,(x,y)in enumerate(zip(mismatch['original_CPU'],mismatch['compiled_CPU']))if x!=y]
        tree(a['directory']);tree(gate['directory'])
        authors[role]=dict(status='rejected_at_first_native_CPU_case',source=a['source'],source_sha256=a['source_sha256'],seconds=a['seconds'],input_tokens=a['input_tokens'],output_tokens=a['stats']['predictedTokensCount'],differences=differences,exact_prompts=str(Path(a['directory'])/'prompts-and-responses.txt'),native_Chat_verified=False,new_training=False)
    assert [x['register_index']for x in authors['author']['differences']]==[8,10]
    assert [x['register_index']for x in authors['repair']['differences']]==[8]
    failure_dir=ROOT/'evaluation/native-format-optimization';failure_dir.mkdir(exist_ok=True,parents=True)
    failure_record=dict(status='rejected_guided_development_candidates_not_training_targets',authors=authors,held_out=False,passing_C_target_supplied=False,production_source_changed=False)
    save(failure_dir/'development-failures.json',failure_record)
    for name in ['format_live_capture_extension.c','run_native_format_live_capture.py','replay_native_format_live_calls.py','build_native_format_optimization_candidates.py','prepare_native_format_optimization_replay.py','replay_native_format_optimization_live_fixtures.py','author_biwn_format_string_optimization.py','repair_biwn_format_string_optimization.py',Path(__file__).name]:bind(ROOT/'scripts'/name,True)
    # Preserve wrapper failures as failures; they did not change any emulator code.
    failure_history=[]
    for logname in ['native-format-live-replay.log','native-format-live-replay-corrected.log','native-format-optimization-replay-O2.log','native-format-optimization-replay-O3.log','native-format-optimization-replay-O2-lean.log']:
        path=ROOT/'runs'/logname;bind(path,True);failure_history.append(str(path))
    for p in (ROOT/'verification/native-format-live-replay').glob('*/python-driver-as-failed.py'):bind(p,True);bind(p.parent/'protocol.json',True)
    report=ROOT/'reports/native-format-cost-investigation.txt'
    improvement={k:1-best['summary'][k]['compiled_cycles']/replay['summary'][k]['compiled_cycles']for k in ['pad','string']}
    proof=dict(status='terminal_live_context_semantics_and_optimization_cost_review_published',recorded_at=now.isoformat(),directory=str(out),report=str(report),
               captured_pairs_per_lane=42,total_native_entry_replay_cases=84,full_return_CPU_public_RAM_and_ordered_accesses_match=True,
               actual_live_CPU_and_written_bytes_match=True,observer_repeat_video_position_differences=0,
               baseline_costs=replay['summary'],interrupt_evidence=dict(first_video_difference_frame=210,candidate_pad_ordinal=11,handler_PC=0xe7d4,vector=64,vector_RAM_offset=0x100,core_ack_level=2,
                    interpretation='Observed excursion matches the captured game IRQ vector and retained-core level2 acknowledgement. Supports timing mechanism; does not identify all frame differences or physical timing.'),
               variants=variants,best_sampled_candidate='O2-lean',best_full_helper_and_caller_checks=helper_checks,sampled_cycle_reduction=improvement,
               optimized_disc_built=False,optimized_other_component_inventory_revalidated=False,optimized_fresh_game_run=False,
               original_C_sources_changed=False,accepted_C_authorship='Padding coordinator reference; string deterministic typed-IR lifter. New lean shim coordinator-authored.',
               local_LLM_attempts=authors,native_UI_attempt='CUA getApp timed out120.6077seconds; no new nativeChat action/generation verified. Actual Author/Repair use localSDK.',
               wrapper_failure_logs=failure_history,new_training=False,default_promoted=False,whole_game_complete=False,goal_complete=False,
               dependencies_sha256=deps,source_snapshots=snapshots)
    save(out/'publication.json',proof);save(ROOT/'verification/native-format-cost-publication-current.json',proof)
    report.write_text('\n'.join([
      'The sampled frame differences now have stronger timing evidence, with sampled helper semantics preserved.',
      'Two fresh2600frame runs captured42selected helper entries/returns per lane. Each lane exactly repeated its earlier video/position/scene sequence despite the read-only observer snapshots.',
      'All84real-entry fixtures pass original/compiled full returnCPU,2MBpublicRAM and separate ordered-access comparisons. Only actual observed private compiler scratch and six entry-overlay bytes are excluded. Every sampled actual live returnCPU and helper-written final byte also matches.',
      'Selected calls include10candidate/1control calls with supervisor execution. Candidate padding call11 intersects the IRQ handler in frame210, the first video difference. Captured RAM vector64at100points toE7D4; core level2ack returns64. This supports a timing explanation; all frame causes remain unproven.',
      '', 'Native test-CPU cost on sampled inputs: padding9976original versus70976compiled cycles(7.11x); string12636versus663520(52.51x). These are retained testCPU instruction-cycle measurements, not physical-console clocks or whole-gameFPS.',
      'Three separate compiler/ABI candidates fit the unchanged9216byte reserve. All pass84counterfactual real-entry fixtures. O2-lean is best on these sampled calls:9042linked bytes; padding62160cycles andstring199680cycles,12.4%/69.9%belowbasecompiled cost. Many sampled inputs repeat; no general performance benchmark claim.',
      'O2-lean also passes1668padding+1945string full native/ordered fixture cases,16changing-read cases per helper,and1654complete formatter-caller cases with5161helper returns. Underlying C bodies unchanged; leanABIshim is coordinator-authored.',
      'The optimized payload has no disc/fresh-game run yet. Other exact-build component/readiness/lifecycle and installation checks remain before integration. Current disc/default preview unchanged.',
      '', 'Local C Author:8019input/601outputtokens,35.71seconds; rejected firstCPUcase forA0/A2. Guided same-weight Repair Author:9452input/586outputtokens,27.69seconds; fixedA2butstillwrongA0. Both raw candidates retained/rejected; no passing C target supplied, no new training or promotion.',
      'Native LMStudio UI connection timed out120.61seconds this continuation. These two new roles ran viaactual localSDK, not verifiednativeChat; earlier namedChat demos remain available. Exact prompts/responses are in the author records below.',
      '', 'Author prompts: '+authors['author']['exact_prompts'],'Repair prompts: '+authors['repair']['exact_prompts'],
      'Complete bound proof: '+str(out/'publication.json'),
      'Full goal remains open: optimized integration, broader game/source/audio/console coverage, reliable representative local authorship/training, advertising research/teaching quality, and future256GBhardware validation.'])+'\n')
    goal_path=ROOT/'verification/goal-continuation-current.json';goal=read(goal_path);save(out/'prior-goal-state.json',goal)
    goal.update(status='active_live_formatter_semantics_and_costs_verified_optimized_helpers_pass_full_goal_incomplete',recorded_at=now.isoformat(),
                previous_turn_classification='progress: exact resource/readiness/lifecycle inventory and119live string returns published.',this_turn_classification='progress',
                latest_format_cost_proof=str(ROOT/'verification/native-format-cost-publication-current.json'),latest_finite_jobs_running=[],
                latest_finite_job_status='terminal_live_context_semantics_and_optimization_cost_review_published',
                native_Chat_this_continuation=False,native_UI_latest_observation='Timedout120.6077s; no lock-state conclusion. Previous verified nativeChat demonstrations remain historical evidence.',
                next_actions=['Revalidate exact O2-lean installation and other linked component inventory; build a separate optimized experimental disc and fresh ordinary-input comparisons.',
                  'Continue broader game/source/audio and same-console rebuild work; report timing cadence separately from functional/source completion.',
                  'Improve representative local authorship/training beyond the retained rejected Author/Repair examples; keep deterministic tests authoritative.',
                  'Continue broader advertising research/teaching reliability and futurehardware validation.'],goal_complete=False)
    save(goal_path,goal)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as log:
        log.write(json.dumps(dict(time=now.isoformat(),event='live_formatter_costs_and_optimized_helper_gates_published',
             coordinator='Codex',local_roles=['Author rejected','sameweight RepairAuthor rejected'],actual_local_model='advertising-scholar(27B6bit)',
             exact_prompts=[authors[k]['exact_prompts']for k in ['author','repair']],native_Chat_this_turn=False,training_updates=0,
             source_C_changed=False,default_promoted=False,proof=str(out/'publication.json'),whole_game_complete=False))+'\n')
    for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
        path=ROOT/name;shutil.copyfile(path,out/('prior-'+name));path.write_text('CURRENT FORMATTER COST / LOCAL AUTHOR CHECK — '+now.isoformat()+'\n\n84captured-entry replays preserve sampled semantics and live return effects; base helpers cost7.11x/52.51xoriginal native test cycles. SeparateO2-lean candidate reduces sampled pad/string cost12.4%/69.9%andpasses full helper/caller gates, but still needs other exact-build checks and a fresh disc run. LocalAuthor andoneguidedRepair rejected. No newtraining/default promotion; nativeUI attempt timed out,SDKroles saved.\nReport: '+str(report)+'\n\nEARLIER RECORDS\n\n'+path.read_text())
    print(json.dumps(dict(status=proof['status'],directory=str(out),report=str(report),bound_files=len(deps)),indent=2))
if __name__=='__main__':main()
