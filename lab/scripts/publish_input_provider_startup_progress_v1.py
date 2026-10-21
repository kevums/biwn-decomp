"""Deliver connected top-level providers and wide startup prototype evidence."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    names=['native-input-real-targeting-caller-v1','native-input-real-boundary-caller-v1',
        'native-input-real-resources-caller-v1','native-input-real-combined-caller-v1',
        'local-wide-bootstrap-author-v1','local-wide-bootstrap-reviewed-v1','wide-bootstrap-second-CPU-v1']
    paths=[V/(name+'-current.json')for name in names];proofs=[read(path)for path in paths]
    targeting,boundary,resource,combined,author,wide,dual=proofs
    assert [r['completed']for r in proofs[:4]]==[78,78,27,27]
    assert all(r['raw_volatile_differing_cases']==0 and r['all_targeting_incoming_registers_equal']for r in proofs[:4])
    assert targeting['selected_target_cases']==42 and boundary['actual_outdoor_boundary_calls']==boundary['actual_indoor_boundary_calls']==39
    assert boundary['boundary_directions_covered']==[0,1,2,3]and boundary['nested_boundary_script_calls']==81
    for r in [resource,combined]:
        assert r['actual_resource_get_calls']==r['actual_resource_release_calls']==27
        assert r['actual_heap_allocate_calls']==33 and r['actual_heap_free_calls']==30
        assert r['scripted_resource_loader_calls']==r['scripted_resource_wait_calls']==6 and r['scripted_resource_signal_calls']==3
    assert combined['actual_outdoor_boundary_calls']==15 and combined['actual_indoor_boundary_calls']==12
    assert combined['nested_boundary_script_calls']==24 and combined['native_max_caller_stack']==432
    assert author['new_predictions']==1 and author['candidate_statement_edits']==0 and author['seconds']==16.34
    assert wide['host_valid_cases']==65536 and wide['host_invalid_cases']==9716 and wide['native_copy_cases']==56 and wide['native_integrated_cases']==18
    assert wide['copied_clear_build_byte_identical']and wide['negative_control_wrapped_copy_bytes']==1088 and dual['completed']==3
    for r in proofs:
        for path,digest in r['source_sha256'].items():assert sha(path)==digest,path
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp)
    for path,digest in wrapper['dependencies_sha256'].items():assert sha(path)==digest,path
    packet=read(wrapper['packet']);previous=packet['current_native_input_prototype_progress']
    assert previous['module_bytes']==10580 and not packet['pending_native_candidate']['default_promoted']
    out=V/'input-provider-startup-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'before-packet.json',packet)
    report=ROOT/'reports/BIWN Input Targeting Boundary Resources and Wide Startup Tests.txt'
    transcript=str(Path(author['directory'])/'prompts-and-responses.txt')
    plans=wide['plans'];baseline=plans['native-record-strides-disc-build-v1'];pending=plans['native-record-loop-image-disc-build-v1']
    report.write_text(
        'BIWN — targeting/boundary/resource connections and wider startup prototype\n\n'
        'The native input binary remains10580bytes and is not installed in a new game image. This turn adds four connected caller matrices and an independently tested startup-preparation helper. No original functions are newly recovered or counted. v34remains the reviewed gameplay baseline;v37remains unpromoted after its freshmatrix finalvideoFAIL22858pixels. The Desktop outdoor preview is unchanged.\n\n'
        'TARGETING CONNECTION\n'
        '78paired full-caller cases execute original20820targeting with original camera,animation,nested math and GPU4320on both sides.26nativeinput/52originalfallback routes.42cases select a target;36reject all candidates. Synthetic candidate/transform records are supplied before execution,including stationary positive examples and varied movement states. All incoming targeting registers,publicRAM,orderedCPUaccesses,helper arguments/inputD0seeds,finalflags and finalregisters match. This is a new connection test;the existing1026case/183instruction standalone fullCPUtargeting proof is inherited,not rerun.\n\n'
        'BOUNDARY ROUTING CONNECTION\n'
        '78paired cases connect original19F2Coutdoor and19FDAindoor code with targeting/camera/animation/GPU.39outdoor/39indoor calls cover all four directions.81nested geometry/cleanup/loading/yield helper calls remain explicitRTSproviders,so this is not complete collision geometry or a real transition/load. Boundary entry has upperD1differences in9calls;they are retained. Actual boundary code consumes its declared arguments compatibly and full finalCPU/publicstate matches. Twelve cases select targets in this different fixture set. No pose/timer/controller normalization of a live replay or fresh-game image comparison occurs;these are declared finite layouts.\n\n'
        'RESOURCE / HEAP CONNECTION\n'
        '27paired equipment cases cover9scenarios:resident removal/addition,eviction,cache miss,pending readiness,shared-during-load,and previous/next/both-side free-block merging.9nativeinput/18originalfallback routes. Original1AF04get/1B002release each execute27times;152A2allocator33times;1545Cfree30times. Results,reference counts,cache selection,free-list insertion/coalescing,allocation/splitting and handle registration are computed by actual original instructions,not supplied outcomes. Loader1B044sixcalls,waitDF8Csixcalls andsignalDF9Cthreecalls remain controlled providers. Actual camera/animation/targeting/GPU remain connected;boundary functions are scripted in this matrix. Public state,ordered CPU accesses,all recordedhelper arguments/inputD0seeds,targeting incoming registers,and finalCPU match.\n\n'
        'COMBINED CONNECTION\n'
        'Another27paired cases connect resource/heap,both boundary handlers,targeting,camera,animation and originalGPU together.15outdoor/12indoor calls;24nested boundary provider calls remain scripted. Resource/heap counts and backend6loader/6wait/3signal calls match the separate resource matrix. All publicRAM,orderedCPUaccesses,helper arguments/seeds,flags and finalregisters match. These27are a new provider combination,not27newly recovered functions. Across the four changed-provider matrices,210paired comparisons execute;their input cases overlap and are not210unique gameplay situations. Maximum connected native caller stack remains432bytes;original fallback maximum150.512entryreserve remains provisional for wider real nesting/IRQs. The broader earlier6945scripted matrix still has837upperD1differences,not waived by these bounded zero-final-difference sets.\n\n'
        'IMAGE PLACEMENT / STARTUP LIMIT\n'
        'The diagnostic module address1C0000overlaps the original stream loader staging buffer;it must not be used as an actual image placement. Existing image code lives below1C0000with a reserved heap layout. Inserting10580input bytes before the v34finalizer gives a planned input address'+hex(baseline['input_address'])+',finalizer'+hex(baseline['finalizer_address'])+',Deckarena'+hex(baseline['deck_arena_address'])+',heap'+hex(baseline['heap_start'])+'. Copy132160bytes,staging clear132224,start'+hex(baseline['staging_address'])+',initial freeheap123520bytes. The v37layout would copy132096/clear132160and leave123584heapbytes. These are feasible plans against the original blank staging region,not relinked images. Source modules/arenas/heap constants still require relocation and final integration checks.\n\n'
        'Both proposed sizes exceed the current131072byte word-loop capacity. Existing builders explicitly reject that condition;they have not emitted a truncated image. A deliberate naive16bit wrapping negative control copies only1088of132160bytes,demonstrating why waiving the guard is invalid. The new prototype uses MOVE.Lcopies and a longword staging-clear loop,with unchanged40byte bootstrap length. Loop capacity262144bytes is separate from the smaller actual blank staging region,header/clear overhead and heap limits.\n\n'
        'LOCAL CODER / STARTUP EXECUTION\n'
        'One actual owned copied27B6bit local Coder response produced a pure Python bootstrap patch helper in16.34seconds. Its source is unedited,with no Markdown fence removal. It accepts only the exact known40byte legacy loader except its old count,validates exact argument types/length/alignment/range,and changes only the count and MOVE.WtoMOVE.Lopcode.65536valid-header cases and9716rejection cases pass. This host helper is installed only in a separate source prototype,not current game builders. Coordinator authored the layout planner,long-clear assembly and diagnostics.\n\n'
        'Actual68000instruction tests:56copy-fragment cases cover boundaries through262144bytes;18integrated synthetic payload cases copy,clear staging,restore all savedGPRs/SR/SSP/USP and reach400Awithout executing original400A. Entire2MBRAM and canaries match an independent byte-array oracle. Three fresh131072/132096/132160byte trials also execute in the pinned native M68000core and Unicorn;allRAM/registers/flags/banks match. No gameframes or GPU run in those startup tests. A newly generated clear routine rebuilds byte-identically with the copied SDK. These checks do not execute all arena/heap initialization or qualify a complete boot/image.\n\n'
        'MODEL / FULL GOAL\n'
        'One new local prediction,no optimizer updates or new weights. Prior unapproved Reviewer outputs stay unapproved;defaultReader43unchanged. Exact prompt/rawresponse and inference timings are saved. This is useful local code generation,not evidence of trained-model gain on untouched tasks. NativeLMStudioChatvisibility remains unverified;headless operation remains authorized.\n\n'
        'NEXT\n'
        'Rebase the input source from its colliding fixture address into the planned resident placement;connect original1B044stream loading/copy under explicit transport,then qualify nested collision geometry and real scheduler/IRQ/error behavior. A new image builder must relink affected module arenas and heap constants and use both wide loops,then pass exact-address/startup/heap/provider/alias/observer gates and fresh gameplay. Preserve original191F4globalentry and the old preview until qualified. Fullsource-onlysame-console CPU/GPU/DSP game,fidelity/audio,usefultraininggain,nativeChat ease and future256GBcapacity remain unfinished.\n\n'
        'Targeting:'+str(paths[0])+'\nBoundary:'+str(paths[1])+'\nResources:'+str(paths[2])+'\nCombined:'+str(paths[3])+'\nWide startup:'+str(paths[5])+'\nSecond CPU:'+str(paths[6])+'\nExact local Coder prompt/response:'+transcript+'\n')
    remaining=dict(status='terminal_top_provider_connections_bounded_pass_nested_backends_open',report=str(report),directory=str(out),
        targeting_cases=78,target_selected_cases=42,target_rejected_cases=36,boundary_cases=78,
        outdoor_boundary_calls=39,indoor_boundary_calls=39,boundary_directions=[0,1,2,3],nested_boundary_script_calls=81,
        boundary_entry_upper_D1_differing_calls=9,resource_cases=27,resource_scenarios=resource['resource_scenarios'],
        resource_get_calls=27,resource_release_calls=27,heap_allocate_calls=33,heap_free_calls=30,
        loader_script_calls=6,wait_script_calls=6,signal_script_calls=3,
        combined_cases=27,combined_outdoor_calls=15,combined_indoor_calls=12,combined_nested_boundary_script_calls=24,
        full_public_RAM_bus_args_seeds_and_final_CPU_match=True,all_targeting_incoming_registers_match=True,
        current_sets_raw_final_differences=0,broader837_D1_differences_waived=False,
        original_GPU_both_lanes=True,synchronous_completion=True,maximum_native_stack=432,maximum_fallback_stack=150,
        geometry_loading_scheduler_providers_still_scripted=True,arbitrary_IRQ_qualified=False,
        module_bytes=10580,module_bytes_changed=False,new_original_functions_recovered=0,new_disc_built=False,
        original_191F4_global_entry_preserved=True,installed_preview_changed=False,
        targeting_review=str(paths[0]),boundary_review=str(paths[1]),resource_review=str(paths[2]),combined_review=str(paths[3]))
    startup=dict(status=wide['status'],report=str(report),source_profile=wide['source_profile'],directory=wide['directory'],
        local_Coder_seconds=16.34,local_predictions=1,model_statement_edits=0,model_function_used_in_prototype=True,
        transcript=transcript,host_valid_cases=65536,host_invalid_cases=9716,copy_CPU_cases=56,integrated_CPU_cases=18,
        second_CPU_cases=3,native_wrapped_counter_negative_controls=1,negative_wrapped_copy_bytes=1088,
        copied_clear_build_identical=True,copy_loop_capacity=262144,legacy_word_loop_capacity=131072,
        planned_layouts=plans,fixture_address_conflicts_with_stream_loader=True,
        original_blank_staging_limit_still_required=True,module_arena_heap_relink_qualified=False,
        installed_builders_changed=False,game_image_written=False,game_image_qualified=False,
        optimizer_updates=0,native_Chat_verified=False,review=str(paths[5]),second_CPU_review=str(paths[6]))
    packet['current_input_remaining_helpers_progress']=remaining;packet['current_input_wide_startup_progress']=startup
    packet['previous_native_input_component_before_provider_startup']=previous
    component=dict(previous,status='terminal_additional_input_providers_and_wide_startup_prototype_checked_no_image',
        report=str(report),directory=str(out),additional_provider_progress=remaining,wide_startup_progress=startup,
        actual_targeting_connected=True,actual_boundary_routing_connected=True,actual_resource_cache_heap_connected=True,
        all_remaining_provider_bodies_qualified=False,arbitrary_IRQ_qualified=False,full_real_helper_bound_proven=False,
        scope='Unchanged10580byteinput. New78target/78boundary/27resource/27combinedcallerpairspluswidebootstrapprototype. Nested geometry/loader/wait/signal/scheduler,IRQ/error,arenaheaprelink,image/freshfidelityremainopen.')
    packet['current_native_input_prototype_progress']=component;packet['latest_source_development']=component
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    packet['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v31.py')
    packet['current_status_frontend_progress']=dict(status='status18_entry31_prepared_actual_checks_pending',renderer=str(ROOT/'scripts/show_native_status_v18.py'),portable_entry_version=31,default_brief_lines=12,game_or_model_results_changed=False,new_predictions=0,detailed_report=str(report))
    packet['checked_current_summary']+=' New78target/78boundary/27resource/27combinedcallercomparisonsmatchpublicstate/finalCPUunderexplicitbackendlimits. Localuneditedwidecopyhelper16.34spasses65536valid/9716invalid,56copy/18clear-restore/3secondCPUchecks. Plannedv34copy132160requireswiderloops;notanimage. No weights/previewchange.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
    save(out/'facts.json',dict(providers=remaining,startup=startup));save(out/'current-status-packet.json',packet)
    deps={str(Path(__file__)):sha(__file__),str(report):sha(report)}
    for path,r in zip(paths,proofs):deps[str(path)]=sha(path);deps.update(r['source_sha256'])
    for path in Path(author['directory']).iterdir():
        if path.is_file():deps[str(path)]=sha(path)
    for name in ['show_native_status_v18.py','portable_biwn_entry_v31.py']:
        path=ROOT/'scripts'/name;deps[str(path)]=sha(path)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py');clone(ROOT/'scripts/portable_biwn_entry_v31.py',P/'workbench/portable_biwn.py')
    deps.update({str(path):sha(path)for path in out.iterdir()if path.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps})
    atomic(wp,wrapper);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    atomic(V/'input-provider-startup-delivered-v1-current.json',dict(status='terminal_additional_providers_wide_startup_published_no_image',directory=str(out),report=str(report),new_predictions=1,new_training=False,new_disc_built=False,dependencies_sha256=deps))
    print('Provider and wide startup prototype evidence published;all image/IRQ/backend limits preserved.',flush=True)


if __name__=='__main__':main()
