"""Freeze same-input development outcomes, including load errors and all rejected C."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 pp=ROOT/'verification/native-author-model-comparison-current.json';p=json.loads(pp.read_text());assert p['status']=='terminal_model_profile_comparison_complete'and p['daily_restored']and len(p['results'])==6
 spec=Path(p['precommitted_specification']);assert sha(spec)==p['precommitted_sha256'];definition=json.loads(spec.read_text());assert definition['repair_feedback']is False and definition['max_output_tokens']==4500 and definition['context_length']==16384
 prior=p['prior_protocol'];assert prior['precommitted_sha256']==p['precommitted_sha256']
 assert all(not x['gate_passed']and x['gate_exit_code']==1 and x['canonical_accepted']is False for x in p['results'])
 out=ROOT/'verification/native-author-model-comparison-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);deps={};snapshots={};review=[]
 def pin(path,snapshot=False):
  path=Path(path).resolve();assert path.is_relative_to(ROOT);rel=str(path.relative_to(ROOT));digest=sha(path)
  if snapshot:
   dest=out/(hashlib.sha256(rel.encode()).hexdigest()[:12]+'-'+path.name)
   if not dest.exists():shutil.copy2(path,dest)
   assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;snapshots[rel]=str(dest.relative_to(ROOT))
  else:deps[rel]=digest
 pin(pp,True);pin(spec,True);pin(Path(__file__),True)
 for row in p['results']:
  directory=Path(row['directory']);assert sha(row['source'])==row['source_sha256']and sha(directory/'candidate-gate.py')==row['gate_script_sha256'];active=Path(row['gate_active_proof']);gate=json.loads(active.read_text());assert gate['status']=='terminal_failed';gd=Path(gate['directory']);mismatch=gd/'mismatch.json'
  reason='strict_compilation_failure';case=None;differences={}
  if mismatch.exists():
   data=json.loads(mismatch.read_text());reason='native_return_or_public_RAM_hardware_mismatch';case=data['case'];a=data['original_CPU'];b=data['compiled_CPU'];differences={k:{'original':a[k],'candidate':b[k]}for k in a if a[k]!=b[k]};pin(mismatch)
  review.append(dict(profile=row['profile'],task=row['task'],reported_seconds=row['reported_seconds'],usage=row['usage'],gate_passed=False,rejection=reason,first_failed_case=case,CPU_differences=differences,raw_source=str(row['source']),exact_prompts_and_responses=str(directory/'prompts-and-responses.txt')))
  for path in directory.iterdir():
   if path.is_file():pin(path,True)
  pin(active,True)
  for name in ['make.log','protocol.json','fixtures.json','disassembly.txt']:
   path=gd/name
   if path.exists():pin(path,True)
 for directory in [Path(p['directory']),Path(prior['directory'])]:
  for path in directory.iterdir():
   if path.is_file():pin(path,True)
 facts=dict(status='both_profiles_zero_of_three_strict_module_passes',profiles=p['loaded_profiles'],cases=review,scope=definition['scope'],prompt_budget=dict(context=16384,workers=1,reasoning='off',temperature=0.2,max_output_tokens=4500),repairs_or_feedback_supplied=False,coordinator_full_branch_algorithms_supplied=False,ABI_helpers_supplied=True,prior_task_development_exposure=True,native_UI_verified=False,new_training=False,weights_promoted=False,daily_restored=True,daily_after=p['daily_after'],conclusion='Daily27B6bit and installed CoderNextGGUFQ3both reject3of3module drafts under this same assembly/ABI prompt suite. Two strict compilation failures and four first-case native mismatches; invalid outputs cannot establish a speed-quality advantage. This is a known-module development comparison, not heldout/general reasoning or advertising quality evidence. No raw candidate replaces canonical code. Next steps require richer typed operand/frame inputs and separate function-grouped training/holdout decisions.',loader_notes='First launcher failed before generation on unsupported engine-config flag; next run completed daily3tasks but failed Nextfullpath lookup. Continuation resolved that exact catalogGGUFpath to CLI modelKey, retained same frozen prompts/target weights and did not repeat baseline. Original attempts/logs preserved.')
 manifest=dict(status='published_native_author_development_comparison',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),facts=facts,dependencies_sha256=deps,source_snapshots=snapshots,new_training=False,whole_game_complete=False)
 save(out/'publication.json',manifest);save(ROOT/'verification/native-author-model-comparison-publication-current.json',manifest);print(json.dumps({'status':facts['status'],'directory':str(out),'dependencies':len(deps)}),flush=True)
if __name__=='__main__':main()
