"""Verify new C instruction dispatcher against retained original120witnesses."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
    baseline=read(ROOT/'verification/startup-elapsed-clock-current.json');runs={}
    for plan in ['up-left','none']:
        n=Path(baseline['plans'][plan]['runs']['native']);c=Path((ROOT/f'runs/startup-single-step-C-120-{plan}.log').read_text().splitlines()[0])
        ns,cs=read(n/'native-startup.json')['startup'],read(c/'C-startup.json')['startup']
        for key in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:assert ns[key]==cs[key],(plan,'startup',key)
        for suffix in ['startup-instruction-PCs.bin','startup-CPU-state-hashes.bin','startup-instruction-costs.bin']:assert(n/('native-'+suffix)).read_bytes()==(c/('C-'+suffix)).read_bytes(),(plan,suffix)
        for suffix in ['world-return-checkpoints.json','JERRY-events.json','music.json','HLE-asset-clock-events.json','startup-elapsed-clock.json']:assert read(n/('native-'+suffix))==read(c/('C-'+suffix)),(plan,suffix)
        nr,cr=read(n/'native.json'),read(c/'C.json')
        for key in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert nr[key]==cr[key],(plan,'world',key)
        assert cr['C_original_CPU_attempts']==0
        assert len(read(c/'C-world-return-checkpoints.json'))==120
        probe=read(c/'C-startup-instruction-probe.json');assert probe['instructions']==2073884
        runs[plan]=dict(native_reference=str(n),C_run=str(c),native_reference_reused=True,startup_instruction_boundaries=probe['instructions'],full_CPU_state_trace_match=True,all_startup_and120world_states_events_match=True,original_CPU_GPU_DSP_forbidden_on_C_side=True)
    j=read(ROOT/'verification/startup-single-step-candidate.json');j.update(status='one_instruction_C_dispatcher_full_startup_and120input_control_match',runs=runs,main_event_candidate_adopted=False,global_cycle_scheduling_verified=False,whole_game_complete=False,limits=['Periodic services still deferred toDDD8; legacy source video IRQ handlers still synchronous in this accepted timing configuration.','Separate real main/JERRY boundary experiment is rejected for345376originalGPU opcode escapes inside video callback. No adoption of that hybrid path.'])
    p=ROOT/'verification/startup-single-step-current.json';p.write_text(json.dumps(j,indent=2)+'\n');Path(j['directory']).joinpath('runtime-verification.json').write_text(json.dumps(j,indent=2)+'\n');print(p)
if __name__=='__main__':main()
