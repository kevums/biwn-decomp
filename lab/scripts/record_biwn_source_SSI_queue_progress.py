"""Record source clock programming in place of an initial host queue rebuild."""
import collections
import hashlib
import json
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'verification/source-SSI-queue-progress'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
prefix=Path((ROOT/'runs/captured-source-single-SSI-chain.log').read_text().splitlines()[0])
export=Path((ROOT/'runs/source-single-SSI-export-check.log').read_text().splitlines()[0])
source=read(prefix/'report.json');checked_export=read(export/'report.json')
assert source['single_SSI_chain_diagnostic'] and not source['initial_queue_rebuilt_at_restore']
assert source['native_instructions']==10375 and source['full_CPU_RAM_logical_GPU_DSP_checked_hardware_match']
assert checked_export['source_directory']==str(prefix)
def queue_ids(b):
    return collections.Counter(struct.unpack_from('=BBid',b,12+32*14+i*14)[1]for i in range(32)if b[12+32*14+i*14])
for mode in ['native','C']:
    continuation=read(prefix/(mode+'-continuation.json'))
    assert continuation['single_SSI_chain_diagnostic'] and continuation['source_SCLK_reschedules']==1
    assert queue_ids((prefix/(mode+'-event-queue.bin')).read_bytes())=={3:1,4:1,5:1}
assert(prefix/'native-event-queue.bin').read_bytes()==(prefix/'C-event-queue.bin').read_bytes()
rows,points,inputs={}, {},[prefix/'report.json',export/'report.json']
for name in ['up-left','control']:
    folder=Path((ROOT/f'runs/entry-source-SSI-{name}-120.log').read_text().splitlines()[0]);d=read(folder/'report.json')
    assert d['actual_pinned_JERRY_event_queue_used'] and d['source_single_SSI_chain_diagnostic'] and not d['initial_JERRY_queue_normalized']
    assert d['all_world_return_checkpoints_equal'] and not d['global_cycle_scheduling_verified']
    points[name]=read(folder/'native-world-return-checkpoints.json');assert points[name]==read(folder/'C-world-return-checkpoints.json')
    music=read(folder/'native-music.json');events=read(folder/'native-JERRY-events.json')
    assert music==read(folder/'C-music.json') and events==read(folder/'C-JERRY-events.json') and not events['errors']
    counts=collections.Counter(i[0]for e in events['events']for i in e['IRQs']);assert counts=={1:34111,2:2046}
    assert sum(c['instructions']for c in music['calls'])==3177562
    assert all(not any(e['PCM'])for e in events['events']) and d['results'][1]['C_original_CPU_attempts']==0
    for mode in ['native','C']:
        a=(folder/(mode+'-initial-event-queue.bin')).read_bytes();b=(folder/(mode+'-setup-event-queue.bin')).read_bytes()
        assert a==b and queue_ids(a)=={3:1,4:1,5:1}
    assert(folder/'native-initial-event-queue.bin').read_bytes()==(prefix/'native-event-queue.bin').read_bytes()
    startup=read(folder/'native-startup.json');player=points[name][-1]['player']
    rows[name]=dict(report=str(folder/'report.json'),world_returns=120,
        post_DD40_CPU_instructions=startup['checks']['native_CPU_steps']+d['results'][0]['processor_instructions'],
        source_DSP_instructions=3177562,SSI_words=34111,timer1_DSP_IRQ2_events=2046,total_JERRY_events=36157,
        elapsed_JERRY_us=events['elapsed_us'],all_original_C_CPU_RAM_stack_devices_contexts_GPU_DSP_DAC_event_queue_timeline_checks_equal=True,
        host_initial_queue_rebuild=False,queue_at_adoption_unchanged=True,nonzero_PCM_pairs=0,final_X=player['0x49c50'],final_Z=player['0x49c56'])
    inputs += [folder/'report.json',folder/'native-JERRY-events.json',folder/'C-JERRY-events.json',folder/'native-initial-event-queue.bin']
assert rows['up-left']['final_Z']==40092 and rows['control']['final_Z']==40096
assert points['up-left'][:5]==points['control'][:5] and points['up-left'][5]!=points['control'][5]
build=read(ROOT/'verification/BIWN-SSI-chain-candidate.json');assert sha(Path(build['core_path']))==build['core_sha256']
build.update(status='opt_in_source_programmed_SSI_queue_checks_passed_not_promoted',full_tests_exit_code=0,
    private_ROM_audio_clipping_and_presence_sentinels='Skipped; optional private ROMs absent, not passes.',RetroArch_validation='Pending, GUI unavailable.')
save(Path(build['directory'])/'build.json',build);save(ROOT/'verification/BIWN-SSI-chain-candidate.json',build)
result=dict(status='source_programmed_SSI_queue_and_entry_task_events_native_C_match_without_initial_queue_rebuild',directory=str(out),runs=rows,
    source_4000_to_DD40=dict(report=str(prefix/'report.json'),original_CPU_instructions=10375,actual_source_SCLK_reschedules=1,native_C_CPU_RAM_GPU_DSP_devices_traces_match=True),
    checked_DD40_context_export=str(export/'report.json'),DD40_export_restore_boundary_remains=True,
    uninterrupted_4000_to120_world_returns_verified=False,
    initial_queue_rebuild_removed=True,opt_in_single_SSI_chain_peripheral_model_required=True,
    correction='The diagnostic model removes duplicate pending SSI callbacks only when the actual source programs SCLK. Default disabled. No queue rebuild runs at restore/adoption; no device registers, CPU/RAM or waveform are supplied by this correction.',
    phase_difference='The source-programmed first SSI deadline is22.675737us, inherited from prior slave-mode programming before SMODE changes; the previous host-rebuilt queue started at64.98462294144us. New120return run therefore has34111 rather than34110SSI events. This is observed pinned-model behavior, not a physical-phase accuracy claim.',
    remaining_controls='Captured diagnostic firmware/4000 and source-derived DD40 export; opt-in SSI-chain and other firmware/CD/SSI/GPU-stack diagnostics; BIOS303C/3042 asset adapters,TOCorigin13227/captured674bytephase,source GPU IRQ2 events and16666.6667us host world-to-JERRY time slices;synchronous GPU/blitter;main/video/OP/CD global events remain held or separately provided.',
    new_training=False,new_local_model_C_authorship=False,ordinary_boot_verified=False,global_cycle_scheduling_verified=False,audible_music_verified=False,whole_game_complete=False,
    diagnostic_core=build,remaining_work=['Remove captured/export/provider inputs through source boot and global CPU/GPU/DSP/CD/video/OP scheduling.','Validate SSI model/phase and audible source audio on hardware/general emulator paths.','Remaining helpers/scenes, physical controllers/scanout and full C playability.'])
save(out/'report.json',result);save(ROOT/'verification/source-SSI-queue-current.json',result)
compact=dict(report=str(out/'report.json'),kind='Separate source-programmed SSI queue test; no host initial queue rebuild',
    source_4000_to_DD40_CPU_instructions=10375,DD40_export_restore_boundary_remains=True,
    world_returns_each_run=120,DSP_instructions_each_run=3177562,SSI_words_each_run=34111,timer1_DSP_IRQ2_each_run=2046,
    total_JERRY_events_each_run=36157,all_native_C_checked_states_queues_timeline_match=True,
    source_SCLK_reschedules=1,initial_queue_rebuild_required=False,opt_in_single_SSI_chain_model_required=True,
    CPU_world_JERRY_time_slices_host_supplied=True,video_held=True,all_PCM_silent=True,normal_boot_or_global_cycles_verified=False,full_playability=False,
    remaining_controls=result['remaining_controls'],remaining_work=result['remaining_work'])
for root in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
    session=Path(read(root/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';d=read(p)
    d['firmware_bootstrap_DSP_progress']['source_stage_loading']['source_programmed_SSI_queue_comparison']=compact;save(p,d)
manual=ROOT/'tools/jaguar-technical-manual/original-JTRM-rev8.pdf'
for page in [91,92]:
    temporary=ROOT/f'tmp/pdfs/SSI-manual-check/page-{page:03d}.png'
    if temporary.exists():shutil.copy2(temporary,out/f'manual-page-{page}.png')
    else:
        subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1400','-singlefile','-png',str(manual),str(out/f'manual-page-{page}')],check=True,capture_output=True)
save(out/'manual-review.json',dict(source=str(manual),sha256=sha(manual),printed_pages=[91,92],visual_review=True,
    supports='SCLK divisor formula and SMODE internal serial clock/word-strobe controls.',does_not_prove='Hardware phase when SCLK/SMODE change, diagnostic duplicate-removal implementation or complete physical timing.'))
inputs += [ROOT/'scripts/build_biwn_SSI_chain_core.py',ROOT/'scripts/check_biwn_captured_source_music_entry.py',ROOT/'scripts/check_biwn_captured_entry_exports.py',ROOT/'scripts/check_biwn_entry_natural_task_rounds.py',Path(__file__),Path(build['core_path']),Path(build['directory'])/'full-test.log',manual]
save(out/'input-manifest.json',{str(p):sha(p)for p in inputs})
(out/'who-prompts-and-responses.txt').write_text('COORDINATOR: Codex read/rendered Jaguar TRM pages91/92, added an opt-in diagnostic single SSI chain on source SCLK writes, checked original/C source4000-toDD40, cross-process owned contexts and120world-return input/control tests. No model wrote new C code and no weights were trained. The DD40 export/restore remains a boundary; this is not a continuous normal boot.\n\nRESULTS:\n'+json.dumps(result,indent=2)+'\n')
print(out)
