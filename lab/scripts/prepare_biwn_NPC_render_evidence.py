"""Publish combined NPC/renderer proof and integrity-checked image snapshots."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: json.loads(path.read_text())
save = lambda path, value: path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    now = datetime.now(timezone.utc).isoformat()
    report = read(ROOT/'verification/biwn-scheduled-npc-render-checks.json')
    directory = Path(report['directory'])
    assert read(directory/'status.json')['status']=='terminal_pass'
    assert [report['cases'],report['NPC_iterations'],report['GPU_submissions'],report['C_sprite_decodes'],report['C_resident_blits']]==[4,20,96,4,6552]
    assert report['source_group_instruction_coverage']['npc']==[143,285]
    assert sha(ROOT/'scripts/check_biwn_scheduled_npc_render.py')==report['test_script_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in report['source_sha256'].items():
        assert sha(source/name)==digest
    fixtures=read(directory/'fixtures.json')
    for row in fixtures:
        assert row['native']['GPU_submission_events']==row['C']['GPU_submission_events']
        assert not row['C']['device']['original_GPUExec1_calls'] and not row['C']['device']['scene_render'][8]
        assert row['C']['device']['C_sprite_decodes']==row['native']['device']['original_GPU_sprite_decodes']==1
        assert any(call['target']==0xea28 and call['queue_count_before']>0 and call['queue_count_after']==0 for call in row['C']['calls'])
        assert any(call['target']==0xe0f2 for call in row['C']['calls'])
        ram=(directory/f"case-{row['case']}-C-final-RAM.bin").read_bytes()
        assert hashlib.sha256(ram).hexdigest()==row['after_RAM_sha256']
        assert int.from_bytes(ram[0x112940:0x112942],'big')==0
    ram=(directory/'case-0-C-final-RAM.bin').read_bytes()
    pointer=int.from_bytes(ram[0x43daa:0x43dae],'big')
    assert pointer==int.from_bytes(ram[0xbd844:0xbd848],'big')
    assert (directory/'C-final-geometry.raw16be').read_bytes()==ram[pointer:pointer+80640]
    sprite=read(directory/'NPC-sprite-preview.json')
    assert sprite['dimensions']==[40,87]
    assert sha(directory/'C-decoded-NPC-sprite.raw16be')==sprite['raw_sha256']
    previews=ROOT/'verified-previews'
    previews.mkdir(exist_ok=True)
    manifest={'recorded_at':now,'source_report':str(ROOT/'verification/biwn-scheduled-npc-render-checks.json'),'previews':{}}
    specifications=[('checked_NPC_sprite','C-decoded-NPC-sprite.png','C-NPC-sprite.png',[40,87],
                     'Verified NPC sprite decoded by the C game reconstruction during the matched loading, actor and renderer test. These are saved sprite pixels, not a complete game viewport or physical-hardware capture.'),
                    ('checked_interior_plane','C-final-geometry.png','C-interior-geometry.png',[224,180],
                     'Verified interior geometry plane from the matched C loading, NPC and renderer test. This saved plane is not composited object-processor scanout or an interactive playable game.')]
    for key,original,target,dimensions,caption in specifications:
        shutil.copy2(directory/original,previews/target)
        manifest['previews'][key]={'relative_png':'verified-previews/'+target,'png_sha256':sha(previews/target),
            'source_dimensions':dimensions,'preview_scale':3,'verified_caption':caption,
            'original_reference_pixels_match':True,'pinned_emulator_CRY_conversion':True,
            'physical_hardware_validation':False,'live_gameplay':False,'source_report':manifest['source_report']}
    save(previews/'scene-previews.json',manifest)
    checkpoint={key:report[key]for key in ['recorded_at','status','cases','source_interiors','disc_transfers','transferred_bytes',
        'task_removals','task_creations','NPC_iterations','GPU_submissions','C_sprite_decodes','C_resident_blits','native_CPU_steps',
        'source_group_instruction_coverage','limits']}
    checkpoint.update(report=manifest['source_report'],selected_components=135,processor_components={'CPU':122,'GPU':13},
        new_components=0,actual_source_created_NPC_executed=True,renderer_runnable_during_loading_and_actor=True,
        sprite_queue_consumption_verified=True,all_final_sprite_queues_empty=True,mode2_scene_overlay_formatter_text_displaylist_linked=True,
        full_CPU_main2MBRAM_privateframes_observed_helpers_scheduler_disc_events_compared=True,
        per_render_GPU_logical_architecture_RAM_direct_PC_count_hash_compared=True,original_CPU_or_GPU_execution_on_C_side=False,
        generated_NPC_instruction_coverage=[143,285],NPC_source_unchanged_since21_guard_proof=True,
        geometry_GPU_reset_seed_RAM_resident_fixture_retained=True,global_GPU_context_proved=False,shared_pinned_blitter=True,
        dialogue_message_purchase_paths_verified=False,natural_walking_input_verified=False,uninterrupted_world_loop_verified=False,
        composited_scanout_verified=False,physical_hardware_validation=False,whole_game_complete=False,playable=False,native_Chat_verified=False,
        previews=manifest['previews'],decoded_sprite_dimensions=[40,87],decoded_sprite_is_not_proof_of_NPC_visible_in_final_geometry_plane=True,
        local_model_instruction_bodies=171,new_code_authorship='Coordinator integration harness; accepted CPU/GPU code unchanged, no new local-model code prompt/training.',
        checked_renderer_answer='The current four-case test runs the source-created NPC and the renderer together. The C queue consumer decodes its sprite, renders the indoor scene and executes overlay/text/display-list code;20NPCiterations and96render commands match the original reference.',
        checked_playability_answer='The game is not playable yet. Natural world/player input,merchant dialogue/purchases,other tasks/audio/boot/globalGPU/scanout and hardware/backend accuracy remain unfinished.',
        next_work=['Connect actual indoor world/player input/camera and remaining tasks to the live loading/NPC/renderer path.',
                   'Exercise merchant dialogue/message/input/purchase and additional loader/factory/boot/audio/scanout/GPU paths.',
                   'Validate visible native Chat and reliable game/advertising inference; prior model semantic/output failures remain open.'])
    save(ROOT/'verification/scheduled-NPC-render-checkpoint.json',checkpoint)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    for name in ['boot-slice-validation.json','emulator-runtime/summary.json']:
        path=session/name;state=read(path);state['scheduled_NPC_render_checkpoint']=checkpoint;save(path,state)
    for name in ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/requirements-audit.json']:
        path=ROOT/name;state=read(path);state['scheduled_NPC_render_checkpoint']=checkpoint
        if name=='verification/requirements-audit.json':
            state.update(recorded_at_utc=now,this_goal_turn_classification='Progress: four matched scheduled loading/NPC/renderer cases,20NPCiterations,96renderGPUcommands,4decoded sprites,6552residentblits. Full goal active.',next_safe_work=checkpoint['next_work'])
        if name=='verification/current-runtime-state.json':
            state.update(recorded_at=now,emulator_jobs='Terminal: four combined source loading/NPC/renderer cases passed. No active emulator job.')
        save(path,state)
    out=ROOT/'verification/scheduled-NPC-render-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    (out/'snapshot').mkdir(parents=True)
    files=[ROOT/'scripts/check_biwn_scheduled_npc_render.py',ROOT/'scripts/prepare_biwn_NPC_render_evidence.py',
           ROOT/'verification/biwn-scheduled-npc-render-checks.json',ROOT/'verification/scheduled-NPC-render-checkpoint.json',
           previews/'scene-previews.json',previews/'C-NPC-sprite.png',previews/'C-interior-geometry.png']
    for path in files:shutil.copy2(path,out/'snapshot'/path.name)
    save(out/'manifest.json',{'recorded_at':now,'files':{str(path):sha(path)for path in files},'checkpoint':checkpoint,
        'repair':'First native reference stalled at E2EA because spriteGPU4B00completion was not dispatched. Restored the same synchronous device completion hook used by earlier queue tests. No source instructions/actors/frames/data changed or masked.',
        'whole_goal_complete':False})
    note='BLACK ICE WHITE NOISE — SOURCE LOADING / NPC / RENDERER TOGETHER\n'+now+'\n\n'+(
        'Four controlled gate/stair/NPC/renderer cases match original native CPU/GPU versus C.20NPCiterations,96render GPU submissions,4actual model21 sprite decodes and6,552resident blits. Source queue consumption,mode2scene/geometry/projection/draw,overlay/formatter/text/displaylist run alongside source-created EDC4,scheduled loading and asset cleanup/removal. Full CPU/SR/both stack banks,whole2MBRAM/private frames,observed helper/scheduler/disc events and each renderGPU logical4396-byte state/RAM/directPC count/hash compare.24CDtransfers/1,399,216bytes,4task creations,12removals,605,436native reference CPUsteps. No originalCPU/GPU instructions on Cside. NPC group143/285instructions exercised; source unchanged from21host-guard proof. All final sprite queues are empty.\n\n'
        'IMAGES\nDecoded NPCsprite40x87 from real model21 data, and matched interior geometry plane224x180, exported with pinned CRY colors/3x scaling. The sprite is shown separately; it is not proof that the NPC is visible in the final geometry crop. Neither image is composited objectprocessor scanout or live playablegame.\n'+str(previews/'C-NPC-sprite.png')+'\n'+str(previews/'C-interior-geometry.png')+'\n\n'
        'LIMITS\nCaptured post-startup renderer CPU,host-prepared boundary entry/pose/button/kill,blocked other tasks/world,BIOS and external CD completion remain fixtures. GPU6AE0per-frame reset/seed/fixedRAM/resident injection and shared pinned blitter remain; globalGPUcontext/physicaltiming/FPS/backendaccuracy/scanout unproved. Merchant dialogue/messages/purchases,natural player input and uninterrupted worldloop,other tasks/audio/boot and full playablegame remain unfinished.\n\n'
        'WHO / PROMPTS\nCoordinator integrated existing checked CPU/GPU code; no new sourceC/model code prompt/training/default/preset change.171prior local-model instruction bodies and135selectedcomponents(122CPU/13GPU) unchanged; no completionpercentage. Advertising assistant/lesson retained; nativeChat and general local inference still unverified.\n\n'
        'NEXT\n'+'\n'.join(checkpoint['next_work'])+'\n\nAUDIT\n'+str(out)+'\nFull goal active/incomplete.\n')
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(note);(out/'readable-results.txt').write_text(note)
    save(ROOT/'verification/scheduled-NPC-render-review.json',{'recorded_at':now,'directory':str(out)})
    print(json.dumps({'audit':str(out),'cases':4,'NPC_iterations':20,'render_GPU_commands':96,'decoded_sprites':4,'whole_goal_complete':False}))


if __name__=='__main__':main()
