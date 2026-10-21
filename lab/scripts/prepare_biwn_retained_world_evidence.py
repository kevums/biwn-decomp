"""Publish retained movie-to-world task cycles, with exact reference provenance."""
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
REFERENCE=ROOT/'verification/BIWN-retained-world-after-movie/20261014T173259.629365Z'


def main():
    proof=read(ROOT/'verification/BIWN-retained-world-after-movie.json');raw=Path(proof['directory'])
    assert read(raw/'status.json')['status']=='terminal_pass'
    reference=read(REFERENCE/'report.json');assert read(REFERENCE/'status.json')['status']=='terminal_pass'
    assert reference['source_sha256']==proof['source_sha256']
    a=read(REFERENCE/'message-60-native.json');b=read(raw/'message-60-C.json');assert a==b
    state=b['summary'];assert state['CPU']['pc']==0xef88
    assert state['task_cycles']==dict(NPC=12,renderer=12,world=12)
    assert len(state['polls'])==12 and len(state['handoffs'])==60 and len(state['yields'])==60
    first=state['yields'][0]['player'];last=state['yields'][-1]['player']
    assert (first['0x49c50'],first['0x49c56'],last['0x49c50'],last['0x49c56'])==(12832,42400,12832,42398)
    assert 0xf0fa in reference['native_PC_coverage'] and 0x20820 in reference['native_PC_coverage']
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    assert sha(ROOT/'scripts/check_biwn_retained_world_after_movie.py')==proof['script_sha256']
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
    preview=ROOT/'verified-previews/C-post-movie-world-plane.png'
    preview.write_bytes(animation_renderer.image_png(pixels,224,180,3))
    (raw/'C-post-movie-world-plane.CRY16').write_bytes(pixels)
    gpu=state['final_GPU_calls']
    count=lambda key,value:sum(row.get(key)==value for row in gpu)
    assert count('program','movement_4320')==36 and count('program','sprite_4B00')==9
    assert all(count('command',command)==12 for command in ['0x6ae0','0x6da0','0x52e0','0x57a0'])
    now=datetime.now(timezone.utc)
    cp=read(ROOT/'verification/retained-merchant-renderer-checkpoint.json')
    cp.update(recorded_at=now.isoformat(),status=proof['status'],
        checked_answer=('After the source merchant message60 movie187 frames/125 audio enqueues, five source-created '
            'contexts run on retained frames: merchant, renderer, world and two idles. Twelve world/renderer/NPC cycles, '
            '12 emulated input polls and60 source scheduler handoffs match original execution, including full CPU/RAM, '
            'logical GPU/DSP/peripherals, source GPU traces and audio. Player X stays12832; Z moves42400 to42398 under '
            'the supplied button sequence. Camera/targeting execute, with36 movement GPU commands,9 sprite decodes and '
            '12 each interior/actor geometry,projection anddraw commands. No intermediate device reset or geometry GPU reseed. '
            'Initial ready-world task/assets capture, nearby-player/cash0,15 quiescent contexts and five-context unblocking, '
            'source startup, file-backed CD/BIOS3000 no-op, nominal movie clocks, synchronous GPU completion and8-unit '
            'renderer/input clock increments remain supplied. Full boot/source global clocks/firmware, other task bodies, '
            'collision edges/choices/purchases, physical scanout/AV timing and playable complete game remain unverified.'),
        source_renderer_iterations=12,source_world_iterations=12,source_NPC_iterations=12,
        source_idle_contexts=['0xc5928','0xc5528'],source_input_polls=12,source_scheduler_handoffs=60,
        quiescent_contexts=15,source_camera_targeting_executed=True,source_movement_GPU_commands=36,
        source_sprite_GPU_commands=9,source_scene_GPU_commands={command:12 for command in ['0x6ae0','0x6da0','0x52e0','0x57a0']},
        player_checked_coordinates=dict(initial_X=12832,initial_Z=42400,final_X=12832,final_Z=42398),
        supplied_global_clock_step=8,source_global_clock_verified=False,
        declared_providers=['Initial ready-world source-created task/assets capture',
            'Nearby-player XY/cash0;15 task contexts quiescent; renderer/world/two idle contexts unblocked after merchant movement',
            'Controlled emulated button sequence; renderer and input clock increments8 units',
            'Source boot SSP200000 and GPU/DSP startup established before warm merchant resumption',
            'File-backed CD, BIOS3000 no-op, nominal SSI/VBI movie clocks and synchronous GPU completion at source polling'],
        original_reference_directory=str(REFERENCE),original_reference_reused_for_idle_body_replay=True,
        replay_note=('Initial native/C run matched. C replay replaces an idle driver JSR adapter with the existing '
            'task-loop C body, observing its actual stack store before source scheduler call. Entire snapshots match '
            'the saved native reference; identical source C hashes. Replay has no fresh native instruction coverage, '
            'so original coverage remains in the named reference report.'),
        geometry_plane_preview=dict(image_path=str(preview),PNG_sha256=sha(preview),source_dimensions=[224,180],
            raw_sha256=hashlib.sha256(pixels).hexdigest(),pointer=hex(pointer),scope='Saved drawing plane after12 controlled source task cycles; not physical scanout.'),
        implementation_authorship=('Coordinator linked existing world/input/camera/targeting/idle bodies and scheduler '
            'to retained movie/NPC/renderer context. No new local-model code or training;139 selected components/171 '
            'accepted local-model instruction bodies unchanged.'),
        report=str(ROOT/'verification/BIWN-retained-world-after-movie.json'),
        next_work=['Replace the initial ready-world capture with continuous source loading/task creation on retained devices.',
            'Integrate source global clocks/boot/firmware/scanout and remaining tasks; exercise reachable transitions/collision/dialogue choices.',
            'Continue native LM Studio Chat usability and advertising workflows.'])
    save(ROOT/'verification/retained-world-after-movie-checkpoint.json',cp)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    p=session/'emulator-runtime/summary.json';summary=read(p);summary['retained_world_after_movie_checkpoint']=cp;save(p,summary)
    p=ROOT/'verified-previews/scene-previews.json';manifest=read(p)
    manifest['previews']['checked_post_dialogue_plane'].update(relative_png='verified-previews/C-post-movie-world-plane.png',
        png_sha256=sha(preview),source_report=cp['report'],verified_caption=('Verified drawing plane after C merchant dialogue '
            'and12 source world/NPC/renderer cycles with emulated button input. The five source-created contexts share '
            'retained GPU/device state; original execution matches. Initial capture, quiescent tasks and controlled '
            'input/clock/device providers remain; physical scanout and playable full game are unverified.'))
    save(p,manifest)
    out=ROOT/'verification/retained-world-after-movie-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    prior=read(ROOT/'verification/retained-merchant-renderer-review.json')
    files={ROOT/'scripts/check_biwn_retained_world_after_movie.py',Path(__file__),ROOT/'scripts/emulated_pad_input.py',
        ROOT/'verification/BIWN-retained-world-after-movie.json',ROOT/'verification/retained-world-after-movie-checkpoint.json',
        REFERENCE/'report.json',REFERENCE/'message-60-native.json',raw/'message-60-C.json',preview,
        *[src/n for n in proof['source_sha256']]}
    records=[]
    for p in sorted(files):
        dest=out/'snapshot'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        records.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    save(out/'manifest.json',dict(checkpoint=cp,files=records,retained_renderer_bridge_dependency_audit=prior['directory']))
    (out/'who-and-prompts.txt').write_text(cp['implementation_authorship']+'\nNo local-model code-generation prompt in this change. '
        'The native/C task-cycle run and replay are separate records, explicitly linked above. The existing idle body '
        'is observed after its real return-address write. All60 scheduler handoff state snapshots match.\n')
    save(ROOT/'verification/retained-world-after-movie-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — RETAINED MOVIE TO WORLD TASK CYCLES\n'+now.isoformat()+'\n\n'+cp['checked_answer']+'\n\nAudit: '+str(out)+'\nPlane preview: '+str(preview)+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),cycles=12,input_polls=12,handoffs=60,quiescent_contexts=15)))


if __name__=='__main__':main()
