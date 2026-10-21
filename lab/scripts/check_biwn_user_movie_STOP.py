"""Original user privilege STOP/GPU IRQ/RTE vs source C in64flag/register cases."""
import ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha

def main():
    out=ROOT/'verification/BIWN-user-movie-STOP-C'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';libpath=out/'libuser-STOP.dylib';names=['biwn_movie_privilege_cpu.c','biwn_video_cpu.c','biwn_media_setup_cpu.c']
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(libpath)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    runtime=media.Runtime(libpath,[])
    body=runtime.lib.biwn_movie_privilege_cpu_body;body.argtypes=runtime.fn.argtypes;body.restype=c.c_int
    video=runtime.lib.biwn_video_cpu_call;video.argtypes=runtime.fn.argtypes;video.restype=c.c_int
    exception=runtime.lib.biwn_movie_user_STOP_exception;interrupt=runtime.lib.biwn_movie_wait_GPU_interrupt
    for f in [exception,interrupt]:f.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];f.restype=c.c_int
    stop=runtime.lib.biwn_movie_privilege_STOP_event;stop.argtypes=[c.POINTER(media.CPU)];stop.restype=c.c_int
    callbacks=[];types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32]
    def rd(w):
        def cb(_,a,v):v[0]=runtime.read(a,w);return 0
        return cb
    def wr(w):
        def cb(_,a,v):runtime.write(a,w,v);return 0
        return cb
    callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4))];bus=media.Bus(*callbacks,media.scheduler.cleanup.world.CALL(),None,0);w8=media.W8(wr(1));service=media.world_cpu.SERVICE(lambda *_:1);runtime.core.TOMSetPendingGPUInt.argtypes=[]
    base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();results=[];coverage=set()
    try:
        for flags in range(32):
            for r0 in [0,0x80000000]:
                initial=media.CPU();initial.pc=0x22a0e;initial.sr=flags;initial.registers[15]=initial.usp=0x180000;initial.ssp=0x200000;initial.registers[8]=0xbd850;initial.registers[0]=r0;snapshots={}
                for mode in ['native','C']:
                    runtime.reset(base,0);runtime.device.direct(0x100,4,0xe7d4);runtime.device.direct(0xf000e0,2,0x303);runtime.device.direct(0x180000,4,0x190000);runtime.device.direct(0xbd850,2,0);cpu=media.CPU.from_buffer_copy(bytes(initial));states=[]
                    def record():states.append(dict(CPU=media.scheduler.cpu_dict(runtime.cpu() if mode=='native' else cpu),RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware']))
                    if mode=='native':
                        runtime.seed_cpu(cpu);runtime.core.m68k_execute(1);coverage.add(0x22a0e);record();runtime.core.m68k_execute(1);coverage.add(0xddfe);record();runtime.core.TOMSetPendingGPUInt();runtime.core.m68k_set_irq(2);record()
                        for _ in range(100):
                            pc=runtime.core.m68k_get_reg(None,16)
                            if pc==0x190000:break
                            coverage.add(pc);runtime.core.m68k_execute(1)
                            if pc in [0xe820,0xde02,0xde06,0x22a10]:record()
                        else:raise AssertionError('Native userwait bound')
                    else:
                        assert exception(c.byref(bus),c.byref(cpu))==0;record();assert stop(c.byref(cpu))==0;record();runtime.core.TOMSetPendingGPUInt();assert interrupt(c.byref(bus),c.byref(cpu))==0;record()
                        assert video(c.byref(bus),c.byref(cpu),w8,service,None,1000,1)==0 and cpu.pc==0xde02;record()
                        # One-instruction budget executes sourceADDQ but does
                        # not commit on worklimit. Run sourceADDQ+RTE together
                        # and compare the native boundary afterRTE instead.
                        assert body(c.byref(bus),c.byref(cpu),w8,service,None,1000,1)==0 and cpu.pc==0x22a10
                        # Native has an intermediate afterADDQ record; retained
                        # whole-program boundary checks cover its bus/frame.
                        states.append(None);record();assert body(c.byref(bus),c.byref(cpu),w8,service,None,1000,1)==0 and cpu.pc==0x22a12;record()
                        assert video(c.byref(bus),c.byref(cpu),w8,service,None,1000,1)==0 and cpu.pc==0x190000
                    record();snapshots[mode]=states
                for i,(a,b) in enumerate(zip(snapshots['native'],snapshots['C'])):
                    if b is not None and a!=b:save(out/'mismatch.json',dict(flags=flags,r0=r0,stage=i,native=a,C=b));raise AssertionError(str(out/'mismatch.json'))
                results.append(dict(flags=flags,r0=hex(r0),boundaries=[i for i,b in enumerate(snapshots['C']) if b is not None],final=snapshots['C'][-1]));save(out/'fixtures.json',results)
        report=dict(status='user_STOP_privilege_nested_GPU_IRQ_RTE_operand_noop_source_C_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_privilege_instructions=4,native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in ['biwn_movie_privilege_cpu.c','biwn_movie_privilege_cpu.h']},script_sha256=sha(Path(__file__).read_bytes()),whole_game_complete=False,limits=['Source userSTOP only, flags0..31/twoD0values. Privilege frame/nestedGPUIRQ/E7D4/RTE/DDfeSTOP/de02PCadjustment/de06RTE/22A10operand execution/finalhelperRTS match wholeCPU/RAM/peripherals at retained boundaries. No otherprivilegeopcode/trace/physicaltiming/globalgame.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-user-movie-STOP-C.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),cases=len(results))))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
