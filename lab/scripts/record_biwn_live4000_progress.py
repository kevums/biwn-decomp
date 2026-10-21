"""Record one live captured4000-to-startup/task runtime without DD40 reloads."""
import collections
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'verification/live4000-entry-progress'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
old=read(ROOT/'verification/source-SSI-queue-current.json');rows={};points={};inputs=[]
for name in ['up-left','control']:
    folder=Path((ROOT/f'runs/live4000-entry-JERRY-{name}-120.log').read_text().splitlines()[0]);d=read(folder/'report.json')
    assert d['continuous_live4000_to_startup_tasks'] and not d['DD40_export_loaded']
    assert d['all_world_return_checkpoints_equal'] and not d['initial_JERRY_queue_normalized']
    assert d['source_single_SSI_chain_diagnostic'] and d['actual_pinned_JERRY_event_queue_used']
    native_prefix=read(folder/'native-live4000-prefix.json');C_prefix=read(folder/'C-live4000-prefix.json')
    for key in ['CPU','RAM','BUTCH_poll_ticks','GPU_calls','music_calls','logical_GPU_sha256','logical_DSP_sha256']:
        assert native_prefix[key]==C_prefix[key],key
    assert native_prefix['native_CPU_instructions']==10375
    prefix_DSP=sum(call['instructions']for call in native_prefix['music_calls']);assert prefix_DSP==112
    points[name]=read(folder/'native-world-return-checkpoints.json');assert points[name]==read(folder/'C-world-return-checkpoints.json')
    previous=Path(old['runs'][name]['report']).parent
    assert points[name]==read(previous/'native-world-return-checkpoints.json')
    for mode in ['native','C']:
        debug=read(folder/(mode+'-adoption-debug.json'))
        assert debug['initial_restore_PC']=='0x4000' and not debug['DD40_export_loaded']
        assert(folder/(mode+'-initial-event-queue.bin')).read_bytes()==(folder/(mode+'-setup-event-queue.bin')).read_bytes()
    music=read(folder/'native-music.json');events=read(folder/'native-JERRY-events.json')
    assert music==read(folder/'C-music.json') and events==read(folder/'C-JERRY-events.json') and not events['errors']
    counts=collections.Counter(i[0]for e in events['events']for i in e['IRQs']);assert counts=={1:34111,2:2046}
    assert sum(c['instructions']for c in music['calls'])==3177562
    assert all(not any(e['PCM'])for e in events['events']) and d['results'][1]['C_original_CPU_attempts']==0
    startup=read(folder/'native-startup.json');prefix_steps=native_prefix['native_CPU_instructions'];startup_steps=startup['checks']['native_CPU_steps'];task_steps=d['results'][0]['processor_instructions']
    assert startup_steps==360435
    player=points[name][-1]['player'];rows[name]=dict(report=str(folder/'report.json'),world_returns=120,
        source4000_prefix_CPU_instructions=prefix_steps,source_DD40_startup_CPU_instructions=startup_steps,
        later_task_CPU_instructions=task_steps,total_CPU_instructions_from4000=prefix_steps+startup_steps+task_steps,
        source_DSP_instructions_during_startup_and_tasks=3177562,source4000_prefix_DSP_instructions=prefix_DSP,total_DSP_instructions_from4000=prefix_DSP+3177562,SSI_words=34111,timer1_DSP_IRQ2_events=2046,
        all_checked_CPU_RAM_contexts_GPU_DSP_devices_DAC_event_queue_and_timeline_match=True,
        previous_post_DD40_full_checkpoints_unchanged=True,DD40_export_loaded=False,
        intermediate_CPU_RAM_GPU_DSP_reset_or_export_restore=False,initial_queue_rebuild=False,
        all_PCM_silent=True,final_X=player['0x49c50'],final_Z=player['0x49c56'])
    inputs += [folder/file for file in ['report.json','native-live4000-prefix.json','C-live4000-prefix.json','native-startup.json','C-startup.json','native-adoption-debug.json','C-adoption-debug.json','native-JERRY-events.json','C-JERRY-events.json']]
assert rows['up-left']['total_CPU_instructions_from4000']==1315117 and rows['control']['total_CPU_instructions_from4000']==1308081
assert points['up-left'][:5]==points['control'][:5] and points['up-left'][5]!=points['control'][5]
assert rows['up-left']['final_Z']==40092 and rows['control']['final_Z']==40096
result=dict(status='live_captured4000_entry_startup_tasks_and_JERRY_events_native_C_match',directory=str(out),runs=rows,
    initial_input='Captured diagnostic native4000 firmware/game handoff checkpoint with explicitly restored originalROM/disc/diagnostic providers. This remains an initial fixture, not fresh ordinary boot.',
    DD40_export_restore_removed=True,initial_JERRY_queue_rebuild=False,source4000_to120returns_live=True,
    owned_CPU_GPU_DSP_and_shared_devices_carried_without_reload=True,
    remaining_controls='Opt-in singleSSI-chain peripheral model; captured firmware/4000checkpoint and priorROM/CD/SSI/GPUstack/reseek/TOC diagnostics; source-defined processor alternation at relocation/bootstrap/mailbox polls; BIOS303C/3042 file adapters,TOCorigin13227/captured674bytephase;external source GPU IRQ2 and16666.6667us world-to-JERRY slices;synchronous GPU/blitter;main/video/OP/CD global scheduling still held or separately supplied.',
    new_training=False,new_local_model_C_authorship=False,ordinary_boot_verified=False,global_cycle_scheduling_verified=False,
    audible_music_verified=False,whole_game_complete=False,
    remaining_work=['Connect earlier firmware/CD-auth/game handoff into this runtime without the initial4000checkpoint.','Connect main/video/OP/CD and CPU/GPU/DSP cycle events, removing supplied clocks and synchronous completions.','Remaining helpers/scenes, audible source audio, physical controllers/scanout and full C playability.','Trained-model semantic gates, native Chat adoption and future256GB configuration checks.'])
save(out/'report.json',result);save(ROOT/'verification/live4000-entry-current.json',result)
compact=dict(report=str(out/'report.json'),kind='Live captured4000 entry through startup and120task returns; no DD40 export/restore',
    input_total_CPU_instructions=1315117,control_total_CPU_instructions=1308081,source4000_prefix_CPU_instructions=10375,
    DD40_startup_CPU_instructions=360435,input_later_task_CPU_instructions=944307,control_later_task_CPU_instructions=937271,
    world_returns_each_run=120,prefix_DSP_instructions_each_run=112,total_DSP_instructions_from4000_each_run=3177674,DSP_instructions_during_startup_tasks_each_run=3177562,SSI_words_each_run=34111,timer1_DSP_IRQ2_each_run=2046,
    native_C_all_checked_states_and_event_timelines_match=True,DD40_export_restore_required=False,
    captured4000_initial_checkpoint_required=True,initial_queue_rebuild_required=False,opt_in_SSI_model_required=True,
    input_end_X=9376,input_end_Z=40092,control_end_Z=40096,input_control_diverge_at_return=6,
    all_PCM_silent=True,ordinary_boot_verified=False,global_cycle_schedule_verified=False,full_playability=False,
    remaining_controls=result['remaining_controls'],remaining_work=result['remaining_work'])
for root in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
    session=Path(read(root/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';d=read(p)
    d['firmware_bootstrap_DSP_progress']['source_stage_loading']['live_captured4000_entry_comparison']=compact;save(p,d)
inputs += [ROOT/'scripts/biwn_live_source_prefix.py',ROOT/'scripts/check_biwn_entry_natural_task_rounds.py',Path(__file__)]
save(out/'input-manifest.json',{str(p):sha(p)for p in inputs})
(out/'who-prompts-and-responses.txt').write_text('COORDINATOR: Codex extracted the already checked original/C4000prefix as a reusable runtime function, restored helper bindings after execution, and carried CPU/GPU/DSP/shared devices into source startup/tasks without loading anyDD40state file. C banked DSP extension copies existing owned state once; it does not reset or reinitialize the DSP. The captured4000fixture and declared peripheral/timing providers remain. No new local-model C code or weight training.\n\nCOMMANDS:\ncheck_biwn_entry_natural_task_rounds.py --live-4000 --rounds 120 --input-plan up-left --music-words --jerry-events --no-publish [explicit checked core/prefix/export-proof metadata]\ncheck_biwn_entry_natural_task_rounds.py --live-4000 --rounds 120 --input-plan none --music-words --jerry-events --no-publish [same metadata]\n\nRESULTS:\n'+json.dumps(result,indent=2)+'\n')
print(out)
