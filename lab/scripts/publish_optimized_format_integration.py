"""Publish exact optimized build/install/runtime evidence with timing limits."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-optimized-format-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);dependencies={};snapshots={}
    def bind(p,snapshot=False):
        p=Path(p).resolve();dependencies[str(p)]=sha(p)
        if snapshot:
            target=out/'snapshots'/(hashlib.sha256(str(p).encode()).hexdigest()[:16]+'-'+p.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target);snapshots[str(p)]=str(target)
    def tree(directory):
        for p in Path(directory).rglob('*'):
            if p.is_file():bind(p)
    prior_path=ROOT/'verification/native-format-cost-publication-current.json';prior=read(prior_path)
    assert all(sha(p)==h for p,h in prior['dependencies_sha256'].items());bind(prior_path,True)
    bp=ROOT/'verification/native-optimized-format-bundle-current.json';bundle=read(bp);bind(bp,True)
    assert sha(bundle['binary'])==bundle['binary_sha256']=='533c10742617e8596c0ce2dc32e7676d137a9fbbc463b29bb86e0db41fd0ca19'
    assert bundle['binary_bytes']==9042 and bundle['reserved_bytes']==9216 and bundle['heap_start']==0x1611c0
    for p,h in bundle['source_sha256'].items():assert sha(p)==h;bind(p)
    build_path=ROOT/'verification/native-optimized-format-disc-build-current.json';build=read(build_path);bind(build_path,True)
    assert sha(build['derived_disc'])==build['derived_disc_sha256']and build['linked_component_bytes']==9042
    assert build['changed_CDI_bytes']==7952;tree(build['directory'])
    ip=ROOT/'verification/native-optimized-format-integration-current.json';integration=read(ip);bind(ip,True)
    assert integration['status']=='terminal_optimized_format_install_and_component_resource_inventory_pass'
    assert len(integration['full_gates'])==19 and integration['binary_sha256']==bundle['binary_sha256']
    for key,job in integration['jobs'].items():
        p=Path(job['proof']);assert job['status']=='terminal_pass'and sha(p)==job['proof_sha256'];bind(p,True)
        proof=read(p)
        if proof.get('compiled_binary_sha256'):assert proof['compiled_binary_sha256']==bundle['binary_sha256']
        for table in ['source_sha256','artifacts_sha256','execution_dependencies_sha256','component_proofs']:
            values=proof.get(table,{})
            if isinstance(values,dict):
                for path,digest in values.items():assert sha(path)==digest;bind(path)
        tree(proof['directory'])
    prep=read(integration['preparation']);assert sha(integration['preparation'])==integration['preparation_sha256'];bind(integration['preparation'],True)
    for d in prep['drivers']:
        assert sha(d['parent'])==d['parent_sha256']and sha(d['derived'])==d['derived_sha256'];bind(d['parent'],True);bind(d['derived'],True)
    directory=Path(integration['directory'])
    for name in ['initial-path-failure.json','preparation-as-run.json','driver-as-run.py','rng-preflight.log']:bind(directory/name,True)
    helper_gates={}
    for kind,name in [('pad','native-optimized-format-pad-current.json'),('string','native-optimized-format-string-current.json'),('callers','native-optimized-format-callers-current.json')]:
        p=ROOT/'verification'/name;g=read(p);assert g['binary_sha256']==bundle['binary_sha256']and g['source_accepted'];bind(p,True)
        helper_gates[kind]={k:v for k,v in g.items()if k in ['status','native_cases','ordered_cases','changing_read_cases','helper_returns','scope']}
    pair_path=ROOT/'verification/native-optimized-format-selector-deck-pair-current.json';pair=read(pair_path);bind(pair_path,True)
    assert pair['status']=='terminal_fresh_format_selector_deck_pair_classified'and pair['exit_codes']=={'candidate':0,'control':0}
    assert pair['both_helpers_exercised']and pair['final_resident_payload_preserved']
    a=pair['observations']['candidate'];b=pair['observations']['control']
    assert a['compiled_format_calls']==a['format_returns']==[5697,125]and a['old_format_body_steps']==[0,0]
    assert b['compiled_format_calls']==[0,0]and b['format_returns']==[6552,144]
    for obs in [a,b]:assert obs['format_stack_outside']==[0,0]and obs['format_tracking_errors']==obs['format_pending_at_finish']==0
    original_pair_path=ROOT/'verification/native-format-selector-deck-pair-current.json';original_pair=read(original_pair_path);bind(original_pair_path,True)
    cross={}
    for lane in ['candidate','control']:
        d=Path(pair['directory'])/lane;p=d/'report.json';assert sha(p)==pair['report_sha256'][lane];report=read(p)
        previous=read(Path(original_pair['directory'])/lane/'report.json')
        assert report['executed_frames']==len(report['frames'])==len(previous['frames'])==2600
        fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256']
        cross[lane]={k:sum(x[k]!=y[k]for x,y in zip(report['frames'],previous['frames']))for k in fields}
        tree(d)
    assert all(v==0 for v in cross['control'].values())
    for p,h in pair['source_sha256'].items():assert sha(p)==h;bind(p)
    repair=pair['shared_selector_repairs'];assert repair['declared_shared_repair_bytes']==38 and repair['actual_candidate_changed_CDI_bytes']==37 and repair['pair_changed_CDI_bytes']==12
    for key,hkey in [('candidate','candidate_sha256'),('control','control_sha256')]:assert sha(repair[key])==repair[hkey];bind(repair[key])
    long_path=ROOT/'verification/native-format-optimized-long-route-current.json';long=read(long_path);bind(long_path,True)
    assert long['status']=='terminal_fresh_base_optimized_adaptive_routes_classified'and long['exit_codes']=={'base':0,'optimized':0}
    for p,h in long['source_sha256'].items():assert sha(p)==h;bind(p)
    long_summary={}
    for lane,result in long['results'].items():
        assert result['merchant_reached']and result['completed_outdoor_hold']and result['return_floor_values']==[0,1]
        assert result['nonzero_audio_samples']>0
        assert result['observation']['native_C_acquire_calls']==result['observation']['acquire_entries']==11
        assert result['observation']['native_C_loader_calls']==result['observation']['loader_entries']==43
        assert result['observation']['acquire_task_stack_outside']==result['observation']['loader_task_stack_outside']==0
        d=Path(long['directory'])/lane;assert sha(d/'report.json')==result['report_sha256'];tree(d)
        long_summary[lane]={k:v for k,v in result.items()if k not in ['observation','scope']}
    assert long_summary['base']['executed_frames']==24975 and long_summary['optimized']['executed_frames']==29791
    long_delay=29791-24975
    for name in ['prepare_optimized_format_integration.py','check_optimized_format_integration.py','run_biwn_native_optimized_format_selector_deck_pair.py','run_format_optimized_long_routes.py',Path(__file__).name]:bind(ROOT/'scripts'/name,True)
    original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert sha(original)=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f';bind(original)
    report=ROOT/'reports/native-optimized-format-integration.txt'
    publication=dict(status='terminal_optimized_format_install_inventory_and_fresh_routes_published',recorded_at=now.isoformat(),directory=str(out),report=str(report),
        binary_sha256=bundle['binary_sha256'],linked_bytes=9042,reserved_bytes=9216,heap_start=0x1611c0,derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],
        declared_resident_redirects=sum(1 for p in read(build['patch_manifest'])['patches']if(bytes.fromhex(p['replacement'])[:2]==b'\x4e\xf9'and build['resident_address']<=int.from_bytes(bytes.fromhex(p['replacement'])[2:6],'big')<build['resident_address']+9042)),
        redirect_count_scope='Stage JMP redirects into resident code; not the number of all recovered functions or a decompilation percentage.',
        scoped_install_component_resource_full_gates=integration['full_gates'],helper_gates=helper_gates,
        fresh_repaired_pair_frames=2600,optimized_helper_calls=[5697,125],original_helper_control_calls=[6552,144],
        helper_stack_violations=0,helper_pending_at_finish=0,optimized_minimum_observed_helper_stack_headroom=[602,580],
        fixed_input_frame_comparisons=pair['comparisons'],same_lane_changes_vs_prior_build=cross,
        long_adaptive_routes=long_summary,long_route_delay_frames=long_delay,
        whole_game_speedup_demonstrated=False,frame_equivalent=False,
        performance_interpretation='Sampled isolated string test-cycle cost drops69.9percent; short Deck string return count rises119to125. Longer adaptive route requires4816more frames. This is not a whole-game speedup or frame-equivalence result.',
        captured_audio_nonzero=True,physical_audio_or_quality_verified=False,physical_console_verified=False,
        new_training=False,LLM_calls_this_continuation=0,default_promoted=False,whole_game_complete=False,goal_complete=False,
        dependencies_sha256=dependencies,source_snapshots=snapshots)
    save(out/'publication.json',publication);save(ROOT/'verification/native-optimized-format-publication-current.json',publication)
    report.write_text('\n'.join([
      'The separate O2-lean experimental disc now passes exact-build installation/component/resource and fresh-route checks.',
      '9042linked bytes;9216reserved; heap starts1611C0;7952declared rawCDI byte changes from the untouched original. Patches retain original tracks/metadata outside declared stage changes. This remains a mixed original/recompiled build.',
      'Nineteen full install/component/resource gates pass, including96startup cases,5151installed keypad ABI cases, full controller/RNG/task/scheduler/heap/copy/free/release/acquire/loader checks,240coupled lifecycle calls and four16case readiness profiles.',
      'Previously completed full helper/caller receipts bind the exact same binary hash:1668padding,1945string,16changing-read cases perhelper,1654formatter/caller cases and5161helper returns.',
      '', 'Fresh2600frame repaired Deck pair: optimized5697padding/125string returns, no observed helper stack violations or pending/tracking errors. Control6552padding/144string returns. Same38declared selector-repair bytes in both discs; pair differs only12format redirects.',
      'The optimized original-helper control repeats prior video/position/mode/floor/scene exactly. Candidate still differs from control in642video frames,45Xframes and81Zframes. Earlier base candidate differed453video/42X/76Zframes. Changed cadence is not stronger frame equivalence.',
      '', 'Both fresh adaptive hotel/merchant/outdoor routes complete: base24975frames,optimized29791frames,merchant reached,descent tofloor0and120frame outdoorhold. Optimized takes4816more frames. This is not a whole-game speedup; navigation/game cadence remains timing-sensitive.',
      'Each long run exercises11compiled acquisitions and43compiled loader calls with zero observed loader/acquire stack violations. Captured nonzero audio samples:base1609486,optimized7324788. Different durations/input histories prevent audio equality claims; physical audibility/quality remain unverified. The older native28adaptive reference also had nonzero audio, so this is not a first-ever audio claim.',
      '', 'No new local-model calls or training in this continuation. Accepted string C remains deterministic typed-IR output; padding and leanABIshim are coordinator-authored. Last Author/Repair model candidates remain rejected. Current preview/default models unchanged.',
      'One RNG wrapper path failed before CPU execution; correct artifact name restored and completed immutable test receipts reused. Failure/history retained without weakening any CPU comparison.',
      '', 'Raw optimized experimental disc: '+build['derived_disc'],
      'Full bound publication: '+str(out/'publication.json'),
      'Still open: broader source/game/audio/console coverage, timing diagnosis, representative local training/reliable authorship, latest local-status retrieval, advertising quality and futurehardware validation.'])+'\n')
    goal_path=ROOT/'verification/goal-continuation-current.json';goal=read(goal_path);save(out/'prior-goal-state.json',goal)
    goal.update(status='active_optimized_install_inventory_and_fresh_long_routes_verified_full_goal_incomplete',recorded_at=now.isoformat(),
        previous_turn_classification='progress:84real-context semantic/cost checks, tested optimization, rejected localAuthor/Repair evidence published.',this_turn_classification='progress',
        latest_optimized_integration_proof=str(ROOT/'verification/native-optimized-format-publication-current.json'),latest_finite_jobs_running=[],latest_finite_job_status=publication['status'],
        next_actions=['Diagnose optimized route exit delay using actual navigation/scene/actor evidence; do not infer whole-game speedup from helper microbenchmarks.',
          'Refresh local status retrieval with bound current evidence and verify the actual configured MCP/nativeChat path.',
          'Continue broader source/game/audio and full same-console rebuild coverage.',
          'Improve representative local authorship/training and advertising research/teaching reliability; validate future hardware when available.'],goal_complete=False)
    save(goal_path,goal)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as log:log.write(json.dumps(dict(time=now.isoformat(),event='optimized_format_exact_install_and_fresh_routes_published',coordinator='Codex',LLM_calls=0,training_updates=0,
       workflow='deterministic native CPU/bus/component tests and adaptive ordinary-button controller, not LLM agents',proof=str(out/'publication.json'),default_promoted=False,whole_game_complete=False))+'\n')
    for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
        p=ROOT/name;shutil.copyfile(p,out/('prior-'+name));p.write_text('CURRENT OPTIMIZED DISC / ROUTE CHECK — '+now.isoformat()+'\n\nThe separate9042byte O2-lean disc passes19install/component/resource gates and both fresh routes. Short Deck string calls125vs119base; long adaptive route29791vs24975frames,so no whole-game speedup. Nonzero captured audio in both long runs; no physicalquality/console proof. Defaults/weights unchanged; no new model calls/training this continuation.\nReport: '+str(report)+'\n\nEARLIER RECORDS\n\n'+p.read_text())
    watch=ROOT/'WATCH LOCAL AGENTS.txt';shutil.copyfile(watch,out/'prior-WATCH LOCAL AGENTS.txt');watch.write_text('LATEST EXPERIMENTAL DISC CHECK\n'+str(report)+'\nThis experimental result is not yet included in every legacy local status lookup. The named nativeChat demonstrations below remain scoped to their saved evidence.\n\n'+watch.read_text())
    print(json.dumps(dict(status=publication['status'],report=str(report),directory=str(out),bound_files=len(dependencies)),indent=2))
if __name__=='__main__':main()
