"""Byte-exact legacy/register-only GPU state equivalence and RAM isolation."""
import ctypes as c,hashlib,json,random,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    candidate=json.loads((ROOT/'verification/GPU-register-state-experimental-candidate.json').read_text())
    assert candidate['status']=='compiled_core_tests_exit_zero_pending_register_API_equivalence'
    core=Path(candidate['core_path']);assert hashlib.sha256(core.read_bytes()).hexdigest()==candidate['core_sha256']
    lib=c.CDLL(str(core))
    for name in ['GPUStateSave','GPUStateLoad','BIWNGPUStateSaveRegisters','BIWNGPUStateLoadRegisters']:
        fn=getattr(lib,name);fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t
    lib.GPUGetRAM.restype=c.c_void_p;lib.GPUGetReg.argtypes=[c.c_int];lib.GPUGetReg.restype=c.c_uint32
    rng=random.Random(0x44160320);rows=[]
    def full():
        value=c.create_string_buffer(4416);assert lib.GPUStateSave(value)==4416;return value.raw
    for index in range(128):
        raw=bytearray(rng.randbytes(4416));raw[4395]=index%2;raw=bytes(raw)
        seed=c.create_string_buffer(raw);assert lib.GPUStateLoad(seed)==4416 and full()==raw
        buffer=c.create_string_buffer(bytes([0xa5])*336)
        assert lib.BIWNGPUStateSaveRegisters(c.byref(buffer,8))==320
        assert buffer.raw[:8]==bytes([0xa5])*8 and buffer.raw[328:336]==bytes([0xa5])*8
        assert buffer.raw[8:328]==raw[4096:]
        new_RAM=rng.randbytes(4096);c.memmove(lib.GPUGetRAM(),new_RAM,4096)
        assert lib.BIWNGPUStateLoadRegisters(c.byref(buffer,8))==320
        assert full()==new_RAM+raw[4096:]
        assert buffer.raw[:8]==bytes([0xa5])*8 and buffer.raw[328:336]==bytes([0xa5])*8
        changed=bytearray(rng.randbytes(320));changed[299]=(index+1)%2;value=c.create_string_buffer(bytes(changed))
        assert lib.BIWNGPUStateLoadRegisters(value)==320 and full()==new_RAM+bytes(changed)
        for register in [0,15,31]:
            offset=43+changed[299]*128+register*4
            assert lib.GPUGetReg(register)==int.from_bytes(changed[offset:offset+4],sys.byteorder)
        rows.append(dict(case=index,active_bank=changed[299],legacy_suffix_equal=True,RAM_retained=True,canaries_retained=True,active_bank_registers_equal=True))
    out=ROOT/'verification/GPU-register-state-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(status='register_state_legacy_suffix_RAM_isolation_and_bank_pointer_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),core_path=str(core),core_sha256=candidate['core_sha256'],cases=len(rows),suffix_bytes=320,retained_GPU_RAM_bytes=4096,buffer_canaries=True,active_bank_pointer_checks=384,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),fast_GPU_bridge_verified=False,performance_verified=False,default_promoted=False,whole_game_complete=False,scope='128deterministic random legacy states exercise both banks. SaveRegisters equals the exact320byte suffix of legacy4416byte serialization. LoadRegisters reproduces all suffix bytes without changing live4096byteRAM; active register pointers and adjacent caller-buffer canaries checked. No GPU instructions executed, no restored game frames, cross-core game equivalence or performance claim.')
    (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/GPU-register-state-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
