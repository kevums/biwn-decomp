"""Load adjacent real map windows, update source actors, and draw the results.

Positions are explicit diagnostic inputs; no actor is relocated or fabricated.
Each loader/actor/render phase compares original code to reconstructed C.
Other task contexts and GPU reset fixtures retain the isolated proof limits.
"""
import argparse,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scene_queue_restoration as queue
import check_biwn_loaded_actor_runtime as actors
import check_biwn_scene_render_pipeline as render

ROOT=queue.ROOT;get=actors.get;sha=queue.sha;save=queue.save

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args()
    out=ROOT/'verification/nearby-actor-scene'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    qproof=json.loads((ROOT/'verification/scene-queue-restoration-current.json').read_text());qlib=Path(qproof['directory'])/'libscene-queue-restoration.dylib'
    aproof=json.loads((ROOT/'verification/loaded-actor-runtime-current.json').read_text());alib=Path(aproof['directory'])/'libloaded-actor-runtime.dylib'
    assert alib.exists(),str(alib)
    source_root=ROOT/'projects/black-ice-white-noise/restoration'
    for proof in [qproof,aproof]:
        for name,expected in proof['source_sha256'].items():assert sha((source_root/name).read_bytes())==expected,name
    catalogue=json.loads((ROOT/'verification/outdoor-scene-catalog-current.json').read_text());windows=json.loads((Path(catalogue['directory'])/'windows.json').read_text())
    targets=[next(w for w in windows if w['X']==X and w['Z']==Z)for X,Z in [(24063,27393),(23039,27393),(24063,28417)]]
    if opt.limit:targets=targets[:opt.limit]
    rng=random.Random(0x134dc17112);registers=lambda:[rng.getrandbits(32)for _ in render.scene.world.REGS]
    loader=queue.Runtime(qlib);snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes();assert sha(snapshot)==catalogue['resident_flag_RAM_sha256']
    prefix=loader.disc.use_previous_track_prefix();patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0]
    address=int(patch['address'],16);initial=bytearray(snapshot);old=bytes.fromhex(patch['original']);new=bytes.fromhex(patch['replacement']);assert initial[address:address+len(old)]==old;initial[address:address+len(old)]=new;initial[0x47b80:0x47b84]=bytes(4)
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text());buffer=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000];assert sha(buffer)==diagnosis['buffer_sha256'];witness=loader.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],buffer)
    for address,expected in queue.PATCHES.items():assert get(initial,address)==expected;initial[address:address+4]=queue.QUEUE.to_bytes(4,'big')
    loaded=[];rows=[]
    try:
        prepared,_,_,_,_=queue.outdoor.compare(loader,bytes(initial),dict(entry=0x1aa40,mode=1,word_scan=1,incoming=registers(),external_D0=0xc001d00d),out,'textures')
        for i,window in enumerate(targets):
            ram=bytearray(prepared);ram[0x49c50:0x49c54]=window['X'].to_bytes(4,'big');ram[0x49c56:0x49c5a]=window['Z'].to_bytes(4,'big')
            left,right,d0,original,rebuilt=queue.outdoor.compare(loader,bytes(ram),dict(mode=1,word_scan=1,incoming=registers(),external_D0=0xc001d00d),out,f'load-{i}')
            assert original['fault']is None and not original['texture_queue_overruns']and not original['unmapped_actor_reads']
            actual=loader.last_C_raw;assert queue.normalized(actual)==right
            (out/f'scene-{i}-loaded-C-RAM.bin').write_bytes(actual)
            loaded.append((window,actual,dict(original=original,rebuilt=rebuilt,task_records=render.scene.check_task_records(left,right,original),RAM_sha256=sha(actual))))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',phase='loading',error=repr(error)));raise
    finally:loader.close()
    actor=actors.Runtime(alib);states=[]
    try:
        for scene,(window,ram,load)in enumerate(loaded):
            tasks=[task for task in actors.ring(ram)if get(ram,task+8)==get(ram,task+16)==0xf4d8 and get(ram,task+12)==task+0x400]
            for task in tasks:
                obj=0x49d6c+206*get(ram,task+30);common,cpu,fixture=actors.fixture(ram,task,rng)
                for steps in [1,64]:
                    save(out/'status.json',dict(status='running',phase='actors',scene=scene,task=hex(task),steps=steps))
                    left,expected,old=actor.native(common,cpu,task,steps);right,actual,new=actor.translated(common,cpu,task,steps)
                    assert left==right and bytes(expected)==bytes(actual)
                    assert all(old[k]==new[k]for k in ['calls','movements','boundaries','hardware','GPU_argument_mailboxes'])
                    assert not new['device']['original_GPUExec1_calls']and not new['device']['device_error']
                    index=len(states);(out/f'actor-{index}-C-RAM.bin').write_bytes(right)
                    states.append((right,dict(scene=scene,window=window,task=hex(task),object=hex(obj),steps=steps,fixture=fixture,load=load,source_RAM_sha256=sha(ram),actor_before=dict(X=get(ram,obj+4),Z=get(ram,obj+10)),actor_after=dict(X=get(right,obj+4),Z=get(right,obj+10)),original=old,rebuilt=new)))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',phase='actors',completed_states=len(states),error=repr(error)));raise
    finally:actor.close()
    runtime=render.Render(qlib)
    try:
        for index,(ram,actor_proof)in enumerate(states):
            save(out/'status.json',dict(status='running',phase='render',state=index,total=len(states)))
            incoming=registers();left,expected,old=runtime.native(ram,incoming);right,value,new=runtime.translated(ram,incoming)
            assert expected==value and render.scene.native.masked(left)==render.scene.native.masked(right)
            assert not new['status']and not new['errors']and not new['external_calls']
            assert all(old[k]==new[k]for k in ['hardware','GPU_mailboxes','GPU_submissions'])
            assert not new['device']['scene_render']['native_GPU_steps']and not new['device']['device_error']
            fb=get(right,0xbd844);pixels=right[fb:fb+224*180*2]
            import animation_renderer
            image=out/f'state-{index}-matched.png';image.write_bytes(animation_renderer.image_png(pixels,224,180,scale=3))
            (out/f'state-{index}-matched.raw16be').write_bytes(pixels)
            disabled=bytearray(ram);obj=int(actor_proof['object'],16);disabled[obj:obj+2]=bytes(2)
            dleft,dexpected,dold=runtime.native(bytes(disabled),incoming);dright,dvalue,dnew=runtime.translated(bytes(disabled),incoming)
            assert dexpected==dvalue and render.scene.native.masked(dleft)==render.scene.native.masked(dright)
            assert not dnew['status']and not dnew['errors']and not dnew['external_calls']
            assert all(dold[k]==dnew[k]for k in ['hardware','GPU_mailboxes','GPU_submissions'])
            assert not dnew['device']['scene_render']['native_GPU_steps']and not dnew['device']['device_error']
            dfb=get(dright,0xbd844);dpixels=dright[dfb:dfb+224*180*2]
            (out/f'state-{index}-disabled.raw16be').write_bytes(dpixels)
            rows.append(dict(state=index,actor=actor_proof,framebuffer_sha256=sha(pixels),image=str(image),pixels_attributed_to_selected_actor=sum(pixels[k:k+2]!=dpixels[k:k+2]for k in range(0,len(pixels),2)),disabled_framebuffer_sha256=sha(dpixels),original=old,rebuilt=new,disabled_render=dict(original=dold,rebuilt=dnew)))
            save(out/'cases.json',rows);print(json.dumps(dict(state=index,scene=actor_proof['scene'],task=actor_proof['task'],steps=actor_proof['steps'],framebuffer_sha256=sha(pixels))),flush=True)
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',phase='render',completed_states=len(rows),error=repr(error)));raise
    finally:runtime.close()
    comparisons=[]
    for i in range(0,len(rows),2):
        a,b=rows[i:i+2];assert a['actor']['task']==b['actor']['task']and a['actor']['steps']==1 and b['actor']['steps']==64
        p=(out/f'state-{i}-matched.raw16be').read_bytes();q=(out/f'state-{i+1}-matched.raw16be').read_bytes()
        comparisons.append(dict(states=[i,i+1],scene=a['actor']['scene'],task=a['actor']['task'],coordinate_change=a['actor']['actor_after']!=b['actor']['actor_after'],changed_pixels=sum(p[k:k+2]!=q[k:k+2]for k in range(0,len(p),2)),disabled_images_equal=a['disabled_framebuffer_sha256']==b['disabled_framebuffer_sha256'],selected_actor_pixels=[a['pixels_attributed_to_selected_actor'],b['pixels_attributed_to_selected_actor']]))
    save(out/'motion-comparisons.json',comparisons)
    report=dict(status='adjacent_loaded_actor_states_render_like_original',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),scene_positions=len(loaded),actor_entries=len(rows)//2,actor_states=len(rows),actor_updates=sum(row['actor']['steps']for row in rows),states_with_coordinate_change=sum(row['coordinate_change']for row in comparisons),pairs_with_changed_images=sum(row['changed_pixels']>0 for row in comparisons),pairs_with_attributed_visible_motion=sum(row['changed_pixels']>0 and row['disabled_images_equal']and any(row['selected_actor_pixels'])for row in comparisons),disabled_image_pairs_equal=sum(row['disabled_images_equal']for row in comparisons),images=[row['image']for row in rows],script_sha256=sha(Path(__file__).read_bytes()),queue_library_sha256=sha(qlib.read_bytes()),actor_library_sha256=sha(alib.read_bytes()),queue_proof=qproof,actor_proof=aproof,disc_prefix=prefix,disc_witness=witness,scope='Fresh actual-disc adjacent suppliedpositions, explicitqueue/wordscan/672repair, original/C load, sourceactor1or64updates withreal loadedring butothercontextsblocked, original/C render compare. Eachstate also renderswithonlyselectedactoractivewordcleared, anddisabledimagescompare acrossupdates forattribution. No actor relocation or inventedart/geometry. PerphaseGPUcontexts reset throughdeclaredadapters; not uninterruptedglobalGPU/mainloop/naturalreachability/animation/standalone/defaultpromotion.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',states=len(rows)))
    save(ROOT/'verification'/('nearby-actor-scene-preflight-current.json'if opt.limit else'nearby-actor-scene-current.json'),report);print(json.dumps({k:report[k]for k in ['status','directory','scene_positions','actor_entries','actor_updates','pairs_with_changed_images']}),flush=True)

if __name__=='__main__':main()
