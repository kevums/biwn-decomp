"""Publish connected source loading/task creation/movie/world, with remaining initial capture."""
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import animation_renderer
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REFERENCE=ROOT/'verification/BIWN-continuous-loading-movie-world/20261014T175447.423783Z'


def main():
    proof=read(ROOT/'verification/BIWN-continuous-loading-movie-world.json');raw=Path(proof['directory'])
    assert read(raw/'status.json')['status']=='terminal_pass'
    reference=read(REFERENCE/'native-reference-manifest.json')
    assert reference['status']=='native_phase_completed_before_C_provider_mapping_failure'
    assert sha(REFERENCE/'message-60-native.json')==reference['native_endpoint_sha256']
    assert sha(REFERENCE/'message-60-native-final-RAM.bin')==reference['native_RAM_sha256']
    assert sha(REFERENCE/'native-reference-script.py')==reference['script_sha256']
    a=read(REFERENCE/'message-60-native.json');b=read(raw/'message-60-C.json');assert a==b
    state=b['summary'];assert state['CPU']['pc']==0xef88
    assert state['task_cycles']==dict(NPC=12,renderer=12,world=12)
    assert len(state['polls'])==14 and len(state['handoffs'])==60 and len(state['yields'])==60
    first=state['yields'][0]['player'];last=state['yields'][-1]['player']
    assert (first['0x49c50'],first['0x49c56'],last['0x49c50'],last['0x49c56'])==(12832,42400,12832,42398)
    assert not proof['ready_merchant_capture_supplied'] and proof['source_loading_and_task_creation_connected']
    assert len(state['asset_disc_requests'])==6 and len(state['asset_disc_completions'])==6
    assert sum(r['bytes'] for r in state['asset_disc_requests'])==349804
    assert len([e for e in state['prefix_events'] if e['kind']=='source_loading_handoff'])==35
    assert any(e.get('context')=='0xc1528' and e['CPU']['pc']==0xedc4 for e in state['prefix_events'] if e['kind']=='source_loading_handoff')
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    assert sha(ROOT/'scripts/check_biwn_continuous_loading_movie_world.py')==proof['script_sha256']
    ram=(raw/'message-60-C-final-RAM.bin').read_bytes()
    assert ram==(REFERENCE/'message-60-native-final-RAM.bin').read_bytes()
    get=lambda a:int.from_bytes(ram[a:a+4],'big')
    current=get(0xc0920);obj=current;tasks=[]
    for _ in range(128):
        tasks.append(obj);obj=get(obj)
        if obj==current:break
    else:raise AssertionError('Task ring bound')
    assert len(tasks)==20 and sum(get(t+26)!=0 for t in tasks)==15
    pointer=get(0x43daa);assert pointer==get(0xbd844)
    pixels=ram[pointer:pointer+80640];assert len(pixels)==80640
    preview=ROOT/'verified-previews/C-continuous-loading-movie-world-plane.png'
    preview.write_bytes(animation_renderer.image_png(pixels,224,180,3))
    (raw/'C-continuous-loading-movie-world-plane.CRY16').write_bytes(pixels)
    gpu=state['final_GPU_calls']
    count=lambda key,value:sum(row.get(key)==value for row in gpu)
    assert count('program','movement_4320')==36 and count('program','sprite_4B00')==7
    assert all(count('command',command)==12 for command in ['0x6ae0','0x6da0','0x52e0','0x57a0'])
    now=datetime.now(timezone.utc)
    cp=read(ROOT/'verification/retained-world-after-movie-checkpoint.json')
    cp.update(recorded_at=now.isoformat(),status=proof['status'],
        checked_answer=('Earlier startup capture plus controlled doorway/stair entries312->313->314 now drive source loading, '
            'task removal/reuse/creation and merchant cold initialization directly into message60 movie187 frames/125 audio '
            'enqueues and12 later world/NPC/renderer cycles with two idles. No ready-merchant CPU/RAM capture, intermediate '
            'CPU/GPU/DSP reset or standalone frame RAM clearing. Source loading makes6 file-backed transfers/349804 bytes '
            'with35 source handoffs, then merchant context C1528 enters EDC4 and initializes model21/output allocation. '
            'The two paths receive nearby-player/cash0 at sourceEE20; added C host stop READY does not execute a guest opcode. '
            '14 world input polls total include2 before the movie and12 after;60 post-movie handoffs,36 movement GPU commands, '
            '7 sprite decodes and12 each interior/actor geometry,projection anddraw commands match original. FullCPU/RAM, '
            'logicalGPU/DSP/peripherals, traces/audio and prefix events match. Earlier startup capture, controlled doorway '
            'and stair poses/entries/world-loop restore/near-player/buttons/task quiescence, source startup, file-backed '
            'CD/BIOS/nominal clocks/synchronous GPU completion remain supplied. Full boot/source globalclocks/firmware, '
            'remaining tasks/other choices/purchases/collision edges,physicalscanout/AV timing/playablefullgame remain unverified.'),
        source_renderer_iterations=12,source_world_iterations=12,source_NPC_iterations=12,
        source_idle_contexts=['0xc5928','0xc5528'],source_input_polls=14,post_movie_input_polls=12,pre_movie_input_polls=2,source_scheduler_handoffs=60,source_loading_handoffs=35,source_loading_requests=6,source_loading_bytes=349804,ready_merchant_capture_supplied=False,earlier_startup_capture_supplied=True,source_loading_creation_coldinit_connected=True,source_ready_boundary_PC="0xee20",standalone_frame_RAM_clearing=False,
        quiescent_contexts=15,source_camera_targeting_executed=True,source_movement_GPU_commands=36,
        source_sprite_GPU_commands=7,source_scene_GPU_commands={command:12 for command in ['0x6ae0','0x6da0','0x52e0','0x57a0']},
        player_checked_coordinates=dict(initial_X=12832,initial_Z=42400,final_X=12832,final_Z=42398),
        supplied_global_clock_step=8,source_global_clock_verified=False,
        declared_providers=['Earlier startup CPU/RAM capture before doorway/loading path; original21-task startup origin remains separate',
            'Controlled doorway/stair312->313->314 poses/entries and explicit world-loop entry restore',
            'Nearby-player XY/cash0 supplied at sourceEE20;15 othercontexts quiescent; controlled emulated buttons',
            'Source boot SSP200000 and GPU/DSP startup established before loading; no fixed standalone frame RAM clear',
            'Asset CD provider with witness674-byte track phase completes after actual source handoff; movie file-backed CD/BIOS3000 no-op/nominal SSI/VBI clocks',
            'Synchronous GPU completion at source polling;8-unit renderer/world-input clock increments'],
        original_reference_directory=str(REFERENCE),original_reference_reused_for_C_integration_replay=True,
        replay_note=('Original path completed before C mapping failures. C getter/asset init/resource-yield routing were '
            'linked; an added C stop atEE20 aligns near-player input with the native boundary. World input stimulus is '
            'restricted to world context, preventing movie polls from changing the supplied globalclock. C replay matches '
            'the complete saved original snapshots. Reference hashes/script preserved; no fresh native coverage claimed in replay.'),
        geometry_plane_preview=dict(image_path=str(preview),PNG_sha256=sha(preview),source_dimensions=[224,180],
            raw_sha256=hashlib.sha256(pixels).hexdigest(),pointer=hex(pointer),scope='Saved drawing plane after12 controlled source task cycles; not physical scanout.'),
        implementation_authorship=('Coordinator connected existing loading/transition/task/resource/CD/NPC/world/render '
            'bodies, added host observation API atEE20 and removed standalone RAM clearing for this path. All new integration '
            'code is coordinator-authored; no new local-model code or training;139 selected components/171 accepted local-model bodies unchanged.'),
        report=str(ROOT/'verification/BIWN-continuous-loading-movie-world.json'),
        next_work=['Replace the earlier startup capture and controlled entry/pose/world-loop restore with continuous source boot/input-driven loading.',
            'Integrate source global clocks/boot/firmware/scanout and remaining tasks; exercise reachable transitions/collision/dialogue choices.',
            'Continue native LM Studio Chat usability and advertising workflows.'])
    save(ROOT/'verification/continuous-loading-movie-world-checkpoint.json',cp)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    p=session/'emulator-runtime/summary.json';summary=read(p);summary['continuous_loading_movie_world_checkpoint']=cp;save(p,summary)
    p=ROOT/'verified-previews/scene-previews.json';manifest=read(p)
    manifest['previews']['checked_post_dialogue_plane'].update(relative_png='verified-previews/C-continuous-loading-movie-world-plane.png',
        png_sha256=sha(preview),source_report=cp['report'],verified_caption=('Verified drawing plane from C source doorway/stair '
            'loading, merchant creation/coldinit, movie and12 world/NPC/renderer cycles. No ready-merchant capture or intermediate '
            'CPU/GPU/DSP reset; original execution matches. Earlier startup capture and controlled entry/input/clock/device '
            'providers remain; physical scanout and playable full game are unverified.'))
    save(p,manifest)
    out=ROOT/'verification/continuous-loading-movie-world-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    prior=read(ROOT/'verification/retained-merchant-renderer-review.json')
    files={ROOT/'scripts/check_biwn_continuous_loading_movie_world.py',Path(__file__),ROOT/'scripts/emulated_pad_input.py',ROOT/'scripts/generate_biwn_npc_cpu.py',src/'biwn_npc_cpu.h',ROOT/'scripts/check_biwn_movie_source_boot_exit_AV.py',ROOT/'verification/NPC-first-loop-boundary-contract.json',
        ROOT/'verification/BIWN-continuous-loading-movie-world.json',ROOT/'verification/continuous-loading-movie-world-checkpoint.json',
        REFERENCE/'native-reference-manifest.json',REFERENCE/'native-reference-script.py',REFERENCE/'message-60-native.json',raw/'message-60-C.json',preview,
        *[src/n for n in proof['source_sha256']]}
    records=[]
    for p in sorted(files):
        dest=out/'snapshot'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        records.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    save(out/'manifest.json',dict(checkpoint=cp,files=records,retained_renderer_bridge_dependency_audit=prior['directory']))
    (out/'who-and-prompts.txt').write_text(cp['implementation_authorship']+'\nNo local-model code-generation prompt in this change. '
        'The completed original path and C integration replay are separate records. GetterDFA6/asset-init101E0 providers and resource/CD continuation were linked; sourceEE20 near-input and world-only polling boundaries corrected. Existing idle body '
        'is observed after its real return-address write. All35 loading and60 postmovie source handoffs, full CPU/RAM/devices, source movie stages and queues match.\n')
    save(ROOT/'verification/continuous-loading-movie-world-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CONNECTED SOURCE LOADING TO MERCHANT/MOVIE/WORLD\n'+now.isoformat()+'\n\n'+cp['checked_answer']+'\n\nAudit: '+str(out)+'\nPlane preview: '+str(preview)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),cycles=12,input_polls=14,loading_requests=6,loading_bytes=349804,post_movie_handoffs=60,ready_merchant_capture=False)))


if __name__=='__main__':main()
