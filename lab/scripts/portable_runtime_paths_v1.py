"""Explicit in-memory path adaptation for the isolated existing MCP runtime.

Historical JSON and sources retain their exact bytes and original hashes.
Only imports made by copied local modules receive Path/JSON views that translate
declared absolute path values and dictionary keys. Other libraries retain normal
imports. An audit hook rejects access to the origin workbench/LM Studio tree.
This is a same-host experiment, not a general security sandbox.
"""
import atexit
import builtins
import json
import os
from pathlib import Path
import sys
import types

_installed = False


def install():
    global _installed
    if _installed:
        return
    runtime = Path(__file__).resolve().parent
    out = runtime.parent
    origin = json.loads((out / 'origin.json').read_text())
    workbench = out / 'workbench'
    lmstudio = out / 'lmstudio-home'
    old_root = Path(origin['original_workbench'])
    old_runtime = Path(origin['original_runtime'])
    old_lmstudio = old_runtime.parent
    allowed = str(out)
    roots = [str(runtime), str(workbench)]
    pairs = sorted([
        (str(old_root / '.venv'), str(runtime / '.venv')),
        (str(old_root), str(workbench)),
        (str(old_runtime), str(runtime)),
        (str(old_lmstudio), str(lmstudio)),
    ], key=lambda pair: -len(pair[0]))
    counters = dict(rebased_values=0, adapted_imports=0, guarded_events=0)
    reads = set()
    denied = []

    def within(name, prefix):
        return name == prefix or name.startswith(prefix + '/')

    def remap(value):
        if not isinstance(value, str) or not value.startswith('/') or within(value, allowed):
            return value
        for old, new in pairs:
            if within(value, old):
                counters['rebased_values'] += 1
                return new + value[len(old):]
        return value

    def tree(value):
        if isinstance(value, str):
            return remap(value)
        if isinstance(value, list):
            return [tree(item) for item in value]
        if isinstance(value, dict):
            return {remap(key): tree(item) for key, item in value.items()}
        return value

    concrete = type(Path())

    class RelocatedPath(concrete):
        def __new__(cls, *args, **kwargs):
            return super().__new__(cls, remap(str(Path(*args))), **kwargs)

        def __truediv__(self, key):
            return type(self)(super().__truediv__(key))

        def joinpath(self, *args):
            return type(self)(super().joinpath(*args))

        def expanduser(self):
            return type(self)(super().expanduser())

    path_view = types.ModuleType('pathlib')
    path_view.__dict__.update(__import__('pathlib').__dict__)
    path_view.Path = RelocatedPath
    json_view = types.ModuleType('json')
    json_view.__dict__.update(json.__dict__)
    json_view.loads = lambda *a, **k: tree(json.loads(*a, **k))
    json_view.load = lambda *a, **k: tree(json.load(*a, **k))
    original_import = builtins.__import__

    def adapted_import(name, globals=None, locals=None, fromlist=(), level=0):
        result = original_import(name, globals, locals, fromlist, level)
        filename = str((globals or {}).get('__file__', ''))
        local = any(within(filename, root) for root in roots)
        if local and name in {'pathlib', 'json'} and not level:
            counters['adapted_imports'] += 1
            return path_view if name == 'pathlib' else json_view
        return result

    def guard_path(value, event):
        if isinstance(value, bytes):
            value = os.fsdecode(value)
        if not isinstance(value, str) or not value.startswith('/'):
            return
        normalized = os.path.realpath(value)
        if within(normalized, allowed):
            reads.add(normalized)
            return
        if within(normalized, str(old_root)) or within(normalized, str(old_lmstudio)):
            denied.append(dict(event=event, path=normalized))
            raise PermissionError('Relocation origin access rejected: ' + normalized)

    def audit(event, args):
        if event in {'open', 'os.listdir', 'os.scandir', 'ctypes.dlopen'}:
            counters['guarded_events'] += 1
            if args:
                guard_path(args[0], event)
        elif event == 'subprocess.Popen':
            counters['guarded_events'] += 1
            guard_path(args[0], event)
            for arg in args[1] if isinstance(args[1], (list, tuple)) else [args[1]]:
                guard_path(arg, event)
            guard_path(args[2], event)

    def receipt():
        destination = out / ('path-audit-' + str(os.getpid()) + '.json')
        destination.write_text(json.dumps(dict(pid=os.getpid(), original_roots_denied=[str(old_root), str(old_lmstudio)], allowed_restore_root=str(out), counters=counters, denied=denied, restored_paths=sorted(reads), historical_bytes_rewritten=False), indent=2) + '\n')

    sys.addaudithook(audit)
    builtins.__import__ = adapted_import
    atexit.register(receipt)
    _installed = True
