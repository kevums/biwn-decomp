"""Publish the separate three-task actor proof without promoting scripted AI."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    proof = read(ROOT / 'verification/biwn-actor-task-runtime-checks.json')
    assert (proof['cases'], proof['actor_iterations'], proof['task_handoffs']) == (128, 1024, 3072)
    assert proof['whole2MBRAM_including_private_stacks_compared'] and proof['fullCPU_SR_SSP_USP_compared']
    out = Path(proof['directory'])
    assert read(out / 'status.json')['status'] == 'terminal_pass'
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for name, digest in proof['source_sha256'].items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    snapshot = out / 'harness-snapshot'
    snapshot.mkdir(exist_ok=True)
    files = [ROOT / 'scripts' / name for name in [
        'check_biwn_actor_task_runtime.py', 'check_biwn_actor_task.py',
        'check_biwn_render_display_runtime.py', 'check_biwn_scheduler.py',
        'check_biwn_world_update.py', 'check_biwn_boundary_handlers.py',
        'check_biwn_scene_loading.py', 'check_biwn_startup_services.py',
        'check_biwn_actor_creation.py']]
    files += [source / name for name in proof['source_sha256']]
    files += [ROOT / name for name in ['animation_renderer.py', 'inventory_renderer.py']]
    for path in files:
        shutil.copy2(path, snapshot / path.name)
    save(snapshot / 'manifest.json', {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    validation = read(session / 'boot-slice-validation.json')
    assert validation['portable_C_component_count'] == 96
    backup = ROOT / 'verification/actor-task-runtime-backup' / out.name
    backup.mkdir(parents=True, exist_ok=True)
    paths = ['chat_tools.py', 'scripts/summarize_biwn_checks.py', 'presets/Game Assistant.system.txt',
             'presets/Game Assistant.preset.json', 'CURRENT DECOMPILATION.txt', 'START HERE.txt',
             'config.json', 'corpus/game/project-intake.json']
    for name in paths:
        target = backup / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    shutil.copy2(session / 'boot-slice-validation.json', backup / 'boot-slice-validation.json')
    validation['actor_task_scheduler_integration'] = proof
    save(session / 'boot-slice-validation.json', validation)
    path = ROOT / 'scripts/summarize_biwn_checks.py'
    text = path.read_text()
    needle = "    save(folder / 'emulator-runtime/summary.json', runtime)"
    block = """    actor_task_runtime_path=root/'verification/biwn-actor-task-runtime-checks.json'
    if actor_task_runtime_path.exists():
        linked=json.loads(actor_task_runtime_path.read_text())
        if linked['cases']!=128 or linked['task_handoffs']!=3072:raise ValueError('Actor scheduler proof incomplete')
        runtime['CPU_actor_task_scheduler_integration']={**linked,'report':str(actor_task_runtime_path)}
"""
    assert 'CPU_actor_task_scheduler_integration' not in text
    path.write_text(text.replace(needle, block + needle))
    scope = ('The F4D8 caller now passes a separate three-context integration with two idle tasks: '
             '128 cases, 1,024 actor iterations and 3,072 real DF60/TRAP0/DE08/RTE handoffs. '
             'All registers, SR, USP/SSP and the complete 2 MB RAM, including private stacks and public headers, match native execution. '
             'Six helpers remain scripted: RNG, waypoint, steering predicates and movement. Movement field changes are explicit test fixtures. '
             'This is separate from the 21-context startup, where actor task bodies remain blocked. Removal TRAP2 is not executed. '
             'The published count remains 96 pending real helper integration. The full game remains incomplete.')
    path = ROOT / 'chat_tools.py'
    text = path.read_text()
    text = text.replace('Use actor_task forF4D8persistent AI caller,512CPU boundary tests/fullregisters/CCR/stack, pendingDF60/DF7A andunintegrated steering/movement/scheduler scope; itdoesnot mean actors nowrun in startup.',
                        'Use actor_task for the F4D8 caller: 512 boundary cases plus a separate 128-case actor/two-idle integration with 3072 real scheduler handoffs. Six helpers remain scripted; actor bodies are still blocked in the 21-context startup; removal remains pending.')
    start = text.index("        compact['checked_actor_task_scope']=", text.index("    if topic == 'actor_task':"))
    end = text.index('\n', start)
    text = text[:start] + "        compact['CPU_actor_task_scheduler_integration']=observed['CPU_actor_task_scheduler_integration']\n        compact['checked_actor_task_scope']=" + repr(scope) + text[end:]
    path.write_text(text)
    path = ROOT / 'presets/Game Assistant.system.txt'
    text = path.read_text().replace(
        '- actor_task: F4D8 caller boundary proof, full CPU/flags/stack checks, pending scheduler/removal and scripted helpers; not live actor integration.',
        '- actor_task: F4D8 boundary proof and separate actor/two-idle scheduler integration; six scripted helpers, pending removal and no actor execution in the 21-context startup.')
    path.write_text(text)
    path = ROOT / 'presets/Game Assistant.preset.json'
    preset = read(path)
    for field in preset['operation']['fields']:
        if field['key'] == 'llm.prediction.systemPrompt':
            field['value'] = text.strip()
    save(path, preset)
    shutil.copy2(path, Path.home() / '.lmstudio/config-presets/Game Assistant.preset.json')
    path = ROOT / 'CURRENT DECOMPILATION.txt'
    text = path.read_text()
    first = text.index('LATEST IN-PROGRESS WORK')
    last = text.index('PUBLISHED RUNTIME CHECKPOINT')
    path.write_text(text[:first] + 'LATEST ACTOR SCHEDULING RESULT\n' + scope + '\n\n' +
                    'The earlier 512-case caller boundary proof still covers all 191 reachable instructions and 15 host guards. '
                    'Accepted C and the integration harness were authored by Codex and checked against original CPU execution. '
                    'No local model authored or independently verified this C. Native Chat is locked; local inference checks are saved separately.\n\n' +
                    str(ROOT / 'verification/biwn-actor-task-runtime-checks.json') + '\n\n' + text[last:])
    path = ROOT / 'START HERE.txt'
    text = path.read_text().replace('New actor-task caller boundary proof passes512CPUcases; live scheduler/helper integration is pending. Published runtime count remains96.', scope)
    path.write_text(text)
    for name in ['config.json', 'corpus/game/project-intake.json'] + ['verification/' + n for n in [
            'setup-status.json', 'current-runtime-state.json', 'everyday-inference.json', 'requirements-audit.json']]:
        path = ROOT / name
        value = read(path)
        value['actor_task_scheduler_progress'] = scope
        value['actor_task_scheduler_evidence'] = str(ROOT / 'verification/biwn-actor-task-runtime-checks.json')
        # Retain the preceding boundary entry as explicitly historical evidence.
        if 'actor_task_boundary_progress' in value:
            value['actor_task_boundary_progress'] = 'Historical boundary checkpoint; superseded for scheduler scope by actor_task_scheduler_progress. ' + value['actor_task_boundary_progress']
        save(path, value)
    for name in ['summarize_biwn_checks.py', 'install_chat_runtime.py']:
        subprocess.run([str(ROOT / '.venv/bin/python'), str(ROOT / 'scripts' / name)], check=True)
    print(json.dumps({'published_components': 96, 'actor_iterations': 1024, 'handoffs': 3072, 'backup': str(backup)}))


if __name__ == '__main__':
    main()
