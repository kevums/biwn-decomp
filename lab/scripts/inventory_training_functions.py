"""Preparation only: exact C function/header identities, never automatic training labels."""
import concurrent.futures,hashlib,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RESTORE=ROOT/'projects/black-ice-white-noise/restoration'
def sha(data):return hashlib.sha256(data).hexdigest()
def inspect(row):
 source=Path(row['source']);raw=source.read_bytes();assert sha(raw)==row['sha256'];seen={};missing=[]
 def headers(file):
  for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"',file.read_text(),re.M):
   choices=[file.parent/name,RESTORE/name];p=next((p.resolve()for p in choices if p.is_file()),None)
   if p is None or not p.is_relative_to(RESTORE):missing.append(dict(from_file=str(file),include=name));continue
   if str(p) in seen:continue
   seen[str(p)]=sha(p.read_bytes());headers(p)
 headers(source)
 process=subprocess.run(['clang','-std=c99','-I',str(RESTORE),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True,timeout=30);functions=[]
 if process.returncode==0:
  tree=json.loads(process.stdout)
  for node in tree['inner']:
   if node['kind']!='FunctionDecl'or not any(n.get('kind')=='CompoundStmt'for n in node.get('inner',[])):continue
   if node.get('loc',{}).get('includedFrom'):continue
   begin=node['range']['begin'];end=node['range']['end']
   if 'offset'not in begin or 'offset'not in end:continue
   a=begin['offset'];b=end['offset']+end['tokLen'];body=raw[a:b]
   functions.append(dict(name=node['name'],signature=node['type']['qualType'],storage=node.get('storageClass','external'),start_byte=a,end_byte_exclusive=b,start_line=raw[:a].count(b'\n')+1,body_sha256=sha(body),body_bytes=len(body)))
 return dict(source=str(source),source_sha256=row['sha256'],syntax_pass=process.returncode==0,diagnostics=process.stderr[:3000],headers=seen,unresolved_quoted_headers=missing,functions=functions,proof_candidates=row['proof_candidates'],training_ready=False,review_required=['map original assembly/function boundary','verify proof scope and coverage','separate functions and near-duplicate families before splitting','review helper/provider assumptions'])
def main():
 inventory=json.loads((ROOT/'verification/restoration-training-source-provenance-current.json').read_text());rows=[r for r in inventory['source_units']if Path(r['source']).suffix=='.c']
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(inspect,rows))
 groups={}
 for row in results:
  for function in row['functions']:groups.setdefault(function['body_sha256'],[]).append(dict(source=row['source'],name=function['name']))
 duplicate=[v for v in groups.values()if len(v)>1]
 report=dict(status='function_and_header_inventory_pending_semantic_training_review',recorded_at=datetime.now(timezone.utc).isoformat(),source_units=len(results),syntax_pass_units=sum(r['syntax_pass']for r in results),source_functions=sum(len(r['functions'])for r in results),units_with_unresolved_quoted_headers=sum(bool(r['unresolved_quoted_headers'])for r in results),identical_body_groups=duplicate,units=results,training_ready=False,weights_trained=False,scope='Current hash-matched source/proof candidates only. Clang identities and transitive local quoted headers; syntax success does not establish original-game equivalence. No generated labels, automatic train/test split or weights trained. Function-family and assembly/proof review still required.')
 path=ROOT/'verification/restoration-training-function-inventory-current.json';path.write_text(json.dumps(report,indent=2)+'\n');print({k:report[k]for k in ['status','source_units','syntax_pass_units','source_functions','units_with_unresolved_quoted_headers']});print('identical body groups',len(duplicate))
if __name__=='__main__':main()
