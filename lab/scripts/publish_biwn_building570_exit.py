"""Publish the accepted exit instruction extension and its recorded scene."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proof_path = ROOT / 'verification/building570-exit-route-current.json'
    proof = json.loads(proof_path.read_text())
    assert proof['ordinary_controller_exit_verified'] and proof['frames'] == 600
    out = Path(proof['directory'])
    comparison = json.loads((out / 'comparison.json').read_text())
    assert [k for k, v in comparison['checks'].items() if not v] == ['DSP_owned_positive']
    assert comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
    candidate = json.loads((ROOT / 'verification/building570-exit-CPU-experimental-candidate.json').read_text())
    generated = Path(candidate['directory']) / 'biwn_route_CPU.c'
    assert sha(generated) == candidate['source_sha256']
    stable = ROOT / 'projects/black-ice-white-noise/restoration'
    published = stable / 'biwn_scene570_exit_cpu.c'
    # Preserve the exact accepted body. The existing leading provenance comment
    # is the sole publication addition; no behavior is rewritten here.
    assert published.read_text().endswith(generated.read_text())
    prior = json.loads((ROOT / 'verification/controller-direction-library-current.json').read_text())
    dependency = Path(prior['directory']) / 'source/biwn_atomic_startup_math.h'
    destination = stable / dependency.name
    if destination.exists():
        assert destination.read_bytes() == dependency.read_bytes()
    else:
        shutil.copy2(dependency, destination)
    commands = [
        ['clang', '-fsyntax-only', '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(stable), str(published)],
        ['clang', '-fsyntax-only', '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(stable), '-x', 'c', str(stable / 'biwn_scene570_exit_cpu.h')],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True,
                                env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
        logs.append(dict(command=command, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        assert result.returncode == 0, result.stderr
    now = datetime.now(timezone.utc)
    artifact = out / 'source-publication.json'
    publication = dict(recorded_at=now.isoformat(), generated_source=str(generated),
                       generated_sha256=sha(generated), published_source=str(published), published_sha256=sha(published),
                       accepted_body_unchanged=True, header=str(stable / 'biwn_scene570_exit_cpu.h'),
                       dependency=dict(source=str(dependency), published=str(destination), sha256=sha(dependency)),
                       syntax_checks=logs, runtime_proof=str(proof_path),
                       scope='Two accepted instruction cases, not an additional logical function. Syntax checks cover publication only; runtime acceptance is the separate640fixture/600frame evidence. Other PCs delegate to the prior source dispatcher; this is not standalone.')
    artifact.write_text(json.dumps(publication, indent=2) + '\n')
    proof['source_publication'] = str(artifact)
    proof_path.write_text(json.dumps(proof, indent=2) + '\n')
    png = out / 'C/final-frame.png'
    assert png.read_bytes() == (out / 'reference/final-frame.png').read_bytes()
    assert not any((out / 'C/frontend-PCM.s16le').read_bytes())
    caption = ('Checked building570 exit: ordinary controller buttons leave the saved, original/source-matched '
               'indoor570 checkpoint for outdoors. All600 frames, CPU instruction states/costs, RAM/video/PCM '
               'and final machine match the original. Two additional original instruction cases passed640 native '
               'CPU/RAM/cycle fixtures. No scene RAM transplant, player relocation or new repair; the existing18-byte '
               'repair is inherited. DSP stayed inactive and PCM was silent. This is a recorded checkpoint continuation. '
               'Native keyboard/Chat display, physical audio and standalone play remain unverified.')
    manifest = dict(relative_png='verified-previews/latest-checked-scene.png', png_sha256=sha(png),
                    source_frame=600, checked_frames=600, scene_mode=1, retained_scene_index=570,
                    scene_RAM_transplant=False, player_position_injected=False, source_report=str(proof_path),
                    comparison=str(out / 'comparison.json'), native_Chat_verified=False, live_gameplay=False,
                    whole_game_complete=False, verified_caption=caption)
    backup = ROOT / 'config-backups' / now.strftime('%Y%m%dT%H%M%S.%fZ') / 'before-building570-exit-image'
    for folder, tag in [(ROOT, 'workspace'), (RUNTIME, 'runtime')]:
        target = backup / tag
        target.mkdir(parents=True)
        for name in ['latest-scene.json', 'latest-checked-scene.png']:
            shutil.copy2(folder / 'verified-previews' / name, target / name)
        shutil.copy2(png, folder / 'verified-previews/latest-checked-scene.png')
        shutil.copy2(png, folder / 'verified-previews/building570-exit.png')
        (folder / 'verified-previews/latest-scene.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(status='accepted_source_and_recorded_exit_published', publication=str(artifact), caption=caption)))


if __name__ == '__main__':
    main()
