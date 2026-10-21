"""Provision the scoped runtime and its complete local Python import closure."""
import ast,hashlib,json,re,shutil
from pathlib import Path
from datetime import datetime,timezone
import install_chat_runtime as legacy
ROOT=Path(__file__).resolve().parents[1]
ENTRY='chat_tools_current_v6.py'

def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def local_module_closure(root,entry=ENTRY):
    root=Path(root).resolve();pending=[Path(entry).stem];found={}
    while pending:
        name=pending.pop();assert re.fullmatch(r'[A-Za-z_]\w*',name),name
        p=root/(name+'.py')
        if name in found or not p.is_file():continue
        found[name]=p
        for node in ast.walk(ast.parse(p.read_text())):
            imports=[n.name for n in node.names]if isinstance(node,ast.Import)else [node.module]if isinstance(node,ast.ImportFrom)and node.module else[]
            pending.extend(n.split('.')[0]for n in imports if n and(root/(n.split('.')[0]+'.py')).is_file())
    return [p for _,p in sorted(found.items())]
def install(root=ROOT,runtime=None,current_only=False):
    root=Path(root).resolve();runtime=Path(runtime or Path.home()/'.lmstudio/local-ai-lab').resolve();assert runtime!=root and not root.is_relative_to(runtime),'Keep workbench and runtime distinct'
    if not current_only:
        old_root,old_runtime=legacy.ROOT,legacy.RUNTIME
        try:legacy.ROOT=root;legacy.RUNTIME=runtime;assert legacy.install()==runtime
        finally:legacy.ROOT,legacy.RUNTIME=old_root,old_runtime
    assert (runtime/'.venv/bin/python').is_file()and(runtime/'chat_tools.py').is_file(),'Provision the base runtime first'
    sources=local_module_closure(root);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');backup=root/'config-backups'/('runtime-closure-v2-'+stamp);changes=[];records=[]
    for source in sources:
        target=runtime/source.name;action='already_matches'
        if not target.exists()or target.read_bytes()!=source.read_bytes():
            if target.exists():backup.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup/source.name)
            shutil.copy2(source,target);changes.append(str(target));action='installed'
        assert sha(source)==sha(target);records.append(dict(module=source.stem,source=str(source),target=str(target),sha256=sha(target),action=action))
    launcher=runtime/'BIWN Current Status.command';text=legacy.launcher_script(launcher.name);launcher.write_text(text);launcher.chmod(0o755)
    result=dict(status='scoped_runtime_v2_import_closure_installed',runtime=str(runtime),workbench=str(root),modules=records,changes=changes,current_only=current_only,base_runtime_requested=not current_only,entrypoint=str(runtime/ENTRY),scope='Fresh current-host MCP runtime provisioning and local import closure. Workbench, model weights, referenced host libraries and absolute evidence paths are external dependencies. Not an off-machine/path-relocation/hardware proof.')
    (runtime/'runtime-provision-v2.json').write_text(json.dumps(result,indent=2)+'\n');return result
