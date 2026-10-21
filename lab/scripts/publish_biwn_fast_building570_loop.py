"""Update the existing optional preview only after its continuous loop passes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    proof_path = ROOT / 'verification/fast-building570-loop-current.json'
    proof = json.loads(proof_path.read_text())
    assert proof['status'] == 'terminal_continuous_outdoor_building570_outdoor_source_match'
    assert proof['no_intermediate_restore'] and all(proof['segment_checks'].values())
    out = Path(proof['directory'])
    comparison = json.loads(Path(proof['comparison']).read_text())
    assert [k for k, v in comparison['checks'].items() if not v] == ['DSP_owned_positive']
    assert comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    png = out / 'C/final-frame.png'
    assert png.read_bytes() == (out / 'reference/final-frame.png').read_bytes()
    gpu = json.loads((out / 'C/regular-GPU-bundles/report.json').read_text())
    recipe_path = ROOT / 'verification/outdoor-restoration-preview-recipe.json'
    previous = json.loads(recipe_path.read_text())
    old_checkpoint = previous['candidate'][previous['candidate'].index('--restore-original-report') + 1]
    imported = json.loads(Path(proof['explicit_core_import_proof']).read_text())
    assert imported['source_checkpoint'] == proof['initial_checkpoint']
    assert imported['new_original_checkpoint'] == old_checkpoint
    for name, expected in previous['hashes'].items():
        assert sha(Path(name)) == expected, name
    now = datetime.now(timezone.utc)
    backup = ROOT / 'config-backups' / now.strftime('%Y%m%dT%H%M%S.%fZ') / 'before-continuous-building570-preview'
    backup.mkdir(parents=True)
    shutil.copy2(recipe_path, backup / recipe_path.name)
    shutil.copy2(proof_path, backup / proof_path.name)
    proof.update(default_preview_updated=True, GPU_source_instructions=gpu['C_source_instructions'],
                 GPU_counter_units='Ownership counts are callback bundles, including existing delayed pairs.',
                 source_scene570_arrival_verified=True, ordinary_controller_exit_verified=True,
                 scene_RAM_transplant=False, player_relocation=False, new_code_overlay=False,
                 native_keyboard_verified=False, physical_audio_verified=False)
    proof_path.write_text(json.dumps(proof, indent=2) + '\n')
    # Preserve the completed runtime protocol; publication metadata lives in
    # the current proof rather than changing the tested process record.
    extra = [proof_path, out / 'protocol.json', Path(proof['comparison']), Path(proof['raw_comparison']), out / 'input.json', Path(proof['finalizer']), Path(__file__).resolve()]
    command = proof['commands']['C']
    for flag in ['--CPU-candidate', '--native-CPU-candidate']:
        path = Path(command[command.index(flag) + 1])
        extra += [path, Path(json.loads(path.read_text())['library'])]
    hashes = dict(previous['hashes'])
    hashes.update(proof['hashes'])
    for path in extra:
        hashes[str(path)] = sha(path)
    recipe = dict(previous, recorded_at=now.isoformat(), verification=proof['comparison'],
                  candidate=command, frames=4600, hashes=hashes,
                  continuous_building570_loop_proof=str(proof_path), native_window_verified=False,
                  scope=proof['scope'] + ' The optional O preview now starts from the exact checked route checkpoint, one original frame before its previous seed, and includes both checked exit instruction cases. Scripted4600frame acceptance does not prove arbitrary keyboard input or native-window speed.')
    recipe_path.write_text(json.dumps(recipe, indent=2) + '\n')
    caption = ('Checked outdoor → building570 → outdoor loop:4,600 uninterrupted frames from the exact naturally reached outdoor '
               'checkpoint, using ordinary recorded buttons and the faster GPU backend. No checkpoint is restored between '
               'movement, building entry and exit. CPU instruction states/costs, every frame RAM/video/PCM and final machine '
               'match the original; both joined segments also reproduce their earlier checked results. The existing18-byte '
               'repair is inherited; no RAM transplant, player relocation or new repair. DSP stayed inactive and PCM was silent. '
               'The checkpoint core hashes differ; separate pinned-pair and exact-state compatibility checks qualify this transfer. '
               'This is recorded output. Native keyboard/Chat display, physical audio and standalone play remain unverified.')
    manifest = dict(relative_png='verified-previews/latest-checked-scene.png', png_sha256=sha(png),
                    source_frame=4600, checked_frames=4600, scene_mode=1, retained_scene_index=570,
                    scene_RAM_transplant=False, player_position_injected=False, source_report=str(proof_path),
                    comparison=proof['comparison'], native_Chat_verified=False, live_gameplay=False,
                    whole_game_complete=False, verified_caption=caption)
    for folder, tag in [(ROOT, 'workspace'), (RUNTIME, 'runtime')]:
        target = backup / tag
        target.mkdir()
        for name in ['latest-scene.json', 'latest-checked-scene.png']:
            shutil.copy2(folder / 'verified-previews' / name, target / name)
        shutil.copy2(png, folder / 'verified-previews/latest-checked-scene.png')
        shutil.copy2(png, folder / 'verified-previews/building570-continuous-loop.png')
        (folder / 'verified-previews/latest-scene.json').write_text(json.dumps(manifest, indent=2) + '\n')
    report = dict(status='optional_outdoor_preview_updated_after_continuous_building_loop',
                  recorded_at=now.isoformat(), recipe=str(recipe_path), recipe_sha256=sha(recipe_path),
                  proof=str(proof_path), pinned_files=len(hashes), previous_initial_checkpoint=old_checkpoint,
                  initial_checkpoint=proof['initial_checkpoint'], initial_checkpoint_one_original_frame_earlier=True,
                  native_window_verified=False, default_P_unchanged=True, whole_game_complete=False)
    (ROOT / 'verification/fast-building570-preview-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
