"""Regrade saved unchanged base C with the qualified plane scoring wrapper."""
import argparse,json,hashlib,subprocess,sys,textwrap,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('protocol',type=Path);args=ap.parse_args();args.protocol=args.protocol.resolve();base=read(args.protocol)
 assert base['status']=='terminal_code_evaluation'and base['phase']=='base'and base['daily_model_restored']and len(base['results'])==4
 data=Path(base['dataset']);rows=[json.loads(x)for x in(data/'reviewed-source-examples.jsonl').read_text().splitlines()if json.loads(x)['split']=='test'];assert len(rows)==4
 qualified=V/'plane-model-scorer-qualified-v4-current.json';qual=read(qualified);assert qual['status']=='terminal_exact_plane_model_scorer_positive_reference_pass'
 for p,h in qual['source_sha256'].items():assert sha(p)==h,p
 out=V/'game-geometry-base-reviewed-v4'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copyfile(args.protocol,out/'original-protocol.json')
 original=Path(base['directory']);bound={args.protocol,qualified,out/'original-protocol.json',Path(__file__),data/'reviewed-source-examples.jsonl',data/'split-manifest.json'}
 # Bind the actual saved old generation driver, not its subsequently fixed
 # workspace path. The first three original scoring drivers are unchanged.
 for p,h in base['execution_scripts_sha256'].items():
  f=original/'orchestration-as-run'/Path(p).name;assert sha(f)==h,f;bound.add(f)
 for row in rows:
  folder=original/row['function_id'];assert read(folder/'prompt.json')==row['messages'][:-1]
  result=read(folder/'result.json');assert result['candidate_sha256']==sha(folder/Path(row['source']).name)
  bound.update(folder/n for n in ['prompt.json','response.txt','inference.json','result.json','check.log',Path(row['source']).name])
 row=next(x for x in rows if x['function_id']=='plane_layout');folder=out/'rescored-plane';folder.mkdir();candidate=original/'plane_layout'/Path(row['source']).name
 evaluator=ROOT/'scripts/evaluate_game_geometry_curriculum_v4.py';text=evaluator.read_text();start=text.index("    if row['function_id']=='plane_layout':");end=text.index('    try:\n     checked=subprocess.run',start)
 scope=dict(ROOT=ROOT,Path=Path,folder=folder,candidate=candidate,row=row,sys=sys);exec(compile(textwrap.dedent(text[start:end]),'exact-plane-scoring-branch','exec'),scope)
 checked=subprocess.run(scope['command'],capture_output=True,text=True,timeout=240);(folder/'check.log').write_text(checked.stdout+checked.stderr)
 outcome=dict(function='plane_layout',verified=False,exit_code=checked.returncode,raw_candidate_sha256=sha(candidate),new_predictions=0,new_optimizer_updates=0,format_normalization='Same unchanged C extracted by original base driver;no new source edits.')
 if checked.returncode==0:
  gate=read(folder/'receipts/plane-layout-current.json');assert gate['completed']==1408 and gate['bus_error_cases']==65;outcome.update(verified=True,gate=gate)
 result=[dict(x)for x in base['results']]
 for x in result:
  if x['function']=='plane_layout':x.update(verified=outcome['verified'],rescored_with_qualified_wrapper=True)
 save(folder/'result.json',outcome);bound.update([evaluator,folder/'plane-checker-as-run.py',folder/'check.log',folder/'result.json'])
 proof=dict(status='terminal_frozen_base_controls_rescored_valid',directory=str(out),dataset=str(data),original_base_protocol=str(args.protocol),generation_directory=str(original),results=result,passed=sum(x['verified']for x in result),total=4,daily_model_restored=base['daily_model_restored'],sampling=base['sampling'],raw_model_C_unchanged=True,new_predictions=0,new_optimizer_updates=0,
  scope='Four original base generations retained. Plane scorer module-docstring metadata bug fixed and qualified with1408positive/65error cases before regrading unchanged C. The original three resource gates remain as run. Training launcher was stopped before any optimizer update. Complete frozen source-family tests;not a broad reliability result.',source_sha256={str(p):sha(p)for p in bound})
 save(out/'review.json',proof);save(V/'game-geometry-base-reviewed-v4-current.json',proof);print(out,'base passes',proof['passed'],'/',4,flush=True)
if __name__=='__main__':main()
