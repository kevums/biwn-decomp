"""Direct D414 TRAP0 and source DE08/RTE vs C, preserving real private frames."""
import ctypes as c
import json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;CPU=media.CPU;save=media.save;sha=media.sha

def main():
    out=ROOT/'verification/BIWN-movie-trap'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmovie-trap.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_movie_trap.c'),str(source/'biwn_scheduler.c'),str(source/'biwn_media_setup_cpu.c'),'-o',str(library)]
    p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    runtime=media.Runtime(library,[]);fn=runtime.lib.biwn_movie_trap_dispatch;fn.argtypes=[c.POINTER(media.Bus),c.POINTER(CPU),c.c_uint32];fn.restype=c.c_int
    types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32]
    errors=[];fail=None
    def rd(w):
        def cb(_,a,out):
            if fail==('read',w):return 1
            try:out[0]=runtime.read(a,w);return 0
            except Exception as e:errors.append(repr(e));return 1
        return cb
    def wr(w):
        def cb(_,a,v):
            if fail==('write',w):return 1
            try:runtime.write(a,w,v);return 0
            except Exception as e:errors.append(repr(e));return 1
        return cb
    callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4))];bus=media.Bus(*callbacks,media.scheduler.cleanup.world.CALL(),None,0)
    base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0xd414de08);results=[];coverage=set()
    try:
        for flags in range(32):
            for count in [1,2,4]:
                for blocked in [False,True] if count>1 else [False]:
                    case=len(results);initial=CPU();initial.registers[:]=[rng.getrandbits(32) for _ in range(15)]+[0x1fe000];initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.pc=0xd414;initial.sr=0x700|flags
                    ram=bytearray(base)
                    def put(a,w,v):ram[a:a+w]=v.to_bytes(w,'big')
                    put(0x80,4,0xde08);put(0xc0920,4,0x100000);put(0x778cc,4,10)
                    for i in range(count):
                        obj=0x100000+i*0x1000
                        for a,w,v in [(obj,4,0x100000+(i+1)%count*0x1000),(obj+12,4,0x180000+i*0x1000),(obj+16,4,0x190000+i*2),(obj+20,2,0x700|((flags+i)&31)),(obj+22,4,10 if i==2 else 0),(obj+26,4,1 if blocked and i==1 else 0),(obj+34,4,0)]:put(a,w,v)
                    ram=bytes(ram);runtime.reset(ram,0);runtime.seed_cpu(initial)
                    for _ in range(1000):
                        pc=runtime.core.m68k_get_reg(None,16)
                        if pc==0xd416 or 0x190000<=pc<0x190008:break
                        assert pc==0xd414 or 0xde08<=pc<0xde5c,hex(pc);coverage.add(pc);runtime.core.m68k_execute(1)
                    else:raise AssertionError('Native trap bound')
                    left=runtime.device.ram();expected=runtime.cpu()
                    runtime.reset(ram,0);actual=CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(actual),16)
                    right=runtime.device.ram()
                    if status or left!=right or bytes(expected)!=bytes(actual):
                        save(out/'mismatch.json',dict(case=case,status=status,CPU_native=media.scheduler.cpu_dict(expected),CPU_C=media.scheduler.cpu_dict(actual),RAM_diff=[hex(i) for i,(a,b) in enumerate(zip(left,right)) if a!=b][:20],errors=errors));raise AssertionError(str(out/'mismatch.json'))
                    # Dispatch reuses the six-byte supervisor frame for the
                    # selected context; the outgoing PC survives in its TCB.
                    assert int.from_bytes(right[initial.ssp-4:initial.ssp],'big')==actual.pc
                    assert int.from_bytes(right[0x100000+16:0x100000+20],'big')==0xd416
                    results.append(dict(case=case,flags=flags,contexts=count,blocked_next=blocked,CPU=media.scheduler.cpu_dict(actual),RAM_sha256=sha(right)))
        guards=[];initial.pc=0xd414;initial.sr=0x700
        for kind in ['null_bus','null_state','zero_limit','bad_PC','supervisor','trace','bad_vector','read16','read32','write16','write32','missing_read16','missing_read32','missing_write16','missing_write32']:
            runtime.reset(ram,0);s=CPU.from_buffer_copy(bytes(initial));b=media.Bus.from_buffer_copy(bytes(bus));limit=16;fail=None
            if kind=='bad_PC':s.pc=0xd416
            if kind=='supervisor':s.sr|=0x2000
            if kind=='trace':s.sr|=0x8000
            if kind=='bad_vector':runtime.device.direct(0x80,4,0)
            if kind.startswith('missing_'):
                key=kind[8:];setattr(b,key,types[['read8','read16','read32','write16','write32'].index(key)]())
            elif kind in ['read16','read32','write16','write32']:fail=('read' if kind.startswith('read') else 'write',int(kind[-2:])//8)
            before=bytes(s);status=fn(None if kind=='null_bus' else c.byref(b),None if kind=='null_state' else c.byref(s),0 if kind=='zero_limit' else limit)
            assert status!=0 and bytes(s)==before,(kind,status);guards.append(dict(kind=kind,status=status,CPU_unchanged=True))
        save(out/'fixtures.json',results);save(out/'guards.json',guards)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='direct_movie_TRAP0_source_exception_dispatch_RTE_native_C_match',directory=str(out),cases=len(results),guards=len(guards),native_PC_coverage=sorted(coverage),
            source_sha256={n:sha((source/n).read_bytes()) for n in ['biwn_movie_trap.c','biwn_movie_trap.h','biwn_scheduler.c','biwn_scheduler.h']},script_sha256=sha(Path(__file__).read_bytes()),
            matched=['Actual TRAP0 and RTE, full CPU/SR/both stack banks and all2MB RAM. Direct returnPC D416 and source context save/select preserved; no injected DF60/private MOVEM frame.'],
            limits=['Supplied user-mode rings/clock/deadlines, no source movie caller execution, trace or external IRQ/timing, physical hardware or full game.'],new_published_components=0,whole_game_complete=False)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-trap.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),cases=len(results),guards=len(guards))))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()
