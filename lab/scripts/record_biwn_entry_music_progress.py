"""Record source-entry CPU/task/DSP integration with declared event timing."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())
save = lambda p, v: p.write_text(json.dumps(v, indent=2) + '\n')
out = ROOT / 'verification/entry-source-music-progress' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
rows = {}
points = {}
inputs = []
for name in ['up-left', 'control']:
    folder = Path((ROOT / f'runs/entry-music-words-{name}-120.log').read_text().splitlines()[0])
    report = read(folder / 'report.json')
    assert report['declared_source_DSP_music_events'] and report['all_world_return_checkpoints_equal']
    assert report['requested_world_returns'] == 120 and not report['global_cycle_scheduling_verified']
    native, reconstructed = report['results']
    assert reconstructed['C_original_CPU_attempts'] == 0
    points[name] = read(folder / 'native-world-return-checkpoints.json')
    assert points[name] == read(folder / 'C-world-return-checkpoints.json')
    music = read(folder / 'native-music.json')
    assert music == read(folder / 'C-music.json')
    assert len(music['word_events']) == 133
    assert all(not any(e['PCM']) for e in music['word_events'])
    startup = read(folder / 'native-startup.json')
    total_steps = startup['checks']['native_CPU_steps'] + native['processor_instructions']
    player = points[name][-1]['player']
    rows[name] = dict(report=str(folder / 'report.json'), world_returns=120,
        original_CPU_instructions=total_steps, startup_CPU_instructions=startup['checks']['native_CPU_steps'],
        task_CPU_instructions=native['processor_instructions'], original_CPU_and_C_checkpoints_match=True,
        DSP_instructions=sum(call['instructions'] for call in music['calls']),
        DSP_atomic_blocks=sum(call['blocks'] for call in music['calls']),
        source_DSP_init_and_interrupt_calls=len(music['calls']), SSI_word_events=133,
        timer2_events=sum(2 in e['IRQs'] for e in music['word_events']), nonzero_PCM_pairs=0,
        full_logical_DSP_banks_traces_RAM_devices_DAC_PCM_match=True,
        original_DSP_execution_on_C_path=False, final_X=player['0x49c50'], final_Z=player['0x49c56'])
    inputs += [folder / n for n in ['report.json','native-music.json','C-music.json','native-startup.json','C-startup.json']]
assert rows['up-left']['final_Z'] == 40092 and rows['control']['final_Z'] == 40096
assert points['up-left'][:5] == points['control'][:5] and points['up-left'][5] != points['control'][5]
assert rows['up-left']['DSP_instructions'] == rows['control']['DSP_instructions'] == 14692
result = dict(status='source_DD40_startup_tasks_and_active_DSP_mixer_native_C_match', directory=str(out), runs=rows,
    input_control_first_divergence_return=6, source_DSP_is_no_longer_held_in_this_test=True,
    timing='One declared SSI word event per existing source-system GPU IRQ2 tick; DSP timer2 every fourth word. This is host-supplied timing, not a Jaguar global cycle scheduler.',
    audio_scope='All133 DAC PCM pairs are silent. Active mixer/interrupt execution is verified; audible music, sound assets, playback timing and all audio paths are not proved.',
    startup_assets_reads=12, startup_assets_bytes=758846, source_created_contexts=21,
    video_events_held=True, synchronous_GPU_and_blitter_services=True,
    BIOS_file_adapters_and_source_DD40_export_retained=True,
    no_CPU_RAM_reset_after_startup=True, no_original_world_snapshot_or_later_pose_injections=True,
    accepted_held_DSP_entry_and_directional_reports_preserved=True,
    new_training=False, local_model_authored_new_C=False, whole_game_complete=False,
    remaining_work=['ordinary authenticated boot','global CD/video/GPU/DSP cycle scheduling','source-triggered audible sound/music','remaining helpers/scenes','physical controllers/scanout','full C playability'])
save(out / 'report.json', result)
save(ROOT / 'verification/entry-source-music-current.json', result)
compact = dict(report=str(out / 'report.json'), kind='Separate source-entry test with active source DSP mixer and declared events',
    world_returns_each_run=120, input_CPU_instructions=1304742, control_CPU_instructions=1297706,
    DSP_instructions_each_run=14692, SSI_words_each_run=133, timer2_events_each_run=34,
    native_C_CPU_RAM_context_GPU_DSP_DAC_PCM_match=True, source_DSP_held=False, video_held=True,
    input_end_X=9376, input_end_Z=40092, control_end_Z=40096, nonzero_PCM_pairs=0,
    audible_music_verified=False, global_cycle_schedule_verified=False, whole_game_playable=False,
    timing=result['timing'], remaining_work=result['remaining_work'])
installed = Path.home() / '.lmstudio/local-ai-lab'
for root in [ROOT, installed]:
    session = Path(read(root / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    path = session / 'emulator-runtime/summary.json'
    summary = read(path)
    summary['firmware_bootstrap_DSP_progress']['source_stage_loading']['entry_active_source_DSP_comparison'] = compact
    save(path, summary)
inputs += [ROOT / 'scripts/check_biwn_entry_natural_task_rounds.py', ROOT / 'scripts/biwn_music_engine_runtime.py', Path(__file__),
    ROOT / 'projects/black-ice-white-noise/restoration/biwn_dsp_music_engine.c',
    ROOT / 'verification/BIWN-game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world/20261015T001755.513281Z/libscheduled-startup.dylib']
save(out / 'input-manifest.json', {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
(out / 'who-prompts-and-responses.txt').write_text('COORDINATOR: Codex integrated the existing checked C music engine into the source-derived DD40 startup and natural task test. The coordinator changed the harness and ran original/C comparisons; no model wrote new C code.\nCOMMANDS:\ncheck_biwn_entry_natural_task_rounds.py --rounds 120 --input-plan up-left --music-words --no-publish\ncheck_biwn_entry_natural_task_rounds.py --rounds 120 --input-plan none --music-words --no-publish\n\nRESULT:\n'+json.dumps(result,indent=2)+'\n')
print(out)
