"""Publish the completed pilot's actual code outcomes without replacing its evidence."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
    v=ROOT/'verification';training=json.loads((v/'game-geometry-training-v4-current.json').read_text())
    assert training['status']=='terminal_game_geometry_v4_training_and_evaluation_pending_review'and training['daily_model_restored']
    job=Path(training['job']);selection=json.loads((job/'checkpoint-selection.json').read_text())
    out=v/'game-geometry-training-reviewed-v4'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    results={};inputs=[Path(__file__),v/'game-geometry-training-v4-current.json',job/'checkpoint-selection.json',job/'training-result.json',job/'selected-adapter/adapters.safetensors']
    for phase in ['base','adapter']:
        pointer=v/f'game-geometry-v4-{phase}-evaluation-current.json';state=json.loads(pointer.read_text())
        assert state['status']=='terminal_code_evaluation'and len(state['results'])==4
        assert state['daily_model_restored']and not state['default_promoted']
        folder=Path(state['directory']);shutil.copy2(pointer,out/(phase+'-evaluation.json'));inputs.append(pointer)
        cases=[]
        for row in state['results']:
            at=folder/row['function'];result=json.loads((at/'result.json').read_text());log=(at/'check.log').read_text()
            source=next(p for p in at.glob('*.c')if p.name!='plane-checker-as-run.py')
            assert sha(source)==row['candidate_sha256']
            assert result['verified']==row['verified']
            classification=('output_truncated_and_compile_failed'if row['finish_reason']=='length'else
                            'header_filename_compile_failure'if 'No such file or directory'in log or 'file not found'in log else
                            'compiler_failure'if 'error:'in log else 'execution_or_CPU_RAM_contract_failure')
            cases.append(dict(function=row['function'],verified=row['verified'],classification=classification,
                              prompt=str(at/'prompt.json'),response=str(at/'response.txt'),candidate=str(source),check_log=str(at/'check.log')))
            inputs.extend([source,at/'prompt.json',at/'response.txt',at/'result.json',at/'check.log'])
        results[phase]=dict(passed=sum(x['verified']for x in state['results']),total=4,cases=cases)
    assert selection['adapter_sha256']==sha(job/'selected-adapter/adapters.safetensors')
    report=ROOT/'reports/Game Geometry Training v4 Review.txt'
    report.write_text('GAME GEOMETRY MODEL PILOT — NOT ADOPTED\n\n'
        'The 64-update pilot completed. Actual saved-checkpoint validation chose step '+str(selection['selected_step'])+
        ', with validation loss '+str(selection['validation_loss'])+'. The base model passed 0/4 code tests; the selected adapter passed 0/4. No adapter or generated routine was promoted.\n\n'
        'The three adapter resource routines guessed underscore-style header filenames; supplied headers used hyphens. Their code never reached the semantic CPU/RAM gates. The prompts contained header contents but omitted filenames. Both plane-layout outputs reached the 5,000-token limit and failed compilation. Base resource release reached a CPU/RAM mismatch, acquire failed compiler checks, and load failed to return.\n\n'
        'These results establish that these outputs were unusable unchanged in this workflow. They do not establish that every adapter algorithm would fail if the filename ambiguity were removed. Source review also found visible algorithm/register/flag defects in the adapter release output; no hand edits have been applied to the model output or counted as a model pass.\n\n'
        'The separate filename-clarified diagnostic freezes identical base/adapter prompts before generation, retains the already selected weights, and uses the same full acceptance gates. It is an adaptive follow-up after looking at failures, not a new untouched holdout. The original benchmark and checkpoint selection remain preserved.\n\n'
        'Training used 17 examples, one scheduler validation example, and four development code tasks. The three resource tasks have prior project exposure. The plane-layout target was excluded from gradients and checkpoint selection, but shares ABI primitives and project concepts. No broad independent reliability or game-decompilation claim follows from this pilot.\n\n'
        'Prompts/responses: Model Prompts and Responses.command. Current diagnostic progress: Game Model Training Progress.command. The BIWN game preview runs independently.\n')
    inputs.append(report)
    state=dict(status='terminal_game_geometry_training_reviewed_unpromoted',directory=str(out),report=str(report),
        training_completed_updates=64,selected_step=selection['selected_step'],validation_loss=selection['validation_loss'],results=results,
        default_promoted=False,new_training=False,new_inference=False,whole_objective_complete=False,
        diagnostic='game-header-diagnostic-v1-current.json',source_sha256={str(p):sha(p)for p in inputs})
    save(out/'review.json',state);save(v/'game-geometry-training-reviewed-v4-current.json',state);print(out,flush=True)
if __name__=='__main__':main()
