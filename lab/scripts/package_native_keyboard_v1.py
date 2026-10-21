"""Make a small runtime-local native preview bundle from verified artifacts."""
import json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab';TARGET=RUNTIME/'native-preview-v1'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return __import__('hashlib').sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,indent=2)+'\n')
def copy(src,dst):
 src=Path(src);dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists()and sha(dst)==sha(src):return
 p=subprocess.run(['/bin/cp','-c',str(src),str(dst)],capture_output=True,text=True)
 if p.returncode:shutil.copyfile(src,dst)
 assert sha(src)==sha(dst)
def main():
 TARGET.mkdir(parents=True,exist_ok=True);(TARGET/'runs').mkdir(exist_ok=True)
 proof_path=ROOT/'verification/native-Deck-asset-repair-reviewed-current.json';proof=read(proof_path);build=read(proof['build']);parent=read(build['parent_build']);run=read(ROOT/'verification/native-Deck-asset-repair-gameplay-current.json');folder=Path(run['directory'])/'candidate';report=read(folder/'report.json')
 files=['run_biwn_native_keyboard_v1.py','native_preview_observer_v1.c','biwn_live_window.py','biwn_audio_output.py','biwn_controller.py','probe_biwn_fresh_CD_boot.py']
 for name in files:copy(ROOT/'scripts'/name,TARGET/'scripts'/name)
 for src,name in [(build['derived_disc'],'native.cdi'),(parent['component'],'component.bin'),(report['core'],'core.dylib')]:copy(src,TARGET/'artifacts'/name)
 for name in ['state-final.bin','RAM-final.bin','video-final.xrgb8888']:copy(folder/name,TARGET/'candidate'/name)
 new_parent=dict(parent,component=str(TARGET/'artifacts/component.bin'));pp=TARGET/'verification/parent.json';save(pp,new_parent)
 new_build=dict(build,derived_disc=str(TARGET/'artifacts/native.cdi'),parent_build=str(pp),parent_build_sha256=sha(pp));bp=TARGET/'verification/build.json';save(bp,new_build)
 new_proof=dict(proof,build=str(bp),build_sha256=sha(bp),disc=str(TARGET/'artifacts/native.cdi'),source_provenance=str(proof_path),source_provenance_sha256=sha(proof_path));save(TARGET/'verification/native-Deck-asset-repair-reviewed-current.json',new_proof)
 # The frontend requires the complete saved machine and provider hashes,
 # not the much larger historical per-frame trace in its startup recipe.
 keep=['requested_options','video','core_sha256','staged_cart_ROM_sha256','final_serialized_state_sha256','final_RAM_sha256'];new_report={k:report[k]for k in keep};new_report['core']=str(TARGET/'artifacts/core.dylib');save(TARGET/'candidate/report.json',new_report)
 save(TARGET/'verification/native-Deck-asset-repair-gameplay-current.json',dict(directory=str(TARGET)))
 link=TARGET/'.venv/bin/python3.12';link.parent.mkdir(parents=True,exist_ok=True)
 if link.is_symlink():link.unlink()
 assert not link.exists();link.symlink_to(RUNTIME/'.venv/bin/python3.12')
 entries={str(p.relative_to(TARGET)):sha(p)for p in TARGET.rglob('*')if p.is_file()and not {'runs','__pycache__'}&set(p.relative_to(TARGET).parts)and p.name not in ['manifest.json','native-keyboard-preview-current.json']}
 state=dict(status='terminal_runtime_local_native_preview_bundle_prepared',directory=str(TARGET),source_provenance=str(proof_path),source_provenance_sha256=sha(proof_path),files=entries,python=str((RUNTIME/'.venv/bin/python3.12').resolve()),current_other_machine_verified=False,actual_native_Chat_verified=False,new_training=False,whole_game_complete=False,scope='Verified native image/checkpoint/core and small Python frontend copied outside Documents. No game or model bytes changed. Runtime-local package, not a complete lab migration or future-hardware acceptance.')
 save(TARGET/'manifest.json',state);save(ROOT/'verification/native-keyboard-runtime-bundle-current.json',state);print(TARGET,len(entries),'files',flush=True)
if __name__=='__main__':main()
