"""Original/C firmware GPU renderer variants and shared DMA effects.

Standalone fixture originates from natural firmware CPU+C DSP+C videoIRQ.
Match logical GPU, CPU, private RAM, peripherals and source PC/byte/count
traces at each first instruction variant and periodic boundaries.
"""
import ctypes as c,hashlib,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_firmware_relocation_cpu as relocation
import check_biwn_media_setup_cpu as media
import check_biwn_movie_GPU as gpu
from check_biwn_main_GPU_boot import W16
ROOT=media.ROOT;save=media.save;sha=media.sha
OBS=c.CFUNCTYPE(None,c.c_void_p,c.POINTER(gpu.State),c.c_uint32)
SYNC=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(gpu.State),c.c_int)
class Bus(c.Structure):_fields_=[('read8',gpu.R8),('read16',gpu.R16),('read32',gpu.R32),('write16',W16),('write32',gpu.W32),('observe_PC',OBS),('sync',SYNC),('context',c.c_void_p)]

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'firmware-GPU-renderer-generation.json').read_text())
    origin=Path(json.loads((ROOT/'verification/firmware-CPU-video-IRQ-C-linked.json').read_text())['directory'])
    initial=(origin/'GPU-after-video-IRQ.bin').read_bytes();RAM=(origin/'RAM-after-video-IRQ.bin').read_bytes();machine=(origin/'machine-after-video-IRQ.bin').read_bytes();assert len(initial)==4416
    out=ROOT/'verification/BIWN-firmware-GPU-renderer'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    lib=out/'libfirmware-GPU-renderer.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_GPU_renderer.c'),'-o',str(lib)]
    save(out/'protocol.json',dict(status='running',mapping=mapping,fixture_origin=str(origin),initial_GPU_sha256=sha(initial),initial_RAM_sha256=sha(RAM),initial_machine_sha256=sha(machine),compiler=cmd,source_instruction_guards=True,whole_game_complete=False))
    build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    previous=json.loads((ROOT/'verification/firmware-relocation-CPU-checks.json').read_text());runtime=relocation.Runtime(Path(previous['directory'])/'libfirmware-relocation.dylib',[]);core=runtime.core;closed=False
    core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    for name,rest in [('GPUReadByte',c.c_uint8),('GPUReadWord',c.c_uint16),('GPUReadLong',c.c_uint32)]:getattr(core,name).argtypes=[c.c_uint32,c.c_uint32];getattr(core,name).restype=rest
    core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
    core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool
    if hasattr(core,'BlitterStateSave'):
        core.BlitterStateSave.argtypes=[c.c_void_p];core.BlitterStateSave.restype=c.c_size_t;runtime.savers['Blitter']=core.BlitterStateSave
    counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');buffer=c.create_string_buffer(12000);functions=c.CDLL(str(lib));fn=functions.biwn_firmware_GPU_renderer_run;fn.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State),c.c_uint32];fn.restype=c.c_int
    def raw():
        assert runtime.savers['GPU'](buffer)==4416;return buffer.raw[:4416]
    def reset():
        runtime.reset(RAM,0);assert core.retro_unserialize(c.create_string_buffer(machine),len(machine));assert runtime.device.ram()==RAM and raw()==initial
    def hardware(state=None):
        h=runtime.snapshot()['hardware'];h['GPU']=dict(size=4396,sha256=sha(gpu.logical(state)if state is not None else raw()[:4396]));return h
    frames=[];coverage=set();trace=hashlib.sha256();byte_trace=hashlib.sha256();blocks=delays=0
    try:
        reset();CPU_input=bytes(runtime.cpu());before_counter=counter.value
        while core.GPUReadLong(0xf02114,3)&1:
            pc=core.GPUGetPC();assert 0xf03000<=pc<0xf04000,hex(pc)
            location=core.GPUGetRAM()+pc-0xf03000;payload6=c.string_at(location,6);word=int.from_bytes(payload6[:2],'big');size=6 if word>>10==38 else 2;payload=payload6[:size];delay6=c.string_at(location+2,6)
            key=(pc,payload.hex());new=key not in coverage;coverage.add(key);trace.update(struct.pack('>I',pc));byte_trace.update(struct.pack('>I',pc)+payload);core.GPUExec(1);blocks+=1
            if word>>10 in [52,53]and core.GPUGetPC()!=pc+2:
                dw=int.from_bytes(delay6[:2],'big');size=6 if dw>>10==38 else 2;payload=delay6[:size];key=(pc+2,payload.hex());new=new or key not in coverage;coverage.add(key);delays+=1;trace.update(struct.pack('>I',pc+2));byte_trace.update(struct.pack('>I',pc+2)+payload)
            if new or blocks%1000==0 or not core.GPUReadLong(0xf02114,3)&1:
                frames.append(dict(blocks=blocks,instructions=blocks+delays,GPU_hex=raw()[:4396].hex(),RAM_sha256=sha(runtime.device.ram()),hardware=hardware(),CPU=media.scheduler.cpu_dict(runtime.cpu()),PC_trace=trace.hexdigest(),byte_trace=byte_trace.hexdigest()))
            assert blocks<1000000
        assert bytes(runtime.cpu())==CPU_input
        expected={(r['address'],r['bytes'])for r in mapping['instruction_versions']if not r.get('initial_wait_only')};assert coverage==expected,(len(coverage),len(expected))
        save(out/'native-checkpoints.json',frames);(out/'native-final-GPU.bin').write_bytes(raw());(out/'native-final-RAM.bin').write_bytes(runtime.device.ram())
        reset();state=gpu.state_from_raw(initial);C_trace=hashlib.sha256();C_bytes=hashlib.sha256();C_versions=set();errors=[];syncs=[0]
        def sync(_,pointer,after):
            try:
                current=pointer.contents
                if after==0:
                    image=bytearray(initial);image[:4396]=gpu.logical(current);assert core.GPUStateLoad(c.create_string_buffer(bytes(image)))==4416
                else:
                    loaded=gpu.state_from_raw(raw());loaded.instructions=current.instructions;c.memmove(pointer,c.byref(loaded),c.sizeof(loaded))
                syncs[0]+=1;return 0
            except Exception as error:errors.append(repr(error));return 1
        def observe(_,pointer,pc):
            s=pointer.contents;off=pc-0xf03000;word=int.from_bytes(bytes(s.local_RAM[off:off+2]),'big');size=6 if word>>10==38 else 2;payload=bytes(s.local_RAM[off:off+size]);C_versions.add((pc,payload.hex()));C_trace.update(struct.pack('>I',pc));C_bytes.update(struct.pack('>I',pc)+payload)
        callbacks=[gpu.R8(lambda _,a,v:(v.__setitem__(0,core.GPUReadByte(a,3)),0)[1]),gpu.R16(lambda _,a,v:(v.__setitem__(0,core.GPUReadWord(a,3)),0)[1]),gpu.R32(lambda _,a,v:(v.__setitem__(0,core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(core.GPUWriteWord(a,v,3),0)[1]),gpu.W32(lambda _,a,v:(core.GPUWriteLong(a,v,3),0)[1]),OBS(observe),SYNC(sync)];bus=Bus(*callbacks,None)
        C_start=counter.value;done=0;comparisons=[]
        for index,frame in enumerate(frames):
            status=fn(c.byref(bus),c.byref(state),frame['blocks']-done);done=frame['blocks'];actual=gpu.logical(state);expected_bytes=bytes.fromhex(frame['GPU_hex'])
            if status not in [0,4]or actual!=expected_bytes or sha(runtime.device.ram())!=frame['RAM_sha256']or hardware(state)!=frame['hardware']or C_trace.hexdigest()!=frame['PC_trace']or C_bytes.hexdigest()!=frame['byte_trace']or state.instructions!=frame['instructions']or media.scheduler.cpu_dict(runtime.cpu())!=frame['CPU']:
                (out/'native-mismatch-GPU.bin').write_bytes(expected_bytes);(out/'C-mismatch-GPU.bin').write_bytes(actual);save(out/'mismatch.json',dict(index=index,blocks=done,status=status,native_PC=hex(struct.unpack_from('=I',expected_bytes,4096)[0]),C_PC=hex(state.pc),GPU_differences=[i for i,(a,b)in enumerate(zip(expected_bytes,actual))if a!=b][:70],RAM_match=sha(runtime.device.ram())==frame['RAM_sha256'],hardware_native=frame['hardware'],hardware_C=hardware(state),native_PC_trace=frame['PC_trace'],C_PC_trace=C_trace.hexdigest(),native_byte_trace=frame['byte_trace'],C_byte_trace=C_bytes.hexdigest(),native_instructions=frame['instructions'],C_instructions=state.instructions,errors=errors));raise AssertionError(str(out/'mismatch.json'))
            assert counter.value==C_start,(counter.value,C_start)
            comparisons.append(dict(index=index,blocks=done,instructions=state.instructions,all_state_trace_count_matches=True))
        assert C_versions==coverage and not state.control&1
        save(out/'comparisons.json',comparisons);(out/'C-final-GPU.bin').write_bytes(gpu.logical(state));(out/'C-final-RAM.bin').write_bytes(runtime.device.ram());save(out/'status.json',dict(status='comparisons_matched_pending_shutdown'))
        runtime.oracle.close();closed=True
        report=dict(status='guarded_firmware_GPU_renderer_code_variants_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=1,source_instruction_version_coverage=[len(C_versions),len(expected)],source_PCs=len({p for p,b in coverage}),execution_blocks=done,instructions=state.instructions,checkpoints=len(frames),shared_peripheral_sync_calls=syncs[0],original_GPU_instructions_on_C_path=0,CPU_GPU_RAM_peripheral_PC_byte_trace_count_match=True,source_code_overlay_hostcopy=False,fixture_origin=str(origin),initial_machine_sha256=sha(machine),source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,emulator_shutdown_completed=True,implementation_authorship='coordinator',local_model_authored_bodies_added=0,live_firmware_link_verified=False,whole_game_complete=False,limits=['Standalone incomingstate captured from natural firmwareCPU+C DSP+C videoIRQ and originalGPU initialmailboxwait; not uninterrupted C firmwareboot.','1317observedbytevariants/1013PCs only; changedcode/otherqueues/inputs must be extended. Shared pinnedblitter/GPU MMIO and architecturalIRQ effects are peripheral-model dependencies, not reconstructed here.','4396logicalGPUbytes/bothbanks compared;20pipelinebytes are an initialtail provider. No physical/globalclock/discboot/scanout/playability claim.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/firmware-GPU-renderer-checks.json',report)
        print(json.dumps({k:report[k]for k in ['status','directory','source_instruction_version_coverage','instructions','checkpoints']}),flush=True)
    except BaseException as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:
        if not closed:runtime.oracle.close()

if __name__=='__main__':main()
