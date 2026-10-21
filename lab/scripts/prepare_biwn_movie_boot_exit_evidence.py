"""Publish source CPU/GPU movie initialization, controlled A/V and IRQ0 exit."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=read(ROOT/'verification/BIWN-movie-source-boot-exit-AV.json');boot=read(ROOT/'verification/BIWN-main-GPU-boot-C.json');GPUguards=read(ROOT/'verification/BIWN-GPU-boot-exit-guards.json');CPUguards=read(ROOT/'verification/BIWN-GPU-boot-CPU-guards.json')
    assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
    assert (proof['messages'],proof['video_frames'],proof['source_sample_dispatches'],proof['word_clocks'],proof['GPU_loader_CPU_instruction_coverage'])==(6,12,24,3072,[10,10])
    assert proof['C_source_GPU_loader_E00A'] and proof['C_mainGPU_initializer_and_IRQ0_exit'] and proof['source_D3EC_executed'] and not proof['original_CPU_GPU_DSP_instructions_on_C_path']
    assert (boot['cases'],boot['source_instruction_coverage'],GPUguards['checks'],CPUguards['checks'])==(9,[21,21],33,18)
    assert GPUguards['real4396byte_GPU_IRQ_event_match']
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    for n,h in boot['source_sha256'].items():assert sha(src/n)==h
    assert sha(ROOT/'scripts/check_biwn_movie_source_boot_exit_AV.py')==proof['script_sha256']
    fixtures=read(Path(proof['directory'])/'fixtures.json')
    for f in fixtures:
        s=f['snapshot'];assert s['queries'][0]['target']=='0x3000' and s['queries'][0]['A0']==0xf03050
        first=next(x for x in s['overlay_start']['GPU_calls'] if x.get('program')=='main_boot');assert (first['blocks'],first['instructions'])==(20,21)
        last=s['exit']['GPU_calls'];assert (last[0]['program'],last[0]['blocks'],last[0]['instructions'])==('movie_exit',8,10) and last[1]['resident_dispatcher'] and last[1]['idle']
        for item in s['stages']:assert item['before_sound']['sample_witness'].get('matches_previous_all763_C_video',item['before_sound']['sample_witness'].get('matches_extracted_disc_sample'))
    now=datetime.now(timezone.utc).isoformat();cp=dict(recorded_at=now,status=proof['status'],
        checked_answer='The reconstructed source CPU E00A now copies and starts the main GPU program. Its C initializer establishes interrupt enables. Source D3C6/E098 and the C GPU dispatcher load/start the movie overlay, and the source controller drives C CPU/GPU/DSP through the first cluster of each of six movies. A controlled source D3EC exit request then emits the C GPU IRQ0 frame, executes the source handler and returns to resident idle. Full state, devices and trace/counts match the original. BIOS3000, disc transfer/progress and clocks remain declared providers; complete movie caller, streaming, scheduler, physical A/V synchronization and gameplay remain unfinished.',
        movies=6,source_sample_dispatches=24,video_frames=12,controlled_word_clocks=3072,
        C_source_GPU_loader_E00A=True,source_GPU_loader_CPU_instructions=10,source_GPU_loader_CPU_coverage=[10,10],source_CPU_instruction_coverage=proof['CPU_source_coverage'],
        C_mainGPU_initializer=True,mainGPU_initializer_instructions=21,mainGPU_initializer_cases=9,mainGPU_initializer_coverage=[21,21],
        C_GPU_IRQ0_event_and_source_exit=True,GPU_exit_handler_instructions=10,GPU_exit_handler_direct_blocks=8,source_D3EC_executed=True,
        GPU_boot_exit_contract_checks=33,CPU_loader_contract_checks=18,real_captured_GPU_IRQ0_frame_matches=True,
        C_CPU_GPU_DSP=True,movie_state_controller_integrated=True,movie_controller_integration_scope='Source E00A loader/GPU initializer, D3C6/E098 startup, D4A8/D896 first cluster, controlled D3EC IRQ0 exit. Full D3FC caller and natural full-movie ending remain unverified.',
        source_D3C6_E098_and_GPU_dispatcher_executed=True,direct_host_movie_payload_reload=False,direct_host_mainGPU_payload_reload=False,dispatcher_copied_words=562,dispatcher_direct_blocks=2829,dispatcher_instructions_with_delay=3391,
        original_CPU_GPU_DSP_instructions_on_C_path=False,
        matched='Complete CPU/SR/USP/SSP/private frames, all 2MB RAM, 4396 logical GPU bytes, 8496 logical DSP bytes and shared peripherals at source stages; GPU PC trace/direct+delay counts. DSP/RAM/DAC/PCM/instruction counts after each controlled clock. Video pixels equal prior all763 output; audio pointers/bytes equal actual disc samples. Native opcode/pipeline microstates excluded.',
        declared_providers=['BIOS3000 ABI(A0=F03050); actual firmware behavior not implemented or claimed','128KB mastered-byte delivery and BIOS seek/progress ABI','Source state4 clock tick and video times0/40','128 SSI/word clocks after each sample','Host schedules source functions and issues D3EC exit after first cluster; not fullD3FC/global task schedule'],
        BIOS3000_actual_firmware=False,BIOS_streaming_verified=False,complete_D3FC_caller_verified=False,complete_movie_shutdown_verified=False,audio_synchronization_verified=False,in_game_playback_verified=False,native_Chat_verified=False,whole_game_complete=False,
        implementation_authorship='Coordinator generated 10 CPU loader,21 GPU initializer and10 GPU exit-handler blocks plus own IRQ0 event and integration/guard harnesses. Existing31 local-model dispatcher blocks retained; no new local implementation prompts/training. Selected registry139 and accepted local instruction bodies171 unchanged.',
        report=str(ROOT/'verification/BIWN-movie-source-boot-exit-AV.json'),guards=[str(ROOT/'verification/BIWN-GPU-boot-exit-guards.json'),str(ROOT/'verification/BIWN-GPU-boot-CPU-guards.json')],
        next_work=['Connect full source D3FC caller/directTRAP0 and scheduler to actual disc delivery/progress, including all sample/cluster buffer wraps and source end-of-movie audio shutdown.',
                   'Validate BIOS3000/CD firmware or implement and explicitly verify its platform replacement; complete source audio/video clock synchronization.',
                   'Use actual startup supervisor stack (4004 sets A7=200000) for streamed buffers ending1FFC00; the older1FF000 fixture stack overlaps a full buffer. Verify the whole caller lifetime.',
                   'Continue whole source boot/game tasks/runtime/scanout and visible native LM Studio Chat validation.'])
    save(ROOT/'verification/movie-boot-exit-AV-checkpoint.json',cp)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';summary=read(p);summary['movie_boot_exit_AV_checkpoint']=cp;save(p,summary)
    out=ROOT/'verification/movie-boot-exit-AV-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    scripts=['generate_biwn_GPU_boot_cpu.py','generate_biwn_main_GPU_boot.py','generate_biwn_gpu_movie_exit.py','check_biwn_main_GPU_boot.py','probe_biwn_movie_exit_GPU.py','check_biwn_movie_boot_exit_AV.py','check_biwn_movie_source_boot_exit_AV.py','check_biwn_GPU_boot_exit_guards.py','check_biwn_GPU_boot_CPU_guards.py']
    files=[*[src/n for n in proof['source_sha256']],*[src/Path(n).with_suffix('.h') for n in proof['source_sha256']],*[ROOT/'scripts'/n for n in scripts],Path(__file__),ROOT/'verification/BIWN-movie-source-boot-exit-AV.json',ROOT/'verification/BIWN-main-GPU-boot-C.json',ROOT/'verification/BIWN-GPU-boot-exit-guards.json',ROOT/'verification/BIWN-GPU-boot-CPU-guards.json',ROOT/'verification/movie-boot-exit-AV-checkpoint.json'];manifest=[]
    for p in files:
        target=out/p.name;shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(target)))
    save(out/'manifest.json',dict(checkpoint=cp,files=manifest))
    (out/'who-and-prompts.txt').write_text('Coordinator authored the new CPU/GPU source blocks, IRQ event and integration checks. No local-model implementation prompts or training. Existing31 local dispatcher instruction bodies/171total preserved.\nNative CPU/GPU/DSP only execute the reference. C side forbids nativeCPUexecute, checks original GPU/DSP counters unchanged, owns all CPU/GPU IRQ frames. BIOS3000 is a no-op ABI provider on both paths; no firmware claim.\nControlled source D3EC exit after first cluster, not a natural complete movie ending. SourceD3FC caller/audio stop/streaming/global scheduler unfinished.\nCompiler failures retained and unused emitter helpers removed. One failed loader comparison used DSP microstate size8729 on C prefix against logical8496 on native; both now compare all8496logical bytes consistently, with GPU/DSP microstate explicitly excluded throughout. No logical-state or peripheral mask.\n')
    save(ROOT/'verification/movie-boot-exit-AV-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — SOURCE GPU INITIALIZATION AND MOVIE EXIT IN C\n'+now+'\n\n'+cp['checked_answer']+'\n\nChecked: 10/10 CPU loader instructions; 21/21 GPU initializer instructions in 9 cases; 10 GPU IRQ0 handler instructions and exact real interrupt frame. Combined six-movie test:24 samples,12 video frames,3072 controlled clocks, source startup and controlled exit back to resident idle.51 typed contract checks.\n\nAll763 video frames remain checked separately. Neither complete source movie caller nor whole game is complete. No new training or model defaults.\n\nAudit: '+str(out)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),CPU_loader=10,GPU_boot=21,GPU_exit=10,contract_checks=51)))
if __name__=='__main__':main()
