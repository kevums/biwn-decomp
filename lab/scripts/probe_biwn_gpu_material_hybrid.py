"""Hybrid draw chain with five checked C programs, natural blitter context."""
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
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);out=session/'gpu-material-hybrid-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    proof=read(ROOT/'verification/biwn-disc-world-gpu-geometry-checks.json');capture=Path(proof['startup_capture_directory']);runtime=Runtime(Path(proof['directory'])/'libdisc-world-yields.dylib',ROOT/'tools/libbiwn-material-hybrid.dylib')
    for name in ['animation','camera','targeting','dispatch']:getattr(runtime,'enable_'+name)()
    runtime.enable_resource_fixture([[17,18],[],[17,18],[]])
    for name in ['resource_memory','resource_disc','cd_cpu','loading_yields','render_queue','scene_draw','geometry_records','GPU_geometry']:getattr(runtime,'enable_'+name)()
    lib=runtime.device.lib;core=runtime.core
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t
    core.BlitterReadLong.argtypes=[c.c_uint32,c.c_uint32];core.BlitterReadLong.restype=c.c_uint32
    for name in ['lab_projection_prepare','lab_projection_original','lab_draw_hybrid']:getattr(lib,name).restype=c.c_int
    for name in ['lab_hybrid_steps','lab_hybrid_native_steps','lab_hybrid_setup_calls','lab_hybrid_consumer_calls','lab_hybrid_consumer_PC_count','lab_hybrid_material_PC_count']:getattr(lib,name).restype=c.c_uint32
    for name in ['lab_hybrid_PC']:getattr(lib,name).argtypes=[c.c_uint32];getattr(lib,name).restype=c.c_uint32
    lib.lab_hybrid_material_calls.argtypes=[c.c_uint32];lib.lab_hybrid_material_calls.restype=c.c_uint32
    oracle=read(ROOT/'verification/biwn-gpu-draw-integer-original-probes.json');oracle_folder=Path(oracle['directory']);oracle_rows=read(oracle_folder/'cases.json')
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
            status=lib.lab_draw_hybrid();after=runtime.device.ram();after_gpu,after_state=gpu_state(core);after_blitter=blitter_registers(core)
            for suffix,data in [('after-RAM',after),('after-GPU-state',after_gpu),('after-blitter-registers',after_blitter)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
            pcs=[lib.lab_hybrid_PC(i)for i in range(lib.lab_hybrid_steps())];commands=[];all_commands.update(commands)
            save(out/f'{stem}-PC-samples.json',pcs)
            framebuffer=scene.get(before,0xbd83c);row=dict(case=number,capture=str(path),prefix_CPU=runtime.prefix_CPU,status=status,commands=[hex(x)for x in commands],steps=len(pcs),unique_PC_addresses=len(set(pcs)),before_GPU=before_state,after_GPU=after_state,drawing_list_head_before=scene.get(before,0x10a684),drawing_list_head_after=scene.get(after,0x10a684),GPU_busy_after=core.GPUReadLong(0xf03200,0),GPU_command_after=hex(core.GPUReadLong(0xf03204,0)),main_RAM_changed_bytes=sum(a!=b for a,b in zip(before,after)),framebuffer_address=hex(framebuffer),framebuffer_changed_bytes=sum(a!=b for a,b in zip(before[framebuffer:framebuffer+224*180*2],after[framebuffer:framebuffer+224*180*2])),before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_gpu),after_GPU_state_sha256=sha(after_gpu),before_blitter_registers_sha256=sha(before_blitter),after_blitter_registers_sha256=sha(after_blitter),PC_samples_sha256=sha((out/f'{stem}-PC-samples.json').read_bytes()))
            expected=oracle_rows[number];expected_gpu=(oracle_folder/f'{stem}-after-GPU-state.bin').read_bytes();expected_ram=(oracle_folder/f'{stem}-after-RAM.bin').read_bytes();expected_pcs=read(oracle_folder/f'{stem}-PC-samples.json');expected_blitter=(oracle_folder/f'{stem}-after-blitter-registers.bin').read_bytes()
            architectural=['registers','pc','z','c','n','accumulator','remainder','hidata','matrix_control','matrix_pointer','data_organization','control','division_control','active_bank']
            row.update(C_material_calls={h:lib.lab_hybrid_material_calls(i)for i,h in enumerate(['0x6460','0x6720','0x69a0'])},C_material_PC_samples=lib.lab_hybrid_material_PC_count(),C_setup_calls=lib.lab_hybrid_setup_calls(),C_consumer_calls=lib.lab_hybrid_consumer_calls(),C_consumer_PC_samples=lib.lab_hybrid_consumer_PC_count(),native_GPU_steps=lib.lab_hybrid_native_steps(),fullRAM_GPU_RAM_architecturalstate_PC_order_blitter_readbacks_match_original=after==expected_ram and after_gpu[:4096]==expected_gpu[:4096]and after_blitter==expected_blitter and pcs==expected_pcs and all(after_state[k]==expected['after_GPU'][k]for k in architectural))
            save(out/f'{stem}-comparison.json',row)
            assert row['C_setup_calls']==1 and row['native_GPU_steps']==len(pcs)-72-row['C_consumer_PC_samples']-row['C_material_PC_samples'] and row['C_consumer_calls']==expected['commands'].count('0x6380') and all(row['C_material_calls'][h]==expected['commands'].count(h)for h in row['C_material_calls']) and row['fullRAM_GPU_RAM_architecturalstate_PC_order_blitter_readbacks_match_original'],dict(case=number,row=row,expected=expected)
            rows.append(row);save(out/'cases.json',rows);print(json.dumps({k:row[k]for k in ['case','status','commands','steps','drawing_list_head_before','drawing_list_head_after','framebuffer_changed_bytes']}),flush=True)
            assert status==0 and row['GPU_busy_after']==0 and row['GPU_command_after']=='0xffffffff'and row['drawing_list_head_after']==0,dict(case=number,status=status,lastPC=hex(after_state['pc']),list_head=row['drawing_list_head_after'])
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='five_C_GPU_programs_hybrid_draw_chain_matches_original_with_natural_blitter_context',directory=str(out),cases=len(rows),C_setup_calls=sum(r['C_setup_calls']for r in rows),C_consumer_calls=sum(r['C_consumer_calls']for r in rows),C_consumer_PC_samples=sum(r['C_consumer_PC_samples']for r in rows),C_material_calls={h:sum(r['C_material_calls'][h]for r in rows)for h in ['0x6460','0x6720','0x69a0']},C_material_PC_samples=sum(r['C_material_PC_samples']for r in rows),material_source_sha256={h:sha((ROOT/f'projects/black-ice-white-noise/restoration/biwn_gpu_material{h}.c').read_bytes())for h in ['6460','6720','69a0']},source_C_sha256=sha((ROOT/'projects/black-ice-white-noise/restoration/biwn_gpu_setup57.c').read_bytes()),consumer_C_sha256=sha((ROOT/'projects/black-ice-white-noise/restoration/biwn_gpu_consumer6380.c').read_bytes()),bridge_source_sha256=sha((ROOT/'scripts/biwn_material_hybrid_bridge.c').read_bytes()),probe_source_sha256=sha(Path(__file__).read_bytes()),probe_library_sha256=sha((ROOT/'tools/libbiwn-material-hybrid.dylib').read_bytes()),original_draw_oracle_directory=str(oracle_folder),original_GPU57A0_executed=False,original_GPU6380_executed=False,original_GPU_material_programs_executed=False,other_original_GPU_programs_executed=True,full_renderer_C=False,full_viewport_proved=False,scope='Five fixed C programs replace original57A0/6380/6460/6720/69A0. Setup/consumer case bodies remain unchanged local27B output; material cases generated by coordinator from source operands. No reset between preceding geometry/projection/setup/consumer/material/resident execution. Original dispatcher and58A0 resident still execute GPU. Four chains match whole2MBRAM,4KBGPUlocalRAM,64registers/flags/PC/control/matrix/divider/accumulator/dataorganization/bank,exactdirectPC sequence and blitter readbacks. CPU E19E/E202 remain host-submitted rather than executed. Full C renderer/viewport/game and timing unfinished.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_preflight'if options.limit else'terminal_pass'))
        if not options.limit:save(ROOT/'verification/biwn-gpu-material-hybrid-checks.json',report)
        print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.device.close()
if __name__=='__main__':main()
