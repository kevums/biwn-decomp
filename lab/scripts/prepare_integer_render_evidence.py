"""Publish source-consistent divider-zero checks without adding C components."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text())
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    now = datetime.now(timezone.utc).isoformat()
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    source = ROOT/'projects/black-ice-white-noise/restoration'
    gpu = read(ROOT/'verification/biwn-gpu-integer-geometry-checks.json')
    projection = read(ROOT/'verification/biwn-gpu-integer-projection-checks.json')
    linked = read(ROOT/'verification/biwn-disc-world-integer-gpu-geometry-checks.json')
    hybrid = read(ROOT/'verification/biwn-gpu-setup57-integer-hybrid-checks.json')
    draw = read(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json')
    assert gpu['GPU_cases'] == 128 and gpu['source_instruction_coverage'] == [434,434] and gpu['host_guards'] == 13
    assert projection['GPU_cases'] == 48 and projection['source_instruction_coverage'] == [450,450] and projection['host_guards'] == 16
    assert linked['cases'] == 16 and linked['GPU4D80_transform_live_calls'] == 1008 and linked['task_handoffs'] == 6144
    assert hybrid['cases'] == hybrid['C_setup_calls'] == 4 and not hybrid['original_GPU57A0_executed'] and hybrid['other_original_GPU_programs_executed']
    for proof in [gpu, projection, linked]:
        assert proof['GPU_division_control'] == 0
        for name, digest in proof['source_sha256'].items(): assert sha(source/name) == digest
    assert sha(source/'biwn_gpu_setup57.c') == hybrid['source_C_sha256']
    validation = read(session/'boot-slice-validation.json')
    assert validation['portable_C_component_count'] == 117 and validation['processor_component_counts'] == {'CPU':112,'GPU':5}
    # Retain the common publication schema; every changing measurement below is
    # derived from the new fixture records, not inherited from the old mode1 run.
    for key, value in validation['disc_world_actor_pipeline'].items(): linked.setdefault(key, value)
    rows = read(Path(linked['directory'])/'fixtures.json')
    gpu_counts = sorted({c['record_count_after_GPU'] for row in rows for c in row['rebuilt']['GPU_geometry_CPU_calls']})
    added = sorted({(c['record_count']-c['record_count_before']) & 0xffffffff for row in rows for c in row['rebuilt']['geometry_record_calls'] if c['target'] == 0x170a0})
    total = sum(row['original']['steps'].count(0xe220) for row in rows)
    world = sum(sum(c['target'] == 0xe220 for c in row['rebuilt']['world_calls']) for row in rows)
    assert gpu_counts == [0,58] and added == [4] and linked['geometry_record_count_values'] == [4,62]
    assert total == 3488 and world == 1440
    linked.update(GPU_geometry_record_counts=gpu_counts, record_builder_added_record_counts=added,
        original_GPU_submit_entries=total, decoded_sprite_previews=[],
        movement_matrix_scope=dict(whole_scene_E220_submissions=total, world_recorded_E220_calls=world,
            geometry_record_builder_E220_calls=0, actor_E220_calls_by_difference=total-world,
            geometry_record_builder_E220_provider_linked=True, geometry_record_builder_E220_branch_executed=False,
            scope='Whole-scene world/actor movement is separate from the unreached nested record-builder branch.'))
    gpu.update(initial_GPU_RAM_supplied=True, initial_GPU_RAM_input_files_retained=True)
    gpu['matched'] = [s.replace('nonrestoring16.16division', 'nonrestoring integer division (control0)') for s in gpu['matched']]
    gpu['probe_bridge_sha256'] = sha(ROOT/'scripts/biwn_integer_render_device_bridge.c')
    projection['limits'][1] = 'Full CPU E19E is separately reconstructed and checked in128native/Unicorn cases, but remains scripted in the live C scene. C57A0 setup is separately accepted and passes4integer-mode hybrid chains; resident dispatcher and58A0/6380/6460/6720/69A0 still execute original GPU in that hybrid. Assisted startup, scripts and synchronous devices remain. Full C viewport/game incomplete.'
    for name, proof in [('biwn-gpu-integer-geometry-checks.json', gpu), ('biwn-gpu-integer-projection-checks.json', projection), ('biwn-disc-world-integer-gpu-geometry-checks.json', linked)]:
        proof.update(publication_recorded_at=now, new_components=0,
            publication_scope='Host fixture divider mode correction; accepted source C unchanged. Legacy fractional-mode tests retained separately.')
        save(ROOT/'verification'/name, proof); save(Path(proof['directory'])/'report.json', proof)
    remaining = ['resident dispatcher F031BE', '0x58a0', '0x6380', '0x6460', '0x6720', '0x69a0']
    scope = ('The test harness now supplies integer GPU division control0, consistent with GPU reset and the explicit source4B00 return store. '
        'Accepted C source is unchanged. Geometry passes128cases/all434instructions/13guards; projection passes48cases/all450/16guards. '
        'The16-case C scene retains1008geometry calls,720world updates,2048actor iterations and6144handoffs. '
        'Geometry counters are0/58, followed by4builder records, giving absolute counters4/62. '
        'Local27B-authored setup57 case bodies remain unchanged and pass4corrected-mode hybrid chains; other draw programs remain original GPU. '
        'Original-code fast-blitter diagnostics show a recognizable street; the alternate backend differs only in framebuffer RAM and blitter readbacks despite identical GPU state and PC sequence. This discrepancy is unresolved. '
        'Programs6720/69A0 are newly mapped288-byte overlays, not reconstructed C.117selected components112CPU/5GPU is not completion percentage. '
        'Full C drawing, live CPU E19E/E202 linkage, full GPU context continuity, remaining tasks/scenes, audio, boot and playable game remain incomplete.')
    next_work = 'Reconstruct and compare resident dispatcher and58A0/6380/6460/6720/69A0. Integrate full CPU E19E/E202 with coherent GPU context. Resolve raster backend discrepancy; continue overlay/display, tasks/scenes/audio/boot and easy native Chat/advertising evaluation.'
    checkpoint = dict(recorded_at=now, status='integer_mode_host_fixture_corrected_C_sources_unchanged_checks_passed',
        published_components=117, processor_components={'CPU':112,'GPU':5}, new_components=0,
        GPU_division_control=0, full_game_complete=False, full_renderer_C=False,
        full_viewport_proved=False, source_C_changed=False, current_scope=scope, next_work=next_work,
        geometry_cases=128, projection_cases=48, live_scene_cases=16, hybrid_cases=4,
        GPU_counter_values=gpu_counts, record_builder_additions=added, final_record_counter_values=[4,62],
        remaining_C_draw_programs=remaining,
        source_divider_evidence=str(ROOT/'verification/biwn-divider-source-evidence.json'),
        backend_comparison=str(ROOT/'verification/biwn-integer-draw-backend-comparison.json'),
        original_draw_report=str(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json'),
        local_model_activity_this_checkpoint='No new training or inference; prior accepted27Bcase bodies revalidated unchanged.')
    save(ROOT/'verification/integer-render-checkpoint.json', checkpoint)
    validation.update(GPU_geometry_program=gpu, GPU_projection_program=projection,
        disc_world_actor_pipeline=linked, disc_world_GPU_geometry_pipeline=linked,
        original_GPU_draw_chain=draw, hybrid_GPU_setup57_draw_chain=hybrid,
        integer_render_checkpoint=checkpoint, latest_aggregate_update=now, component_count_scope=scope)
    save(session/'boot-slice-validation.json', validation)
    previous = read(ROOT/'verification/projection-full-coverage-checkpoint.json')
    pending = previous['pending_integration_evidence']
    pending.update({key: projection[key] for key in ['status','GPU_cases','actual_live_prefix_cases','declared_camera_variant_cases','source_instruction_coverage','uncovered_instruction_addresses','host_guards','original_GPU_core_calls_on_C_side','live_CPU_E19E_linked','full_renderer_verified','matched','limits']})
    pending.update(report=str(ROOT/'verification/biwn-gpu-integer-projection-checks.json'),
        GPU_division_control=0, projection_list_head_values=[1], later_draw_programs=remaining,
        later_draw_programs_reconstructed=False, scope=scope, integer_render_checkpoint=checkpoint)
    setup = pending['GPU57A0_setup']
    setup['hybrid'].update(report=str(ROOT/'verification/biwn-gpu-setup57-integer-hybrid-checks.json'),
        GPU_division_control=0, remaining_original_components=remaining)
    observed = read(Path(draw['directory'])/'cases.json')
    pending['original_draw_chain'].update(report=str(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json'),
        queued_commands=draw['commands'], GPU_division_control=0,
        framebuffer_changed_bytes=[r['framebuffer_changed_bytes'] for r in observed],
        projection_list_head_values=[1], diagnostic_preview='Recognizable street from original-code fast-blitter diagnostic. Alternate backend disagrees in framebuffer pixels. Not a verified C viewport or playable game.',
        scope='Original GPU draw reference; C57A0 is separately compared in the matching integer-mode hybrid proof.',
        backend_comparison=checkpoint['backend_comparison'])
    save(ROOT/'verification/projection-full-coverage-checkpoint.json', previous)
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/everyday-inference.json','verification/requirements-audit.json']:
        path = ROOT/name; value = read(path)
        value.update(integer_render_checkpoint=checkpoint, disc_world_actor_progress=scope)
        if name == 'config.json': value['chat_frontend']['game']['status'] = scope
        if name == 'corpus/game/project-intake.json': value['latest_checked_status'] = scope
        if name == 'verification/current-runtime-state.json': value.update(recorded_at=now, decomp_progress=scope, emulator_jobs='Terminal: corrected-mode128geometry/48projection/16scene/4hybrid comparisons. No model job running at publication.')
        if name == 'verification/setup-status.json': value['game_work'] = scope
        if name == 'verification/requirements-audit.json':
            value.update(recorded_at_utc=now, this_goal_turn_classification='Progress: host fixture divider correction, unchanged C revalidation and newly reached rendering overlays mapped.', next_safe_work=next_work)
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']: item.update(state=scope)
        save(path, value)
    examples = read(ROOT/'verification/world-actor-checked-examples.json')
    examples.update(checked_world_actor_scope=scope, checked_render_queue_answer=scope,
        checked_projection_scope=scope, integer_render_checkpoint=checkpoint)
    save(ROOT/'verification/world-actor-checked-examples.json', examples)
    # Current summaries prefer the explicit integer-mode reports; old reports
    # remain intact for reproducibility, rather than silently changing fixtures.
    path = ROOT/'scripts/summarize_biwn_checks.py'; text = path.read_text()
    text = text.replace("'biwn-disc-world-gpu-geometry-checks.json']:", "'biwn-disc-world-gpu-geometry-checks.json','biwn-disc-world-integer-gpu-geometry-checks.json']:")
    for key, name in [('GPU_geometry_program','biwn-gpu-integer-geometry-checks.json'),('GPU_projection_program','biwn-gpu-integer-projection-checks.json'),('original_GPU_draw_chain','biwn-gpu-draw-integer-original-probes.json'),('hybrid_GPU_setup57_draw_chain','biwn-gpu-setup57-integer-hybrid-checks.json')]:
        old = {'GPU_geometry_program':'biwn-gpu-geometry-checks.json','GPU_projection_program':'biwn-gpu-projection-checks.json','original_GPU_draw_chain':'biwn-gpu-draw-original-probes.json','hybrid_GPU_setup57_draw_chain':'biwn-gpu-setup57-hybrid-checks.json'}[key]
        text = text.replace(f"('{key}','{old}')", f"('{key}','{name}')")
    path.write_text(text)
    audit = ROOT/'verification/integer-render-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    audit.mkdir(parents=True)
    note = 'BLACK ICE WHITE NOISE — INTEGER DIVIDER CORRECTION\n'+now+'\n\n'+scope+'\n\nWHO DID WHAT\nCodex investigated the noisy diagnostic, compared textures and backends, observed source4B00 clearing divider control, corrected host adapters, reran comparisons and mapped additional overlays. Accepted C and local27Bcase bodies unchanged. No Codex subagents, new training or new local generation in this checkpoint. Native Chat visibility remains unverified; no unlock request is required.\n\nNEXT\n'+next_work+'\n'
    (audit/'readable-results.txt').write_text(note)
    snapshot = audit/'snapshot'; snapshot.mkdir()
    files = [ROOT/'verification'/name for name in ['integer-render-checkpoint.json','biwn-divider-source-evidence.json','biwn-integer-draw-backend-comparison.json','biwn-gpu-integer-geometry-checks.json','biwn-gpu-integer-projection-checks.json','biwn-disc-world-integer-gpu-geometry-checks.json','biwn-gpu-setup57-integer-hybrid-checks.json','biwn-gpu-draw-integer-original-probes.json','biwn-gpu-draw-integer-slow-original-probes.json']]
    files += [session/name for name in ['remaining-draw-GPU-workmap.json','gpu-draw-resident-workmap.json']]
    files += [ROOT/'scripts'/name for name in ['prepare_integer_render_evidence.py','analyze_integer_draw_evidence.py','biwn_integer_render_device_bridge.c','biwn_draw_integer_probe_bridge.c','biwn_draw_integer_slow_probe_bridge.c','biwn_setup57_integer_hybrid_bridge.c']]
    files += [source/name for name in ['biwn_gpu_geometry.c','biwn_gpu_geometry.h','biwn_gpu_projection.c','biwn_gpu_projection.h','biwn_gpu_setup57.c','biwn_gpu_setup57.h']]
    for path in files: shutil.copy2(path, snapshot/path.name)
    save(audit/'manifest.json', dict(recorded_at=now, files=[dict(source=str(p), sha256=sha(p)) for p in files]))
    save(ROOT/'verification/integer-render-review.json',dict(directory=str(audit), recorded_at=now))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(note+'\nAUDIT\n'+str(audit)+'\n')
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with (ROOT/name).open('a') as stream: stream.write('\n'+note)
    path = ROOT/'START HERE.txt'; text = path.read_text(); a = text.index('LATEST GAME RESULT\n'); b = text.index('LOCAL INFERENCE RESULT\n', a)
    path.write_text(text[:a]+'LATEST GAME RESULT\n'+scope+'\n\n'+text[b:])
    for script in ['summarize_biwn_checks.py','install_chat_runtime.py']:
        subprocess.run([str(ROOT/'.venv/bin/python'), str(ROOT/'scripts'/script)], check=True, stdout=subprocess.DEVNULL)
    print(json.dumps(dict(published_components=117, GPU_counter_values=gpu_counts, absolute_record_counts=[4,62], source_C_changed=False, audit=str(audit))))

if __name__ == '__main__': main()
