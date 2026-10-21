"""Copy a frozen workbench closure for testing the existing eighteen-tool runtime.

APFS cloning is mandatory here. No model, original/live configuration, or
historical evidence bytes are rewritten. This prepares a same-host experiment.
"""
import hashlib
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    active = ROOT / 'verification/relocated-runtime-active.json'
    state = read(active)
    assert state['status'] == 'terminal_isolated_frontend_installed_pending_relocation'
    out = Path(state['directory'])
    dest = out / 'workbench'
    assert not dest.exists()
    dest.mkdir()
    publication_path = ROOT / 'verification/current-biwn-latest-publication-current.json'
    publication = read(publication_path)
    paths = dict(publication['dependencies_sha256'])

    def add(path, expected=None):
        p = Path(path).resolve()
        assert p.is_relative_to(ROOT) and p.is_file(), str(p)
        digest = expected or sha(p)
        assert str(p) not in paths or paths[str(p)] == digest, str(p)
        paths[str(p)] = digest

    add(publication_path)
    for source in ROOT.glob('*.py'):
        add(source)
    for pattern in ['scripts/*.py', 'scripts/*.inc.c', 'config/*.json', 'render-assets/*', 'tools/*.dylib', 'tools/*.json', 'tools/m68k-elf/bin/*']:
        for source in ROOT.glob(pattern):
            if source.is_file():
                add(source)
    for source in (ROOT / 'projects/black-ice-white-noise/restoration').rglob('*'):
        if source.is_file() and source.suffix in {'.c', '.h', '.S', '.ld'}:
            add(source)
    for name in ['config.json', 'native-fixture-backend.json', 'chat-runtime.lock', 'verification/biwn-movement-matrix-checks.json', 'render-assets/biwn-inventory-baseline.bin', 'tools/blitter-runtime/virtualjaguar_libretro.dylib', 'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib', 'projects/black-ice-white-noise/originals/BIWN#23.cdi']:
        add(ROOT / name)
    # The five process receipts are terminal history: no migrated PID is live.
    pointer_names = set()
    for source in ROOT.glob('current_biwn_evidence_v*.py'):
        pointer_names.update(re.findall(r"'([\w-]+-active\.json)'", source.read_text()))
    for name in pointer_names:
        p = ROOT / 'verification' / name
        add(p)
        job = read(p)
        assert job['status'].startswith('terminal_'), name
        if job.get('reference'):
            add(Path(job['reference']) / 'report.json', job['source_sha256'][str(Path(job['reference']) / 'report.json')])
    for key in ['derived_disc', 'derived_stage', 'component']:
        build = publication['facts']['experimental_build']
        if key in build:
            add(build[key], build[key + '_sha256'])

    def clone(item):
        name, digest = item
        source = Path(name)
        target = dest / source.relative_to(ROOT)
        assert sha(source) == digest, name
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['/bin/cp', '-c', str(source), str(target)], check=True, capture_output=True)
        assert sha(target) == digest, str(target)
        return dict(original=name, relative=str(target.relative_to(dest)), bytes=target.stat().st_size, sha256=digest, method='APFSclone')

    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(clone, paths.items()))
    save(out / 'workbench-files.json', records)
    origin = dict(original_workbench=str(ROOT), restored_workbench=str(dest), original_runtime=str(Path.home() / '.lmstudio/local-ai-lab'), restored_runtime=state['runtime'], publication_sha256=sha(publication_path), historical_bytes_rewritten=False, source_files=len(records), model_weights_copied=False, scope=__doc__)
    save(out / 'origin.json', origin)
    state.update(status='terminal_runtime_workbench_cloned_pending_MCP_relocation', workbench=str(dest), workbench_files=len(records), workbench_logical_bytes=sum(r['bytes'] for r in records), publication_sha256=origin['publication_sha256'])
    save(out / 'workbench-copy-receipt.json', state)
    save(active, state)
    print(json.dumps({k: state[k] for k in ['status', 'workbench_files', 'workbench_logical_bytes']}))


if __name__ == '__main__':
    main()
