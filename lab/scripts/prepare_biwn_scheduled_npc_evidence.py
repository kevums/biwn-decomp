"""Publish scoped actual NPC execution; retain separate older scene proofs."""
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
    report = read(ROOT / 'verification/biwn-scheduled-npc-checks.json')
    guards = read(ROOT / 'verification/biwn-npc-guard-checks.json')
    directory = Path(report['directory'])
    assert read(directory / 'status.json')['status'] == 'terminal_pass'
    assert [report['cases'], report['NPC_iterations'], report['task_creations'], report['task_removals']] == [4, 20, 4, 12]
    assert report['source_group_instruction_coverage']['npc'] == [136, 285] and guards['host_guards'] == 21
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for name, digest in report['source_sha256'].items():
        assert sha(source / name) == digest
    assert sha(ROOT / 'scripts/check_biwn_scheduled_npc.py') == report['test_script_sha256']
    assert guards['source_sha256']['biwn_npc_cpu.c'] == report['source_sha256']['biwn_npc_cpu.c']
    fixtures = read(directory / 'fixtures.json')
    for row in fixtures:
        assert 0xedc4 in row['native']['steps']
        iterations = [event for event in row['C']['events'] if 'npc_iteration' in event]
        assert len(iterations) == row['NPC_iterations']
        assert row['C']['device']['original_GPUExec1_calls'] == 0
        assert not row['C']['device']['game_frames_executed']
    entrance = read(ROOT / 'verification/biwn-scheduled-entrance-checks.json')
    assert entrance['cases'] == 6 and entrance['task_creations'] == 2
    checkpoint = {key: report[key] for key in ['recorded_at', 'status', 'cases', 'source_interiors', 'disc_transfers',
                 'transferred_bytes', 'task_removals', 'task_creations', 'NPC_iterations', 'native_CPU_steps',
                 'source_group_instruction_coverage', 'limits']}
    checkpoint.update(report=str(ROOT / 'verification/biwn-scheduled-npc-checks.json'),
        selected_components=135, processor_components={'CPU': 122, 'GPU': 13}, new_components=0,
        actual_source_created_NPC_executed=True, actual_NPC_entry='EDC4', source_actor_model_ID=21,
        actual_resource_allocation_animation_movement_and_cleanup=True, actual_scheduler_yields_and_removal=True,
        full_CPU_SR_USP_SSP_main2MBRAM_privateframes_and_observed_helper_events_compared=True,
        generated_NPC_instruction_coverage=[136, 285], NPC_host_guards=21,
        dialogue_message_purchase_paths_verified=False, renderer_or_sprite_queue_consumer_executed=False,
        natural_walking_input_verified=False, uninterrupted_world_loop_verified=False,
        global_GPU_architecture_state_compared=False, original_CPU_or_GPU_execution_on_C_side=False,
        previous_six_case_creation_only_checkpoint_retained=True,
        checked_execution_answer='The newer four-case follow-on test runs the actual source-created EDC4 task for20iterations, then checks its resource cleanup and TRAP2 removal. The older six-case doorway test stopped before that task executed.',
        checked_playability_answer='The game is still not playable. Dialogue/purchases, renderer/sprite consumption, natural player input/world-loop control and other full-game work remain unverified.',
        local_model_instruction_bodies=171, new_code_authorship='Codex coordinator; no model code prompt/training for the NPC blocks.',
        whole_game_complete=False, playable=False, native_Chat_verified=False,
        next_work=['Connect indoor renderer/sprite queue consumption to live NPC tasks/world/input and source transitions.',
                   'Implement and verify merchant dialogue/input/message/purchase branches and remaining tasks/assets.',
                   'Finish remaining loader/factory/boot/audio/globalGPU/scanout/hardware work; full game remains unfinished.',
                   'Validate usable local/advertising inference and visible native Chat; model benchmark semantic failures remain open.'])
    save(ROOT / 'verification/scheduled-NPC-checkpoint.json', checkpoint)
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    for name in ['boot-slice-validation.json', 'emulator-runtime/summary.json']:
        path = session / name
        state = read(path)
        state['scheduled_NPC_checkpoint'] = checkpoint
        save(path, state)
    for name in ['config.json', 'corpus/game/project-intake.json', 'verification/setup-status.json',
                 'verification/current-runtime-state.json', 'verification/requirements-audit.json']:
        path = ROOT / name
        state = read(path)
        state['scheduled_NPC_checkpoint'] = checkpoint
        if name == 'verification/requirements-audit.json':
            state.update(recorded_at_utc=now, this_goal_turn_classification='Progress: four actual source-created EDC4 task lifecycle cases/20iterations match native/C full CPU/RAM;21host guards. Source retrieval compact citation fixed. Full goal active.', next_safe_work=checkpoint['next_work'])
        if name == 'verification/current-runtime-state.json':
            state.update(recorded_at=now, emulator_jobs='Terminal: four source-created EDC4 execution/removal cases and21NPC guards passed. No active emulator job.')
        save(path, state)
    out = ROOT / 'verification/scheduled-NPC-review' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    (out / 'snapshot').mkdir(parents=True)
    files = [source / name for name in ['biwn_npc_cpu.c', 'biwn_npc_cpu.h']]
    files += [ROOT / 'scripts' / name for name in ['generate_biwn_npc_cpu.py', 'check_biwn_scheduled_npc.py',
              'check_biwn_npc_guards.py', 'prepare_biwn_scheduled_npc_evidence.py']]
    files += [ROOT / 'verification' / name for name in ['biwn-scheduled-npc-checks.json', 'biwn-npc-guard-checks.json',
              'scheduled-NPC-checkpoint.json', 'NPC-report-name-collision.json']]
    for path in files:
        shutil.copy2(path, out / 'snapshot' / path.name)
    save(out / 'manifest.json', {'recorded_at': now, 'files': {str(path): sha(path) for path in files}, 'checkpoint': checkpoint,
         'repairs': ['Added actual DFA6 getter blocks; native old F4D8 getter is not logged as a provider because the already-checked C actor implements it internally.',
                     'New cloned harness initially reused the prior report name. Restored exact six-case entrance report from accepted snapshot and assigned dedicated NPC directory/library/report names; raw collision evidence retained.',
                     'Corrected source-interior metadata to312/313/314 and generated group count285. No source path/data/task/actor record erased to make cases pass.'],
         'whole_goal_complete': False})
    note = ('BLACK ICE WHITE NOISE — ACTUAL SOURCE-CREATED NPC LIFECYCLE\n' + now + '\n\n'
        'Four controlled gate/stair-to-NPC cases run the actual EDC4 task created on interior314 after312->313->314. Twenty loop iterations match original nativeCPU versus C, including model21 acquisition/output allocation,distance/facing,animation,movement/collision/geometry helpers and actual scheduler yields. A declared killword then drives source output/model release and TRAP2 removal. Full CPU/SR/both stack banks,whole2MBRAM/private frames and observed helper/yield/removal/disc events match. Four task creations,12removals including old actors,24CDtransfers/1,399,216bytes,528,312native reference CPUsteps. C side executes no original CPU/GPU. New NPC group136/285instructions exercised;21host guards.\n\n'
        'LIMITS\nRenderer/spritequeue consumption, dialogue/messages/purchases, natural player input and uninterrupted worldloop are not verified. World/other tasks are blocked for the actor phase; startup/pose/button/host entries/killword/BIOS and external CD completion remain fixtures. Existing synchronous movementGPUmath device is used; no globalGPUarchitecture/scanout/hardware/FPS proof. Full playable game remains unfinished.\n\n'
        'EARLIER WORK\nThe six-case source doorway/context-reuse checkpoint,24interiorCloading/rendering cases and16street/world/overlay cases remain separate proofs.135selectedcomponents(122CPU/13GPU) is not a completionpercentage.\n\n'
        'AUTHORSHIP / LOCAL MODELS\nNew NPC source/harness coordinator authored;171prior accepted local-model instruction bodies unchanged. Temporary coder evaluation completed four questions in about2seconds each but failed semantic/tool/retrieval review; original27Bbase restored. Olsen2001 citation retrieval and final unexecuted-tool-markup detection fixed without changing source PDFs or filtering responses. No training/weights/defaults/preset changes. NativeChat still unverified.\n\n'
        'NEXT\n' + '\n'.join(checkpoint['next_work']) + '\n\nAUDIT\n' + str(out) + '\nFull goal active/incomplete.\n')
    (ROOT / 'CURRENT DECOMPILATION.txt').write_text(note)
    (out / 'readable-results.txt').write_text(note)
    save(ROOT / 'verification/scheduled-NPC-review.json', {'recorded_at': now, 'directory': str(out)})
    print(json.dumps({'audit': str(out), 'NPC_cases': 4, 'NPC_iterations': 20, 'instruction_coverage': [136, 285], 'host_guards': 21}))


if __name__ == '__main__':
    main()
