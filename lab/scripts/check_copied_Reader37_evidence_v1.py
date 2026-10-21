"""Read-only copied runtime preflight; no model loading or prediction."""
import runpy,sys
from pathlib import Path
P=Path('/Users/kevin/Documents/Local AI Lab Restore Tests/20261020T194117.103058Z-biwn-current-moved')
sys.path.insert(0,str(P/'runtime/.venv/lib/python3.12/site-packages'));sys.path.insert(0,str(P/'runtime'))
import portable_runtime_paths_v8 as adapter
adapter.install();sys.path.insert(0,str(P/'workbench'));sys.path.insert(0,str(P/'workbench/scripts'))
script=P/'workbench/scripts/run_deck_status_live_v37.py';sys.argv=[str(script),'--default','--check-only'];runpy.run_path(str(script),run_name='__main__')
