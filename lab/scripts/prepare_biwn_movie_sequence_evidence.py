"""Publish all-frame retained C GPU comparisons and silent lossless previews."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    report=read(ROOT/'verification/BIWN-movie-sequence-GPU-C.json');guards=read(ROOT/'verification/BIWN-movie-sequence-GPU-guards.json');export=read(ROOT/'verification/BIWN-movie-sequence-export.json')
    assert read(Path(report['directory'])/'status.json')['status']=='terminal_pass'
    assert (report['frames'],report['key_frames'],report['delta_frames'],report['GPU_commands'],report['observed_code_instructions'])==(763,53,710,1526,252)
    assert report['C_GPU_checks']['retained_C_GPU_architecture'] and report['C_GPU_checks']['commands']==1526
    assert guards['host_guards']==18 and guards['source_sha256']==report['C_GPU_checks']['source_sha256']
    assert export['source_report_sha256']==sha(ROOT/'verification/BIWN-movie-sequence-GPU-C.json') and export['total_source_frames']==763
    for n,digest in report['C_GPU_checks']['source_sha256'].items():assert sha(ROOT/'projects/black-ice-white-noise/restoration'/n)==digest
    clips=[]
    for c in export['clips']:
        assert sha(Path(c['path']))==c['sha256'] and c['decoded_RGB_and_timing_match_all_source_frames']
        clips.append({k:c[k] for k in ['message_id','source_frames','duration_ms','source_nominal_Hz','path','sha256','bytes','audio_included','lossless_RGB']})
    now=datetime.now(timezone.utc).isoformat()
    checkpoint=dict(recorded_at=now,status=report['status'],
        checked_answer='The retained C GPU decoder now reproduces all763video samples across the six merchant dialogue movies:53keyframes/710deltaframes. All1526source-prepared commands match the original, preserving C register/codebook state between commands. Six silent lossless animation previews are available. Complete game movie streaming/audio synchronization and C CPU wrappers remain unfinished.',
        movies=6,frames=763,key_frames=53,delta_frames=710,GPU_commands=1526,source_instruction_coverage=[252,252],host_guards=18,
        source_instructions_including_mandatory_delays=report['source_instructions'],
        C_GPU_state_retained_between_commands=True,allowed_source_CPU_GPU_RAM_update='F039F0..F03A18 command/argument mailbox only',
        matched='Every command: all4396logicalGPUbytes, full2MBRAM, exact outerPC hash/count, inline delay count, CPU interrupt registers/stack and serialized DSP/TOM/JERRY/DAC/cartridge state. All763C-produced rawCRYframes match original. No original GPU instruction runs on the C path.',
        source_CPU_video_wrappers_native=True,source_GPU_startup_relocation_native=True,source_CPU_wrappers_C_verified=False,
        initialization='Initial fixture uses the public save/load normalization so DAC ratio agrees with suppliedSMODE/SCLK. DAC state is compared; no mismatching field is masked.',
        code_scope='252observed CRY code/delay addresses for commands0/1/7/8. Other source addresses remain BAD_PC; complete overlay/RGB/other movie sets not claimed.',
        preview_format='Silent lossless animatedWebP,224x180, nominal source15fps from timescale600/duration40; decode roundtrip checks all frames and timestamps.',
        clips=clips,physical_timing_verified=False,BIOS_streaming_verified=False,audio_synchronization_verified=False,in_game_playback_verified=False,
        native_Chat_verified=False,whole_game_complete=False,
        implementation_authorship='Coordinator authored252staticGPUblocks, source comparisons and exporters; no new local-model code/training. Prior171local-model instruction bodies retained.',
        previously_selected_component_registry=139,new_components_added_to_registry=0,
        report=str(ROOT/'verification/BIWN-movie-sequence-GPU-C.json'),guards=str(ROOT/'verification/BIWN-movie-sequence-GPU-guards.json'),export_report=str(ROOT/'verification/BIWN-movie-sequence-export.json'),
        next_work=['Port CPU video/STOP/IRQ and startup relocation interfaces, then connect the movie controller and source scheduler.',
                   'Validate disc seek/progress mapping and source buffer reload/wrap/stop lifetimes; connect all real audio chunks with source synchronization.',
                   'Continue remaining game tasks/boot/scanout and native LM Studio Chat verification.'])
    save(ROOT/'verification/movie-sequence-video-checkpoint.json',checkpoint)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);path=session/'emulator-runtime/summary.json';summary=read(path);summary['movie_sequence_video_checkpoint']=checkpoint;save(path,summary)
    out=ROOT/'verification/movie-sequence-video-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');(out/'snapshot').mkdir(parents=True)
    files=[*[ROOT/'scripts'/n for n in ['probe_biwn_movie_sequence.py','generate_biwn_movie_sequence_GPU.py','check_biwn_movie_sequence_GPU.py','check_biwn_movie_sequence_GPU_guards.py','export_biwn_movie_sequences.py']],Path(__file__),
        *[ROOT/'projects/black-ice-white-noise/restoration'/n for n in ['biwn_movie_sequence_GPU.c','biwn_movie_sequence_GPU.h']],
        *[ROOT/'verification'/n for n in ['BIWN-movie-sequence-GPU-C.json','BIWN-movie-sequence-GPU-guards.json','BIWN-movie-sequence-export.json','movie-sequence-video-checkpoint.json']],*[Path(c['path']) for c in clips]]
    snapshots=[]
    for p in files:
        target=out/'snapshot'/p.name;shutil.copy2(p,target);snapshots.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(recorded_at=now,checkpoint=checkpoint,files=snapshots,
        prior_failed_fixture='First GPU/RAM/trace/CPU comparison matched but fullDAC ratio differed because DACStateLoad derives its provisional reset ratio. Coherent initial fixture fixed this; no DAC fields excluded.',
        earlier_checkpoint_pointer_repair=str(ROOT/'verification/movie-sequence-checkpoint-publishing-fix.json')))
    (out/'who-and-prompts.txt').write_text('Coordinator: native retained-state probes,252staticC GPU blocks, all1526comparison boundaries,18guards and six lossless animation exports.\nLocal model: no new code prompts or training in this implementation; separate assistant questions/prompts are audited independently.\nNative CPU wrappers/STOP/IRQ and GPU startup relocation prepare the declared test; C GPU registers/codebooks persist across commands. OriginalGPUinstructions onCpath:0.\nSilent nominal15fps previews; no firmware streaming/audio synchronization/gameplay proof.\n')
    save(ROOT/'verification/movie-sequence-video-review.json',dict(directory=str(out),status='published',checkpoint=checkpoint))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — ALL SIX DIALOGUE VIDEO SEQUENCES IN C\n'+now+'\n\n'+checkpoint['checked_answer']+'\n\n763C-produced frames/53key/710delta;1,526commands;252execution-provenGPUinstructions;18guards. Whole4396logicalGPUbytes/2MBRAM/CPUIRQ and serialized peripheral/cartridge state match per command. C architecture retained between commands; only source CPU mailbox updates supplied. '+str(report['source_instructions'])+'sourceinstructions including mandatory delays.\n\nSix silent lossless animatedWebP previews decoded back to allsourceRGBframes/timestamps. Nominal15fps; notphysicaltiming or in-gameplayback.\n\nCoordinator-authored; no new local-model code/training. Source CPU/video wrappers, startup relocation, controller/firmware stream/audio synchronization still separate. Full game unfinished.\n\nPreview: '+clips[0]['path']+'\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(checkpoint['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),movies=6,frames=763,preview=clips[0]['path'])))

if __name__=='__main__':main()
