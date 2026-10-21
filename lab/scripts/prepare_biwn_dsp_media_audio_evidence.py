"""Publish the checked source DSP sample engine and explicitly synthetic preview."""
import hashlib
import json
import shutil
import struct
import wave
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    now=datetime.now(timezone.utc).isoformat();report=read(ROOT/'verification/biwn-dsp-media-audio-checks.json');guards=read(ROOT/'verification/biwn-dsp-media-audio-guards.json')
    directory=Path(report['directory']);assert read(directory/'status.json')['status']=='terminal_pass'
    assert [report[k] for k in ['cases','SSI_events','word_strobes','DSP_source_instructions']]==[31,4427,4427,179020]
    assert report['source_instruction_coverage']==[113,118] and guards['host_guards']==19 and len(guards['diagnostics'])==9
    assert report['unexercised_instructions']==['0xf1b01a','0xf1b130','0xf1b132','0xf1b134','0xf1b136']
    assert sha(ROOT/'scripts/check_biwn_dsp_media_audio.py')==report['test_script_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in report['source_sha256'].items():assert sha(source/name)==digest
    assert report['source_sha256']==guards['source_sha256']
    fixture=read(directory/'fixtures.json')[-1];assert len(fixture['PCM_pairs'])==3196
    preview=ROOT/'verified-previews/C-DSP-synthetic-test.wav';shutil.copy2(directory/'synthetic-C-DSP-word-strobes.wav',preview)
    with wave.open(str(preview),'rb') as w:
        assert (w.getnframes(),w.getframerate(),w.getnchannels(),w.getsampwidth())==(3196,31960,2,2)
        data=w.readframes(3196)
    assert [list(pair) for pair in struct.iter_unpack('<hh',data)]==fixture['PCM_pairs']
    samples=struct.unpack('<6392h',data);assert min(samples)==-25600 and max(samples)==25600
    checkpoint=dict(recorded_at=now,status='source_DSP_media_audio_program_and_SSI_processing_native_C_match',
        cases=31,source_instruction_coverage=[113,118],normal_source_instructions=113,source_padding_NOPs=5,
        forced_padding_diagnostics_separate_from_normal_coverage=True,host_guards=19,separate_diagnostics=9,
        SSI_events=4427,word_strobes=4427,DSP_source_instructions=179020,
        idle_interrupt_positions=['F1B074 before OR','F1B076 after OR'],
        source_queue_wrap_sample_skip_stereo_output_shutdown_verified=True,
        all8496logical_DSP_bytes_and_main_RAM_DAC_state_compared_after_every_atomic_instruction_block=True,
        source_SSI_private_frame_and_mandatory_delays_compared=True,
        original_DSP_execution_on_C_side=False,source_code_modified=False,
        program_bank0=True,other_banks_IRQs_and_global_DSP_timing_verified=False,
        audio_playback_in_game_verified=False,movie_streaming_verified=False,physical_audio_capture=False,
        supplied_sample_buffers_and_word_clocks=True,new_components=1,published_components=139,
        processor_components=dict(CPU=125,GPU=13,DSP=1),local_model_instruction_bodies=171,new_local_model_instruction_bodies=0,
        authorship='Coordinator source-specific static C and IRQ/driver interfaces, adapted from checked integer primitives; no new local-model code prompt or weight training.',
        report=str(ROOT/'verification/biwn-dsp-media-audio-checks.json'),guard_report=str(ROOT/'verification/biwn-dsp-media-audio-guards.json'),
        source_sha256=report['source_sha256'],whole_game_complete=False,playable=False,native_Chat_verified=False,
        synthetic_preview=dict(path=str(preview),relative_path='verified-previews/C-DSP-synthetic-test.wav',sha256=sha(preview),
            frames=3196,channels=2,sample_width_bytes=2,declared_sample_rate=31960,duration_seconds=0.1,
            amplitude_min=-25600,amplitude_max=25600,
            verified_caption='Synthetic test samples processed by the reconstructed C DSP sound program under declared word-clock events. This is a 0.1-second comparison preview, not recovered game audio, in-game playback or a physical capture.'),
        checked_answer='The source DSP sound program now executes as C: initialization, SSI interrupt frames, sample queues, sample skipping, stereo writes and shutdown match the original across 31 controlled cases and 4,427 word clocks. It exercised 113 caller-reached instructions; five padding NOPs were checked separately, with 19 error guards and nine diagnostics. Supplied test samples produce a matching synthetic preview; real movie streaming, in-game audio and physical timing remain unverified.',
        next_work=['Connect source movie/video state handlers and real disc audio buffers to the checked DSP program.',
            'Verify video GPU overlay, CPU/DSP/IRQ scheduling and source stop/reload lifetimes; preserve exact source frames.',
            'Continue merchant interactions, other tasks, boot/global GPU/object-processor scanout and visible native Chat.'])
    save(ROOT/'verification/DSP-media-audio-checkpoint.json',checkpoint)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json')
    assert validation['portable_C_component_count'] in [138,139]
    validation.update(portable_C_component_count=139,processor_component_counts=checkpoint['processor_components'],
        DSP_media_audio_checkpoint=checkpoint,latest_aggregate_update=now,
        component_count_scope='139 selected C components across scoped standalone and connected proofs, including one new source DSP sound program. Earlier world and media-setup checkpoints retain their original snapshots. Counts are not game-completion percentages.')
    save(session/'boot-slice-validation.json',validation)
    for path in [session/'emulator-runtime/summary.json']+[ROOT/name for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/requirements-audit.json']]:
        state=read(path);state['DSP_media_audio_checkpoint']=checkpoint
        if path.name=='requirements-audit.json':state.update(recorded_at_utc=now,
            this_goal_turn_classification='Progress: source DSP audio program/SSI frames/stereo output reconstructed and compared in31cases/4427word clocks;19guards and9separate diagnostics; full goal incomplete.',next_safe_work=checkpoint['next_work'])
        if path.name=='current-runtime-state.json':state.update(recorded_at=now,emulator_jobs='Terminal: DSP media audio comparisons and guards passed.')
        save(path,state)
    out=ROOT/'verification/DSP-media-audio-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');(out/'snapshot').mkdir(parents=True)
    files=[ROOT/'scripts/generate_biwn_dsp_media_audio.py',ROOT/'scripts/check_biwn_dsp_media_audio.py',ROOT/'scripts/check_biwn_dsp_media_audio_guards.py',
        ROOT/'scripts/prepare_biwn_dsp_media_audio_evidence.py',ROOT/'verification/biwn-dsp-media-audio-checks.json',ROOT/'verification/biwn-dsp-media-audio-guards.json',
        ROOT/'verification/DSP-media-audio-checkpoint.json',source/'biwn_dsp_media_audio.c',source/'biwn_dsp_media_audio.h',preview]
    for path in files:shutil.copy2(path,out/'snapshot'/path.name)
    save(out/'manifest.json',dict(recorded_at=now,files={str(p):sha(p) for p in files},checkpoint=checkpoint,
        preview_correction='Earlier40-clock preview used a wrong DAC holding-register offset. It is rejected as an audio preview. Current extraction uses source ABI offsets, reads the newly strobed ring pair and checks it against holding registers and both instruction implementations.',
        earlier_preview_rejected=str(ROOT/'verification/biwn-dsp-media-audio/20261014T092441.017395Z/synthetic-C-DSP-word-strobes.wav'),whole_goal_complete=False))
    note='BLACK ICE WHITE NOISE — C DSP SAMPLE ENGINE\n'+now+'\n\n'+checkpoint['checked_answer']+'\n\n'+(
        'VERIFICATION\nEvery atomic source instruction block compares all 8,496 logical DSP bytes (both register banks, flags/control/accumulator/matrix/divider fields and 8 KB RAM), main RAM and DAC state. Taken branches include their mandatory delay instruction. C emits the source SSI private stack frame. C execution advances no original DSP instruction counter. Normal coverage excludes the alignment NOP and four post-shutdown NOPs; forced diagnostics cover those separately.\n\n'
        'PREVIEW\n'+checkpoint['synthetic_preview']['verified_caption']+'\n'+str(preview)+'\n\n'
        'LIMITS\nBank0, source entrypoints, supplied chunks/rates and explicit word clocks/SSI events. Shared pinned DAC/bus model; no real movie stream, complete game audio, global timing, other IRQ/bank execution or physical capture. The game remains unfinished.\n\n'
        'WHO / PROMPTS\nCoordinator authored the static C, IRQ interface, comparisons and guard tests. No new local-model code prompts or training in this implementation. Previous 171 accepted local-model instruction bodies remain unchanged. Selected count: 139 (125 CPU / 13 GPU / 1 DSP), not a completion percentage.\n\n'
        'PRIOR WORLD TEST\nFour controlled loading/world/input/NPC/renderer cases remain separate: 28 world updates/polls, 20 NPC iterations, 112 GPU submissions and 24 sprite decodes. Media setup separately passed18cases/all59instructions/16guards. Those proofs are retained.\n\n'
        'NEXT\n'+'\n'.join(checkpoint['next_work'])+'\n\nAUDIT\n'+str(out)+'\nFull goal active/incomplete.\n')
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(note);(out/'readable-results.txt').write_text(note)
    save(ROOT/'verification/DSP-media-audio-review.json',dict(recorded_at=now,directory=str(out)))
    print(json.dumps(dict(audit=str(out),selected_components=139,DSP_programs=1,source_instruction_coverage=[113,118],synthetic_preview=str(preview),whole_goal_complete=False)))


if __name__=='__main__':main()
