"""Publish source CPU+GPU relocation/video/STOP/IRQ comparisons across763frames."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/BIWN-full-video-CPU-GPU.json');guards=read(ROOT/'verification/BIWN-video-CPU-guards.json');previous=read(ROOT/'verification/movie-sequence-video-checkpoint.json')
    assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
    assert (proof['cases'],proof['frames'],proof['CPU_source_instruction_coverage'],guards['host_guards'])==(6,763,[204,254],27)
    assert not proof['original_CPU_or_GPU_instructions_on_C_path'] and proof['source_STOP_IRQ_RTE_C']
    assert proof['source_sha256']==guards['source_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for n,digest in proof['source_sha256'].items():assert sha(source/n)==digest
    now=datetime.now(timezone.utc).isoformat();checkpoint=dict(recorded_at=now,status=proof['status'],
        checked_answer='The source CPU video wrappers, GPU self-relocation loader, STOP, GPU interrupt frame, IRQ handler and RTE now run in C with the C GPU decoder across all763video samples of six dialogue movies. Full CPU/private frames, RAM, logical GPU state, devices and GPU trace/counts match the original at each wrapper boundary. No original CPU/GPU instructions execute on the rebuilt path. Movie controller/streaming/scheduler/audio synchronization remain unfinished.',
        movies=6,frames=763,source_CPU_instruction_coverage=[204,254],source_CPU_generated_instructions=254,source_CPU_unexercised_instructions=50,host_guards=27,
        C_CPU_video_wrappers=True,C_GPU_self_relocation=True,C_STOP_GPU_interrupt_IRQ_RTE=True,
        original_CPU_or_GPU_instructions_on_C_path=False,
        source_GPU_decoder_instructions=252,source_GPU_initialization_instructions=47,
        C_CPU_GPU_state_retained_between_frames=True,
        matched='Each source wrapper: completeCPU/SR/USP/SSP/privateframes, all2MBRAM, all4396logicalGPUbytes, serializedDSP/TOM/JERRY/DAC/cartridge state and GPU outerPC hashes/direct+delay counts.',
        stopped_CPU_device_adapter='C GPU control write publishes pendingGPU to the shared TOM model and emits the C-owned CPU interrupt frame. The masked native CPU shadow never executes or emits a substitute frame; its deferred CPUINT event is suppressed in favor of the C stopped-state event.',
        startup_fixture='D340 receives canonical pre-relocation GPU bytes from the preserved stage; frozen runtime RAM already contains a relocated image and cannot be relocated twice.',
        declared_providers=['Host invokes sourceCPU functions and supplies each actual video sample.','Overlay reload/restart is an explicit event; sourceD3C6 resident dispatcher not integrated.','CPU/GPU alternate at sourceSTOP; full game scheduler/physical timing not verified.'],
        source_CPU_coverage_scope='204of254instructions exercised by all six real movie video sequences. Invalid/multiple-strip/VBI paths and22780boolean helper remain outside this normal corpus proof.',
        movie_controller_integrated=False,BIOS_streaming_verified=False,audio_synchronization_verified=False,in_game_playback_verified=False,physical_timing_verified=False,native_Chat_verified=False,whole_game_complete=False,
        implementation_authorship='Coordinator authored254staticCPUblocks,47GPUinitializationblocks, STOP/IRQ event functions and comparisons/guards. No new local-model code or training; prior171local instruction bodies retained.',
        previously_selected_component_registry=139,new_components_added_to_registry=0,
        report=str(ROOT/'verification/BIWN-full-video-CPU-GPU.json'),guards=str(ROOT/'verification/BIWN-video-CPU-guards.json'),
        retained_silent_video_previews=previous['clips'],
        next_work=['Connect these C video providers to source movie state handlers/controller and scheduler, includingD3C6 overlay load/restart.',
                   'Validate source disc seek/progress/buffer wrap/reload lifetimes and complete audio synchronization.',
                   'Continue other game tasks, actual boot/runtime/scanout and native LM Studio Chat validation.'])
    save(ROOT/'verification/full-video-CPU-GPU-checkpoint.json',checkpoint)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';summary=read(p);summary['full_video_CPU_GPU_checkpoint']=checkpoint;save(p,summary)
    out=ROOT/'verification/full-video-CPU-GPU-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');(out/'snapshot').mkdir(parents=True)
    files=[*[source/n for n in proof['source_sha256']],*[ROOT/'scripts'/n for n in ['generate_biwn_video_cpu.py','generate_biwn_movie_relocation_GPU.py','check_biwn_video_cpu_gpu.py','check_biwn_full_video_cpu_gpu.py','check_biwn_video_cpu_guards.py']],Path(__file__),ROOT/'verification/BIWN-full-video-CPU-GPU.json',ROOT/'verification/BIWN-video-CPU-guards.json',ROOT/'verification/full-video-CPU-GPU-checkpoint.json'];snapshots=[]
    for p in files:
        target=out/'snapshot'/p.name;shutil.copy2(p,target);snapshots.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(recorded_at=now,checkpoint=checkpoint,files=snapshots))
    (out/'who-and-prompts.txt').write_text('Coordinator authored CPU/IRQ/STOP/RTE and GPU relocation source reconstruction. No local-model implementation prompts or training in this work. Prior171accepted local instruction bodies unchanged.\nC path forbids originalCPUexecute and verifies originalGPUcounter unchanged. All763video samples match with both processorsC; original path supplies the oracle.\nCanonical source image fixes double-relocation fixture; C stopped-state adapter reproduces pendingGPU/IRQ semantics through shared TOM bus, with C-owned six-byte frame.\nSource movie controller/overlay dispatcher/firmware stream/scheduler/audio synchronization remain separate.\n')
    save(ROOT/'verification/full-video-CPU-GPU-review.json',dict(directory=str(out),status='published',checkpoint=checkpoint))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CPU AND GPU VIDEO PATH IN C\n'+now+'\n\n'+checkpoint['checked_answer']+'\n\nSix movies/763frames;sourceCPU204of254instructions;27guards. GPUself-relocation handles mutableMOVEIoperands without decodingopcodes. STOP/IRQ/RTE sourceframes preserved; C-ownedIRQ uses sharedTOM pendingGPU event. No originalCPU/GPUinstructions onCpath.\n\nHost supplies samples and overlayreload/CPU-GPUalternation; moviecontroller/residentdispatcher/firmwarestream/audio synchronization not yet integrated. Existing six silent lossless clips retained. Full game unfinished.\n\nCoordinator-authored; no new local-modelcode/training. Priorselected139registry unchanged.\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(checkpoint['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),frames=763,CPU_coverage=[204,254],guards=27)))

if __name__=='__main__':main()
