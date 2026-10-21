"""Resident timer IRQ frame/handler against pinned original GPU, full state."""
import ctypes as c,json,os,random,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_overlay_AV as overlay
import check_biwn_movie_GPU as gpu
from check_biwn_main_GPU_boot import Bus,W16
ROOT=overlay.ROOT;save=overlay.save;sha=overlay.sha
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'GPU-timer-C-generation.json').read_text());src=ROOT/'projects/black-ice-white-noise/restoration';out=ROOT/'verification/BIWN-GPU-timer'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);library=out/'libGPU-timer.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_gpu_timer.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
    lib=c.CDLL(str(library));run=lib.biwn_gpu_timer_run;run.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State),c.c_uint32,c.c_uint32];run.restype=c.c_int;event=lib.biwn_gpu_timer_assert;event.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State)];event.restype=c.c_int
    previous=json.loads((ROOT/'verification/BIWN-movie-source-overlay-AV.json').read_text());maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())['instructions_decoded']for n in ['movie','video','media-setup']];runtime=overlay.Runtime(Path(previous['directory'])/'libcontroller-AV.dylib',sum(maps,[]),*maps);core=runtime.core;core.GPUSetIRQLine.argtypes=[c.c_int,c.c_int];core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
    baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();payload=baseline[0x40a8:0x4324];results=[];coverage=set();rng=random.Random(0x3140c)
    def fixture(seed,bank,clock,frac,step,word):
        runtime.mode='native';runtime.gpu=None;runtime.reset(baseline,seed%3);c.memmove(core.GPUGetRAM(),payload,len(payload));raw=bytearray(overlay.video.gpu_state(core)[0]);regs=[rng.getrandbits(32)for _ in range(64)];regs[31]=0xf04000
        flags=0x40|(0x4000 if bank else 0)|(seed%8);struct.pack_into('=64I',raw,4139,*regs);struct.pack_into('=I',raw,4096,0xf031ce);struct.pack_into('=I',raw,4112,flags);struct.pack_into('=I',raw,4128,1);raw[4136:4139]=bytes([flags&1,(flags>>2)&1,(flags>>1)&1]);raw[4395]=bank;assert core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw)
        for a,w,v in [(0x778cc,4,clock),(0xbd854,4,frac),(0xbd858,4,step),(0xbd852,2,word)]:runtime.device.direct(a,w,v)
        return bytes(raw)
    def hardware(state=None):
        h=runtime.snapshot()['hardware'];h['GPU']=dict(size=4396,sha256=sha(gpu.logical(state)if state is not None else overlay.video.gpu_state(core)[0][:4396]));return h
    try:
        for case in range(128):
            bank=case%2;clock=[0,1,0xfffffffe,0xffffffff][case%4];frac=[0,1,0xffffffff,0x80000000][(case//4)%4];step=[0,1,0xffffffff,0x0481db08][(case//16)%4];word=[0,1,0xfffe,0xffff][(case//32)%4]
            initial=fixture(case,bank,clock,frac,step,word);initial_RAM=runtime.device.ram();initial_hw=hardware();initial_rng=rng.getstate();core.GPUSetIRQLine(2,1);entered=overlay.video.gpu_state(core)[0][:4396];entry_RAM=runtime.device.ram();pcs=[];delays=0;code=c.string_at(core.GPUGetRAM(),4096)
            for _ in range(100):
                pc=core.GPUGetPC()
                if pc==0xf031ce:break
                pcs.append(pc);coverage.add(pc);opcode=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');core.GPUExec(1)
                if opcode>>10 in [52,53]and core.GPUGetPC()!=pc+2:delays+=1;coverage.add(pc+2)
            else:raise AssertionError(('Native timer bound',hex(pc)))
            expected=overlay.video.gpu_state(core)[0][:4396];expected_RAM=runtime.device.ram();expected_hw=hardware()
            # Reinstall the exact input state, not a new random fixture.
            runtime.reset(initial_RAM,case%3);assert core.GPUStateLoad(c.create_string_buffer(initial))==len(initial);state=gpu.state_from_raw(initial);trace=[]
            callbacks=[gpu.R16(lambda _,a,v:(v.__setitem__(0,core.GPUReadWord(a,3)),0)[1]),gpu.R32(lambda _,a,v:(v.__setitem__(0,core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(core.GPUWriteWord(a,v,3),0)[1]),gpu.W32(lambda _,a,v:(core.GPUWriteLong(a,v,3),0)[1]),gpu.OBS(lambda _,pc:trace.append(pc))];bus=Bus(*callbacks,None);counter=runtime.gpu_counter.value
            assert event(c.byref(bus),c.byref(state))==0
            assert gpu.logical(state)==entered and runtime.device.ram()==entry_RAM
            status=run(c.byref(bus),c.byref(state),100,0xf031ce)
            if status or gpu.logical(state)!=expected or runtime.device.ram()!=expected_RAM or hardware(state)!=expected_hw or trace!=pcs or state.instructions!=len(pcs)+delays:
                save(out/'mismatch.json',dict(case=case,status=status,native_trace=pcs,C_trace=trace,native_hardware=expected_hw,C_hardware=hardware(state),GPU_differences=[i for i,(a,b)in enumerate(zip(gpu.logical(state),expected))if a!=b][:70]));raise AssertionError(str(out/'mismatch.json'))
            assert runtime.gpu_counter.value==counter;carry=frac+step>0xffffffff
            get=lambda a,w=4:int.from_bytes(expected_RAM[a:a+w],'big')
            assert get(0x778cc)==(clock+1)&0xffffffff and get(0xbd854)==(frac+step)&0xffffffff and get(0xbd852,2)==(word+int(carry))&0xffff
            results.append(dict(case=case,bank=bank,clock=clock,fraction=frac,step=step,word=word,carry=carry,CPU_event_frame_match=True,GPU_sha256=sha(expected),RAM_sha256=sha(expected_RAM),instructions=state.instructions,full_GPU_RAM_peripherals_trace_match=True));save(out/'cases.json',results)
        selected={r['address']for r in mapping['instructions_decoded']};assert selected<=coverage,[hex(x)for x in selected-coverage]
        report=dict(status='resident_GPU_timer_IRQ2_event_handler_clock_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_instruction_coverage=[len(selected&coverage),len(selected)],both_incoming_banks_verified=True,clock_wrap_and_fraction_word_carry_verified=True,full_logical_GPU4396_RAM_peripherals_IRQ_frame_PC_trace_and_counts_compared=True,original_GPU_instructions_on_C_path=0,source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,limits=['IRQ2 asserted at declared resident-idle boundary; no concurrent higher-priority IRQ/delay-slot entry, latched/disabled/halted event or physical timer period proof.','Clock-handler/event only; globalclock scheduling/integration into CPU task/movie/world chain and full4000boot/BIOS/DSPmusic/physicalscanout remain pending. LogicalGPU/pipeline microstate distinction retained.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/GPU-timer-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
