"""Attribute sampled pixels to a selected real loaded actor.

The diagnostic disables only the actor's active word in a separate lane. It
does not repair the game or assert camera reachability. Both supplied states
are independently checked against original CPU/GPU rendering.
"""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scene_render_pipeline as render

ROOT=render.ROOT;get=render.scene.native.get;sha=render.sha;save=render.save

def build_trace_device(out):
    src=ROOT/'projects/black-ice-white-noise/restoration'
    original=(src/'biwn_gpu_projection.c').read_text()
    observer='''
static uint32_t lab_projection_events[512][71],lab_projection_count,lab_projection_prev[2];
void lab_projection_reset(void){lab_projection_count=0;lab_projection_prev[0]=lab_projection_prev[1]=0;}
uint32_t lab_projection_event_count(void){return lab_projection_count;}
uint32_t lab_projection_event(unsigned i,unsigned j){return i<lab_projection_count&&j<71?lab_projection_events[i][j]:0;}
static void lab_projection_observe(const struct biwn_gpu_projection_state *s){
 unsigned i,j;uint32_t *r;
 if((s->pc==0xf03584u||s->pc==0xf03590u)&&lab_projection_count<512u){
  r=lab_projection_events[lab_projection_count++];r[0]=s->pc;r[1]=s->registers[1][13];r[2]=lab_projection_prev[0];r[3]=lab_projection_prev[1];
  for(i=0;i<2;i++)for(j=0;j<32;j++)r[4+i*32+j]=s->registers[i][j];
  r[68]=s->z;r[69]=s->n;r[70]=s->c;
 }
 lab_projection_prev[0]=lab_projection_prev[1];lab_projection_prev[1]=s->pc;
}
'''
    marker='#include <string.h>'
    assert original.count(marker)==1 and original.count('s.instructions++;switch(s.pc)')==1
    altered=original.replace(marker,marker+'\n'+observer).replace('s.instructions++;switch(s.pc)','s.instructions++;lab_projection_observe(&s);switch(s.pc)')
    instrumented=out/'biwn_gpu_projection_observed.c';instrumented.write_text(altered)
    receipt=json.loads((ROOT/'verification/expanded-scene-render-device-build-current.json').read_text())
    assert sha(render.DEVICE.read_bytes())==receipt['library_sha256']
    device=out/'libscene-projection-observed.dylib'
    command=[str(instrumented)if x==str(src/'biwn_gpu_projection.c')else str(device)if x==str(render.DEVICE)else x for x in receipt['command']]
    command[1:1]=['-I',str(src)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
    save(out/'instrumentation.json',dict(command=command,original_projection_sha256=sha(original.encode()),instrumented_projection_sha256=sha(altered.encode()),device_sha256=sha(device.read_bytes()),scope='Passive test-only register snapshots at cull and sort-depth stores; original source and historical backend unchanged. Full native/C GPU architecture/RAM/path comparisons still required.'))
    return device

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--trace-projection',action='store_true');opt=ap.parse_args()
    proof=json.loads((ROOT/'verification/loaded-actor-runtime-current.json').read_text())
    source=Path(proof['directory']);cases=json.loads((source/'cases.json').read_text())
    selected=[(i,row)for i,row in enumerate(cases)if row['iterations']==8]
    if opt.limit:selected=selected[:opt.limit]
    out=ROOT/'verification/loaded-actor-visibility'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    if opt.trace_projection:render.DEVICE=build_trace_device(out)
    runtime=render.Render(Path(proof['scene_setup_directory'])/'libscene-queue-restoration.dylib')
    if opt.trace_projection:
        diag=runtime.device.lib;diag.lab_projection_reset.argtypes=[];diag.lab_projection_event_count.restype=c.c_uint32
        diag.lab_projection_event.argtypes=[c.c_uint,c.c_uint];diag.lab_projection_event.restype=c.c_uint32
    rng=random.Random(0x171187);rows=[]
    try:
        for index,case in selected:
            initial=(source/f'case-{index}-C-RAM.bin').read_bytes()
            assert sha(initial)==case['rebuilt']['boundaries'][-1]['RAM_sha256']
            obj=0x49d6c+206*case['fixture']['actor_parameter'];assert get(initial,obj,2)==64
            states={};captures=[]
            old_write=runtime.device.write
            def write(a,v):
                if a==0xf03204 and v==0x52e0:
                    if opt.trace_projection:diag.lab_projection_reset()
                    raw=runtime.device.ram();count=get(raw,0x49b88);record=get(raw,obj+192,2)
                    captures.append(dict(record_count=count,actor_record_index=record if get(raw,obj,2)else None,actor_source=raw[obj+128:obj+192].hex(),record=raw[0x47b88+record*64:0x47b88+(record+1)*64].hex()if get(raw,obj,2)else None,camera_record=raw[0x47b88:0x47bc8].hex()))
                old_write(a,v)
                if a==0xf03204 and v==0x52e0:
                    raw=runtime.device.ram();record=captures[-1]['actor_record_index']
                    captures[-1]['projection_sort_buffer']=raw[0x10a684:0x10a684+16+get(raw,0x49b88)*8].hex()
                    captures[-1]['actor_sort_depth']=get(raw,0x10a684+record*8)if record is not None else None
                    captures[-1]['actor_sort_record_offset']=get(raw,0x10a688+record*8)if record is not None else None
                    if opt.trace_projection:
                        pointer=0x47b88+record*64 if record is not None else None
                        events=[]
                        for i in range(diag.lab_projection_event_count()):
                            data=[diag.lab_projection_event(i,j)for j in range(71)]
                            if data[1]==pointer:events.append(dict(PC=hex(data[0]),record=hex(data[1]),preceding_PCs=[hex(x)for x in data[2:4]],registers=[data[4:36],data[36:68]],ZNC=data[68:71]))
                        captures[-1]['actor_projection_events']=events
            runtime.device.write=write
            incoming=[rng.getrandbits(32)for _ in render.scene.world.REGS]
            for enabled in [True,False]:
                ram=bytearray(initial)
                if not enabled:ram[obj:obj+2]=bytes(2)
                save(out/'status.json',dict(status='running',actor_case=index,enabled=enabled))
                left,expected,old=runtime.native(bytes(ram),incoming);right,value,new=runtime.translated(bytes(ram),incoming)
                assert expected==value and render.scene.native.masked(left)==render.scene.native.masked(right)
                assert not new['status']and not new['errors']and not new['external_calls']
                assert all(old[k]==new[k]for k in ['hardware','GPU_mailboxes','GPU_submissions'])
                assert not new['device']['scene_render']['native_GPU_steps']and not new['device']['device_error']
                fb=get(right,0xbd844);pixels=right[fb:fb+224*180*2]
                states[enabled]=(pixels,dict(original=old,rebuilt=new,framebuffer_sha256=sha(pixels),final_record_count=get(right,0x49b88),projection_input=captures[-1]))
                (out/f'case-{index}-{enabled}-C-RAM.bin').write_bytes(right)
            runtime.device.write=old_write
            a,b=states[True][0],states[False][0]
            changed=sum(a[i:i+2]!=b[i:i+2]for i in range(0,len(a),2))
            rows.append(dict(actor_case=index,scene=case['scene'],task=case['task'],actor_object=hex(obj),actor_before=case['actor_before'],actor_after=case['actor_after'],source_RAM_sha256=sha(initial),pixels_attributed_to_actor=changed,enabled=states[True][1],disabled=states[False][1]))
            save(out/'cases.json',rows);print(json.dumps(dict(actor_case=index,changed_pixels=changed)),flush=True)
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',cases=len(rows),error=repr(error)));raise
    finally:runtime.close()
    report=dict(status='selected_actor_pixel_attribution_checked_against_original',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),actor_states=len(rows),original_C_render_comparisons=len(rows)*2,states_with_pixel_contribution=sum(r['pixels_attributed_to_actor']>0 for r in rows),actor_proof=str(ROOT/'verification/loaded-actor-runtime-current.json'),actor_directory=str(source),script_sha256=sha(Path(__file__).read_bytes()),device_sha256=sha(render.DEVICE.read_bytes()),scope='Each existing8-update loaded actor state rendered normally and with only its activeword explicitlycleared. Bothdiagnosticlanes compare originalCPU/GPUvsC fullD0/publicRAM/device/GPUcommandarchitecture. Pixelcontribution is conditional on unchanged suppliedcamera/otheractors/geometry; zerocontribution does not alone identify culling/occlusion or establish missinggraphicsinitialization. No naturalcamera/fullframe/standalone proof ordefaultpromotion.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    save(ROOT/'verification'/('loaded-actor-visibility-preflight-current.json'if opt.limit else'loaded-actor-visibility-current.json'),report)
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
