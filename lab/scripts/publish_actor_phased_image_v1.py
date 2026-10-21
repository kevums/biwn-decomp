"""Publish v41 finite route pass while preserving failed builds and open fidelity."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    names = ['actor-phased-v1', 'actor-phased-fixed-v2', 'actor-phased-disc-build-v1', 'actor-phased-leaf-stack-v2',
        'actor-phased-image-startup-heap-v1', 'actor-phased-copied-rebuild-v1', 'actor-phased-watch-v1',
        'actor-phased-fresh-preflight-v1', 'actor-phased-image-fresh-input-reviewed-v1', 'actor-phased-local-reviewer-v1']
    deps = {str(Path(__file__)): sha(__file__)}
    copied_inputs = {}
    receipts = {}
    def include(path, digest=None):
        p = Path(path)
        actual = sha(p)
        assert digest is None or actual == digest, p
        if p.is_relative_to(ROOT):
            deps[str(p)] = actual
        else:
            assert p.is_relative_to(P), p
            copied_inputs[str(p)] = actual
    for name in names:
        p = V / (name + '-current.json')
        receipt = read(p)
        assert receipt['status'].startswith('terminal_') and 'failed' not in receipt['status'], (name, receipt['status'])
        receipts[name] = receipt
        include(p)
        for path, digest in receipt.get('source_sha256', receipt.get('dependencies_sha256', {})).items():
            include(path, digest)
        for path in Path(receipt['directory']).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                include(path)
    b = receipts['actor-phased-disc-build-v1']
    review = receipts['actor-phased-image-fresh-input-reviewed-v1']
    reviewer = receipts['actor-phased-local-reviewer-v1']
    assert b['profile'] == 'native-actor-phased-v41-experimental'
    assert review['candidate_frames'] == 25024 and review['control_frames'] == 25011
    assert review['video_differences'] == 6950 and review['final_video_equal'] and review['final_selected_fields_equal']
    assert review['all_monitors_clear_and_quiescent'] and not review['game_fidelity_verified']
    assert reviewer['new_predictions'] == 0 and reviewer['status'] == 'terminal_shared_slot_busy_zero_predictions'
    manifest = V / 'native-Deck-current-status-v1-current.json'
    wrapper = read(manifest)
    for path, digest in wrapper['dependencies_sha256'].items():
        assert sha(path) == digest, path
    packet = read(wrapper['packet'])
    out = V / 'actor-phased-image-delivered-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out / 'before-packet.json', packet)
    report = ROOT / 'reports/BIWN v41 Phased Actors and Fresh Route Pass.txt'
    progress = dict(status='v41_phased_actor_fix_passes_finite_and_fresh_input_route_fidelity_open', profile=b['profile'],
        report=str(report), build=str(V / 'actor-phased-disc-build-v1-current.json'), disc=b['derived_disc'], disc_sha256=b['derived_disc_sha256'],
        dispatch_bytes=476, initializer_bytes=1570, dispatch_entry=0x1638c8, initializer_entry=0x163eec,
        transient_context_bytes=96, C_frames_parked_across_helpers=0, new_per_task_arena_bytes=0,
        resident_reservation=275328, copy_bytes=133120, initial_heap_bytes=122560, heap_and_all_arena_addresses_unchanged_from_v40=True,
        initializer_component_pairs=1024, joint_component_pairs=856, fixed_address_task_layout_pairs=232, task_slots=101,
        protected_fixture_task_bytes=64, physical_task_metadata_bytes=38, captured_initializer_SP_above_task=520,
        captured_dispatch_SP_above_task=556, component_initializer_maximum_stack=156, component_joint_maximum_stack=192,
        static_C_phase_bounds=dict(dispatch=136, initialize=156), static_bounds_exclude_helpers_IRQ_and_exceptions=True,
        all_global_stack_paths_proven=False, copied_new_module_builds=2,
        actual_startup_cases_each_core=6, heap_initialize_cases=192, new_gate_files=6, reused_v40_gate_files=31,
        reused_v40_gate_executions_repeated=0, reused_scope='Unchanged module bytes/layout and observer text; controlled helper limitations retained.',
        actor_observer_fault_controls=7, actor_observer_off_on_pairs=48, actor_observer_calls=14270,
        actor_observer_RAM_boundary_checks=213, actor_observer_context_scope='Original public16/32-byte save frames; no parked C contexts.',
        whole_source_only_game_rebuild=False, candidate_frames=25024, control_frames=25011,
        actor_counts=review['actor_counts'], frame_acquire_counts=review['frame_acquire_counts'], call_counts=review['call_counts'],
        all_monitors_clear_and_quiescent=True, former_actor_header_defect_fixed_in_v41=True,
        video_differences=6950, first_video_difference_frame=375, frontend_button_schedule_differences=256,
        game_latched_button_RAM_differences=252, final_video_equal=True, final_selected_fields_equal=True,
        minimum_sampled_heap_while_outer_active=review['minimum_sampled_heap_while_outer_active'], global_heap_minimum_measured=False,
        both_audio_captures_silent=True, fresh_route_qualified=True, whole_game_input_qualified=False, game_fidelity_verified=False,
        default_promoted=False, installed_preview_changed=False, new_predictions=0, optimizer_updates=0, new_training=False,
        native_Chat_verified=False, physical_console_verified=False, arbitrary_IRQ_qualified=False, new_unique_original_functions=0)
    report.write_text(
        'BIWN — v41 phased actors; fresh route passes, fidelity open\n\n'
        'RESULT\nThe formerly failing native-input candidate completes25,024frames and the original-input control25,011. Both return outdoors and complete the Deck trial. Each lane has15/15native actor dispatch returns,13/13native initializer returns,18/18initializer helper returns and124/124frame-acquire returns. All retained/scene/resource/input/actor monitors end clear and quiescent,with zero reported task-stack violations. This qualifies this finite route,not full-game input,fidelity or physical-console readiness. v34reviewed baseline,failedv37/v38/v39/v40and the Desktop preview remain unchanged. v41is unpromoted.\n\n'
        'SOURCE CHANGE\nOne readable dispatch Cphase chooses actor/sprite/complete; two initializer Cphases split initialization and callback selection around geometry. Original hardware registers carry state across helpers;96-byte transient contexts and all Cframes are released before child/geometry/task-create calls. Original16/32-byte public save frames and helper stack/arguments/flags remain. Callback is staged at publicT-8;slot atT-4,matching original callback-first helper argument order. New476/1570-byte fixed-address modules fit existing blocks and preserve publicentries1638C8/163EEC. Use actor_phased_symbols for new internal phase/return locations; historical symbols and capture metadata in the inherited build are superseded. Only1,630resident bytes differ;all other resident bytes,heap/arena/staging addresses,275328-byte reservation and122560-byte initial heap remain. No new per-task arena or unique original function is added. The algorithms were recovered earlier; this repairs their native integration.\n\n'
        'CHECKS\nPrototype and separately linked fixed-address versions each pass1024initializer and856joint original-versus-C comparisons on Unicorn and the pinned CPU,including complete CPU/SR/banks,logical helper contexts,ordered public accesses and public2MBRAM. Comparison excludes384bytes below rootSP; arguments and returnSP are checked separately. Reused fixtures at changed addresses are not unique game paths. Additional232fixed-address task-layout pairs span101slots with64guard bytes and captured entry offsets520/556. Captured parameters/registers use baseline valid geometry/providers;no live gameplay snapshot is resumed. Maximum fixture stack156initializer/192joint. Outside geometry/task leaf services remain prescribed; original inside and sprite bodies execute.\n\n'
        'CFG/SPanalysis visits every linked C-phase instruction and requires consistent joins/loops and balanced normal returns. Fixed wrapper/Cphase bounds are136dispatch/156initializer. Helpers,callers,IRQ and illegal-instruction exception handling are excluded;this is not a global stack bound. The first qualifier incorrectly expected128dispatch bytes;actual analysis found136. Source code was unchanged;the corrected qualifier is retained separately. Both changed modules rebuild byte-identically with the copied SDK. Actual v41startup passes6dirtyRAMcases perCPU with whole2MBoracles and192heap comparisons.\n\n'
        'OBSERVERS AND REUSE\nNew actor watchers protect original public save frames,helper ABI,return words and physical task bounds. Legacy context counters now describe16/32-byte public frames;parked-C-context SP counters are inapplicable. Seven decodedCPU/mirror-only fault controls are rejected.48actual actor off/on pairs cover14270CPUreadonly calls and213immediatewholeRAMboundary checks;complete final CPU/RAM/helper results agree without exclusions. Whole observer compiles. Old31finite module gates are bound by exact unchanged code/layout and identical observer text outside the two actor watchers;zero oldgate executions are repeated. Their controlled-helper/provider/selectedIRQ limits remain. The new preflight binds31reused plus6new gate files. The first observer renderer expected shared ELF files in the new build directory;correctedv2explicitly reads exact unchanged ancestor ELF metadata after checking allowed resident deltas.\n\n'
        'FIDELITY\nPaired frame-index video differs6950times,first375. The feedback frontend chooses different buttons256times;latched button RAM differs252times. Final video and selected recorded fields agree at unequal durations. These adaptive schedules do not establish original-game fidelity,causal timing improvement or same-input equivalence. Both audio captures are silent. Minimum heap sampled while the outer task is active is2800bytes in both lanes;not the global minimum. Raw video,pose,buttons,PCM,CPU/GPU/DSP/RAM state and reports remain unmodified. Control changes only the six-byte inputJSRregion at1A266;the entire disc comparison verifies no other changes. Phased actors/frame/scene/resource code remain compiled in both lanes.\n\n'
        'WHO DID WHAT / LOCAL MODEL\nCoordinator authored the source,assembly,integration,checks and review. No cloud subagents ran. One informed local Reviewer prompt included exact source and checked component facts. The shared inference lease was unavailable before model inspection or generation:zero predictions,optimizer updates or new weights. This provides no evidence of current native Chat display,easy inference or useful training gain. Exact system/user prompt,schema and evidence: '+reviewer['directory']+'\n\n'
        'NEXT\nRun identical physical-input schedules and broader indoor/native-input paths;diagnose first video divergence,silent audio and remaining device/IRQ behavior. Continue readable CPU/GPU/DSP/firmware source-only rebuilding and actual console validation. Evaluate local authorship/training and native Chat usability when its owned inference lease is available;qualify the future256GBhardware separately.\n')
    packet['current_actor_phased_image_progress'] = packet['unqualified_actor_phased_image'] = progress
    packet['latest_source_development'] = packet['current_native_input_prototype_progress'] = dict(status=progress['status'], profile=b['profile'],
        artifact_type='built_experimental_disc_finite_fresh_route_pass_fidelity_open', report=str(report), new_disc_built=True,
        fresh_gameplay_verified=True, whole_game_input_qualified=False, frame_acquire_original_defect_fixed=True,
        actor_initialize_defect_fixed=True, default_promoted=False, installed_preview_changed=False,
        actor_phased_image_progress=progress, authorship='Coordinator C/assembly/checks; no new local model response or weights.')
    packet['current_actor_phased_local_Reviewer_progress'] = reviewer
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True, current_source_reply_verified=False, current_source_factual_claims_reviewed=False)
    packet['current_default_Reader_progress']['entry_source'] = str(ROOT / 'scripts/portable_biwn_entry_v37.py')
    packet['current_status_frontend_progress'] = dict(status='status24_entry37_prepared_actual_checks_pending', renderer=str(ROOT / 'scripts/show_native_status_v24.py'), portable_entry_version=37, default_brief_lines=12, new_predictions=0, detailed_report=str(report))
    packet['checked_current_summary'] = ('v41phasedactorsrepairheaderdefect: nativeinputcandidate25024/control25011completeDeckroute; eachlaneAD15/15,AI13/13,Frame124/124,no monitor/pending/stack errors. Finite1024+856/232taskpairs101slots/copied2/startup6perCPU+192/48off-on/7faultcontrols pass. No additional arena;heap122560.6950pairedvideo differences,finalvideo/selectedfieldsagree;bothaudiosilent. Unpromoted;v34baseline/failedv37-v40/previewpreserved.0predictions/weights;fullsource-onlygame/fidelity/console/usefultraining/nativeChat/futurehardwareunfinished.')
    packet['checked_answer'] = packet['checked_current_summary']
    packet['recorded_at'] = datetime.now(timezone.utc).isoformat()
    save(out / 'facts.json', progress)
    save(out / 'current-status-packet.json', packet)
    save(out / 'copied-runtime-inputs-verified-at-publication.json', copied_inputs)
    for name in ['show_native_status_v24.py', 'portable_biwn_entry_v37.py', 'review_actor_phased_image_input_route_v1.py',
                 'shared_deck_actor_phased_image_full_observer_v1.py', 'check_actor_phased_leaf_stack_v1.py']:
        include(ROOT / 'scripts' / name)
    include(report)
    for p in out.iterdir():
        if p.is_file():
            include(p)
    for path, digest in deps.items():
        p = Path(path)
        assert sha(p) == digest
        clone(p, P / 'workbench' / p.relative_to(ROOT))
    clone(ROOT / 'scripts/portable_biwn_entry_v37.py', P / 'workbench/portable_biwn.py')
    wrapper.update(packet=str(out / 'current-status-packet.json'), dependencies_sha256={**wrapper['dependencies_sha256'], **deps})
    atomic(manifest, wrapper)
    clone(manifest, P / 'workbench/verification' / manifest.name)
    for root in [ROOT, P / 'workbench']:
        (root / 'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    atomic(V / 'actor-phased-image-delivered-v1-current.json', dict(status='terminal_v41_fresh_actor_route_pass_published_unpromoted',
        directory=str(out), report=str(report), source_sha256=deps, new_predictions=0, new_training=False))
    print('Published v41 actor fix and finite fresh route pass.', flush=True)


if __name__ == '__main__':
    main()
