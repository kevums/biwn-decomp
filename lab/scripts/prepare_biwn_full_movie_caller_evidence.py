"""Publish full normal movie caller comparisons under explicit file/clock providers."""
import json,hashlib,shutil,wave
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/BIWN-full-movie-caller.json');guards=read(ROOT/'verification/BIWN-movie-VBI-guards.json');raw=Path(proof['directory']);assert read(raw/'status.json')['status']=='terminal_pass' and proof['all_six']
    assert (len(proof['messages']),proof['frames'],proof['audio_samples'],proof['word_clocks'],proof['source_dispatches'],proof['disc_requests'],proof['source_CPU_coverage'],guards['checks'])==(6,763,512,1103611,1856,43,[451,519],13)
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for name,h in proof['source_sha256'].items():assert sha(src/name)==h
    assert sha(ROOT/'scripts/check_biwn_full_movie_caller.py')==proof['script_sha256'];assert guards['source_sha256']==proof['source_sha256']['biwn_movie_VBI_event.c']
    previews=[]
    for m in proof['messages']:
        assert not m['original_CPU_GPU_DSP_instructions_on_C_path']
        a=read(raw/f'message-{m["message_id"]}-native.json');b=read(raw/f'message-{m["message_id"]}-C.json');assert a==b
        native=raw/f'message-{m["message_id"]}-native.wav';rebuilt=raw/f'message-{m["message_id"]}-C.wav';assert native.read_bytes()==rebuilt.read_bytes()
        target=ROOT/f'verified-previews/C-full-caller-message-{m["message_id"]}-controlled-audio.wav';shutil.copy2(rebuilt,target)
        with wave.open(str(target),'rb') as w:
            assert w.getnchannels()==2 and w.getsampwidth()==2 and w.getnframes()==m['word_clocks']
            info=dict(message_id=m['message_id'],file=str(target),sha256=sha(target),sample_rate=w.getframerate(),frames=w.getnframes(),seconds=w.getnframes()/w.getframerate(),caption='C source caller output under declared nominal clocks; matches reference PCM. Natural source stop leaves final queued audio token unconsumed in this schedule; no physical synchronization proof.')
        previews.append(info)
    now=datetime.now(timezone.utc).isoformat();cp=dict(recorded_at=now,status=proof['status'],
        checked_answer='The complete normal D3FC movie caller now runs in C through all six dialogue movies: 763 video frames, 512 queued audio samples, 1856 source state dispatches and 43 actual source-selected disc requests. CPU/GPU/DSP/RAM/devices, GPU trace/counts and controlled audio output match the original through source E918 audio shutdown and D3EC exit to resident idle. A file-backed MSF/LBA reader and declared clocks supply the platform. This is the renderer-ready, repeat-zero, uncancelled path; busy TRAP0 scheduling, actual BIOS/physical timing and whole-game playback remain unverified.',
        movies=6,video_frames=763,audio_samples_enqueued=512,source_state_dispatches=1856,source_disc_requests=43,controlled_word_clocks=1103611,source_movie_CPU_coverage=[451,519],source_movie_CPU_unexercised_instructions=68,VBI_contract_checks=13,
        C_CPU_GPU_DSP=True,normal_D3FC_caller_verified=True,source_E918_audio_shutdown_verified=True,source_D3EC_GPU_exit_to_resident_verified=True,all_source_sample_pointers_and_arguments_retained=True,
        original_CPU_GPU_DSP_instructions_on_C_path=False,
        queued_file_reader='Actual source303C MSF request to declared raw track LBA ranges; word-swap16/+2-byte alignment; source A0/A1 destination/end. Partial progress uses32-byte quantization. Bootstrap delivery ticks and352800-byte/second rate are declared platform behavior. No per-sample host delivery or pointer replacement.',
        VBI_progress='Own six-byte supervisor IRQ2 frame at D4A8, shared TOM pendingvideo, source E7D4 CD_ptr/progress update and RTE. Compared against originalCPU handler within each caller dispatch.',
        clock_scope='Source600-unit video timestamps set declared time at dispatch boundaries; SCLK18 gives21868nominalwordclocks/sec. DSP clock blocks use immutable RAM (asserted before/after) and permit onlyDAC external stores; everyDSP/DAC/PCM/count state enters a cumulative digest. All2MBRAM also compared per source dispatch.',
        audio_lifetime='Every audio enqueue pointer/length/bytes match extracted original samples. EveryC DSP external audio byte matches its chronological original queued token, detecting overwrite before consumption.',
        audio_tail_limit='All512chunks are enqueued, but the natural E918 stop under this nominal dispatch schedule leaves each movie final queued token unconsumed. WAVs reproduce the matched reference output; they do not prove every queued byte played or physical A/V sync.',
        supervisor_stack='Source4004 setsA7=200000. Six callerarguments+JSR usecalleeSP1FFFE4, safely above DMAend1FFC00. Source movie destination uses frozenBD830=778D0; no host video address replacement.',
        declared_providers=['BIOS3000 no-op ABI provider; actualfirmware unverified','Queued file-backed CD read/progress with stated MSF mapping/alignment/rate','Nominal dispatch-boundary time/SSI/VBI schedule; host invokes the normalcaller','Renderer-ready0/repeatcount0/no input cancellation; whole boot/globaltask schedule separate'],
        busy_TRAP0_path_verified=False,repeat_or_cancellation_paths_verified=False,BIOS_actual_firmware=False,physical_AV_synchronization_verified=False,every_queued_audio_byte_played=False,whole_game_complete=False,in_game_playback_verified=False,native_Chat_verified=False,
        implementation_authorship='Coordinator authored fullcaller/file-reader/clock/VBI integration and guards. Existing C source CPU/GPU/DSP bodies unchanged. No new localmodelcode/training;139selectedregistry and171localinstructionbodies unchanged.',
        audio_previews=previews,report=str(ROOT/'verification/BIWN-full-movie-caller.json'),guards=str(ROOT/'verification/BIWN-movie-VBI-guards.json'),
        next_work=['Exercise source renderer-busy D414TRAP0/scheduler handoff, repeats and cancellation under source caller frames.', 'Replace nominal timing with source GPU timer/SSI/global scheduling; inspect the matched audio-tail truncation before any restoration change.', 'Validate BIOS3000/CD firmware or verify its platform replacement; link actor dialogue/world runtime and actual scanout/boot.', 'Continue native LM Studio Chat usability and advertising workflows.'])
    save(ROOT/'verification/full-movie-caller-checkpoint.json',cp)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';s=read(p);s['full_movie_caller_checkpoint']=cp;save(p,s)
    out=ROOT/'verification/full-movie-caller-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[ROOT/'scripts/check_biwn_full_movie_caller.py',ROOT/'scripts/check_biwn_movie_VBI_guards.py',Path(__file__),ROOT/'verification/BIWN-full-movie-caller.json',ROOT/'verification/BIWN-movie-VBI-guards.json',ROOT/'verification/full-movie-caller-checkpoint.json',*[src/n for n in proof['source_sha256']],src/'biwn_movie_VBI_event.h'];manifest=[]
    for p in files:
        target=out/p.name;shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(checkpoint=cp,files=manifest))
    (out/'who-and-prompts.txt').write_text('Coordinator implemented the queued disc reader, source dispatch-boundary VBI event, own DSP CSR linkage/reinitialization/stop polling and completeD3FC comparison. No local-model implementation prompts or training;171 prior local bodies unchanged.\nSource controller now chooses all sample pointers, disc requests, framebuffers and natural E918/D3EC shutdown. OriginalCPU/GPU/DSP solely form reference; C side executes none.\nFirst native movie completed while C failed because DC7C cartridge-clear helper budget200000 was below its262144wordwrites; the finite2millioninstruction budget fixes its actual source loop. Native reference retained; then allsix native/C runs recomputed.\nThe declared nominal clock schedule leaves each last audio token queued at source stop; no claim of complete audible tails or physical synchronization. BusyTRAP0/repeat/cancel/globalgameplay remain unfinished.\n')
    save(ROOT/'verification/full-movie-caller-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — COMPLETE NORMAL MOVIE CALLERS IN C\n'+now+'\n\n'+cp['checked_answer']+'\n\nSix movies:763frames,512audioenqueues,1856state dispatches,43disc requests,1103611wordclocks.451/519source movie CPUinstructions;13VBI checks. FullCPU/RAM/GPU/DSP/peripherals and GPUtrace/counts perdispatch, everyDSP/DAC/PCM/count afterwordclock via digest.\n\nImportant: all audio samples are queued; natural stop under this declared schedule leaves each last token unconsumed. Audio previews match reference output, not complete audible tails or physical synchronization. Whole game remains incomplete.\n\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),frames=763,audio_samples=512,word_clocks=1103611)))
if __name__=='__main__':main()
