"""Repair a copied package's Python/MCP paths using its current directory.

Runs with the bundled base Python, without downloading dependencies or changing
the real LM Studio configuration. Existing historical origin/evidence stays raw.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import venv


def main():
    root=Path(__file__).resolve().parent
    runtime=root/'runtime'
    origin=json.loads((root/'origin.json').read_text())
    layout_path=root/'restore-layout.json'
    layout=json.loads(layout_path.read_text())if layout_path.exists()else{}
    prior=set(layout.get('previous_restore_roots',[]))
    prior.add(str(Path(origin['restored_runtime']).parent))
    if layout.get('current_restore_root'):
        prior.add(layout['current_restore_root'])
    prior.discard(str(root))
    layout.update(current_restore_root=str(root),previous_restore_roots=sorted(prior))
    layout_path.write_text(json.dumps(layout,indent=2)+'\n')
    assert Path(sys.executable).resolve()==(runtime/'python/bin/python3.12').resolve()
    venv.EnvBuilder(with_pip=False,symlinks=True).create(runtime/'.venv')
    python=runtime/'.venv/bin/python'
    if python.is_symlink():
        python.unlink()
    python.symlink_to('../../python/bin/python3.12')
    changes=[]
    for path in (runtime/'.venv/bin').iterdir():
        if not path.is_file()or path.is_symlink():
            continue
        raw=path.read_bytes()
        first,sep,rest=raw.partition(b'\n')
        if first.startswith(b'#!')and b'python'in first.lower():
            replacement=('#!'+str(python)).encode()
            if first!=replacement:
                path.write_bytes(replacement+sep+rest)
                changes.append(dict(path=str(path.relative_to(root)),old_shebang=first.decode(),new_shebang=replacement.decode()))
    config_path=root/'lmstudio-home/mcp.json'
    before=config_path.read_bytes()
    backup=root/'mcp-before-path-repair.json'
    if not backup.exists():
        backup.write_bytes(before)
    config=json.loads(before)
    config.setdefault('mcpServers',{})['local-ai-lab']=dict(command=str(python),args=[str(runtime/'portable_chat_tools_v3.py')],env={'PYTHONPATH':str(runtime)})
    config_path.write_text(json.dumps(config,indent=2)+'\n')
    result=dict(status='copied_runtime_paths_repaired',package_root=str(root),python=str(python),relative_python_symlink=os.readlink(python),venv_home_regenerated=True,shebang_changes=changes,configuration=str(config_path),model_weights_changed=False,live_LM_Studio_configuration_changed=False,scope=__doc__)
    (root/'path-repair-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
