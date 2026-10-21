"""Bind exact-build resource tests and repaired fresh-game helper observations."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-format-resource-live-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    deps={};copies={}
    def bind(p,snapshot=False):
        p=Path(p).resolve();deps[str(p)]=sha(p)
        if snapshot:
            target=out/'snapshots'/(hashlib.sha256(str(p).encode()).hexdigest()[:16]+'-'+p.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target);assert sha(target)==deps[str(p)];copies[str(p)]=str(target)
    previous_path=ROOT/'verification/native-format-component-chat-review-current.json';previous=read(previous_path)
    assert all(sha(p)==h for p,h in previous['dependencies_sha256'].items())
    bind(previous_path,True)
    resource_path=ROOT/'verification/native-format-resource-gates-current.json';resource=read(resource_path)
    assert resource['status']=='terminal_exact_format_resource_and_lifecycle_gates_pass'
    expected='6d4c4c6cd953df0a7000309acd27fd69d4a426783d79133cde2150a2a1cec972'
    assert resource['binary_sha256']==expected and resource['binary_bytes']==8742
    assert resource['heap_start']==0x1611c0 and resource['reservation_bytes']==9216
    bind(resource_path,True);jobs={**resource['prior_completed_gates_reused'],**resource['jobs']};gates={}
    expected_counts={'acquire':(3072,3072),'allocator':(384,384),'initialize':(192,192),'loader':(1100,114)}
    for key,job in jobs.items():
        path=Path(job['proof']);assert sha(path)==job['proof_sha256'];proof=read(path)
        assert proof['status'].startswith('terminal_')and'pass'in proof['status'];bind(path,True)
        for table in ['source_sha256','artifacts_sha256','execution_dependencies_sha256','component_proofs']:
            values=proof.get(table,{})
            if isinstance(values,dict):
                for p,h in values.items():assert sha(p)==h,p;bind(p)
        if proof.get('compiled_binary_sha256'):assert proof['compiled_binary_sha256']==expected
        if key.endswith('-preflight'):continue
        if key in expected_counts:assert (proof['native_cases'],proof['trace_cases'])==expected_counts[key]
        if key=='loader':assert proof['reference_instruction_coverage']==[71,71]
        if key=='lifecycle':assert proof['variants']==8 and proof['native_call_pairs']==240 and proof['payload_byte_comparisons']==84121
        if key=='heap-blitter-witness':assert proof['payload_bytes_checked']==232
        if 'readiness'in key:assert proof['cases']==16 and proof['real_readiness_component_pass']
        gates[key]={k:v for k,v in proof.items()if k in ['status','scope','native_cases','trace_cases','cases','native_call_pairs','variants','payload_byte_comparisons','payload_bytes_checked','verified_payload_bytes','source_accepted','real_readiness_component_pass','compiled_binary_sha256']}
        for p in Path(proof['directory']).rglob('*'):
            if p.is_file():bind(p)
    assert len(gates)==10
    # Keep both initial failures and their exact sources as diagnostic history.
    for p in [Path(resource['prior_driver_failure']),Path(resource['prior_preparation'])]:bind(p,True)
    prior_dir=Path(resource['prior_driver_failure']).parent
    for name in ['initial-orchestration-failure.json','driver-as-run.py','loader-readiness-driver-before-kernel-fix.py']:
        bind(prior_dir/name,True)
    initial=read(resource['prior_driver_failure'])
    for key in ['loader-readiness-preflight','loader-readiness-nested-preflight']:
        log=Path(initial['jobs'][key]['log']);bind(log,True)
        child=Path(log.read_text().splitlines()[0]);bind(child/'protocol.json',True)

    fresh_path=ROOT/'verification/native-format-selector-deck-pair-current.json';fresh=read(fresh_path)
    assert fresh['status']=='terminal_fresh_format_selector_deck_pair_classified'
    assert fresh['exit_codes']=={'candidate':0,'control':0} and fresh['both_helpers_exercised']
    assert fresh['host_guest_RAM_writes']==fresh['checkpoint_restores']==0
    bind(fresh_path,True);repair=fresh['shared_selector_repairs']
    assert repair['declared_shared_repair_bytes']==38 and repair['actual_candidate_changed_CDI_bytes']==37
    assert repair['pair_changed_CDI_bytes']==12
    for key,hashkey in [('parent_disc','parent_disc_sha256'),('candidate','candidate_sha256'),('control','control_sha256'),('source_overlay','source_overlay_sha256')]:
        assert sha(repair[key])==repair[hashkey];bind(repair[key],key=='source_overlay')
    for p,h in fresh['source_sha256'].items():assert sha(p)==h,p;bind(p,Path(p).suffix in ['.py','.c','.json'])
    lane_summary={}
    expected_calls={'candidate':[5427,119],'control':[6552,144]}
    for lane in ['candidate','control']:
        directory=Path(fresh['directory'])/lane;report=read(directory/'report.json');obs=read(directory/'gameplay-observation.json')
        assert sha(directory/'report.json')==fresh['report_sha256'][lane]
        assert obs==fresh['observations'][lane]
        assert obs['format_entries']==obs['format_returns']==expected_calls[lane]
        assert obs['format_pending_at_finish']==obs['format_tracking_errors']==0
        assert obs['format_stack_outside']==[0,0]and obs['format_user_observations'][1]>0
        assert report['executed_frames']==len(report['frames'])==2600
        assert report['captured_state_input'] is False and report['host_CPU_or_GPU_register_seed'] is False
        assert report['normal_input_only'] is True
        frames=report['frames'];debug=[x for x in frames if x['debug_overlay_word']==1]
        assert len(debug)==200 and debug[0]['frame']==1800 and debug[-1]['frame']==1999
        assert all(x['cumulative_nonzero_audio_samples']==0 for x in frames)
        assert frames[-1]['editor_state_word']==2
        assert obs['compiled_format_calls']==(expected_calls[lane]if lane=='candidate'else[0,0])
        memory=(directory/'RAM-final.bin').read_bytes();assert sha(directory/'RAM-final.bin')==report['final_RAM_sha256']
        build=read(fresh['build_proof']);resident=Path(build['component']).read_bytes()
        assert memory[build['resident_address']:build['heap_start']]==resident
        assert int.from_bytes(memory[0x112d60:0x112d64],'big')==0x1611c0
        lane_summary[lane]=dict(format_entries=obs['format_entries'],format_returns=obs['format_returns'],
             compiled_format_calls=obs['compiled_format_calls'],old_format_body_steps=obs['old_format_body_steps'],
             observed_stack_violations=obs['format_stack_outside'],minimum_observed_headroom_bytes=obs['format_min_headroom'],
             debug_active_frames=[1800,1999],debug_active_frame_count=200,final_editor_state=2,
             final_position=[frames[-1]['raw_player_X'],frames[-1]['raw_player_Z']],final_scene=frames[-1]['scene_word'],
             payload_preserved=True,nonzero_audio_samples=0)
        for p in directory.rglob('*'):
            if p.is_file():bind(p)
    assert fresh['PCM_equal'] and not fresh['timing_vs_algorithm_cause_resolved']
    original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    assert sha(original)=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f';bind(original)
    for name in ['prepare_native_format_resource_gates.py','run_native_format_resource_gates.py','finish_native_format_loader_readiness.py','prepare_native_format_selector_deck_pair.py','run_biwn_native_format_selector_deck_pair.py',Path(__file__).name]:bind(ROOT/'scripts'/name,True)
    prep_path=ROOT/'verification/native-format-resource-preparation-current.json';prep=read(prep_path);bind(prep_path,True)
    for row in prep['drivers']:
        assert sha(row['parent'])==row['parent_sha256']and sha(row['derived'])==row['derived_sha256'];bind(row['parent'],True);bind(row['derived'],True)
    report=ROOT/'reports/native-format-resource-and-live-string.txt'
    publication=dict(status='terminal_exact_format_resource_checks_and_repaired_live_string_published',recorded_at=now.isoformat(),directory=str(out),report=str(report),
         linked_binary_sha256=expected,linked_bytes=8742,reservation_bytes=9216,heap_start=0x1611c0,
         prior_eight_component_matrices=previous['gates'],resource_gates=gates,
         earlier_component_publication_dependencies_unchanged=len(previous['dependencies_sha256']),
         live_fresh_frames_per_lane=2600,live_helper_coverage=lane_summary,shared_repairs=repair,
         live_string_exercised=True,scoped_native28_matrix_readiness_lifecycle_inventory_revalidated=True,
         frame_comparisons=fresh['comparisons'],frame_equivalent=False,
         timing_vs_algorithm_cause_resolved=False,PCM_equal=True,audible_output_verified=False,
         original_disc_preserved=True,default_promoted=False,physical_console_verified=False,
         same_console_full_source_rebuild_ready=False,new_training=False,whole_game_complete=False,goal_complete=False,
         failure_history='Receipt filename ingestion corrected with completed immutable receipts reused; kernel-aware parent restored missing scan ownership range without weakening stack assertions. Production payload/source unchanged.',
         next_actions=['Analyze timing/IRQ versus semantics in observed formatter frame differences','Optimize new source helpers if timing cost is causal, preserving full CPU/public memory contracts','Continue broader gameplay/audio and whole-game source/console reconstruction','Improve representative local C authorship/training and advertising workflow reliability'],
         dependencies_sha256=deps,source_snapshots=copies)
    save(out/'publication.json',publication);save(ROOT/'verification/native-format-resource-live-publication-current.json',publication)
    lines=['Exact8742byte format payload now passes the listed component/resource/readiness/lifecycle inventory.','',
      'Earlier eight matrices: controller,RNG,tasks,scheduler,heap,copy,free,release.',
      'New controlled acquire3072native+3072ordered; actual-allocator acquire384+384; initializer192+192; repaired loader1100native+114ordered with71/71instruction coverage.',
      'Coupled heap lifecycle:8sequences,240paired native calls,84,121known payload-byte comparisons. Separate232byte compaction/blitter witness.',
      'Four two-client readiness profiles:16cases each, covering standalone/relocated acquire and standalone/nested loader. Explicit BIOS adapters, startup captures, provider/exclusion limits remain. These are component fixtures, not64fresh full-game runs.',
      '', 'Live string path: a separate fresh HLEboot pair now enters the Deck/debug path after identical existing selector/count repairs at464A6/10AC2. Declared38patch bytes,37actual candidate CDI bytes changed. Candidate/control still differ only12formatter-redirect bytes.',
      'Candidate:5427padding+119string calls; all observed returning. Control:6552padding+144string calls,all returning. No observed user-task stack violations or pending/tracking errors. Minimum observed candidate stack headroom602padding/512string bytes; control694/688bytes.',
      'Debug word active on frames1800..1999,editor state2afterexit. Final X9535/Z40399/scene0/floor0 in both lanes. Resident payload and new heap boundary preserved.',
      'Video differs453frames; X differs42/Z76frames. Different helper call counts/return rates show execution cadence differs; this does not by itself prove the cause or full semantic equivalence. PCM equal butsilent. No default promotion.',
      '', 'Test-harness corrections: wrapper initially looked for the wrong acquire receipt filename; completed child evidence was reused, not rerun. Initial loader adaptation used the general gate and omitted scan-kernel ownership; existing kernel-aware gate restored exact ELF/object-derived range. Original failures retained; stack comparisons/assertions preserved. No production-source/payload change for these fixes.',
      '', 'This is meaningful source-built integration progress, not a standalone/full-game decompilation or physical Jaguar rebuild. Full goal including reliable local training, broader advertising quality and future hardware remains active.',
      '', 'Full bound publication: '+str(out/'publication.json')]
    report.write_text('\n'.join(lines)+'\n')
    status_path=ROOT/'verification/goal-continuation-current.json';status=read(status_path);save(out/'prior-goal-state.json',status)
    status.update(status='active_exact_format_resource_inventory_and_repaired_live_string_verified_full_goal_incomplete',recorded_at=now.isoformat(),
                  previous_turn_classification='progress: eight exact linked matrices, actual native BIWN/advertising Chat tests and findable saved workflows published.',
                  this_turn_classification='progress',latest_format_resource_live_proof=str(ROOT/'verification/native-format-resource-live-publication-current.json'),
                  latest_finite_job_status='terminal_exact_format_resource_and_lifecycle_gates_pass',latest_finite_jobs_running=[],
                  string_live_path_verified_with_declared_selector_repairs=True,
                  next_actions=publication['next_actions'],goal_complete=False)
    save(status_path,status)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as log:
        log.write(json.dumps(dict(time=now.isoformat(),event='exact_format_resource_inventory_and_repaired_live_string_published',
                  coordinator='Codex',LLM_calls_this_continuation=0,verifiers='retained native CPU and separate ordered bus; read-only game observer',
                  production_C_origin='inherited accepted sources; string deterministic typed-IR lifter',
                  proof=str(out/'publication.json'),live_compiled_calls=[5427,119],training_updates=0,default_promoted=False,whole_game_complete=False))+'\n')
    for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
        p=ROOT/name;shutil.copyfile(p,out/('prior-'+name))
        heading=('CURRENT RESOURCE / LIVE STRING CHECK — '+now.isoformat()+'\n\n'
                 'Exact format build: listed component/resource/readiness/lifecycle inventory passed. Separate repaired fresh Deck run calls compiled padding5427times/string119times, all observed returning with no stack violation. Same38byte selector repair set in both lanes. Frame differences remain unresolved; defaults/weights unchanged.\n'
                 'Report: '+str(report)+'\n'
                 'This continuation used deterministic tests/observer only; no additional local-model prompts or new training. Previous native Chat demonstrations remain saved and available.\n\nEARLIER RECORDS\n\n')
        p.write_text(heading+p.read_text())
    print(json.dumps(dict(status=publication['status'],report=str(report),directory=str(out),bound_files=len(deps)),indent=2))
if __name__=='__main__':main()
