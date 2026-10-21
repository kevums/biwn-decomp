"""Copy the current saved prompt/response index and its referenced records."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 state=read(V/'portable-biwn-current-v1-current.json');package=Path(state['package']);index=read(V/'current-model-work-index-v4-current.json');files=[V/'current-model-work-index-v4-current.json',Path(index['report']),Path(index['directory'])/'manifest.json',Path(index['source_list_snapshot'])];rows=[]
 frozen=Path(index['source_list_snapshot']);destination=package/'workbench/config/current-model-work-sources.json';subprocess.run(['/bin/cp','-c',str(frozen),str(destination)],check=True,capture_output=True);assert sha(destination)==index['source_list_sha256']
 for name,title in read(frozen):
  p=V/name
  if p.is_file():files.append(p)
 for row in index['files']:
  for field in ['path','prompt','response','protocol']:
   if row.get(field):files.append(Path(row[field]))
 for p in sorted(set(files)):
  if not p.is_relative_to(ROOT)or not p.is_file():continue
  target=package/'workbench'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['/bin/cp','-c',str(p),str(target)],capture_output=True,check=True);assert sha(p)==sha(target);rows.append(dict(relative=str(target.relative_to(package)),sha256=sha(p)))
 # Saved directories that contain explicit role transcripts are represented by
 # their actual indexed file;no predictions are replayed by the export.
 result=subprocess.run([str(package/'runtime/python/bin/python3.12'),str(package/'workbench/portable_biwn.py'),'prompts'],capture_output=True,text=True,cwd='/',timeout=30);out=Path(state['directory']);(out/'copied-prompts-export.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 copied=read(package/'workbench/verification/current-model-work-index-v4-current.json');assert copied['saved_prompt_or_transcript_records']==index['saved_prompt_or_transcript_records']==171,copied['saved_prompt_or_transcript_records']
 proof=dict(status='terminal_current_171_saved_prompt_transcript_records_export_from_moved_copy',package=str(package),saved_records=171,new_predictions=0,new_training=False,copied_files=rows);(out/'copied-transcripts-v2.json').write_text(json.dumps(proof,indent=2)+'\n');(V/'portable-biwn-transcripts-v2-current.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'])
if __name__=='__main__':main()
