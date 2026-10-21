"""Publish three checked standalone media interfaces, retaining world-test scope."""
import hashlib
import json
import shutil
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    now=datetime.now(timezone.utc).isoformat();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    primary=read(ROOT/'verification/biwn-media-setup-cpu-checks.json')
    extra=read(ROOT/'verification/biwn-media-setup-write16-guard.json')
    directory=Path(primary['directory'])
    assert read(directory/'status.json')['status']=='terminal_pass'
    assert primary['cases']==18 and primary['source_instruction_coverage']==[59,59]
    assert primary['host_guards']==15 and extra['total_host_guards']==16
    assert primary['cart_ROM_writes_ignored_and_contents_retained'] and not primary['original_CPU_execution_on_C_side']
    assert sha(ROOT/'scripts/check_biwn_media_setup_cpu.py')==primary['test_script_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in primary['source_sha256'].items():assert sha(source/name)==digest
    mapping=read(session/'media-setup-fullCPU-generation.json')
    assert mapping['source_sha256']==primary['source_sha256']==extra['source_sha256']
    assert sha(ROOT/'scripts/generate_biwn_media_setup_cpu.py')==mapping['generator_sha256']
    checkpoint=dict(recorded_at=now,status='three_standalone_media_setup_CPU_interfaces_checked',
        functions=[dict(entry='0x18160',role='Initialize display/blitter/TOM state'),
            dict(entry='0xe840',role='Stop DSP, copy source audio image and initialize its control/data registers'),
            dict(entry='0xdc7c',role='Set cartridge-space log pointer and execute the source clear loop')],
        cases=18,source_instruction_coverage=[59,59],host_guards=16,native_CPU_steps=primary['native_CPU_steps'],
        full_CPU_SR_USP_SSP_private_frames_main_RAM_compared=True,
        complete_serialized_GPU_DSP_TOM_JERRY_DAC_and_TOM_RAM_compared=True,Unicorn_C_ordered_bus_compared=True,
        cart_ROM_interval=['0x802000','0x902000'],cart_ROM_contents_retained_in_pinned_mode=True,
        DSP_source_image_bytes=384,DSP_source_postcopy_data_writes=primary['DSP_source_postcopy_data_writes'],
        hardware_scope='Pinned emulator bus/blitter with masked interrupts, supplied matching GPU/DSP RAM and ROM patterns. No physical hardware proof.',
        original_CPU_execution_on_C_side=False,GPU_DSP_execution_or_game_frames_requested=False,
        movie_state_machine_verified=False,audio_playback_verified=False,NPC_message_integration_verified=False,
        native_Chat_verified=False,whole_game_complete=False,playable=False,
        new_components=3,published_components=138,processor_components=dict(CPU=125,GPU=13),
        local_model_instruction_bodies=171,new_local_model_instruction_bodies=0,
        authorship='Coordinator generated source-specific fixed C, interfaces and comparison/guard harnesses. No new model prompts, weight training or default/preset change in this implementation.',
        report=str(ROOT/'verification/biwn-media-setup-cpu-checks.json'),
        extra_guard_report=str(ROOT/'verification/biwn-media-setup-write16-guard.json'),
        source_sha256=primary['source_sha256'],
        checked_answer='Three source setup routines now match original CPU, independent bus execution and C: display initialization, a 384-byte DSP image load with its source data writes, and the cartridge clear loop. Eighteen cases cover all 59 instructions, with 16 host-error guards. This proves setup, not video decoding, audio playback or merchant dialogue.',
        remaining_work=['Reconstruct and verify video state handlers and GPU overlay, then DSP program execution and audio/device timing.',
            'Preserve direct source TRAP0 frames and streaming/synchronization while integrating merchant messages, choice and purchase paths.',
            'Continue other game tasks, boot/global GPU/object-processor scanout and visible native Chat verification.'])
    save(ROOT/'verification/media-setup-checkpoint.json',checkpoint)
    validation=read(session/'boot-slice-validation.json')
    assert validation['portable_C_component_count'] in [135,138]
    validation.update(portable_C_component_count=138,processor_component_counts=dict(CPU=125,GPU=13),
        media_setup_checkpoint=checkpoint,latest_aggregate_update=now,
        component_count_scope='138 selected C components across scoped standalone and connected proofs. Three new CPU media-setup interfaces are standalone; the previous world/input/NPC/render proof retains its 135-component snapshot. Counts are not game-completion percentages.')
    save(session/'boot-slice-validation.json',validation)
    for path in [session/'emulator-runtime/summary.json']+[ROOT/name for name in ['config.json','corpus/game/project-intake.json',
            'verification/setup-status.json','verification/current-runtime-state.json','verification/requirements-audit.json']]:
        state=read(path);state['media_setup_checkpoint']=checkpoint
        if path.name=='requirements-audit.json':state.update(recorded_at_utc=now,
            this_goal_turn_classification='Progress: three new standalone media-setup interfaces accepted by 18 native/Unicorn/C cases, all59sourceinstructions and16guards; full goal incomplete.',next_safe_work=checkpoint['remaining_work'])
        if path.name=='current-runtime-state.json':state.update(recorded_at=now,emulator_jobs='Terminal: media setup comparisons and late write16 guard passed.')
        save(path,state)
    out=ROOT/'verification/media-setup-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');(out/'snapshot').mkdir(parents=True)
    files=[ROOT/'scripts/generate_biwn_media_setup_cpu.py',ROOT/'scripts/check_biwn_media_setup_cpu.py',ROOT/'scripts/check_biwn_media_setup_write16_guard.py',
        ROOT/'scripts/prepare_biwn_media_setup_evidence.py',ROOT/'verification/biwn-media-setup-cpu-checks.json',ROOT/'verification/biwn-media-setup-write16-guard.json',
        ROOT/'verification/media-setup-checkpoint.json',ROOT/'verification/NPC-message-video-dependency-inspection.json',
        source/'biwn_media_setup_cpu.c',source/'biwn_media_setup_cpu.h']
    for path in files:shutil.copy2(path,out/'snapshot'/path.name)
    save(out/'manifest.json',dict(recorded_at=now,files={str(p):sha(p) for p in files},checkpoint=checkpoint,
        fixture_repair='GPUReset randomizes local RAM from an advancing PRNG; the three execution paths now receive matching declared RAM. DSP image assertion includes two actual source postcopy writes. Game source/data were not changed.',whole_goal_complete=False))
    old=(ROOT/'CURRENT DECOMPILATION.txt').read_text();(out/'snapshot/CURRENT DECOMPILATION.before.txt').write_text(old)
    note='BLACK ICE WHITE NOISE — MEDIA SETUP AND CURRENT GAME INTEGRATION\n'+now+'\n\n'+checkpoint['checked_answer']+'\n\n'+(
        'The source clear loop writes across a 1 MB cartridge interval. In the selected pinned bus mode those writes are ignored and the three ROM patterns are retained. This mapping is observed emulator behavior; physical hardware and writable-cartridge modes remain unverified. Full CPU, private/main RAM, serialized hardware states and independent ordered bus effects compare. Source audio-code loading does not establish audio playback.\n\n'
        'CURRENT WORLD TEST\nThe earlier four-case loading/world/input/NPC/renderer proof remains intact: 28 world updates and controller polls, 20 NPC iterations, 112 GPU submissions and 24 sprite decodes, followed by a completed renderer pass with empty queues. Saved drawing planes are not composited scanout or a playable-game capture.\n\n'
        'WHO / PROMPTS\nCoordinator authored the new three-routine C group and tests; no new local-model code prompt or weight training in this implementation. Previous 171 accepted local-model instruction bodies remain unchanged. There are 138 selected components: 125 CPU and 13 GPU. The older world proof retains its 135-component snapshot. Counts are not completion percentages.\n\n'
        'NEXT\n'+'\n'.join(checkpoint['remaining_work'])+'\n\nAUDIT\n'+str(out)+'\nFull goal active/incomplete.\n')
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(note);(out/'readable-results.txt').write_text(note)
    save(ROOT/'verification/media-setup-review.json',dict(recorded_at=now,directory=str(out)))
    print(json.dumps(dict(audit=str(out),selected_components=138,CPU=125,GPU=13,media_setup_cases=18,whole_goal_complete=False)))


if __name__=='__main__':main()
