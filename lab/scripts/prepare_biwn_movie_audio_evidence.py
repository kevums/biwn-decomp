"""Publish source movie parser/first audio enqueue and direct-trap follow-ons."""
import json,hashlib,shutil,wave
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    names=['BIWN-movie-CPU','BIWN-movie-CPU-guards','BIWN-movie-audio-integration','BIWN-movie-trap']
    reports={n:read(ROOT/'verification'/f'{n}.json') for n in names}
    for r in reports.values():assert read(Path(r['directory'])/'status.json')['status']=='terminal_pass'
    cpu=reports[names[0]];guards=reports[names[1]];integration=reports[names[2]];trap=reports[names[3]]
    assert (cpu['cases'],cpu['states_per_case'],cpu['source_movie_instruction_coverage'],guards['guards'])==(12,8,[319,519],24)
    assert len(integration['cases'])==6 and integration['word_clocks']==4736 and integration['source_CPU_states']==48
    assert (trap['cases'],trap['guards'])==(160,15)
    assert cpu['source_sha256']==guards['source_sha256']==integration['CPU_controller_source_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for r in [cpu,trap]:
        for n,digest in r['source_sha256'].items():assert sha(source/n)==digest
    for n,digest in integration['DSP_source_sha256'].items():assert sha(source/n)==digest
    preview=ROOT/'verified-previews/C-movie-CPU-to-DSP-message-58-first-chunk.wav'
    shutil.copy2(integration['cases'][0]['wav'],preview);assert sha(preview)==integration['cases'][0]['wav_sha256']
    with wave.open(str(preview),'rb') as w:assert (w.getnframes(),w.getframerate(),w.getnchannels(),w.getsampwidth())==(4096,21868,2,2)
    now=datetime.now(timezone.utc).isoformat()
    checkpoint=dict(recorded_at=now,status=integration['status'],
        checked_answer='The reconstructed movie CPU now parses actual supplied FILM/STAB bytes and enqueues the first real audio chunk directly into shared C DSP RAM. Six source CPU-to-DSP cases match the original output. The movie caller direct TRAP0 frame also matches separately. Complete streaming/video/dialogue and in-game playback remain unfinished.',
        source_CPU_cases=12,source_CPU_state_dispatches=96,source_CPU_instruction_coverage=[319,519],source_CPU_guards=24,
        source_audio_integration_cases=6,source_audio_integration_state_dispatches=48,word_clocks=4736,
        direct_TRAP_cases=160,direct_TRAP_guards=15,
        actual_disc_sample_bytes=True,E902_sample_pointer_or_length_replaced_by_host=False,
        rate_behavior='DSP boots before parsing: R23 retains source E840 increment0481DB08; E8E2 updates its RAM increment field to04924924. Source behavior preserved under this declared schedule.',
        comparison='Native/Unicorn/C parser: full CPU/SR/USP/SSP, RAM, hardware/cartridge and Unicorn/C ordered bus. CPU-to-DSP: same CPU/RAM/hardware with logical8496DSPbytes, then DSP/RAM/DAC/PCM/source instruction count after every clock boundary.',
        source_C_controller_generated_instructions=519,source_C_controller_unexercised_instructions=200,
        declared_providers=['Host delivers128KBof actual disc bytes between states0/1.','BIOS seek/progress return ABI; original firmware/physical seek mapping not verified.','State4 gets an explicit clock change; SSI/word clocks are supplied.'],
        video_GPU_executed=False,complete_movie_caller_integrated=False,BIOS_streaming_verified=False,full_dialogue_playback_verified=False,in_game_playback_verified=False,
        native_Chat_verified=False,whole_game_complete=False,
        implementation_authorship='Coordinator authored static movie CPU reconstruction, direct trap bridge, integration and guards. Existing DSP code unchanged. No new local-model code/training; prior171accepted local instruction bodies retained.',
        previously_selected_component_registry=139,new_components_added_to_registry=0,
        preview=dict(path=str(preview),sha256=sha(preview),frames=4096,declared_Hz=21868,seconds=4096/21868,label='First real audio chunk from message58 via source C CPU-to-DSP under declared test events; not complete dialogue or in-game capture.'),
        reports={n:str(ROOT/'verification'/f'{n}.json') for n in names},
        next_work=['Validate movie seek/progress mapping and integrate source caller/scheduler with nonoverlapping stacks/buffers.',
                   'Reconstruct/check movie video GPU and CPU video interfaces, then source reload/wrap/stop and whole dialogue playback.',
                   'Continue the remaining game tasks, boot/runtime/scanout and visible LM Studio Chat validation.'])
    save(ROOT/'verification/movie-audio-CPU-checkpoint.json',checkpoint)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    path=session/'emulator-runtime/summary.json';summary=read(path);summary['movie_audio_CPU_checkpoint']=checkpoint;save(path,summary)
    out=ROOT/'verification/movie-audio-CPU-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');(out/'snapshot').mkdir(parents=True)
    files=[*[source/n for n in ['biwn_movie_cpu.c','biwn_movie_cpu.h','biwn_movie_trap.c','biwn_movie_trap.h']],
        *[ROOT/'scripts'/n for n in ['generate_biwn_movie_cpu.py','check_biwn_movie_cpu.py','check_biwn_movie_cpu_guards.py','check_biwn_movie_audio_integration.py','check_biwn_movie_trap.py']],Path(__file__),
        *[ROOT/'verification'/f'{n}.json' for n in names],ROOT/'verification/movie-audio-CPU-checkpoint.json',preview]
    snapshots=[]
    for p in files:
        target=out/'snapshot'/p.name;shutil.copy2(p,target);snapshots.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(recorded_at=now,checkpoint=checkpoint,files=snapshots,
        failed_test_assumptions_corrected=['The first parser preflight incorrectly expected a zero marker. The source third record field is its actual16-longword sync marker (7FFFFFFF/80000000..4); bytes are preserved.',
            'The first direct-trap test incorrectly expected its original supervisor PC bytes to persist. The source dispatcher reuses that frame for the selected context; outgoing D416 remains in its TCB. Native/C CPU and RAM already matched.']))
    (out/'who-and-prompts.txt').write_text('Coordinator authored and reviewed the source movie CPU, direct TRAP bridge, native/Unicorn/C tests and CPU-to-DSP integration.\nNo new local-model code prompts, training, model changes or defaults. Prior171accepted local-model instruction bodies unchanged.\nFirmware/data delivery and clock events remain declared test providers. No video GPU/helper was returned as if completed.\nNative LM Studio Chat remains unverified while locked; SDK questions are audited separately.\n')
    save(ROOT/'verification/movie-audio-CPU-review.json',dict(directory=str(out),status='published',checkpoint=checkpoint))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — SOURCE MOVIE CPU TO C DSP\n'+now+'\n\n'+checkpoint['checked_answer']+'\n\n12native/Unicorn/C cases:8state dispatches each,319/519movieinstructions,24guards. Six real first-audio enqueue integrations:48state dispatches/4,736clocks. Direct sourceTRAP0:160cases/15guards; genuineD416return frame, noDF60wrapper.\n\n'+checkpoint['rate_behavior']+'\n\nOriginalDSPinstructions onCpath:0. Shared C DSP RAM receives the source E902 pointer/length without host replacement. Whole game incomplete. Source movie caller/videoGPU/firmware stream/timing remain separate.\n\nCoordinator-authored follow-on; no new local-model code/training. Previously selected139component registry unchanged; these follow-ons retain scoped checks.\n\nPreview: '+str(preview)+'\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(checkpoint['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),preview=str(preview))))

if __name__=='__main__':main()
