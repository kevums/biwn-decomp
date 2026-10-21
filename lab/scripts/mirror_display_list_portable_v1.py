"""Complete the moved package's v27 raw artifacts without altering history."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 pub=read(V/'native-scene17-display-list-fresh-reviewed-v1-current.json');frozen=Path(pub['directory'])
 pointers=[]
 for p in V.glob('*-current.json'):
  if 'scene17-display-list'in p.name or 'scene-display-list'in p.name:pointers.append(p)
 directories=set();files=set(pointers);missing=[]
 for p in pointers:
  d=read(p)
  for key in ['directory','payload','derived_disc','derived_stage','component']:
   value=d.get(key)
   if not isinstance(value,str):continue
   src=Path(value)
   if not src.is_relative_to(ROOT):continue
   if src.is_dir():directories.add(src)
   elif src.is_file():files.add(src)
  for key in ['source_sha256','copied_source_sha256','files_sha256']:
   for name,h in d.get(key,{}).items():
    src=Path(name)
    if src.is_relative_to(ROOT)and src.is_file():
     assert sha(src)==h,(p.name,name);files.add(src)
 for directory in directories:
  files.update(p for p in directory.rglob('*')if p.is_file()and'__pycache__'not in p.parts)
 b=read(V/'native-scene17-display-list-disc-build-v1-current.json')
 files.update(p for p in Path(b['directory']).rglob('*')if p.is_file())
 candidate=read(read(V/'native-Deck-current-status-v1-current.json')['packet'])['latest_native_candidate']
 files.add(Path(candidate['native_module']))
 copied=[];verified=[]
 out=V/'display-list-portable-closure-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for src in sorted(files):
  target=P/'workbench'/src.relative_to(ROOT);digest=sha(src)
  if target.is_file()and sha(target)==digest:verified.append(str(src.relative_to(ROOT)));continue
  # Mutable current pointers may advance; keep exact previous copies in receipt.
  if target.exists():
   if not src.name.endswith('-current.json'):raise AssertionError(('Existing immutable copied file differs',str(src)))
   backup=out/'previous-copied-pointers'/src.name;backup.parent.mkdir(exist_ok=True);subprocess.run(['/bin/cp','-c',str(target),str(backup)],check=True,capture_output=True)
  target.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['/bin/cp','-c',str(src),str(target)],check=True,capture_output=True);assert sha(target)==digest
  copied.append(dict(relative=str(src.relative_to(ROOT)),sha256=digest))
 for key,hkey in [('native_module','native_module_sha256'),('candidate_disc','candidate_disc_sha256')]:assert sha(P/'workbench'/Path(candidate[key]).relative_to(ROOT))==candidate[hkey]
 result=dict(status='terminal_v27_raw_artifact_portable_closure_verified',directory=str(out),package=str(P),new_files_or_pointers=copied,already_identical_files=len(verified),source_directories=len(directories),candidate_module_bytes=candidate['native_module_bytes'],candidate_module_byte_identical=True,candidate_disc_byte_identical=True,new_game_runs=0,new_predictions=0,new_training=False,scope='Exact selected v27 raw verification directories, compiler outputs, full experimental build and proof source references mirrored. Package evidence resolution remains subject to actual guarded MCP/status checks; no preview promotion or game fidelity claim.')
 save(out/'protocol.json',result);save(V/'display-list-portable-closure-v1-current.json',result);print(result['status'],len(copied),'copied',len(verified),'already identical',flush=True)
if __name__=='__main__':main()
