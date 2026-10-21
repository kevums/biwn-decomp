"""Publish a measured source stack repair; preserve both rejected designs."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    names=['acquire-stack-gap-prototype-v2','native-input-acquire-gap448-caller-v5','acquire-arena-prototype-v1',
        'native-input-acquire-arena-caller-v1','native-input-arena-admission-v6','native-input-arena-admission-entry-v1',
        'native-input-acquire-arena-caller-v2','native-input-acquire-arena-second-CPU-v1','acquire-arena-identity-v1']
    paths=[V/(n+'-current.json')for n in names];receipts=[read(p)for p in paths]
    gap,rejected,arena,first,v6,entry,primary,second,identity=receipts
    assert gap['original512_rebuild_byte_identical'] and gap['changed_displacement_instructions']==7
    assert rejected['status']=='terminal_full_caller_comparison_failed' and rejected['completed']==6
    overlap_path=Path(rejected['directory'])/'parked-state-overlap.json';overlap=read(overlap_path)
    assert overlap['PC']==0x15f4b2 and overlap['frame']['target']==0x1b044
    assert arena['code_bytes']==676 and arena['new_RAM_reserved']==0
    assert first['completed']==18 and v6['changed_bytes']==1 and v6['copied_build_byte_identical']
    assert entry['completed']==20188 and entry['native_reserve_bytes']==768
    for receipt in [primary,second]:
        assert receipt['completed']==27 and receipt['admitted_native_cases']==9 and receipt['original_fallback_cases']==18
        assert receipt['actual_stream_loader_calls']==receipt['actual_loaded_payload_checks']==receipt['scripted_loader_yields']==6
        assert receipt['actual_blitter_copy_commands']==6 and receipt['parked_state_checks']==21
        assert receipt['native_max_caller_stack']==786 and receipt['fallback_max_caller_stack']==524
        assert receipt['minimum_private_arena_stack_offset']==60 and receipt['raw_volatile_differing_cases']==0
    assert primary['public_RAM_and_ordered_bus_equal_outside_task_private_arena']
    assert not second['ordered_CPU_data_bus_verified'] and second['actual_pinned_native_CPU']
    assert identity['completed']==432 and identity['valid_task_slots']==101 and identity['invalid_ids']==7
    assert identity['C_body_explicit_RTS_provider'] and identity['v6_all_symbol_addresses_independently_verified']
    for receipt in receipts:
        assert receipt['status'].startswith('terminal_')
        for p,h in receipt.get('source_sha256',{}).items():assert sha(p)==h,p
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp)
    for p,h in wrapper['dependencies_sha256'].items():assert sha(p)==h,p
    packet=read(wrapper['packet']);previous=packet['current_native_input_prototype_progress']
    assert packet['unqualified_native_input_image']['stack_failure_confirmed_two_CPUs']
    out=V/'acquire-arena-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'before-packet.json',packet)
    report=ROOT/'reports/BIWN Resource Stack Arena Prototype.txt'
    report.write_text(
        'BIWN — resource compiler-stack arena prototype\n\n'
        'RESULT\n'
        'A source prototype fixes the measured resource-stack collision in27controlled caller comparisons on each of two CPU cores. The resource-acquire C algorithm and all compiled resource/release/load/heap/copy/GPU providers remain in place. A676-byte coordinator assembly adapter parks acquire compiler state in the existing per-task GPU scratch slot, keeping original guest helper stacks and arguments separate. No additional RAM is reserved. This prototype is at fixture1F0000with5explicit jump stubs in an in-memory resident copy. It is not a new CDI, not promoted and not a complete game. Failed v38 remains unchanged; reviewed v34 and the earlier Desktop preview remain unchanged. Pending v37 still fails its separate22858pixel matrix-video gate.\n\n'
        'REJECTED SMALLER-GAP DESIGN\n'
        'The inherited512-byte acquire shim first rebuilt byte-identically at its actual address. A448-byte source variant kept all function addresses and opcodes, changing only7LEAdisplacements (9bytes). It avoided the first task-header collision in resident-resource cases, but was rejected on cache miss after6completed valid-stack comparisons. At PC0x15F4B2, the nested loader wrote4bytes at0x0C1730inside parked acquire state[0x0C1680,0x0C1734). Shrinking the gap therefore exchanges one corruption for another. The original failed v38 still reaches958task-stack bytes and changes protected task bytes62/63; its second-core counterexample remains preserved. An initial linker attempt aligned the shim two bytes too high; its byte-identity guard rejected it before use. A fixed explicit section address/SUBALIGN(2) was required.\n\n'
        'ARENA DESIGN\n'
        'Each existing GPU scratch slot is256bytes with16-byte fences at both ends,224usable bytes. The new resource context uses72bytes at slot+168; its compiler stack grows below that. Original resource-acquire D2-D5/A2-A3 guest saves remain on the original task stack. Dependency captures temporarily restore the original guest SP/arguments and recover the parked compiler SP afterward. The original acquire C body is unchanged at0x160434. Five old entry points jump to the new adapter/captures. No heap or arena allocation changes in this fixture. This reuse still requires a lifetime/ownership proof against GPU activity, real task switches, IRQs and reentry; it is not a general shared-stack safety claim.\n\n'
        'CONNECTED EXECUTION\n'
        'The initial18valid task+1020caller comparisons passed, revealing786maximum guest-stack bytes and180of224private scratch bytes used (minimumSPoffset60, lower fence ends16). A further changed-input/changed-progress27-case matrix passes on the primary CPU, and27paired comparisons pass independently on the pinned native M68000. Each matrix covers9resource/heap scenarios:9nativeinput and9supervisorfallback at task+1020, plus9valid headroom fallbacks at task+800 under the revised admission reserve. Reference executes original191F4; candidate executes compiled input. Both retain the same actual compiled resource/load/heap/copy/matrix providers. No providers were replaced with original implementations to make a test pass.\n\n'
        'Per matrix: get18? The actual saved receipt is authoritative: get27,release27,allocate33,free30;6actual loader calls,6actual blitter copies,6independent512-byte payload checks,6controlled loader yields,21parked-state return checks. Native guest-stack maximum786; fallback524. All final registers/flags/banks, targeting incoming registers, helper arguments/inputD0seeds and public RAM match. All102arena-slot fences remain intact. Private scratch context/stack bytes are explicit exclusions from public RAM/bus comparison, with raw differences retained; they are never changed in live execution for comparison. In the primary matrix746bus-value differences occur inside the selected224-byte private interval; final private RAM differs in2cases. A source adapter first labeled only savedA0, then D1/A0/A1, before the arena prototype needed the complete declared private interior; the final27-case receipt uses the complete interval explicitly. No public memory field is normalized.\n\n'
        'The primary CPU checks every write against parked acquire state while each dependency runs, then verifies the entire parked snapshot at return. The pinned core separately executes the same provider combination and checks return snapshots; its instruction-boundary interface does not observe CPU data-bus order or every private write. These are independently original-versus-native comparisons, not a direct all-state cross-core comparison.\n\n'
        'TransportD206/D2F0/D306,data/progress,one reference event,cache wait/signal,loader yield and boundary backends remain controlled. The CLR.L dummy read is excluded from progress advancement so every actual load takes one declared yield. OriginalGPU4320completes synchronously; this is not console timing. Real TRAP/RTE,arbitraryIRQ,nested geometry and audio remain open. Earlier6945scripted cases with837upperD1differences are not waived by this zero-final-difference set.\n\n'
        'ADMISSION / COPIED SDK\n'
        'Inputv6remains10580bytes at0x17C724. It changes one immediate byte from the v5binary: the provisional reserve512becomes768. All other bytes and all ELF symbol addresses match; the C algorithm, physical-call bridge and unedited local predicate remain unchanged. The copied SDK independently rebuilds v6identically. The measured786full-caller peak includes60bytes of caller overhead before input entry;768covers this measured chain with42bytes remaining, but it is not a global helper/IRQ bound.20,188new direct-entry route/fence cases cover the new832-byte offset boundary,all101slots,invalid task/SP values,user/supervisor and flags. The36-byte checked preflight remains safe and preserves the measured D0/callee-save/SR/SP/banks until routing. No stack access precedes preflight.\n\n'
        'The former task+500fallback fixture has only436bytes above its fence and cannot fit every original-input/compiled-resource path. It is not counted as a passing full-helper fallback. The new task+800headroom fixture is below the768entry threshold after caller overhead and has enough room for the measured524-byte original-input path. Original fallback still does not repair an invalid original stack.\n\n'
        'ADAPTER IDENTITY CHECKS\n'
        '432adapter-only cases cover all101task slots and7invalid IDs,each in user/supervisor modes with two incoming flag endpoints. An explicit RTS C-body provider isolates slot selection,capture and restoration. All15GPRs,SR,SP,alternate stack bank,exact34guest-save bytes,all102slot fences and every byte outside the selected private interval/guest save match. Invalid IDs select boot slot101. These are not432resource,task-switch or IRQ tests.\n\n'
        'WHO / LOCAL MODEL STATUS\n'
        'Coordinator authored all new assembly,builds,tests and publication. No cloud subagents or local LLM generations ran in this continuation; no optimizer updates or new weights. The earlier local predicate and widening helper keep their attribution. DefaultReader43and prepared structuredReaderremain unapproved for these new facts. Native LMStudioChatvisibility,easy ordinary inference and useful trained-model gain on untouched restoration tasks remain unverified. No unrelated model jobs were inspected or interrupted.\n\n'
        'NEXT\n'
        'Prove scratch lifetime across actual resource waits/yields and different tasks/GPU activity;test same-task alias/reentry and IRQ behavior. Add a checked ownership mechanism if a legal path can overlap. Then relink the676-byte adapter into the real resident layout,move finalizer/Deck/outer arenas and heap as needed,perform copied rebuilds and all exact-address/startup/heap/provider/alias/observer/fresh gates. Do not promote based on a fixture1F0000run. Fullsource-onlysame-consoleCPU/GPU/DSP,audio/fidelity,physical verification,usefultraininggain,nativeChat ease and future256GBhardware remain incomplete.\n\n'
        'Rejected gap:'+str(paths[1])+'\nOverlap:'+str(overlap_path)+'\nArena source:'+arena['source_profile']+'\nV6input:'+str(paths[4])+'\nEntry routes:'+str(paths[5])+'\nPrimary:'+str(paths[6])+'\nPinned core:'+str(paths[7])+'\nAdapter identity:'+str(paths[8])+'\n')
    # Remove a drafting marker before publishing the exact final report.
    report.write_text(report.read_text().replace('get18? The actual saved receipt is authoritative: get27','get27'))
    progress=dict(status='terminal_shared_arena_source_stack_repair_bounded_dual_CPU_pass_image_open',report=str(report),source_profile=arena['source_profile'],adapter_bytes=676,adapter_fixture_address=0x1f0000,adapter_stubs=5,new_RAM_reserved=0,input_profile=v6['source_profile'],input_bytes=10580,input_byte_changes=1,all_other_input_bytes_identical=True,all_input_symbol_addresses_identical=True,copied_SDK_byte_identical=True,input_reserve=768,input_reserve_global_bound_proven=False,primary_paired_cases=27,pinned_CPU_paired_cases=27,native_routes_each=9,supervisor_fallback_each=9,valid_headroom_fallback_each=9,headroom_fixture_offset=800,old500fallback_not_qualified=True,actual_loads_each=6,actual_blitter_copies_each=6,payload_checks_each=6,controlled_loader_yields_each=6,parked_state_checks_each=21,native_guest_stack=786,fallback_guest_stack=524,private_scratch_used=180,private_scratch_usable=224,minimum_private_SP_offset=60,all102slot_fences_checked=True,private_comparison_exclusion_bytes=224,private_raw_bus_differences=746,private_final_RAM_differing_cases=2,runtime_RAM_normalized=False,primary_ordered_public_bus_and_all_parked_writes_checked=True,pinned_ordered_CPU_bus_checked=False,all_final_contexts_match=True,entry_route_cases=20188,preflight_stack=36,adapter_only_identity_cases=432,identity_valid_slots=101,identity_invalid_ids=7,identity_C_body_RTS_provider=True,rejected_gap=448,rejected_gap_completed_pairs=6,rejected_gap_parked_state_corruption=True,original_v38_failure_preserved=True,new_disc_built=False,default_promoted=False,installed_preview_changed=False,real_task_switch_qualified=False,scratch_lifetime_alias_qualified=False,arbitrary_IRQ_qualified=False,fresh_gameplay_verified=False,game_frames=0,new_predictions=0,optimizer_updates=0,reviews=[str(p)for p in paths],scope='Controlled compiled-provider source prototype plus new768entry routes and adapter-only slot tests. No new image or lifetime/scheduler/IRQ proof.')
    component=dict(status=progress['status'],profile='input-dispatch-native-v6-arena-admission',artifact_type='uninstalled_input_and_resource_adapter_source_prototype',module_bytes=10580,resource_adapter_bytes=676,source_profile=v6['source_profile'],payload=v6['payload'],payload_sha256=v6['payload_sha256'],component_prefix_byte_identical=False,same_v5_bytes_except_one_reserve_immediate=True,algorithm_runtime_C_statements_changed=0,copied_SDK_byte_identical=True,all_symbol_addresses_unchanged=True,new_disc_built=False,installed_in_experimental_image=False,installed_in_default_game=False,default_promoted=False,private_task_stack_admission_qualified=False,full_real_helper_bound_proven=False,arbitrary_IRQ_qualified=False,all_remaining_provider_bodies_qualified=False,fresh_gameplay_verified=False,installed_preview_changed=False,new_predictions=0,optimizer_updates=0,new_training=False,native_Chat_verified=False,report=str(report),stack_repair_progress=progress,historical_v5_failed_image=str(V/'native-input-callsite-disc-build-v1-current.json'),scope=progress['scope'])
    packet['previous_native_input_component_before_arena_repair']=previous
    packet['current_acquire_arena_stack_progress']=progress
    packet['current_native_input_prototype_progress']=packet['latest_source_development']=component
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    packet['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v33.py')
    packet['current_status_frontend_progress']=dict(status='status20_entry33_prepared_actual_checks_pending',renderer=str(ROOT/'scripts/show_native_status_v20.py'),portable_entry_version=33,default_brief_lines=12,new_predictions=0,detailed_report=str(report))
    packet['checked_current_summary']='Reviewedv34unchanged;failedv37video/v38stackremainunpromoted. Rejected448gapcausesparked-statecorruption. New676byteacquireadaptersharesper-taskGPUarena,no newRAM,fixture1F0000only. Inputv6reserve768onebytechange/copiedSDKidentical. Actualcompiledresourcechain27pairspereachCPU,sixloads/copies/yieldseach,21parkedchecks,guest786/fallback524/private180of224,fences/finalCPU/publicstatematch. Declared224privatebytesexcludedwithrawdifferencesrecorded;primaryCPUbuschecked,pinnedbusunobserved.20188entryroutesand432adapter-onlyidentitycasespass. Real task switching,arena-lifetime/IRQ/image/fresh/source-onlyfullgame/fidelity/audio/trainedgain/nativeChat/futurehardwareunfinished. No newprediction,weights,imageorpreviewchange.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
    save(out/'facts.json',dict(component=component,progress=progress));save(out/'current-status-packet.json',packet)
    deps={str(Path(__file__)):sha(__file__),str(report):sha(report)}
    for path,receipt in zip(paths,receipts):
        deps[str(path)]=sha(path);deps.update(receipt.get('source_sha256',{}))
        for artifact in Path(receipt['directory']).rglob('*'):
            if artifact.is_file()and'__pycache__'not in artifact.parts:deps[str(artifact)]=sha(artifact)
    for name in ['show_native_status_v20.py','portable_biwn_entry_v33.py','check_native_input_acquire_gap448_caller_v1.py','check_native_input_acquire_gap448_caller_v2.py','check_native_input_acquire_gap448_caller_v3.py','check_native_input_acquire_gap448_caller_v4.py','prepare_acquire_stack_gap_v1.py']:
        path=ROOT/'scripts'/name;deps[str(path)]=sha(path)
    deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py');deps[str(out/'before-portable_biwn.py')]=sha(out/'before-portable_biwn.py')
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    clone(ROOT/'scripts/portable_biwn_entry_v33.py',P/'workbench/portable_biwn.py')
    wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps});atomic(wp,wrapper);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    atomic(V/'acquire-arena-delivered-v1-current.json',dict(status='terminal_source_stack_repair_published_images_unpromoted',directory=str(out),report=str(report),new_predictions=0,optimizer_updates=0,new_disc_built=False,dependencies_sha256=deps))
    print('Published bounded arena source repair; v37/v38 failures and all lifetime/image limits preserved.',flush=True)


if __name__=='__main__':main()
