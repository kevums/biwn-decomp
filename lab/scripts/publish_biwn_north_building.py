"""Publish only the checked source frame and scoped building570 route facts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RT = Path.home() / '.lmstudio/local-ai-lab'


def main():
    path = ROOT / 'verification/north-building-route-current.json'
    proof = json.loads(path.read_text())
    assert proof['status'] == 'terminal_natural_outdoor_to_building570_source_match'
    out = Path(proof['directory'])
    comparison = json.loads((out / 'comparison.json').read_text())
    assert [k for k, v in comparison['checks'].items() if not v] == ['DSP_owned_positive']
    assert comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    gpu = json.loads((out / 'C/regular-GPU-bundles/report.json').read_text())
    source_png = out / 'C/final-frame.png'
    assert source_png.read_bytes() == (out / 'reference/final-frame.png').read_bytes()
    assert not any((out / 'C/frontend-PCM.s16le').read_bytes())
    now = datetime.now(timezone.utc)
    proof.update(recorded_at=now.isoformat(), ordinary_controller_indoor_entry_verified=True,
                 final_scene_index=570, final_floor=0, source_scene_mode=2,
                 GPU_counter_units='Ownership counts are callback bundles, including existing delayed pairs.',
                 GPU_source_instructions=gpu['C_source_instructions'], DSP_counts=comparison['DSP_counts'],
                 planning_reference_reproduced_exactly=True, scene_RAM_transplant=False,
                 player_position_injected=False, source_RAM_scope='Exact naturally reached original checkpoint after200 outdoor movement frames; inherited18byte repair.',
                 native_keyboard_verified=False, whole_game_complete=False,
                 implementation_authorship='Coordinator recovered rectangle route and steering; deterministic original/C comparison. No local-model planning or new weights in this route.')
    path.write_text(json.dumps(proof, indent=2) + '\n')
    caption = ('Checked building570 arrival: ordinary buttons traverse outdoor rectangles and enter building570 on floor0 '
               'from the naturally reached outdoor checkpoint. All4,000 recorded frames, CPU instruction states/costs, '
               'RAM/video/PCM and final machine match original CPU/GPU execution. No scene RAM transplant, player relocation '
               'or new code repair; the existing18byte marker repair is inherited. DSP stayed inactive and PCM was silent. '
               'This is a checkpoint continuation. The continuous merchant/elevator route remains pending after a source byte-guard rejection; '
               'a repaired bridge replay is active. Native keyboard/Chat display, physical audio and standalone play remain unverified.')
    manifest = dict(relative_png='verified-previews/latest-checked-scene.png',
                    png_sha256=hashlib.sha256(source_png.read_bytes()).hexdigest(), source_frame=4000, checked_frames=4000,
                    scene_mode=2, scene_index=570, scene_RAM_transplant=False, player_position_injected=False,
                    source_report=str(path), comparison=str(out / 'comparison.json'), native_Chat_verified=False,
                    live_gameplay=False, whole_game_complete=False, verified_caption=caption)
    backup = ROOT / 'config-backups' / now.strftime('%Y%m%dT%H%M%S.%fZ') / 'before-building570-image'
    for folder in [ROOT, RT]:
        tag = 'workspace' if folder == ROOT else 'runtime'
        target = backup / tag
        target.mkdir(parents=True)
        for name in ['latest-scene.json', 'latest-checked-scene.png']:
            shutil.copy2(folder / 'verified-previews' / name, target / name)
        shutil.copy2(source_png, folder / 'verified-previews/latest-checked-scene.png')
        shutil.copy2(source_png, folder / 'verified-previews/building570-arrival.png')
        (folder / 'verified-previews/latest-scene.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(caption)


if __name__ == '__main__':
    main()
