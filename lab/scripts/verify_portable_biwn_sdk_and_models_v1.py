"""Compare copied installed dependency files and all selected model resources."""
import hashlib,json,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 v=ROOT/'verification';package=Path(json.loads((v/'portable-biwn-current-v1-current.json').read_text())['package']);out=v/'portable-biwn-model-integrity-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='checking_copied_dependencies_and_weights',pid=os.getpid(),directory=str(out),package=str(package),dependency_files_verified=0,model_files_verified=0)
 def mark():save(out/'protocol.json',state);save(v/'portable-biwn-model-integrity-v1-active.json',state)
 mark();source=ROOT/'.venv/lib/python3.12/site-packages';target=package/'runtime/.venv/lib/python3.12/site-packages';rows=[]
 for path in sorted(source.rglob('*')):
  if not path.is_file()or '__pycache__'in path.parts or path.suffix=='.pyc':continue
  dest=target/path.relative_to(source);assert dest.exists()and dest.stat().st_size==path.stat().st_size,str(dest);digest=sha(path);assert sha(dest)==digest,str(dest);rows.append(dict(relative=str(path.relative_to(source)),sha256=digest,bytes=path.stat().st_size))
  if len(rows)%2048==0:state['dependency_files_verified']=len(rows);mark();print('Dependency files',len(rows),flush=True)
 save(out/'dependency-files.json',rows);inventory_record=json.loads((v/'relocated-model-copy-current.json').read_text());inventory=json.loads((Path(inventory_record['directory'])/'frozen-inventory.json').read_text());model_rows=[]
 for i,row in enumerate(inventory):
  relative=Path(row['target_home_relative']);p=package/'lmstudio-home'/Path(*relative.parts[1:]);assert p.stat().st_size==row['bytes']and sha(p)==row['sha256'],str(p);model_rows.append(dict(row,target=str(p)));state['model_files_verified']=len(model_rows);mark()
  if row['weight_shard']:print('Copied weight shard',i+1,'/',len(inventory),'verified',flush=True)
 save(out/'model-files.json',model_rows);state.update(status='terminal_portable_dependencies_and_model_hashes_pass',dependency_files_verified=len(rows),dependency_bytes=sum(x['bytes']for x in rows),model_files_verified=len(model_rows),weight_shards_verified=sum(x['weight_shard']for x in model_rows),model_bytes=sum(x['bytes']for x in model_rows),source_sha256={str(p):sha(p)for p in [Path(__file__),out/'dependency-files.json',out/'model-files.json']},scope=__doc__);mark();save(v/'portable-biwn-model-integrity-v1-current.json',state);print(json.dumps({k:state[k]for k in ['status','dependency_files_verified','model_files_verified','weight_shards_verified']}))
if __name__=='__main__':main()
