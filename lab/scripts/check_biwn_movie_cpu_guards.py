"""Error/continuation contract for source movie CPU candidate; no video claim."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_movie_cpu as movie
ROOT=movie.ROOT;save=movie.save;sha=movie.sha

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-CPU.json').read_text())
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'movie-fullCPU-generation.json').read_text());setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text())
    runtime=movie.Runtime(Path(proof['directory'])/'libmovie.dylib',mapping['instructions_decoded']+setup['instructions_decoded'])
    out=ROOT/'verification/BIWN-movie-CPU-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    types=[movie.media.scheduler.cleanup.world.R8,movie.media.scheduler.cleanup.world.R16,movie.media.scheduler.cleanup.world.R32,movie.media.scheduler.cleanup.world.W16,movie.media.scheduler.cleanup.world.W32,movie.W8]
    try:
        kinds=['null_bus','null_cpu','null_write8','null_service','zero_budget','bad_stop_flag','bad_PC','budget_one',
               'read8','read16','read32','write16','write32','service_error','service_bad_SP','service_bad_return',
               'trap_suspend','trap_unimplemented','division_zero']+['missing_'+key for key in ['read8','read16','read32','write16','write32']]
        for kind in kinds:
            runtime.reset(base,0);runtime.mode='C';runtime.timer_arm=False;runtime.timer_reads=0
            s=movie.CPU();s.registers[:]=[0x12345678]*15+[0x1fe000];s.usp=0x1fe000;s.ssp=0x1ff000;s.sr=0x700;s.pc=0xe902
            runtime.device.direct(s.registers[15],4,movie.STOP);runtime.device.direct(0xbd85c,2,0)
            if kind=='read8':s.pc=0xd500
            if kind=='read16':s.pc=0xd4a8
            if kind=='write16':s.pc=0xd7e4
            if kind.startswith('service_'):s.pc=0xd3c6
            if kind.startswith('trap_'):s.pc=0xd414
            if kind=='division_zero':s.pc=0xdc56;s.registers[0]=0
            if kind=='bad_PC':s.pc=0
            fail=None
            if kind in ['read8','read16','read32','write16','write32']:fail=('read' if kind.startswith('read') else 'write',int(kind[len('read') if kind.startswith('read') else len('write'):])//8)
            callbacks=[]
            for name,typ,w in zip(['read8','read16','read32','write16','write32','write8'],types,[1,2,4,2,4,1]):
                if name.startswith('read'):
                    def cb(_,a,out,w=w):
                        if fail==('read',w):return 1
                        out[0]=runtime.read(a,w);return 0
                else:
                    def cb(_,a,v,w=w):
                        if fail==('write',w):return 1
                        runtime.write(a,w,v);return 0
                callbacks.append(typ() if kind=='missing_'+name else typ(cb))
            bus=movie.Bus(*callbacks[:5],movie.media.scheduler.cleanup.world.CALL(),None,0)
            def provider(_,b,state,target):
                if kind=='service_error':return 1
                if kind=='service_bad_SP':state.contents.registers[15]+=4
                if kind=='service_bad_return':runtime.device.direct(state.contents.registers[15],4,0)
                return 0
            service=movie.media.world_cpu.SERVICE() if kind=='null_service' else movie.media.world_cpu.SERVICE(provider)
            before=bytes(s);RAM_before=sha(runtime.device.ram())
            status=runtime.movie_call(None if kind=='null_bus' else c.byref(bus),None if kind=='null_cpu' else c.byref(s),
                movie.W8() if kind=='null_write8' else callbacks[5],service,None,
                0 if kind=='zero_budget' else 1 if kind=='budget_one' else 10000,2 if kind=='bad_stop_flag' else 0 if kind=='trap_unimplemented' else 1)
            expected=6 if kind=='trap_suspend' else 8 if kind=='trap_unimplemented' else 9 if kind=='division_zero' else 7 if kind=='bad_PC' else 4 if kind=='budget_one' else 3 if kind=='service_error' else 5 if kind.startswith('service_bad') else 2 if kind in ['read8','read16','read32','write16','write32'] else 1
            assert status==expected and bytes(s)==before,(kind,status,expected)
            rows.append(dict(kind=kind,status=status,CPU_unchanged=True,prior_RAM_effects_retained=RAM_before!=sha(runtime.device.ram())))
        save(out/'guards.json',rows)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='movie_CPU_error_and_direct_TRAP_suspend_contract_checked',directory=str(out),guards=len(rows),source_sha256=mapping['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),rows=rows,new_published_components=0,whole_game_complete=False)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-CPU-guards.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),guards=len(rows))))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()
