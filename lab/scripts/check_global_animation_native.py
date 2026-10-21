"""Cross-check selected accepted function fixtures with the pinned Jaguar CPU."""
import ctypes as c
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
import check_local_global_animation_tick as test
import check_biwn_media_setup_cpu as media
ROOT=test.ROOT
def main():
    proof=json.loads((ROOT/'verification/local-global-animation-checks-current.json').read_text());out=Path(proof['directory']);source=Path(proof['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==proof['source_sha256']
    rows=json.loads((out/'fixtures.json').read_text())[:720];selected=rows[::15]
    library=c.CDLL(str(out/'libglobal-animation-tick.dylib'));fn=library.biwn_global_animation_tick;fn.argtypes=[c.POINTER(test.boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=media.scheduler.Native(diagnostic_core=core);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();coverage=set();results=[]
    try:
        for row in selected:
            case=row['parameters'];a=test.boundary.Script(snapshot,case);b=test.boundary.Script(snapshot,case);memory=bytearray(a.memory);memory[test.SP:test.SP+4]=test.STOP.to_bytes(4,'big')
            initial=media.CPU();initial.registers[:15]=case['incoming'];initial.registers[15]=test.SP;initial.usp=0x180000;initial.ssp=test.SP;initial.sr=0x2000;initial.pc=0x10ba4
            runtime.device.seed(bytes(memory),0);runtime.seed_cpu(initial);pcs=[]
            for _ in range(100):
                state=runtime.cpu()
                if state.pc==test.STOP:break
                assert 0x10ba4<=state.pc<=0x10c16;pcs.append(state.pc);coverage.add(state.pc);runtime.core.m68k_execute(1)
            else:raise AssertionError('Native CPU bound')
            native=runtime.cpu();native_RAM=runtime.device.ram();status,value,errors=test.translated(fn,b,case)
            assert not status and not errors and value==native.registers[0]==row['full_D0']
            assert native_RAM[:test.SP]==b.memory[:test.SP]and native_RAM[test.SP+4:]==b.memory[test.SP+4:]
            assert pcs==row['steps']
            results.append(dict(fixture=row['case'],original_PC_trace=pcs,full_D0=value,external_RAM_match=True))
    finally:oracle.close()
    assert len(coverage)==26
    report=dict(status='accepted_local_global_animation_matches_pinned_native_CPU',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),original_instruction_address_coverage=[26,26],core=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),source=str(source),source_sha256=proof['source_sha256'],source_body_edited=False,original_cases=results,full_route_runtime_promoted=False,new_training=False,scope='48selected static-RAM edge fixtures cover all26original instructions,matching originalPCsequence/fullD0/externalRAM in pinned JaguarCPU as well as the separate723-case Unicorn comparison. Volatile rereads are in the Unicorn proof. CCR/otherregisters/private stack/timing/naturalgameplay excluded.')
    (out/'native-original-review.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-global-animation-native-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(results))
if __name__=='__main__':main()
