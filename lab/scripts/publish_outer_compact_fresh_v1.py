"""Publish measured compact-arena gameplay and reconcile current facts from evidence."""
import shutil
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_scene_gpu_family_component_v1 import clone

def main():
    componentp=V/'outer-compact-components-reviewed-v1-current.json';component=read(componentp)
    prefixp=V/'outer-compact-fixed-prefix-reviewed-v2-current.json';prefix=read(prefixp)
    readerp=V/'copied-Reader37-reviewed-v1-current.json';reader=read(readerp)
    deps={str(Path(__file__)):sha(__file__)}
    for pointer,proof in [(componentp,component),(prefixp,prefix),(readerp,reader)]:
        for p,h in proof.get('dependencies_sha256',proof.get('source_sha256',{})).items():assert sha(p)==h,p
        deps.update(proof.get('dependencies_sha256',proof.get('source_sha256',{})));deps[str(pointer)]=sha(pointer)
    bp=V/'native-outer-compact-disc-build-v1-current.json';b=read(bp);scene_gate=read(V/'outer-compact-final-bridge-v1-current.json')
    out=V/'outer-compact-fresh-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    jobs={};reports={}
    for lane in ['candidate','control']:
        pointer=V/f'native-outer-compact-fresh-v2-{lane}-current.json';j=read(pointer)
        assert j['status']=='terminal_fresh_scene17_route_pending_review'
        assert j['snapshot_restores']==j['host_guest_RAM_writes']==j['host_CPU_or_task_seeds']==0
        for p,h in j['source_sha256'].items():assert sha(p)==h,p
        deps.update(j['source_sha256']);deps[str(pointer)]=sha(pointer)
        report=Path(j['report']);assert sha(report)==j['report_sha256'];deps[str(report)]=sha(report)
        for p in (Path(j['directory'])/'candidate').glob('*-observation.json'):deps[str(p)]=sha(p)
        jobs[lane]=j;reports[lane]=read(report);save(out/(lane+'-job.json'),j)
    a,c=reports['candidate']['frames'],reports['control']['frames'];candidate=jobs['candidate']
    fields=['video_sha256','held_buttons','raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','floor_word','locomotion_state']
    compared={}
    for key in fields:
        ids=[x['frame']for x,y in zip(a,c)if x[key]!=y[key]]
        compared[key]=dict(count=len(ids),first_frame=ids[0]if ids else None,final_equal=a[-1][key]==c[-1][key])
    frontend=sum((x.get('navigation')or{}).get('buttons',[])!=(y.get('navigation')or{}).get('buttons',[])for x,y in zip(a,c))
    heap={k:j['outer_observation']['minimum_heap_free_while_outer_active']for k,j in jobs.items()}
    outer_low={k:j['outer_observation']['C_stack_low_offset']for k,j in jobs.items()}
    assert len(a)==24985 and len(c)==24969 and heap==dict(candidate=19696,control=19696)and outer_low==dict(candidate=204,control=204)
    assert compared['video_sha256']['count']==7351 and compared['held_buttons']['count']==359 and frontend==338
    assert all(x['final_equal']for x in compared.values())
    nr=candidate['shared_observation']['native_returns'][5];nh=candidate['shared_observation']['helper_returns'][5]
    assert nr==6299 and nh==5297
    observations={name:read(Path(candidate['directory'])/f'candidate/{name}-observation.json')for name in ['rotation','clear','display']}
    assert all(x['returns']==5297 for x in observations.values())
    comparison=dict(fields=compared,frames=dict(candidate=len(a),control=len(c)),frontend_button_schedule_differences=338,game_latched_button_RAM_differences=359,
        field_meanings=dict(held_buttons='Game-latched controller RAM long at0x49ba4; not the frontend schedule.'),
        audio={k:r['audio']for k,r in reports.items()},final_video_equal=True,final_selected_fields_equal=True,
        identical_frontend_inputs=False,same_feedback_policy=True,minimum_sampled_heap_while_outer_active=heap,global_heap_minimum_measured=False,
        scope='Control restores only ten original scene-entry bytes in the same compact layout. Both retain the same compact outer task and inherited global native GPU wrappers. Candidate scene bypasses their pending-command guard using its pinned-original idle-only wait. Different feedback input schedules and changed layout prevent a single-cause timing or fidelity inference.')
    save(out/'fresh-comparison.json',comparison)
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
    packet=read(w['packet']);save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet)
    report=ROOT/'reports/BIWN Compact Outer Memory and Fresh Route Review.txt'
    action='Use the recovered capacity to implement and qualify readable170A0 geometry-record processing and its copy/movement-matrix providers. Continue fixed-input/device-wait analysis and remaining CPU/GPU/DSP/HLE source recovery. Whole-game same-console rebuilding, useful held-out training quality, copied-weight Native Chat rendering and audio/IRQ/physical-console fidelity remain open.'
    facts={k:v for k,v in component.items()if k!='dependencies_sha256'}
    facts.update(status='terminal_compact_outer_fresh_route_and_live_capacity_verified_fidelity_open',directory=str(out),report=str(report),fresh_gameplay_verified=True,
        candidate_frames=len(a),control_frames=len(c),fresh_scene_native_returns=nr,fresh_scene_helper_returns=nh,
        native_display_returns=5297,native_rotation_returns=5297,native_clear_returns=5297,video_differences=7351,
        game_latched_button_RAM_differences=359,frontend_button_schedule_differences=338,final_video_equal=True,final_selected_game_fields_equal=True,
        live_heap_gain_measured=True,minimum_sampled_heap_while_outer_active=heap,previous_sampled_outer_active_heap=dict(candidate=560,control=560),
        sampled_outer_active_heap_increase=19136,global_heap_minimum_measured=False,outer_C_stack_low_offsets=outer_low,
        all_monitors_clear_and_quiescent=True,snapshot_restores=0,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,
        current_fixed_input_video_comparison=prefix['comparisons']['compact_candidate_control']['video_sha256'],
        fixed_input_control_layout_changes=prefix['comparisons']['compact_control_versus_v30_control'],
        game_fidelity_verified=False,next_action=action)
    report.write_text('BIWN — compact outer task, measured memory and fresh route\n\n'
        'The new experimental image completes 24,985 candidate and 24,969 control frames from a fresh HLE CD boot. All 6,299 native scene calls and 5,297 captured geometry-record calls return. Display-list, rotation and clear helpers each return 5,297 times. All retained/shared/face/geometry/outer/reset/display/clear/rotation monitors finish clear and quiescent. No checkpoint or host RAM/CPU/task repair was used.\n\n'
        'Free heap sampled while the outer task was active rises from 560 to 19,696 bytes in both lanes, an increase of 19,136 bytes. This is not the global minimum. Each private outer slot shrinks from 576 to 384 bytes, reclaiming 19,392 bytes across 101 slots. Added code/alignment consumes 256 bytes of that gain. Initial heap rises from 120,320 to 139,456 bytes. Outer C stack uses 164 of 224 reserved bytes, retaining 60 bytes of measured margin; scene stack remains 168 of 208 bytes. The shared module is 48,738 bytes and outer module 6,060 bytes. Linked code is 89,830 bytes; total reservation is 258,432 bytes; boot copy is 116,224 bytes.\n\n'
        'All eight relocated component/startup/heap gates pass, along with scene 772, display-body 1,153, fallback 384, self-reentry 64, public-bus 14, scene/input/face aliases 256, input/face aliases 256, coordinate/geometry aliases 128 and outer-connected 128. Both deployed modules rebuild byte for byte with the copied SDK. Read-only monitors pass fault controls, 512 shared CPU lanes, 64 geometry lanes and 128 actual outer root/iteration lanes. The extra outer test deliberately ends with its outer call active at an iteration boundary; that state is checked explicitly. Its first completion assumption failed and is preserved, alongside the corrected result. An early reset-observer launch also waited on a not-yet-complete retained gate and was rerun only after that dependency passed.\n\n'
        'Fidelity remains unresolved: 7,351 paired video frames differ, while final video and selected final fields agree. Game-latched controller RAM differs on 359 paired frames; actual frontend button schedules differ on 338 frames. Both audio captures are silent. The identical-input 1,000-frame prefix differs on 437 video frames, first at frame 552; v30 differed on 435, first at 551. Compact versus v30 controls differ on 216 video frames, first at 195. Cross-layout game-latched RAM differs on 3 frames despite identical frontend schedules. Earlier wording that treated the RAM field as frontend input is corrected here. No rendering, speed, IRQ, audio or console fidelity improvement follows from the memory gain.\n\n'
        'Current outer-context/layout changes are coordinator-authored. Earlier linked hybrid components retain their recorded attribution; no new local model body or trained weights were adopted. The copied local Reader37 answered in 13.2 seconds and 140 words, with correct main numbers, but invented a pending disc for an unbuilt prototype. Its answer is not fully approved. Reader38 now explicitly distinguishes source prototypes from built images; one bounded local attempt is queued behind the shared model lease. Exact Reader37 prompts/output are preserved. No optimizer updates or broad trained-quality result. Native-window inspection timed out, so copied-weight LM Studio Chat rendering remains unverified.\n\n'
        'The installed Desktop checkpoint preview is unchanged. Full readable-source and same-console rebuilding, remaining CPU/GPU/DSP/HLE/device/rendering recovery, useful training quality and future 256 GB hardware performance remain incomplete.\n\nNext: '+action+'\n\nDisc: '+b['derived_disc']+'\nComparison: '+str(out/'fresh-comparison.json')+'\n')
    packet['native_outer_compact_progress']=packet['latest_source_development']=facts
    packet['previous_native_candidate_before_outer_compaction']=packet['latest_native_candidate']
    latest=dict(status=facts['status'],variant='v32 compact persistent outer task with v30 scene GPU CPU command family',directory=str(out),report=str(report),
        candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],native_internal_helpers=['0x'+x for x in b['geometry_internal_helper_entries']],
        native_input_internal_helpers=['0x1102a'],native_scene_internal_helpers=['0x'+x for x in b['scene_internal_helper_entries']],total_internal_compiled_helpers=16,
        native_module=scene_gate['payload'],native_module_sha256=scene_gate['payload_sha256'],native_module_bytes=48738,native_outer_module_bytes=6060,
        native_code_bytes=89830,total_reservation_bytes=258432,candidate_initial_heap_bytes=139456,
        maximum_observed_C_stack_bytes=164,C_stack_partition_bytes=176,observed_C_stack_margin_bytes=12,native_geometry_cases=256,native_retained_cases=4992,native_fallback_cases=1280,
        native_scene_C_stack_partition_bytes=208,native_scene_prototype_C_stack_bytes=168,scene_C_stack_low_offset=648,
        native_outer_C_stack_bytes=164,native_outer_C_stack_reserved=224,native_outer_C_stack_margin=60,outer_arena_stride=384,
        final_address_gates_verified=True,new_nesting_verified=True,fresh_route_completed=True,new_fresh_gameplay_verified=True,native_disc_qualified=False,native_disc_fidelity_verified=False,
        candidate_frames=len(a),control_frames=len(c),differing_video_frames=7351,final_video_equal=True,final_selected_game_fields_equal=True,
        native_scene_entries=nr,native_scene_returns=nr,native_scene_helper_returns=nh,native_rotation_returns=5297,native_clear_returns=5297,native_display_returns=5297,
        game_latched_button_RAM_differing_frames=359,frontend_button_schedule_differing_frames=338,held_button_differing_frames=359,
        minimum_sampled_heap_while_outer_active=heap,control_scope=comparison['scope'],control_restores_only_scene=True,installed_preview_changed=False,
        experimental_game_model_adopted=False,whole_game_complete=False,copied_final_module_rebuild_verified=True,all_runtime_error_pending_outside_counts_zero=True,
        authorship='Current outer state/layout is coordinator work; prior linked hybrid-code attribution is retained.',scope=facts['scope']+' '+comparison['scope'],next_action=action)
    packet['latest_native_candidate']=packet['latest_fresh_reviewed_candidate']=latest;packet.pop('pending_native_candidate',None)
    scene=dict(status=facts['status'],profile='deck-shared-v30-scene-gpu-commands-v1',image_profile=facts['profile'],experimental_disc=b['derived_disc'],experimental_disc_sha256=b['derived_disc_sha256'],
        final_module_bytes=48738,prototype_module_bytes=48738,native_code_bytes=89830,initial_heap_bytes=139456,shared_bridge_cases=772,final_scene_cases=772,shared_bridge_C_stack_bytes=168,
        native_display_integrated=True,native_display_returns=5297,native_rotation_returns=5297,native_clear_returns=5297,original185B2_retained=False,original185B2_global_entry_preserved=True,original185B2_captured_inside_scene=False,
        fresh_scene_native_entries=nr,fresh_scene_native_returns=nr,fresh_scene_helper_returns=nh,candidate_frames=len(a),control_frames=len(c),fresh_differing_video_frames=7351,held_input_differing_frames=359,
        game_latched_button_RAM_differences=359,frontend_button_schedule_differences=338,final_video_equal=True,final_selected_game_fields_equal=True,new_disc_fresh_gameplay_tested=True,new_disc_fresh_route_completed=True,new_disc_fidelity_verified=False,
        latest_fresh_result_is_passing_route=True,minimum_sampled_heap_while_outer_active=heap,current_fixed_input_video_comparison=facts['current_fixed_input_video_comparison'],
        fixed_input_control_layout_changes=facts['fixed_input_control_layout_changes'],remaining_original_scene_services=['0x170a0'],installed_preview_changed=False,report=str(report),scope=latest['scope'],next_action=action)
    packet['native_scene_draw_progress']=scene
    display=dict(packet['native_display_list_progress']);display.update(status=facts['status'],module_bytes=48738,module_sha256=scene_gate['payload_sha256'],
        final_deployed_payload=scene_gate['payload'],module_address=b['shared_Deck_code_address'],experimental_disc=b['derived_disc'],fresh_gameplay_verified=True,fresh_route_completed=True,
        final_native_display_returns=5297,candidate_frames=len(a),control_frames=len(c),game_fidelity_verified=False,report=str(report),next_action=action)
    packet['native_display_list_progress']=display
    gpu=dict(packet['native_scene_gpu_family_progress']);gpu.update(status=facts['status'],image_profile=facts['profile'],candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],module_sha256=scene_gate['payload_sha256'],
        initial_heap_bytes=139456,reservation_bytes=258432,linked_native_bytes=89830,boot_copy_bytes=116224,candidate_frames=len(a),control_frames=len(c),fresh_scene_native_returns=nr,fresh_scene_helper_returns=nh,
        native_display_returns=5297,native_rotation_returns=5297,native_clear_returns=5297,video_differences=7351,held_input_differences=359,game_latched_button_RAM_differences=359,frontend_button_schedule_differences=338,
        minimum_sampled_heap_while_outer_active=heap,current_fixed_input_v30_comparison_verified=True,current_fixed_input_video_comparison=facts['current_fixed_input_video_comparison'],
        report=str(report),scope=latest['scope'],next_action=action)
    packet['native_scene_gpu_family_progress']=gpu
    packet['native_outer_inplace_progress'].update(integrated_into_compact_candidate=True,compact_profile='deck-outer-v32-compact-v1',compact_fresh_review=str(V/'outer-compact-fresh-reviewed-v1-current.json'),next_action=action)
    packet['native_scene_dispatch_headroom_progress']['next_action']=action
    packet['current_frame_difference_analysis']=dict(status=prefix['status'],review=str(prefixp),comparisons=prefix['comparisons'],field_meanings=prefix['field_meanings'],whole_game_fidelity_proven=False)
    packet['current_copied_Reader_progress']=dict(status=reader['status'],directory=reader['directory'],review=str(readerp),actual_predictions=1,seconds=13.2,words=140,max_words=150,word_limit_pass=True,
        required_current_numeric_facts_correct=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=True,artifact_type_error=True,latest_source_changed_since_last_prediction=True,
        broader_quality_approved=False,quality_approved=False,new_training=False,optimizer_updates=0,trained_adapter_used=False,native_Chat_display_verified=False,raw_responses_retained=True,
        model_identifier=reader['model_identifier'],ordinary_launcher_verified=True,default_reader_version=38,default_reader_prepared=True,default_reader_generation_verified=False,
        scope='One actual copied Reader37 response passed numeric and140-word formatting checks but called an unbuilt prototype a pending image. Current Reader38 has explicit artifact types; no accepted reply on the compact-image facts yet.')
    packet['current_default_Reader_progress']=dict(status='prepared_Reader38_artifact_type_prompt_correction_prediction_pending',version=38,prepared=True,current_evidence_preflight_verified=False,actual_prediction_verified=False,new_predictions=0,new_training=False,native_Chat_verified=False,
        entry=str(P/'workbench/portable_biwn.py'),script=str(P/'workbench/scripts/run_deck_status_live_v38.py'),scope='Corrected prototype/image instruction; one bounded ordinary-launcher attempt is queued. No copied-weight Native Chat rendering or trained-quality claim.')
    packet['checked_current_summary']='Compact outer image passes 24,985/24,969 fresh frames and all monitors. Native scene6,299; geometry-service/display/rotation/clear5,297 each. Sampled outer-active heap19,696 bytes versus560 before; outer stack164/224 and scene168/208. Video7,351 differences, final video/selected fields agree; silent audio. Same-input1,000-frame prefix437 video differences. Whole-game rebuilding, fidelity and useful trained quality remain open; checkpoint preview unchanged.'
    save(out/'facts.json',facts);save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py');shutil.copy2(report,out/report.name)
    deps.update({str(p):sha(p)for p in out.rglob('*')if p.is_file()});deps[str(report)]=sha(report)
    pub=V/'outer-compact-fresh-reviewed-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),report=str(report),facts=str(out/'facts.json'),new_predictions=0,new_training=False,whole_objective_complete=False,dependencies_sha256=deps))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,w)
    for p,h in deps.items():
        src=Path(p);assert src.is_relative_to(ROOT);clone(src,P/'workbench'/src.relative_to(ROOT))
    clone(pub,P/'workbench/verification'/pub.name);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text());(root/'WATCH LOCAL AGENTS.txt').write_text(report.read_text()+'\nExact saved local prompts and outputs are available through Model Prompts and Responses.command.\n')
    print(facts['status'],report,flush=True)

if __name__=='__main__':main()
