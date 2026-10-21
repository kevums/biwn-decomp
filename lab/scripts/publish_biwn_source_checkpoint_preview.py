"""Update optional O only after the same-core source-checkpoint loop passes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def shared_dependencies(libraries):
    found, pending = set(), list(map(Path, libraries))
    while pending:
        path = pending.pop().resolve()
        if path in found:
            continue
        assert path.is_relative_to(ROOT)
        found.add(path)
        result = subprocess.run(['otool', '-L', str(path)], check=True, capture_output=True, text=True)
        for line in result.stdout.splitlines()[1:]:
            name = line.strip().split(' (compatibility version', 1)[0]
            dependency = Path(name)
            if dependency.is_absolute() and dependency.is_relative_to(ROOT):
                assert dependency.exists(), dependency
                pending.append(dependency)
    return found


def main():
    proof_path = ROOT / 'verification/source-checkpoint-building-loop-current.json'
    proof = json.loads(proof_path.read_text())
    assert proof['status'] == 'source_checkpoint_continuous_building570_entry_exit_match'
    assert proof['no_intermediate_restore'] and proof['original_checkpoint_restored'] is False
    assert all(proof['prefix_checks'].values())
    comparison = json.loads(Path(proof['comparison']).read_text())
    failed = [key for key, value in comparison['checks'].items() if not value]
    assert failed == ['DSP_owned_positive'] and comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    assert comparison['checks']['checkpoint_core'] and comparison['checks']['checkpoint_is_verified_source']
    for key in ['source_IRQ_entry', 'source_IRQ_selection']:
        assert proof[key]['Owned'] > 0 and proof[key]['Original'] == proof[key]['Rejected'] == 0
    command = proof['commands']['C']
    assert '--restore-source-report' in command and '--restore-original-report' not in command
    out = Path(proof['directory'])
    assert (out / 'C/final-frame.png').read_bytes() == (out / 'reference/final-frame.png').read_bytes()
    old_path = ROOT / 'verification/outdoor-restoration-preview-recipe.json'
    old_bytes = old_path.read_bytes()
    old = json.loads(old_bytes)
    for name, digest in old['hashes'].items():
        assert sha(name) == digest, name
    now = datetime.now(timezone.utc)
    backup = ROOT / 'config-backups' / now.strftime('%Y%m%dT%H%M%S.%fZ') / 'before-source-checkpoint-preview'
    backup.mkdir(parents=True)
    shutil.copy2(old_path, backup / old_path.name)
    shutil.copy2(proof_path, backup / proof_path.name)
    gpu = json.loads((out / 'C/regular-GPU-bundles/report.json').read_text())
    proof.update(optional_preview_updated=True, GPU_source_instructions=gpu['C_source_instructions'],
                 GPU_counter_units='Owned counts are callback bundles; source instruction count is separate.')
    proof_path.write_text(json.dumps(proof, indent=2) + '\n')
    inputs = set(Path(name) for name in old['hashes'])
    inputs.update([proof_path, Path(proof['comparison']), out / 'protocol.json', out / 'input.json',
                   Path(command[0]), Path(command[1]), Path(__file__).resolve()])
    checkpoint_proof = Path(command[command.index('--source-checkpoint-proof') + 1])
    source_report = Path(command[command.index('--restore-source-report') + 1])
    source_proof = json.loads(checkpoint_proof.read_text())
    inputs.update([checkpoint_proof, source_report, Path(source_proof['comparison']),
                   source_report.parent / 'final-RAM.bin', source_report.parent / 'final-video.bin',
                   source_report.parent / 'final-serialized-state.bin', source_report.parent / 'frontend-PCM.s16le',
                   Path(command[1]).parent / 'biwn_verified_source_checkpoint.py'])
    libraries = [Path(command[command.index('--core') + 1])]
    for flag in ['--CPU-candidate', '--native-CPU-candidate', '--native-GPU-candidate', '--DSP-router-candidate']:
        manifest = Path(command[command.index(flag) + 1])
        inputs.add(manifest)
        value = json.loads(manifest.read_text())
        if 'library' in value:
            libraries.append(Path(value['library']))
        for key in ['CPU_library', 'cost_library', 'original_marker_CPU_library']:
            if key in value:
                libraries.append(Path(value[key]))
    closure = shared_dependencies(libraries)
    inputs.update(closure)
    hashes = {str(path): sha(path) for path in sorted(inputs)}
    recipe = dict(status='verified_experimental_recipe', recorded_at=now.isoformat(), verification=proof['comparison'],
                  candidate=command, frames=4600, DSP_inactive_qualified=True, DSP_execution_verified=False,
                  hashes=hashes, project_shared_library_dependencies=sorted(map(str, closure)),
                  project_dependency_closure_checked=True, legacy_recipe_pins_retained=True,
                  source_checkpoint_proof=str(checkpoint_proof), continuous_source_checkpoint_loop_proof=str(proof_path),
                  initial_checkpoint_origin='verified_source_execution', inherited_program_repair_bytes=18,
                  exact_same_core_checkpoint_restore=True, source_IRQ_selection_and_entry=True,
                  attack_CPU_body_included_but_not_exercised_in_this_route=True,
                  optional_preview_updated=True, default_frame_runtime_promoted=False,
                  native_keyboard_verified=False, physical_audio_verified=False, whole_game_complete=False,
                  scope=proof['scope'] + ' Optional O now restores this checked source-produced outdoor state. Its attack CPU replacement is included, but this route has zero attack calls; separate17call gameplay proof covers that body. Native window speed, physical keyboard/audio and arbitrary input remain unverified.')
    candidate = backup / 'new-outdoor-recipe.json'
    candidate.write_text(json.dumps(recipe, indent=2) + '\n')
    prepare = subprocess.run([sys.executable, str(ROOT / 'scripts/run_biwn_interactive.py'), '--recipe', str(candidate), '--check-only'],
                             capture_output=True, text=True)
    (backup / 'candidate-check.log').write_text(prepare.stdout + prepare.stderr)
    assert prepare.returncode == 0, prepare.stderr
    # Switch only this optional recipe. Any launcher failure restores the prior
    # file; existing preview processes have already loaded their own settings.
    old_path.write_bytes(candidate.read_bytes())
    launcher_checks = []
    try:
        for base in [ROOT, RUNTIME]:
            command_check = [str(base / 'Outdoor Restoration Preview.command'), '--check-only']
            result = subprocess.run(command_check, capture_output=True, text=True)
            (backup / ('workspace-check.log' if base == ROOT else 'installed-check.log')).write_text(result.stdout + result.stderr)
            assert result.returncode == 0, result.stderr
            line = result.stdout.splitlines()[-1]
            prepared = json.loads(line)
            assert prepared['status'] == 'validated_not_launched'
            assert '--restore-source-report' in prepared['command'] and '--source-CPU-IRQ-entry' in prepared['command']
            assert '--restore-original-report' not in prepared['command']
            launcher_checks.append(dict(command=command_check, status=prepared['status'], recipe_candidate=prepared['command']))
    except BaseException:
        old_path.write_bytes(old_bytes)
        proof_path.write_bytes((backup / proof_path.name).read_bytes())
        raise
    for base in [ROOT, RUNTIME]:
        shutil.copy2(out / 'C/final-frame.png', base / 'verified-previews/source-checkpoint-building-loop.png')
    report = dict(status='optional_outdoor_preview_uses_verified_source_checkpoint_and_source_IRQ',
                  recorded_at=now.isoformat(), recipe=str(old_path), recipe_sha256=sha(old_path),
                  proof=str(proof_path), pinned_files=len(hashes), dependency_libraries=len(closure),
                  launcher_checks=launcher_checks, previous_recipe_backup=str(backup / old_path.name),
                  source_checkpoint=proof['source_checkpoint'], default_P_changed=False,
                  native_window_verified=False, physical_audio_verified=False, whole_game_complete=False,
                  scope=recipe['scope'])
    for base in [ROOT, RUNTIME]:
        (base / 'verification/source-checkpoint-preview-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['status', 'pinned_files', 'dependency_libraries', 'native_window_verified']}), flush=True)


if __name__ == '__main__':
    main()
