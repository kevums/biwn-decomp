"""Verify sole HLE assets, source IRQ completion and full120return pairs."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];INSTALLED=Path.home()/'.lmstudio/local-ai-lab'
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',type=Path,default=ROOT/'runs');args=parser.parse_args()
    previous=json.loads((ROOT/'verification/fresh-HLE-runtime-current.json').read_text())
    out=ROOT/'verification/HLE-asset-owner-progress'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    manifest={};runs={}
    for plan in ['up-left','none']:
        directories={}
        for mode in ['native','C']:
            log=args.run_root/('HLE-assets-checked120-'+mode+'-'+plan+'.log');directory=Path(log.read_text().splitlines()[0]);directories[mode]=directory
            report=json.loads((directory/'report.json').read_text());assert report['experimental_HLE_asset_owner'] and report['status']=='completed_unpaired_fresh_HLE_side'
            for p in [log,*directory.glob('*.json')]:manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        N,C=directories['native'],directories['C'];ns=json.loads((N/'native-startup.json').read_text());cs=json.loads((C/'C-startup.json').read_text());a,b=ns['startup'],cs['startup']
        for key in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:assert a[key]==b[key],(plan,'startup',key)
        for phase in ['fresh_HLE_entry','live_prefix']:
            left=a['source4000_entry'][phase];right=b['source4000_entry'][phase]
            for key in left:
                if key not in ['mode','source_C_game','native_CPU_instructions']:assert left[key]==right[key],(plan,phase,key)
        assert not a['source4000_entry']['HLE_disabled_after_DD40_for_shared_file_transport']
        nr=json.loads((N/'native.json').read_text());cr=json.loads((C/'C.json').read_text())
        for key in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert nr[key]==cr[key],(plan,'tasks',key)
        for suffix in ['world-return-checkpoints','music','JERRY-events']:
            assert json.loads((N/('native-'+suffix+'.json')).read_text())==json.loads((C/('C-'+suffix+'.json')).read_text()),(plan,suffix)
        nv=json.loads((N/'native-HLE-asset-VBIs.json').read_text());cv=json.loads((C/'C-HLE-asset-VBIs.json').read_text())
        assert len(nv)==len(cv)==12
        for left,right in zip(nv,cv):
            for key in ['CPU','progress','source_completion_VBIs']:assert left[key]==right[key],(plan,'asset sourceVBI',key)
        legacy=json.loads((Path(previous['runs'][plan]['sources']['native'])/'native-startup.json').read_text())['startup']['disc']['requests']
        assets=a['disc']['requests'];assert len(assets)==len(legacy)==12
        for actual,known in zip(assets,legacy):
            for key in ['destination_start','destination_end','bytes','packed_binary_MSF','sha256']:assert actual[key]==known[key],(plan,'known asset payload',key)
            assert not actual['captured_stream_phase_used']
        pn=a['source4000_entry']['live_prefix'];en=a['source4000_entry']['fresh_HLE_entry']
        CPU_windows={'game_loader':en['counts']['CPU_steps'],'game_entry':pn['native_CPU_instructions'],
                     'startup_outer_loop':ns['checks']['native_CPU_steps'],'source_asset_VBI_handlers':sum(v['reference_CPU_steps'] for v in nv),
                     'world_tasks':nr['processor_instructions']}
        music=json.loads((N/'native-music.json').read_text());jerry=json.loads((N/'native-JERRY-events.json').read_text());points=json.loads((N/'native-world-return-checkpoints.json').read_text());assert len(points)==120
        runs[plan]=dict(sources={k:str(v) for k,v in directories.items()},CPU_windows=CPU_windows,total_reference_CPU_steps=sum(CPU_windows.values()),
            total_DSP_instructions=sum(v['instructions'] for v in music['calls'])+sum(v['instructions'] for v in pn['music_calls']),
            asset_reads=12,asset_bytes=sum(v['bytes'] for v in assets),all_asset_payload_hashes_match_prior_source_witness=True,
            asset_HLE_stream_ticks=sum(v['HLE_stream_ticks'] for v in assets),source_completion_VBIs=sum(v['source_completion_VBIs'] for v in nv),
            captured674byte_phase_used=False,direct_RAM_progress_write=False,file_payload_memcpy_adapter=False,
            created_contexts=len(a['contexts']),world_returns=120,final_X=points[-1]['player']['0x49c50'],final_Z=points[-1]['player']['0x49c56'],
            SSI_callbacks=sum([1,1] in v['IRQs'] for v in jerry['events']),timer1_DSP_IRQ2_callbacks=sum([2,1] in v['IRQs'] for v in jerry['events']),
            all_recorded_PCM_pairs_silent=all(v['PCM']==[0,0] for v in jerry['events']),all_checked_states_traces_and_events_equal=True)
    report=dict(status='sole_HLE_disc_asset_stream_source_VBI_completion_120world_input_control_native_C_match',directory=str(out),runs=runs,
        initial_saved_machine_state_loaded=False,HLE_services_retained_after_DD40=True,coherent_single_asset_transport_owner=True,
        new_training=False,new_local_model_C_authorship=False,whole_game_complete=False,global_cycle_scheduling_verified=False,
        limits=['Platform HLE loads the boot stub and scans/streams sectors from the preserved CDI. Native firmware authentication and its full device behavior remain bypassed.',
                'HLE ticks are pumped synchronously at source task handoffs. Two supplied source VBI events per asset handle the deferred first poll and actual completion; their CPU instruction counts are separately included in reference totals. This is not globally coupled drive/video/processor timing.',
                'Later world-to-JERRY16666.6667us slices, opt-inSSI/IRQ ownership, synchronousGPU/blitter and held main/video/OP scheduling remain. Recorded PCM silent; remaining game code/scenes, physical controllers/scanout and a playable reconstructed C app unfinished.'],
        next_action='Interleave CD transfer and source video/processor events over a common time base instead of synchronous completion at each handoff; keep current payload/state regression and training/UI gates.')
    save(out/'report.json',report);save(ROOT/'verification/HLE-asset-owner-current.json',report)
    compact={**report,'report':str(out/'report.json')};compact.pop('directory')
    for base in [ROOT,INSTALLED]:
        session=json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text());p=Path(session['directory'])/'emulator-runtime/summary.json';x=json.loads(p.read_text());x['sole_HLE_asset_runtime_comparison']=compact;save(p,x)
    for name in ['biwn_HLE_asset_owner.py','check_biwn_entry_natural_task_rounds.py','record_biwn_HLE_asset_progress.py']:
        p=ROOT/'scripts'/name;manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    save(out/'input-manifest.json',manifest)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR TASK\nKeep platform HLE as the sole asset transport afterDD40. Read actual disc sectors/sentinel data without captured674byte alignment, and report completion through actual sourceVBI, never directbd848 write. Compare all120input/control native/C states and known12asset byte hashes; retain supplied scheduling limits.\n\n'+json.dumps(report,indent=2)+'\n')
    print(out,flush=True)

if __name__=='__main__':main()
