"""Install the versioned current-status MCP entry after the established runtime."""
import argparse,json,os,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check-only',action='store_true');parser.add_argument('--current-only',action='store_true');args=parser.parse_args()
    if not args.current_only:
        import install_frontend_config as base
        old_argv=sys.argv
        try:
            sys.argv=[str(Path(base.__file__))]+(['--check-only']if args.check_only else[])
            base.main()
        finally:sys.argv=old_argv
    sources=['current_biwn_evidence_v2.py','current_biwn_evidence_v3.py','current_biwn_evidence_v4.py','current_biwn_evidence_v5.py','chat_tools_current_v4.py','chat_tools_current_v5.py']
    for name in sources:assert (ROOT/name).is_file()
    assert (ROOT/'BIWN Current Status.command').is_file()
    if args.check_only:
        print(json.dumps(dict(status='current_status_v2_install_targets_checked_no_changes',modules=sources,
                              entrypoint=str(RUNTIME/'chat_tools_current_v5.py'),runtime_rebuilt=False)))
        return
    assert (RUNTIME/'.venv/bin/python').exists()and(RUNTIME/'chat_tools.py').is_file(),'Install the base runtime first'
    backup=ROOT/'config-backups'/('current-frontend-v5-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    changes=[]
    def write(path,data,label):
        if path.exists()and path.read_bytes()==data:return
        backup.mkdir(parents=True,exist_ok=True)
        if path.exists():shutil.copy2(path,backup/label)
        path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_name(path.name+'.current-install.tmp');temporary.write_bytes(data);os.replace(temporary,path)
        changes.append(str(path))
    for name in sources:write(RUNTIME/name,(ROOT/name).read_bytes(),name)
    from install_chat_runtime import launcher_script
    launcher=RUNTIME/'BIWN Current Status.command';write(launcher,launcher_script(launcher.name).encode(),'BIWN Current Status.command');launcher.chmod(0o755)
    path=Path.home()/'.lmstudio/mcp.json';config=json.loads(path.read_text())if path.exists()else{'mcpServers':{}}
    original=json.loads(json.dumps(config));entry=dict(config.setdefault('mcpServers',{}).get('local-ai-lab',{}))
    entry.update(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools_current_v5.py')]);config['mcpServers']['local-ai-lab']=entry
    assert {k:v for k,v in config['mcpServers'].items()if k!='local-ai-lab'}=={k:v for k,v in original['mcpServers'].items()if k!='local-ai-lab'}
    write(path,(json.dumps(config,indent=2)+'\n').encode(),'mcp-before.json')
    result=dict(status='current_frontend_v5_installed',changes=changes,entrypoint=entry,
                base_runtime_requested=not args.current_only,historical_sources_unchanged=True,
                native_Chat_generation_verified=False,future_hardware_verified=False)
    save=ROOT/'verification/current-frontend-v5-install-current.json';save.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
