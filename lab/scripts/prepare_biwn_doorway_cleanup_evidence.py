"""Publish standalone CPU proofs, retaining separate connected-scene scope."""
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
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    doorway = read(ROOT / 'verification/biwn-doorway-cpu-checks.json')
    boundary = read(ROOT / 'verification/biwn-boundary-fullCPU-checks.json')
    cleanup = read(ROOT / 'verification/biwn-cleanup-fullCPU-checks.json')
    inventory = read(ROOT / 'verification/biwn-disc-gate-target-inventory.json')
    assert doorway['source_instruction_coverage'] == [75, 75] and doorway['CPU_cases'] == 1070
    assert boundary['source_instruction_coverage'] == [169, 169] and boundary['CPU_cases'] == 1930
    assert cleanup['source_instruction_coverage'] == [226, 226] and cleanup['CPU_cases'] == 556 and cleanup['nested_helper_scripts'] == 0
    assert cleanup['source_sha256']['biwn_transition_cpu.c'] == boundary['source_sha256']['biwn_transition_cpu.c']
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for report in [doorway, boundary, cleanup]:
        for name, digest in report['source_sha256'].items():
            assert sha(source / name) == digest
        assert read(Path(report['directory']) / 'status.json')['status'] == 'terminal_pass'
    checkpoint = {'recorded_at': now, 'scope': 'Standalone full-CPU entrance/boundary/cleanup proofs; actual scheduled boundary-to-loaded-scene transition still unverified.',
                  'doorway_cases': 1070, 'boundary_cases': 1930, 'cleanup_cases': 556,
                  'doorway_instruction_coverage': [75, 75], 'boundary_instruction_coverage': [169, 169],
                  'cleanup_instruction_coverage_including_existing_free': [226, 226],
                  'transition_generated_group_coverage_across_separate_proofs': [308, 308],
                  'host_guards': {'doorway': 18, 'boundary': 29, 'cleanup': 21},
                  'all_CPU_registers_SR_USP_SSP_privateframes_and_main2MBRAM_compared': True,
                  'native_and_Unicorn_references': True, 'ordered_Unicorn_C_bus_compared': True,
                  'boundary_helpers_scripted_in_standalone_proof': True, 'cleanup_helpers_scripted': False,
                  'candidate_gate_records': 291, 'outdoor_payloads_scanned': 611,
                  'startup_tile_record_witnesses': len(inventory['startup_25_tile_record_witness']),
                  'short_empty_segment_spans_unresolved': 329,
                  'actual_scheduled_boundary_loading_verified': False, 'natural_doorway_reachability_verified': False,
                  'actor_task_removal_reuse_during_transition_verified': False,
                  'selected_component_count_changed': False, 'local_model_instruction_bodies': 171,
                  'new_code_authorship': 'Codex coordinator; no local-model source prompt or training for these blocks.',
                  'reports': {'doorway': str(ROOT / 'verification/biwn-doorway-cpu-checks.json'),
                              'boundary': str(ROOT / 'verification/biwn-boundary-fullCPU-checks.json'),
                              'cleanup': str(ROOT / 'verification/biwn-cleanup-fullCPU-checks.json')},
                  'whole_game_complete': False, 'playable_rebuilt_game': False, 'native_Chat_verified': False,
                  'next_work': 'Connect actual source entrance/boundary/cleanup with scheduler yield, actor removal/context reuse and full C loading on retained device state; exercise actual interior targets beyond first four maps.'}
    save(ROOT / 'verification/doorway-boundary-cleanup-checkpoint.json', checkpoint)
    for name in ['boot-slice-validation.json', 'emulator-runtime/summary.json']:
        path = session / name
        state = read(path)
        state['doorway_boundary_cleanup_checkpoint'] = checkpoint
        save(path, state)
    for name in ['config.json', 'corpus/game/project-intake.json', 'verification/setup-status.json',
                 'verification/current-runtime-state.json', 'verification/requirements-audit.json']:
        path = ROOT / name
        state = read(path)
        state['doorway_boundary_cleanup_checkpoint'] = checkpoint
        if name == 'verification/requirements-audit.json':
            state.update(recorded_at_utc=now, this_goal_turn_classification='Progress: 1070 doorway,1930 boundary and556 actual cleanup fullCPU comparisons passed; standalone scope, full goal active.', next_safe_work=checkpoint['next_work'])
        if name == 'verification/current-runtime-state.json':
            state.update(recorded_at=now, emulator_jobs='Terminal: standalone doorway,boundary andactual cleanup comparisons passed. No active emulator job.')
        save(path, state)
    out = ROOT / 'verification/doorway-boundary-cleanup-review' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    (out / 'snapshot').mkdir(parents=True)
    files = [source / name for name in ['biwn_doorway_cpu.c', 'biwn_doorway_cpu.h', 'biwn_transition_cpu.c', 'biwn_transition_cpu.h']]
    files += [ROOT / 'scripts' / name for name in ['inspect_biwn_disc_gate_targets.py', 'generate_biwn_doorway_cpu.py',
              'generate_biwn_transition_cpu.py', 'check_biwn_doorway_cpu.py', 'check_biwn_boundary_full_cpu.py',
              'check_biwn_cleanup_full_cpu.py', 'prepare_biwn_doorway_cleanup_evidence.py']]
    files += [ROOT / 'verification' / name for name in ['biwn-doorway-cpu-checks.json', 'biwn-boundary-fullCPU-checks.json',
              'biwn-cleanup-fullCPU-checks.json', 'doorway-boundary-cleanup-checkpoint.json']]
    for path in files:
        shutil.copy2(path, out / 'snapshot' / path.name)
    save(out / 'manifest.json', {'recorded_at': now, 'files': {str(path): sha(path) for path in files},
         'checkpoint': checkpoint, 'whole_goal_complete': False,
         'repairs': ['Generator initially removed sx8/shift despite source uses; strict compilation rejected it. Restored helpers before tests.',
                     'Native boundary observer initially omitted queued target/index rereads; supplied them at actual source read instructions before acceptance.',
                     'Level-change fixture initially placed bit6 in the low header byte; expanded valid word fixtures to exercise source BTST.B on the high byte. No forced PCs or erased source actors.']})
    note = '\nDOORWAY / BOUNDARY / CLEANUP CPU CHECKS\n' + now + '\n' + (
        '1070 entrance checks (75/75 instructions),1930 boundary/level-change callers (169/169),556 actual nested cleanup/free checks (226/226 including existing free function) match native M68000 and Unicorn. Complete CPU/SR/both stack banks/private frames/main2MBRAM,ordered Unicorn/C bus and native/C helper states compare. 18/29/21 host guards pass. Boundary standalone helpers remain scripts; cleanup helpers execute actual reconstructed C. One real DF60 stop checkpoint preserves source frames; scheduler not executed there. All308 generated transition-group instructions are exercised across separate boundary/cleanup proofs. The291 candidate gates remain relocated/controlled fixtures, not demonstrated natural doorway entry. Full scheduled boundary-to-loaded-scene, transition actor context removal/reuse, remaining loader branches and full playable game remain unfinished. Component total135/local-model instruction bodies171 unchanged; new source coordinator authored, no new weights/training/defaults/UI changes.\n'
        'Next: ' + checkpoint['next_work'] + '\nAudit: ' + str(out) + '\n')
    with (ROOT / 'CURRENT DECOMPILATION.txt').open('a') as stream:
        stream.write(note)
    (out / 'readable-results.txt').write_text(note)
    save(ROOT / 'verification/doorway-boundary-cleanup-review.json', {'recorded_at': now, 'directory': str(out)})
    print(json.dumps({'audit': str(out), 'cases': [1070, 1930, 556], 'full_goal_complete': False}))


if __name__ == '__main__':
    main()
