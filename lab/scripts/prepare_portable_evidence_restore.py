"""Clone canonical evidence/assets into a new root and exercise a strict path resolver."""
import json,hashlib,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
import portable_biwn_status as portable

def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc);out=ROOT/'migration/evidence-restore'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);dest=out/'workbench';dest.mkdir();pp=ROOT/'verification/current-biwn-latest-publication-current.json';publication=read(pp);pubhash=portable.digest(pp);state=dict(status='preparing_offline_evidence_restore',directory=str(out),destination=str(dest),original_workbench=str(ROOT),pid=__import__('os').getpid(),copied_model_bytes=0,off_machine_restore_verified=False,full_workbench_restore_verified=False,live_MCP_frontend_installed=False,new_training=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/evidence-restore-pilot-active.json',state)
 mark()
 with ReferenceBridge()as bridge:captured=bridge.call('project_evidence',{'topic':'status'});connection=bridge.metadata
 assert captured['proof_sha256']==pubhash and len(captured['processor_tests'])==5
 paths=dict(publication['dependencies_sha256']);additional={}
 def add(p,expected=None):
  p=Path(p).resolve();assert p.is_relative_to(ROOT)and p.is_file();h=expected or portable.digest(p)
  if str(p)in paths:assert paths[str(p)]==h
  paths[str(p)]=h;additional[str(p)]=h
 add(pp,pubhash)
 # Include BIWN input plus current tested/pending disc and source-stage assets.
 original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';add(original,'0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f')
 add(publication['facts']['experimental_build']['derived_disc'],publication['facts']['experimental_build']['derived_disc_sha256'])
 pending=read(ROOT/'verification/native-actor-move-disc-build-current.json')
 for key in ['derived_disc','derived_stage','component']:add(pending[key],pending[key+'_sha256'])
 for p in ROOT.glob('*.py'):add(p)
 for p in ROOT.glob('*.command'):add(p)
 for p in [ROOT/'requirements.lock',ROOT/'config.json',ROOT/'portable_biwn_status.py']:add(p)
 modelinv=read(ROOT/'verification/model-migration-inventory-current.json');add(Path(modelinv['directory'])/'files.json')
 records=[]
 def copy_one(item):
  name,expected=item;p=Path(name);target=dest/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
  assert portable.digest(p)==expected,name
  cp=subprocess.run(['/bin/cp','-c',str(p),str(target)],capture_output=True,text=True);method='APFSclone'
  if cp.returncode:shutil.copy2(p,target);method='bytecopy'
  assert portable.digest(target)==expected,name
  return dict(original=name,target_relative=str(target.relative_to(dest)),bytes=p.stat().st_size,sha256=expected,copy_method=method)
 with ThreadPoolExecutor(max_workers=4)as pool:
  for row in pool.map(copy_one,paths.items()):records.append(row)
 save(out/'files.json',records);save(dest/'migration-status-as-recorded.json',captured);origin=dict(original_workbench=str(ROOT),publication_original_path=str(pp),publication_sha256=pubhash,status_snapshot_sha256=portable.digest(dest/'migration-status-as-recorded.json'),additional_assets_sha256=additional,snapshot_at=now.isoformat(),scope='Canonical source/evidence/BIWN assets and recorded status only; excluded models,fullhistoricalruns/tools/training/runtime. No livePIDclaims.')
 save(dest/'.portable-origin.json',origin);result=portable.load(dest);assert result['all_verified_reads_inside_restored_root']and result['experimental_build']['resident_bytes']==publication['facts']['experimental_build']['resident_bytes'];assert Path(result['experimental_build']['derived_disc']).is_relative_to(dest)
 negatives=[]
 for name,bad in [('outside_origin','/tmp/outside-workbench'),('parent_traversal',str(ROOT)+'/../outside')]:
  try:portable.resolve_recorded(dest,str(ROOT),bad)
  except ValueError:negatives.append(dict(defect=name,rejected=True))
  else:raise AssertionError('Portable path boundary bypassed')
 symlink=dest/'escape-probe';symlink.symlink_to(ROOT/'portable_biwn_status.py')
 try:
  try:portable.resolve_recorded(dest,str(ROOT),str(ROOT/'escape-probe'))
  except ValueError:negatives.append(dict(defect='symlink_escape_to_original',rejected=True))
  else:raise AssertionError('Original-tree fallback escaped bundle boundary')
 finally:symlink.unlink()
 # Corrupt one restored evidence file, require hash failure, then restore exact bytes.
 selected=next(Path(p)for p in result['read_paths']if Path(p).suffix=='.py');bytes_before=selected.read_bytes();selected.write_bytes(bytes_before+b'\n# restore integrity probe\n')
 try:
  try:portable.load(dest)
  except ValueError as error:assert 'hash mismatch'in str(error);negatives.append(dict(defect='copied_evidence_corruption',rejected=True))
  else:raise AssertionError('Corrupted restored evidence accepted')
 finally:selected.write_bytes(bytes_before)
 final=portable.load(dest);assert final['all_verified_reads_inside_restored_root'];save(out/'restored-status.json',{k:v for k,v in final.items()if k!='read_paths'});save(out/'verified-read-paths.json',final['read_paths']);state.update(status='terminal_offline_evidence_restore_pilot_pass',files=len(records),logical_bytes=sum(x['bytes']for x in records),APFS_clones=sum(x['copy_method']=='APFSclone'for x in records),evidence_files_verified=final['evidence_files_verified'],all_verified_reads_inside_restored_root=True,original_tree_fallback=False,tested_resident_bytes=final['experimental_build']['resident_bytes'],pending_resident_bytes=final.get('next_component_development',{}).get('latest_built_resident_bytes'),negative_controls=negatives,processor_statuses='Five terminal receipts captured from actual configuredMCP; historical,no restored PIDinspection',MCP_connection=connection,source_sha256={str(p):portable.digest(p)for p in [Path(__file__),ROOT/'portable_biwn_status.py',out/'files.json',dest/'.portable-origin.json',dest/'migration-status-as-recorded.json',out/'restored-status.json',out/'verified-read-paths.json']},scope='Same-host different-root offline canonical-evidence/BIWN restoration. Models not copied; full runtime/toolchain/training/corpus/index/workflow/preset restoration, off-machine validation and future hardware remain unverified. Sources and historical hash keys unchanged; renderer maps artifact paths only.');mark();save(ROOT/'verification/evidence-restore-pilot-current.json',state);print(json.dumps({k:state[k]for k in ['status','files','logical_bytes','evidence_files_verified','all_verified_reads_inside_restored_root','destination']}))
if __name__=='__main__':main()
