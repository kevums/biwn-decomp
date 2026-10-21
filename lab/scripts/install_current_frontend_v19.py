"""Install existing reviewed status surfaces, preserving previous configuration."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home()/'.lmstudio/local-ai-lab'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out = ROOT/'verification/current-frontend-v19-install'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    files = []
    def backup(path):
        if path.exists():
            dst = out/('before-'+str(len(files))+'-'+path.name)
            shutil.copyfile(path, dst)
            files.append(dict(path=str(path), backup=str(dst), sha256=sha(dst)))
    for name in ['native_deck_status_evidence_v1.py','native_format_evidence.py','chat_tools_current_v19.py']:
        target=RUNTIME/name
        backup(target)
        shutil.copyfile(ROOT/name, target)
        assert sha(target)==sha(ROOT/name)
    for name, old, new in [
        ('Live Local BIWN Briefing.command','run_deck_status_live_v16.py','run_deck_status_live_v17.py'),
        ('Show BIWN Native Disc.command','reveal_biwn_native_disc_v2.py','reveal_biwn_native_disc_v3.py')]:
        path=ROOT/name
        backup(path)
        content=path.read_text()
        assert old in content
        path.write_text(content.replace(old,new))
    path=ROOT/'BIWN Current Status.command'
    backup(path)
    path.write_text('#!/bin/zsh\nset -eu\nLAB_ROOT="${0:A:h}"\ncd /\n"$LAB_ROOT/.venv/bin/python3.12" -u "$LAB_ROOT/scripts/run_deck_status_live_v17.py" "$@"\nif [[ -t 0 ]]; then print "Press Return to close."; read -r || true; fi\n')
    config=Path.home()/'.lmstudio/mcp.json'
    backup(config)
    data=json.loads(config.read_text())
    assert data['mcpServers']['local-ai-lab']['args']==[str(RUNTIME/'chat_tools_current_v18.py')]
    data['mcpServers']['local-ai-lab']['args']=[str(RUNTIME/'chat_tools_current_v19.py')]
    config.write_text(json.dumps(data,indent=2)+'\n')
    # Existing tools/connections retain all their other settings.
    previous=json.loads(Path(files[-1]['backup']).read_text())
    expected=json.loads(json.dumps(data))
    expected['mcpServers']['local-ai-lab']['args']=previous['mcpServers']['local-ai-lab']['args']
    assert expected==previous
    sources=ROOT/'config/current-model-work-sources.json'
    backup(sources)
    items=json.loads(sources.read_text())
    item=['Deck-status-live-v17-reviewed-current.json','Five-caller current briefing: accepted raw local Reader, exact prompt and stream']
    assert not any(x[0]==item[0] for x in items)
    items.insert(0,item)
    sources.write_text(json.dumps(items,indent=2)+'\n')
    state=dict(status='terminal_v19_current_status_files_installed_pending_MCP_check',directory=str(out),
               backups=files,config_sha256=sha(config),tool_privileges_added=False,native_Chat_reload_observed=False,
               new_prediction=False,new_training=False,whole_goal_complete=False)
    (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n')
    (ROOT/'verification/current-frontend-v19-install-current.json').write_text(json.dumps(state,indent=2)+'\n')
    print(out)


if __name__=='__main__':
    main()
