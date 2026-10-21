"""Check startup observation and nested-yield host API contracts."""
import ctypes as c,json,hashlib
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_startup_rng_cpu as check
ROOT=check.ROOT;report=json.loads((ROOT/'verification/startup-caller-fullCPU-checks.json').read_text());library=Path(report['directory'])/'libstartup-rng-cpu.dylib'
lib=c.CDLL(str(library));fn=lib.biwn_startup_cpu_body;fn.argtypes=[c.POINTER(check.queue.world.Bus),c.POINTER(check.CPU),check.queue.cd.dispatch.W8,check.queue.cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
def main():
    events=[]
    def read(w):
        def cb(_,a,v):events.append(['r',a,w]);v[0]=0;return 0
        return cb
    def write(w):
        def cb(_,a,v):events.append(['w',a,w,v]);return 0
        return cb
    callbacks=[check.queue.world.R8(read(1)),check.queue.world.R16(read(2)),check.queue.world.R32(read(4)),check.queue.world.W16(write(2)),check.queue.world.W32(write(4)),check.queue.cd.dispatch.W8(write(1))]
    bus=check.queue.world.Bus(*callbacks[:5],check.queue.world.CALL(),None,0);noop=check.queue.cd.world_cpu.SERVICE(lambda *_:0);rows=[]
    def state(pc,sr=0):
        s=check.CPU();s.registers[:]=list(range(15))+[check.SP];s.pc=pc;s.sr=sr;s.usp=0x170000 if sr&0x2000 else check.SP;s.ssp=check.SP if sr&0x2000 else 0x1d0000;return s
    for sr in [0,0x2000]:
        for name,expected in [('ready',8),('bad_pc',7),('null_bus',1),('null_cpu',1),('null_write8',1),('null_service',1),('zero_budget',1),('bad_yield',1)]:
            s=state(0 if name=='bad_pc'else 0x17dc2,sr);before=bytes(s);events.clear()
            status=fn(None if name=='null_bus'else c.byref(bus),None if name=='null_cpu'else c.byref(s),check.queue.cd.dispatch.W8()if name=='null_write8'else callbacks[5],check.queue.cd.world_cpu.SERVICE()if name=='null_service'else noop,None,0 if name=='zero_budget'else 100,2 if name=='bad_yield'else 1)
            assert status==expected and bytes(s)==before and not events
            rows.append(dict(contract=name,SR=hex(sr),status=status,CPU_unchanged=True,no_bus_effects=True))
        for boundary in [0xdf60,0xdf8c]:
            s=state(0x17c40,sr);events.clear()
            def suspend(_,passed,cpu,target):assert target==cpu.contents.pc==0x4088;cpu.contents.pc=boundary;return 6
            callback=check.queue.cd.world_cpu.SERVICE(suspend);status=fn(c.byref(bus),c.byref(s),callbacks[5],callback,None,100,1)
            expected_writes=[['w',check.SP-4,4,10],['w',check.SP-8,4,4],['w',check.SP-12,4,3],['w',check.SP-16,4,2],['w',check.SP-20,4,0x17c4a]]
            assert status==6 and s.pc==boundary and s.registers[15]==check.SP-20 and events==expected_writes
            assert (s.ssp if sr&0x2000 else s.usp)==check.SP-20
            rows.append(dict(contract='supplied_nested_suspension',SR=hex(sr),boundary=hex(boundary),status=status,source_MOVEM_JSR_frames_preserved=True,events=list(events)))
    out=ROOT/'verification/startup-CPU-host-contracts.json';result=dict(status='startup_CPU_host_contracts_pass',recorded_at=datetime.now(timezone.utc).isoformat(),cases=len(rows),rows=rows,library=str(library),library_sha256=hashlib.sha256(library.read_bytes()).hexdigest(),test_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits='Host API guards and supplied helper suspension only; does not execute real DF60/DF8C wrappers, scheduler or source boot.');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],cases=len(rows))))
if __name__=='__main__':main()
