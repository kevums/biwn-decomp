"""Source mainGPU initializer C versus original full logical/device state."""
import ctypes as c,json,struct,subprocess,os,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_movie_source_overlay_AV as overlay
import check_biwn_movie_GPU as gpu
ROOT=overlay.ROOT;save=overlay.save;sha=overlay.sha
W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16)
class Bus(c.Structure):_fields_=[('read16',gpu.R16),('read32',gpu.R32),('write16',W16),('write32',gpu.W32),('observe_PC',gpu.OBS),('context',c.c_void_p)]
def main():
    source=ROOT/'projects/black-ice-white-noise/restoration';mapping=json.loads((Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])/'main-GPU-boot-C-generation.json').read_text())
    previous=json.loads((ROOT/'verification/BIWN-movie-source-overlay-AV.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    maps=[json.loads((session/n).read_text())['instructions_decoded'] for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']];runtime=overlay.Runtime(Path(previous['directory'])/'libcontroller-AV.dylib',sum(maps,[]),*maps)
    out=ROOT/'verification/BIWN-main-GPU-boot-C'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);library=out/'libmain-GPU-boot.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_gpu_main_boot.c'),'-o',str(library)];build=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    lib=c.CDLL(str(library));run=lib.biwn_gpu_main_boot_run;run.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State),c.c_uint32];run.restype=c.c_int
    base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();payload=base[0x40a8:0x4324];results=[];coverage=set()
    def fixture(seed,flags):
        runtime.mode='native';runtime.reset(base,seed);c.memmove(runtime.core.GPUGetRAM(),payload,len(payload));raw=bytearray(overlay.video.gpu_state(runtime.core)[0]);rng=random.Random(0x3224+seed)
        struct.pack_into('=64I',raw,4139,*[rng.getrandbits(32) for _ in range(64)]);raw[4136:4139]=bytes([flags&1,(flags>>2)&1,(flags>>1)&1]);struct.pack_into('=I',raw,4096,0xf03224);struct.pack_into('=I',raw,4096+4*4,flags);struct.pack_into('=I',raw,4096+8*4,1);raw[4395]=0
        buffer=c.create_string_buffer(bytes(raw));assert runtime.core.GPUStateLoad(buffer)==len(raw)
        return bytes(raw)
    def hardware(state=None):
        h=runtime.snapshot()['hardware'];h['GPU']=dict(size=4396,sha256=sha(gpu.logical(state) if state is not None else overlay.video.gpu_state(runtime.core)[0][:4396]));return h
    try:
        for seed in range(3):
            for flags in [0,7,8]:
                initial=fixture(seed,flags);pcs=[];delays=0;code=c.string_at(runtime.core.GPUGetRAM(),4096)
                for _ in range(100):
                    pc=runtime.core.GPUGetPC()
                    if pc==0xf031be:break
                    pcs.append(pc);word=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');runtime.core.GPUExec(1)
                    if word>>10 in [52,53] and runtime.core.GPUGetPC()!=pc+2:delays+=1;coverage.add(pc+2)
                    coverage.add(pc)
                else:raise AssertionError('Native boot bound')
                native=overlay.video.gpu_state(runtime.core)[0][:4396];native_RAM=runtime.device.ram();native_hardware=hardware();fixture(seed,flags);state=gpu.state_from_raw(initial);trace=[]
                callbacks=[gpu.R16(lambda _,a,v:(v.__setitem__(0,runtime.core.GPUReadWord(a,3)),0)[1]),gpu.R32(lambda _,a,v:(v.__setitem__(0,runtime.core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(runtime.core.GPUWriteWord(a,v,3),0)[1]),gpu.W32(lambda _,a,v:(runtime.core.GPUWriteLong(a,v,3),0)[1]),gpu.OBS(lambda _,pc:trace.append(pc))]
                runtime.core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];bus=Bus(*callbacks,None);counter=runtime.gpu_counter.value
                assert run(c.byref(bus),c.byref(state),100)==0
                if gpu.logical(state)!=native or hardware(state)!=native_hardware or runtime.device.ram()!=native_RAM or trace!=pcs or state.instructions!=len(pcs)+delays:
                    save(out/'mismatch.json',dict(seed=seed,flags=flags,C_trace=trace,native_trace=pcs,C_instructions=state.instructions,native_instructions=len(pcs)+delays,C_hardware=hardware(state),native_hardware=native_hardware,GPU_differences=[i for i,(a,b) in enumerate(zip(gpu.logical(state),native)) if a!=b][:50]));raise AssertionError(str(out/'mismatch.json'))
                assert runtime.gpu_counter.value==counter;results.append(dict(seed=seed,initial_flags=flags,direct_blocks=len(pcs),instructions=state.instructions,logical_GPU_sha256=sha(native),RAM_sha256=sha(native_RAM),hardware=native_hardware,C_original_GPU_instructions=0));save(out/'fixtures.json',results)
        report=dict(status='C_mainGPU_initializer_21instructions_native_full_logical_RAM_devices_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_instruction_coverage=[len(coverage),mapping['instructions']],source_sha256=mapping['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),source_entry='0xf03224',source_return='0xf031be',original_GPU_instructions_on_C_side=0,full_mainGPU_program=False,BIOS3000_verified=False,whole_game_complete=False,
            limits=['Source initializer only: three RAM/registerseeds and flags0/7/8; no otherIRQ/bank1/framehandling.', 'Full4396logicalGPU/2MBRAM/DSP/TOM/JERRY/DAC/cart/TOMraw and exactPC/direct+delaycounts. NativeGPUopcode/pipeline microstate excluded.', 'Host installs159preservedwords and sourceE00A entryPC; fullCPUloader/BIOS3000/mainGPUinterrupt handlers remain separate.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-main-GPU-boot-C.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),cases=len(results),coverage=report['source_instruction_coverage'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
