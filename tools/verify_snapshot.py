#!/usr/bin/env python3
"""Verify copied source bytes without executing decompilation or inference."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'snapshot/source-files.json').read_text())
errors = []
for entry in manifest['files']:
    p = root / entry['path']
    if not p.is_file():
        errors.append({'path': entry['path'], 'error': 'missing'})
        continue
    data = p.read_bytes()
    if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
        errors.append({'path': entry['path'], 'error': 'content changed'})
print(json.dumps({'verified': not errors, 'copied_files': len(manifest['files']), 'errors': errors}, indent=2))
raise SystemExit(bool(errors))
