"""Pinned native caller+tick with explicit machine-code helper fixtures."""
import ctypes as c,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import check_local_six_function_scene as test
import check_biwn_media_setup_cpu as media
ROOT=test.ROOT
def main():
    proof=json.loads((ROOT/'verification/local-six-function-scene-integration-current.json').read_text());out=Path(proof['directory']);assert hashlib.sha256(Path(proof['source']).read_bytes()).hexdigest()==proof['source_sha256']
    rows=json.loads((out/'fixtures.json').read_text());selected=[rows[(k*13)%len(rows)]for k in range(48)];lib=c.CDLL(str(out/'libglobal-scene-prepare.dylib'));fn=lib.biwn_global_scene_prepare;tick=lib.biwn_global_animation_tick
    for f in [fn,tick]:f.argtypes=[c.POINTER(test.animation.boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];f.restype=c.c_int
    test.SLOT_FN=lib.biwn_slot_clear;test.SLOT_FN.argtypes=[c.POINTER(test.slot.Bus),c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];test.SLOT_FN.restype=c.c_int
    test.PREPARE_FN=lib.biwn_scene_slot_prepare;test.PREPARE_FN.argtypes=[c.POINTER(test.animation.boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];test.PREPARE_FN.restype=c.c_int
    test.FACE_FN=lib.biwn_face_coordinates;test.FACE_FN.argtypes=[c.POINTER(test.animation.boundary.world.Bus),c.c_uint32,c.c_uint32,c.c_uint16,c.POINTER(c.c_uint32)];test.FACE_FN.restype=c.c_int
    test.EXPAND_FN=lib.biwn_scene_slots_expand;test.EXPAND_FN.argtypes=[c.POINTER(test.animation.boundary.world.Bus),c.POINTER(test.expand.Seed),c.POINTER(c.c_uint32)];test.EXPAND_FN.restype=c.c_int
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=media.scheduler.Native(diagnostic_core=core);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();results=[]
    try:
        for row in selected:
            case=row['parameters'];a=test.Script(snapshot,case);b=test.Script(snapshot,case);memory=bytearray(a.memory);stubs=[]
            for target in test.HELPERS:
                code=bytearray()
                for address,width,value in case['helper_effects'].get(str(target),[]):
                    assert width in [2,4];code+=(b'\x33\xfc'if width==2 else b'\x23\xfc')+value.to_bytes(width,'big')+address.to_bytes(4,'big')
                code+=(b'\x4e\x75'if target==0xe26c else b'\x20\x3c'+case['helper_returns'][str(target)].to_bytes(4,'big')+b'\x4e\x75');memory[target:target+len(code)]=code;stubs.append(dict(target=hex(target),bytes=code.hex(),length=len(code)))
            memory[test.SP:test.SP+4]=test.STOP.to_bytes(4,'big');initial=media.CPU();initial.registers[:15]=case['incoming'];initial.registers[15]=test.SP;initial.usp=0x180000;initial.ssp=test.SP;initial.sr=0x2000;initial.pc=0x11ad4
            runtime.device.seed(bytes(memory),0);runtime.seed_cpu(initial);pcs=[]
            for _ in range(6000):
                state=runtime.cpu()
                if state.pc==test.STOP:break
                pcs.append(state.pc);runtime.core.m68k_execute(1)
            else:raise AssertionError('Native caller bound')
            native=runtime.cpu();ram=bytearray(runtime.device.ram());status,value,errors,ticks=test.translated(fn,tick,b,case)
            assert not status and not errors and ticks==[0]and value==native.registers[0]==row['full_D0']
            for stub in stubs:
                target=int(stub['target'],16);ram[target:target+stub['length']]=b.memory[target:target+stub['length']]
            assert ram[:test.SP-80]==b.memory[:test.SP-80]and ram[test.SP+4:]==b.memory[test.SP+4:]
            results.append(dict(case=row['case'],full_D0=value,original_native_PC_trace=pcs,helper_fixture_stubs=stubs,external_RAM_match=True))
    finally:oracle.close()
    report=dict(status='local_six_function_scene_match_pinned_native_CPU_values',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_sha256=proof['source_sha256'],tick_source_sha256=proof['tick_source_sha256'],core=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),coordinator_C_body_edits=True,coordinator_corrected_function='1142E',coordinate_local_model_repair=True,prepare_source_sha256=proof['prepare_source_sha256'],face_source_sha256=proof['face_source_sha256'],expand_source_sha256=proof['expand_source_sha256'],slot_source_sha256=proof['slot_source_sha256'],results=results,new_training=False,full_route_runtime_promoted=False,scope='48selected caller+real10BA4+10968+11384+110D4+1142Efixtures match pinned JaguarCPU fullD0/externalRAM. E26C GPU service and10734 use explicit machine-code fixture stubs for supplied RAM effects; E26C preserves originalD0 viaRTS,10734 returns fixtureD0. E26C GPU internals/stack-word overread excluded. Nativebus dummy read order,CCR,otherregisters,private stack,timing and naturalgameplay excluded; ordered logical access proof is the separate Unicorn comparison.')
    (out/'native-original-review.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-six-function-scene-native-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['cases'])
if __name__=='__main__':main()
