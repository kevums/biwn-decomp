"""Summarize saved, completed checks for ordinary LM Studio Chat questions."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import extract_biwn_stage as stage


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    root = stage.ROOT
    folder = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    comparison_path = folder / 'emulator-runtime/boot-comparison.json'
    comparison = json.loads(comparison_path.read_text())
    runs = []
    for run in comparison['runs']:
        if run['status'] != 'terminal' or run['exit_code'] != 0:
            raise ValueError('Runtime run did not finish successfully')
        log_path = Path(run['log'])
        log = log_path.read_text()
        result = re.search(r'\[PASS\]\s+BIWN#23\.cdi : (.*final_pc=\$([0-9A-F]+))', log)
        if not result:
            raise ValueError('Missing expected game smoke result')
        runs.append({'mode': run['mode'], 'frames': run['frames'],
                     'harness_score': 'pass', 'final_sampled_CPU_PC': '0x' + result[2].lower(),
                     'log': str(log_path), 'log_sha256': stage.cdi_layout.sha(log_path)})
    if not comparison['inputs_unchanged']:
        raise ValueError('Runtime inputs changed')
    runtime = {
        'time': comparison['time'], 'emulator': 'Pinned VirtualJaguar headless core',
        'source_revision': comparison['runs'][0]['source_revision'],
        'runs': runs, 'inputs_unchanged': True,
        'BIOS_path_caveat': 'The core loaded the user-provided BIOS but also injected the game boot stub, an 0x80000 trampoline and a synthesized TOC. This is an assisted emulator boot, not an unmodified BIOS or physical-CD test.',
        'observations': 'BIOS-mode final sample is 0x180182 in the boot GPU-wait loop. HLE-mode final sample is 0x134a0 in the proposed nextstage range; exact runtime bytes have not yet been compared.',
        'scope': 'Smoke scores check coarse CPU/RAM activity. Menu, graphics, input, audio, gameplay, exact loader mapping and hardware accuracy remain unverified.',
    }
    capture_review = folder / 'emulator-runtime/capture-review.json'
    if capture_review.exists():
        review = json.loads(capture_review.read_text())
        if review['stage_SHA256'] != stage.STAGE_SHA:
            raise ValueError('Runtime review refers to a different stage')
        runtime['runtime_mapping'] = {
            'stage_bytes': review['stage_bytes'], 'interval': review['stage_interval'],
            'exact_stage_RAM_matches': len(review['exact_stage_matches']),
            'matched_mode_and_frame': [{'mode':r['mode'],'frame':r['frame_label']} for r in review['exact_stage_matches']],
            'scope': 'Exact whole-stage bytes matched in assisted BIOS-mode emulator RAM; physical hardware and unmodified BIOS remain unverified.'}
        runtime['observations'] = 'HLE captures show a character, street and HUD; scripted controller input changes the viewpoint after matching pre-input RAM/framebuffers. HLE audio is silent. BIOS-mode late framebuffer is black and CPU samples remain in the boot GPU-wait loop.'
        runtime['input_response'] = {
            'events': review['input_events'],
            'pre_input_RAM_and_framebuffer_equal': True,
            'post_input_RAM_and_framebuffer_differ': True,
            'scope': 'Short original-game emulator interaction, not reconstructed C or complete gameplay validation.'}
        runtime['capture_review'] = str(capture_review)
        runtime['scope'] = 'Short original-game assisted-emulator graphics/input observations and exact stage-byte mapping; complete gameplay, game audio, unmodified BIOS and physical hardware accuracy remain unverified.'
    pc_summary = folder / 'emulator-runtime/pc-observer-summary.json'
    if pc_summary.exists():
        observed=json.loads(pc_summary.read_text())
        runtime['CPU_PC_samples']=[{
            'run':r['name'], 'frames':r['frames_observed'],
            'static_entry_addresses_observed':len(r['static_function_entry_addresses_observed'])
        } for r in observed['runs']]
        runtime['PC_sampling_scope']='Latest1024CPU PCs after each frame, checked against candidate bytes; incomplete coverage and no proof of inferred function boundaries.'
        runtime['captured_bytes_per_sampled_PC']=observed.get('captured_bytes_per_PC',8)
    observed_export=folder/'observed-disassembly-summary.json'
    observed_calls=folder/'observed-call-entries-summary.json'
    if observed_export.exists() and observed_calls.exists():
        listing=json.loads(observed_export.read_text())
        calls=json.loads(observed_calls.read_text())
        if listing['stage_sha256']!=stage.STAGE_SHA or calls['stage_sha256']!=stage.STAGE_SHA:
            raise ValueError('Observed export has different stage provenance')
        runtime['observed_static_export']={
            'new_sampled_instruction_starts':listing['new_instructions'],
            'instructions_total':listing['instructions_total'],
            'direct_call_entry_candidates_added':calls['created'],
            'functions_total':calls['function_count'],
            'functions_decompiled':calls['decompiled_functions'],
            'sampled_matching_PCs_missing_from_listing':listing['sampled_PCs_missing_after'],
            'baseline_projects_retained_unchanged':True,
            'scope':calls['scope']+' '+listing['scope'],
            'listing_report':str(observed_export),'call_entries_report':str(observed_calls)}
    processor_review = folder/'emulator-runtime/processor-state-review.json'
    if processor_review.exists():
        processors=json.loads(processor_review.read_text())
        runtime['processor_snapshots']={
            'report':str(processor_review),
            'BIOS_first_running_low_GPU_PC_frame':439,
            'BIOS_CPU_wait_start_frame':620,
            'HLE_helper_matching_bytes':2184,
            'HLE_helper_matching_frame_interval':[177,205],
            'excluded_helper_bytes':'36 bytes overlapped by separate main GPU load and4-byte completion word',
            'HLE_nonsilent_audio_pairs':0,
            'scope':'Post-frame original-game emulator observations only. No cause established for BIOS divergence or HLE silence; no reconstructed C/hardware validation. Source reports retain all mismatches.'}
    stack_review = root/'verification/biwn-gpu-stack-test-review.json'
    if stack_review.exists():
        stack = json.loads(stack_review.read_text())
        if stack['status'] != 'reviewed_controlled_assisted_BIOS_experiment':
            raise ValueError('GPU stack experiment lacks completed coordinator review')
        runtime['controlled_GPU_stack_experiment'] = {
            'report': str(stack_review),
            'intervention': stack['intervention'],
            'baseline': stack['baseline'],
            'initialized': stack['initialized'],
            'input': stack['input'],
            'input_difference_counts': stack['input_difference_counts'],
            'pre_intervention_observations_equal': stack['pre_intervention_observations_equal'],
            'audio': stack['audio'],
            'conclusion': stack['conclusion'],
            'limits': stack['limits'],
        }
        runtime['observations'] += ' A separate controlled guest-state experiment initializes GPU bank0R31=F03FF0 before frame438 and clears the assisted BIOS stall; reviewed captures show character/street/HUD and an input-dependent viewpoint. Baseline remains unchanged and black; game-phase audio is still silent.'
    record_report = root / 'verification/biwn-record4-checks.json'
    if record_report.exists():
        record = json.loads(record_report.read_text())
        if record['original_candidate_sha256'] != stage.STAGE_SHA or record['cases'] != 192:
            raise ValueError('Record routine check has unexpected provenance or case count')
        runtime['record_routine_reconstruction'] = {
            'interval': record['original_interval'], 'CPU_differential_fixtures': record['cases'],
            'host_guard_fixtures': len(record['host_guards']),
            'scope': record['limits'], 'report': str(record_report)}
    copy_report = root / 'verification/biwn-copy-checks.json'
    if copy_report.exists():
        copy = json.loads(copy_report.read_text())
        if copy['stage_sha256'] != stage.STAGE_SHA or copy['status'] != 'copy_bytes_and_device_command_plan_matched_original_CPU':
            raise ValueError('Copy checks have unexpected provenance or status')
        runtime['copy_routine_reconstruction'] = {
            'interval': copy['original_interval'],
            'CPU_byte_copy_fixtures': copy['CPU_byte_copy_cases'],
            'device_command_trace_fixtures': copy['device_command_trace_cases'],
            'host_guard_fixtures': copy['host_guard_cases'],
            'device_behavior_emulated': False,
            'scope': copy['limits'], 'report': str(copy_report)}
    volatile_report = folder / 'shared-volatile-summary.json'
    if volatile_report.exists():
        volatile = json.loads(volatile_report.read_text())
        if volatile['stage_sha256'] != stage.STAGE_SHA or volatile['status'] != 'volatile_annotation_preserves_observed_polling_in_C':
            raise ValueError('Volatile annotation has unexpected provenance or status')
        runtime['shared_memory_polling_annotation'] = {
            'function_entry_candidate': '0xe0a6', 'volatile_interval': '[0xf03200,0xf03220)',
            'instructions_unchanged': volatile['instructions_unchanged'],
            'function_entries_unchanged': volatile['function_entries_unchanged'],
            'automatic_C_preserves': 'Five writes, repeated read at0xe0de against0x4d80, initial/final0xe098calls and return; unconditional infinite-loop simplification removed.',
            'scope': volatile['scope'], 'report': str(volatile_report)}
    command_report = root / 'verification/biwn-gpu-commands-checks.json'
    if command_report.exists():
        commands = json.loads(command_report.read_text())
        if (commands['stage_sha256'] != stage.STAGE_SHA or
                commands['status'] != 'CPU_protocol_and_portable_C_match_scripted_bus' or
                commands['completed_CPU_cases'] != 528 or commands['host_guard_cases'] != 13):
            raise ValueError('GPU command CPU checks have unexpected provenance or status')
        runtime['GPU_command_CPU_reconstruction'] = {
            'report': str(command_report), 'interval': commands['original_interval'],
            'portable_components': 3, 'CPU_fixtures': 528, 'host_guard_fixtures': 13,
            'matched': commands['matched'], 'limits': commands['excluded'],
            'critical_contract': 'Both submit routines wait F03200==0 before writes, poll F03204 until it differs from the published command, then wait F03200==0 again before returning. Nonzero unequal acknowledgements are valid.'}
    audio_review = root / 'verification/biwn-audio-path-review.json'
    if audio_review.exists():
        audio = json.loads(audio_review.read_text())
        if audio['status'] != 'coordinator_reviewed_zero_output_path' or not audio['inputs_and_core_unchanged']:
            raise ValueError('Audio path lacks a completed scoped review')
        runtime['audio_path_observations'] = {
            'report': str(audio_review), 'scope': 'Original game, frames622..900; HLE and controlled assisted-BIOS GPU-stack experiment.',
            'conclusion': audio['conclusion'], 'interpretation': audio['interpretation'],
            'runs': [{k:r[k] for k in ['name','post622_output_register_write_records',
                        'post622_nonzero_output_or_capture_frames','post622_output_ring_nonzero_frames']}
                     for r in audio['observations']],
            'limits': audio['caveats'], 'next_step': audio['next_step']}
    commands_review = root / 'verification/biwn-audio-commands-review.json'
    if commands_review.exists():
        commands = json.loads(commands_review.read_text())
        if commands['status'] != 'coordinator_reviewed_bounded_command_test':
            raise ValueError('Audio command experiment is not reviewed')
        runtime['audio_command_observations'] = commands
    startup_review = root / 'verification/biwn-dsp-startup-review.json'
    if startup_review.exists():
        startup = json.loads(startup_review.read_text())
        checked = startup['CPU_comparison']
        if (startup['candidate_sha256'] != stage.STAGE_SHA or
                startup['status'] != 'coordinator_reviewed_initial_stream_loop_and_CPU_startup' or
                checked['completed_CPU_cases'] != 96 or checked['host_guard_cases'] != 19):
            raise ValueError('DSP startup/stream evidence is not reviewed')
        runtime['DSP_startup_CPU_reconstruction'] = {
            'report': str(startup_review), 'CPU_report': str(root / 'verification/biwn-dsp-startup-checks.json'),
            'portable_components': 4, 'CPU_fixtures': 96, 'host_guard_fixtures': 19,
            'actual_payload': checked['actual_payload'], 'matched': checked['matched'], 'limits': checked['excluded']}
        runtime['initial_audio_stream_loop'] = {
            'report': str(startup_review),
            'stream_matches_original_candidate_in_all279_postframe_samples': True,
            'GPU_stream_population_at483': startup['initial_stream']['GPU_stream_population_at483'],
            'command2_static_path': startup['DSP_command2_static_path'],
            'observed_sequence_handler': startup['observed_sequence_handler'],
            'PC_occurrences_in_sampled_windows': [
                {'name': o['name'], 'counts': o['PC_occurrences_in_last1024_postframe_windows']}
                for o in startup['observations']],
            'limits': startup['limits'], 'next_step': startup['next_step']}
    long_review = root / 'verification/biwn-long-audio-review.json'
    if long_review.exists():
        long = json.loads(long_review.read_text())
        if long['status'] != 'coordinator_reviewed_long_original_game_audio_and_static_expansion':
            raise ValueError('Long exploration lacks completed review')
        runtime['long_original_game_exploration'] = {
            'report': str(long_review), 'frames_per_long_run': 9000,
            'preflight900_exact_match': long['preflight900_exact_match'],
            'observations': long['observations'], 'difference_counts': long['difference_counts'],
            'command_difference_frames': long['command_difference_frames'],
            'visual_review': long['visual_review'], 'conclusion': long['conclusion'],
            'limits': long['limits'], 'next_step': long['next_step']}
        expanded = long['static_expansion']
        runtime['observed_static_export']['historical_900frame_export'] = dict(runtime['observed_static_export'])
        runtime['observed_static_export'].update(
            instructions_total=expanded['instructions_total'], functions_total=expanded['function_count'],
            new_long_run_instruction_starts=expanded['new_instructions'],
            sampled_matching_PCs_missing_from_long_listing=expanded['stable_sampled_PCs_missing_after'],
            latest_export=expanded['final_export'], latest_long_review=str(long_review),
            scope='Latest separate project adds81stable sampled CPU instruction starts, including14bytes reclassified from data after boundary review.206entry candidates retained; no new function entries. Original bytes/instructions preserved. ApproximateC, original ABI and reconstructed-game behavior remain unverified.')
    selection_report = root / 'verification/biwn-inventory-select-checks.json'
    selection_runtime = root / 'verification/biwn-inventory-runtime-review.json'
    if selection_report.exists() and selection_runtime.exists():
        checked = json.loads(selection_report.read_text())
        observed = json.loads(selection_runtime.read_text())
        if (checked['stage_sha256'] != stage.STAGE_SHA or
                checked['status'] != 'CPU_decoder_and_selection_block_match_portable_C' or
                observed['status'] != 'coordinator_reviewed_eight_runtime_selection_write_groups'):
            raise ValueError('Input selection checks or runtime review have unexpected provenance')
        runtime['inventory_selection_CPU_reconstruction'] = {
            'report': str(selection_report), 'portable_components': 2,
            'digit_decoder_CPU_cases': checked['digit_decoder_CPU_cases'],
            'selection_block_CPU_cases': checked['selection_block_CPU_cases'],
            'host_guard_cases': checked['host_guard_cases'],
            'digit_interval': checked['digit_interval'], 'selection_interval': checked['selection_interval'],
            'matched': checked['matched'], 'limits': checked['excluded'],
            'critical_contract': 'Zero digit CLR.W retains D0upper16; source rereads retained.49D56is written only by the selection block. Block falls through1A254; selection fixtures model the redraw call. Connected CPU drawing/text/sprite protocol is checked separately below; device rasterization is unfinished.'}
        runtime['inventory_selection_runtime_consistency'] = {
            'report': str(selection_runtime),
            'all9000_prior_frame_DSP_command_catalog_capture_data_identical': observed['baseline_replay_all9000_frames_and_DSP_CSVs_catalog_captures_identical'],
            'active_groups_compared': observed['all_observed_selection_copy_writes_covered'],
            'observed_slot_changes': observed['observed_slot_changes'],
            'matched': observed['matched'], 'trace_counts': observed['trace_counts'],
            'read_data_warning': observed['source_watch_read_warning']['fact'],
            'limits': observed['limits'], 'next_step': observed['next_step']}
    draw_report = root / 'verification/biwn-inventory-draw-checks.json'
    draw_runtime = root / 'verification/biwn-inventory-draw-runtime-review.json'
    drawing_volatile = folder / 'drawing-volatile-summary.json'
    if draw_report.exists() and draw_runtime.exists() and drawing_volatile.exists():
        checked = json.loads(draw_report.read_text())
        observed = json.loads(draw_runtime.read_text())
        annotation = json.loads(drawing_volatile.read_text())
        if (checked['stage_sha256'] != stage.STAGE_SHA or checked['CPU_cases'] != 330 or
                checked['status'] != 'whole_CPU_inventory_drawing_protocol_matches_portable_C' or
                observed['status'] != 'coordinator_reviewed_original_game_inventory_drawing_write_sequences' or
                annotation['status'] != 'volatile_annotation_preserves_inventory_drawing_store_order_in_C'):
            raise ValueError('Drawing protocol lacks checked provenance or review')
        runtime['inventory_drawing_CPU_protocol_reconstruction'] = {
            'report': str(draw_report), 'portable_components': 1,
            'interval': checked['original_interval'], 'CPU_cases': checked['CPU_cases'],
            'host_guard_cases': checked['host_guard_cases'],
            'matched': checked['matched'], 'limits': checked['excluded'],
            'historical_test_uses_modeled_sprite_text_calls': True,
            'critical_contract': 'One money label before five circular rows. Background and number overlay each row; occupied rows additionally invoke sprite callback and three item labels. Negative X is sign-extended before OR packing with Y. Exact source rereads and drawing-word write order retained.'}
        runtime['inventory_drawing_runtime_write_consistency'] = {
            'report': str(draw_runtime), 'groups_compared': observed['groups_compared'],
            'CPU_long_writes': sum(x['CPU_long_writes'] for x in observed['groups']),
            'original_routine_word_write_records': observed['original_routine_word_write_records'],
            'baseline9000_frames_commands_DSP_CPU_catalog_captures_identical': observed['baseline9000_frames_commands_DSP_CPU_catalog_captures_identical'],
            'write_semantics': observed['source_watch_semantics'],
            'scope': observed['scope'], 'limits': observed['limits']}
        runtime['drawing_volatile_annotation'] = {
            'report': str(drawing_volatile), 'review': annotation['coordinator_order_review'],
            'scope': annotation['scope']}
        runtime['observed_static_export']['latest_export'] = str(Path(annotation['directory']) / 'export')
        runtime['observed_static_export']['latest_drawing_annotation_review'] = str(drawing_volatile)
    text_path = root / 'verification/biwn-text-checks.json'
    sprite_path = root / 'verification/biwn-sprite-checks.json'
    pipeline_path = root / 'verification/biwn-inventory-pipeline-checks.json'
    connected_runtime_path = root / 'verification/biwn-inventory-pipeline-runtime-review.json'
    if all(p.exists() for p in [text_path,sprite_path,pipeline_path,connected_runtime_path]):
        text = json.loads(text_path.read_text());sprite = json.loads(sprite_path.read_text())
        pipeline = json.loads(pipeline_path.read_text());observed = json.loads(connected_runtime_path.read_text())
        if (any(p['stage_sha256'] != stage.STAGE_SHA for p in [text,sprite,pipeline]) or
                text['status'] != 'full_text_CPU_helpers_match_portable_C_protocol' or
                sprite['status'] != 'whole_sprite_CPU_mailbox_protocol_matches_portable_C' or
                pipeline['status'] != 'connected_inventory_text_sprite_CPU_command_pipeline_matches_C' or
                observed['status'] != 'coordinator_reviewed_connected_inventory_and_text_original_game_write_sequences'):
            raise ValueError('Connected CPU pipeline lacks checked provenance')
        runtime['text_CPU_helpers_reconstruction'] = {
            'report':str(text_path),'portable_components':3,
            'alignment_CPU_cases':text['alignment_CPU_cases'],'text_CPU_cases':text['text_CPU_cases'],
            'host_guard_cases':text['host_guard_cases'],'matched':text['matched'],'limits':text['excluded'],
            'checked_examples':text.get('checked_examples',{})}
        runtime['sprite_mailbox_CPU_reconstruction'] = {
            'report':str(sprite_path),'portable_components':1,
            'CPU_cases':sprite['CPU_cases'],'host_guard_cases':sprite['host_guard_cases'],
            'matched':sprite['matched'],'limits':sprite['excluded'],
            'checked_examples':sprite.get('checked_examples',{})}
        runtime['connected_inventory_CPU_pipeline'] = {
            'report':str(pipeline_path),'additional_original_components':0,
            'CPU_cases':pipeline['CPU_cases'],'host_guard_cases':pipeline['host_guard_cases'],
            'CPU_sprite_and_text_helpers_reconstructed':True,
            'GPU_and_rasterization_backend_reconstructed':False,
            'matched':pipeline['matched'],'limits':pipeline['excluded'],
            'original_game_runtime':{
                'report':str(connected_runtime_path),'groups_compared':observed['groups_compared'],
                'drawing_and_text_word_records':observed['drawing_and_text_word_records'],
                'nested_text_word_records':observed['nested_text_word_records'],
                'main_drawing_word_records':observed['main_drawing_word_records'],
                'matched':observed['matched'],'limits':observed['limits']}}
    sprite_decode_path = root / 'verification/biwn-sprite-decode-checks.json'
    if sprite_decode_path.exists():
        sprite_decode = json.loads(sprite_decode_path.read_text())
        if (sprite_decode['stage_sha256'] != stage.STAGE_SHA or
                sprite_decode['status'] != 'original_GPU_sprite_overlay_and_C_decoder_match' or
                sprite_decode['GPU_cases'] != 244 or sprite_decode['actual_asset_cases'] != 61):
            raise ValueError('GPU sprite decoder lacks checked provenance')
        compact_decoder = {
            'recorded_at':sprite_decode['recorded_at'],'report':str(sprite_decode_path),
            'processor':'GPU','portable_components':1,'GPU_cases':244,
            'actual_asset_frames':61,'synthetic_cases':183,'host_guard_cases':14,
            'raw_16bit_sprite_words_reconstructed':True,
            'complete_individual_sprite_arrays_generated':sprite_decode['actual_frames_emitted_exact_declared_size'],
            'reconstructed_game_screen_frames_generated':False,
            'linked_into_inventory_pipeline':False,'whole_inventory_frame_rebuilt':False,
            'GPU_overlay_bytes':608,'CPU_source_interval':sprite_decode['overlay_source_interval'],
            'GPU_interval':sprite_decode['overlay_GPU_interval'],
            'token_lengths':sprite_decode['token_lengths'],
            'checked_examples':sprite_decode['checked_examples'],
            'matched':sprite_decode['matched'],'limits':sprite_decode['excluded'],
            'diagnostic_preview':str(root/'artifacts/decoded-sprites/sprite-silhouettes.png'),
            'preview_scope':'Complete individual sprite arrays are generated. Preview shows their nonzero16bitword silhouettes; original displaycolors and the complete inventory/game screen are not rebuilt. These61frames are spriteasset frames, not61game screen frames.'}
        runtime['GPU_sprite_decoder_reconstruction'] = compact_decoder
        # Retained under the existing compact pipeline dictionary too, so a
        # resident read-only tool process sees new evidence without new schema.
        runtime['connected_inventory_CPU_pipeline']['standalone_GPU_sprite_decoder'] = compact_decoder
    panel_path = root / 'verification/biwn-inventory-frame-checks.json'
    if panel_path.exists():
        panel_check = json.loads(panel_path.read_text())
        if (panel_check['stage_sha256'] != stage.STAGE_SHA or
                panel_check['status'] != 'reconstructed_inventory_buffer_matches_original_code_and_saved_game_capture' or
                panel_check['fast_cases'] != 300 or panel_check['accurate_cases'] != 30 or
                panel_check['actual_capture_poison_checks'] != 8):
            raise ValueError('Inventory panel lacks checked provenance')
        panel = {
            'recorded_at':panel_check['recorded_at'],'report':str(panel_path),
            'additional_original_components':0,'internal_buffer_dimensions':[96,180],
            'visible_row_count':5,'inventory_slot_count':10,
            'complete_internal_inventory_panel_rendered':True,
            'complete_game_viewport_rendered':False,'whole_game_rebuilt':False,
            'GPU_sprite_decoder_linked':True,'hardware_backend':'Pinned VirtualJaguar emulator blitter library.',
            'independent_blitter_reconstruction':False,'fast_cases':300,'accurate_cases':30,
            'original_capture_poison_checks':8,'frame_sha256':panel_check['frame_sha256'],
            'original_CPU_instructions_executed_in_rebuilt_render':0,
            'original_GPU_instructions_executed_in_rebuilt_render':0,
            'matched':panel_check['matched'],'limits':panel_check['excluded'],
            'preview_tool':'render_inventory_preview; slots1..10matchdisplaylabels, default1/money200.'}
        runtime['inventory_panel_reconstruction'] = panel
        runtime['connected_inventory_CPU_pipeline']['inventory_panel_reconstruction'] = panel
        decoder = runtime['GPU_sprite_decoder_reconstruction']
        decoder.update(linked_into_inventory_pipeline=True,whole_inventory_frame_rebuilt=True,
            inventory_frame_scope='Internal96x180panel using emulatedblitter, not completegameviewport.',
            linked_updated_at=panel_check['recorded_at'],panel_check_report=str(panel_path))
        interaction_path=root/'verification/biwn-inventory-interaction-checks.json'
        if interaction_path.exists():
            interaction=json.loads(interaction_path.read_text())
            if interaction['status']!='connected_selection_and_inventory_render_match_original_execution' or interaction['steps']!=600:
                raise ValueError('Selection/render integration lacks checked provenance')
            panel['selection_interaction']={
                'recorded_at':interaction['recorded_at'],'report':str(interaction_path),
                'steps':600,'sequences':60,'fast_steps':300,'accurate_steps':300,'redraw_steps':520,
                'original_draw_stubbed':False,'physical_controller_polled':False,
                'whole_main_loop_executed':False,'additional_original_components':0,
                'game_screen_digit_for_last_position':'0; position10/internal9',
                'preview_actions':'Optional ordered list, maximum20: cycle, digit strings0..9, none. Each call starts from supplied position.',
                'matched':interaction['matched'],'limits':interaction['limits']}
    world_path=root/'verification/biwn-world-update-checks.json'
    if world_path.exists():
        world=json.loads(world_path.read_text())
        if world['CPU_cases']!=1024 or world['covered_caller_instructions']!=239 or world['uncovered_instructions']:
            raise ValueError('CPU update caller lacks checked provenance')
        runtime['world_update_CPU_caller_reconstruction']={
            'recorded_at':world['recorded_at'],'report':str(world_path),'interval':world['interval'],
            'CPU_cases':1024,'host_guards':20,'covered_caller_instructions':239,'total_caller_instructions':239,
            'additional_original_components':0,'component_scope':world['component_scope'],
            'dependencies_scripted':True,'GPU_movement_helper_reconstructed':False,
            'full_scene_reconstructed':False,'full_main_loop_reconstructed':False,'whole_game_rebuilt':False,
            'facts':['Signed clock-difference clamp limits only values greater than30; negative differences remain negative.',
                     'Fraction fields use14bits. 0x3fff+1 yields one integer carry and zero remainder.',
                     'Primary position widths are32,16,32bits; secondary position widths are16,16,16bits, all wrap at their stored width.',
                     'Collision low-word result0 restores saved primary positions/fractions;1 advances secondary positions;other nonzero values retain primary state without advancing secondary positions.',
                     'Integer delta words clear in Z/Y/X analyst order. Camera helper F0FA return sign sets status-1or1; a changed status sets a flag. The earlier terrain label was incorrect.'],
            'matched':world['matched'],'limits':world['limits'],'analyst_naming':world.get('analyst_naming','Analyst symbols, not original source names.')}
    movement_path=root/'verification/biwn-movement-matrix-checks.json'
    movement_submit_path=root/'verification/biwn-movement-submit-checks.json'
    movement_pipeline_path=root/'verification/biwn-world-movement-pipeline-checks.json'
    if movement_path.exists() and movement_submit_path.exists() and movement_pipeline_path.exists():
        movement=json.loads(movement_path.read_text());submit=json.loads(movement_submit_path.read_text());linked=json.loads(movement_pipeline_path.read_text())
        if movement['GPU_cases']!=1025 or submit['CPU_cases']!=256 or linked['cases']!=256:
            raise ValueError('Movement components lack checked provenance')
        examples=json.loads((root/'verification/movement-matrix-checked-examples.json').read_text())
        runtime['GPU_movement_matrix_reconstruction']={
            'recorded_at':movement['recorded_at'],'report':str(movement_path),'processor':'GPU','overlay_bytes':1016,
            'GPU_cases':1025,'host_guards':10,'single_axis_angle_cases':768,'mixed_cases':256,'snapshot_argument_cases':1,
            'code_instructions':353,'direct_PC_instructions':345,'mandatory_delay_instructions':8,'coverage_method':movement['coverage_method'],
            'rotation_order':['angle2','angle1','angle3'],'sine_table_entries':65,'angle_semantics':'low8 bits, full32bit nonzero branch test',
            'speed_semantics':'signed low16','rotation_rounding_bias':8192,'translation_rounding_bias':0,
            'fixed_point_fraction_bits':14,'stored_raw_fraction_bits':16,
            'identity_speed_minus1_zero_translation':{'integer_Z_word':65535,'integer_Z_signed':-1,'raw_Z_fraction_word':49152,'raw_Z_fraction_hex':'0xc000','caller_masked_Z_fraction':0,'original_GPU_and_C_checked':True},
            'checked_examples':examples['examples'],'matched':movement['matched'],'isolated_limits':movement['limits'],
            'linked_into_CPU_caller':True,'full_scene_reconstructed':False,'whole_game_rebuilt':False}
        runtime['CPU_movement_submit_reconstruction']={'recorded_at':submit['recorded_at'],'report':str(movement_submit_path),'CPU_cases':256,'host_guards':9,'interval':submit['interval'],'command':'0x4320','argument_count':5,'acknowledgement':'Any value unequal to4320, then idle exactly zero.','host_status_not_original_D0':True}
        pipeline={'recorded_at':linked['recorded_at'],'report':str(movement_pipeline_path),'cases':256,'redraw_cases':166,
            'CPU_movement_helper_linked':True,'GPU_movement_algorithm_linked':True,'inventory_pipeline_linked':True,
            'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'complete_game_frames_executed':0,
            'remaining_scripted_helper_targets':linked['remaining_scripted_helper_targets'],'matched':linked['matched'],'limits':linked['limits'],
            'full_scene_reconstructed':False,'full_main_loop_reconstructed':False,'whole_game_rebuilt':False}
        runtime['connected_world_movement_pipeline']=pipeline
        world=runtime['world_update_CPU_caller_reconstruction']
        world.update(GPU_movement_helper_reconstructed=True,CPU_movement_helper_reconstructed=True,linked_movement_pipeline=pipeline,
            latest_linked_update=linked['recorded_at'],remaining_scripted_helper_targets=linked['remaining_scripted_helper_targets'],
            isolated_caller_fixture_limits=world['limits'],current_limits=linked['limits'])
    boundary_path=root/'verification/biwn-boundary-handlers-checks.json'
    boundary_pipeline_path=root/'verification/biwn-world-boundary-pipeline-checks.json'
    if boundary_path.exists() and boundary_pipeline_path.exists():
        boundary=json.loads(boundary_path.read_text());linked=json.loads(boundary_pipeline_path.read_text())
        if boundary['CPU_cases']!=1450 or boundary['covered_CPU_instructions']!=135 or linked['cases']!=256:
            raise ValueError('Boundary handlers lack checked provenance')
        examples=json.loads((root/'verification/boundary-checked-examples.json').read_text())
        runtime['CPU_boundary_handlers_reconstruction']={
            'recorded_at':boundary['recorded_at'],'report':str(boundary_path),'CPU_cases':1450,
            'type1_cases':970,'type2_cases':480,'host_guards':23,'CPU_instruction_coverage':[135,135],
            'interval':boundary['original_interval'],'bytes':460,'portable_components':2,
            'nested_dependency_targets':boundary['remaining_dependencies'],'full_collision_geometry_reconstructed':False,
            'full_D0_checked':True,'caller_uses_only_low16':True,
            'checked_examples':{
                'unsupported_edge_2345_incoming_abcd1234':{'full_D0_hex':'0xabcd0000','low_word':0},
                'neighbor_after_failed_geometry':{'initial':10,'delta':5,'helper_sets_current':100,'helper_returns_D0_hex':'0x12340000','after_subtract':95,'full_D0_hex':'0x12340000'},
                'matching_negative_flags_9000_calls_target_helper':True,
                'signed_index_fffe_byte_offset':-12,
                'scan_crossing_9fffc_to_a0002_zero_flags_D0_hex':'0x90000',
                'source_report':str(root/'verification/boundary-checked-examples.json')},
            'facts':['Type1FFFF tentatively adds signed-word delta, then on zero lowword geometry result rereads the current neighborword and subtracts delta; it does not restore a cached value.',
                     'CLR.W preserves upper16D0. A zero lowword can coexist with nonzero fullD0.',
                     'Type2 uses signed16 coordinate differences before ASR6; signed16 table index times6; sixbyte records.',
                     'Negative record flags terminate only after key mismatch. Matching flags0x9000 still contain0x1000 and can invoke the target helper.',
                     'Index and target fields are deliberately reread. A scan crossing64k preserves the initial entry-pointer upperhalf in zero-return D0 paths.'],
            'matched':boundary['matched'],'limits':boundary['limits']}
        pipeline={'recorded_at':linked['recorded_at'],'report':str(boundary_pipeline_path),'cases':256,
            'type1_handler_calls':49,'type2_handler_calls':62,'redraw_cases':166,
            'CPU_boundary_handlers_linked':True,'CPU_GPU_movement_linked':True,'inventory_linked':True,
            'remaining_top_level_scripted_helpers':linked['remaining_top_level_scripted_helpers'],
            'remaining_nested_dependency_targets':linked['remaining_nested_dependency_targets'],
            'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'complete_game_frames_executed':0,
            'full_collision_geometry_reconstructed':False,'whole_game_rebuilt':False,
            'matched':linked['matched'],'limits':linked['limits']}
        runtime['connected_world_boundary_pipeline']=pipeline
        world=runtime['world_update_CPU_caller_reconstruction']
        world.update(CPU_boundary_helpers_reconstructed=True,current_linked_pipeline=pipeline,
            latest_linked_update=linked['recorded_at'],remaining_scripted_helper_targets=linked['remaining_top_level_scripted_helpers'],
            remaining_nested_dependency_targets=linked['remaining_nested_dependency_targets'],current_limits=linked['limits'])
    geometry_path=root/'verification/biwn-geometry-checks.json'
    geometry_pipeline_path=root/'verification/biwn-world-geometry-pipeline-checks.json'
    if geometry_path.exists() and geometry_pipeline_path.exists():
        geometry=json.loads(geometry_path.read_text());linked=json.loads(geometry_pipeline_path.read_text())
        if geometry['CPU_cases']!=1216 or geometry['CPU_instruction_coverage']!=[245,245] or linked['cases']!=256:
            raise ValueError('Geometry functions lack checked provenance')
        runtime['CPU_geometry_reconstruction']={
            'recorded_at':geometry['recorded_at'],'report':str(geometry_path),'CPU_cases':1216,
            'entry_cases':geometry['entry_cases'],'host_guards':23,'CPU_instruction_coverage':[245,245],
            'portable_components':5,'original_bytes':772,'nested_helper_calls':0,'full_D0_checked':True,
            'implemented':['0x1028e outside-bounds predicate','0x102c4 reverse tile search','0x1039c tile selection','0x10430 portal selection','0x10652 region selection'],
            'facts':['Bounds are signed and half-open: lower<=position<upper. The first three failed bounds return fullD0=1; the final Z-upper test preserves incomingD0 upper16 and returns lowword0or1.',
                     'Tile records are20bytes, portal records28bytes and region records24bytes. Tile/region shifts truncate to16bits before sign extension; portal shifts sign-extend16 first and then shift32.',
                     'Signed negative tile/region indexes are not clamped when the original signed index<count comparison accepts them. Tile lookup scans backwards with DBRA word semantics.',
                     'Room directory entries are at0x49bb4+signextendedRoom*4. Tile-table pointer is container+8; region-table pointer is header+4. Earlier automatic decompiler field offsets were inaccurate.',
                     'Portal direction matching uses signed bytes; byte128 cannot match an ASR6-and15 key. All declared position, origin, bounds, index and target rereads are preserved.'],
            'examples':{'inside_incoming_abcd1234':'0xabcd0000','late_Z_upper_outside_incoming_abcd1234':'0xabcd0001','early_X_outside_incoming_abcd1234':'0x00000001','record_word_0x0400_shift6_tile_or_region_signed':0,'record_word_0x0400_shift6_portal_signed':65536},
            'matched':geometry['matched'],'standalone_limits':geometry['limits'],
            'linked_into_current_pipeline':True,'full_collision_geometry_reconstructed':False,'whole_game_rebuilt':False}
        pipeline={'recorded_at':linked['recorded_at'],'report':str(geometry_pipeline_path),'cases':256,
            'geometry_function_calls':linked['geometry_function_calls'],'type1_handler_calls':linked['type1_calls'],'type2_handler_calls':linked['type2_calls'],'redraw_cases':166,
            'CPU_geometry_helpers_linked':True,'CPU_boundary_handlers_linked':True,'CPU_GPU_movement_linked':True,'inventory_linked':True,
            'remaining_top_level_scripted_helpers':linked['remaining_top_level_scripted_helpers'],
            'remaining_nested_dependency_targets':linked['remaining_nested_transition_helpers'],
            'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'complete_game_frames_executed':0,
            'full_collision_geometry_reconstructed':False,'whole_game_rebuilt':False,'matched':linked['matched'],'limits':linked['limits']}
        runtime['connected_world_geometry_pipeline']=pipeline
        world=runtime['world_update_CPU_caller_reconstruction']
        world.update(CPU_geometry_helpers_reconstructed=True,current_linked_pipeline=pipeline,
            latest_linked_update=linked['recorded_at'],remaining_scripted_helper_targets=linked['remaining_top_level_scripted_helpers'],
            remaining_nested_dependency_targets=linked['remaining_nested_transition_helpers'],current_limits=linked['limits'])
    cleanup_path=root/'verification/biwn-transition-cleanup-checks.json'
    cleanup_pipeline_path=root/'verification/biwn-world-cleanup-pipeline-checks.json'
    if cleanup_path.exists()and cleanup_pipeline_path.exists():
        cleanup=json.loads(cleanup_path.read_text());linked=json.loads(cleanup_pipeline_path.read_text())
        if cleanup['CPU_cases']!=556 or cleanup['CPU_instruction_coverage']!=[226,226]or linked['cases']!=256:
            raise ValueError('Cleanup functions lack checked provenance')
        examples=json.loads((root/'verification/cleanup-local-roles-current.json').read_text())
        examples_path=Path(examples['directory'])/'original-examples.json';expected=json.loads(examples_path.read_text())['expected']
        runtime['CPU_transition_cleanup_reconstruction']={
            'recorded_at':cleanup['recorded_at'],'report':str(cleanup_path),'CPU_cases':556,'entry_cases':cleanup['entry_cases'],
            'host_guards':33,'CPU_instruction_coverage':[226,226],'portable_components':6,'original_bytes':700,'nested_helper_stubs':0,'full_D0_checked':True,
            'implemented':['0x1545c free handle/list insertion/coalescing','0x1ae56 release texture reference','0x20cc4 release room references','0x20e40 release region references','0x20e8c reset rooms/objects','0x20f0c reset region/objects'],
            'facts':['Reference release stops at the first matching ID even when its count is zero; a later duplicate is untouched. Any nonzero count, including0xffff, decrements with16bit wrap.',
                     'Room release uses signed count comparisons and rereads the count and table pointer. Region release uses signed index*6, cached signed group count and six consecutive IDs per group; each baseID is reread.',
                     'Reset rooms visits25 directory entries, then writes word1 to40 records at206byte stride and clears40 object-active words at30byte stride. Reset region releases the current region before the same40object reset.',
                     'A nonzero object-active word triggers a handle test and handle reread before free. Free accepts a pointer to a handle; null pointer or zero payload is skipped. The handle is cleared after insertion.',
                     'Free increments the32bit free-byte counter modulo2^32, inserts by unsigned address order, and merges adjacent left/right/both neighbors. Head/next/size/handle rereads are preserved. It is not an allocator allocation implementation.'],
            'original_CPU_checked_examples':expected,'examples_report':str(examples_path),
            'matched':cleanup['matched'],'standalone_limits':cleanup['limits'],'linked_into_current_pipeline':True,'whole_game_rebuilt':False}
        pipeline={'recorded_at':linked['recorded_at'],'report':str(cleanup_pipeline_path),'cases':256,
            'original_cleanup_function_entries':linked['original_cleanup_function_entries'],'geometry_function_calls':linked['geometry_function_calls'],
            'type1_handler_calls':linked['type1_calls'],'type2_handler_calls':linked['type2_calls'],'redraw_cases':linked['redraw_cases'],
            'CPU_cleanup_helpers_linked':True,'CPU_geometry_helpers_linked':True,'CPU_boundary_handlers_linked':True,'CPU_GPU_movement_linked':True,'inventory_linked':True,
            'remaining_top_level_scripted_helpers':linked['remaining_top_level_scripted_helpers'],'remaining_nested_dependency_targets':linked['remaining_nested_transition_helpers'],
            'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'complete_game_frames_executed':0,'full_collision_geometry_reconstructed':False,'whole_game_rebuilt':False,'matched':linked['matched'],'limits':linked['limits']}
        runtime['connected_world_cleanup_pipeline']=pipeline
        world=runtime['world_update_CPU_caller_reconstruction']
        world.update(CPU_cleanup_helpers_reconstructed=True,current_linked_pipeline=pipeline,latest_linked_update=linked['recorded_at'],
            remaining_scripted_helper_targets=linked['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=linked['remaining_nested_transition_helpers'],current_limits=linked['limits'])
    scheduler_path=root/'verification/biwn-scheduler-checks.json'
    if scheduler_path.exists():
        scheduler=json.loads(scheduler_path.read_text())
        if scheduler['native_CPU_cases']!=512 or scheduler['CPU_instruction_coverage']!=[26,26]or not scheduler['original_TRAP_and_RTE_executed']:
            raise ValueError('Scheduler lacks native control-flow provenance')
        runtime['CPU_scheduler_reconstruction']={
            'recorded_at':scheduler['recorded_at'],'report':str(scheduler_path),'native_CPU_cases':512,
            'handler_cases':256,'yield_cases':256,'Unicorn_pre_RTE_bus_cases':256,'host_guards':18,
            'different_context_cases':scheduler['different_context_cases'],'fresh_task_entry_cases':scheduler['fresh_task_entry_cases'],'high_bit_deadline_read_cases':scheduler['high_bit_deadline_read_cases'],
            'CPU_instruction_coverage':[26,26],'portable_components':2,'original_bytes':96,'helper_stubs':0,
            'implemented':['0xde08 scheduler exception handler through originalRTE','0xdf60 yield wrapper through originalTRAP/MOVEM/RTS'],
            'full_CPU_continuation_checked':True,'linked_into_current_world_pipeline':False,
            'checked_deadline_example':json.loads((root/'verification/scheduler-checked-example.json').read_text()),
            'facts':['The service stores the current user stack, saved returnPC and savedSR in the current context, then follows the next-context link before testing readiness.',
                     'Any nonzero long at context+0x1a or+0x22 causes a skip. A nonzero deadline at+0x16 is reread, compared unsigned with clock0x778cc and cleared when deadline<=clock.',
                     'Deadline zero bypasses the clock read and leaves D0 unchanged. D0 retains a previous nonzero deadline even if a later zero-deadline context is selected.',
                     'The chosen context restores itsPC,SR andUSP. Yield saves11callee-saved registers (D2-D7/A2-A6). A warm yield continuation restores the selected task\'s saved registers and return address; a fresh entry transfers directly to its selectedPC.',
                     'It can resume a different task, so a host caller must honor the returned continuation. A plain immediate-return replacement would not model general task switching.'],
            'native_state_checked':['D0-D7','A0-A7','PC','SR bits0x271f','normalizedUSP','normalizedSSP','all2MBRAM'],
            'matched':scheduler['matched'],'limits':scheduler['limits'],'primary_architecture_reference':scheduler['primary_architecture_reference'],
            'current_world_yield_boundary_still_scripted':True,'whole_game_rebuilt':False}
        runtime['world_update_CPU_caller_reconstruction'].update(CPU_scheduler_standalone_reconstructed=True,CPU_scheduler_linked=False)
    task_runtime_path=root/'verification/biwn-task-runtime-checks.json'
    if task_runtime_path.exists():
        tasks=json.loads(task_runtime_path.read_text());guards=json.loads((root/'verification/task-loop-host-guards.json').read_text())
        if tasks['cases']!=256 or tasks['world_update_calls']!=512 or tasks['task_handoffs']!=1572 or tasks['task_loop_CPU_instruction_coverage']!=[7,7]or len(guards['guards'])!=14:
            raise ValueError('Task runtime lacks connected execution provenance')
        pipeline={'recorded_at':tasks['recorded_at'],'report':str(task_runtime_path),'cases':256,'world_update_calls':512,'task_handoffs':1572,
            'world_inner_yields':12,'redraw_cases':tasks['inventory_redraw_calls'],'redraw_count_scope':'332redrawcalls across512updates, not332fixturecases',
            'task_entries':tasks['task_entries'],'task_contexts':tasks['task_contexts'],'implemented_task_bodies':3,'captured_task_bodies':21,'other_task_bodies_unported':18,
            'task_loop_CPU_instruction_coverage':[7,7],'task_loop_original_bytes':30,'new_original_components':3,'host_guards':14,
            'CPU_scheduler_linked_for_three_task_subset':True,'inner_world_yield_is_immediate_stub':False,'CPU_GPU_movement_linked':True,'inventory_linked':True,
            'remaining_top_level_scripted_helpers':tasks['remaining_top_level_scripted_helpers'],'remaining_nested_dependency_targets':tasks['remaining_nested_scripted_helpers'],
            'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'complete_game_frames_executed':0,'whole_game_rebuilt':False,
            'full_task_ring_reconstructed':False,'matched':tasks['matched'],'limits':tasks['limits']}
        runtime['connected_three_task_runtime']=pipeline
        world=runtime['world_update_CPU_caller_reconstruction'];world.update(CPU_scheduler_linked=True,task_runtime_subset=[3,21],current_linked_pipeline=pipeline,
            latest_linked_update=tasks['recorded_at'],remaining_scripted_helper_targets=tasks['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=tasks['remaining_nested_scripted_helpers'],current_limits=tasks['limits'])
        scheduler=runtime['CPU_scheduler_reconstruction'];scheduler.update(linked_into_current_world_pipeline=True,
            linked_scope='Three actual task bodies:world1A544 andyield-onlyF360/F880.18othercapturedtasksunported;notfulltaskring/game.',
            current_world_yield_boundary_still_scripted=False,current_task_runtime=pipeline)
        scheduler['standalone_limits_at_that_checkpoint']=scheduler.pop('limits')
        scheduler['current_limits']=tasks['limits']
    input_path=root/'verification/biwn-input-poll-checks.json'
    input_runtime_path=root/'verification/biwn-task-input-runtime-checks.json'
    if input_path.exists()and input_runtime_path.exists():
        polling=json.loads(input_path.read_text());linked=json.loads(input_runtime_path.read_text());pad=json.loads((root/'verification/emulated-pad-mapping.json').read_text())
        if polling['CPU_cases']!=1024 or polling['CPU_instruction_coverage']!=[32,32]or linked['input_poll_calls']!=584 or linked['raw_MMIO_reads']!=2336 or pad['native_CPU_cases']!=132:
            raise ValueError('Input polling lacks original execution provenance')
        runtime['CPU_input_poll_reconstruction']={
            'recorded_at':polling['recorded_at'],'report':str(input_path),'CPU_cases':1024,'CPU_instruction_coverage':[32,32],
            'host_guards':15,'portable_components':1,'original_bytes':124,'original_interval':polling['interval'],
            'original_D0_D7_A0_A6_preserved':True,'host_status_separate_from_original_D0':True,'row_select_words':polling['row_select_words'],
            'raw_MMIO_possible_output_mask':'0x33ff33ff','ordinary_emulated_port0_output_mask':'0x32ff22ff','native_emulated_pad_cases':132,'emulated_button_count':21,
            'checked_press_hold_release_repress':pad['press_hold_release_repress_sequence'],
            'facts':['Four ordered word-select/long-read pairs atF14000 feed the original ORmask/rotates/AND/complement calculation. Current held state is stored at49BA4.',
                     'Newpressedges=(previousheld XOR currentheld)ANDcurrentheld. Holding the same button produces no second newpress edge; release produces no press edge; repress produces a new edge.',
                     'Native/C emulatedpause press/hold/release/repress checks give pressedges10000000,0,0,10000000. These are observations of the pinned emulator pad model, not physicalpad validation.',
                     'Original CPU preserves every D0-D7/A0-A6 register. The C return is a host status, not the original D0 value.',
                     'Clock and externalbuttonstate samples are supplied by the test environment at poll boundaries. The polling function itself does not implement a clock/timer.'],
            'matched':polling['matched'],'standalone_limits_at_that_checkpoint':polling['limits'],'linked_into_current_three_task_runtime':True,
            'physical_pad_validation':False,'implementation_origin':'Coordinator-authored C retained; local Author/Reviewer/guided Remediator drafts all rejected.',
            'local_drafting_audit':str(root/'verification/local-input-author-audit.json')}
        pipeline=dict(runtime['connected_three_task_runtime']);pipeline.update(recorded_at=linked['recorded_at'],report=str(input_runtime_path),
            redraw_cases=linked['inventory_redraw_calls'],redraw_count_scope='150redrawcalls across512worldupdates using real held/edge polling; historical scripted-input run had332redrawcalls.',
            input_poll_linked=True,input_poll_calls=584,raw_MMIO_reads=2336,input_poll_original_components=1,additional_original_components=0,
            remaining_top_level_scripted_helpers=linked['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],matched=linked['matched'],limits=linked['limits'])
        runtime['connected_three_task_input_runtime']=pipeline
        world=runtime['world_update_CPU_caller_reconstruction'];world.update(CPU_input_poll_reconstructed=True,current_linked_pipeline=pipeline,
            latest_linked_update=linked['recorded_at'],remaining_scripted_helper_targets=linked['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],current_limits=linked['limits'])
        runtime['CPU_scheduler_reconstruction'].update(current_task_runtime=pipeline,current_limits=linked['limits'])
    dispatch_path=root/'verification/biwn-input-dispatch-checks.json'
    if dispatch_path.exists():
        dispatch=json.loads(dispatch_path.read_text())
        if dispatch['CPU_cases']!=1890 or dispatch['CPU_instruction_coverage']!=[816,816]or dispatch['host_guards']!=38:
            raise ValueError('Input dispatcher lacks complete standalone execution provenance')
        runtime['CPU_input_dispatch_reconstruction']={
            'recorded_at':dispatch['recorded_at'],'report':str(dispatch_path),'CPU_cases':1890,'CPU_instruction_coverage':[816,816],
            'host_guards':38,'portable_components':1,'original_bytes':3384,'jump_table_bytes':26,'state_count':13,
            'original_interval':dispatch['interval'],'helper_targets':dispatch['helper_targets'],
            'checked_examples':json.loads((root/'verification/input-dispatch-checked-examples.json').read_text()),
            'matched':dispatch['matched'],'limits':dispatch['limits'],'linked_into_current_three_task_runtime':False,
            'standalone_nested_helper_targets_scripted':19,'complete_game_frames_executed':0,
            'implementation_origin':'Codex coordinator authored C; original M68000 execution is the independent comparison oracle. No local code draft or new weight training in this dispatcher checkpoint.',
            'next_work':'Connect the dispatcher to the existing three-task runtime, including its new internal yield points and explicit equipment/scene dependencies. Reconstruct remaining terrain/scene/entity/texture services,18othercapturedtasks and other game code. Full goal incomplete.'}
        runtime['world_update_CPU_caller_reconstruction']['CPU_input_dispatch_standalone_reconstructed']=True
        runtime['world_update_CPU_caller_reconstruction']['CPU_input_dispatch_linked']=False
    division_path=root/'verification/biwn-signed-division-checks.json'
    dispatch_runtime_path=root/'verification/biwn-task-dispatch-runtime-checks.json'
    if division_path.exists()and dispatch_runtime_path.exists():
        division=json.loads(division_path.read_text());linked=json.loads(dispatch_runtime_path.read_text())
        if division['CPU_cases']!=2048 or division['normal_return_instruction_coverage']!=[48,48]or linked['cases']!=256 or linked['dispatcher_animation_wait_yields']!=35 or linked['inventory_redraw_calls']!=56:
            raise ValueError('Connected dispatcher/division lacks terminal execution provenance')
        runtime['CPU_signed_division_reconstruction']={
            'recorded_at':division['recorded_at'],'report':str(division_path),'CPU_cases':2048,'CPU_instruction_coverage':[48,50],
            'normal_return_instruction_coverage':[48,48],'excluded_zero_divisor_exception_instructions':division['excluded_zero_divisor_exception_instructions'],
            'host_guards':5,'portable_components':1,'original_bytes':130,'interval':division['interval'],
            'facts':['For nonzero signed32divisors, quotient truncates towardzero and remainder has the numerator sign. Outputs are raw32bit two-complement values.',
                     'INT_MIN/-1 gives rawquotient80000000/remainder0. Zero division returns added hosterror withoutoutputmutation; original exception path is excluded.',
                     'Signed division is now linked in the connected three-task dispatcher test, with59actualcalls, rather than scripted as in the earlier standalone dispatcher check.'],
            'matched':division['matched'],'standalone_limits_at_that_checkpoint':division['limits'],'linked_into_current_three_task_runtime':True,'connected_calls':linked['signed_division_calls']}
        pipeline=dict(runtime['connected_three_task_input_runtime']);pipeline.update(recorded_at=linked['recorded_at'],report=str(dispatch_runtime_path),
            world_update_calls=linked['world_update_calls'],task_handoffs=linked['task_handoffs'],world_inner_yields=linked['world_inner_yields'],
            redraw_cases=linked['inventory_redraw_calls'],redraw_count_scope='56redrawcalls across512updates with new state/input/equipment/selection fixtures; earlier input-only fixtures had150redrawcalls. Different inputs, not a performance regression comparison.',
            input_poll_calls=linked['input_poll_calls'],raw_MMIO_reads=linked['raw_MMIO_reads'],input_dispatch_linked=True,signed_division_linked=True,
            input_dispatch_calls=linked['input_dispatch_calls'],signed_division_calls=linked['signed_division_calls'],
            dispatcher_animation_wait_yields=linked['dispatcher_animation_wait_yields'],dispatcher_wait_return_PCs=linked['dispatcher_wait_return_PCs'],
            dispatcher_states_observed=linked['dispatcher_states_observed'],original_dispatcher_instruction_coverage=linked['original_dispatcher_instruction_coverage'],
            remaining_top_level_scripted_helpers=linked['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],
            matched=linked['matched'],limits=linked['limits'])
        runtime['connected_three_task_dispatch_runtime']=pipeline
        dispatch=runtime['CPU_input_dispatch_reconstruction'];dispatch.update(linked_into_current_three_task_runtime=True,current_connected_runtime=pipeline,
            signed_division_current=runtime['CPU_signed_division_reconstruction'],current_limits=linked['limits'],
            next_work='Reconstruct the remaining terrain/scene/entity/allocator/equipment/texture services and18othercapturedtaskbodies plus other gamecode. Expand mainloop/scenes/audio and make the C path easier to run. Full goal incomplete.')
        dispatch['standalone_limits_at_that_checkpoint']=dispatch.pop('limits')
        runtime['world_update_CPU_caller_reconstruction'].update(CPU_input_dispatch_linked=True,current_linked_pipeline=pipeline,
            latest_linked_update=linked['recorded_at'],remaining_scripted_helper_targets=linked['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],current_limits=linked['limits'])
        runtime['CPU_scheduler_reconstruction'].update(current_task_runtime=pipeline,current_limits=linked['limits'])
    camera_path=root/'verification/biwn-camera-checks.json'
    camera_runtime_path=root/'verification/biwn-task-camera-runtime-checks.json'
    if camera_path.exists()and camera_runtime_path.exists():
        camera=json.loads(camera_path.read_text());linked=json.loads(camera_runtime_path.read_text())
        if camera['CPU_cases']!=3840 or camera['reachable_instruction_coverage']!=[234,234]or linked['camera_calls']!=512 or linked['multiply_calls']!=1936 or linked['direction_calls']!=512:
            raise ValueError('Camera integration lacks terminal comparison provenance')
        runtime['CPU_camera_reconstruction']={
            'recorded_at':camera['recorded_at'],'report':str(camera_path),'CPU_cases':3840,'camera_cases':768,'multiply_cases':2048,'direction_cases':1024,
            'CPU_instruction_coverage':[234,235],'reachable_instruction_coverage':[234,234],'unreachable_instructions':['0x134be'],'unreachable_basis':camera['unreachable_basis'],
            'host_guards':23,'portable_components':3,'original_bytes':840,'intervals':camera['intervals'],
            'facts':['F0FA updates camera offsets/angles, submits movement at matrixbase47B88 and returns the final sharedlong3C846. The earlier terrain-query label was incorrect.',
                     'Normal tracking writes a temporary counter-derived long to3C846, then overwrites it with27; finalreturn rereads sharedmemory after movement. Debug mode keeps the prior sharedvalue, so return is not unconditionally27.',
                     'Debug mode consumes lowword incomingD2/D3; world adapter supplies previousstatus/boundarydecision as explicit register seeds, not originalstackarguments.',
                     'Three routines:cameraF0FA,multiplyE540,direction13440. Multiply wraps32bits; direction scans the original64long thresholdtable and has signedword/quadrant edge behavior, not an assumed libraryatan2.',
                     'Direction fallbackBRA134BE is unreachable because D3 is assigned1..4 on every path and the checked division helper preservesD3. Reachablecoverage234/234; totaldecoded235.'],
            'checked_examples':json.loads((root/'verification/camera-checked-examples.json').read_text()),'matched':camera['matched'],
            'standalone_limits_at_that_checkpoint':camera['limits'],'linked_into_current_three_task_runtime':True,'physical_hardware_validation':False,
            'implementation_origin':'Codex coordinator authored C and register-seed adapter; no new local code-author roles or weight training in this checkpoint.'}
        pipeline=dict(runtime['connected_three_task_dispatch_runtime']);pipeline.update(recorded_at=linked['recorded_at'],report=str(camera_runtime_path),
            camera_linked=True,multiply_linked=True,direction_linked=True,camera_calls=512,multiply_calls=1936,direction_calls=512,
            signed_division_calls=linked['signed_division_calls'],original_camera_instruction_coverage=linked['original_camera_instruction_coverage'],
            remaining_top_level_scripted_helpers=linked['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],matched=linked['matched'],limits=linked['limits'])
        runtime['connected_three_task_camera_runtime']=pipeline
        runtime['CPU_camera_reconstruction'].update(current_connected_runtime=pipeline,current_limits=linked['limits'])
        runtime['CPU_input_dispatch_reconstruction'].update(current_connected_runtime=pipeline,current_limits=linked['limits'],
            next_work='Reconstruct animationEB04/entity20820 and remaining equipment/allocator/texture/scene services,18othercapturedtasks and other game code; expand mainloop/scenes/audio. Full goal incomplete.')
        division=runtime['CPU_signed_division_reconstruction'];division.update(connected_calls=linked['signed_division_calls'])
        division['facts'][2]='Signed division is linked in the current camera/dispatcher runtime, with562actualcalls; it was scripted in the earlier standalone dispatcher proof.'
        runtime['CPU_input_dispatch_reconstruction']['signed_division_current']=division
        runtime['world_update_CPU_caller_reconstruction'].update(CPU_camera_linked=True,current_linked_pipeline=pipeline,
            latest_linked_update=linked['recorded_at'],remaining_scripted_helper_targets=linked['remaining_top_level_scripted_helpers'],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],current_limits=linked['limits'],
            camera_register_seed_adapter={'lowD2':'previousstatus','lowD3':'boundarydecision','original_stack_argument_count':0,'checked_against_actual_original_registers':True})
        runtime['CPU_scheduler_reconstruction'].update(current_task_runtime=pipeline,current_limits=linked['limits'])
    animation_path=root/'verification/biwn-animation-checks.json'
    targeting_path=root/'verification/biwn-targeting-checks.json'
    complete_world_path=root/'verification/biwn-task-targeting-runtime-checks.json'
    if animation_path.exists()and targeting_path.exists()and complete_world_path.exists():
        animation=json.loads(animation_path.read_text());targeting=json.loads(targeting_path.read_text());linked=json.loads(complete_world_path.read_text())
        if animation['CPU_cases']!=1538 or animation['CPU_instruction_coverage']!=[101,101]or targeting['CPU_cases']!=1026 or targeting['CPU_instruction_coverage']!=[183,183]or linked['targeting_calls']!=512 or linked['remaining_top_level_scripted_helpers']:
            raise ValueError('Animation/targeting lacks terminal complete direct-helper provenance')
        runtime['CPU_animation_reconstruction']={
            'recorded_at':animation['recorded_at'],'report':str(animation_path),'CPU_cases':1538,'update_cases':1025,'queue_cases':513,'CPU_instruction_coverage':[101,101],
            'host_guards':21,'portable_components':2,'original_bytes':320,'intervals':animation['intervals'],
            'facts':['EB04 advances four-byte frame records. Offset0is frame byte,1signed duration,2flag byte read bydispatcher,3signed relative-step byte. New-sequence index uses absolute signedword with original16bit wrap.',
                     'EAC4 writes fourlong requests in original order:record+4,record+0,record+8,record+12,then increments theword count. The original capacity test is signed count>39; negative counts are not clamped.',
                     'Rejected queue clears only D0low16, preserving itsupper16. Accepted enqueue returns fullD0=1. A fullqueue does not clear the animation dirty word, so later updates retry.',
                     'A positive countdown with no dirty flag returns its wrapped lowword while preserving incomingD0upper16. Expired updates can catch up multiple frames; sameframe/clean records suppress queue requests.',
                     'Current connected test executes real original/C EB04/EAC4 and supplies external delta-word samples. No return/completion stub executes and482flagbytes percase remain immutable afterseeding.',
                     'Queue consumer/model/pose processing, actor lifecycle and a complete hardwareclock remain unported. Queuing requests is not proof of fully animated model rendering.'],
            'checked_examples':json.loads((root/'verification/animation-checked-examples.json').read_text()),'matched':animation['matched'],'standalone_limits_at_that_checkpoint':animation['limits'],
            'linked_into_current_three_task_runtime':True,'queue_consumer_linked':False,'physical_hardware_validation':False}
        runtime['CPU_targeting_reconstruction']={
            'recorded_at':targeting['recorded_at'],'report':str(targeting_path),'CPU_cases':1026,'CPU_instruction_coverage':[183,183],'host_guards':14,'portable_components':1,'original_bytes':636,'interval':targeting['interval'],
            'facts':['20820scans40records with206byte stride. Candidate state/transform depth checks precede direction; accepted signedbyte angle error is-5through5 and depth is16through1024.',
                     'Candidate score is wrapped32bit dxSquared+dzSquared+20*angleErrorSquared, compared as signed32. Equal scores retain the first eligible candidate. Weapon-range comparison uses squared planar distance separately.',
                     'After projection/cursor updates the radius loop rereads only the low16distance word and sign-extends it. Checked distance33124is lowword8154, interpreted as-32412; the first square1exceeds it, so radius=255 and fullD0=1.',
                     'Target/cursor is an analyst label from behavior, not recovered originalsymbols. Candidate/transform producers, complete actorAI/collision and a rendered crosshair/fullviewport remain unverified.'],
            'checked_examples':json.loads((root/'verification/targeting-checked-examples.json').read_text()),'matched':targeting['matched'],'standalone_limits_at_that_checkpoint':targeting['limits'],
            'linked_into_current_three_task_runtime':True,'physical_hardware_validation':False}
        pipeline=dict(runtime['connected_three_task_camera_runtime']);pipeline.update(recorded_at=linked['recorded_at'],report=str(complete_world_path),
            task_handoffs=linked['task_handoffs'],world_inner_yields=linked['world_inner_yields'],dispatcher_animation_wait_yields=linked['dispatcher_animation_wait_yields'],
            multiply_calls=linked['multiply_calls'],direction_calls=linked['direction_calls'],signed_division_calls=linked['signed_division_calls'],
            animation_update_linked=True,animation_queue_linked=True,targeting_linked=True,all_direct_world_helpers_linked=True,
            animation_update_calls=linked['animation_update_calls'],animation_queue_calls=linked['animation_queue_calls'],targeting_calls=linked['targeting_calls'],
            animation_delta_events=linked['animation_delta_events'],animation_completion_flags_scripted=False,animation_asset_flags_unchanged=True,
            immutable_animation_flags_per_case=482,animation_queue_consumer_linked=False,
            original_dispatcher_instruction_coverage=linked['original_dispatcher_instruction_coverage'],original_camera_instruction_coverage=linked['original_camera_instruction_coverage'],
            animation_original_instruction_coverage=linked['animation_original_instruction_coverage'],targeting_original_instruction_coverage=linked['targeting_original_instruction_coverage'],
            remaining_top_level_scripted_helpers=[],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],matched=linked['matched'],limits=linked['limits'])
        runtime['connected_three_task_animation_targeting_runtime']=pipeline
        for name in['CPU_input_dispatch_reconstruction','CPU_camera_reconstruction']:
            runtime[name].update(current_connected_runtime=pipeline,current_limits=linked['limits'])
        runtime['CPU_input_dispatch_reconstruction']['next_work']='Implement animation queue consumer/model/pose processing,15remainingnestedservices,18othercapturedtasks and other game code; broaden mainloop/scenes/audio. Full goal incomplete.'
        division=runtime['CPU_signed_division_reconstruction'];division.update(connected_calls=linked['signed_division_calls'])
        division['facts'][2]='Signed division is linked in the current animation/targeting/camera/dispatcher runtime, with2047actualcalls. Earlier standalone dispatcher proof scripted it.'
        runtime['CPU_input_dispatch_reconstruction']['signed_division_current']=division
        runtime['world_update_CPU_caller_reconstruction'].update(all_direct_helpers_linked=True,current_linked_pipeline=pipeline,
            latest_linked_update=linked['recorded_at'],remaining_scripted_helper_targets=[],remaining_nested_dependency_targets=linked['remaining_nested_scripted_helpers'],current_limits=linked['limits'])
        runtime['CPU_scheduler_reconstruction'].update(current_task_runtime=pipeline,current_limits=linked['limits'])
    images_path=root/'verification/biwn-animation-images-checks.json'
    frames_path=root/'verification/biwn-animation-frames-checks.json'
    if images_path.exists() and frames_path.exists():
        images=json.loads(images_path.read_text());frames=json.loads(frames_path.read_text())
        if images['CPU_cases']!=321 or images['CPU_instruction_coverage']!=[50,50] or frames['frame_cases']!=144 or frames['distinct_frames']!=72 or frames['producer_consumer_sequence_steps']!=16:
            raise ValueError('Animation image evidence is incomplete')
        runtime['CPU_animation_images_reconstruction']={**images,'report':str(images_path)}
        runtime['sequential_animation_sprite_pipeline']={**frames,'report':str(frames_path)}
        runtime['CPU_animation_reconstruction'].update(queue_consumer_standalone_reconstructed=True,
            queue_consumer_linked_in_sequential_sprite_pipeline=True,queue_consumer_linked_to_captured_task_ring=False)
        runtime['CPU_input_dispatch_reconstruction']['next_work']='Link the reconstructed animation consumer into its rendering task with compatible asset lifecycles; continue15nestedservices,18othercapturedtasks,scene/mainloop/audio. Full goal incomplete.'
    scene_path=root/'verification/biwn-render-scene-checks.json'
    loop_path=root/'verification/biwn-render-loop-checks.json'
    if scene_path.exists() and loop_path.exists():
        scene=json.loads(scene_path.read_text());loop=json.loads(loop_path.read_text())
        if scene['CPU_cases']!=1024 or scene['CPU_instruction_coverage']!=[102,102]or loop['cases']!=144 or loop['task_handoffs']!=432:
            raise ValueError('Render scene/continuation evidence incomplete')
        runtime['CPU_render_scene_reconstruction']={**scene,'report':str(scene_path)}
        runtime['scheduled_render_continuation_pipeline']={**loop,'report':str(loop_path)}
    overlay_path=root/'verification/biwn-overlay-checks.json'
    format_path=root/'verification/biwn-overlay-format-checks.json'
    linked_path=root/'verification/biwn-render-overlay-runtime-checks.json'
    if overlay_path.exists() and format_path.exists() and linked_path.exists():
        overlay=json.loads(overlay_path.read_text());formatting=json.loads(format_path.read_text());linked=json.loads(linked_path.read_text())
        if overlay['CPU_cases']!=1024 or overlay['CPU_instruction_coverage']!=[184,184]or formatting['cases']!=1024 or linked['text_calls']!=108 or linked['formatter_calls']!=108:
            raise ValueError('Overlay/text/format evidence incomplete')
        runtime['CPU_overlay_reconstruction']={**overlay,'report':str(overlay_path),
            'checked_examples':json.loads((root/'verification/overlay-checked-examples.json').read_text())['examples']}
        runtime['fixed_overlay_format_adapter']={**formatting,'report':str(format_path)}
        runtime['scheduled_render_overlay_pipeline']={**linked,'report':str(linked_path)}
    display_path=root/'verification/biwn-display-list-checks.json'
    display_runtime_path=root/'verification/biwn-render-display-runtime-checks.json'
    if display_path.exists() and display_runtime_path.exists():
        display=json.loads(display_path.read_text());linked=json.loads(display_runtime_path.read_text())
        if display['CPU_cases']!=1025 or display['reachable_instruction_coverage']!=[252,252]or linked['display_list_calls']!=115 or len(linked['nested_scripted_targets'])!=6:
            raise ValueError('Display-list evidence incomplete')
        runtime['CPU_display_list_reconstruction']={**display,'report':str(display_path),
            'checked_example':json.loads((root/'verification/display-list-checked-example.json').read_text())}
        runtime['scheduled_render_display_pipeline']={**linked,'report':str(display_runtime_path)}
    create_path=root/'verification/biwn-task-create-checks.json'
    startup_path=root/'verification/biwn-render-startup-runtime-checks.json'
    if create_path.exists() and startup_path.exists():
        create=json.loads(create_path.read_text());startup=json.loads(startup_path.read_text())
        if create['native_CPU_cases']!=1028 or create['CPU_instruction_coverage']!=[25,25]or startup['created_task_calls']!=2304 or startup['render_task_caller_instruction_coverage']!=[98,98]or not startup['saved_context_CCR_bits_compared']:
            raise ValueError('Task creation/startup evidence incomplete')
        runtime['CPU_task_creation_reconstruction']={**create,'report':str(create_path),
            'checked_example':json.loads((root/'verification/task-create-checked-example.json').read_text())}
        runtime['render_task_startup_pipeline']={**startup,'report':str(startup_path)}
    rng_path=root/'verification/biwn-rng-checks.json'
    rng_runtime_path=root/'verification/biwn-render-rng-runtime-checks.json'
    if rng_path.exists() and rng_runtime_path.exists():
        rng=json.loads(rng_path.read_text());linked=json.loads(rng_runtime_path.read_text())
        if rng['CPU_cases']!=2194 or rng['CPU_instruction_coverage']!=[187,187] or linked['RNG_initializations']!=144 or linked['RNG_fill_iterations']!=36720:
            raise ValueError('RNG evidence incomplete')
        runtime['CPU_rng_reconstruction']={**rng,'report':str(rng_path),**json.loads((root/'verification/rng-checked-examples.json').read_text())}
        runtime['render_rng_startup_pipeline']={**linked,'report':str(rng_runtime_path)}
    services_path=root/'verification/biwn-startup-services-checks.json'
    services_runtime_path=root/'verification/biwn-render-services-runtime-checks.json'
    if services_path.exists() and services_runtime_path.exists():
        services=json.loads(services_path.read_text());linked=json.loads(services_runtime_path.read_text())
        if services['CPU_cases']!=1152 or services['CPU_instruction_coverage']!=[210,210] or linked['created_task_calls']!=2448 or linked['C_sprite_decodes']!=0:
            raise ValueError('Startup service evidence incomplete')
        runtime['CPU_startup_services_reconstruction']={**services,'report':str(services_path)}
        runtime['render_services_startup_pipeline']={**linked,'report':str(services_runtime_path)}
    memory_path=root/'verification/biwn-memory-checks.json'
    memory_native_path=root/'verification/biwn-memory-native-checks.json'
    memory_startup_path=root/'verification/biwn-render-memory-runtime-checks.json'
    if memory_path.exists() and memory_native_path.exists() and memory_startup_path.exists():
        memory=json.loads(memory_path.read_text());native=json.loads(memory_native_path.read_text());linked=json.loads(memory_startup_path.read_text())
        if memory['CPU_cases']!=2816 or memory['CPU_instruction_coverage']!=[257,257]or native['cases']!=656 or linked['real_output_allocations']!=144:
            raise ValueError('Memory management evidence incomplete')
        runtime['CPU_memory_reconstruction']={**memory,'report':str(memory_path),**json.loads((root/'verification/memory-checked-examples.json').read_text())}
        runtime['memory_native_pipeline']={**native,'report':str(memory_native_path)}
        runtime['render_memory_startup_pipeline']={**linked,'report':str(memory_startup_path)}
    resources_path=root/'verification/biwn-resources-checks.json'
    resources_native_path=root/'verification/biwn-resources-native-checks.json'
    resources_startup_path=root/'verification/biwn-render-resources-runtime-checks.json'
    if all(p.exists()for p in [resources_path,resources_native_path,resources_startup_path]):
        resource=json.loads(resources_path.read_text());native=json.loads(resources_native_path.read_text());linked=json.loads(resources_startup_path.read_text())
        if resource['CPU_cases']!=1920 or resource['CPU_instruction_coverage']!=[201,201]or native['cases']!=66 or linked['disc_read_requests']!=288:
            raise ValueError('Resource evidence incomplete')
        runtime['CPU_resources_reconstruction']={**resource,'report':str(resources_path),**json.loads((root/'verification/resources-checked-examples.json').read_text())}
        runtime['resources_native_pipeline']={**native,'report':str(resources_native_path)}
        runtime['render_resources_startup_pipeline']={**linked,'report':str(resources_startup_path)}
    scene_path=root/'verification/biwn-scene-loading-checks.json'
    scene_startup_path=root/'verification/biwn-render-scenes-runtime-checks.json'
    if scene_path.exists() and scene_startup_path.exists():
        scene=json.loads(scene_path.read_text());linked=json.loads(scene_startup_path.read_text())
        if scene['CPU_cases']!=1536 or scene['CPU_instruction_coverage']!=[479,479]or linked['disc_read_requests']!=1008:
            raise ValueError('Scene loading evidence incomplete')
        runtime['CPU_scene_loading_reconstruction']={**scene,'report':str(scene_path),**json.loads((root/'verification/scene-checked-examples.json').read_text())}
        runtime['render_scene_loading_startup_pipeline']={**linked,'report':str(scene_startup_path)}
    texture_path=root/'verification/biwn-texture-cache-checks.json'
    texture_startup_path=root/'verification/biwn-render-textures-runtime-checks.json'
    if texture_path.exists() and texture_startup_path.exists():
        texture=json.loads(texture_path.read_text());linked=json.loads(texture_startup_path.read_text())
        if texture['CPU_cases']!=2051 or texture['CPU_instruction_coverage']!=[190,190]or linked['disc_read_requests']!=1728:
            raise ValueError('Texture cache evidence incomplete')
        runtime['CPU_texture_cache_reconstruction']={**texture,'report':str(texture_path),**json.loads((root/'verification/texture-checked-examples.json').read_text())}
        runtime['render_texture_cache_startup_pipeline']={**linked,'report':str(texture_startup_path)}
    actor_path=root/'verification/biwn-actor-creation-checks.json'
    actor_startup_path=root/'verification/biwn-render-actors-runtime-checks.json'
    if actor_path.exists() and actor_startup_path.exists():
        actor=json.loads(actor_path.read_text());linked=json.loads(actor_startup_path.read_text())
        if actor['CPU_cases']!=2560 or actor['CPU_instruction_coverage']!=[469,469]or linked['created_task_calls']!=2736:
            raise ValueError('Actor creation evidence incomplete')
        runtime['CPU_actor_creation_reconstruction']={**actor,'report':str(actor_path),**json.loads((root/'verification/actor-checked-examples.json').read_text())}
        runtime['render_actor_creation_startup_pipeline']={**linked,'report':str(actor_startup_path)}
    actor_task_path=root/'verification/biwn-actor-task-boundary-checks.json'
    if actor_task_path.exists():
        actor_task=json.loads(actor_task_path.read_text())
        if actor_task['CPU_cases']!=512 or actor_task['reachable_instruction_coverage']!=[191,191]:raise ValueError('Actor task boundary proof incomplete')
        runtime['CPU_actor_task_boundary_reconstruction']={**actor_task,'report':str(actor_task_path)}
    actor_task_runtime_path=root/'verification/biwn-actor-task-runtime-checks.json'
    if actor_task_runtime_path.exists():
        linked=json.loads(actor_task_runtime_path.read_text())
        if linked['cases']!=128 or linked['task_handoffs']!=3072:raise ValueError('Actor scheduler proof incomplete')
        runtime['CPU_actor_task_scheduler_integration']={**linked,'report':str(actor_task_runtime_path)}
    navigation_path=root/'verification/biwn-actor-navigation-checks.json'
    navigation_runtime_path=root/'verification/biwn-actor-navigation-runtime-checks.json'
    if navigation_path.exists() and navigation_runtime_path.exists():
        navigation=json.loads(navigation_path.read_text());linked=json.loads(navigation_runtime_path.read_text())
        if navigation['CPU_cases']!=4096 or navigation['CPU_instruction_coverage']!=[209,209]or linked['navigation_helper_return_comparisons_total']!=1279:
            raise ValueError('Actor navigation evidence incomplete')
        runtime['CPU_actor_navigation_reconstruction']={**navigation,'report':str(navigation_path),**json.loads((root/'verification/actor-navigation-checked-examples.json').read_text())}
        runtime['actor_navigation_scheduler_integration']={**linked,'report':str(navigation_runtime_path)}
    rng_cpu_path=root/'verification/biwn-rng-cpu-checks.json'
    actor_rng_path=root/'verification/biwn-actor-rng-runtime-checks.json'
    if rng_cpu_path.exists() and actor_rng_path.exists():
        rng_cpu=json.loads(rng_cpu_path.read_text());linked=json.loads(actor_rng_path.read_text())
        if rng_cpu['CPU_cases']!=6144 or rng_cpu['host_guards']!=19 or linked['helper_return_CPU_comparisons_total']!=2375:
            raise ValueError('Full CPU RNG evidence incomplete')
        runtime['CPU_indexed_RNG_full_CPU']={**rng_cpu,'report':str(rng_cpu_path)}
        runtime['actor_rng_scheduler_integration']={**linked,'report':str(actor_rng_path)}
    actor_movement_path=root/'verification/biwn-actor-movement-gpu-checks.json'
    if actor_movement_path.exists():
        reports={name:json.loads((root/'verification'/name).read_text())for name in ['biwn-actor-movement-boundary-checks.json','biwn-actor-direction-checks.json','biwn-actor-movement-direction-checks.json','biwn-movement-submit-cpu-checks.json','biwn-actor-movement-gpu-checks.json']}
        caller,direction,connected,submit,gpu=reports.values()
        if caller['CPU_cases']!=2048 or gpu['CPU_cases']!=256 or gpu['GPU_output_words_scripted']:
            raise ValueError('Actor movement evidence incomplete')
        runtime['CPU_actor_movement_reconstruction']={**caller,'report':str(root/'verification/biwn-actor-movement-boundary-checks.json')}
        runtime['CPU_actor_direction_full_CPU']={**direction,'report':str(root/'verification/biwn-actor-direction-checks.json')}
        runtime['CPU_movement_submit_full_CPU']={**submit,'report':str(root/'verification/biwn-movement-submit-cpu-checks.json')}
        runtime['actor_movement_GPU_pipeline']={**gpu,'report':str(actor_movement_path),**json.loads((root/'verification/actor-movement-checked-examples.json').read_text())}
    actor_collision_path=root/'verification/biwn-actor-collision-checks.json'
    actor_full_path=root/'verification/biwn-actor-full-movement-runtime-checks.json'
    if actor_collision_path.exists() and actor_full_path.exists():
        collision=json.loads(actor_collision_path.read_text());actor=json.loads(actor_full_path.read_text())
        if collision['CPU_cases']!=4096 or collision['CPU_instruction_coverage']!=[109,109]or actor['helper_return_CPU_comparisons_total']!=2671:
            raise ValueError('Actor collision/live movement evidence incomplete')
        runtime['CPU_geometry_full_CPU']={**json.loads((root/'verification/biwn-geometry-cpu-checks.json').read_text()),'report':str(root/'verification/biwn-geometry-cpu-checks.json')}
        runtime['CPU_actor_collision_reconstruction']={**collision,'report':str(actor_collision_path),**json.loads((root/'verification/actor-collision-checked-examples.json').read_text())}
        runtime['actor_complete_movement_pipeline']={**json.loads((root/'verification/biwn-actor-movement-collision-checks.json').read_text()),'report':str(root/'verification/biwn-actor-movement-collision-checks.json')}
        runtime['actor_full_movement_runtime']={**actor,'report':str(actor_full_path)}
    lifecycle_path=root/'verification/biwn-actor-lifecycle-runtime-checks.json'
    if lifecycle_path.exists():
        lifecycle=json.loads(lifecycle_path.read_text());removal_path=root/'verification/biwn-task-removal-checks.json';removal=json.loads(removal_path.read_text())
        if lifecycle['cases']!=256 or lifecycle['task_handoffs']!=3840 or removal['native_CPU_cases']!=1024:
            raise ValueError('Actor lifecycle/removal proof incomplete')
        runtime['CPU_task_removal_reconstruction']={**removal,'report':str(removal_path)}
        runtime['actor_lifecycle_runtime']={**lifecycle,'report':str(lifecycle_path)}
        runtime['actor_lifecycle_checked_examples']=json.loads((root/'verification/actor-lifecycle-checked-examples.json').read_text())
    actor_scene_path=root/'verification/biwn-disc-scene-actors-checks.json'
    if actor_scene_path.exists():
        actor_scene=json.loads(actor_scene_path.read_text())
        if actor_scene['cases']!=16 or actor_scene['task_handoffs']!=2064 or actor_scene['cases_with_position_change']!=12:raise ValueError('Disc-scene actor proof incomplete')
        runtime['actor_disc_scene_pipeline']={**actor_scene,'report':str(actor_scene_path)}
        runtime['actor_disc_scene_checked_examples']=json.loads((root/'verification/actor-scene-checked-examples.json').read_text())
    disc_world_path=root/'verification/biwn-disc-world-actors-checks.json'
    for name in ['biwn-disc-world-animation-checks.json','biwn-disc-world-camera-checks.json','biwn-disc-world-targeting-checks.json','biwn-disc-world-dispatch-checks.json','biwn-disc-world-yields-checks.json','biwn-disc-world-resources-checks.json','biwn-disc-world-cd-wrappers-checks.json','biwn-disc-world-loading-yields-checks.json','biwn-disc-world-render-queue-checks.json','biwn-disc-world-scene-draw-checks.json','biwn-disc-world-geometry-records-checks.json','biwn-disc-world-gpu-geometry-checks.json','biwn-disc-world-integer-gpu-geometry-checks.json']:
        candidate=root/'verification'/name
        if candidate.exists():disc_world_path=candidate
    if disc_world_path.exists():
        linked=json.loads(disc_world_path.read_text())
        expected_handoffs=6144 if linked.get('render_task_fullCPU_real')else 5136 if linked.get('dispatcher_continuations_in_disc_scene_verified')else 2576
        if linked['cases']!=16 or linked['task_handoffs']!=expected_handoffs or linked['shared_timestep_directly_scripted']:raise ValueError('Disc world/actor proof incomplete')
        runtime['world_full_CPU_reconstruction']={**json.loads((root/'verification/biwn-world-cpu-checks.json').read_text()),'report':str(root/'verification/biwn-world-cpu-checks.json')}
        runtime['world_real_input_full_CPU']={**json.loads((root/'verification/biwn-world-input-cpu-checks.json').read_text()),'report':str(root/'verification/biwn-world-input-cpu-checks.json')}
        runtime['disc_world_actor_pipeline']={**linked,'report':str(disc_world_path)}
        runtime['world_actor_checked_examples']=json.loads((root/'verification/world-actor-checked-examples.json').read_text())
        for key,name in [('world_animation_full_CPU','biwn-animation-cpu-checks.json'),('world_camera_full_CPU','biwn-camera-cpu-checks.json'),('world_targeting_full_CPU','biwn-targeting-cpu-checks.json'),('world_dispatch_full_CPU','biwn-input-dispatch-cpu-checks.json'),('dispatcher_scheduled_yields','biwn-input-dispatch-yield-checks.json'),('resource_full_CPU','biwn-resource-cpu-checks.json'),('cd_wrapper_full_CPU','biwn-cd-cpu-checks.json'),('resource_synchronization_full_CPU','biwn-resource-sync-checks.json'),('two_client_resource_readiness','biwn-resource-readiness-checks.json'),('render_queue_full_CPU','biwn-render-queue-cpu-checks.json'),('scene_draw_full_CPU','biwn-scene-draw-cpu-checks.json'),('geometry_records_full_CPU','biwn-geometry-records-cpu-checks.json'),('GPU_geometry_program','biwn-gpu-integer-geometry-checks.json'),('GPU_projection_program','biwn-gpu-integer-projection-checks.json'),('CPU_projection_submit','biwn-gpu-projection-submit-cpu-checks.json'),('original_GPU_draw_chain','biwn-gpu-draw-integer-original-probes.json'),('GPU_setup57_program','biwn-gpu-setup57-checks.json'),('hybrid_GPU_setup57_draw_chain','biwn-gpu-setup57-integer-hybrid-checks.json'),('GPU_consumer6380_program','biwn-gpu-consumer6380-checks.json'),('combined_GPU_setup57_consumer6380_draw_chain','biwn-gpu-consumer6380-hybrid-checks.json'),('GPU_material_programs','biwn-gpu-material-checks.json'),('five_C_GPU_draw_chain','biwn-gpu-material-hybrid-checks.json'),('GPU_resident_candidate','biwn-gpu-resident-candidate-checks.json'),('experimental_six_C_GPU_draw_chain','biwn-gpu-resident-hybrid-checks.json'),('GPU_dispatcher_loop','biwn-gpu-dispatcher-checks.json'),('observed_C_GPU_draw_slice','biwn-GPU-C-draw-checks.json')]:
            candidate=root/'verification'/name
            if candidate.exists():runtime[key]={**json.loads(candidate.read_text()),'report':str(candidate)}
    consumer_checkpoint=root/'verification/consumer6380-checkpoint.json'
    if consumer_checkpoint.exists():runtime['GPU_consumer6380_checkpoint']=json.loads(consumer_checkpoint.read_text())
    material_checkpoint=root/'verification/material-checkpoint.json'
    if material_checkpoint.exists():runtime['GPU_material_checkpoint']=json.loads(material_checkpoint.read_text())
    resident_checkpoint=root/'verification/resident-candidate-checkpoint.json'
    if resident_checkpoint.exists():runtime['GPU_resident_candidate_checkpoint']=json.loads(resident_checkpoint.read_text())
    dispatcher_checkpoint=root/'verification/dispatcher-C-draw-checkpoint.json'
    if dispatcher_checkpoint.exists():runtime['GPU_dispatcher_C_draw_checkpoint']=json.loads(dispatcher_checkpoint.read_text())
    scene_submissions_checkpoint=root/'verification/scene-render-submissions-checkpoint.json'
    if scene_submissions_checkpoint.exists():runtime['scene_render_submissions_checkpoint']=json.loads(scene_submissions_checkpoint.read_text())
    scene_display_checkpoint=root/'verification/scene-display-list-checkpoint.json'
    if scene_display_checkpoint.exists():runtime['scene_display_list_checkpoint']=json.loads(scene_display_checkpoint.read_text())
    overlay_text_checkpoint=root/'verification/overlay-text-scene-checkpoint.json'
    if overlay_text_checkpoint.exists():runtime['overlay_text_scene_checkpoint']=json.loads(overlay_text_checkpoint.read_text())
    projection_checkpoint=root/'verification/projection-full-coverage-checkpoint.json'
    if projection_checkpoint.exists():runtime['GPU_projection_pending']=json.loads(projection_checkpoint.read_text())['pending_integration_evidence']
    save(folder / 'emulator-runtime/summary.json', runtime)

    baseline = json.loads((folder / 'divu-baseline-pcode-checks.json').read_text())
    candidate = json.loads((folder / 'divu-candidate-pcode-checks.json').read_text())
    compiled = json.loads((root / 'verification/biwn-decompiled-division-checks.json').read_text())
    if candidate['cases'] != 592 or candidate['DIVU_failures'] or candidate['helper_failures'] or compiled['cases'] != 296:
        raise ValueError('Division regression checks have not passed')
    manifest = json.loads((folder / 'nextstage-divu-export/manifest.json').read_text())
    original = json.loads((folder / 'nextstage-stack2-export/manifest.json').read_text())
    def boundaries(report):
        return {row['address']: (row['size'], row['bytes']) for row in report['instructions']}
    before, after = boundaries(original), boundaries(manifest)
    if before != after:
        raise ValueError('Candidate changed decoded instruction bytes/boundaries')
    image = (folder / 'nextstage-68000-candidate.bin').read_bytes()
    if stage.digest(image) != stage.STAGE_SHA:
        raise ValueError('Candidate image changed')
    for row in manifest['instructions']:
        offset = int(row['address'], 16) - 0x4000
        if offset < 0 or image[offset:offset + row['size']].hex() != row['bytes']:
            raise ValueError('Exported instruction bytes differ from captured image')
    decompiled = folder / 'nextstage-divu-export/decompiled.c'
    division = {
        'time': datetime.now(timezone.utc).isoformat(),
        'language': candidate['language'], 'compiler_profile': candidate['compiler_spec'],
        'original_default_pcode': {k:baseline[k] for k in ['cases','DIVU_failures','helper_failures']},
        'separate_candidate_pcode': {k:candidate[k] for k in ['cases','DIVU_failures','helper_failures']},
        'verbatim_exported_division_C_cases_passed': compiled['cases'],
        'static_export': {'function_entries': len(manifest['functions']),
                          'decompiled': sum(x['decompiled'] for x in manifest['functions']),
                          'instructions_matching_previous_export_and_image': len(after),
                          'C_warning_count': decompiled.read_text().count('WARNING:')},
        'scope': 'One nonzero-divisor arithmetic helper was checked. Two function signatures and one merged boundary are analyst annotations. Other automatic C remains approximate; zero-divisor traps and the full condition-code ABI are excluded. The decoder is still a 68040 superset.',
    }
    save(folder / 'divu-candidate-summary.json', division)
    print(json.dumps({'runtime_runs': len(runs), 'division_C_cases': compiled['cases'],
                      'candidate_functions': len(manifest['functions']), 'instructions': len(after)}))


if __name__ == '__main__':
    main()
