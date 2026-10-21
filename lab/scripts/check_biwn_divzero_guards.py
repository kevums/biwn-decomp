"""Local exception source host guards and side-effect order, separate from native cases."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
from check_local_GPU_wait_C import Bus,R8,R16,R32,W16,W32,CALL
from check_biwn_scheduler import CPU
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    bp=ROOT/'verification/CPU-division-provider-build-current.json';build=json.loads(bp.read_text());candidate=json.loads(Path(build['CPU_candidate']).read_text());lib=c.CDLL(candidate['library']);fn=lib.biwn_divzero_entry
    fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),c.c_uint32];fn.restype=c.c_int
    out=ROOT/'verification/CPU-divzero-host-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    log=[];fail_at=None;handler=0;resume=0x123456
    def read(_,a,p):
        log.append(['r32',a]);p[0]=handler;return int(len(log)==fail_at)
    def write32(_,a,v):log.append(['w32',a,v]);return int(len(log)==fail_at)
    def write16(_,a,v):log.append(['w16',a,v]);return int(len(log)==fail_at)
    callbacks=[R32(read),W16(write16),W32(write32)]
    bus=Bus(R8(),R16(),callbacks[0],callbacks[1],callbacks[2],CALL(),None,0)
    def cpu(mode=0):
        s=CPU();s.registers[:]=list(range(16));s.registers[15]=0x1d0000;s.usp=0x1d0000 if not mode else 0x1c0000;s.ssp=0x1e0000 if not mode else 0x1d0000;s.pc=0xd1e0;s.sr=mode|0x071f;return s
    rows=[]
    for name,b,s in [('null_bus',None,cpu()),('null_cpu',c.byref(bus),None)]:
        log.clear();old=bytes(s)if s is not None else None;status=fn(b,c.byref(s)if s is not None else None,resume)
        assert status==1 and not log and (s is None or bytes(s)==old);rows.append(dict(case=name,status=status))
    for missing in range(3):
        values=list(callbacks);values[missing]=[R32,W16,W32][missing]()
        bad=Bus(R8(),R16(),values[0],values[1],values[2],CALL(),None,0);s=cpu();old=bytes(s);log.clear();status=fn(c.byref(bad),c.byref(s),resume)
        assert status==1 and bytes(s)==old and not log;rows.append(dict(case='missing_callback_'+str(missing),status=status))
    for bit in range(16):
        if 0x271f&(1<<bit):continue
        s=cpu();s.sr|=1<<bit;old=bytes(s);log.clear();status=fn(c.byref(bus),c.byref(s),resume)
        assert status==1 and bytes(s)==old and not log;rows.append(dict(case='unsupported_SR_bit_'+str(bit),status=status))
    for mode in [0,0x2000]:
        sp=0x1e0000 if not mode else 0x1d0000
        expected=[['w32',sp-4,resume],['w16',sp-6,(mode|0x071f)&~2],['r32',20]]
        for stage in [1,2,3]:
            s=cpu(mode);old=bytes(s);log.clear();fail_at=stage;status=fn(c.byref(bus),c.byref(s),resume)
            assert status==2 and bytes(s)==old and log==expected[:stage]
            rows.append(dict(case='callback_failure_'+str(stage),mode=mode,status=status,observed=list(log),prior_effects_not_rolled_back=True))
        for handler in [0,0x190000]:
            fail_at=None;s=cpu(mode);log.clear();status=fn(c.byref(bus),c.byref(s),resume)
            assert status==11 and log==expected and s.pc==handler and s.registers[15]==s.ssp==sp-6 and s.sr==0x271d
            assert s.usp==(0x1d0000 if not mode else 0x1c0000)
            rows.append(dict(case='ordered_success',mode=mode,handler=handler,status=status,observed=list(log)))
    proof=dict(status='terminal_local_divzero_host_guards_pass',directory=str(out),cases=len(rows),cases_detail=rows,local_C_unedited=True,
        scope='Added host error contracts and declared stack/vector callback order; distinct from native CPU/RAM/cycle and strict-owner gates. Partial writes on error are retained.',
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',bp,Path(candidate['library']),Path(build['local_exception_source'])]},new_training=False,default_promoted=False)
    save(out/'protocol.json',proof);save(ROOT/'verification/CPU-divzero-host-guards-current.json',proof);print(proof['status'],len(rows))

if __name__=='__main__':main()
