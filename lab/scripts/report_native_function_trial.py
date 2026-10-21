"""Publish the exact finite training/evaluation result and readable raw transcripts."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 dataset=read(ROOT/'verification/native-function-curriculum-current.json');data=Path(dataset['directory'])
 train=read(ROOT/'verification/native-function-training-current.json')
 jobs=sorted((data/'jobs').glob('*'));job=jobs[-1];training=read(job/'training-result.json')
 memory=[json.loads(x)for x in (job/'training-memory.jsonl').read_text().splitlines()]if(job/'training-memory.jsonl').exists()else[]
 batches=[json.loads(x)for x in (job/'training-batches.jsonl').read_text().splitlines()]
 lengths=read(data/'token-preflight.json');allowed={(v['prompt_tokens'],v['tokens'])for v in lengths if v['split']in ['train','valid']}
 assert all(tuple(b['lengths'][0])in allowed for b in batches),'Unrecognized/truncated token batch'
 report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),dataset=str(data),dataset_sha256=sha(data/'reviewed-source-examples.jsonl'),training_job=str(job),training_status=training['status'],completed_updates=max((x['iteration']for x in memory),default=0),maximum_MLX_peak_GB=max((x['peak_memory']for x in memory),default=None),batch_records=len(batches),all_observed_full_lengths_match=True,phases={},default_promoted=False,goal_complete=False)
 lines=['BIWN LOCAL MODEL TRAINING TRIAL','',
  'Roles: Codex coordinator freezes proof-linked examples and runs deterministic execution gates. Local27B Author generates each raw C draft independently. Adapter Author uses the same base plus the trial LoRA. No independent Reviewer model or native LM Studio Chat verification is claimed.','',
  'Data:7complete training units,1scheduler validation unit,3resource-family test units. Resource targets never enter this trial’s training/validation. Prior prompts and source development exposed these functions; this is an adaptive development holdout. Task creation and scheduler share scheduling concepts across train/validation. Shared ABI/helper contracts remain.','',
  f"Training:32planned updates,{train.get('num_layers',2)}LoRA layers,rank8,learning rate1e-5,full8960context,128token checkpointed suffix-head chunks,512MiB free-cache cap,eager execution. Fresh locked27B6bit base; no previous failed adapter is resumed.",
  f"Training state:{training['status']}; completed updates:{report['completed_updates']}; maximum recorded MLX peak:{report['maximum_MLX_peak_GB']}GB.",
  f"Observed batches:{len(batches)}; all exact prepared token lengths retained.",'',
  'Scoring:identical frozen system/user prompts; thinking off,temperature0,max5000output tokens. A single complete outer C fence may be removed; generated code is otherwise unchanged. Strict compilation and existing full original-CPU/public-RAM/helper/ordered-access gates decide acceptance. A timeout/nonreturn/compile error is a failure. CPU proofs remain scoped; no whole-game or physical-console claim.','']
 transcript=['EXACT LOCAL AUTHOR PROMPTS AND RESPONSES','']
 if train.get('recovery_from'):
  report['recovery_from']=train['recovery_from'];lines+=['Recovery:two-layer run failed with Metal Insufficient Memory before its first update. Fresh one-layer retry keeps complete examples and identical evaluation; no optimizer resume.',f"Failed job:{train['recovery_from']}",'']
 for phase in ['base','adapter']:
  pointer=ROOT/'verification'/f'native-function-{phase}-evaluation-current.json'
  if not pointer.exists():continue
  evaluation=read(pointer)
  if evaluation['dataset']!=str(data):continue
  report['phases'][phase]={k:evaluation.get(k)for k in ['status','passed','total','results','directory','daily_model_restored','accepted_pointers_unchanged','adapter_sha256']}
  lines.append(f"{phase.upper()}: {evaluation.get('passed','pending')}/{evaluation.get('total',3)} complete code gates; state:{evaluation['status']}.")
  for result in evaluation['results']:
   folder=Path(evaluation['directory'])/result['function'];receipt=read(folder/'result.json')
   lines.append(f"  {result['function']}: {'PASS'if result['verified']else'FAIL'}, {result['seconds']:.2f}s, {result['generation_tokens']}tokens, finish:{result['finish_reason']}. Gate log:{folder/'check.log'}")
   transcript.extend([f"{phase.upper()} / {result['function']}", 'PROMPT:',json.dumps(read(folder/'prompt.json'),ensure_ascii=False,indent=2),'RESPONSE:',(folder/'response.txt').read_text(),'GATE RESULT:',json.dumps({k:v for k,v in receipt.items()if k!='response'},indent=2),''])
  lines.append('')
 report['fresh_phases']={}
 for phase in ['base','adapter']:
  pointer=ROOT/'verification'/f'native-function-fresh-{phase}-evaluation-current.json'
  if not pointer.exists():continue
  evaluation=read(pointer)
  if evaluation['dataset']!=str(data):continue
  report['fresh_phases'][phase]={k:evaluation.get(k)for k in ['status','passed','total','results','directory','daily_model_restored','accepted_pointers_unchanged','adapter_sha256','case_file_sha256']}
  lines.append(f"FRESH FORMATTING / {phase.upper()}: {evaluation.get('passed','pending')}/{evaluation.get('total',1)} complete code gates; state:{evaluation['status']}.")
  for result in evaluation['results']:
   folder=Path(evaluation['directory'])/result['function']
   lines.append(f"  {result['function']}: {'PASS'if result['verified']else'FAIL'}, {result['seconds']:.2f}s, {result['generation_tokens']}tokens. Gate log:{folder/'check.log'}")
   transcript.extend([f"FRESH FORMATTING / {phase.upper()}",'PROMPT:',json.dumps(read(folder/'prompt.json'),ensure_ascii=False,indent=2),'RESPONSE:',(folder/'response.txt').read_text(),'GATE RESULT:',json.dumps({k:v for k,v in read(folder/'result.json').items()if k!='response'},indent=2),''])
  lines.append('')
 controls=ROOT/'verification/native-curriculum-positive-controls/proof.json'
 if controls.exists():report['positive_controls']=str(controls);report['positive_controls_sha256']=sha(controls)
 fresh_proof=ROOT/'verification/native-format-pad-publication-current.json'
 if fresh_proof.exists():
  report['fresh_reference_proof']=str(fresh_proof);report['fresh_reference_proof_sha256']=sha(fresh_proof)
  lines+=['Fresh formatting reference:1668native CPU/RAM cases,1668stable ordered-access cases,16changing-read traces,all27originalinstructionlocations. Three deliberate X/character-offset/signedness defects rejected after compilation. This coordinator reference is outside gradients and disc integration.','']
  lines += [f"Fresh standalone C source:{ROOT/'projects/black-ice-white-noise/restoration/native-m68k/format-pad-reference.c'}",'']
 resolved_pointer=ROOT/'verification/native-function-header-resolved-current.json'
 if resolved_pointer.exists():
  resolved=read(resolved_pointer)
  if resolved['dataset']==str(data):
   report['header_resolution']=dict(proof=str(resolved_pointer),proof_sha256=sha(resolved_pointer),scores=resolved['scores'],scope=resolved['scope'])
   lines+=['Build-boundary audit:these frozen prompts supplied header contents but omitted explicit filenames. Future dataset preparation now labels exact filenames; current frozen training/evaluation messages were unchanged. A supplemental check maps quoted basename-only includes to the sole supplied byte-identical ABI header; it also supplies conventional filename/guard aliases. Generated C bytes and full compilation/CPU/RAM/access gates remain unchanged. Raw scores are retained.']
   for suite,phases in resolved['scores'].items():
    lines.append(f"  Header-resolved {suite}: "+'; '.join(f"{p} {v['passed']}/{v['total']}"for p,v in phases.items()))
   lines+=['']
 complete=all(report['phases'].get(p,{}).get('status')=='terminal_code_evaluation'and report['fresh_phases'].get(p,{}).get('status')=='terminal_code_evaluation'for p in ['base','adapter'])
 report['status']='terminal_native_function_training_comparison'if complete else'native_function_trial_in_progress'
 if complete:
  base=report['phases']['base']['passed'];adapter=report['phases']['adapter']['passed']
  report['decision']='unpromoted_development_trial';report['code_gate_change']=adapter-base
  fresh_pointer=ROOT/'verification/native-function-fresh-case-current.json';fresh=read(fresh_pointer);fresh.update(status='terminal_fresh_format_pad_base_adapter_evaluated',local_model_used=True,training_used=False,evaluation=report['fresh_phases']);fresh_pointer.write_text(json.dumps(fresh,indent=2)+'\n')
  lines+=['Decision:trial remains unpromoted. No generated-code acceptance gain was demonstrated on either test group, including after header resolution. A lower training loss and shorter outputs do not establish correctness. Next work should ground stack/operand/register effects and compiler/CPU feedback in the author workflow, rather than repeat this small-corpus run on loss alone.','']
 lines += ['The checked native28 scan-kernel disc, running P/O previews and daily model configuration are separate artifacts. This trial does not replace them.','',f'Data and all training prompts/targets:{data}',f'Full raw evaluation transcripts:{ROOT/"reports/native-function-trial-prompts.txt"}',f'Current machine-readable result:{ROOT/"verification/native-function-trial-reviewed-current.json"}']
 (ROOT/'reports/native-function-trial.txt').write_text('\n'.join(lines)+'\n');(ROOT/'reports/native-function-trial-prompts.txt').write_text('\n'.join(transcript)+'\n')
 report['report']=str(ROOT/'reports/native-function-trial.txt');report['report_sha256']=sha(report['report']);report['transcript']=str(ROOT/'reports/native-function-trial-prompts.txt');report['transcript_sha256']=sha(report['transcript'])
 (ROOT/'verification/native-function-trial-reviewed-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','completed_updates','maximum_MLX_peak_GB','report']}),flush=True)
if __name__=='__main__':main()
