"""Publish rebase/stream/image startup evidence and preserve the failed stack gate."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    names = ['native-input-rebase-v1','native-input-real-stream-caller-v2','native-input-real-stream-second-CPU-v1',
        'stream-rebase-structured-reader-v1','native-input-callsite-disc-build-v1','native-input-image-startup-heap-v1',
        'native-input-image-inherited-providers-v1','native-input-image-provider-stack-diagnostic-v1','native-input-image-stack-second-CPU-v1']
    paths = [V/(name+'-current.json') for name in names]
    receipts = [read(path) for path in paths]
    rebase, stream, second, reader, build, startup, failed, diagnostic, negative = receipts
    assert rebase['changed_relocation_records'] == 48 and rebase['changed_byte_count'] == 144
    assert rebase['runtime_source_statements_changed'] == 0 and rebase['copied_build_byte_identical']
    assert stream['completed'] == second['completed'] == 27
    assert stream['actual_loaded_payload_checks'] == second['actual_loaded_payload_checks'] == 6
    assert stream['native_max_caller_stack'] == second['native_max_caller_stack'] == 458
    assert reader['status'] == 'terminal_shared_slot_busy_zero_predictions' and reader['new_predictions'] == 0
    assert build['status'] == 'terminal_input_callsite_image_built_UNQUALIFIED'
    assert startup['native_startup_cases'] == startup['Unicorn_startup_cases'] == 6 and startup['heap_initialize_cases'] == 192
    assert failed['status'] == diagnostic['status'] == 'terminal_full_caller_comparison_failed' and failed['completed'] == 0
    assert negative['status'] == 'terminal_same_input_image_task_stack_boundary_failure_confirmed_pinned_CPU'
    counter_path = Path(diagnostic['directory'])/'stack-boundary-counterexample.json'
    counter = read(counter_path)
    assert counter['PC'] == 0x1603fe and counter['SP'] == counter['task']+62 and counter['stack_bytes'] == 958
    changed = [i for i,value in enumerate(bytes.fromhex(counter['task_memory'])[:64]) if value != 0xa5]
    assert changed == [62,63]
    for receipt in receipts:
        assert receipt['status'].startswith('terminal_')
        for path,digest in receipt.get('source_sha256',{}).items():
            assert sha(path) == digest, path
    wp = V/'native-Deck-current-status-v1-current.json'
    wrapper = read(wp)
    for path,digest in wrapper['dependencies_sha256'].items():
        assert sha(path) == digest, path
    packet = read(wrapper['packet'])
    previous = packet['current_native_input_prototype_progress']
    out = V/'input-image-stack-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out/'before-packet.json',packet)
    report = ROOT/'reports/BIWN Rebased Input Image and Stack Failure.txt'
    report.write_text(
        'BIWN — rebased input, real stream loading, experimental image and failed stack gate\n\n'
        'CURRENT RESULT\n'
        'A separate v34-derived experimental v38 CDI now includes the10580-byte input component at0x17C724, with only caller1A266 redirected to0x17EFDC. Original global191F4 is preserved. The image builds and its actual wide startup/arena/heap checks pass, but its first connected native resource case violates the protected task-stack boundary. The second CPU independently confirms that failure. It is unpromoted and must not replace the playable preview or reviewed v34. Pending v37 also remains unpromoted after its separate22858-pixel matrix-video failure.\n\n'
        'WHO DID WHAT / MODEL OUTPUT\n'
        'The coordinator authored the rebase audit, loader fixtures, image builder, startup and stack diagnostics, status renderer and publication. No cloud subagents were used. The new builder consumes the previously saved, unedited local Coder widen_biwn_loader function (16.34seconds in its earlier run), now actually used in this experimental image. No new model prediction or optimizer update occurred in this continuation. A structured local Reader prompt/schema was prepared and saved, but a nonblocking shared lease was unavailable before generation; predictions0. A lock alone does not identify a live job. No unrelated model work was inspected, unloaded or interrupted. Default Reader43 remains historical and unapproved for these new facts; native LM Studio Chat visibility and useful trained-model gain remain unverified.\n\n'
        'REBASE\n'
        'Runtime C/assembly statements match v4 exactly.48ELF relocation records change144bytes; all other bytes match. The input body and guarded entry offsets are preserved. This is explicit source/relocation inheritance, not byte-prefix identity or a replay of the old4630/20188entry tests. The copied SDK builds the rebased10580bytes identically. The former fixture address1C0000 conflicted with stream staging; the new image allocates the code below it.\n\n'
        'CONTROLLED ORIGINAL-PROVIDER STREAM MATRIX\n'
        '27paired cases on the primary CPU and27on the pinned native M68000 cover9coherent resource/heap scenarios in native, supervisor-fallback and low-headroom-fallback modes. Each matrix has9native/18fallback cases,6actual original1B044loader calls,6actual E3E0/blitter copies and6independent512-byte payload checks. Original resource, heap, targeting, camera, animation and GPU4320execute. Transport D206/D2F0/D306, data/progress and one reference-count event are supplied; DF8Cwait/DF9Csignal/DF60loader yield and boundary backends remain controlled. Native stack maximum458, fallback196; final public RAM/helper arguments/registers/flags/banks match. The primary matrix checks ordered CPU accesses; the pinned core does not observe data-bus order. These are independently original-versus-native comparisons on each core, not a direct cross-core whole-RAM digest comparison. Broader historical837upperD1differences are not waived.\n\n'
        'ACTUAL IMAGE LAYOUT / STARTUP\n'
        'The builder derives from reviewed v34, not failed v37. It relinks the54134-byte shared Deck and6060-byte outer modules at their existing code addresses against moved arenas; patches exactly7declared heap operands and the startup-finalizer jump; inserts exact v5input; and preserves inherited restoration/provider code. It uses the checked local40-byte longword copy loader plus a coordinator longword staging-clear routine. Copy132160bytes, staging clear132224bytes at0xDDD80; finalizer248bytes at0x17F078, Deckarena0x17F200, outerarena0x198600, heap0x1A1D80. Resident reservation274368bytes; initial freeheap123520. Parent CDI hash unchanged; cloned CDI stage readback matches byte-for-byte. No default or preview alias changed.\n\n'
        'Six actual startup inputs per core use three dirty resident/arena patterns and two incoming flag states. Both pinned M68000 and Unicorn execute the built image from4000to400A. An independent complete2MBRAM oracle includes code, padding, both cleared/fenced101-slot arenas, all outer pointers, staging clear and all60saved-stack bytes. All registers/SR/SSP/USP agree; input bytes remain exact. Original400A and gameframes do not execute in this test.192pinned-core heap initialization comparisons cover3register variants,2privilege modes and32flag settings; original instructions with exactly5declared floor operands changed agree in CPU and all other RAM. The new resident stays intact. Startup passes do not prove gameplay, audio, IRQs or physical-console behavior.\n\n'
        'FAILED ACTUAL-IMAGE RESOURCE CONNECTION\n'
        'The new caller comparison loads the actual stage/resident in both lanes and changes only the input callsite. The intended27-case matrix stops in the first native equipment/resource case;0paired comparisons complete. The image inherits compiled resource and heap providers as well as E3E0/E220/E098. The earlier passing loader fixtures used original resource instructions, so their458-byte bound cannot qualify this image. At PC0x1603FE (acquire_nz32), SP0x0C0966 for task0x0C0928 reaches task+62; initial SPtask+1020 gives956bytes available above the64-byte fence, while observed use is958. Protected bytes62and63 have changed fromA5to00. This is the first violation, not a completed-path maximum. The compiled acquire shim contains a512-byte private reservation beneath its guest-save area; nested input/compiler frames must be handled together. Raising a fixture limit or calling512a global bound would be invalid.\n\n'
        'The primary diagnostic saves all stack-low events and128recent instruction/SP pairs. A separate pinned-M68000 negative diagnostic runs only that native lane and matches the same first PC/SP,958bytes and every stack-low event. It confirms the failure; it does not pass27cases or establish data-bus equivalence. This image has not run fresh gameplay, and provider/alias/observer/IRQ/full-fidelity gates remain open.\n\n'
        'NEXT\n'
        'Repair private compiler-stack versus original guest-stack placement for the actual resource chain, while preserving helper entry/return context, real scheduler behavior and task boundaries. Re-prove admission against that complete chain; keep the failure as a regression case. Then qualify actual-image providers, nested geometry, alias/reentry, observers, arbitrary IRQ/error paths and fresh gameplay. Full source-only same-console CPU/GPU/DSP/audio/fidelity restoration, useful training gains, ordinary native Chat ease and future256GBhardware capacity remain incomplete.\n\n'
        'Image build: '+str(paths[4])+'\nStartup/heap: '+str(paths[5])+'\nFailed provider matrix: '+str(paths[6])+'\nStack counterexample: '+str(counter_path)+'\nPinned-core confirmation: '+str(paths[8])+'\nPrepared Reader prompt/schema: '+reader['directory']+'\nPrior unedited local Coder prompt/response: '+packet['current_input_wide_startup_progress']['transcript']+'\n')
    stream_progress = dict(status='terminal_rebased_controlled_original_stream_tests_pass',module_bytes=10580,profile='input-dispatch-native-v5-rebased',base=rebase['new_base'],entry=rebase['new_entry'],runtime_statements_changed=0,changed_ELF_relocations=48,changed_bytes=144,non_relocation_bytes_identical=True,copied_SDK_byte_identical=True,primary_paired_cases=27,second_CPU_paired_cases=27,actual_loader_calls_each=6,payload_checks_each=6,native_stack=458,fallback_stack=196,primary_ordered_bus_checked=True,second_CPU_ordered_bus_checked=False,full_real_helper_bound_proven=False,scripted_transport_wait_signal_yield_boundary_remain=True,prepared_Reader_directory=reader['directory'],prepared_Reader_predictions=0,prepared_Reader_default_promoted=False,report=str(report),reviews=[str(p)for p in paths[:4]])
    image = dict(status='built_startup_pass_resource_stack_gate_FAILED_unpromoted',profile=build['profile'],artifact_type='experimental_disc_with_confirmed_task_stack_failure',new_disc_built=True,disc=build['derived_disc'],disc_sha256=build['derived_disc_sha256'],build=str(paths[4]),startup_review=str(paths[5]),failed_provider_review=str(paths[6]),stack_diagnostic=str(paths[7]),second_CPU_confirmation=str(paths[8]),counterexample=str(counter_path),module_bytes=10580,resident_bytes=274368,copy_bytes=132160,staging_clear_bytes=132224,initial_heap_bytes=123520,native_startup_cases=6,Unicorn_startup_cases=6,heap_initialize_cases=192,completed_image_provider_pairs=0,first_violating_stack_bytes=958,available_bytes_in_failing_fixture=956,protected_task_bytes_changed=changed,first_violation_PC=counter['PC'],first_violation_SP=counter['SP'],stack_failure_confirmed_two_CPUs=True,full_path_stack_maximum_known=False,admission_reserve=512,admission_reserve_sufficient=False,default_promoted=False,installed_preview_changed=False,fresh_gameplay_verified=False,game_frames=0,physical_console_verified=False,arbitrary_IRQ_qualified=False,report=str(report))
    component = dict(status='experimental_image_input_rebased_stack_integration_FAILED',profile='input-dispatch-native-v5-rebased',artifact_type='source_component_installed_in_unpromoted_experimental_disc',module_bytes=10580,source_profile=rebase['source_profile'],payload=rebase['payload'],payload_sha256=sha(rebase['payload']),component_prefix_byte_identical=False,prior_prefix_byte_identical=False,runtime_source_statements_changed=0,checked_relocation_records=48,changed_bytes=144,copied_SDK_byte_identical=True,copied_build=rebase['copied_build'],new_disc_built=True,installed_in_experimental_image=True,installed_in_default_game=False,default_promoted=False,private_task_stack_admission_qualified=False,full_real_helper_bound_proven=False,caller_191F4_ABI_qualified=False,yielding_or_IRQ_qualified=False,arbitrary_IRQ_qualified=False,all_remaining_provider_bodies_qualified=False,fresh_gameplay_verified=False,installed_preview_changed=False,new_predictions=0,optimizer_updates=0,new_training=False,native_Chat_verified=False,report=str(report),rebase_review=str(paths[0]),controlled_stream_progress=stream_progress,experimental_image=image,historical_v4_component_proof_packet=str(out/'before-packet.json'),authorship='v4 runtime sources unchanged; coordinator relocation audit/integration. Earlier local120byte predicate and unedited Python widening helper retain their attribution.',scope='Rebase and controlled-original-provider loader checks pass; new experimental image startup passes but actual inherited resource chain violates task guard on both CPUs. No promotion or global stack bound.')
    packet['previous_native_input_component_before_rebased_image'] = previous
    packet['current_input_stream_rebase_progress'] = stream_progress
    packet['unqualified_native_input_image'] = image
    packet['current_native_input_prototype_progress'] = packet['latest_source_development'] = component
    packet['current_input_wide_startup_progress'] = dict(packet['current_input_wide_startup_progress'],historical_prototype_counts=True,installed_builders_changed=True,new_experimental_builder_uses_checked_local_helper=True,game_image_written=True,game_image_qualified=False,module_arena_heap_relink_qualified=False,current_actual_image_startup_review=str(paths[5]),current_image_stack_gate_failed=True,report=str(report))
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    packet['current_default_Reader_progress']['entry_source'] = str(ROOT/'scripts/portable_biwn_entry_v32.py')
    packet['prepared_structured_stream_Reader'] = dict(status=reader['status'],directory=reader['directory'],new_predictions=0,optimizer_updates=0,default_promoted=False,actual_schema_generation_support_tested=False)
    packet['current_status_frontend_progress'] = dict(status='status19_entry32_prepared_actual_checks_pending',renderer=str(ROOT/'scripts/show_native_status_v19.py'),portable_entry_version=32,default_brief_lines=12,new_predictions=0,detailed_report=str(report))
    packet['checked_current_summary'] = 'Reviewed gameplay remainsv34;v37matrixvideoFAIL22858pixels remains unpromoted. Inputv5rebased10580bytes/48relocations/144changedbytes,0runtime-sourcechanges,copiedSDKidentical. Controlledstreamloader27pairedcasesoneachCPUwith6load/copy/payloadchecks eachpass;458native/196fallbackstackunderoriginalproviders. Newv38experimentalCDIactualstartup6casesperCPUand192heapchecks pass;initialheap123520. Actualinheritedresourcechainfailsfirstnativecaseat958stackbytes,changesprotectedtaskbytes62/63;bothCPUsconfirm.0imageproviderpairscomplete;512admissionreserveinsufficient. No promotion,previewchange,newpredictionorweightupdate. Fullgame,IRQ,fidelity/audio,traininggain,nativeChat/futurehardwareunfinished.'
    packet['checked_answer'] = packet['checked_current_summary']
    packet['recorded_at'] = datetime.now(timezone.utc).isoformat()
    save(out/'facts.json',dict(component=component,stream=stream_progress,image=image))
    save(out/'current-status-packet.json',packet)
    deps = {str(Path(__file__)):sha(__file__),str(report):sha(report)}
    for path,receipt in zip(paths,receipts):
        deps[str(path)] = sha(path)
        deps.update(receipt.get('source_sha256',{}))
        directory = receipt.get('directory')
        if directory:
            for artifact in Path(directory).rglob('*'):
                if artifact.is_file() and '__pycache__' not in artifact.parts:
                    deps[str(artifact)] = sha(artifact)
    for name in ['show_native_status_v19.py','portable_biwn_entry_v32.py','check_native_input_image_inherited_providers_v1.py','check_native_input_image_provider_stack_diagnostic_v1.py','run_stream_rebase_structured_reader_v1.py']:
        path = ROOT/'scripts'/name
        deps[str(path)] = sha(path)
    deps.update({str(path):sha(path)for path in out.iterdir()if path.is_file()})
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py')
    deps[str(out/'before-portable_biwn.py')] = sha(out/'before-portable_biwn.py')
    for path,digest in deps.items():
        source = Path(path)
        assert source.is_relative_to(ROOT) and sha(source) == digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    clone(ROOT/'scripts/portable_biwn_entry_v32.py',P/'workbench/portable_biwn.py')
    wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps})
    atomic(wp,wrapper)
    clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    atomic(V/'input-image-stack-delivered-v1-current.json',dict(status='terminal_rebased_image_startup_and_failed_resource_stack_published',directory=str(out),report=str(report),new_predictions=0,optimizer_updates=0,new_disc_built=True,image_gate_failed=True,default_promoted=False,dependencies_sha256=deps))
    print('Published v5 rebase/stream tests and v38 startup with dual-CPU stack failure; no promotion.',flush=True)


if __name__ == '__main__':
    main()
