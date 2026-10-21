"""Publish matched scheduled doorway/stair loading separately from rendering."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: json.loads(path.read_text())
save = lambda path, value: path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    now = datetime.now(timezone.utc).isoformat()
    report = read(ROOT / 'verification/biwn-scheduled-entrance-checks.json')
    directory = Path(report['directory'])
    guards = read(ROOT / 'verification/biwn-actor-factory-guard-checks.json')
    assert read(directory / 'status.json')['status'] == 'terminal_pass'
    assert [report['cases'], report['task_removals'], report['task_creations'], report['disc_transfers']] == [6, 12, 2, 18]
    assert report['source_stair_transitions_312_to_313_to_314'] == 4 and guards['host_guards'] == 21
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for name, digest in report['source_sha256'].items():
        assert sha(source / name) == digest
    assert sha(ROOT / 'scripts/check_biwn_scheduled_entrance.py') == report['test_script_sha256']
    assert guards['source_sha256']['biwn_actor_factory_cpu.c'] == report['source_sha256']['biwn_actor_factory_cpu.c']
    fixtures = read(directory / 'fixtures.json')
    for row in fixtures:
        creations = [call for call in row['C']['calls'] if call['target'] == 0xdf6c]
        assert len(creations) == (1 if row['gate']['target'] == 312 else 0)
        if creations:
            assert creations[0]['created_context'] == '0xc1528'
            ram = (directory / f"case-{row['case']}-C-final-RAM.bin").read_bytes()
            assert int.from_bytes(ram[0xc1530:0xc1534], 'big') == 0xedc4
            assert 0xedc4 not in row['native']['steps'], 'Creation is verified; task execution is not claimed'
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    stage = (session / 'nextstage-68000-candidate.bin').read_bytes()
    before = (directory / 'case-0-before-RAM.bin').read_bytes()
    assert before[0x13620:0x13706] == stage[0x13620 - 0x4000:0x13706 - 0x4000]
    checkpoint = {key: report[key] for key in ['recorded_at', 'status', 'cases', 'source_interiors', 'disc_transfers',
                 'transferred_bytes', 'task_removals', 'task_creations', 'source_stair_transitions_312_to_313_to_314',
                 'native_CPU_steps', 'source_group_instruction_coverage', 'limits']}
    checkpoint.update(report=str(ROOT / 'verification/biwn-scheduled-entrance-checks.json'),
        selected_components=135, processor_components={'CPU': 122, 'GPU': 13}, new_components=0,
        full_CPU_RAM_privateframes_helper_yield_removal_disc_events_match=True,
        boundary_cleanup_and_actual_scheduler_loading_verified_for_declared_fixtures=True,
        actor_context_reuse_verified_for_declared_fixtures=True, source_gate_scene_actor_records_patched=False,
        manual_spare_contexts_added=False, source_task_jump_table_SHA256=hashlib.sha256(before[0x13620:0x13706]).hexdigest(),
        actual_created_callback='EDC4', created_callback_executed=False,
        runnable_contexts_before_removal=5, explicitly_blocked_contexts=16, renderer_blocked=True,
        natural_walking_input_reachability_verified=False, uninterrupted_world_loop_verified=False,
        indoor_rendering_linked_after_these_transitions=False, original_CPU_or_GPU_execution_on_C_side=False,
        factory_host_guards=21, factory_generated_instruction_coverage=[141, 210],
        source_empty_pool_ILLEGAL_emulated=False, local_model_instruction_bodies=171,
        new_code_authorship='Codex coordinator; no new local-model code generation/training.',
        whole_game_complete=False, playable=False, native_Chat_verified=False,
        next_work=['Run newly created EDC4 actor and other tasks on the loaded indoor scene.',
                   'Connect actual indoor world/input/camera/rendering with transitions; remove controlled pose/host-entry and blocked-task gaps.',
                   'Exercise remaining factory/loader branches, audio/boot/global GPU state/scanout and hardware/backend accuracy; full playable game remains unfinished.',
                   'Verify visible native LM Studio Chat and general local/advertising inference reliability.'])
    save(ROOT / 'verification/scheduled-entrance-checkpoint.json', checkpoint)
    for name in ['boot-slice-validation.json', 'emulator-runtime/summary.json']:
        path = session / name
        state = read(path)
        state['scheduled_entrance_checkpoint'] = checkpoint
        save(path, state)
    for name in ['config.json', 'corpus/game/project-intake.json', 'verification/setup-status.json',
                 'verification/current-runtime-state.json', 'verification/requirements-audit.json']:
        path = ROOT / name
        state = read(path)
        state['scheduled_entrance_checkpoint'] = checkpoint
        if name == 'verification/requirements-audit.json':
            state.update(recorded_at_utc=now, this_goal_turn_classification='Progress: six source doorway/stair cleanup/scheduler/CD-loading cases match full original CPU/RAM;12task removals,2actual EDC4 task creations/context reuses. Full goal active.', next_safe_work=checkpoint['next_work'])
        if name == 'verification/current-runtime-state.json':
            state.update(recorded_at=now, emulator_jobs='Terminal: six scheduled source transition cases and21factory host guards passed. No active emulator job.')
        save(path, state)
    out = ROOT / 'verification/scheduled-entrance-review' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    (out / 'snapshot').mkdir(parents=True)
    files = [source / name for name in ['biwn_actor_factory_cpu.c', 'biwn_actor_factory_cpu.h']]
    files += [ROOT / 'scripts' / name for name in ['generate_biwn_actor_factory_cpu.py', 'check_biwn_scheduled_entrance.py',
              'check_biwn_actor_factory_guards.py', 'inspect_biwn_entrance_actor_dispatch.py', 'prepare_biwn_scheduled_entrance_evidence.py']]
    files += [ROOT / 'verification' / name for name in ['biwn-scheduled-entrance-checks.json',
              'biwn-actor-factory-guard-checks.json', 'scheduled-entrance-checkpoint.json']]
    for path in files:
        shutil.copy2(path, out / 'snapshot' / path.name)
    save(out / 'manifest.json', {'recorded_at': now, 'files': {str(path): sha(path) for path in files}, 'checkpoint': checkpoint,
         'rejected_early_task_expectations': 'IDs4/5/6/7 dispatch directly to return in the exact source table. Earlier source-record presence was incorrectly expected to imply task creation. Neither gate nor actor/table data was changed; source stairs through313to314 reach ID9/EDC4 and demonstrate genuine reuse.',
         'harness_repairs': ['BIOS bytes are adapter boundaries, not truncated two-byte source disassembly.',
                            'Included internal20E8C/20F0C/D1E0 provider entries in observer/dispatch registry.',
                            'Native observer closes D306 tail frame at BIOS3042 before RTS; whole RAM/private frames remain unmasked.',
                            'Report hashes file bytes rather than Path objects; raw failed runs retained.',
                            'All resumed source RTS instructions execute through fixed C full-call interfaces; Python only orchestrates explicit host entries.'],
         'whole_goal_complete': False})
    note = ('BLACK ICE WHITE NOISE — SCHEDULED DOORWAY / STAIR LOADING\n' + now + '\n\n'
        'Six cases match original native M68000 versus fixed C: actual loaded source gate records enter interiors17/312, cleanup marks actors dead, actual actor/TRAP2 removal frees contexts, source loading yields switch tasks and external CD completion supplies preserved bytes. Two312cases continue through actual stair records/source positioning/button-driven1A0F8 transitions313then314; ID9/EDC4 task creation reuses one freed context in each. No spare contexts or changed scene/gate/actor/table records. Full CPU/SR/USP/SSP,whole2MBRAM/private frames,all nested helper states and yield/removal/handoff/disc events match.12task removals,2task creations,18disc transfers/1,030,080bytes;458,412original reference CPU steps. C side runs no original CPU/GPU instructions. Factory source141/210 instructions exercised,21host guards; unsupported sourceILLEGAL not emulated.\n\n'
        'SCOPE\nHost directly enters the boundary task and supplies player pose/tile; stair pose/button and two source entries are also declared host fixtures. Five contexts initially run;16including renderer are blocked. BIOS is a preserve-register RTS adapter and CD completion an external event after a real task switch. Assisted-startup RAM/SSP remain. New EDC4 is created but not executed. Indoor rendering/world/input/natural walking,other tasks/audio/boot/global GPU/scanout/backend accuracy and full playable game remain unfinished.\n\n'
        'EARLIER VERIFIED WORK\n24same-device C interior loading/rendering cases for maps1/2/3 and16street/world/overlay cases remain separate proofs. They are not automatically extended by these transitions.135selected components(122CPU/13GPU) is not a completion percentage.\n\n'
        'WHO / PROMPTS\nCodex coordinator generated the fixed factory/task-create blocks and connected harness. No new model code prompt or training;171previously accepted local-model instruction bodies remain. IDs4/5/6/7 were inspected and found unscheduled in the source table; their records were preserved. Advertising assistant/source-reviewed lesson retained. Native Chat still unverified after prior observation timeouts.\n\n'
        'NEXT\n' + '\n'.join(checkpoint['next_work']) + '\n\nAUDIT\n' + str(out) + '\nFull goal active/incomplete.\n')
    (ROOT / 'CURRENT DECOMPILATION.txt').write_text(note)
    (out / 'readable-results.txt').write_text(note)
    save(ROOT / 'verification/scheduled-entrance-review.json', {'recorded_at': now, 'directory': str(out)})
    print(json.dumps({'audit': str(out), 'cases': 6, 'removals': 12, 'created_EDC4_context_reuses': 2, 'whole_goal_complete': False}))


if __name__ == '__main__':
    main()
