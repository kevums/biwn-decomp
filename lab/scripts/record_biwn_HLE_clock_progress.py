"""Strict paired evidence for incremental CD delivery, not global timing."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',type=Path,default=ROOT/'runs');parser.add_argument('--loader-cycle-clock',action='store_true');parser.add_argument('--prefix-instruction-clock',action='store_true');parser.add_argument('--atomic-startup',action='store_true');args=parser.parse_args();assert not args.atomic_startup or args.prefix_instruction_clock;assert not args.prefix_instruction_clock or args.loader_cycle_clock
    out=ROOT/('verification/atomic-startup-progress'if args.atomic_startup else'verification/CPU-loader-prefix-progress'if args.prefix_instruction_clock else'verification/CPU-loader-cycle-progress'if args.loader_cycle_clock else'verification/HLE-clock-progress')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    previous=read(ROOT/'verification/HLE-asset-owner-current.json')
    runs={};manifest={}
    for plan in ['up-left','none']:
        ds={}
        for mode in ['native','C']:
            log=args.run_root/(f'atomic-startup-{mode}-120-{plan}.log'if args.atomic_startup else f'CPU-loader-prefix-{mode}-120-{plan}.log'if args.prefix_instruction_clock else f'CPU-loader-cycle-normalized-{mode}-120-{plan}.log'if args.loader_cycle_clock else f'HLE-clock-{mode}-120-{plan}.log');d=Path(log.read_text().splitlines()[0]);ds[mode]=d
            r=read(d/'report.json');assert r['experimental_HLE_asset_clock'] and r['status']=='completed_unpaired_fresh_HLE_side'
            if args.loader_cycle_clock:assert r['experimental_loader_CPU_cycle_clock']
            if args.prefix_instruction_clock:assert r['experimental_prefix_CPU_cycle_clock']
            for p in [log,*d.glob('*.json')]:manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        N,C=ds['native'],ds['C'];ns=read(N/'native-startup.json');cs=read(C/'C-startup.json');a,b=ns['startup'],cs['startup']
        for key in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:assert a[key]==b[key],(plan,'startup',key)
        for phase in ['fresh_HLE_entry','live_prefix']:
            left=a['source4000_entry'][phase];right=b['source4000_entry'][phase]
            for key in left:
                if key not in ['mode','source_C_game','native_CPU_instructions','native_slice_end_bookkeeping_cycles_excluded']:assert left[key]==right[key],(plan,phase,key)
        nr,cr=read(N/'native.json'),read(C/'C.json')
        for key in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert nr[key]==cr[key],(plan,'world',key)
        assert cs['checks']['original_CPU_attempts']==cr['C_original_CPU_attempts']==0
        for suffix in ['HLE-asset-clock-events','world-return-checkpoints','music','JERRY-events']:
            assert read(N/f'native-{suffix}.json')==read(C/f'C-{suffix}.json'),(plan,suffix)
        events=read(N/'native-HLE-asset-clock-events.json');nv,cv=read(N/'native-HLE-asset-VBIs.json'),read(C/'C-HLE-asset-VBIs.json')
        assert len(nv)==len(cv)==12
        for n,v in zip(nv,cv):
            for key in ['CPU','progress','source_completion_VBIs']:assert n[key]==v[key],(plan,'completion',key)
        known=read(Path(previous['runs'][plan]['sources']['native'])/'native-startup.json')['startup']['disc']['requests']
        if args.prefix_instruction_clock:
            assert read(N/'native-prefix-instruction-boundaries.json')==read(C/'C-prefix-instruction-boundaries.json'),(plan,'prefix instruction boundaries')
            boundaries=read(N/'native-prefix-instruction-boundaries.json');assert not boundaries['errors'] and len(boundaries['instructions'])==7412
            assert read(N/'native-startup-clock-probe.json')==read(C/'C-startup-clock-probe.json'),(plan,'startup clock pulse boundaries')
            assert len(read(C/'C-pending-CPU-IRQs.json'))==1
        if args.atomic_startup:
            ni,ci=read(N/'native-startup-instruction-probe.json'),read(C/'C-startup-instruction-probe.json')
            assert ni==ci and ni['full_CPU_state_trace'] and ni['instructions']>370000,(plan,'full startup instruction state trace')
            assert (N/'native-startup-instruction-PCs.bin').read_bytes()==(C/'C-startup-instruction-PCs.bin').read_bytes()
            assert (N/'native-startup-CPU-state-hashes.bin').read_bytes()==(C/'C-startup-CPU-state-hashes.bin').read_bytes()
        assets=a['disc']['requests'];assert len(assets)==len(known)==12
        partial=0;duration=0
        for index,(asset,witness) in enumerate(zip(assets,known)):
            for key in ['destination_start','destination_end','bytes','packed_binary_MSF','sha256']:assert asset[key]==witness[key],(plan,'payload',index,key)
            assert not asset['captured_stream_phase_used']
            pulses=[e for e in events if e['asset_index']==index];assert len(pulses)>1
            assert sum(e['advanced_ticks']for e in pulses)==asset['HLE_stream_ticks']
            assert len(pulses)==asset['source_completion_VBIs']
            assert not pulses[-1]['stream_active'] and pulses[-1]['source_progress']>=asset['destination_end']
            progressing=[e for e in pulses if e['stream_active'] and asset['destination_start']<e['source_progress']<asset['destination_end']]
            assert progressing,(plan,'no partial progress',index)
            assert all(e['GPU_write_pointer_after']>=e['GPU_write_pointer_before'] for e in pulses)
            partial+=len(progressing);duration+=asset['last_clock_us']-asset['first_clock_us']
        assert all(h['disc_completed'] is None for h in a['handoffs'])
        pn,en=a['source4000_entry']['live_prefix'],a['source4000_entry']['fresh_HLE_entry']
        windows=dict(game_loader=en['counts']['CPU_steps'],game_entry=pn['native_CPU_instructions'],startup_outer_loop=ns['checks']['native_CPU_steps'],source_asset_VBI_handlers=sum(v['reference_CPU_steps']for v in nv),world_tasks=nr['processor_instructions'])
        music=read(N/'native-music.json');jerry=read(N/'native-JERRY-events.json');points=read(N/'native-world-return-checkpoints.json');assert len(points)==120
        runs[plan]=dict(sources={k:str(v)for k,v in ds.items()},CPU_windows=windows,total_reference_CPU_steps=sum(windows.values()),
            total_DSP_instructions=sum(v['instructions']for v in music['calls'])+sum(v['instructions']for v in pn['music_calls']),
            asset_reads=12,asset_bytes=sum(v['bytes']for v in assets),all_asset_payload_hashes_match_prior_source_witness=True,
            asset_HLE_stream_ticks=sum(v['HLE_stream_ticks']for v in assets),source_asset_VBIs=len(events),partial_progress_events=partial,
            startup_clock_pulses=a['external_system_clock_ticks'],last_asset_clock_us=events[-1]['clock_us'],
            handoff_finishes_read=False,captured674byte_phase_used=False,direct_RAM_progress_write=False,file_payload_memcpy_adapter=False,
            created_contexts=len(a['contexts']),world_returns=120,final_X=points[-1]['player']['0x49c50'],final_Z=points[-1]['player']['0x49c56'],
            SSI_callbacks=sum([1,1]in v['IRQs']for v in jerry['events']),timer1_DSP_IRQ2_callbacks=sum([2,1]in v['IRQs']for v in jerry['events']),
            all_recorded_PCM_pairs_silent=all(v['PCM']==[0,0]for v in jerry['events']),all_checked_states_traces_and_events_equal=True)
    report=dict(status='incremental_HLE_assets_source_clock_120world_input_control_native_C_match',directory=str(out),runs=runs,
        initial_saved_machine_state_loaded=False,HLE_services_retained_after_DD40=True,coherent_single_asset_transport_owner=True,
        handoff_burst_completion_removed=True,source_clock_quantum_us=16666.666666666668,
        new_training=False,new_local_model_C_authorship=False,whole_game_complete=False,global_cycle_scheduling_verified=False,
        limits=['Platform HLE supplies boot stub, sector/sentinel delivery and BIOS APIs; native firmware authentication remains bypassed.',
                'CD bytes advance by core halfline budgets at successive source-clock pulses; source VBI observes partial progress. The 16666.6667us system clock cadence remains supplied, not derived from CPU/GPU instruction cycles. Video/OP/main events remain held; GPU/blitter execution synchronous.',
                'JERRY callbacks share the supplied clock quantum, with opt-in DSP IRQ ownership. Recorded PCM is silent. Remaining game paths, physical controller/scanout and standalone playable C application are unfinished.'],
        next_action='Replace supplied source-clock pulses with processor-cycle/event scheduling and verify video plus non-silent source music; retain intermediate transfer/state regressions.')
    if args.loader_cycle_clock:
        for plan in ['up-left','none']:
            native=read(Path(runs[plan]['sources']['native'])/'native-startup.json')['startup']['source4000_entry']['fresh_HLE_entry']
            rebuilt=read(Path(runs[plan]['sources']['C'])/'C-startup.json')['startup']['source4000_entry']['fresh_HLE_entry']
            assert native['CPU_cycle_driven_main_events'] and rebuilt['CPU_cycle_driven_main_events']
            assert not native['supplied_main_event_quanta'] and not rebuilt['supplied_main_event_quanta']
            assert native['native_slice_end_bookkeeping_cycles_excluded']==1 and rebuilt['native_slice_end_bookkeeping_cycles_excluded']==0
            assert native['CPU_cycles']==rebuilt['CPU_cycles']==38988932
            runs[plan]['loader_CPU_clock']=dict(cycles=native['CPU_cycles'],elapsed_us=native['CPU_elapsed_us'],main_events=native['counts']['main_events'],native_GPU_GO_timeslice_bookkeeping_cycles_excluded=1,shared_bus_extra_cycles=native['shared_bus_extra_cycles'],native_C_CPU_cycle_count_and_elapsed_match=True)
        report['status']='CPU_cycle_driven_HLE_loader_incremental_assets_120world_input_control_native_C_match'
        report['loader_main_event_poll_quanta_removed']=True
        report['limits'][1]='Loader180000->4000 main events advance from executed/predicted CPU instruction costs at pinned NTSC clock rate, not fixed quanta at CD_poll. One native GPU_GO one-cycle request bookkeeping artifact is separately excluded by a narrow verified source rule. GPU execution remains synchronous and JERRY held in that loader. After4000, prefix alternation and16666.6667us system/JERRY/asset pulses remain supplied, with video/OP/main scheduling held; not global cycle scheduling.'
        report['next_action']='Extend CPU instruction timing into4000prefix/startup and asynchronous GPU/DSP/video events, keeping all current state/disc/event regression gates.'
    if args.prefix_instruction_clock:
        for plan in ['up-left','none']:
            prefix=read(Path(runs[plan]['sources']['native'])/'native-live4000-prefix.json')
            clock=prefix['instruction_clock'];assert clock['CPU_cycles']==105572 and clock['CPU_instruction_boundaries']==7412
            assert len(clock['GPU_timer_events'])==1 and clock['GPU_timer_events'][0]['instructions']==29
            runs[plan]['entry_prefix_CPU_clock']=clock
            runs[plan]['pending_source_CPU_IRQs_after_prefix']=1
        report['status']='CPU_timed_loader_and_entry_prefix_incremental_assets_120world_native_C_match'
        core_proof=read(ROOT/'verification/BIWN-CPU-IRQ-state-export-candidate.json')
        assert core_proof['suite_exit_code']==0 and core_proof['emulation_C_source_byte_identical']
        report['diagnostic_core_suite_status']='exit0;32private_corpus_checks_skipped'
        report['diagnostic_core_suite_log']=core_proof['suite_log']
        report['emulator_C_source_changed']=False
        report['diagnostic_export_addition']='Existing read-only M68KStateSave exposed; no state loading'
        report['installed_launcher_new_prefix_path_adopted']=True
        report['installed_launcher_end_to_end_status']='game comparisons passed; SDK/outer completion pending'if args.run_root.parent.name=='fresh-HLE-runtime'else'not verified by this recorder'
        report['entry_prefix_main_events_CPU_cost_driven']=True
        report['new_pending_GPU_timer_and_CPU_IRQ_handled_by_C_source']=True
        report['limits'][1]='Loader180000->4000 and entry4000->DD40 main events advance from CPU costs at pinned NTSC clock. Entry GPU timer IRQ is delivered by actual main queue and its source C handler runs to its saved return PC. A pending TOM CPU request is sampled using queued/acknowledged line state and SR mask, not pending latch alone; source CPU handler runs in C. GPU/DSP helpers/IRQ handlers remain synchronous, loader/prefixJERRY held. AfterDD40 system/JERRY/asset cadence16666.6667us and later main/video/OP timing remain supplied/held; not global cycle scheduling.'
        report['next_action']='Extend instruction boundaries into source startup/scheduler and share CPU/GPU/DSP/video/JERRY time rather than supplied postDD40 pulses; continue silent-audio diagnosis.'
    if args.atomic_startup:
        for plan in ['up-left','none']:
            probe=read(Path(runs[plan]['sources']['native'])/'native-startup-instruction-probe.json')
            runs[plan]['startup_instruction_boundaries']=probe['instructions']
            runs[plan]['startup_unique_PCs']=probe['unique_PCs']
            runs[plan]['all_startup_PC_and_full_CPU_states_match']=True
            runs[plan]['startup_CPU_state_trace_sha256']=probe['CPU_state_trace_sha256']
        report['status']='instruction_based_math_scheduler_geometry_input_full_startup_CPU_trace_and120world_native_C_match'
        report['startup_instruction_boundary_gaps']=0
        report['startup_clock_cadence_still_supplied']=True
        report['new_weight_training']=False
        report['new_unique_game_coverage']=False
        report['local_model_instruction_helper']='One ADDX.L helper passes69632native opcode cases after two explicit repairs. Other fresh thinking-on attempts are unpromoted and raw-format rejected; no general reliability claim.'
        report['next_action']='Advance postDD40 shared event queues from the now complete startup CPU boundaries, replacing supplied system/asset/JERRY pulses; keep all CPU/asset/world/event checks and code-authoring gates.'
    for name in ['biwn_HLE_asset_clock.py','biwn_HLE_asset_owner.py','check_biwn_entry_natural_task_rounds.py','record_biwn_HLE_clock_progress.py','biwn_fresh_HLE_entry.py','biwn_m68k_cycle_cost.py','biwn_divu_cycle_cost_local.py','biwn_live_source_prefix.py','biwn_pending_CPU_irq.py','check_biwn_entry_scheduled_startup.py','build_biwn_instruction_observer.py','biwn_startup_instruction_probe.py','generate_biwn_atomic_startup_math.py','generate_biwn_atomic_scheduler.py','generate_biwn_atomic_geometry.py','generate_biwn_atomic_input_poll.py']:
        p=ROOT/'scripts'/name;manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    save(out/'report.json',report);save(out/'input-manifest.json',manifest)
    save(ROOT/('verification/atomic-startup-current.json'if args.atomic_startup else'verification/CPU-loader-prefix-current.json'if args.prefix_instruction_clock else'verification/CPU-loader-cycle-current.json'if args.loader_cycle_clock else'verification/HLE-clock-current.json'),report)
    compact={**report,'report':str(out/'report.json')};compact.pop('directory')
    for base in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
        session=read(base/'projects/black-ice-white-noise/analysis/current-session.json');p=Path(session['directory'])/'emulator-runtime/summary.json';summary=read(p);summary['atomic_startup_runtime_comparison'if args.atomic_startup else'CPU_cycle_loader_prefix_runtime_comparison'if args.prefix_instruction_clock else'CPU_cycle_loader_runtime_comparison'if args.loader_cycle_clock else'incremental_HLE_asset_runtime_comparison']=compact;save(p,summary)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR IMPLEMENTATION TASK\nMove HLE sector bytes out of handoff bursts into successive source-clock pulses. Source VBI must observe partial progress and write completion. Pair original/C CPU/RAM and all120 input/control world/event checkpoints, compare12asset hashes, retain explicit supplied-clock/global-timing limits.\n\n'+json.dumps(report,indent=2)+'\n')
    if args.loader_cycle_clock:
        with(out/'who-prompts-and-responses.txt').open('a')as f:f.write('\nADDITIONAL COORDINATOR TASK\nReplace loader CD_poll main-event quanta with CPU instruction-cost time; investigate returned native GPU_GO timeslice bookkeeping without shifting event timing. Retain initial failed/unpaired runs, complete native/C loader/event/120input-control comparison and explicit post4000 synchronous/supplied-clock limits.\n')
    print(out)

if __name__=='__main__':main()
