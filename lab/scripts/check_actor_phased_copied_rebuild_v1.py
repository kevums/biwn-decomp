"""Rebuild both changed actor modules with the relocated SDK and compare bytes."""
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha
from publish_geometry_records_progress_v1 import clone


def main():
    bp = V / 'actor-phased-disc-build-v1-current.json'
    b = read(bp)
    source = Path(b['actor_phased_source'])
    dest = P / 'workbench' / source.relative_to(ROOT)
    out = V / 'actor-phased-copied-rebuild-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    paths = [Path(__file__), bp, Path(b['component'])]
    for p in source.iterdir():
        if p.is_file():
            clone(p, dest / p.name)
            assert sha(p) == sha(dest / p.name)
            paths.append(p)
    pieces = []
    for name, artifact in b['actor_phased_artifacts'].items():
        relative = Path('../../../../../builds/actor-phased-v41') / out.name / name
        result = subprocess.run(['make', 'MODULE=' + name, 'BUILD=' + str(relative)], cwd=dest, capture_output=True, text=True)
        log = out / (name + '-copied-build.log')
        log.write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
        binary = (dest / relative / 'native.bin').resolve()
        blob = binary.read_bytes()
        at = artifact['code_address'] - b['resident_address']
        assert blob == Path(artifact['binary']).read_bytes() == Path(b['component']).read_bytes()[at:at+len(blob)]
        saved = out / (name + '-copied.bin')
        clone(binary, saved)
        paths += [log, binary, saved]
        pieces.append(dict(piece=name, bytes=len(blob), copied_binary=str(binary), sha256=sha(binary), byte_identical=True))
    proof = dict(status='terminal_both_phased_actor_modules_copied_SDK_byte_identical', directory=str(out), pieces=pieces,
        new_builds=2, whole_source_only_game_rebuild=False, unchanged_modules_not_recompiled=True, new_predictions=0, new_training=False,
        source_sha256={str(p): sha(p) for p in paths})
    save(out / 'protocol.json', proof)
    save(V / 'actor-phased-copied-rebuild-v1-current.json', proof)
    print(proof['status'], flush=True)


if __name__ == '__main__':
    main()
