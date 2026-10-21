"""Supplement raw scores with exact-byte ABI aliases; never repair generated C."""
import hashlib,json,re,shutil,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 dataset=json.loads((ROOT/'verification/native-function-curriculum-current.json').read_text());data=Path(dataset['directory']);out=data/'header-resolved-checks';out.mkdir(exist_ok=True);results=[]
 for suite,suffix in [('resource',''),('fresh','-fresh')]:
  for phase in ['base','adapter']:
   pointer=ROOT/'verification'/f'native-function{suffix}-{phase}-evaluation-current.json'
   if not pointer.exists():continue
   evaluation=json.loads(pointer.read_text())
   if evaluation['dataset']!=str(data)or evaluation['status']!='terminal_code_evaluation':continue
   for row in evaluation['results']:
    src=Path(evaluation['directory'])/row['function'];original=json.loads((src/'result.json').read_text());candidate=next(p for p in src.glob('*.c'));assert sha(candidate)==original['candidate_sha256']
    folder=out/(phase+'-'+row['function']);folder.mkdir(exist_ok=True);result_path=folder/'result.json'
    if result_path.exists():
     old=json.loads(result_path.read_text())
     if old['candidate_sha256']==sha(candidate)and old.get('policy_version')==3:results.append(old);continue
    copy=folder/candidate.name;shutil.copy2(candidate,copy);assert sha(copy)==sha(candidate);aliases=[]
    headers=list(src.glob('*.h'))
    for header in headers:
     shutil.copy2(header,folder/header.name);names={header.name.replace('-','_')}
     guard=re.search(r'^#ifndef\s+(\w+)_H\b',header.read_text(),re.M)
     if guard:names.add(guard.group(1).lower()+'.h')
     # The frozen prompts supplied exactly one ABI header but no filename.
     # Resolve quoted basename-only includes to that sole declared ABI;
     # compiler/CPU gates still reject absent helpers or wrong behavior.
     if len(headers)==1:
      names.update(name for name in re.findall(r'^\s*#include\s+"([^"\n]+)"',copy.read_text(),re.M)if name.endswith('.h')and Path(name).name==name)
     for name in sorted(names):
      alias=folder/name;shutil.copy2(header,alias);assert sha(header)==sha(alias)
      aliases.append(dict(original=header.name,alias=alias.name,sha256=sha(header)))
    start=time.monotonic();command=[sys.executable,str(ROOT/'scripts/check_native_curriculum_candidate.py'),row['function'],str(copy),str(folder/'receipts')]
    try:
     r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=240);(folder/'check.log').write_text(r.stdout+r.stderr);verified=r.returncode==0;code=r.returncode
    except subprocess.TimeoutExpired as e:
     (folder/'check.log').write_text(str(e.stdout)+'\n'+str(e.stderr));verified=False;code='timeout'
    result=dict(policy_version=3,suite=suite,phase=phase,function=row['function'],raw_verified=row['verified'],header_resolved_verified=verified,candidate_sha256=sha(copy),generated_C_unchanged=True,aliases=aliases,exit_code=code,seconds=time.monotonic()-start,original_result=str(src/'result.json'),directory=str(folder))
    result_path.write_text(json.dumps(result,indent=2)+'\n');results.append(result);print(phase,row['function'],'header-resolved',verified,flush=True)
 report=dict(status='terminal_observed_header_resolution_checks',policy_version=3,recorded_at=datetime.now(timezone.utc).isoformat(),dataset=str(data),results=results,scores={suite:{phase:dict(passed=sum(x['header_resolved_verified']for x in results if x['suite']==suite and x['phase']==phase),total=sum(x['suite']==suite and x['phase']==phase for x in results))for phase in ['base','adapter']}for suite in ['resource','fresh']},raw_scores_unchanged=True,source_code_repaired=False,default_promoted=False,scope='Supplemental build-boundary check after raw strict scores. Frozen prompts omitted explicit header filenames. With exactly one supplied ABI header,quoted basename-only includes map to that byte-identical header; slash/path includes are not resolved. Conventional filename/guard aliases are also supplied. Generated C bytes,compiler warnings and full native CPU/RAM/ordered-access gates remain unchanged. Development build normalization,not raw task success or model-authored repair.')
 (ROOT/'verification/native-function-header-resolved-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['scores']),flush=True)
if __name__=='__main__':main()
