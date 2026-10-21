"""Original resident dispatcher/draw chain immediately after live52E0 output."""
import argparse,ctypes as c,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_disc_scene_actors as scene
from probe_biwn_gpu_projection import Runtime,PrefixCaptured,gpu_state
ROOT=scene.ROOT;read=lambda p:json.loads(p.read_text());save=scene.save;sha=lambda x:hashlib.sha256(x).hexdigest()
def blitter_registers(core):
    return b''.join(core.BlitterReadLong(0xf02200+i,0).to_bytes(4,'big')for i in range(0,160,4))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args()
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);out=session/'gpu-draw-chain-slow-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    proof=read(ROOT/'verification/biwn-disc-world-gpu-geometry-checks.json');capture=Path(proof['startup_capture_directory']);runtime=Runtime(Path(proof['directory'])/'libdisc-world-yields.dylib',ROOT/'tools/libbiwn-draw-slow-probe.dylib')
    for name in ['animation','camera','targeting','dispatch']:getattr(runtime,'enable_'+name)()
    runtime.enable_resource_fixture([[17,18],[],[17,18],[]])
    for name in ['resource_memory','resource_disc','cd_cpu','loading_yields','render_queue','scene_draw','geometry_records','GPU_geometry']:getattr(runtime,'enable_'+name)()
    lib=runtime.device.lib;core=runtime.core
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t
    core.BlitterReadLong.argtypes=[c.c_uint32,c.c_uint32];core.BlitterReadLong.restype=c.c_uint32
    for name in ['lab_projection_prepare','lab_projection_original','lab_draw_original']:getattr(lib,name).restype=c.c_int
    for name in ['lab_draw_steps','lab_draw_command_count']:getattr(lib,name).restype=c.c_uint32
    for name in ['lab_draw_PC','lab_draw_command']:getattr(lib,name).argtypes=[c.c_uint32];getattr(lib,name).restype=c.c_uint32
    rows=[];all_commands=set()
    try:
        for number,path in enumerate(sorted(capture.glob('startup-C-*.bin'))[:options.limit]):
            save(out/'status.json',dict(status='running',case=number));metadata=read(capture/f'startup-capture-{path.stem.split("-")[-1]}.json');ram=bytearray(path.read_bytes());assert sha(ram)==metadata['C_RAM_sha256']
            for ctx in scene.startup.CONTEXTS:ram[ctx+26:ctx+30]=(0 if ctx in scene.RUNNABLE|{0xc2128,scene.startup.RENDER}else 1).to_bytes(4,'big')
            for a in [0x49d54,0x49d56]:ram[a:a+2]=(1).to_bytes(2,'big')
            cpu=scene.CPU();cpu.registers[:]=metadata['CPU']['registers']
            for field in ['pc','sr','usp','ssp']:setattr(cpu,field,metadata['CPU'][field])
            cpu.ssp=0x1ff000;runtime.enable_world(8)
            try:runtime.native(bytes(ram),cpu,64)
            except PrefixCaptured:pass
            else:raise AssertionError('E19E prefix absent')
            assert lib.lab_projection_prepare()==0 and lib.lab_projection_original()==0
            stem=f'case-{number:02d}';before=runtime.device.ram();before_gpu,before_state=gpu_state(core);before_blitter=blitter_registers(core)
            for suffix,data in [('before-RAM',before),('before-GPU-state',before_gpu),('before-blitter-registers',before_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            status=lib.lab_draw_original();after=runtime.device.ram();after_gpu,after_state=gpu_state(core);after_blitter=blitter_registers(core)
            for suffix,data in [('after-RAM',after),('after-GPU-state',after_gpu),('after-blitter-registers',after_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            pcs=[lib.lab_draw_PC(i)for i in range(lib.lab_draw_steps())];commands=[lib.lab_draw_command(i)for i in range(lib.lab_draw_command_count())];all_commands.update(commands)
            save(out/f'{stem}-PC-samples.json',pcs)
            framebuffer=scene.get(before,0xbd83c);row=dict(case=number,capture=str(path),prefix_CPU=runtime.prefix_CPU,status=status,commands=[hex(x)for x in commands],steps=len(pcs),unique_PC_addresses=len(set(pcs)),before_GPU=before_state,after_GPU=after_state,drawing_list_head_before=scene.get(before,0x10a684),drawing_list_head_after=scene.get(after,0x10a684),GPU_busy_after=core.GPUReadLong(0xf03200,0),GPU_command_after=hex(core.GPUReadLong(0xf03204,0)),main_RAM_changed_bytes=sum(a!=b for a,b in zip(before,after)),framebuffer_address=hex(framebuffer),framebuffer_changed_bytes=sum(a!=b for a,b in zip(before[framebuffer:framebuffer+224*180*2],after[framebuffer:framebuffer+224*180*2])),before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_gpu),after_GPU_state_sha256=sha(after_gpu),before_blitter_registers_sha256=sha(before_blitter),after_blitter_registers_sha256=sha(after_blitter),PC_samples_sha256=sha((out/f'{stem}-PC-samples.json').read_bytes()))
            rows.append(row);save(out/'cases.json',rows);print(json.dumps({k:row[k]for k in ['case','status','commands','steps','drawing_list_head_before','drawing_list_head_after','framebuffer_changed_bytes']}),flush=True)
            assert status==0 and row['GPU_busy_after']==0 and row['GPU_command_after']=='0xffffffff'and row['drawing_list_head_after']==0,dict(case=number,status=status,lastPC=hex(after_state['pc']),list_head=row['drawing_list_head_after'])
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_GPU_resident_dispatcher_draw_chain_returned_and_consumed_list_C_unimplemented',directory=str(out),cases=len(rows),commands=sorted(hex(x)for x in all_commands),bridge_source_sha256=sha((ROOT/'scripts/biwn_draw_slow_probe_bridge.c').read_bytes()),probe_source_sha256=sha(Path(__file__).read_bytes()),probe_library_sha256=sha((ROOT/'tools/libbiwn-draw-slow-probe.dylib').read_bytes()),original_dispatcher_executed=True,source_CPU_E19E_E202_executed=False,C_draw_reconstructed=False,full_viewport_proved=False,scope='OriginalGPU and pinnedblitter withfastoptiondisabled, continuing actual liveprefix geometry/record state through host-submitted52E0 then57A0 and originalresidentdispatcher. The originalCPU submission wrappers are not run. Host installs originalresident512bytes and supplieslastloaded52E0 marker and57A0command. No reset betweengeometry/projection/draw. Existing assisted-startup/script/clock/device limits retained. Framebufferchanges are measured bytes, not a verified playable/rendered viewport or scanout.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_preflight'if options.limit else'terminal_pass'))
        if not options.limit:save(ROOT/'verification/biwn-gpu-draw-slow-original-probes.json',report)
        print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.device.close()
if __name__=='__main__':main()
