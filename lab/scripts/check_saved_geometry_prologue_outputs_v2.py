"""Diagnose the two saved complete prologues; no model replay or source-body edits."""
import re,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
from geometry_records_model_source_parser_v2 import extract

def normalize(raw):
 text=raw.strip();normalization=[]
 if text.startswith('```c\n')and text.endswith('```'):text=text[5:-3].strip();normalization.append('outer Markdown fence removed')
 signature=r'^static\s+void\s+geometry_records_prologue\s*\(\s*struct\s+biwn_deck_context\s*\*\s*s\s*\)\s*\{'
 if not re.match(signature,text):raise ValueError('Expected prologue signature after optional complete fence')
 checked=text.replace('geometry_records_prologue','geometry_records_body',1);a=checked.index('{')+1;z=checked.rfind('}');extract(checked[:a]+'GEOMETRY_RECORDS_BEGIN(s);'+checked[a:z]+'GEOMETRY_RECORDS_END(s);'+checked[z:])
 if re.search(r'\b(?:GEOMETRY_RECORDS_BEGIN|GEOMETRY_RECORDS_END)\s*\(',text):raise ValueError('Block must not duplicate outer markers')
 if re.search(r's\s*->\s*cpu\s*\.\s*pc\s*=',text):raise ValueError('Block must not assign outer PC')
 return text[text.index('{')+1:text.rfind('}')],normalization

def main():
 pointer=V/'local-geometry-records-prologue-v1-current.json';run=read(pointer);assert run['status']=='terminal_local_prologue_attempts_rejected' and run['new_predictions']==2
 folder=Path(run['directory']);out=V/'local-geometry-prologue-reviewed-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 reference=ROOT/'projects/black-ice-white-noise/restoration/experimental/geometry-records-structured-v1/coordinator-reference.inc';gold=reference.read_text();a=gold.index(' /* MOVEM predecrement order:');z=gold.index(' gr_move_register(s,3,2,0);',a);rows=[];deps={str(Path(__file__)):sha(__file__),str(pointer):sha(pointer),str(reference):sha(reference),**run['source_sha256']}
 for role in ['Author_Prologue','Repair_Prologue']:
  source=folder/role;d=out/role;d.mkdir();raw=(source/'response.txt').read_text();interior,normalization=normalize(raw)
  (d/'unedited-model-interior.inc').write_text(interior);composite=d/'composite.inc';composite.write_text(gold[:a]+'\n {'+interior+'}\n'+gold[z:]);gate=d/'host-gate'
  with(d/'check.log').open('w')as log:q=subprocess.run([str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/check_geometry_records_structured_host_v1.py'),'--body-source',str(composite),'--output',str(gate),'--no-publish'],cwd='/',stdout=log,stderr=subprocess.STDOUT,timeout=300)
  compiler=(gate/'compiler.txt').read_text();assert q.returncode!=0 and "unused variable 'u'"in compiler
  assert not(gate/'fixtures.json').exists() and not(gate/'report.json').exists()
  inference=read(source/'inference.json');rows.append(dict(role=role,seconds=inference['seconds'],output_tokens=inference['usage']['completion_tokens'],complete_source=True,normalization=normalization,body_statement_edits=0,original_checker_feedback=read(source/'feedback.json'),source_form_v2_pass=True,extra_entry_budget_guard=bool(re.search(r'\bgr_work\s*\(',interior)),compile_attempted=True,compile_pass=False,compiler_reason="unused local variable 'u' under existing -Werror",semantic_machine_cases_run=0,host_verified=False,native_verified=False,compiler_log=str(gate/'compiler.txt')))
  for p in source.rglob('*'):
   if p.is_file():deps[str(p)]=sha(p)
  for p in d.rglob('*'):
   if p.is_file():deps[str(p)]=sha(p)
 transcript=out/'prompts-and-responses.txt';transcript.write_bytes((folder/'prompts-and-responses.txt').read_bytes());deps[str(transcript)]=sha(transcript)
 report=ROOT/'reports/BIWN Bounded Geometry Prologue Agent Review.txt'
 report.write_text('BIWN — bounded local22instruction prologue\n\nTwo actual copied-model generations completed:Author50.23seconds/915tokens,Repair34.62seconds/650tokens. Both now produce complete short C,unlike the previous full-function truncations. Original prompt and exact outputs are preserved. Target block was withheld,while the existing coordinator remainder supplies the rest of the full function. This is development scaffolding,not independent or held-out review.\n\nThe initial checker rejected an extra gr_work guard with opaque AssertionError feedback;Repair then failed raw-only signature parsing because it included a complete Markdown fence. Corrected parsing removes only an outer complete fence and reports block-contract violations explicitly. No model source statements were edited.\n\nBoth saved candidates were actually passed to the unchanged strict C host build. Each fails compilation for unused local variable u under existing -Werror. Zero semantic machine cases ran. Both also contain an extra gr_work call despite a prompt requiring the outer budget guard to remain singular;budget/CPU/RAM/helper semantics are unverified. Neither is installed,no source is adopted,and no optimizer updates occurred. Corrected feedback can cite the compiler error and redundant guard before another bounded Repair.\n\nExact transcript: '+str(transcript)+'\n')
 facts=dict(status='terminal_two_complete_local_prologue_outputs_compile_rejected_unused_variable',directory=str(out),report=str(report),original_run_directory=str(folder),actual_predictions=2,new_predictions_in_this_review=0,roles=rows,compiled_attempts=2,compiled_successes=0,semantic_machine_cases_run=0,model_source_installed=False,new_training=False,optimizer_updates=0,native_Chat_verified=False,coordinator_target_block_supplied=False,coordinator_remainder_used=True,held_out_benchmark=False,source_sha256=deps)
 save(out/'review.json',facts);save(V/'local-geometry-prologue-reviewed-v2-current.json',facts)
 for p in [*map(Path,deps),out/'review.json',report,V/'local-geometry-prologue-reviewed-v2-current.json']:
  if p.is_relative_to(ROOT):
   dest=P/'workbench'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
 print(facts['status'],flush=True)
if __name__=='__main__':main()
