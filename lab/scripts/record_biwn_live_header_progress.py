"""Publish the live361E BIOS/game handoff through source entry and task updates."""
import json,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text());save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'verification/live-header-entry-progress'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows={};points={};paths=[]
for name in ['up-left','control']:
 folder=Path((ROOT/f'runs/live-header-entry-JERRY-{name}-120.log').read_text().splitlines()[0]);d=read(folder/'report.json');assert d['continuous_live_header_to_startup_tasks'] and not d['initial4000_capture_loaded'] and not d['DD40_export_loaded'];assert d['all_world_return_checkpoints_equal'] and not d['initial_JERRY_queue_normalized']
 tail=read(folder/'native-header-tail/native.json');C_tail=read(folder/'C-header-tail/C.json')
 for k in ['CPU_steps','CPU_PC_trace','final','GPU_calls','events','IRQ_events']:assert tail[k]==C_tail[k],k
 assert tail['CPU_steps']==1386 and sum(g['instructions']for g in tail['GPU_calls'])==5523 and len(tail['events'])==274 and len(tail['IRQ_events'])==185
 assert C_tail['original_GPU_instructions_on_C_path']==0 and C_tail['original_DSP_instructions']==0
 assert len(read(folder/'native-header-tail/native-CPU-instruction-checkpoints.json'))==1386
 prefix=read(folder/'native-live4000-prefix.json');C_prefix=read(folder/'C-live4000-prefix.json')
 for k in ['CPU','RAM','BUTCH_poll_ticks','GPU_calls','music_calls','logical_GPU_sha256','logical_DSP_sha256']:assert prefix[k]==C_prefix[k],k
 assert prefix['native_CPU_instructions']==10375 and sum(c['instructions']for c in prefix['music_calls'])==112
 points[name]=read(folder/'native-world-return-checkpoints.json');assert points[name]==read(folder/'C-world-return-checkpoints.json')
 startup=read(folder/'native-startup.json');assert startup['checks']['native_CPU_steps']==360435
 for mode in ['native','C']:
  debug=read(folder/(mode+'-adoption-debug.json'));assert debug['initial_restore_PC']=='0x361e' and not debug['DD40_export_loaded']
  assert(folder/(mode+'-initial-event-queue.bin')).read_bytes()==(folder/(mode+'-setup-event-queue.bin')).read_bytes()
 music=read(folder/'native-music.json');events=read(folder/'native-JERRY-events.json');assert music==read(folder/'C-music.json') and events==read(folder/'C-JERRY-events.json')
 assert sum(c['instructions']for c in music['calls'])==3177562 and len(events['events'])==36157
 counts=collections.Counter(i[0]for e in events['events']for i in e['IRQs']);assert counts=={1:34111,2:2046}
 assert all(not any(e['PCM'])for e in events['events']) and d['results'][1]['C_original_CPU_attempts']==0
 player=points[name][-1]['player'];later=d['results'][0]['processor_instructions'];rows[name]=dict(report=str(folder/'report.json'),initial_restore_PC='0x361e',header_tail_CPU_instructions=1386,entry_CPU_instructions=10375,startup_CPU_instructions=360435,later_task_CPU_instructions=later,total_CPU_instructions=1386+10375+360435+later,world_returns=120,header_tail_GPU_instructions=5523,header_tail_scheduled_main_and_JERRY_events=274,header_tail_DSP_SSI_IRQ_lines=137,total_DSP_instructions=3177674,entry_DSP_instructions=112,startup_task_DSP_instructions=3177562,startup_task_SSI_words=34111,startup_task_timer1_DSP_IRQ2_events=2046,all_checked_native_C_states_event_queues_and_timelines_match=True,initial4000_or_DD40_checkpoint_loaded=False,intermediate_processor_RAM_reset_or_restore=False,initial_queue_rebuild=False,all_startup_task_PCM_silent=True,final_X=player['0x49c50'],final_Z=player['0x49c56'])
 paths +=[folder/p for p in ['report.json','native-header-tail/native.json','C-header-tail/C.json','native-header-tail/native-CPU-instruction-checkpoints.json','native-live4000-prefix.json','C-live4000-prefix.json','native-startup.json','C-startup.json','native-world-return-checkpoints.json','C-world-return-checkpoints.json']]
assert rows['up-left']['total_CPU_instructions']==1316503 and rows['control']['total_CPU_instructions']==1309467
assert points['up-left'][:5]==points['control'][:5] and points['up-left'][5]!=points['control'][5]
assert rows['up-left']['final_Z']==40092 and rows['control']['final_Z']==40096
result=dict(status='live_captured361E_handoff_entry_startup_tasks_and_events_native_C_match',directory=str(out),runs=rows,
 source361E_to120returns_live=True,initial4000_and_DD40_checkpoint_loads_removed=True,
 initial_firmware_header_capture_required=True,input_scope='Captured diagnostic firmware-header state atCPU361E, with largerstagebytes alreadyloaded. InitialROM/disc/firmware/GPUstack/reseek/TOC diagnostics remain; no fresh power-on/authentication/source data-read proof before361E.',
 remaining_controls='Opt-inSSI-chain anddefaultNULL GPU/DSPIRQ-owner diagnostics. Header304Epolls supply one main/video andoneJERRY callback with synchronousGPU services; later GPU IRQ2 and16666.6667us world-to-JERRY slices remain supplied. BIOS303C/3042asset file adapters,TOCorigin13227/captured674bytephase, synchronousGPU/blitter persist. Main/video/OP/CD events are not yet globally coupled during laterstartup/tasks.',
 count_scope='CPU total spans this one live run. DSP total includes112entry-prefix and3177562startup/task instructions; headerDSP is halted with0opcodes. The274header events and34111laterSSI words are different scoped counters; do not silently merge callback counts with instruction counts.',
 new_training=False,new_local_model_C_authorship=False,ordinary_boot_verified=False,global_cycle_scheduling_verified=False,audible_source_music_verified=False,physical_scanout_verified=False,whole_game_complete=False,
 next_action='Connect earlier firmware/authentication/read phases without the initial361Ecapture and make main/video/OP/CD andCPU/GPU/DSP timing global throughout the run. Preserve other file/model/clock controls until independently removed. Keep trained-model/nativeChat/future256GB gates.')
save(out/'report.json',result);save(ROOT/'verification/live-header-entry-current.json',result)
compact=dict(report=str(out/'report.json'),kind='Live captured361E BIOS handoff through entry/startup/120taskreturns',input_CPU_instructions=1316503,control_CPU_instructions=1309467,CPU_windows=dict(header_tail=1386,entry=10375,startup=360435,input_tasks=944307,control_tasks=937271),DSP_total_each_run=3177674,DSP_windows=dict(header_tail=0,entry=112,startup_tasks=3177562),world_returns_each_run=120,header_GPU_instructions=5523,header_scheduled_events=274,header_DSP_SSI_IRQ_lines=137,startup_task_SSI_words_each_run=34111,startup_task_timer1_DSP_IRQ2_each_run=2046,all_native_C_checked_states_and_event_timelines_match=True,initial4000_checkpoint_required=False,DD40_checkpoint_required=False,earlier_captured361E_input_required=True,stage_bytes_already_loaded_in_initial_capture=True,opt_in_models_and_supplied_timing_remain=True,input_end_X=9376,input_end_Z=40092,control_end_Z=40096,all_startup_task_PCM_silent=True,ordinary_boot=False,global_cycles=False,full_playability=False,remaining_controls=result['remaining_controls'])
for root in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
 session=Path(read(root/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';d=read(p);d['firmware_bootstrap_DSP_progress']['source_stage_loading']['live_captured_header_entry_comparison']=compact;save(p,d)
paths +=[ROOT/'scripts/biwn_live_header_handoff.py',ROOT/'scripts/biwn_live_source_prefix.py',ROOT/'scripts/check_biwn_entry_natural_task_rounds.py',Path(__file__)];save(out/'input-manifest.json',{str(p):sha(p)for p in paths})
(out/'who-prompts-and-responses.txt').write_text('COORDINATOR: Codex connected the already checked361E BIOS/GPU/event tail directly into checked4000entry andDD40startup/tasks. It passes the ownedCPU to the entry runner and retains ownedGPU/DSP state, rather than rebuilding them from original shadows. Only the initial361Ecore image is restored; no4000/DD40image is loaded. Original/C match allchecked phases. No localmodel authorednewCcode or weights. Earlierfirmwarecapture/model/timing/file providers remain.\n\nRESULTS:\n'+json.dumps(result,indent=2)+'\n');print(out)
