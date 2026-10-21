"""Draw verified loaded-actor update outputs with original/C render paths."""
import json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scene_render_pipeline as rendering
ROOT=rendering.ROOT;scene=rendering.scene;save=scene.save;sha=scene.sha


def main():
    proof=json.loads((ROOT/'verification/loaded-actor-runtime-current.json').read_text());folder=Path(proof['directory']);cases=json.loads((folder/'cases.json').read_text());setup=Path(proof['scene_setup_directory'])
    out=ROOT/'verification/loaded-actor-render'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    runtime=rendering.Render(setup/'libscene-queue-restoration.dylib');rng=random.Random(0xf4d817e0e);rows=[];images=[]
    try:
        for index,case in enumerate(cases):
            if case['iterations']!=8:continue
            ram=(folder/f'case-{index}-C-RAM.bin').read_bytes();assert sha(ram)==case['rebuilt']['boundaries'][-1]['RAM_sha256']
            for frame in range(4):
                save(out/'status.json',dict(status='running',actor_case=index,frame=frame));incoming=[rng.getrandbits(32)for _ in scene.world.REGS]
                left,expected,original=runtime.native(ram,incoming);right,value,rebuilt=runtime.translated(ram,incoming)
                fields=['hardware','GPU_mailboxes','GPU_submissions']
                if scene.native.masked(left)!=scene.native.masked(right)or expected!=value or rebuilt['status']or rebuilt['errors']or rebuilt['external_calls']or any(original[k]!=rebuilt[k]for k in fields):
                    save(out/'mismatch.json',dict(actor_case=index,frame=frame,native_D0=expected,C_D0=value,original=original,rebuilt=rebuilt,RAM_differences=[hex(a)for a,(l,r)in enumerate(zip(scene.native.masked(left),scene.native.masked(right)))if l!=r][:64]));raise AssertionError(str(out/'mismatch.json'))
                assert not rebuilt['device']['scene_render']['native_GPU_steps']and not rebuilt['device']['scene_render']['forbidden_GPU_attempts']
                framebuffer=scene.native.get(right,0xbd844);pixels=right[framebuffer:framebuffer+224*180*2];assert pixels==left[framebuffer:framebuffer+224*180*2]
                if not frame:
                    import animation_renderer
                    image=out/f'actor-case-{index}-matched-frame.png';image.write_bytes(animation_renderer.image_png(pixels,224,180,scale=3));images.append(str(image))
                rows.append(dict(actor_case=index,scene=case['scene'],task=case['task'],frame=frame,actor_updates_before_render=8,actor_before=case['actor_before'],actor_after=case['actor_after'],full_D0=value,framebuffer_sha256=sha(pixels),original=original,rebuilt=rebuilt,public_RAM_and_complete_GPU_command_states_match=True));ram=right
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',completed_cases=len(rows),error=repr(error)));raise
    finally:runtime.close()
    save(out/'cases.json',rows)
    report=dict(status='disc_scene_actor_updates_feed_matching_C_render',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),actor_update_states=len({row['actor_case']for row in rows}),scene_positions=len({row['scene']for row in rows}),frames_per_state=4,actor_updates_before_each_state=8,C_blitter_commands=sum(row['rebuilt']['device']['blit_commands']for row in rows),images=images,actor_proof=str(ROOT/'verification/loaded-actor-runtime-current.json'),actor_source_directory=str(folder),source_sha256=proof['source_sha256'],render_library=str(setup/'libscene-queue-restoration.dylib'),device_sha256=sha(rendering.DEVICE.read_bytes()),script_sha256=sha(Path(__file__).read_bytes()),default_promoted=False,scope='C-loaded discscene -> sourceC scheduler/actor activation and8updates -> commonRAM for original17E0Eand linkedC rendering. FullD0/publicRAM/devicefields and eachgeometry/projection/drawGPUarchitecture/RAM/PCpath match. Actor test blocksothercontexts and suppliescallerentry; geometryGPUcontext is explicitlyreset fromcapturedfixture eachrender, matrixdevice uses itsdeclaredisolatedadapter. Model/animation/other task contexts and naturalfullframe/globalGPUcontext/interrupts/clocks/scanout/standaloneplayability remain unproved. Draws are off-line comparisons of updateoutputs, not one uninterrupted whole-game loop.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)));save(ROOT/'verification/loaded-actor-render-current.json',report);print(json.dumps({k:report[k]for k in ['status','directory','cases','actor_update_states','scene_positions']}),flush=True)


if __name__=='__main__':main()
