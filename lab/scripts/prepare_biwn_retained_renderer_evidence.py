"""Publish source merchant-to-renderer continuity and its supplied boundaries."""
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    proof=read(ROOT/'verification/BIWN-retained-merchant-renderer.json');raw=Path(proof['directory'])
    assert read(raw/'status.json')['status']=='terminal_pass'
    a=read(raw/'message-60-native.json');b=read(raw/'message-60-C.json');assert a==b
    state=b['summary'];assert state['CPU']['pc']==0xef88
    assert state['renderer_begin']['pc']==0x17dce and state['renderer_end']['pc']==0xdf60
    assert (state['render_queue_before'],state['render_queue_after'])==(2,0)
    gpu=state['final_GPU_calls'];sprites=[x for x in gpu if x.get('program')=='sprite_4B00']
    commands=[x['command'] for x in gpu if x.get('program')=='retained_scene']
    assert len(sprites)==2 and commands==['0x6ae0','0x6da0','0x52e0','0x57a0']
    assert not proof['renderer_geometry_GPU_reset']
    src=ROOT/'projects/black-ice-white-noise/restoration'
    for n,h in proof['source_sha256'].items():assert sha(src/n)==h
    assert sha(ROOT/'scripts/check_biwn_retained_merchant_renderer.py')==proof['script_sha256']
    standalone=read(ROOT/'verification/BIWN-sprite-fullGPU.json')
    assert standalone['cases']==244 and standalone['source_instruction_coverage']==[198,214]
    assert read(Path(standalone['directory'])/'status.json')['status']=='terminal_pass'
    preview=read(raw/'plane-preview.json');assert sha(Path(preview['image_path']))==preview['PNG_sha256']
    ram=(raw/'message-60-C-final-RAM.bin').read_bytes()
    assert ram==(raw/'message-60-native-final-RAM.bin').read_bytes()
    bridge=read(ROOT/'verification/retained-interior-render-device-build.json')
    assert sha(Path(bridge['command'][-1]))==bridge['library_sha256']
    # Two source-created contexts execute after controlled quiescence.
    get=lambda a:int.from_bytes(ram[a:a+4],'big')
    current=get(0xc0920);obj=current;tasks=[]
    for _ in range(128):
        tasks.append(obj);obj=get(obj)
        if obj==current:break
    else:raise AssertionError('Task ring bound')
    assert len(tasks)==20 and sum(get(t+26)!=0 for t in tasks)==18
    now=datetime.now(timezone.utc)
    cp=read(ROOT/'verification/retained-merchant-movement-checkpoint.json')
    cp.update(recorded_at=now.isoformat(),status=proof['status'],
        checked_answer=('The source-created merchant chooses message60, plays187 movie frames with125 audio enqueues, '
            'then resumes state2/facing/animation/movement and yields into the source-created renderer at17DCE. '
            'One renderer iteration consumes two queued sprites, executes6AE0 interior geometry,6DA0 actor geometry, '
            '52E0 projection and57A0 drawing, then sourceDF60 yields back to merchantEF88. Native/C fullCPU/RAM, '
            'logicalGPU/DSP, peripheral state, GPU traces and audio match. No intermediate device reset or geometry GPU reseed. '
            'Initial ready-world capture, nearby-player/cash0,18 quiescent task contexts, renderer unquiescence, source startup '
            'and file-backed disc/BIOS3000/nominal clocks/synchronous GPU completion remain supplied. '
            '244 standalone sprite cases match198/214 classified instructions;16 unreached rows are listed. '
            'Full boot, global world/task timing, collision edges, other dialogue choices/purchases, physical scanout/AV timing '
            'and playable complete game remain unverified.'),
        renderer_after_dialogue_verified=True,source_renderer_iterations=1,source_created_renderer_task='0xc0d28',
        source_renderer_entry='0x17dce',source_renderer_yield='0xdf60',source_return_to_merchant='0xef88',
        renderer_queue_before=2,renderer_queue_after=0,source_sprite_GPU_commands=2,
        source_scene_GPU_commands=commands,renderer_geometry_GPU_reset=False,
        source_renderer_device_reset=False,standalone_sprite_cases=244,standalone_sprite_instruction_coverage=[198,214],
        standalone_sprite_uncovered_instructions=16,quiescent_contexts=18,source_created_task_ring_contexts=20,
        geometry_plane_preview=preview,
        declared_providers=['Initial ready-world source-created task/assets capture',
            'Nearby-player XY and cash0;18 other task contexts quiescent; renderer unblocked after merchant movement',
            'Source boot SSP200000 and source GPU/DSP startup established before warm merchant resumption',
            'File-backed CD, BIOS3000 no-op, nominal SSI/VBI movie clocks',
            'Synchronous GPU completion at source polling; renderer clock advances600 units at each source clock read'],
        implementation_authorship=('Coordinator generated the inherited-state sprite GPU variant and renderer bridge, '
            'linked existing source CPU/GPU bodies and compared the retained source task handoff/renderer loop. '
            'No new local-model code or training;139 selected components/171 accepted local-model bodies remain unchanged.'),
        report=str(ROOT/'verification/BIWN-retained-merchant-renderer.json'),
        next_work=['Continue repeated merchant/renderer/world loops and reachable collision/choice branches on this retained context.',
            'Replace initial ready-world capture with continuous source loading/task creation; integrate source global clocks/firmware/boot/scanout.',
            'Continue native LM Studio Chat usability and advertising workflows.'])
    save(ROOT/'verification/retained-merchant-renderer-checkpoint.json',cp)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    p=session/'emulator-runtime/summary.json';summary=read(p);summary['retained_merchant_renderer_checkpoint']=cp;save(p,summary)
    p=ROOT/'verified-previews/scene-previews.json';manifest=read(p)
    manifest['previews']['checked_post_dialogue_plane']=dict(relative_png='verified-previews/C-post-dialogue-renderer-plane.png',
        png_sha256=preview['PNG_sha256'],source_dimensions=[224,180],preview_scale=3,
        verified_caption=('Verified geometry plane after C merchant dialogue, animation, movement and one source renderer iteration. '
            'The source task consumed two queued sprites and drew the interior while retaining GPU context. '
            'Initial capture, controlled task/input/clock/device providers remain; physical scanout and playable full game are unverified.'),
        original_reference_pixels_match=True,pinned_emulator_CRY_conversion=True,physical_hardware_validation=False,
        live_gameplay=False,source_report=cp['report'])
    save(p,manifest)
    out=ROOT/'verification/retained-merchant-renderer-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files={ROOT/'scripts/check_biwn_retained_merchant_renderer.py',Path(__file__),
        ROOT/'scripts/generate_biwn_sprite_fullGPU.py',ROOT/'scripts/check_biwn_sprite_fullGPU.py',
        ROOT/'verification/BIWN-retained-merchant-renderer.json',ROOT/'verification/BIWN-sprite-fullGPU.json',
        ROOT/'verification/retained-merchant-renderer-checkpoint.json',ROOT/'verification/retained-interior-render-device-build.json',
        raw/'plane-preview.json',Path(preview['image_path']),*[src/n for n in proof['source_sha256']]}
    pending=[Path(v) for v in bridge['command'] if v.endswith('.c')]
    while pending:
        p=pending.pop().resolve()
        if p in files:continue
        files.add(p)
        for relative in re.findall(r'^\s*#include\s+"([^"]+)"',p.read_text(),re.M):
            included=(p.parent/relative).resolve()
            if included.exists() and included.is_relative_to(ROOT):pending.append(included)
    records=[]
    for p in sorted(files):
        dest=out/'snapshot'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        records.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    save(out/'manifest.json',dict(checkpoint=cp,files=records))
    (out/'who-and-prompts.txt').write_text('Coordinator: all new integration code and inherited-state sprite/renderer changes. '
        'No new code-generation prompts to a local model and no training. Existing accepted source bodies linked. '
        'Original GPU execution is enabled only in the reference path; C path uses source C kernels under guards. '
        'Initial build unused helper and missing E3E0 harness PC/provider were repaired. '
        'Standalone244-case comparison passed but strict all214-classified-row coverage failed; exact198 reached/16 unreached rows now recorded explicitly. '
        'No complete program or game claim.\n')
    save(ROOT/'verification/retained-merchant-renderer-review.json',dict(directory=str(out),status='published',checkpoint=cp))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — MERCHANT DIALOGUE TO SOURCE RENDERER\n'+now.isoformat()+'\n\n'+cp['checked_answer']+'\n\nAudit: '+str(out)+'\nPlane preview: '+preview['image_path']+'\n\nNEXT\n'+'\n'.join(cp['next_work'])+'\n')
    print(json.dumps(dict(directory=str(out),renderer_iterations=1,queued_sprites=2,geometry_GPU_reseed=False)))


if __name__=='__main__':main()
