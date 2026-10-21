"""Record actual pinned JERRY event handling and explicit initial queue repair."""
import collections
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())
save = lambda p, value: p.write_text(json.dumps(value, indent=2) + '\n')
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = ROOT / 'verification/entry-JERRY-event-progress' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
rows, points, inputs = {}, {}, []
for name in ['up-left','control']:
    folder = Path((ROOT / f'runs/entry-JERRY-events-{name}-120.log').read_text().splitlines()[0])
    report = read(folder / 'report.json')
    assert report['actual_pinned_JERRY_event_queue_used'] and report['initial_JERRY_queue_normalized']
    assert report['all_world_return_checkpoints_equal'] and not report['global_cycle_scheduling_verified']
    points[name] = read(folder / 'native-world-return-checkpoints.json')
    assert points[name] == read(folder / 'C-world-return-checkpoints.json')
    music = read(folder / 'native-music.json')
    events = read(folder / 'native-JERRY-events.json')
    assert music == read(folder / 'C-music.json') and events == read(folder / 'C-JERRY-events.json')
    assert not events['errors']
    for label in ['initial','setup']:
        assert (folder / f'native-{label}-event-queue.bin').read_bytes() == (folder / f'C-{label}-event-queue.bin').read_bytes()
    counts = collections.Counter(irq[0] for event in events['events'] for irq in event['IRQs'])
    assert counts == {1:34110,2:2046}
    instructions = sum(call['instructions'] for call in music['calls'])
    assert instructions == 3177473
    assert all(not any(event['PCM']) for event in events['events'])
    assert report['results'][1]['C_original_CPU_attempts'] == 0
    startup = read(folder / 'native-startup.json')
    final = points[name][-1]['player']
    rows[name] = dict(report=str(folder / 'report.json'), world_returns=120,
        native_CPU_instructions=startup['checks']['native_CPU_steps']+report['results'][0]['processor_instructions'],
        source_DSP_instructions=instructions, JERRY_events=len(events['events']), SSI_words=counts[1], timer1_DSP_IRQ2_events=counts[2],
        elapsed_JERRY_time_us=events['elapsed_us'], original_C_CPU_RAM_context_devices_GPU_DSP_DAC_event_queue_match=True,
        native_C_DSP_PC_trace_counts_and_exact_event_timeline_match=True, nonzero_PCM_pairs=0,
        final_X=final['0x49c50'], final_Z=final['0x49c56'])
    inputs += [folder / file for file in ['report.json','native-JERRY-events.json','C-JERRY-events.json','native-initial-event-queue.bin','native-setup-event-queue.bin']]
assert points['up-left'][:5] == points['control'][:5] and points['up-left'][5] != points['control'][5]
assert rows['up-left']['final_Z']==40092 and rows['control']['final_Z']==40096
bad = Path((ROOT / 'runs/entry-JERRY-events-3-export-fixed.log').read_text().splitlines()[0])
good = Path(rows['up-left']['report']).parent
queue = (good / 'native-initial-event-queue.bin').read_bytes()
def live_JERRY_ids(blob):
    return collections.Counter(struct.unpack_from('=BBid',blob,12+32*14+i*14)[1] for i in range(32) if blob[12+32*14+i*14])
before = live_JERRY_ids(queue)
after = live_JERRY_ids((good/'native-setup-event-queue.bin').read_bytes())
assert before == {5:31,4:1} and after == {3:1,4:1,5:1}
bad_events = read(bad/'native-JERRY-events.json')
build = read(ROOT / 'verification/BIWN-DSP-IRQ-forward-candidate.json')
assert digest(Path(build['core_path'])) == build['core_sha256']
build.update(status='diagnostic_event_queue_native_C_checks_passed_not_promoted',full_tests_exit_code=0,
    private_ROM_audio_presence_and_clipping_sentinels='Skipped: optional private ROMs absent; not passes.',
    RetroArch_audio_validation='Pending; GUI unavailable. Diagnostic harness only.',
    default_IRQ_owner='NULL; original path retained unless explicitly installed')
save(Path(build['directory'])/'build.json',build)
save(ROOT/'verification/BIWN-DSP-IRQ-forward-candidate.json',build)
result = dict(status='source_entry_tasks_and_pinned_JERRY_events_native_C_match_with_explicit_queue_rebuild',directory=str(out),runs=rows,
    prior_turn='progress: source DSP mixer linked to source-derived startup/tasks and shared NPC runtime rebuilt',
    queue_problem=dict(report=str(bad/'report.json'),SSI_callbacks_before=31,PIT2_callbacks_before=1,
        before_queue_capture=str(good/'native-initial-event-queue.bin'),before_queue_is_same_source_DD40_export=True,
        events_in_266666us=len(bad_events['events']),native_C_matched=True,timing_proof_accepted=False),
    queue_control=dict(action='Remove all saved SSI/PIT1/PIT2 callbacks, then run pinned JERRYResetPIT1/JERRYResetPIT2/JERRYRescheduleI2S using existing registers.',
        SSI_callbacks_after=1,PIT1_callbacks_after=1,PIT2_callbacks_after=1,CPU_RAM_or_device_register_reset=False,
        source_export_is_not_normal_ordinary_boot=True),
    timing_scope='Actual pinned hardware queue determines SSI/timer deadlines and IRQ order. CPU/world-to-JERRY time remains a supplied16666.6667us slice at each source-system tick. Main/video/OP/CD scheduling and CPU/GPU instruction-cycle interleaving are not integrated.',
    source_DSP_original_execution_on_C_path=False,original_CPU_execution_on_C_path=False,
    PCM_scope='All samples silent; neither audible game music nor physical clock accuracy/playability proved.',
    diagnostic_core=build, new_training=False,local_model_authored_new_C=False,whole_game_complete=False,
    remaining_work=['Recapture through source boot with a valid event queue, removing the explicit queue rebuild.','Link main/video/OP/CD events and CPU/GPU/DSP cycle scheduling.','Source-triggered audible sound/music, remaining helpers/scenes, physical controllers/scanout and full C playability.'])
save(out/'report.json',result);save(ROOT/'verification/entry-JERRY-event-current.json',result)
compact=dict(report=str(out/'report.json'),kind='Separate source-entry task test with actual pinned JERRY queue and explicit initial queue rebuild',
    world_returns_each_run=120,source_DSP_instructions_each_run=3177473,SSI_words_each_run=34110,timer1_DSP_IRQ2_each_run=2046,
    JERRY_events_each_run=36156,JERRY_elapsed_us_each_run=2216666.6666655233,
    native_C_CPU_RAM_GPU_DSP_DAC_event_queue_and_timeline_match=True,all_PCM_silent=True,
    saved_SSI_callbacks_before=31,SSI_callbacks_after_rebuild=1,initial_queue_rebuild_required=True,
    host_world_to_JERRY_time_slice_us=16666.666666666668,global_cycle_schedule_verified=False,
    video_held=True,audible_music_verified=False,full_playability=False,remaining_work=result['remaining_work'])
installed=Path.home()/'.lmstudio/local-ai-lab'
for root in [ROOT,installed]:
    session=Path(read(root/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    p=session/'emulator-runtime/summary.json';summary=read(p)
    summary['firmware_bootstrap_DSP_progress']['source_stage_loading']['entry_source_JERRY_queue_comparison']=compact;save(p,summary)
inputs += [ROOT/'scripts/check_biwn_entry_natural_task_rounds.py',ROOT/'scripts/build_biwn_DSP_IRQ_forward_core.py',Path(__file__),Path(build['core_path']),Path(build['diagnostic_source'])/'src/jerry/dsp.c',Path(build['directory'])/'full-test.log']
save(out/'input-manifest.json',{str(p):digest(p) for p in inputs})
(out/'who-prompts-and-responses.txt').write_text('COORDINATOR: Codex added a default-off diagnostic DSP IRQ owner and actual JERRY event mode. It discovered31 duplicate SSI callbacks in the held diagnostic export, rejected that cadence as timing proof, and rebuilt only the queue from existing registers under an explicit control. Original and C execute identical event timelines. No new local-model C authorship or weight training.\n\nRESULTS:\n'+json.dumps(result,indent=2)+'\n')
print(out)
