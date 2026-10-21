"""Install presets/model definitions and the complete scoped runtime with explicit paths."""
import argparse,json,os,shutil
from pathlib import Path
from datetime import datetime,timezone
from install_frontend_config import preset_targets
from install_chat_runtime_v3 import install,local_module_closure,ENTRY
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path);parser.add_argument('--lmstudio-dir',type=Path,default=Path.home()/'.lmstudio');parser.add_argument('--current-only',action='store_true');parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    lm=args.lmstudio_dir.resolve();runtime=(args.runtime or lm/'local-ai-lab').resolve();assert lm!=ROOT and runtime!=ROOT
    definitions=['advertising-qwen38','advertising-reviewer-experimental'];targets=preset_targets(ROOT/'presets',lm/'config-presets')
    for name in definitions:
        directory=ROOT/'model-definitions'/name
        for filename in ['model.yaml','manifest.json','provenance.json']:
            source=directory/filename;assert source.is_file(),str(source);targets.append((source,lm/'hub/models/local'/name/filename))
    package_path=ROOT/'verification/advertising-reviewer-v10cap-package-current.json';package=json.loads(package_path.read_text())
    import hashlib
    expected_by_name={Path(path).name:digest for path,digest in package['model_files_sha256'].items()if '/hub/models/local/advertising-reviewer-experimental/'in path}
    for name in ['model.yaml','manifest.json','provenance.json']:
        path=ROOT/'model-definitions/advertising-reviewer-experimental'/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected_by_name[name],'Preserve frozen Reviewer registration metadata: '+name
    modules=local_module_closure(ROOT)
    if args.check_only:
        print(json.dumps(dict(status='frontend_v9_targets_checked_no_changes',runtime=str(runtime),lmstudio_dir=str(lm),modules=[p.name for p in modules],targets=[str(b)for _,b in targets],base_runtime_requested=not args.current_only)));return
    backup=ROOT/'config-backups'/('current-frontend-v9-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));changes=[]
    def write(path,data,label):
        if path.exists()and path.read_bytes()==data:return
        if path.exists():backup.mkdir(parents=True,exist_ok=True);shutil.copy2(path,backup/label)
        path.parent.mkdir(parents=True,exist_ok=True);temporary=path.with_name(path.name+'.frontend-v9.tmp');temporary.write_bytes(data);os.replace(temporary,path);changes.append(str(path))
    for i,(source,target)in enumerate(targets):write(target,source.read_bytes(),str(i)+'-'+target.name)
    provision=install(ROOT,runtime,current_only=args.current_only)
    config_path=lm/'mcp.json';config=json.loads(config_path.read_text())if config_path.exists()else {'mcpServers':{}};other={k:v for k,v in config.get('mcpServers',{}).items()if k!='local-ai-lab'};entry={**config.setdefault('mcpServers',{}).get('local-ai-lab',{}),'command':str(runtime/'.venv/bin/python'),'args':[str(runtime/ENTRY)]};config['mcpServers']['local-ai-lab']=entry;assert other=={k:v for k,v in config['mcpServers'].items()if k!='local-ai-lab'};write(config_path,(json.dumps(config,indent=2)+'\n').encode(),'mcp-before.json')
    result=dict(status='frontend_v9_installed',runtime=str(runtime),lmstudio_dir=str(lm),entrypoint=entry,changes=changes,provision=provision,model_weights_copied=False,native_Chat_verified=False,path_relocation_verified=False,future_hardware_verified=False)
    destination=runtime/'frontend-install-v9.json';destination.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],runtime=str(runtime),lmstudio_dir=str(lm),modules=len(modules),changes=changes),indent=2))
if __name__=='__main__':main()
