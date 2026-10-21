"""Promote P only after same-profile Deck/mail, combat and elevator retention.

The initial checkpoint is source-produced and unmodified. P then applies
the same explicit56byte legacy repair set used by its earlier mail profile.
This preview switch does not establish physical input/audio or standalone.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from biwn_verified_unmodified_merchant_checkpoint import verify_source_checkpoint
from publish_biwn_source_checkpoint_preview import shared_dependencies

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def check_comparison(path):
    comparison = json.loads(Path(path).read_text())
    failed = [key for key, value in comparison['checks'].items() if not value]
    assert failed == ['DSP_owned_positive'] and comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    assert comparison['checks']['checkpoint_core'] and comparison['checks']['checkpoint_is_verified_source']
    assert comparison['checks']['no_original_CPU'] and comparison['checks']['no_rejected_CPU']
    for key in ['source_IRQ_entry_positive', 'source_IRQ_selection_positive', 'no_original_IRQ_entry', 'no_rejected_IRQ_entry',
                'no_original_IRQ_selection', 'no_rejected_IRQ_selection']:
        assert comparison['checks'][key], key
    return comparison


def main():
    mail_path = ROOT / 'verification/source-checkpoint-mail-current.json'
    profile_path = ROOT / 'verification/primary-source-profile-current.json'
    mail, profile = [json.loads(p.read_text()) for p in [mail_path, profile_path]]
    assert mail['status'] == 'source_merchant_Deck_mail_roundtrip_match'
    assert profile['status'] == 'source_merchant_combined_repair_combat_and_elevator_profile_match'
    assert mail['inherited_program_repair_bytes'] == profile['inherited_program_repair_bytes'] == 0
    assert mail['post_restore_repair_bytes'] == 56
    assert [c['continuation_repair_bytes'] for c in profile['cases']] == [56, 56, 56]
    assert [c['attack_calls'] for c in profile['cases']] == [9, 8, 0]
    assert [c['damage_instructions'] for c in profile['cases']] == [1, 1, 0]
    assert mail['mail_list_calls'] == mail['mail_message_calls'] == 1 and mail['world_returns'] >= 2
    assert profile['source_checkpoint']['report_sha256'] == mail['source_checkpoint']['report_sha256']
    mail_comparison = check_comparison(mail['comparison'])
    for case in profile['cases']:
        check_comparison(case['comparison'])
    command = next(row['command'][:] for row in mail['commands'] if row['phase'] == 'C')
    assert '--restore-source-report' in command and '--restore-original-report' not in command
    assert '--source-CPU-IRQ-entry' in command
    source_report = Path(command[command.index('--restore-source-report') + 1])
    cold_proof = Path(command[command.index('--source-checkpoint-proof') + 1])
    core = Path(command[command.index('--core') + 1])
    provenance = verify_source_checkpoint(source_report, cold_proof, core)
    now = datetime.now(timezone.utc)
    out = ROOT / 'verification/primary-source-preview-build' / now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    old_path = ROOT / 'verification/interactive-preview-recipe.json'
    old_bytes = old_path.read_bytes()
    (out / 'previous-primary-recipe.json').write_bytes(old_bytes)
    # Keep all known project-runtime pins from the checked optional profile.
    # These are a conservative superset; no O file is rewritten here.
    optional = json.loads((ROOT / 'verification/outdoor-restoration-preview-recipe.json').read_text())
    for path, digest in optional['hashes'].items():
        assert sha(path) == digest, path
    inputs = set(map(Path, optional['hashes']))
    for source, name in [(mail_path, 'mail-proof.json'), (profile_path, 'profile-proof.json'), (cold_proof, 'source-checkpoint-proof.json')]:
        target = out / name
        shutil.copy2(source, target)
        inputs.add(target)
    command[command.index('--source-checkpoint-proof') + 1] = str(out / 'source-checkpoint-proof.json')
    manifest_flags = [('--CPU-candidate', 'CPU-candidate.json'), ('--native-CPU-candidate', 'native-CPU-candidate.json'),
                      ('--native-GPU-candidate', 'GPU-candidate.json'), ('--DSP-router-candidate', 'DSP-candidate.json'),
                      ('--experimental-code-overlay', 'combined-repair.json')]
    libraries = [core]
    for flag, name in manifest_flags:
        source = Path(command[command.index(flag) + 1])
        target = out / name
        shutil.copy2(source, target)
        command[command.index(flag) + 1] = str(target)
        inputs.add(target)
        value = json.loads(target.read_text())
        for key in ['library', 'CPU_library', 'cost_library', 'original_marker_CPU_library']:
            if key in value:
                libraries.append(Path(value[key]))
    source = json.loads(source_report.read_text())
    inputs.update([source_report, Path(json.loads(cold_proof.read_text())['comparison']), Path(mail['comparison']),
                   Path(mail['directory']) / 'protocol.json', Path(mail['observed_PC_counts']),
                   Path(profile['directory']) / 'protocol.json', Path(command[0]), Path(command[1]),
                   Path(command[1]).parent / 'biwn_verified_source_checkpoint.py', Path(__file__).resolve(),
                   ROOT / 'scripts/run_biwn_interactive.py', ROOT / 'Play BIWN Preview.command'])
    inputs.update(Path(case['comparison']) for case in profile['cases'])
    inputs.update(source_report.parent / name for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le'])
    inputs.update(Path(source[key]) for key in ['regular_GPU_report', 'DSP_report', 'CPU_IRQ_report'])
    closure = shared_dependencies(libraries)
    inputs.update(closure)
    hashes = {str(path): sha(path) for path in sorted(inputs)}
    recipe = dict(status='verified_experimental_recipe', recorded_at=now.isoformat(), verification=mail['comparison'],
        candidate=command, frames=200, DSP_inactive_qualified=True, DSP_execution_verified=False,
        hashes=hashes, project_shared_library_dependencies=sorted(map(str, closure)), project_dependency_closure_checked=True,
        legacy_optional_recipe_pins_retained=True, source_checkpoint_proof=str(out / 'source-checkpoint-proof.json'),
        initial_checkpoint_origin='verified_source_execution', inherited_program_repair_bytes=0, post_restore_repair_bytes=56,
        repair_patch_count=3, exact_same_core_checkpoint_restore=True, source_IRQ_selection_and_entry=True,
        mail_roundtrip_proof=str(out / 'mail-proof.json'), combat_elevator_profile_proof=str(out / 'profile-proof.json'),
        default_frame_runtime_promoted=True, native_keyboard_verified=False, physical_audio_verified=False, whole_game_complete=False,
        scope='Primary P starts from the exact unmodified merchant machine produced by the checked23538frame source run, on the same core. It then applies the existing56byte repair set in3patches for Deck/selector/marker behavior. Source CPU/GPU/IRQ is checked on the same profile for200frame Deck/mail/read/exit,120frame unarmed/300frame Beretta combat and1200frame two-floor/outdoor routes. The attack body is CPU-compatible, not the high-level API. DSP is inactive in these continuations; the cold startup separately exercises source DSP. Original queue/ACK/HLE/OP/device/commit services remain. Physical keyboard/audio, arbitrary gameplay, sustained speed and standalone/whole-game completion are unverified.')
    candidate = out / 'candidate-primary-recipe.json'
    save(candidate, recipe)
    prepared = subprocess.run([sys.executable, str(ROOT / 'scripts/run_biwn_interactive.py'), '--recipe', str(candidate), '--check-only'], capture_output=True, text=True)
    (out / 'candidate-check.log').write_text(prepared.stdout + prepared.stderr)
    assert prepared.returncode == 0, prepared.stderr
    checks = []
    try:
        old_path.write_bytes(candidate.read_bytes())
        for base in [ROOT, RUNTIME]:
            result = subprocess.run([str(base / 'Play BIWN Preview.command'), '--check-only'], capture_output=True, text=True)
            (out / ('workspace-P-check.log' if base == ROOT else 'installed-P-check.log')).write_text(result.stdout + result.stderr)
            assert result.returncode == 0, result.stderr
            parsed = json.loads(result.stdout.splitlines()[-1])
            assert parsed['status'] == 'validated_not_launched'
            assert '--restore-source-report' in parsed['command'] and '--source-CPU-IRQ-entry' in parsed['command']
            assert '--restore-original-report' not in parsed['command']
            checks.append(dict(launcher=str(base / 'Play BIWN Preview.command'), status=parsed['status'], command=parsed['command']))
        for base in [ROOT, RUNTIME]:
            result = subprocess.run([str(base / 'Outdoor Restoration Preview.command'), '--check-only'], capture_output=True, text=True)
            assert result.returncode == 0, result.stderr
    except BaseException:
        old_path.write_bytes(old_bytes)
        raise
    report = dict(status='primary_preview_uses_verified_source_merchant_checkpoint_and_source_IRQ', recorded_at=now.isoformat(),
        directory=str(out), recipe=str(old_path), recipe_sha256=sha(old_path), checks=checks, pinned_files=len(hashes),
        project_dependency_libraries=len(closure), source_checkpoint=provenance, inherited_repair_bytes=0, post_restore_repair_bytes=56,
        previous_recipe=str(out / 'previous-primary-recipe.json'), O_recipe_changed=False, existing_preview_process_restarted=False,
        default_P_changed=True, native_window_verified=False, physical_audio_verified=False, whole_game_complete=False, scope=recipe['scope'])
    save(out / 'publication.json', report)
    for base in [ROOT, RUNTIME]:
        save(base / 'verification/primary-source-preview-current.json', report)
        shutil.copy2(Path(mail['directory']) / 'C/frame-90.png', base / 'verified-previews/source-checkpoint-mail.png')
    print(json.dumps({key: report[key] for key in ['status', 'pinned_files', 'project_dependency_libraries', 'post_restore_repair_bytes', 'native_window_verified']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
