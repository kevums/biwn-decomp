"""Read local workbench progress without loading a model or waiting on its lock."""
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def process(pid,expected):
    if not pid:return False
    result=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
    return result.returncode==0 and expected in result.stdout
def main():
    print('LOCAL AI LAB — TRAINING STATUS\n')
    pointer=ROOT/'verification/native-repair-training-current.json'
    if not pointer.exists():print('No native repair trial is recorded.');return
    state=read(pointer);print('Trial phase:',state['status']);print('Launcher process:', 'live'if process(state.get('pid'),'run_native_repair_training.py')else'not running')
    data=Path(state['data']);jobs=sorted((data/'jobs').glob('*'))if(data/'jobs').exists()else[]
    if jobs:
        job=Path(state['job'])if state.get('job')else jobs[-1];result=read(job/'training-result.json');live=process(result.get('pid'),'mlx_lora_reasoning_off.py')
        print('Training worker:', 'live'if live else result['status']);reports=[]
        p=job/'training-memory.jsonl'
        if p.exists():
            for line in p.read_text().splitlines():
                try:reports.append(json.loads(line))
                except ValueError:pass
        if reports:
            last=reports[-1];print(f"Completed updates: {last['iteration']} / 64");print(f"Latest training loss: {last['train_loss']:.4f}");print(f"Peak MLX memory: {max(row['peak_memory']for row in reports):.2f} GB")
        print('Training log:',job/'training.log')
        selection=job/'checkpoint-selection.json'
        if selection.exists():
            value=read(selection)
            if value.get('source')=='Actual checkpoint rescoring, not pre-update trainer log labels':print('Validation-selected saved checkpoint:',value['selected_step'])
            else:print('Checkpoint selection: preliminary; actual saved checkpoints will be rescored before resource tests.')
    control=ROOT/'verification/native-repair-base-evaluation-current.json'
    if control.exists():
        value=read(control);print('Original-task base resource functions passing:',sum(row['verified']for row in value['results']),'/',len(value['results']))
    adapter=ROOT/'verification/native-repair-adapter-evaluation-current.json'
    if adapter.exists():
        value=read(adapter);print('Original-task adapter resource functions passing:',sum(row['verified']for row in value['results']),'/',len(value['results']))
    clarified=ROOT/'verification/native-build-contract-evaluation-current.json'
    if clarified.exists():
        value=read(clarified)
        print('Original-task limitation: supplied header text omitted its filenames; preserve the build failures with that qualification.')
        print('Clarified same-task comparison:',value['status'])
        print('Comparison launcher:', 'live'if process(value.get('pid'),'run_native_build_contract_followup.py')else'not running')
        for phase in ['base','adapter']:
            rows=[row for row in value.get('results',[])if row.get('phase')==phase]
            if rows:print(phase.title(),'clarified results:',sum(bool(row.get('verified'))for row in rows),'/',len(rows))
        print('Clarified prompts and outputs:',value['directory'])
    feedback=ROOT/'verification/native-resource-feedback-team-current.json'
    if feedback.exists():
        value=read(feedback);print('\nLocal Reviewer → Restorer workflow:',value['status'])
        print('Workflow process:', 'live'if process(value.get('pid'),'run_native_resource_feedback_team.py')else'not running')
        if value.get('current_role'):print('Current role:',value['current_role'])
        for phase in ['base','adapter']:
            rows=[row for row in value.get('results',[])if row['phase']==phase]
            if rows:print(phase.title(),'feedback-assisted native passes:',sum(row['verified']for row in rows),'/',len(rows),'completed cases')
        print('Workflow prompts and raw responses:',value['directory'])
        print('Same-model roles run sequentially; adaptive repairs do not replace the original single-pass score.')
        reviewed=ROOT/'verification/native-resource-feedback-team-reviewed-current.json'
        if reviewed.exists():print('Workflow review:',read(reviewed)['status'],'— incomplete study; no six-case score')
    print('Promotion: experimental; generated C must pass native checks.')
    print('Exact control/evaluation prompts and outputs are under:',data)
    game=ROOT/'verification/external-DSP-combined-route-current.json'
    if game.exists():
        value=read(game);alive=process(value.get('child_pid'),str(Path(value['directory'])/'probe.py'));print('\nBIWN combined route:', 'live'if alive else value['status'])
        log=Path(value['directory'])/'C.log'
        if log.exists():
            for line in reversed(log.read_text().splitlines()):
                try:row=json.loads(line)
                except ValueError:continue
                if isinstance(row,dict)and'frame'in row and'CPU_full'in row:print('Last logged game frame:',row['frame']);break
    print('\nTraining temporarily unloads the daily Chat model. The trial launcher restores it automatically.')

if __name__=='__main__':main()
