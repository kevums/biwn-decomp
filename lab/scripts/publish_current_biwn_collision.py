"""Publish the reviewed 28380-byte collision experiment with explicit limits."""
import copy
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def read(p):
    return json.loads(Path(p).read_text())


def main():
    v = ROOT / 'verification'
    pointer = v / 'current-biwn-latest-publication-current.json'
    previous = read(pointer)
    assert previous['facts']['experimental_build']['resident_bytes'] == 26220
    review = read(v / 'actor-collision-integration-reviewed-current.json')
    assert review['status'] == 'terminal_native_actor_collision_fresh_routes_reviewed' and review['live_monitor_pass']
    build = read(v / 'native-actor-collision-disc-build-current.json')
    candidate = read(v / 'native-actor-collision-candidate-current.json')
    control = read(v / 'native-actor-collision-control-current.json')
    co, ctrl = candidate['observations'], control['observations']
    migration = read(v / 'relocated-runtime-boundaries-current.json')
    models = read(v / 'relocated-model-copy-current.json')
    assert models['status'] == 'terminal_isolated_model_package_copy_integrity_pass'
    assert migration['status'] == 'terminal_relocated_existing_MCP_boundaries_pass'
    out = v / 'current-biwn-latest-publication' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    for name, value in [('previous-publication.json', previous), ('collision-review.json', review), ('collision-build.json', build), ('candidate.json', candidate), ('control.json', control), ('migration-boundaries.json', migration), ('model-copy.json', models)]:
        save(out / name, value)
    facts = copy.deepcopy(previous['facts'])
    facts['previous_movement_component_verification'] = facts['component_verification']
    comparison = review['comparison']
    facts.update(recorded_at=datetime.now(timezone.utc).isoformat(),
        checked_current_summary='The latest experimental disc adds rebuilt outdoor and indoor collision C to native movement and actor/sprite creation: 28,380 resident bytes. Both collision roots pass5,120 full-interface cases covering all109original instruction sites. Movement+collision composition passes2,560cases;5,120original/C context executions preserve task-header canaries and reach894bytes private depth.96full-payload startup cases pass. Fresh candidate29,797frames/control24,996both returned outdoors. Candidate executes3,868outdoor collision calls in C,zero original collision-body steps;13,872native movement calls/31,612real helpers with zero reported movement ABI/context/task-boundary errors. Indoor collision0livecalls;broader outcomes and arbitrary concurrency remain unproved. Video/audio/state differ and timing equivalence remains unresolved. New collision/movement/creation source and integration are coordinator work; inherited accepted local helpers retain attribution. No new weights. Five older processor tests remain terminal only for their own discs. Preview unchanged/nativeChatunverified. Full readable same-console game, reliable local/Advertising workflows and full migration/future256GBconfiguration remain unfinished.',
        experimental_build={**facts['experimental_build'], 'name':'rebuilt collision, movement and actor/sprite creation', 'resident_bytes':28380, 'reservation_free_bytes':164, 'derived_disc':build['derived_disc'], 'derived_disc_sha256':build['derived_disc_sha256']},
        component_verification=dict(original_entries=['0x13b5a','0x13bb0'],native_bytes=2160,stable_cases=5120,per_root_cases=2560,original_instruction_coverage=[109,109],actual_geometry_helpers=['0x1039c','0x102c4','0x1028e','0x10652'],prescribed_direct_collision_helpers=0,startup_cases=96,composition_cases=2560,composition_context_executions=5120,composition_private_stack_bytes=894,composition_min_task_headroom=24,source=build['source'],source_defect_controls=5,smaller_reserve_composition_negative=True,scope='Full returnedCPU/SR/banks/physicalhelperCPU/SP/SR/arguments/public2MBRAM/orderedpublicaccess comparison. Actual geometry executes both lanes; onlyE220GPU effects prescribed in combined movement fixtures. Original/C context/task-header canaries checked; arbitrary concurrent/fault/device/timing behavior unproved.'),
        live_path_coverage=f"Collision candidate outdoor{co['ac_entries'][0]}/indoor{co['ac_entries'][1]}completed calls,all reached bodies native; control outdoor{ctrl['ac_entries'][0]}/indoor{ctrl['ac_entries'][1]}original calls. Native movement{co['am_entries']}returns/{co['am_helper_entries']}actual helpers,including{co['am_outdoor_calls']}outdoor and{co['am_indoor_calls']}indoor collision calls. Indoor live collision and per-outcome/rollback coverage remain unproved. Dispatcher13returns(12actor/1sprite),initializer12/16helpers,spritecreator1/3helpers. These are routing/completion counts,not selector successes. Actorselector14successes/0failures;spriteselector0successes/1skippedfailure.",
        gameplay_comparison=dict(candidate_frames=review['candidate_frames'], control_frames=review['control_frames'],compared_prefix_frames=comparison['aligned_frames'],collision_outdoor_completed_returns=co['ac_returns'][0],collision_indoor_completed_returns=co['ac_returns'][1],collision_native_instruction_steps=co['ac_native_steps'],collision_original_body_steps=co['ac_original_steps'],control_collision_outdoor_returns=ctrl['ac_returns'][0],control_collision_original_steps=ctrl['ac_original_steps'],movement_completed_returns=co['am_returns'],actual_movement_helper_calls=co['am_helper_entries'],movement_helper_counts=dict(direction=co['am_direction_calls'],GPU_submission=co['am_submit_calls'],outdoor_collision=co['am_outdoor_calls'],indoor_collision=co['am_indoor_calls']),control_movement_completed_returns=ctrl['am_returns'],control_actual_helper_calls=ctrl['am_helper_entries'],live_monitor_pass=True,movement_context_checks=co['am_context_checks'],context_corruptions=0,movement_max_private_depth=co['am_max_depth'],movement_min_task_headroom=co['am_min_headroom'],creation_max_nested_private_depth=co['ad_max_depth'],creation_min_task_headroom=co['ad_min_headroom'],parent_context_checks=co['ad_context_checks'],initializer_context_checks=co['ai_context_checks'],sprite_context_checks=co['sc_context_checks'],video_equal=comparison['differing_frames']['video_sha256']==0,navigation_equal=comparison['differing_frames']['navigation']==0,PCM_byte_equal=comparison['PCM_equal'],PCM_bytes=[comparison['PCM'][name]['bytes'] for name in ['candidate','control']],all_field_difference_counts=comparison['differing_frames'],frame_counts_equal=review['candidate_frames']==review['control_frames'],exact_whole_state_equivalence=False,timing_disagreement_unresolved=True,adaptive_controller_paths_may_differ=True,control_scope='Only two collision entry regions restored(14declaredbytes);native movement,priornativefunctions,reservation,staging,heap and unusedcollisioncodecommon. This is not an unmodified-game baseline.',processors='Retained native emulator CPU/GPU/DSP/IRQ/platform/HLE services',live_collision_monitor_scope='Read-only entry/body/return ownership counts plus qualified movement context/task-stack monitor. Full collision output equivalence is separate finite component/composition evidence.'),
        report=review['report'],component_proof=build['component_gate'])
    facts['local_authorship'].update(current_disc='Coordinator new collision, movement and actor/sprite creation source/ABI/fixtures/monitors/integration; inherited functions retain their own authorship.', accepted_C='Coordinator reference for the new original-facing collision/movement/creation routines',actual_model_calls_for_current_disc_code=0,new_weight_training=False)
    facts['migration_progress']=dict(runtime=migration['runtime'],workbench=migration['workbench'],same_host_different_root=True,registered_tools=18,tested_tool_kinds=7,negative_controls=4,original_tree_fallback=False,model_files_copied=39,model_weight_shards_verified=10,model_logical_bytes=models['logical_bytes'],restored_weight_inference_verified=False,native_Chat_verified=False,full_workbench_restored=False,all_tools_behavior_verified=False,off_machine_restore_verified=False,future_hardware_verified=False,canonical_publication_snapshot_resident_bytes=26220,scope='Copied current frontend/Python/26moduleclosure plus a workbench/evidence subset; historical paths adapted in memory with origin-read rejection. Seven tool kinds tested,including nativeCPU and rendered image. Source/corpus/model package expansion separate receipts. Copied47GBweights are not the source of the current loaded-model output probes. No full toolchain/training/workflow/off-machine restore claim.',boundary_report=str(Path(migration['directory'])/'protocol.json'),model_copy_report=str(Path(models['directory'])/'protocol.json'))
    deps = dict(previous['dependencies_sha256'])
    for obj in [review,migration,models]:
        for p,h in obj.get('dependencies_sha256',obj.get('source_sha256',{})).items():
            assert sha(p)==h,p
            assert p not in deps or deps[p]==h,p
            deps[p]=h
    for path in [Path(__file__),*out.glob('*.json')]:
        deps[str(path)]=sha(path)
    # Freeze any inherited mutable aliases before this publication is made live.
    snapshots=out/'snapshots';snapshots.mkdir();aliases=[]
    for name,h in list(deps.items()):
        p=Path(name)
        if p.name.endswith(('-current.json','-active.json')):
            assert sha(p)==h,name
            target=snapshots/(hashlib.sha256(name.encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);deps[str(target)]=h;del deps[name];aliases.append(dict(original=name,snapshot=str(target),sha256=h))
    result=dict(status='terminal_native_geometry_status_v2_published',schema_version=2,directory=str(out),recorded_at=facts['recorded_at'],facts=facts,dependencies_sha256=deps,historical_pointer_snapshots=aliases,scope=__doc__+' Full goal remains active. Five older processor jobs are observed separately by their own disc hashes. The restore workbench preserves a26220snapshot,not a live mirror of this publication.')
    for p,h in deps.items():
        assert sha(p)==h,p
    save(out/'publication.json',result);save(pointer,result)
    print(json.dumps(dict(status=result['status'],resident_bytes=28380,dependency_files=len(deps),new_training=False,default_preview_promoted=False)))


if __name__=='__main__':
    main()
