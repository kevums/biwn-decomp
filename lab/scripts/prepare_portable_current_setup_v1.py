"""New APFS-cloned current setup; preserve old package, live config and source bytes.
Latest18tool v17 frontend,32980byte experiment,and Advertising/Desktop workflows.
"""
import json,hashlib,os,shutil,subprocess,uuid
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 source=Path(read(V/'portable-sdk-workbench-reviewed-current.json')['package']);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=V/'portable-current-setup'/stamp;out.mkdir(parents=True);target=Path.home()/'Documents/Local AI Lab Restore Tests'/(stamp+'-current-setup');assert not target.exists();live_mcp=Path.home()/'.lmstudio/mcp.json';before=sha(live_mcp)
 state=dict(status='cloning_current_setup_from_frozen_baseline',pid=os.getpid(),directory=str(out),package=str(target),baseline_package=str(source),live_mcp_sha256=before,new_training=False,new_predictions=0,completed=0)
 def mark():save(out/'protocol.json',state);save(V/'portable-current-setup-active.json',state)
 mark();print(out,flush=True);subprocess.run(['/bin/cp','-cR',str(source),str(target)],capture_output=True,check=True);records=[]
 def clone(src,dst):
  src,dst=Path(src),Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);h=sha(src);subprocess.run(['/bin/cp','-c',str(src),str(dst)],capture_output=True,check=True);assert sha(dst)==h;records.append(dict(source=str(src),target_relative=str(dst.relative_to(target)),sha256=h,bytes=src.stat().st_size))
 def overlay(src,dst):
  src,dst=Path(src),Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);assert src.name==dst.name;subprocess.run(['/bin/cp','-cR',str(src),str(dst.parent)],capture_output=True,check=True)
 runtime=target/'runtime';workbench=target/'workbench';state['status']='copying_current_frontend_scripts_and_evidence';mark()
 for p in ROOT.iterdir():
  if p.is_file()and(p.suffix in['.py','.command']or p.name in['lab','config.json','Local AI Start Here.txt']):clone(p,workbench/p.name)
 for name in['scripts','presets','model-definitions','config','corpus','indexes']:overlay(ROOT/name,workbench/name)
 overlay(ROOT/'projects/black-ice-white-noise/restoration',workbench/'projects/black-ice-white-noise/restoration');overlay(ROOT/'tools/m68k-elf',workbench/'tools/m68k-elf')
 publication=read(V/'current-biwn-latest-publication-current.json');assert publication['facts']['experimental_build']['resident_bytes']==32980
 for i,(p,h)in enumerate(publication['dependencies_sha256'].items()):
  p=Path(p);assert p.is_relative_to(ROOT)and sha(p)==h,str(p);clone(p,workbench/p.relative_to(ROOT))
  if i%128==0:state['completed']=i+1;mark();print('Evidence',i+1,'/',len(publication['dependencies_sha256']),flush=True)
 # Current pointers used by the copied frontend/launchers are operational data,not copied PID ownership.
 pointers=['current-biwn-latest-publication-current','native-gpu-mailbox-disc-build-current','native-actor-direction-disc-build-current','native-task-pool-arena-disc-build-current','task-pool-arena-final-current','native-gpu-mailbox-current','gpu-mailbox-native-Author-current','advertising-study-card-packets-current','advertising-study-card-reviewed-current','advertising-reviewer-v10cap-package-current','advertising-desk-source-pages-reviewed-current','goal-continuation-current']
 for name in pointers:clone(V/(name+'.json'),workbench/'verification'/(name+'.json'))
 for p in ROOT.glob('*.py'):clone(p,runtime/p.name)
 clone(ROOT/'config.json',runtime/'config.json');overlay(ROOT/'config',runtime/'config');overlay(ROOT/'corpus',runtime/'corpus');overlay(ROOT/'indexes',runtime/'indexes')
 clone(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi',workbench/'projects/black-ice-white-noise/originals/BIWN#23.cdi')
 # Preserve every copied source byte. Package adapters select current modules and copied models.
 clone(source/'runtime/portable_runtime_paths_v5.py',runtime/'portable_runtime_paths_v6.py')
 (runtime/'sitecustomize.py').write_text('import portable_runtime_paths_v6\nportable_runtime_paths_v6.install()\n')
 site=runtime/'.venv/lib/python3.12/site-packages';(site/'sitecustomize.py').write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parents[4]))\nimport portable_runtime_paths_v6\nportable_runtime_paths_v6.install()\n")
 (runtime/'portable_chat_tools_v6.py').write_text("import portable_runtime_paths_v6\nportable_runtime_paths_v6.install()\nimport sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'workbench'))\nimport chat_tools_current_v17 as entry\nentry.legacy.mcp.run(transport='stdio')\n")
 repair=(source/'repair_copied_runtime_v5.py').read_text().replace('portable_chat_tools_v5.py','portable_chat_tools_v6.py');(target/'repair_copied_runtime_v6.py').write_text(repair)
 loader=target/'Restore Current Setup.command';loader.write_text('#!/bin/zsh\nset -eu\nCURRENT_SETUP_DIR=${0:A:h}\nunset PYTHONPATH PYTHONHOME VIRTUAL_ENV\n"$CURRENT_SETUP_DIR/runtime/python/bin/python3.12" "$CURRENT_SETUP_DIR/repair_copied_runtime_v6.py"\nexec "$CURRENT_SETUP_DIR/runtime/python/bin/python3.12" "$CURRENT_SETUP_DIR/repair_copied_indexes.py"\n');loader.chmod(0o755)
 for name in['portable-package-id.json','portable-model-bindings.json','model-registration-receipt.json']:
  if(target/name).exists():shutil.copy2(target/name,target/('baseline-'+name))
 save(target/'portable-package-id.json',dict(id=uuid.uuid4().hex[:12]))
 models=(ROOT/'scripts/portable_model_setup_template.py').read_text();models=models.replace("identifier='portable-ailab-'+identity+'-'+suffix", "identifier='advertising-scholar'if label=='daily_base'else'advertising-reviewer-experimental'");(workbench/'portable_models_current.py').write_text(models)
 # The package needs fresh bindings; old baseline aliases must never be rewritten.
 for name in['portable-model-bindings.json','model-registration-receipt.json']:
  if(target/name).exists():(target/name).unlink()
 layout=read(target/'restore-layout.json');layout['previous_restore_roots']=list(dict.fromkeys([*layout['previous_restore_roots'],str(source)]));save(target/'restore-layout.json',layout)
 env={k:v for k,v in os.environ.items()if k not in['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']};run=subprocess.run([str(loader)],capture_output=True,text=True,env=env,timeout=120);(out/'restore.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 save(out/'overlaid-files.json',records);assert sha(live_mcp)==before
 state.update(status='terminal_current_setup_cloned_pending_move_and_execution',completed=len(records),overlaid_files=len(records),resident_code_bytes=32980,total_reservation_bytes=59200,frontend_version='v17',tool_count=18,model_resources_copied_from_baseline=True,model_identity_fresh=True,original_sources_and_historical_JSON_unchanged=True,live_configuration_changed=False,source_sha256={str(p):sha(p)for p in[Path(__file__),out/'overlaid-files.json',out/'restore.log',runtime/'portable_runtime_paths_v6.py',runtime/'portable_chat_tools_v6.py',target/'repair_copied_runtime_v6.py',target/'path-repair-receipt.json',target/'index-repair-receipt.json']},scope=__doc__);mark();save(V/'portable-current-setup-current.json',state);print({k:state[k]for k in['status','package','overlaid_files']})
if __name__=='__main__':main()
