"""Publish checked source controller CPU/GPU/DSP first-cluster integration."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/BIWN-movie-source-overlay-AV.json');out=ROOT/'verification/movie-source-overlay-AV-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
    assert (proof['messages'],proof['video_frames'],proof['source_sample_dispatches'],proof['word_clocks'])==(6,12,24,3072)
    assert not proof['original_CPU_GPU_DSP_instructions_on_C_path']
    assert proof['source_D3C6_E098_and_GPU_dispatcher_executed'] and not proof['direct_host_movie_payload_reload']
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    fixtures=read(Path(proof['directory'])/'fixtures.json')
    for f in fixtures:
        startup=f['snapshot']['overlay_start'];assert 'CPU' in startup
        dispatch=next(x for x in startup['GPU_calls'] if x.get('resident_dispatcher') and not x['idle']);assert (dispatch['blocks'],dispatch['instructions'])==(2829,3391)
        stages=f['snapshot']['stages'];assert len(stages)==4
        for s in stages:
            assert len(s['sound_states'])==128
            witness=s['before_sound']['sample_witness']
            assert witness.get('matches_previous_all763_C_video',witness.get('matches_extracted_disc_sample'))
    now=datetime.now(timezone.utc).isoformat();cp=dict(recorded_at=now,status=proof['status'],
        checked_answer='Source CPU D3C6/E098 now submits the movie overlay through the reconstructed resident GPU dispatcher, which copies562words and starts the source decoder header. The direct host payload reload has been removed from this integration. Startup CPU/RAM/GPU/devices and dispatcher trace/counts match the original, followed by the first-cluster C CPU/GPU/DSP integration in all six movies:24samples/12frames/3072controlledwordclocks. Initial resident context, disc delivery/progress and clocks remain fixtures; fullboot/moviecaller/shutdown/streaming/scheduler/audio-video synchronization/gameplay remain unfinished.',
        movies=6,source_sample_dispatches=24,first_clusters=6,video_frames=12,controlled_word_clocks=3072,
        source_CPU_instruction_coverage=proof['CPU_source_coverage'],
        movie_state_controller_integrated=True,movie_controller_integration_scope='D3C6/E098 overlaystartup and D4A8/D896 firstcluster; not fullD3FC caller/shutdown/streaming/scheduler',
        C_CPU_GPU_DSP=True,source_D3C6_E098_and_GPU_dispatcher_executed=True,direct_host_movie_payload_reload=False,dispatcher_copied_words=562,dispatcher_direct_blocks=2829,dispatcher_instructions_with_delay=3391,source_video_arguments_and_audio_pointer_host_replaced=False,original_CPU_GPU_DSP_instructions_on_C_path=False,
        matched='FullCPU/SR/USP/SSP/privateframes and all2MBRAM plus4396logicalGPU/8496logicalDSP/peripherals/GPUtrace/counts eachdispatch; all8496DSP/RAM/DAC/instructioncounts/PCM each controlledclock. Audio sample bytes verified against disc hashes and video against prior763frame output.',
        declared_providers=['128KB mastered-byte delivery and BIOS seek/progress ABI','Clock values0/40 and source state4 timer tick','Initial resident GPU code/idle context; sourceD3C6/GPUdispatcher performs the movie overlay reload','128SSI/word clocks after each sample; no physical synchronization'],
        whole_game_complete=False,in_game_playback_verified=False,BIOS_streaming_verified=False,audio_synchronization_verified=False,native_Chat_verified=False,
        implementation_authorship='Coordinator authored startup/integration harness; existing source C components unchanged. Existing GPUdispatcher retains31acceptedlocalinstructionbodies. No new localmodelimplementationprompts/training;139selectedregistry/171localinstructionbodies unchanged.',
        report=str(ROOT/'verification/BIWN-movie-source-overlay-AV.json'),
        next_work=['Integrate sourceD3EC movie shutdown/GPUforcedIRQ/residentreturn and fullD3FC caller/directTRAP0 scheduler.','Validate source disc request/progress delivery, ring buffer wraps/reloads and complete movies.','Complete audio/video source clock/scheduler synchronization and actual game runtime/scanout; validate native LM Studio Chat.'])
    save(ROOT/'verification/movie-source-overlay-AV-checkpoint.json',cp)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';d=read(p);d['movie_source_overlay_AV_checkpoint']=cp;save(p,d)
    files=[ROOT/'verification/BIWN-movie-source-overlay-AV.json',ROOT/'verification/BIWN-movie-controller-video.json',ROOT/'verification/movie-source-overlay-AV-checkpoint.json',ROOT/'scripts/check_biwn_movie_controller_video.py',ROOT/'scripts/check_biwn_movie_controller_AV.py',ROOT/'scripts/check_biwn_movie_source_overlay_AV.py',Path(__file__),*[src/n for n in proof['source_sha256']]];manifest=[]
    for p in files:
        dest=out/p.name;shutil.copy2(p,dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    save(out/'manifest.json',dict(checkpoint=cp,files=manifest))
    (out/'who-and-prompts.txt').write_text('Coordinator connected sourceD3C6/E098 to existing residentGPUdispatcher, preserving GPUarchitecture and bus/RAM across decoderstartup and firstcluster CPU/GPU/DSP execution. No new sourcecasebodies/modelcodeprompts/training; existing31localdispatcher bodies/171total unchanged.\nNative oracle alone executes original CPU/GPU/DSP. C side forbids CPUexecute and verifies GPU/DSPcounters unchanged within source programs. Source D3C6 writes21EA0; reconstructed GPUdispatcher copies562words,2829directblocks/3391instructions including562delayNOPs; sourceheader3instructions startsdecoder. Direct host moviepayload copy/start removed.\nInitial residentGPUcontext/code and clock/disc/progress providers remain fixtures; fullboot/D3FC/directTRAP0/shutdown/GPUforcedIRQ/residentreturn/streaming/scheduler/physicalAV/gameplay unfinished.\n')
    save(ROOT/'verification/movie-source-overlay-AV-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — SOURCE MOVIE OVERLAY STARTUP AND C CPU/GPU/DSP\n'+now+'\n\n'+cp['checked_answer']+'\n\nScope: first cluster per movie, two audio and two video samples. Both audio sample pointers/bytes originate in the source controller. Each video frame equals its prior checked all763-frame output. This is not yet a complete movie player.\n\nPrior all763video frames with CCPUwrappers/GPUloader/STOP/IRQ/RTE remain verified separately. Existing six silent clips retained. No new training/defaults; coordinator-authored integration.\n\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),video_frames=12,word_clocks=3072)))
if __name__=='__main__':main()
