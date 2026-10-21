"""Compare isolated CPU-budgeted startup candidates; never promote the launcher."""
import argparse,collections,hashlib,json,struct
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',type=Path,default=ROOT/'runs');parser.add_argument('--log-prefix',default='startup-elapsed-clock');parser.add_argument('--rounds',type=int,default=3);parser.add_argument('--input-plan',default='none');args=parser.parse_args()
    dirs={m:Path((args.run_root/f'{args.log_prefix}-{m}.log').read_text().splitlines()[0])for m in ['native','C']}
    snapshots={m:read(d/(m+'-startup.json'))['startup']for m,d in dirs.items()}
    for key in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:
        assert snapshots['native'][key]==snapshots['C'][key],('startup',key)
    for suffix in ['startup-instruction-PCs.bin','startup-CPU-state-hashes.bin','startup-instruction-costs.bin']:
        assert (dirs['native']/('native-'+suffix)).read_bytes()==(dirs['C']/('C-'+suffix)).read_bytes(),suffix
    for suffix in ['startup-elapsed-clock.json','HLE-asset-clock-events.json','JERRY-events.json','music.json','world-return-checkpoints.json']:
        assert read(dirs['native']/('native-'+suffix))==read(dirs['C']/('C-'+suffix)),suffix
    costs=list(struct.iter_unpack('>II',(dirs['native']/'native-startup-instruction-costs.bin').read_bytes()))
    actual=[v[0]for v in struct.iter_unpack('>I',(dirs['native']/'native-startup-original-cycle-costs.bin').read_bytes())]
    clock=read(dirs['native']/'native-startup-elapsed-clock.json')
    assert len(costs)==len(actual)
    delta=collections.Counter((pc,a-b)for(pc,b),a in zip(costs,actual)if a!=b)
    assert delta=={(0xe7d4,56):clock['IRQ_entries']},delta
    assert sum(actual)==clock['CPU_cycles']
    assert clock['service_pulses']<clock['system_task_visits']
    for event in clock['events']:
        assert event['service_time_us']<=event['elapsed_us']
    assert len(snapshots['C']['disc']['requests'])==12
    assert sum(x['bytes']for x in snapshots['C']['disc']['requests'])==758846
    accepted=read(ROOT/'verification/atomic-startup-current.json')
    old=read(Path(accepted['runs'][args.input_plan]['sources']['native'])/'native-startup.json')['startup']['disc']['requests']
    for asset,witness in zip(snapshots['C']['disc']['requests'],old):
        for key in ['destination_start','destination_end','bytes','packed_binary_MSF','sha256']:assert asset[key]==witness[key],('prior asset witness',key)
    points=read(dirs['C']/'C-world-return-checkpoints.json');assert len(points)==args.rounds
    nr,cr=read(dirs['native']/'native.json'),read(dirs['C']/'C.json')
    for key in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert nr[key]==cr[key],('world',key)
    assert cr['C_original_CPU_attempts']==0
    jerry=read(dirs['C']/'C-JERRY-events.json')
    assert all(v['PCM']==[0,0]for v in jerry['events'])
    report=dict(status='CPU_budgeted_startup_native_C_match',input_plan=args.input_plan,recorded_at=datetime.now(timezone.utc).isoformat(),runs={m:str(d)for m,d in dirs.items()},instructions=len(costs),CPU_cycles=sum(actual),elapsed_clock={k:v for k,v in clock.items()if k!='events'},world_returns=len(points),startup_full_CPU_states_match=True,assets=12,asset_bytes=758846,source_hashes={n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest()for n in ['biwn_startup_elapsed_clock.py','biwn_startup_instruction_probe.py','check_biwn_entry_natural_task_rounds.py','check_biwn_entry_scheduled_startup.py']},global_cycle_scheduling_verified=False,launcher_promoted=False,limits=['Candidate uses periodic service adapter at DDD8 safe points; delivery is not at every CPU instruction boundary. Main video queue remains held, GPU/DSP helpers synchronous, later world slices supplied.','Pinned emulator IRQ entry56 cycles has accuracy FIXME. Silent audio, HLE authentication bypass, uncovered game paths and standalone application remain unfinished.','This report covers only the specified input plan and number of world returns; other scenes and paths are unverified.'])
    p=ROOT/('verification/startup-elapsed-clock-candidate.json'if args.rounds==3 else 'verification/startup-elapsed-clock-120-'+args.input_plan+'.json');p.write_text(json.dumps(report,indent=2)+'\n');print(p)
if __name__=='__main__':main()
