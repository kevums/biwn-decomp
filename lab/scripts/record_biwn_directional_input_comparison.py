"""Publish the separate Down/Right experiment against accepted source-entry proofs."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
save = lambda p, value: p.write_text(json.dumps(value, indent=2) + '\n')
read = lambda p: json.loads(p.read_text())
accepted = read(ROOT / 'verification/entry-task-material65e0-progress-current.json')['entry_input']
up = Path(accepted['report']).parent
control = Path(accepted['control_report']).parent
down = ROOT / 'verification/BIWN-entry-natural-task-rounds/20261015T193559.358326Z'
review = ROOT / 'verification/easy-firmware-CD-routing/20261015T193559.533976Z'
out = ROOT / 'verification/directional-entry-input' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
points = {name: read(folder / 'native-world-return-checkpoints.json') for name, folder in [('up_left', up), ('down_right', down), ('no_input', control)]}
rows = {}
for name, folder in [('up_left', up), ('down_right', down), ('no_input', control)]:
    report = read(folder / 'report.json')
    native, reconstructed = report['results']
    assert report['all_world_return_checkpoints_equal'] and report['requested_world_returns'] == 120
    assert points[name] == read(folder / 'C-world-return-checkpoints.json')
    assert native['GPU_calls'] == reconstructed['GPU_calls'] and native['polls'] == reconstructed['polls']
    assert reconstructed['C_original_CPU_attempts'] == 0
    startup = read(folder / 'native-startup.json')['startup']
    C_startup = read(folder / 'C-startup.json')['startup']
    for key in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:
        assert startup[key] == C_startup[key], (name, key)
    start, end = points[name][0]['player'], points[name][-1]['player']
    rows[name] = dict(report=str(folder / 'report.json'), world_returns=120,
        post_startup_native_CPU_instructions=native['processor_instructions'],
        startup_native_CPU_instructions=accepted['startup_native_CPU_instructions'],
        total_native_CPU_instructions=accepted['startup_native_CPU_instructions'] + native['processor_instructions'],
        start_X=start['0x49c50'], start_Z=start['0x49c56'], end_X=end['0x49c50'], end_Z=end['0x49c56'],
        all_120_original_CPU_vs_C_checkpoints_equal=True, final_GPU_and_pad_polls_equal=True,
        original_CPU_execution_attempts_on_C_path=0)
assert rows['no_input']['start_Z'] == rows['no_input']['end_Z'] == 40096
assert rows['up_left']['end_Z'] == 40092 and rows['down_right']['end_Z'] == 40101
for name in ['up_left', 'down_right']:
    equal = [a == b for a, b in zip(points[name], points['no_input'])]
    assert all(equal[:5]) and not equal[5]
    rows[name]['first_divergent_return_vs_no_input'] = 6
for row in rows.values():
    assert row['start_X'] == row['end_X'] == 9376
protocol = read(review / 'protocol.json')
answer = protocol['results'][0]
assert not answer['quality_flags'] and 'cannot establish' in answer['answer']
answer['semantic_review'] = 'Accepted proposed-test scope review; test execution and result validation are coordinator work. Same weights, not independent verification.'
protocol['status'] = 'accepted_proposed_test_scope_review'
save(review / 'protocol.json', protocol)
result = dict(status='separate_source_entry_directional_runs_native_C_match', directory=str(out), runs=rows,
    input_plans={'up_left':'Up polls 5-64, Left 65-94, then release', 'down_right':'Down polls 5-64, Right 65-94, then release', 'no_input':'No buttons'},
    interpretation='Bounded emulated directional displacement. Turning and forward/backward are sequential; this does not isolate each button contribution or prove physical walking.',
    local_reviewer=dict(protocol=str(review / 'protocol.json'), seconds=answer['seconds'], words=answer['words'], independent_validation=False),
    current_accepted_entry_pointer_preserved=True, new_training=False, new_model_code=False,
    native_Chat_verified=False, whole_game_complete=False,
    remaining_controls=accepted['remaining_controls'],
    remaining_work=['ordinary authenticated firmware boot','global CD/video/DSP scheduling','remaining helpers/scenes/audio','physical controller and scanout','full C playability'])
save(out / 'report.json', result)
save(ROOT / 'verification/directional-entry-input-current.json', result)
root_session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
installed = Path.home() / '.lmstudio/local-ai-lab'
installed_session = Path(read(installed / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
compact = dict(report=str(out / 'report.json'), up_left_end_Z=40092, down_right_end_Z=40101, no_input_Z=40096,
    X_stays=9376, each_run_world_returns=120, each_run_native_C_matches=True,
    down_right_total_native_CPU_instructions=rows['down_right']['total_native_CPU_instructions'],
    both_input_runs_diverge_from_control_at_return=6,
    counts_are_separate_runs_not_a_single_continuous_run=True, physical_walking_or_playability_proven=False)
for session in [root_session, installed_session]:
    path = session / 'emulator-runtime/summary.json'
    summary = read(path)
    summary['firmware_bootstrap_DSP_progress']['source_stage_loading']['directional_entry_input_comparison'] = compact
    save(path, summary)
audit = 'COORDINATOR: Codex added a separate Down/Right input plan, ran original native and reconstructed C, and compared both with the retained no-input control. No CPU/RAM reset after startup. No local-model code authorship.\n\nLOCAL REVIEWER: Same daily advertising-scholar weights, sequential SDK role, no independent validation.\n'
audit += (review / 'prompts-and-responses.txt').read_text()
audit += '\nRESULTS:\n' + json.dumps(result, indent=2) + '\n'
(out / 'who-prompts-and-responses.txt').write_text(audit)
manifest = {}
for path in [ROOT / 'scripts/check_biwn_entry_natural_task_rounds.py', Path(__file__), down / 'report.json', up / 'report.json', control / 'report.json', review / 'protocol.json']:
    manifest[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
save(out / 'input-manifest.json', manifest)
print(out)
