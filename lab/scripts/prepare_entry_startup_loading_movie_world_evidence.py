"""Publish verified live scheduled-startup -> loading/movie/world chain."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import animation_renderer
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--timer',action='store_true');args=parser.parse_args();proof_path=ROOT/'verification'/('entry-timer-startup-loading-movie-world-checks.json'if args.timer else 'startup-loading-movie-world-checks.json')
    proof=read(proof_path);raw=Path(proof['directory']);assert read(raw/'status.json')['status']=='terminal_pass'
    assert proof['cases']==2 and proof['frames_per_case']==[187,187]and proof['audio_enqueued_per_case']==[125,125]
    assert not proof['source_DF60_RTS_completion_adapter']and not proof['initial_context_or_startup_capture_supplied']and proof['source_startup_to_movie_world_connected']
    assert proof['test_script_sha256']==sha(ROOT/'scripts/check_biwn_entry_scheduled_startup.py')
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,digest in proof['source_sha256'].items():assert sha(src/n)==digest
    states=[]
    for case in range(2):
        a=read(raw/f'case-{case}-native.json');b=read(raw/f'case-{case}-C.json');assert a==b
        assert (raw/f'case-{case}-native-final-RAM.bin').read_bytes()==(raw/f'case-{case}-C-final-RAM.bin').read_bytes()
        assert sha(raw/f'case-{case}-native-movie.wav')==sha(raw/f'case-{case}-C-movie.wav')
        s=b['summary'];boot=s['startup'];assert len(boot['handoffs'])==26 and boot['external_system_clock_ticks']==13
        assert len(boot['disc']['requests'])==12 and sum(x['bytes']for x in boot['disc']['requests'])==758846
        assert len(s['asset_disc_requests'])==18 and sum(x['bytes']for x in s['asset_disc_requests'])==1108650
        assert s['task_cycles']==dict(NPC=12,renderer=12,world=12)and len(s['polls'])==14 and len(s['handoffs'])==60
        assert sum(x['kind']=='source_loading_handoff'for x in s['prefix_events'])==35
        assert s['CPU']['pc']==0xef88 and s['frames']==187 and s['audio_enqueued']==125 and s['word_clocks']==271164
        states.append(s)
    if args.timer:
        assert proof['source_system_clock_IRQ2_handler']and not proof['source_system_clock_direct_RAM_increment']and proof['source_system_timer_events_per_case']==[13,13]
        for state in states:
            assert sum(call.get('program')=='source_timer_IRQ2'for call in state['startup']['GPU_calls'])==13
    s=states[0];ram=(raw/'case-0-C-final-RAM.bin').read_bytes();get=lambda a:int.from_bytes(ram[a:a+4],'big');pointer=get(0x43daa);assert pointer==get(0xbd844)
    pixels=ram[pointer:pointer+80640];preview=ROOT/'verified-previews/C-startup-loading-movie-world-plane.png';preview.write_bytes(animation_renderer.image_png(pixels,224,180,3));(raw/'C-startup-loading-movie-world-plane.CRY16').write_bytes(pixels)
    now=datetime.now(timezone.utc);out=ROOT/'verification/startup-loading-movie-world-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    cp=read(ROOT/'verification/continuous-loading-movie-world-checkpoint.json')
    cp.update(recorded_at=now.isoformat(),status=proof['status'],verified_profiles=2,earlier_startup_capture_supplied=False,ready_merchant_capture_supplied=False,initial_context_ring_freepool_supplied=False,source_DD40_system_pool_and_render_creation=True,source_initial_freepool_records=100,source_total_initial_task_creations=20,source_startup_contexts=21,source_startup_scheduler_handoffs=26,source_startup_clock_ticks=13,source_health_sleep_TRAP3=True,source_health_timeout_expiration_and_removal_verified=False,source_actor_bodies_during_startup_reached=proof['actor_task_body_reached'],source_startup_disc_requests=12,source_startup_disc_bytes=758846,total_asset_disc_requests=18,total_asset_disc_bytes=1108650,source_DF60_RTS_completion_adapter=False,source_loading_handoffs=35,source_loading_requests=6,source_loading_bytes=349804,source_startup_to_loading_movie_world_connected=True,intermediate_startup_RAM_restore_or_CPU_GPU_DSP_reset=False,source_boot_verified=False,
        original_reference_directory=str(raw),original_reference_reused_for_C_integration_replay=False,original_reference_reused_for_idle_body_replay=False,replay_note='Both original Native and C were executed fresh for two source-startup/input/device seed profiles. Exact nested snapshots, complete RAM, handoffs, disc transfers, GPU/DSP/peripherals/AV digests and WAV bytes match. No captured startup/merchant boundary or intermediate processor reset/RAM restoration.',
        initial_boundary='Supplied FrozenRAM/CPU/processor initialization followed by sourceDD40; no17DC2startup or ready-merchant capture',
        declared_providers=['Frozen RAM image/initial CPU/supervisor stack and source GPU/DSP/media setup beforeDD40; source4000/globalboot/firmware not linked.',
            'One-unit system clock increments at sourceDDD8 (13ticks duringstartup), emulated buttons keeping modalbit0 clear.',
            'Asset file-backed disc with captured674-byte normalized-track phase; BIOS303C/3042 preserve-register adapters; completion after real source handoff.',
            'Controlled doorway/stairs312->313->314 poses/entries/world-loop restore via byte changes in live RAM;15 other task contexts quiescent.',
            'Nearby-player/cash0 at sourceEE20; controlled postmovie button sequence and8-unit world/render clock increments.',
            'Movie file-backed MSF/LBA/+2 alignment/352800Bps; BIOS3000 no-op, nominal600 video timeline/sourceVBI andSCLK18SSI/DAC clocks.',
            'Synchronous GPU completion at source polling and shared pinned emulator blitter; no intermediateGPUreset/reseed.'],
        geometry_plane_preview=dict(image_path=str(preview),PNG_sha256=sha(preview),source_dimensions=[224,180],raw_sha256=hashlib.sha256(pixels).hexdigest(),pointer=hex(pointer),scope='Saved drawing plane after source scheduledstartup/loading/movie and12world cycles; not physical scanout.'),
        report=str(raw/'report.json'),audit=str(out),implementation_authorship='Coordinator-authored health timeout CPU/source scheduling/live continuation and test integration. Existing C CPU/GPU/DSP bodies reused; no new local-model code authorship or training.',
        checked_answer='Two fresh Native/C profiles now run sourceDD40 system/pool/render creation, scheduledstartup and actualhealthTRAP3sleep through26 sourcehandoffs/13external systemticks, then controlleddoorway/stairs312->313->314 loading/taskreuse/creation/merchantcoldinit,187-frame125-enqueue movie and12later world/NPC/renderer cycles. The earlier17DC2startup and ready-merchant captures are removed; no intermediate CPU/GPU/DSP reset or RAM restoration. Source startup12asset transfers758846bytes plus later6/349804bytes total18/1108650bytes;35laterloading and60postmovie handoffs match. FullCPU/privateRAM/logicalGPU-DSP/peripherals/requests/traces/AVdigests/WAV bytes match. FrozenRAM/CPU/sourceprocessor-setup,13systemclockticks,controlledposes/entries/worldlooprestore/nearplayer/buttons/taskquiescence/8-unitworldclocks,file-CD/BIOS/nominalvideo/SSI/VBI/sharedsynchronousblitter/GPUcompletion remain providers. Full4000/globalboot/sourceglobaltiming/firmware/remainingtasks/modalbranch/purchases/collisionedges/physicalscanout/playablegame/nativeChat remain unverified.',
        next_work=['Replace controlled doorway/pose/entry/worldlooprestore with source input-driven loading; implement remaining task bodies/health timeout expiration/modal branch.',
            'Connect source4000/globalboot/timer interrupts/global clocks/firmware and physicalscanout; expand reachable choices/transitions/collision edges.',
            'Continue native LMStudio Chat usability and advertising workflows.'])
    if args.timer:
        cp.update(source_system_clock_IRQ2_handler=True,source_system_clock_direct_RAM_increment=False,source_system_timer_events=13,source_global_clock_verified=False,standalone_timer_proof=read(ROOT/'verification/GPU-timer-checks.json'),early_CPU_helpers_proof=read(ROOT/'verification/entry-setup-helpers-checks.json'))
        cp['declared_providers'][1]='Externally delivered timer IRQ2 at sourceDDD8 (13 events during startup); source GPU handler updates778CC/BD854/BD852. Physical timer period/global time remain supplied; modalbit0 clear buttons.'
        cp['checked_answer']=cp['checked_answer'].replace('13external systemticks','13delivered timerIRQ2 events with sourceGPU clock updates').replace('13systemclockticks','13externally delivered timerIRQ2 events; physicalperiod/globaltime')
        cp['implementation_authorship']='Coordinator authored timer event/handler translation, early CPU helper translation and Native/C tests; no local-model code-generation prompt or new training in these changes.'
        cp['next_work'][1]='Connect source4000 boot, BIOS and music DSP; replace external timer delivery and later world/movie clock providers with verified global device scheduling; expand transitions and physicalscanout.'
    assert proof['source4000_entry_connected']and not proof['initial_processor_setup_calls_supplied']and not proof['initial_CPU_replaced_at_DD40']and not proof['DSP_music_mailbox_completion_script']
    cp.update(source4000_entry_connected=True,source4000_to_DD40_caller_verified_with_declared_providers=True,initial_processor_setup_calls_supplied=False,initial_CPU_replaced_at_DD40=False,DSP_music_mailbox_completion_script=False,entry_CPU_coverage=proof['entry_CPU_coverage'],music_DSP_bootstrap_proof=read(ROOT/'verification/music-DSP-bootstrap-checks.json'),full_music_mixer_verified=False,standalone_source4000_proof=read(ROOT/'verification/source4000-entry-checks.json'))
    cp['initial_boundary']='Supplied FrozenRAM/initial CPU/device seed at source4000 and canonical pre-relocation GPU source bytes; continuous source4000->DD40->scheduledstartup, no initialized processor-setup calls or replacement CPU atDD40.'
    cp['declared_providers'][0]='Supplied FrozenRAM/CPU/device seed and canonical pre-relocation GPU source bytes; BIOS3000/3048/3006 ABI adapters and305A syntheticTOC. Source4000/processor setup now executes; firmware-complete cold/globalboot remains unverified.'
    cp['declared_providers'].append('Explicit CPU/DSP alternation: music flag init before command2 and source command2 acknowledgement before CPU poll. Music engine is stopped atF1B148 before bank1/mixer/SSI; song pointer3BCE0/index0 only.')
    cp['checked_answer']=cp['checked_answer'].replace('run sourceDD40','run source4000 CPU entry/GPU initialization/musicDSP command2 acknowledgement continuously into sourceDD40').replace('FrozenRAM/CPU/sourceprocessor-setup','FrozenRAM/initialCPU/device/canonicalGPUbytes/BIOS-TOC/CPU-DSPalternation').replace('Full4000/globalboot','Firmware-complete cold/globalboot').replace('physicalscanout/playablegame/nativeChat remain unverified.','bank1 music engine/SSI/mixer/physicalscanout/playablegame/nativeChat remain unverified.')
    cp['implementation_authorship']='Coordinator authored source4000 entry/helper and88instruction musicDSP bootstrap translations and Native/C connection through scheduledstartup/loading/movie/world. Local model code authorship/training/defaults unchanged; BIOS and timing providers disclosed.'
    cp['next_work'][1]='Replace FrozenRAM with verified cold RAM plus stage/firmware load; implement BIOS/timer period/global event schedule and bank1 DSP music/SSI/mixer; expand transitions and physicalscanout.'
    save(ROOT/'verification/startup-loading-movie-world-checkpoint.json',cp);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);p=session/'emulator-runtime/summary.json';data=read(p);data['startup_loading_movie_world_checkpoint']=cp;save(p,data)
    p=ROOT/'verified-previews/scene-previews.json';data=read(p);data['previews']['checked_post_dialogue_plane'].update(relative_png='verified-previews/C-startup-loading-movie-world-plane.png',png_sha256=sha(preview),source_report=cp['report'],verified_caption='Verified C drawing plane after live source system/scheduledstartup/loading/movie and12world cycles. No suppliedstartup/merchant capture or intermediateprocessor reset. InitialRAM/setup and controlledinput/timing/device providers remain; physicalscanout/playability unverified.');save(p,data)
    files=[Path(__file__),ROOT/'scripts/check_biwn_entry_scheduled_startup.py',ROOT/'scripts/check_biwn_startup_retained_GPU.py',ROOT/'scripts/check_biwn_continuous_loading_movie_world.py',ROOT/'scripts/generate_biwn_health_timeout_cpu.py',proof_path,ROOT/'verification/startup-loading-movie-world-checkpoint.json',session/'health-timeout-fullCPU-generation.json',preview,ROOT/'tools/libbiwn-retained-interior-render-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']
    if args.timer:files.extend([ROOT/'verification/GPU-timer-checks.json',ROOT/'verification/entry-setup-helpers-checks.json',ROOT/'scripts/generate_biwn_GPU_timer.py',ROOT/'scripts/check_biwn_GPU_timer.py',ROOT/'scripts/generate_biwn_entry_setup_cpu.py',ROOT/'scripts/check_biwn_entry_setup_helpers.py',src/'biwn_entry_setup_cpu.c',src/'biwn_entry_setup_cpu.h',session/'entry-setup-fullCPU-generation.json'])
    files.extend([ROOT/'scripts/check_biwn_source_entry_boot.py',ROOT/'scripts/generate_biwn_music_DSP_bootstrap.py',ROOT/'scripts/check_biwn_music_DSP_bootstrap.py',ROOT/'verification/music-DSP-bootstrap-checks.json',ROOT/'verification/source4000-entry-checks.json',session/'music-DSP-bootstrap-generation.json'])
    files.extend(src/n for n in proof['source_sha256']);files.extend(src/n.replace('.c','.h')for n in proof['source_sha256']);files.extend(raw.glob('case-*'));files.extend(raw/n for n in ['report.json','status.json','cases.json','coverage.json','compiler.txt','libscheduled-startup.dylib'])
    manifest=[]
    for i,p in enumerate(files):
        dest=out/f'{i:03d}-{p.name}';shutil.copy2(p,dest);assert sha(p)==sha(dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(p)))
    save(out/'checkpoint.json',cp);save(out/'manifest.json',manifest)
    (out/'who-and-prompts.txt').write_text(cp['implementation_authorship']+'\nNo local-model code-generation prompt in this integration. SourceDD40/system/health sleep and sourceCD scheduler resume were connected to live loading/movie/world. Timer-handler status and initial processor setup/clock/input/BIOS/disc/device providers are disclosed in checkpoint.\n')
    p=ROOT/'CURRENT DECOMPILATION.txt';p.write_text('LIVE SOURCE4000 ENTRY TO STARTUP/LOADING/MOVIE/WORLD\n'+now.isoformat()+'\n\n'+cp['checked_answer']+'\n\nAUDIT\n'+str(out)+'\n\nPREVIEW\n'+str(preview)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n\nEARLIER CHECKPOINTS\n'+p.read_text())
    print(json.dumps(dict(status=cp['status'],audit=str(out),profiles=2,startup_capture=False,startup_handoffs=26,total_asset_transfers=18,frames=187,postmovie_cycles=12)))
if __name__=='__main__':main()
