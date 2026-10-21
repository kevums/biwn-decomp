"""Freeze exact two local outputs and distinguish truncation from semantic gates."""
import json,shutil
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 pointer=V/'local-geometry-records-source-v1-current.json';run=read(pointer);assert run['status']=='terminal_local_records_two_attempts_rejected'and run['new_predictions']==2 and not run['new_training']
 folder=Path(run['directory']);out=V/'local-geometry-records-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);roles=[];deps={str(pointer):sha(pointer),str(Path(__file__)):sha(__file__)}
 for role in ['Author','Repair']:
  d=folder/role;response=read(d/'inference.json');request=read(d/'stream-request.json');text=(d/'response.txt').read_text();feedback=read(d/'feedback.json');assert response['text']==text and response['usage']['completion_tokens']==6499 and request['max_output_tokens']==6500
  assert text.startswith('```c\nstatic void geometry_records_body(struct biwn_deck_context *s)')and not text.rstrip().endswith('```')and 'GEOMETRY_RECORDS_END(s)'not in text
  assert feedback==dict(source_restriction_pass=False,error='Exact body signature required')
  assert not(d/'host-gate').exists()and not(d/'model-body.inc').exists()
  roles.append(dict(role=role,seconds=response['seconds'],time_to_first_message_seconds=response['stream']['time_to_first_message_seconds'],output_tokens=6499,prompt_tokens=response['usage']['prompt_tokens'],configured_output_cap=6500,raw_response=str(d/'response.txt'),raw_response_sha256=sha(d/'response.txt'),classification='incomplete_output_at_token_cap',opening_signature_valid=True,closing_fence_missing=True,body_completion_marker_missing=True,parser_feedback_misclassified=True,compiled=False,host_verified=False,native_verified=False,coordinator_body_edits=0))
  for path in d.rglob('*'):
   if path.is_file():deps[str(path)]=sha(path)
 for name in ['protocol.json','task.json','prompts-and-responses.txt','prepared-prompts.txt']:
  path=folder/name;deps[str(path)]=sha(path)
 assert roles[0]['raw_response_sha256']==roles[1]['raw_response_sha256'],'Expected exact repeated greedy output'
 transcript=out/'prompts-and-responses.txt';shutil.copy2(folder/'prompts-and-responses.txt',transcript);save(out/'run-as-reviewed.json',run)
 report=ROOT/'reports/BIWN Local Geometry Author and Repair.txt'
 report.write_text('BIWN — local170A0 Author and Repair\n\n'
  'Two actual generations used the copied local27B model through LM Studio API. Author324.08seconds,Repair345.03seconds. Each emitted6,499tokens under a6,500token cap and stopped mid-expression before completing the function. First streamed text appeared after7.262/11.135seconds;these timings exclude waiting for the shared lease. Total end-to-end user waiting was not instrumented. Both raw outputs are byte-identical. No optimizer updates or new trained weights.\n\n'
  'Neither response was compiled or installed. The source-form parser reported an exact-signature error because it could not remove an unclosed code fence. The opening function signature was valid;the actual problem was incomplete output at the token limit. Repair therefore received misleading feedback and repeated the same truncated code. This is a workflow/feedback defect alongside the model output-budget failure,not evidence of a compiled semantic test failure.\n\n'
  'Static inspection also shows risky primitive use:the output copies logical registers into a separate local array/aliases and ignores scene_shift return values while subsequently reading the logical register array. These observations do not substitute for a machine check;no complete candidate was produced. The next coding workflow should detect truncation before ordinary source checks,require direct logical-register aliases and returned arithmetic results,and use concise bounded sections rather than repeating this full noisy response.\n\n'
  'Original assembly and supplied flag/memory/stack primitives were exposed. Coordinator target C was withheld. This is scaffolded source development,not a held-out benchmark,independent multi-model review or training-quality improvement. The game candidate remains coordinator-authored for this new routine. Native Chat rendering with copied weights is still unverified;the UI tool timed out again without establishing screen state. Headless work remains authorized.\n\n'
  'Exact Author/Repair prompts and raw outputs: '+str(transcript)+'\n')
 facts=dict(status='terminal_two_local_record_generations_truncated_identical_and_unpromoted',directory=str(out),report=str(report),original_run_directory=str(folder),model_identifier=run['model_identifier'],roles=roles,actual_predictions=2,accepted_complete_functions=0,compiled_candidates=0,coordinator_target_body_supplied=False,primitive_scaffolding_supplied=True,duplicate_raw_response=True,new_training=False,optimizer_updates=0,model_source_installed=False,native_Chat_verified=False,development_task=True,held_out_benchmark=False,source_sha256=deps)
 save(out/'review.json',facts);shutil.copy2(report,out/report.name)
 # Retain all exact role files in the moved package; never replay generations.
 for path in [*map(Path,deps),transcript,out/'review.json',out/'run-as-reviewed.json',report,out/report.name]:
  if not path.is_relative_to(ROOT):continue
  dest=P/'workbench'/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists()or sha(dest)!=sha(path):shutil.copy2(path,dest)
 save(V/'local-geometry-records-reviewed-v1-current.json',facts);shutil.copy2(V/'local-geometry-records-reviewed-v1-current.json',P/'workbench/verification/local-geometry-records-reviewed-v1-current.json')
 command='#!/bin/zsh\nset -eu\nBIWN_PACKAGE="$HOME/Desktop/BIWN Portable Lab"\nBIWN_PACKAGE=${BIWN_PACKAGE:A}\nopen -a TextEdit "$BIWN_PACKAGE/workbench/'+str(transcript.relative_to(ROOT))+'"\n'
 for root in [ROOT,P/'workbench']:
  path=root/'BIWN Geometry Agent Results.command';path.write_text(command);path.chmod(0o755)
 print(facts['status'],report,flush=True)
if __name__=='__main__':main()
