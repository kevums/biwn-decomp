"""Verify the paired trial, preserved game artifacts and immutable evidence copies."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
cache={}
def sha(p):
 p=Path(p).resolve()
 if p not in cache:
  with p.open('rb')as f:cache[p]=hashlib.file_digest(f,'sha256').hexdigest()
 return cache[p]
def read(p):return json.loads(Path(p).read_text())
def main():
 review=read(ROOT/'verification/native-function-trial-reviewed-current.json');assert review['status']=='terminal_native_function_training_comparison'and review['completed_updates']==32
 data=Path(review['dataset']);job=Path(review['training_job']);files=set();pairs=[]
 for name in ['split-manifest.json','token-preflight.json','reviewed-source-examples.jsonl','train.jsonl','valid.jsonl','test.jsonl','ABI-sidecar-audit.json']:files.add(data/name)
 for group in ['phases','fresh_phases']:
  base,adapter=[review[group][phase]for phase in ['base','adapter']]
  assert base['status']==adapter['status']=='terminal_code_evaluation'and base['daily_model_restored']and adapter['daily_model_restored']
  for row in base['results']:
   ident=row['function'];left=Path(base['directory'])/ident/'prompt.json';right=Path(adapter['directory'])/ident/'prompt.json';assert left.read_bytes()==right.read_bytes();pairs.append(dict(function=ident,prompt_sha256=sha(left),exact_prompt_pair=True))
  for phase in ['base','adapter']:
   folder=Path(review[group][phase]['directory']);files.update(p for p in folder.rglob('*')if p.is_file())
 for current in ['native-function-curriculum-current.json','native-function-training-current.json','native-function-followup-current.json','native-function-fresh-case-current.json','native-function-trial-reviewed-current.json','native-function-header-resolved-current.json','native-format-pad-current.json','native-format-pad-publication-current.json']:
  files.add(ROOT/'verification'/current)
 resolved=read(ROOT/'verification/native-function-header-resolved-current.json');assert len(resolved['results'])==8 and resolved['policy_version']==3
 for row in resolved['results']:
  folder=Path(row['directory']);candidate=next(folder.glob('*.c'));assert sha(candidate)==row['candidate_sha256']
  for alias in row['aliases']:assert sha(folder/alias['alias'])==alias['sha256']
  files.update(p for p in folder.rglob('*')if p.is_file())
  active=read(next((folder/'receipts').glob('*-active.json')));actual=Path(active['directory'])
  for name in ['protocol.json','mismatch.json','make.log','build.log']:
   if(actual/name).exists():files.add(actual/name)
 for attempt in (data/'jobs').glob('*'):
  files.update(p for p in attempt.rglob('*')if p.is_file())
 files.update(p for p in (data/'orchestration-snapshot').glob('*')if p.is_file())
 files.update(p for p in (data/'finite-evaluation-followup').glob('*')if p.is_file())
 fresh=read(ROOT/'verification/native-function-fresh-case-current.json');fresh_dir=Path(fresh['case_file']).parent;files.update(p for p in fresh_dir.rglob('*')if p.is_file())
 native=read(ROOT/'verification/native-format-pad-current.json');files.update(Path(p)for p in native['artifacts_sha256']);files.update(p for p in Path(native['directory']).rglob('*')if p.is_file())
 files.add(ROOT/'reports/native-function-trial.txt');files.add(ROOT/'reports/native-function-trial-prompts.txt')
 controls=ROOT/'verification/native-curriculum-positive-controls/proof.json';files.add(controls)
 for row in read(controls)['checks']:files.add(Path(row['proof']))
 checks={}
 for recipe in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  pins=read(ROOT/'verification'/recipe)['hashes'];assert all(sha(p)==h for p,h in pins.items());checks[recipe]=len(pins)
 prior_path=ROOT/'verification/native-load-scan-current.json';prior=read(prior_path);assert all(sha(p)==h for p,h in prior['dependencies_sha256'].items());checks['prior_native28_dependencies']=len(prior['dependencies_sha256'])
 original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert sha(original)=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f';checks['original_CDI_unchanged']=True
 daily=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(daily)==1 and daily[0]['identifier']=='advertising-scholar'and daily[0]['contextLength']==32768 and daily[0]['parallel']==1 and daily[0]['status']=='idle'
 out=ROOT/'verification/native-function-trial-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshots={};deps={}
 for p in sorted(files):
  digest=sha(p);dest=out/(digest+'-'+p.name)
  if not dest.exists():shutil.copy2(p,dest)
  assert sha(dest)==digest;deps[str(p)]=digest;snapshots[str(p)]=str(dest)
 result=dict(status='native_function_trial_published_unpromoted_goal_incomplete',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),review=str(ROOT/'verification/native-function-trial-reviewed-current.json'),review_sha256=sha(ROOT/'verification/native-function-trial-reviewed-current.json'),paired_prompts=pairs,preserved_artifacts=checks,daily_model=daily[0],dependencies_sha256=deps,source_snapshots=snapshots,default_promoted=False,goal_complete=False,whole_game_complete=False,native_Chat_verified=False,scope='One32update one-layer full-example LoRA trial after a retained two-layer first-update Metal OOM. Both profiles0/3adaptive resource gates and0/1fresh formatting gate; supplemental sole-ABI-header filename resolution also yields0/3and0/1. Coordinator standalone formatting C passes1668native/1684ordered checks but is not in the disc or model training. No model quality/default/full-game/physical/native Chat completion claim.')
 (out/'publication.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'verification/native-function-trial-publication-current.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],files=len(deps),paired_prompts=len(pairs),preserved=checks,directory=str(out))),flush=True)
if __name__=='__main__':main()
