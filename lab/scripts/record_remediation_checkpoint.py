"""Record completed remediation/decomp artifacts without claiming the full goal is done."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def read(path): return json.loads(path.read_text())
def write(path, value): path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    now = datetime.now(timezone.utc).isoformat()
    job = ROOT / 'training/game/20261012T222054.879303Z/jobs/20261012T222116.372520Z'
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    copy = read(ROOT / 'verification/biwn-copy-checks.json')
    assert copy['status'] == 'copy_bytes_and_device_command_plan_matched_original_CPU'
    hybrid = read(ROOT / 'verification/cpu-remediation-hybrid-package.json')
    assert hybrid['native_load_verified'] and hybrid['combined_heldout_loss'] == 1.887
    backup = ROOT / 'config-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') / 'remediation-progress'
    backup.mkdir(parents=True)
    names = ['setup-status.json', 'requirements-audit.json', 'current-runtime-state.json', 'everyday-inference.json', 'cpu-remediation-dataset.json']
    for name in names: shutil.copy2(ROOT / 'verification' / name, backup / name)
    shutil.copy2(session / 'boot-slice-validation.json', backup / 'boot-slice-validation.json')
    shutil.copy2(ROOT / 'config.json', backup / 'config.json')
    training = 'Real128-step game QLoRA remediation completed on188examples (160CPU-checked synthetic,28prior workflows); validation-selected step96. Teacher-forced heldout loss3.946base to1.887adapter/hybrid. First4bit fusion regressed to3.352 and remains unselected. Hybrid20.8GB package loads at32k; generated-answer review remains required before promotion. Earlier32-step pilot also retained unpromoted.'
    decomp = 'Runtime-guided separate Ghidra listing now18,225instructions (+513),206direct/static entry candidates (+7),206approximateCexports. Five earlier portable components plus forward-byte-copy and device-command planner give seven isolated C components. New1024CPU-byte fixtures,1024device-write traces and7host guards passed. Device effects/completion, whole-game reconstruction, silentHLEaudio, BIOSGPUwait and physical hardware remain unverified. Earlier exact1,032,192-byte assisted RAM stage mapping and short input-response captures retained.'
    frontend = 'Two saved everyday native Chat assistants at32k/oneworker remain available. User now authorizes localAPI progress while locked, with prompts/responses/roles collected afterward. Native visible Chat base/hybrid comparison is still pending; API response comparison recorded separately. Roles use one local model with correlated errors.'
    validation = read(session / 'boot-slice-validation.json')
    validation.update(portable_C_component_count=7, component_count_scope='Five earlier components plus CPU forward-byte copying and a device-command trace planner; these are isolated behaviors, not seven validated whole-game functions.')
    validation['nextstage_copy_C'] = {'report': str(ROOT / 'verification/biwn-copy-checks.json'),
        'CPU_byte_copy_fixtures': copy['CPU_byte_copy_cases'], 'device_command_trace_fixtures': copy['device_command_trace_cases'],
        'host_guards': copy['host_guard_cases'], 'device_behavior_emulated': False, 'scope': copy['limits']}
    validation['copy_components_added_at'] = now
    write(session / 'boot-slice-validation.json', validation)
    dataset = read(ROOT / 'verification/cpu-remediation-dataset.json')
    dataset.update(status='trained_128_steps_selected96_scored_and_packaged_unpromoted', training_job=str(job),
                   checkpoint_selection=str(job / 'checkpoint-selection.json'), loss_review=str(job / 'test-loss-review.json'), hybrid_package=str(job / 'hybrid-package.json'))
    write(ROOT / 'verification/cpu-remediation-dataset.json', dataset)
    package = read(ROOT / 'verification/cpu-remediation-package.json')
    package['promotion'] = 'unselected: 4bit fusion regressed loss3.352 versus adapter1.887; higher-precision hybrid retained separately'
    write(ROOT / 'verification/cpu-remediation-package.json', package)
    setup = read(ROOT / 'verification/setup-status.json')
    setup.update(updated_at_utc=now, training=training, game_work=decomp, frontend=frontend,
                 pending='Full goal incomplete. API response/workflow evaluation continues with post-review authorization; native UI requires unlock; no advertising weight adapter trained.',
                 domain_adaptation='Prior DEV snapshots preserved/indexed; game remediation adapter trained and packaged. Advertising source retrieval ready; no advertising weight adapter trained.')
    write(ROOT / 'verification/setup-status.json', setup)
    audit = read(ROOT / 'verification/requirements-audit.json')
    audit.update(recorded_at_utc=now, goal_status='active incomplete; UI locked, API progress explicitly authorized',
                 previous_goal_turn_classification=audit.get('this_goal_turn_classification'),
                 this_goal_turn_classification='progress: runtime-guided listing/call entries, actual128step CPU-remediation training, hybrid packaging and2048copy differential fixtures')
    for item in audit['requirements']:
        name = item['requirement']
        if name == 'Configure LM frontend on this Mac': item['state'] = frontend
        if name == 'Train/adapt from prior game workflows':
            item['state'] = training
            item['evidence'] += ['verification/cpu-remediation-dataset.json', 'verification/cpu-remediation-loss-review.json', 'verification/cpu-remediation-hybrid-package.json']
        if name == 'Black Ice White Noise Atari Jaguar CD decompilation test':
            item['state'] = decomp
            item['evidence'] += [str(session / 'observed-disassembly-summary.json'), str(session / 'observed-call-entries-summary.json'), 'verification/biwn-copy-checks.json']
    audit['next_safe_work'] = 'Review logged localAPI generated-answer comparison, run bounded source-grounded separate-context roles, investigate MMIO decompiler volatility and BIOS/GPU/audio behavior; continue reconstruction against original CPU checks.'
    write(ROOT / 'verification/requirements-audit.json', audit)
    state = read(ROOT / 'verification/current-runtime-state.json')
    models = json.loads(subprocess.run([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'], cwd=Path.home() / '.lmstudio', check=True, capture_output=True, text=True).stdout)
    state.update(recorded_at=now, models=models, decomp_progress=decomp, visible_chat=frontend,
                 local_inference_jobs='See current model/queued status and saved API comparison protocol; API inference explicitly authorized while locked.',
                 ghidra_jobs='Observed listing and direct-call candidate jobs terminal; approximate C remains unverified.',
                 MCP_updated_evidence='Snapshot refresh carries seven isolated C components and scoped CPU/device-command checks; native follow-up response not yet tested.')
    write(ROOT / 'verification/current-runtime-state.json', state)
    everyday = read(ROOT / 'verification/everyday-inference.json')
    everyday.update(updated_at=now, frontend=frontend, model=models,
                    screen_unlock='NativeUI tool still reports locked; user explicitly permits API continuation and post review.',
                    trained_candidate=str(ROOT / 'verification/cpu-remediation-hybrid-package.json'), full_goal_status='incomplete')
    write(ROOT / 'verification/everyday-inference.json', everyday)
    config = read(ROOT / 'config.json')
    config['chat_frontend']['game']['status'] = 'Saved native32k Chat retained for supervised use. Seven isolated C components checked. Trained hybrid candidate separate/unpromoted; API evaluation now permitted while locked.'
    config['locked_screen_workflow'] = {'authorization': 'nah if locked, dont worry and proceed; will gather in post',
        'interface': 'LM Studio localhost API', 'audit': 'Save complete system/user prompts, responses, role dependencies, evidence and tool results.',
        'native_chat': 'Retained for everyday use; API requests do not appear as native Chat messages.'}
    write(ROOT / 'config.json', config)
    event = {'time': now, 'actor': 'Codex coordinator, native LM Studio local models, MLX training, Ghidra, Unicorn and clang; no Codex subagents',
        'action': 'Runtime-guided disassembly,128step remediation training, higher-precision hybrid packaging and original CPU copy/command checks',
        'training': training, 'decomp': decomp, 'API_authorization': config['locked_screen_workflow'],
        'training_loss_is_generated_accuracy': False,
        'development_failures': ['First8byte observed-instruction attempt accepted truncated Capstone boundary; rejected before promotion,16byte PC sampling and exact export comparison replaced it.',
            '4bit adapter fusion regressed heldout loss; preserved but unselected. Higher-precision adapted modules retain loss1.887.',
            'First copy-check harness hit Unicorn hook sign extension; masked observed values to access width before comparisons.'],
        'evidence': [str(ROOT / 'verification/cpu-remediation-hybrid-package.json'), str(ROOT / 'verification/biwn-copy-checks.json'), str(session / 'observed-call-entries-summary.json')],
        'full_goal': 'active incomplete'}
    with (session / 'activity.jsonl').open('a') as stream: stream.write(json.dumps(event) + '\n')
    with (session / 'workflow.txt').open('a') as stream:
        stream.write('\n' + now + '\n' + training + '\n' + decomp + '\n' + frontend + '\nEvidence: verification/cpu-remediation-hybrid-package.json; verification/biwn-copy-checks.json; verification/cpu-remediation-responses.\n')
    start = ROOT / 'START HERE.txt'
    text = start.read_text().replace('Five portable C components checked;', 'Seven isolated portable C components checked, including a command planner that does not execute devices;')
    text += '\nTRAINED CANDIDATE\nrestoration-cpu-remediation-hybrid-v2 is a separate20.8GB experimental package;32k load checked. Default chats retain their existing model pending generated-answer review.\n\nLOCKED SCREEN WORK\nLocal LM Studio API runs may continue when locked, as requested. Full prompts, responses and role records are saved under verification/cpu-remediation-responses and runs. They do not appear automatically in native Chat history.\n'
    start.write_text(text)
    print(json.dumps({'status': 'checkpoint_recorded_goal_incomplete', 'backup': str(backup), 'portable_components': 7}))


if __name__ == '__main__': main()
