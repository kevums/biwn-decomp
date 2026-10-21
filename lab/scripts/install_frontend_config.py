"""Install one saved preset per identifier and the scoped local runtime."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
from install_chat_runtime import install

ROOT = Path(__file__).resolve().parent.parent


def preset_targets(source_folder, destination_folder):
    """Preserve the existing name; identical source aliases install once."""
    groups = {}
    for path in sorted(source_folder.glob('*.json')):
        value = json.loads(path.read_text())
        identifier = value.get('identifier') or 'filename:' + path.name
        groups.setdefault(identifier, []).append((path, value))
    installed = {}
    for path in destination_folder.glob('*.json'):
        try:
            value = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if value.get('identifier'):
            installed.setdefault(value['identifier'], []).append(path)
    targets = []
    for identifier, aliases in groups.items():
        if any(value != aliases[0][1] for _, value in aliases[1:]):
            raise ValueError('Conflicting source presets share identifier ' + identifier)
        existing = installed.get(identifier, [])
        if len(existing) > 1:
            raise ValueError('Multiple installed presets share identifier ' + identifier)
        destination = existing[0] if existing else destination_folder / aliases[0][0].name
        source = next((path for path, _ in aliases if path.name == destination.name), aliases[0][0])
        targets.append((source, destination))
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Validate targets without writing files or installing packages')
    args = parser.parse_args()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    targets = preset_targets(ROOT / 'presets', Path.home() / '.lmstudio/config-presets')
    definition = ROOT / 'model-definitions/advertising-qwen38'
    targets.extend((definition / name, Path.home() / '.lmstudio/hub/models/local/advertising-qwen38' / name)
                   for name in ['model.yaml', 'manifest.json', 'provenance.json'])
    assert all(source.is_file() for source, _ in targets)
    if args.check_only:
        print(json.dumps(dict(status='validated_install_targets_no_changes',
                              targets=[dict(source=str(a), destination=str(b)) for a, b in targets]), indent=2))
        return
    report = []
    for source, destination in targets:
        if destination.is_file() and destination.read_bytes() == source.read_bytes():
            report.append(dict(path=str(destination), status='already matches'))
            continue
        if destination.exists():
            backup = ROOT / 'config-backups' / stamp / destination.relative_to(Path.home() / '.lmstudio')
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        report.append(dict(path=str(destination), status='installed'))
    # Preserve other integrations; this lab registers only its own server.
    destination = Path.home() / '.lmstudio/mcp.json'
    current = json.loads(destination.read_text()) if destination.exists() else {'mcpServers': {}}
    runtime = install()
    server = dict(command=str(runtime / '.venv/bin/python'), args=[str(runtime / 'chat_tools.py')])
    if current.setdefault('mcpServers', {}).get('local-ai-lab') != server:
        if destination.exists():
            backup = ROOT / 'config-backups' / stamp / 'mcp.json'
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
        current['mcpServers']['local-ai-lab'] = server
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(current, indent=2) + '\n')
        report.append(dict(path=str(destination), status='registered scoped local evidence tools'))
    else:
        report.append(dict(path=str(destination), status='local evidence tools already match'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
