"""Pair isolated fresh boot/startup/task runs; reject unpaired proof claims."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
INSTALLED=Path.home()/'.lmstudio/local-ai-lab'


def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',type=Path,default=ROOT/'runs');args=parser.parse_args()
    out=ROOT/'verification/fresh-HLE-runtime-progress'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    manifest={};runs={};sources={}
    for plan in ['up-left','none']:
        directories={}
        for mode in ['native','C']:
            log=args.run_root/('fresh-HLE-120-'+mode+'-'+plan+'.log')
            directory=Path(log.read_text().splitlines()[0]);directories[mode]=directory
            report=json.loads((directory/'report.json').read_text())
            assert report['status']=='completed_unpaired_fresh_HLE_side'
            assert report['fresh_HLE'] and not report['initial_capture_loaded']
            for p in [log,*directory.glob('*.json')]:manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        N,C=directories['native'],directories['C'];sources[plan]={mode:str(d) for mode,d in directories.items()}
        ns=json.loads((N/'native-startup.json').read_text());cs=json.loads((C/'C-startup.json').read_text());a,b=ns['startup'],cs['startup']
        for k in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:assert a[k]==b[k],(plan,'startup',k)
        en=a['source4000_entry']['fresh_HLE_entry'];ec=b['source4000_entry']['fresh_HLE_entry']
        for k in en:
            if k not in ['mode','source_C_game']:assert en[k]==ec[k],(plan,'entry',k)
        pn=a['source4000_entry']['live_prefix'];pc=b['source4000_entry']['live_prefix']
        for k in pn:
            if k!='native_CPU_instructions':assert pn[k]==pc[k],(plan,'prefix',k)
        nr=json.loads((N/'native.json').read_text());cr=json.loads((C/'C.json').read_text())
        for k in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert nr[k]==cr[k],(plan,'tasks',k)
        for suffix in ['world-return-checkpoints','music','JERRY-events']:
            assert json.loads((N/('native-'+suffix+'.json')).read_text())==json.loads((C/('C-'+suffix+'.json')).read_text()),(plan,suffix)
        points=json.loads((N/'native-world-return-checkpoints.json').read_text());assert len(points)==120
        music=json.loads((N/'native-music.json').read_text());jerry=json.loads((N/'native-JERRY-events.json').read_text())
        total_DSP=sum(call['instructions'] for call in music['calls'])+sum(call['instructions'] for call in pn['music_calls'])
        CPU_windows={'game_loader':en['counts']['CPU_steps'],'game_entry':pn['native_CPU_instructions'],
                     'startup':ns['checks']['native_CPU_steps'],'world_tasks':nr['processor_instructions']}
        runs[plan]=dict(sources=sources[plan],CPU_windows=CPU_windows,total_reference_CPU_steps=sum(CPU_windows.values()),
            loader_HLE_vector_RTS=en['counts']['HLE_RTS'],loader_main_callbacks=en['counts']['main_events'],
            total_DSP_instructions=total_DSP,DSP_bootstrap_instructions=sum(call['instructions'] for call in pn['music_calls']),
            world_returns=120,final_X=points[-1]['player']['0x49c50'],final_Z=points[-1]['player']['0x49c56'],
            checked_CPU_RAM_hardware_contexts_GPU_requests_and_event_timelines_equal=True,
            asset_reads=len(a['disc']['requests']),asset_bytes=sum(row['bytes'] for row in a['disc']['requests']),
            created_contexts=len(a['contexts']),JERRY_elapsed_us=jerry['elapsed_us'],JERRY_callbacks=len(jerry['events']),
            SSI_callbacks=sum([1,1] in event['IRQs'] for event in jerry['events']),
            timer1_DSP_IRQ2_callbacks=sum([2,1] in event['IRQs'] for event in jerry['events']),
            all_recorded_PCM_pairs_silent=all(event['PCM']==[0,0] for event in jerry['events']),
            source_C_original_CPU_attempts=cr['C_original_CPU_attempts'])
    np=json.loads((Path(sources['up-left']['native'])/'native-world-return-checkpoints.json').read_text())
    cp=json.loads((Path(sources['none']['native'])/'native-world-return-checkpoints.json').read_text())
    divergence=next(i+1 for i,(a,b) in enumerate(zip(np,cp)) if a!=b)
    # Retain code generator mappings as static evidence, not loaded machine inputs.
    report=dict(status='fresh_disc_HLE_loader_entry_startup_120world_input_control_native_C_match',directory=str(out),
        runs=runs,input_control_first_divergent_world_return=divergence,
        initial_saved_RAM_CPU_GPU_DSP_state_loaded=False,intermediate_machine_state_reload=False,
        whole_game_complete=False,global_cycle_scheduling_verified=False,native_firmware_boot_verified=False,
        new_training=False,new_local_model_C_authorship=False,
        limits=[
            'Platform HLE extracts/loads the boot stub directly from the preserved CDI, initializes its BIOS API/TOC/CPU context and supplies CD stream services throughDD40. This bypasses firmware authentication; no separately supplied extracted boot/stage payload or saved initial machine state is loaded.',
            'HLE API bridge temporarily exposes C-owned CPU registers to the existing native platform ABI, restores its shadow and executes no original CPU opcodes. C path originalGPU/DSP opcode counters are guarded; shared peripheral/blitter implementation remains.',
            'AtDD40 HLE dispatch is explicitly disabled on both sides to avoid double-driving the file-backed asset adapter. Source startup/task code then uses the existing file-backed BIOS303C/3042 adapter and captured674byte stream phase; this is not full live HLE CD timing throughout the run.',
            'Four main-event callbacks at loader GPU startup and one at each source CD poll; later16666.6667us world-to-JERRY slices, opt-in singleSSI-chain/IRQ ownership hooks and synchronousGPU/blitter services remain. Later main/video/OP/CD scheduling is held. Initial snapshots are read only for static source code mappings.',
            'Bounded emulated player displacement, not every scene/branch, physical controllers/scanout, playable reconstructed C application or source music proof. Earlier fresh original-emulator HLE game test remains separate.'],
        next_action='Replace the postDD40 file-backed CD handoff with one coherent disc-service owner and coordinate processor/video/CD timing; extend missing game branches/audio and native LM Studio Chat/adapter accuracy gates.')
    save(out/'report.json',report);save(ROOT/'verification/fresh-HLE-runtime-current.json',report)
    for p in [ROOT/'scripts'/n for n in ['biwn_fresh_HLE_entry.py','biwn_fresh_HLE_prefix.py','biwn_fresh_HLE_platform.py','biwn_live_source_prefix.py','probe_biwn_fresh_CD_boot.py','check_biwn_entry_natural_task_rounds.py','record_biwn_fresh_HLE_runtime.py']]:manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    save(out/'input-manifest.json',manifest)
    compact=dict(report=str(out/'report.json'),kind='Fresh disc HLE platform -> reconstructed game loader/entry/startup/120world returns',runs=runs,
        initial_saved_machine_state_required=False,HLE_platform_required=True,HLE_disabled_after_DD40=True,
        captured674byte_stream_phase_retained=True,first_divergent_world_task_return_number=divergence,
        divergence_unit='World task return/update number; not a physical/video frame number.',
        all_checked_state_and_event_timelines_equal=True,whole_game_complete=False,
        limits=report['limits'],new_training=False,new_local_model_C_authorship=False)
    for base in [ROOT,INSTALLED]:
        session=json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text());p=Path(session['directory'])/'emulator-runtime/summary.json';data=json.loads(p.read_text());data['fresh_HLE_entry_startup_tasks_comparison']=compact;save(p,data)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR TASK\nConnect reconstructed game180000/4000/DD40/startup/world tasks to a fresh disc HLE load without saved machine state. Pair native/C from isolated fresh processes; retain explicit platform/file/timing limits and failed experiments. Do not call looping instruction counts unique code coverage or full playability.\n\n'+json.dumps(report,indent=2)+'\n')
    print(out,flush=True)


if __name__=='__main__':main()
