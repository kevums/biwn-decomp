"""Original/C firstboot GPU texture startup and source shutdown, full state."""
import ctypes as c,json,os,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
import check_biwn_full_video_cpu_gpu as video
import check_biwn_movie_GPU as gpu
from check_biwn_main_GPU_boot import W16
ROOT=media.ROOT;save=media.save;sha=media.sha
class Bus(c.Structure):
    _fields_=[('read8',gpu.R8),('read16',gpu.R16),('read32',gpu.R32),('write16',W16),('write32',gpu.W32),('observe_PC',gpu.OBS),('context',c.c_void_p)]
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'game-firstboot-GPU-C-generation.json').read_text());boot=(session/'boot-payload-68000-candidate.bin').read_bytes();bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();out=ROOT/'verification/BIWN-game-firstboot-GPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libfirstboot-GPU.dylib';names=['biwn_game_firstboot_GPU.c','biwn_media_setup_cpu.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    runtime=media.Runtime(lib,[]);core=runtime.core;core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    for name,width in [('GPUReadByte',1),('GPUReadWord',2),('GPUReadLong',4)]:f=getattr(core,name);f.argtypes=[c.c_uint32,c.c_uint32];f.restype={1:c.c_uint8,2:c.c_uint16,4:c.c_uint32}[width]
    for name,kind in [('GPUWriteWord',c.c_uint16),('GPUWriteLong',c.c_uint32)]:getattr(core,name).argtypes=[c.c_uint32,kind,c.c_uint32]
    fn=runtime.lib.biwn_game_firstboot_GPU_run;fn.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State),c.c_uint32,c.c_uint32];fn.restype=c.c_int;counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');coverage=set();results=[];rng=random.Random(0x180000)
    def hardware(state=None):
        h=runtime.snapshot()['hardware'];h['GPU']=dict(size=4396,sha256=sha(gpu.logical(state)if state is not None else video.gpu_state(core)[0][:4396]));return h
    def original(stop):
        pcs=[];delays=0;image=c.string_at(core.GPUGetRAM(),4096)
        for _ in range(1000000):
            pc=core.GPUGetPC()
            if pc==stop and pcs:return pcs,delays
            assert pc in selected,hex(pc);pcs.append(pc);coverage.add(pc);word=int.from_bytes(image[pc-0xf03000:pc-0xf03000+2],'big');core.GPUExec(1)
            if word>>10 in [52,53]and core.GPUGetPC()!=pc+2:delays+=1;coverage.add(pc+2)
        raise AssertionError('Original firstboot GPU bound')
    selected={r['address']for r in mapping['instructions_decoded']}
    try:
        for case in range(2):
            ram=bytearray(bytes([case*37])*0x200000);ram[0x180000:0x180000+len(boot)]=boot;runtime.reset(bytes(ram),case)
            raw=bytearray(video.gpu_state(core)[0]);raw[0x200:0x9d4]=boot[0x188:0x95c];raw[0x50:0x1a0]=bios[0x84a6+0x382:0x84a6+0x4d2];raw[0x10:0x1c]=bytes.fromhex('981e306400f0d3c0e400e400');raw[0x800:0x804]=bytes(4)
            regs=[rng.getrandbits(32)for _ in range(64)];regs[31]=0xf04000;flags=0x20|(case*7);struct.pack_into('=64I',raw,4139,*regs);struct.pack_into('=I',raw,4096,0xf03200);struct.pack_into('=I',raw,4112,flags);struct.pack_into('=I',raw,4128,1);raw[4136:4139]=bytes([flags&1,(flags>>2)&1,(flags>>1)&1]);raw[4395]=0
            assert core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw);runtime.tom[6]=0;runtime.tom[7]=4
            initial=bytes(raw);snapshots=[];traces=[];counts=[]
            for phase,stop in [('initialization',0xf032ce),('redraw',0xf032ce),('shutdown',0xf03328)]:
                if phase=='redraw':runtime.tom[7]=0
                if phase=='shutdown':runtime.tom[7]=4;core.GPUWriteLong(0xf03800,1,6)
                trace,delays=original(stop);traces.append(trace);counts.append(len(trace)+delays);snapshots.append(dict(GPU=video.gpu_state(core)[0][:4396],RAM=runtime.device.ram(),hardware=hardware()))
            runtime.reset(bytes(ram),case);assert core.GPUStateLoad(c.create_string_buffer(initial))==len(initial);runtime.tom[6]=0;runtime.tom[7]=4;state=gpu.state_from_raw(initial);trace=[]
            callbacks=[gpu.R8(lambda _,a,v:(v.__setitem__(0,core.GPUReadByte(a,3)),0)[1]),gpu.R16(lambda _,a,v:(v.__setitem__(0,core.GPUReadWord(a,3)),0)[1]),gpu.R32(lambda _,a,v:(v.__setitem__(0,core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(core.GPUWriteWord(a,v,3),0)[1]),gpu.W32(lambda _,a,v:(core.GPUWriteLong(a,v,3),0)[1]),gpu.OBS(lambda _,pc:trace.append(pc))];bus=Bus(*callbacks,None)
            for phase,stop,index in [('initialization',0xf032ce,0),('redraw',0xf032ce,1),('shutdown',0xf03328,2)]:
                if phase=='redraw':runtime.tom[7]=0
                if phase=='shutdown':runtime.tom[7]=4;state.local_RAM[0x800:0x804]=(1).to_bytes(4,'big');core.GPUWriteLong(0xf03800,1,6)
                trace.clear();before=state.instructions;guard=counter.value;status=fn(c.byref(bus),c.byref(state),1000000,stop);expected=snapshots[index]
                if status or gpu.logical(state)!=expected['GPU']or runtime.device.ram()!=expected['RAM']or hardware(state)!=expected['hardware']or trace!=traces[index]or state.instructions-before!=counts[index]:
                    save(out/'mismatch.json',dict(case=case,phase=phase,status=status,C_PC=hex(state.pc),GPU_differences=[i for i,(a,b)in enumerate(zip(gpu.logical(state),expected['GPU']))if a!=b][:60],RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(runtime.device.ram(),expected['RAM']))if a!=b][:20],native_hardware=expected['hardware'],C_hardware=hardware(state),native_count=counts[index],C_count=state.instructions-before,native_trace_prefix=traces[index][:30],C_trace_prefix=trace[:30]));raise AssertionError(str(out/'mismatch.json'))
                assert counter.value==guard
                results.append(dict(case=case,phase=phase,instructions=counts[index],GPU_sha256=sha(expected['GPU']),RAM_sha256=sha(expected['RAM']),full_GPU_RAM_peripherals_trace_count_match=True));save(out/'cases.json',results)
        report=dict(status='source_firstboot_GPU_initialization_shutdown_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=2,phases=6,source_instruction_coverage=[len(selected&coverage),len(selected)],uncovered_PC=sorted(selected-coverage),source_sha256=mapping['source_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),original_GPU_instructions_on_C_path=0,whole_game_complete=False,limits=['Supplied boot payload/GPU code/registers/controller state, controlled TOMVCOUNT0/4 and explicit stop-flag event. Startup decodes two images, sets object-list/video registers, and source shutdown clearsGPU GO. Not CPU game180000/controller linkage, physical video/global schedule or complete firmware boot.','Only observed startup/RLE and selected poll/shutdown instructions are generated. Unobserved code fails BAD_PC; other compressed inputs/branches remain unverified. Full4396logicalGPU/RAM/peripherals/PCtrace/instructioncounts compared; GPU pipeline tail is supplied/excluded.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/game-firstboot-GPU-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','uncovered_PC']}))
    except BaseException as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
