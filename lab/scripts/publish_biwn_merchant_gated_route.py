"""Publish the completed fresh-start merchant/elevator route and real outputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    job_path = ROOT / 'verification/merchant-gated-outdoor-route-current.json'
    job = json.loads(job_path.read_text())
    assert job['status'] == 'terminal_exact_merchant_elevator_outdoor_CPU_GPU_DSP_IRQ_match'
    out = Path(job['directory'])
    comparison = json.loads(Path(job['comparison']).read_text())
    assert comparison['status'] == 'CPU_GPU_DSP_frame_comparison_pass'
    assert all(comparison['checks'].values()) and all(job['semantic_milestone_checks'].values())
    gate = job['exact_unpatched_merchant_gate']
    assert gate['actual_RAM_sha256'] == gate['expected_RAM_sha256']
    assert gate['actual_machine_sha256'] == gate['expected_machine_sha256']
    assert gate['before_frame'] == 23539 and not gate['state_restored'] and not gate['memory_injected']
    report = json.loads((out / 'C/report.json').read_text())
    assert report['warm_original_frames'] == 0 and report['restored_original_checkpoint'] is None
    assert report['original_CPU_instructions'] == report['rejected_CPU_instructions'] == 0
    for key in ['GPU_counts', 'DSP_counts']:
        assert comparison[key]['Owned'] > 0 and comparison[key]['Original'] == comparison[key]['Rejected'] == 0
    irq = job['source_IRQ']
    assert irq['source']['errors'] == 0
    for key in ['core', 'selection']:
        assert irq[key]['Owned'] > 0 and irq[key]['Original'] == irq[key]['Rejected'] == 0
    for name, expected in job['hashes'].items():
        assert sha(Path(name)) == expected, name
    gpu = json.loads(Path(report['regular_GPU_report']).read_text())
    states = []
    for frame, expected in [(23538, (2, 2, 314)), (23698, (2, 0, 312)), (24738, (1, 0, 312))]:
        ram = (out / f'C/frame-{frame}-RAM.bin').read_bytes()
        get = lambda address, width=2: int.from_bytes(ram[address:address + width], 'big')
        assert (get(0x49c60), get(0x49c62), get(0x49c64)) == expected
        states.append(dict(frame=frame, mode=expected[0], floor=expected[1], retained_scene_index=expected[2],
                           X=get(0x49c50, 4), Z=get(0x49c56, 4)))
    pcm = Path(report['PCM_capture'])
    samples = np.memmap(pcm, mode='r', dtype='<i2')
    nonzero = np.flatnonzero(samples)
    assert len(nonzero) == report['audio']['nonzero_samples'] > 0
    # WAV requires an integer rate. This is the rounded declared NTSC frontend
    # rate used by the earlier original merchant recording, without resampling.
    prior_audio = ROOT / 'verification/normal-merchant-dialogue-current.json'
    rate = json.loads(prior_audio.read_text())['audio_capture']['declared_rate']
    assert rate == 48044
    first_pair = int(nonzero[0]) // 2
    start = max(0, first_pair - rate // 4)
    stop = min(len(samples) // 2, start + rate * 6)
    excerpt = samples[start * 2:stop * 2].tobytes()
    reference = Path(comparison['reference']) / 'frontend-PCM.s16le'
    with reference.open('rb') as stream:
        stream.seek(start * 4)
        assert stream.read(len(excerpt)) == excerpt
    audio_path = out / 'merchant-source-audio-excerpt.wav'
    with wave.open(str(audio_path), 'wb') as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(excerpt)
    audio = dict(relative_WAV='verified-previews/merchant-source-audio.wav',
                 source_PCM=str(pcm), source_PCM_sha256=sha(pcm), WAV_sha256=sha(audio_path),
                 first_nonzero_source_frame=next(row['frame'] for row in report['frames'] if row['audio']['nonzero_samples']),
                 total_nonzero_channel_samples=len(nonzero), first_nonzero_PCM_frame=first_pair,
                 excerpt_start_PCM_frame=start, excerpt_stereo_frames=stop - start,
                 integer_WAV_rate=rate, rate_source=str(prior_audio),
                 peak_absolute=int(np.max(np.abs(samples.astype(np.int32)))),
                 full_scale_channel_samples=int(np.count_nonzero((samples == -32768) | (samples == 32767))),
                 normalization_or_resampling=False, original_excerpt_bytes_match=True,
                 physical_audio_verified=False, speech_content_transcribed=False)
    now = datetime.now(timezone.utc)
    proof_path = ROOT / 'verification/merchant-gated-full-route-verdict-current.json'
    proof = dict(status='fresh_start_merchant_two_elevator_floors_outdoor_source_match',
                 recorded_at=now.isoformat(), directory=str(out), frames=24738,
                 comparison=job['comparison'], comparison_recorded_at=comparison['recorded_at'],
                 all_comparison_gates_passed=True, CPU_instructions=comparison['owned_CPU_instructions'],
                 GPU_counts=comparison['GPU_counts'], GPU_source_instructions=gpu['C_source_instructions'],
                 GPU_counter_units='Owned counts are callback bundles, including delayed pairs; source instruction count is separate.',
                 DSP_counts=comparison['DSP_counts'], source_IRQ_selection=irq['selection'], source_IRQ_entry=irq['core'],
                 exact_unpatched_merchant_gate=gate, captured_states=states,
                 continuous_merchant_elevator_outdoor_chain_verified=True,
                 original_warm_frames=0, initial_checkpoint_restored=False,
                 scene_RAM_transplant=False, player_relocation=False, repair_bytes=18,
                 repair_applied_before_frame=23539, unmodified_program_through_frame=23538,
                 audio=audio, native_keyboard_verified=False, physical_audio_verified=False,
                 whole_game_complete=False, default_preview_changed=False,
                 remaining_providers=['Original IRQ queue/device line', 'Original device ACK/vector resolution',
                                      'Host CPU commit/prefetch and cycle charge', 'Firmware HLE/CD bootstrap',
                                      'Original Object Processor and hardware devices'],
                 raw_remaining_providers=comparison['remaining_providers'],
                 raw_provider_label_correction='Raw comparator lists OriginalIRQSelection generically. Actual selector counts show zero original/rejected selection; queue/device-line/ACK/commit/cycle services remain original.',
                 authorship='Coordinator integration, exact-byte variant bridge and verification; local27B selector body unchanged except fence removal. No new weights or cloud agents.',
                 scope='Independent source start atframe1, zero original warmup and no checkpoint restore. Exact unmodified merchant RAM+whole machine reached before23539 without injection. Sole18byte marker-scan repair then applied to both original and source executions. Ordinary recorded inputs descend two floors and exit outdoors. All CPUbefore/cycle traces, every frameCPU/RAM/video/PCM and complete final machine match. CPU/GPU/DSP/IRQ selection+entry owner fallbacks are zero. Nonzero captured PCM is byte-identical; physical playback/speech content is unverified. GPU/DSP per-instruction state streams, broader gameplay, remaining device providers, native Chat/keyboard and standalone execution remain outside this finite-route proof.')
    proof_path.write_text(json.dumps(proof, indent=2) + '\n')
    png = out / 'C/final-frame.png'
    assert png.read_bytes() == (Path(comparison['reference']) / 'final-frame.png').read_bytes()
    caption = ('Checked fresh-start merchant/elevator/outdoor route:24,738frames, zero original warmup and no checkpoint restore. '
               'The source run reaches the exact unmodified merchant state, then the sole18-byte repair is applied before23539 '
               'to both executions. Ordinary recorded buttons descend two elevator floors and exit outdoors. CPU instruction states/costs, '
               'all frameRAM/video/PCM and final machine match original execution. Source CPU/GPU/DSP and interrupt selection/entry '
               'have zero owner fallback. Captured PCM includes nonzero audio; physical playback is unverified. This is recorded output. '
               'Original IRQ/device/HLE/Object Processor services remain; native Chat/input and standalone play are unverified.')
    manifest = dict(relative_png='verified-previews/latest-checked-scene.png', png_sha256=sha(png),
                    source_frame=24738, checked_frames=24738, scene_mode=1, retained_scene_index=312,
                    scene_RAM_transplant=False, player_position_injected=False, source_report=str(proof_path),
                    comparison=job['comparison'], native_Chat_verified=False, live_gameplay=False,
                    whole_game_complete=False, verified_caption=caption)
    backup = ROOT / 'config-backups' / now.strftime('%Y%m%dT%H%M%S.%fZ') / 'before-fresh-merchant-route-output'
    for folder, name in [(ROOT, 'workspace'), (RUNTIME, 'runtime')]:
        destination = backup / name
        destination.mkdir(parents=True)
        for filename in ['latest-scene.json', 'latest-checked-scene.png']:
            shutil.copy2(folder / 'verified-previews' / filename, destination / filename)
        shutil.copy2(png, folder / 'verified-previews/latest-checked-scene.png')
        shutil.copy2(png, folder / 'verified-previews/fresh-merchant-elevator-outdoor.png')
        shutil.copy2(audio_path, folder / audio['relative_WAV'])
        (folder / 'verified-previews/latest-scene.json').write_text(json.dumps(manifest, indent=2) + '\n')
        (folder / 'verified-previews/merchant-source-audio.json').write_text(json.dumps(audio, indent=2) + '\n')
    print(json.dumps(dict(status=proof['status'], frames=proof['frames'], CPU_instructions=proof['CPU_instructions'],
                          source_IRQ_entry=proof['source_IRQ_entry'], audio=audio, proof=str(proof_path))))


if __name__ == '__main__':
    main()
