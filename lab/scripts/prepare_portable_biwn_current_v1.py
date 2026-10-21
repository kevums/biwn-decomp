"""Clone and refresh a separate current game workbench;no inference or live install."""
import hashlib,json,os,shutil,subprocess,uuid
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';RT=Path.home()/'.lmstudio/local-ai-lab'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 source=Path(read(V/'portable-current-setup-reviewed-current.json')['package']);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=V/'portable-biwn-current-v1'/stamp;out.mkdir(parents=True);target=Path.home()/'Documents/Local AI Lab Restore Tests'/(stamp+'-biwn-current');assert not target.exists();live=Path.home()/'.lmstudio/mcp.json';before=sha(live)
 state=dict(status='cloning',pid=os.getpid(),directory=str(out),package=str(target),baseline=str(source),new_predictions=0,new_training=False,live_MCP_sha256=before)
 def mark():save(out/'protocol.json',state);save(V/'portable-biwn-current-v1-active.json',state)
 mark();print(out,flush=True);subprocess.run(['/bin/cp','-cR',str(source),str(target)],check=True,capture_output=True)
 historical=target/'historical-entrypoints';historical.mkdir()
 for p in list(target.glob('*.command')):p.rename(historical/p.name)
 records={}
 def clone(src,dst):
  src,dst=Path(src),Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);digest=sha(src)
  if not dst.is_file()or sha(dst)!=digest:subprocess.run(['/bin/cp','-c',str(src),str(dst)],check=True,capture_output=True)
  assert sha(dst)==digest;records[str(src)]=dict(relative=str(dst.relative_to(target)),sha256=digest,bytes=src.stat().st_size)
 def overlay(src,dst):
  src,dst=Path(src),Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);assert src.name==dst.name;subprocess.run(['/bin/cp','-cR',str(src),str(dst.parent)],check=True,capture_output=True)
 work=target/'workbench';runtime=target/'runtime';state['status']='overlaying_current_game_sources';mark()
 for p in ROOT.iterdir():
  if p.is_file()and(p.suffix in ['.py','.command']or p.name in ['lab','config.json','models.lock.json','candidate-models.lock.json']):clone(p,work/p.name)
 for p in ROOT.glob('*.py'):clone(p,runtime/p.name)
 for name in ['scripts','presets','model-definitions','config','corpus','indexes']:overlay(ROOT/name,work/name)
 for name in ['config','corpus','indexes']:overlay(ROOT/name,runtime/name)
 clone(ROOT/'config.json',runtime/'config.json')
 overlay(ROOT/'projects/black-ice-white-noise/restoration',work/'projects/black-ice-white-noise/restoration');overlay(ROOT/'tools/m68k-elf',work/'tools/m68k-elf');overlay(RT/'native-preview-v4',runtime/'native-preview-v4')
 seeds=[V/'native-Deck-current-status-v1-current.json',V/'native-debug-gameplay-published-v1-current.json',V/'native-Deck-debug-gameplay-reviewed-v1-current.json',V/'local-typed-clear-target-v2-current.json',V/'typed-local-clear-reviewed-v3-current.json',V/'game-decomposed-clear-v3-current.json',V/'native-Deck-debug-disc-build-v1-current.json',RT/'native-preview-v4/verification/native-Deck-six-reviewed-v1-current.json',RT/'native-preview-v4/verification/native-Deck-six-outer-v1-candidate-current.json']
 queue=list(seeds);done=set();missing=set();state['status']='copying_bound_game_evidence';mark()
 def strings(obj):
  if isinstance(obj,str):yield obj
  elif isinstance(obj,list):
   for value in obj:yield from strings(value)
  elif isinstance(obj,dict):
   for key,value in obj.items():yield key;yield from strings(value)
 while queue:
  p=Path(queue.pop())
  if p in done:continue
  done.add(p)
  owner=ROOT if p.is_relative_to(ROOT)else RT if p.is_relative_to(RT)else None
  if owner is None:continue
  if not p.is_file():missing.add(str(p));continue
  destination=(work if owner==ROOT else runtime)/p.relative_to(owner);clone(p,destination)
  if p.suffix=='.json':
   try:data=read(p)
   except (UnicodeError,json.JSONDecodeError):continue
   for value in strings(data):
    if not value.startswith('/'):continue
    q=Path(value)
    if q.is_relative_to(ROOT)or q.is_relative_to(RT):
     if q.is_file():queue.append(q)
  if len(done)%100==0:state['copied_evidence_files']=len(done);mark();print('Evidence',len(done),flush=True)
 save(out/'referenced_missing_files.json',sorted(missing))
 # Adapters preserve original evidence bytes;only operational paths are rebased.
 adapter=(source/'runtime/portable_runtime_paths_v7.py').read_text();(runtime/'portable_runtime_paths_v8.py').write_text(adapter)
 (runtime/'portable_chat_tools_v8.py').write_text("import portable_runtime_paths_v8\nportable_runtime_paths_v8.install()\nimport sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'workbench'))\nimport chat_tools_current_v22 as entry\nentry.legacy.mcp.run(transport='stdio')\n")
 (runtime/'sitecustomize.py').write_text('import portable_runtime_paths_v8\nportable_runtime_paths_v8.install()\n')
 (runtime/'.venv/lib/python3.12/site-packages/sitecustomize.py').write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parents[4]))\nimport portable_runtime_paths_v8\nportable_runtime_paths_v8.install()\n")
 (target/'repair_copied_runtime_v8.py').write_text((source/'repair_copied_runtime_v7.py').read_text().replace('portable_chat_tools_v7.py','portable_chat_tools_v8.py'))
 loader=target/'Restore BIWN Setup.command';loader.write_text('#!/bin/zsh\nset -eu\nBIWN_PACKAGE=${0:A:h}\nunset PYTHONPATH PYTHONHOME VIRTUAL_ENV\n"$BIWN_PACKAGE/runtime/python/bin/python3.12" "$BIWN_PACKAGE/repair_copied_runtime_v8.py"\nexec "$BIWN_PACKAGE/runtime/python/bin/python3.12" "$BIWN_PACKAGE/repair_copied_indexes.py"\n');loader.chmod(0o755)
 # Fresh identity prevents inherited model links from being retargeted.
 for name in ['portable-package-id.json','portable-model-bindings.json','model-registration-receipt.json']:
  p=target/name
  if p.exists():p.rename(target/('historical-'+name))
 save(target/'portable-package-id.json',dict(id=uuid.uuid4().hex[:12]));clone(ROOT/'scripts/portable_model_setup_template.py',work/'portable_models_game.py')
 layout=read(target/'restore-layout.json');layout['previous_restore_roots']=list(dict.fromkeys([*layout['previous_restore_roots'],str(source)]));save(target/'restore-layout.json',layout)
 env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']}
 p=subprocess.run([str(loader)],env=env,capture_output=True,text=True,timeout=120);(out/'initial-restore.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 moved=target.with_name(target.name+'-moved');target.rename(moved);state['initial_package']=str(target);target=moved;state['package']=str(target);state['status']='repairing_moved_game_snapshot';mark()
 p=subprocess.run([str(target/loader.name)],env=env,capture_output=True,text=True,timeout=120);(out/'moved-restore.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 save(out/'copied-file-manifest.json',records)
 assert sha(live)==before
 state.update(status='terminal_current_biwn_snapshot_moved_pending_checks',copied_current_files=len(records),missing_explicit_seed_files=sorted(missing),frontend='v22',tool_count=18,current_native_helpers=6,new_predictions=0,new_training=False,live_MCP_unchanged=True,source_sha256={str(p):sha(p)for p in [Path(__file__),out/'copied-file-manifest.json',out/'initial-restore.log',out/'moved-restore.log']});mark();save(V/'portable-biwn-current-v1-current.json',state);print(state['status'],target,flush=True)
if __name__=='__main__':main()
