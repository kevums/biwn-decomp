"""Publish checked source controller CPU/GPU/DSP first-cluster integration."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/BIWN-movie-controller-AV.json');out=ROOT/'verification/movie-controller-AV-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
    assert (proof['messages'],proof['video_frames'],proof['source_sample_dispatches'],proof['word_clocks'])==(6,12,24,3072)
    assert not proof['original_CPU_GPU_DSP_instructions_on_C_path']
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    fixtures=read(Path(proof['directory'])/'fixtures.json')
    for f in fixtures:
        stages=f['snapshot']['stages'];assert len(stages)==4
        for s in stages:
            assert len(s['sound_states'])==128
            witness=s['before_sound']['sample_witness']
            assert witness.get('matches_previous_all763_C_video',witness.get('matches_extracted_disc_sample'))
    now=datetime.now(timezone.utc).isoformat();cp=dict(recorded_at=now,status=proof['status'],
        checked_answer='The source movie state controller now drives reconstructed C CPU video providers, C GPU decoding and C DSP audio execution together for the first cluster of each of six dialogue movies: 24 samples, 12 video frames and 3072 controlled audio word clocks match the original. Audio pointers/bytes match the extracted disc samples, video pixels match the earlier all763 decoder proof. Full movie streaming, caller/overlay dispatcher, global scheduling and physical audio/video synchronization remain unfinished.',
        movies=6,source_sample_dispatches=24,first_clusters=6,video_frames=12,controlled_word_clocks=3072,
        source_CPU_instruction_coverage=proof['CPU_source_coverage'],
        movie_state_controller_integrated=True,movie_controller_integration_scope='D4A8/D896 first cluster only; not completeD3FC caller, streaming or scheduler',
        C_CPU_GPU_DSP=True,source_video_arguments_and_audio_pointer_host_replaced=False,original_CPU_GPU_DSP_instructions_on_C_path=False,
        matched='FullCPU/SR/USP/SSP/privateframes and all2MBRAM plus4396logicalGPU/8496logicalDSP/peripherals/GPUtrace/counts eachdispatch; all8496DSP/RAM/DAC/instructioncounts/PCM each controlledclock. Audio sample bytes verified against disc hashes and video against prior763frame output.',
        declared_providers=['128KB mastered-byte delivery and BIOS seek/progress ABI','Clock values0/40 and source state4 timer tick','GPU overlay reload/start instead of residentD3C6 dispatcher','128SSI/word clocks after each sample; no physical synchronization'],
        whole_game_complete=False,in_game_playback_verified=False,BIOS_streaming_verified=False,audio_synchronization_verified=False,native_Chat_verified=False,
        implementation_authorship='Coordinator authored integration harness; existing source C CPU/GPU/DSP components unchanged. No local-model implementation prompts or new training. Prior139selectedregistry/171acceptedlocalinstructionbodies unchanged.',
        report=str(ROOT/'verification/BIWN-movie-controller-AV.json'),
        next_work=['Integrate source D3C6 resident GPU overlay reload and fullD3FC movie caller/directTRAP0 scheduler.','Validate source disc request/progress delivery, ring buffer wraps/reloads and complete movies.','Complete audio/video source clock/scheduler synchronization and actual game runtime/scanout; validate native LM Studio Chat.'])
    save(ROOT/'verification/movie-controller-AV-checkpoint.json',cp)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';d=read(p);d['movie_controller_AV_checkpoint']=cp;save(p,d)
    files=[ROOT/'verification/BIWN-movie-controller-AV.json',ROOT/'verification/BIWN-movie-controller-video.json',ROOT/'verification/movie-controller-AV-checkpoint.json',ROOT/'scripts/check_biwn_movie_controller_video.py',ROOT/'scripts/check_biwn_movie_controller_AV.py',Path(__file__),*[src/n for n in proof['source_sha256']]];manifest=[]
    for p in files:
        dest=out/p.name;shutil.copy2(p,dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    save(out/'manifest.json',dict(checkpoint=cp,files=manifest))
    (out/'who-and-prompts.txt').write_text('Coordinator connected existing reconstructed source movie state CPU, video CPU/STOP/GPU interrupt/IRQ/RTE, GPU decoder and DSP sample engine. No local-model code prompts or training in this implementation. Prior139selectedcomponents and171acceptedlocalinstructionbodies unchanged.\nNativeCPU/GPU/DSP run only the oracle. C side forbids nativeCPUexecute, originalGPU/DSPcounters unchanged. Controller supplies actual source arguments/pointers; individual video/audio wrappers no longer host-invoked for this first-cluster integration.\nFirst failed fixture retained: D340 naturally sets idleFFFF, explicit requeststate0 must follow startup; user-mode STOP raises original privilege exception, so this video/controller path uses supervisor fixture. Source instructions unchanged.\nProviders remain host128KBdisc/BIOSABI/clock/overlayrestart/SSI clocks; fullD3FC/directTRAP0/residentD3C6/streaming/synchronization/gameplay unfinished.\n')
    save(ROOT/'verification/movie-controller-AV-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — SOURCE MOVIE CONTROLLER WITH C CPU/GPU/DSP\n'+now+'\n\n'+cp['checked_answer']+'\n\nScope: first cluster per movie, two audio and two video samples. Both audio sample pointers/bytes originate in the source controller. Each video frame equals its prior checked all763-frame output. This is not yet a complete movie player.\n\nPrior all763video frames with CCPUwrappers/GPUloader/STOP/IRQ/RTE remain verified separately. Existing six silent clips retained. No new training/defaults; coordinator-authored integration.\n\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),video_frames=12,word_clocks=3072)))
if __name__=='__main__':main()
