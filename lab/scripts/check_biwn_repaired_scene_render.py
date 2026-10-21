"""Render fresh queue-restored scene outputs against original CPU/GPU draw."""
import argparse,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scene_render_pipeline as rendering
ROOT=rendering.ROOT;scene=rendering.scene;sha=scene.sha;save=scene.save


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args()
    proof=json.loads((ROOT/'verification/scene-queue-restoration-current.json').read_text());folder=Path(proof['directory']);source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,expected in proof['source_sha256'].items():assert sha((source/name).read_bytes())==expected,name
    vectors=json.loads((folder/'render-inputs.json').read_text())
    if opt.limit:vectors=vectors[:opt.limit]
    out=ROOT/'verification/repaired-scene-render'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    runtime=rendering.Render(folder/'libscene-queue-restoration.dylib');rng=random.Random(0x1f000017e0e);rows=[];images=[]
    try:
        for i,vector in enumerate(vectors):
            ram=(folder/f'render-input-{i}.bin').read_bytes();assert sha(ram)==vector['RAM_sha256']
            for frame in range(4):
                save(out/'status.json',dict(status='running',scene=i,frame=frame));incoming=[rng.getrandbits(32)for _ in scene.world.REGS]
                left,expected,original=runtime.native(ram,incoming);right,value,rebuilt=runtime.translated(ram,incoming)
                fields=['hardware','GPU_mailboxes','GPU_submissions']
                match=scene.native.masked(left)==scene.native.masked(right)and expected==value and not rebuilt['status']and not rebuilt['errors']and not rebuilt['external_calls']and all(original[k]==rebuilt[k]for k in fields)
                if not match:
                    (out/'native-RAM.bin').write_bytes(left);(out/'C-RAM.bin').write_bytes(right)
                    save(out/'mismatch.json',dict(scene=i,frame=frame,window=vector['window'],expected_D0=expected,C_D0=value,original=original,rebuilt=rebuilt,RAM_differences=[hex(a)for a,(l,r)in enumerate(zip(scene.native.masked(left),scene.native.masked(right)))if l!=r][:64]));raise AssertionError(str(out/'mismatch.json'))
                stats=rebuilt['device']['scene_render'];assert not stats['native_GPU_steps']and not stats['forbidden_GPU_attempts']and not rebuilt['device']['device_error']
                framebuffer=scene.native.get(right,0xbd844);assert framebuffer==scene.native.get(ram,0xbd83c)
                pixels=right[framebuffer:framebuffer+224*180*2];assert pixels==left[framebuffer:framebuffer+224*180*2]
                if not frame:
                    import animation_renderer
                    path=out/f'scene-{i}-matched-frame.png';path.write_bytes(animation_renderer.image_png(pixels,224,180,scale=3));images.append(str(path));(out/f'scene-{i}-matched-frame.raw16be').write_bytes(pixels)
                rows.append(dict(scene=i,frame=frame,window=vector['window'],full_D0=value,record_count=scene.native.get(right,0x49b88),original=original,rebuilt=rebuilt,public_RAM_sha256=sha(scene.native.masked(right)),framebuffer=hex(framebuffer),framebuffer_sha256=sha(pixels)))
                ram=right
        save(out/'cases.json',rows)
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',completed_cases=len(rows),error=repr(error)));raise
    finally:runtime.close()
    report=dict(status='queue_restored_disc_scenes_render_like_native_CPU_GPU',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),fresh_scene_positions=len(vectors),frames_per_scene=4,queue_setup_proof=str(ROOT/'verification/scene-queue-restoration-current.json'),queue_setup_directory=str(folder),source_sha256=proof['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),device_sha256=sha(rendering.DEVICE.read_bytes()),images=images,C_blitter_commands=sum(row['rebuilt']['device']['blit_commands']for row in rows),native_CPU_instructions=sum(row['original']['CPU_instructions']for row in rows),native_GPU_steps=sum(row['original']['device']['scene_render']['native_GPU_steps']for row in rows),C_original_GPU_steps=0,external_C_render_calls=0,default_promoted=False,standalone=False,scope='Common input is each freshly C-loaded scene from explicit queue-restoration proof, including formerly corrupted window27/1/4. Original17E0Eand linked C rendering compare fullD0/publicRAM/sevenblitterregs/eightGPUmailboxes and geometry/projection/drawGPUarchitecture/RAM/PCcounts/hashes. Queue operand patches remain in suppliedRAM but are not reached duringrender. Frozenresidentmerchant actorstate/art, suppliedpositions, geometryGPUresetfixtureand synchronousdevices remain. New actor tasks are created by setup but not executed here. No naturalgameentry/globalGPUcontext/physicaltiming/scanout/fullgame/standalone proof. Render match does not prove original overflowing setup was correct.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    save(ROOT/'verification'/('repaired-scene-render-preflight-current.json'if opt.limit else'repaired-scene-render-current.json'),report)
    print(json.dumps({k:report[k]for k in ['status','directory','cases','fresh_scene_positions','C_blitter_commands']}),flush=True)


if __name__=='__main__':main()
