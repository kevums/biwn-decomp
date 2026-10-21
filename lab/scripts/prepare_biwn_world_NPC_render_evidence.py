"""Publish scoped source world/input/NPC/render proof without replacing older proofs."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    now=datetime.now(timezone.utc).isoformat()
    report_path=ROOT/'verification/biwn-scheduled-world-NPC-render-checks.json'
    report=read(report_path);directory=Path(report['directory'])
    assert read(directory/'status.json')['status']=='terminal_pass'
    assert [report[k] for k in ['cases','world_updates','input_polls','NPC_iterations',
        'GPU_submissions','C_sprite_decodes','C_resident_blits']]==[4,28,28,20,112,24,7552]
    assert report['source_group_instruction_coverage']['world-flow']==[159,284]
    assert sha(ROOT/'scripts/check_biwn_scheduled_world_NPC_render.py')==report['test_script_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in report['source_sha256'].items():assert sha(source/name)==digest
    guards=read(ROOT/'verification/biwn-world-flow-guard-checks.json')
    assert guards['host_guards']==21 and guards['status']=='world_flow_host_guards_pass'
    for name,digest in guards['source_sha256'].items():assert sha(source/name)==digest
    fixtures=read(directory/'fixtures.json');moved_cases=0;movement_examples=[]
    for row in fixtures:
        for key in ['calls','events','disc_requests','disc_completions','disc_stops',
            'GPU_submission_events','world_updates','poll_inputs']:
            assert row['native'][key]==row['C'][key]
        state=row['C'];assert state['device']['C_sprite_decodes']==row['native']['device']['original_GPU_sprite_decodes']
        assert not state['device']['original_GPUExec1_calls'] and not state['device']['scene_render'][8]
        assert len(state['world_updates'])==len(state['poll_inputs']) in [4,10]
        assert any(p['buttons']==[0] and p['held']==1048576 and p['pressed']==0 for p in state['poll_inputs'])
        changes=[dict(before=u['player_before']['0x49c56'],after=u['player_after']['0x49c56'])
            for u in state['world_updates'] if u['player_before']['0x49c56']!=u['player_after']['0x49c56']]
        assert changes==[dict(before=42208,after=42206)]
        moved_cases+=bool(changes);movement_examples.append(dict(case=row['case'],Z=changes))
        ram=(directory/f"case-{row['case']}-C-final-RAM.bin").read_bytes()
        assert hashlib.sha256(ram).hexdigest()==row['after_RAM_sha256']
        assert int.from_bytes(ram[0x112940:0x112942],'big')==0
    ram=(directory/'case-0-C-final-RAM.bin').read_bytes()
    pointer=int.from_bytes(ram[0x43daa:0x43dae],'big')
    assert pointer==int.from_bytes(ram[0xbd844:0xbd848],'big')
    assert (directory/'C-final-geometry.raw16be').read_bytes()==ram[pointer:pointer+80640]
    sprite=read(directory/'NPC-sprite-preview.json')
    assert sprite['dimensions']==[24,89] and sprite['matches_source_created_NPC_model']
    assert sha(directory/'C-decoded-NPC-sprite.raw16be')==sprite['raw_sha256']
    previews=ROOT/'verified-previews';manifest=dict(recorded_at=now,source_report=str(report_path),previews={})
    specs=[('checked_NPC_sprite','C-decoded-NPC-sprite.png','C-world-NPC-sprite.png',[24,89],
        'Verified NPC sprite decoded during the matched C world-input, loading, NPC and renderer test. This is a saved sprite, not a complete game viewport or physical-hardware capture.'),
        ('checked_interior_plane','C-final-geometry.png','C-world-interior-geometry.png',[224,180],
        'Verified interior drawing plane from the matched C world-input, loading, NPC and renderer test. This saved plane is not composited object-processor scanout or an interactive playable game.')]
    for key,original,target,dimensions,caption in specs:
        shutil.copy2(directory/original,previews/target)
        manifest['previews'][key]=dict(relative_png='verified-previews/'+target,png_sha256=sha(previews/target),
            source_dimensions=dimensions,preview_scale=3,verified_caption=caption,original_reference_pixels_match=True,
            pinned_emulator_CRY_conversion=True,physical_hardware_validation=False,live_gameplay=False,source_report=str(report_path))
    save(previews/'scene-previews.json',manifest)
    checkpoint={k:report[k] for k in ['recorded_at','status','cases','source_interiors','disc_transfers','transferred_bytes',
        'task_removals','task_creations','world_updates','input_polls','NPC_iterations','GPU_submissions','C_sprite_decodes',
        'C_resident_blits','native_CPU_steps','source_group_instruction_coverage','limits']}
    checkpoint.update(report=str(report_path),selected_components=135,processor_components=dict(CPU=122,GPU=13),new_components=0,
        world_task_blocked_after_loading=False,bounded_world_loop_with_NPC_and_renderer_verified=True,
        input_poll_dispatch_camera_targeting_source_bodies_linked=True,emulated_buttons_press_hold_release_verified=True,
        emulated_input_player_position_change_cases=moved_cases,player_position_examples=movement_examples,
        source_world_flow_instruction_coverage=[159,284],world_flow_host_guards=21,
        NPC_instruction_coverage_in_this_test=[137,285],all_final_sprite_queues_empty=True,
        original_CPU_or_GPU_execution_on_C_side=False,full_CPU_RAM_privateframes_observed_helpers_events_compared=True,
        per_render_GPU_logical_architecture_RAM_direct_PC_count_hash_compared=True,
        source_world_flow_coordinator_authored=True,local_model_instruction_bodies=171,
        physical_controller_verified=False,uninterrupted_boot_world_lifecycle_verified=False,
        dialogue_message_purchase_paths_verified=False,all_task_bodies_verified=False,audio_verified=False,
        composited_scanout_verified=False,global_GPU_context_proved=False,shared_pinned_blitter=True,
        whole_game_complete=False,playable=False,native_Chat_verified=False,previews=manifest['previews'],
        decoded_NPC_sprite=sprite,decoded_sprite_is_not_proof_of_NPC_visible_in_final_geometry_plane=True,
        checked_progress_answer='The controlled indoor test now runs the world loop, controller polling, input dispatch and camera alongside the NPC and renderer. Four cases match the original: 28 world updates and polls, 20 NPC iterations, 112 render submissions and 24 sprite decodes, including press/hold/release and a small player-position change. The renderer finishes a pass after NPC removal; all final queues are empty.',
        checked_playability_answer='The full game is unfinished. Other tasks, dialogue/purchases, boot, audio, physical controller input, global GPU context and composited scanout still need work. Entry, pose, clock, disc-completion and NPC-kill fixtures remain.',
        next_work=['Connect additional world interactions and NPC dialogue/message/purchase paths without host entry/kill fixtures.',
            'Integrate remaining tasks, boot, audio and object-processor scanout; verify full game behavior.',
            'Test current evidence, images and advertising research/education through visible native LM Studio Chat.'])
    save(ROOT/'verification/scheduled-world-NPC-render-checkpoint.json',checkpoint)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    for path in [session/'boot-slice-validation.json',session/'emulator-runtime/summary.json']+[ROOT/name for name in
        ['config.json','corpus/game/project-intake.json','verification/setup-status.json','verification/current-runtime-state.json','verification/requirements-audit.json']]:
        state=read(path);state['scheduled_world_NPC_render_checkpoint']=checkpoint
        if path.name=='requirements-audit.json':state.update(recorded_at_utc=now,
            this_goal_turn_classification='Progress: source world/input/camera linked with loading/NPC/renderer, four matched cases and 21 world-flow guards.',next_safe_work=checkpoint['next_work'])
        if path.name=='current-runtime-state.json':state.update(recorded_at=now,
            emulator_jobs='Terminal: four combined world/input/loading/NPC/renderer cases and 21 guards passed.')
        save(path,state)
    out=ROOT/'verification/scheduled-world-NPC-render-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    (out/'snapshot').mkdir(parents=True)
    files=[report_path,ROOT/'verification/scheduled-world-NPC-render-checkpoint.json',ROOT/'verification/biwn-world-flow-guard-checks.json',
        ROOT/'scripts/check_biwn_scheduled_world_NPC_render.py',ROOT/'scripts/generate_biwn_world_flow_cpu.py',
        ROOT/'scripts/check_biwn_world_flow_guards.py',ROOT/'scripts/prepare_biwn_world_NPC_render_evidence.py',
        source/'biwn_world_flow_cpu.c',source/'biwn_world_flow_cpu.h',previews/'scene-previews.json',
        previews/'C-world-NPC-sprite.png',previews/'C-world-interior-geometry.png']
    for path in files:shutil.copy2(path,out/'snapshot'/path.name)
    save(out/'manifest.json',dict(recorded_at=now,files={str(p):sha(p) for p in files},checkpoint=checkpoint,
        observation_repair='Reference observer extended to include nested camera and movement provider calls; final CPU/RAM already matched before this repair. No original game instructions or data altered.',whole_goal_complete=False))
    note='BLACK ICE WHITE NOISE — WORLD INPUT, NPC AND RENDERER TOGETHER\n'+now+'\n\n'+(
        checkpoint['checked_progress_answer']+'\n\nAll CPU registers, SR, both stack banks, private frames, 2 MB RAM, observed helper calls, disc/scheduler events and each render GPU state/RAM/PC trace match. The C side executes no original game CPU/GPU instructions. There are 24 disc transfers, 4 task creations and 12 removals across these cases.\n\n'
        'IMAGES\nThe saved drawing plane includes scene and actor pixels. The NPC sprite is separately identified by its source-created actor model. Neither is object-processor scanout or a playable-game capture.\n'+str(previews/'C-world-NPC-sprite.png')+'\n'+str(previews/'C-world-interior-geometry.png')+'\n\n'
        'LIMITS\n'+checkpoint['checked_playability_answer']+' World-flow coverage is 159 of 284 instructions; 21 error-contract guards passed. NPC coverage in this test is 137 of 285 instructions; the older renderer-only proof separately covered 143. Counts are not completion percentages.\n\n'
        'WHO / PROMPTS\nCoordinator generated and integrated the separate source world-flow candidate. Older accepted source remains intact. No new local-model code prompts, weight training or model-default changes in this integration. The previous 171 local-model instruction bodies and 135 selected components remain unchanged.\n\n'
        'NEXT\n'+'\n'.join(checkpoint['next_work'])+'\n\nAUDIT\n'+str(out)+'\nFull goal active/incomplete.\n')
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(note);(out/'readable-results.txt').write_text(note)
    save(ROOT/'verification/scheduled-world-NPC-render-review.json',dict(recorded_at=now,directory=str(out)))
    print(json.dumps(dict(audit=str(out),cases=4,world_updates=28,NPC_iterations=20,sprite_decodes=24,whole_goal_complete=False)))


if __name__=='__main__':main()
