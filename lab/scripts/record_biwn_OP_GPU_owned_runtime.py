"""Strict fresh original/C paired proof; no global/playability claim."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,collections,struct
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',type=Path);args=parser.parse_args();folder=args.run_root or Path(read(ROOT/'runs/OP-GPU-owned-full-pointer.json')['directory']);cmds=read(folder/'commands.json');assert len(cmds)==4 and all(v['exit_code']==0 for v in cmds);runs={}
    old=read(ROOT/'verification/startup-elapsed-clock-current.json')
    for plan in ['up-left','none']:
        ds={mode:Path((folder/f'OP-GPU-{mode}-{plan}.log').read_text().splitlines()[0])for mode in ['native','C']};n,c=ds['native'],ds['C'];a,b=read(n/'native-startup.json')['startup'],read(c/'C-startup.json')['startup']
        for k in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:assert a[k]==b[k],(plan,'startup',k)
        for suffix in ['startup-instruction-PCs.bin','startup-CPU-state-hashes.bin','startup-instruction-costs.bin']:assert(n/('native-'+suffix)).read_bytes()==(c/('C-'+suffix)).read_bytes(),(plan,suffix)
        for suffix in ['startup-boundary-events.json','world-return-checkpoints.json','JERRY-events.json','music.json']:assert read(n/('native-'+suffix))==read(c/('C-'+suffix)),(plan,suffix)
        nr,cr=read(n/'native.json'),read(c/'C.json')
        for k in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert nr[k]==cr[k],(plan,'world',k)
        assert cr['C_original_CPU_attempts']==0
        points=read(c/'C-world-return-checkpoints.json');assert len(points)==120
        costs=list(struct.iter_unpack('>II',(n/'native-startup-instruction-costs.bin').read_bytes()));actual=[v[0]for v in struct.iter_unpack('>I',(n/'native-startup-original-cycle-costs.bin').read_bytes())];assert len(costs)==len(actual)
        deltas=collections.Counter((pc,v-pred)for(pc,pred),v in zip(costs,actual)if v!=pred);assert all(pc==0xe7d4 and delta==56 for pc,delta in deltas)
        clock=read(c/'C-startup-boundary-events.json');assert clock['CPU_cycles']==sum(actual)and clock['instruction_boundary_event_delivery']
        assets=b['disc']['requests'];witness=read(Path(old['plans'][plan]['runs']['native'])/'native-startup.json')['startup']['disc']['requests'];assert len(assets)==len(witness)==12
        for asset,expected in zip(assets,witness):
            for k in ['destination_start','destination_end','bytes','packed_binary_MSF','sha256']:assert asset[k]==expected[k],(plan,'asset',k)
        owner=read(c/'C-OP-GPU-owner.json');assert owner['calls']==21586 and owner['original_GPU_opcodes_on_C_side']==0 and not owner['captured_GPU_or_RAM_loaded_into_live_game']
        jerry=read(c/'C-JERRY-events.json');silent=all(v['PCM']==[0,0]for v in jerry['events'])
        runs[plan]=dict(sources={m:str(d)for m,d in ds.items()},CPU_instruction_boundaries=len(costs),CPU_cycles=sum(actual),CPU_IRQ_entries=sum(deltas.values()),elapsed_us=clock['elapsed_us'],main_events=clock['main_events'],JERRY_startup_events=clock['JERRY_events'],GPU_timer_handlers=len(clock['GPU_timers']),OP_GPU_source_slices=owner['calls'],OP_GPU_source_instructions=owner['source_instructions'],original_GPU_CPU_DSP_opcodes_forbidden_on_C_side=True,assets=12,asset_bytes=sum(v['bytes']for v in assets),world_returns=120,all_full_CPU_RAM_GPU_DSP_event_and_world_states_match=True,all_recorded_PCM_pairs_silent=silent,final_player=points[-1]['player'])
    out=ROOT/'verification/OP-GPU-owned-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);core=read(ROOT/'verification/BIWN-OP-GPU-owner-candidate.json');assert core['suite_exit_code']==core['lint_exit_code']==0
    report=dict(status='instruction_boundary_main_JERRY_and_C_owned_OP_GPU_120input_control_match',directory=str(out),run_root=str(folder),runs=runs,event_core=core['core_path'],CPU_library=read(ROOT/'verification/startup-single-step-current.json')['library'],OP_GPU_library=read(ROOT/'verification/OP-GPU-slice-candidate.json')['library'],core_default_NULL_suite_exit0=True,instruction_boundary_event_delivery=True,global_cycle_scheduling_verified=False,whole_game_complete=False,new_training=False,coordinator_authored=True,limits=['CPU costs drive main and JERRY queues during startup; source OP GPU slices now C-owned. GPU/DSP/blitter still synchronous and later world time slices supplied; no global/cross-processor/physical timing proof.','Logical GPU4396bytes and shared hardware/RAM verified;20bytes of decoder scratch are retained, not reconstructed or claimed equivalent. Current GPU pipeline/DRAM timing profile only.','Boot uses HLE firmware/authentication bypass. Recorded PCM silence, uncovered game paths, physical controls/scanout and standalone playable application remain unfinished.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/OP-GPU-owned-runtime-current.json').write_text(json.dumps(report,indent=2)+'\n')
    manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [folder/'commands.json',*[ROOT/'scripts'/n for n in ['biwn_OP_GPU_owner.py','biwn_startup_boundary_events.py','generate_biwn_OP_GPU_slice.py','biwn_startup_single_step.py','check_biwn_entry_scheduled_startup.py','biwn_startup_instruction_probe.py','check_biwn_entry_natural_task_rounds.py']]]};(out/'input-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(out)
if __name__=='__main__':main()
