"""Publish both verified 120-update plans with bounded timing scope."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    plans={p:json.loads((ROOT/f'verification/startup-elapsed-clock-120-{p}.json').read_text())for p in ['up-left','none']}
    assert all(v['world_returns']==120 and v['startup_full_CPU_states_match']for v in plans.values())
    report=dict(status='CPU_budgeted_startup_120input_control_native_C_match',plans=plans,global_cycle_scheduling_verified=False,whole_game_complete=False,new_training=False,new_unique_game_coverage=False,authorship='Coordinator-authored cost observer/timing adapter; one previously guided local ADDX helper remains. Local review needed one factual correction; same weights are not independent verification.',limits=plans['none']['limits'],installed_launcher_end_to_end_status='pending')
    step_path=ROOT/'verification/startup-single-step-current.json'
    if step_path.exists():
        step=json.loads(step_path.read_text())
        if step['status']=='one_instruction_C_dispatcher_full_startup_and120input_control_match':
            report['single_instruction_dispatcher']={'status':step['status'],'library':step['library'],'report':str(step_path),'per_instruction_host_return':True,'main_boundary_event_candidate_adopted':False}
    experiment_path=ROOT/'verification/startup-boundary-events-experiment-current.json'
    if experiment_path.exists():
        experiment=json.loads(experiment_path.read_text());report['instruction_boundary_experiment']={k:v for k,v in experiment.items()if k!='native_boundary_events'};report['instruction_boundary_experiment']['report']=str(experiment_path)
    p=ROOT/'verification/startup-elapsed-clock-current.json';p.write_text(json.dumps(report,indent=2)+'\n')
    for root in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
        session=json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text());path=Path(session['directory'])/'emulator-runtime/summary.json';j=json.loads(path.read_text());j['CPU_budgeted_startup_runtime_comparison']={**report,'report':str(p)};path.write_text(json.dumps(j,indent=2)+'\n')
    print(p)
if __name__=='__main__':main()
