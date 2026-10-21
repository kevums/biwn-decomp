"""Read-only copied runtime preflight; no model loading or prediction."""
import runpy,sys
from pathlib import Path
P=Path('/Users/kevin/Documents/Local AI Lab Restore Tests/20261020T194117.103058Z-biwn-current-moved')
sys.path.insert(0,str(P/'runtime/.venv/lib/python3.12/site-packages'));sys.path.insert(0,str(P/'runtime'))
import portable_runtime_paths_v8 as adapter
origin_root=Path(__file__).resolve().parents[1]
sys.path[:]=[x for x in sys.path if x and not Path(x).resolve().is_relative_to(origin_root)]
adapter.install();sys.path.insert(0,str(P/'workbench'));sys.path.insert(0,str(P/'workbench/scripts'))
from datetime import datetime,timezone
original=P/'workbench/scripts/run_deck_status_live_v38.py';source=original.read_text()
source=source.replace('Deck-status-live-v38-current.json','Reader38-preflight-current.json')
script=P/'workbench/scripts'/('Reader38-preflight-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'.py');script.write_text(source)
sys.argv=[str(script),'--default','--check-only'];runpy.run_path(str(script),run_name='__main__')
