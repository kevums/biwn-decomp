"""Real strict CPU-owner exception/RTE roundtrips; original opcodes only in control."""
import ctypes as c,json,random
from datetime import datetime,timezone
from pathlib import Path
import biwn_fast_CPU_bridge as bridge
from check_biwn_division_CPU import inventory
from check_biwn_scheduler import Native,CPU,cpu_dict
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    buildp=ROOT/'verification/CPU-division-provider-build-current.json';build=json.loads(buildp.read_text());directory=Path(build['directory']);cp=Path(build['CPU_candidate']);candidate=json.loads(cp.read_text());atlas,entries=inventory(candidate)
    nativep=directory/'native-CPU-candidate.json';native=json.loads(nativep.read_text())
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';assert sha(core)==native['required_core_sha256']
    out=ROOT/'verification/CPU-division-owner-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    n=Native(diagnostic_core=core);l=n.lib;fixture=bytearray(atlas);fixture[20:24]=(0xde06).to_bytes(4,'big');assert fixture[0xde06:0xde08]==bytes.fromhex('4e73')
    for at in [0x1d0000-8,0x1e0000-8]:fixture[at:at+8]=b'\xa5'*8
    fixture[0x49d24:0x49d28]=b'\0'*4
    n.device.seed(bytes(fixture),0)
    owner,retired,library,host,finish=bridge.install(l,out,'C',n.device.pointer,nativep,trace=False)
    l.BIWNReadCPUState.argtypes=[c.POINTER(CPU)]
    def read_cpu():
        cpu=CPU();l.BIWNReadCPUState(c.byref(cpu));return cpu_dict(cpu)
    rng=random.Random(0xd1e0de06);rows=[];failures=[]
    try:
        for entry in entries:
            if entry['operand_kind']=='immediate':continue
            for ipl in range(8):
                for mode in [0,0x2000]:
                    for flags in range(32):
                        regs=[rng.getrandbits(32) for _ in range(15)]+[0x1d0000]
                        regs[entry['destination']]=rng.getrandbits(32)
                        if entry['operand_kind']=='register':regs[entry['operand']]&=0xffff0000
                        lanes={}
                        for lane in ['reference','C']:
                            l.BIWNSetCPUExecOwner(owner if lane=='C' else bridge.OWNER(),int(lane=='C'))
                            for at in [0x1d0000-8,0x1e0000-8]:
                                n.device.direct(at,4,int.from_bytes(fixture[at:at+4],'big'));n.device.direct(at+4,4,int.from_bytes(fixture[at+4:at+8],'big'))
                            l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,0x1e0000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1c0000);l.m68k_set_reg(17,mode|(ipl<<8)|flags)
                            for i,value in enumerate(regs):l.m68k_set_reg(i,value)
                            l.m68k_set_reg(16,entry['pc'])
                            stages=[]
                            for step in range(2):
                                cycles=l.m68k_execute(1)
                                stages.append(dict(cycles=cycles,CPU=read_cpu(),RAM_sha256=__import__('hashlib').sha256(n.device.ram()).hexdigest()))
                            counts={name:getattr(l,'BIWNCPU'+name+'InstructionCount')() for name in ['Owned','Original','Rejected']}
                            lanes[lane]=dict(stages=stages,counts=counts)
                        matched=lanes['reference']['stages']==lanes['C']['stages'] and lanes['C']['counts']==dict(Owned=2,Original=0,Rejected=0)
                        final=lanes['C']['stages'][-1]['CPU']
                        matched=matched and final['pc']==entry['pc']+entry['size'] and final['sr']==(mode|(ipl<<8)|flags)&~2
                        row=dict(PC=hex(entry['pc']),sr=mode|(ipl<<8)|flags,matched=matched,C_counts=lanes['C']['counts']);rows.append(row)
                        if not matched and len(failures)<8:failures.append(dict(**row,lanes=lanes))
            print(hex(entry['pc']),'roundtrips',len(rows),'failures',sum(not row['matched'] for row in rows),flush=True)
        stats=finish()
    finally:
        l.BIWNSetCPUExecOwner(bridge.OWNER(),0);n.close()
    save(out/'cases.json',rows);save(out/'first-mismatches.json',failures)
    proof=dict(status='terminal_strict_C_division_exception_RTE_pass' if not failures else 'terminal_strict_C_division_exception_RTE_rejected',
        directory=str(out),roundtrips=len(rows),instruction_boundaries=2*len(rows),failed_roundtrips=sum(not row['matched'] for row in rows),
        C_original_opcode_fallback=0 if all(row['C_counts']['Original']==0 for row in rows) else None,
        C_rejections=sum(row['C_counts']['Rejected'] for row in rows),backend=stats,
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',buildp,cp,Path(candidate['library']),nativep,Path(native['library']),Path(native['directory'])/'fast_CPU_bridge.c',core]},
        scope='22 fixed variable-divisor addresses; all32CCR,bothmodes,all8IPL; actual original zero trap then existing DE06 RTE versus strict C owner. FullCPU/2MBRAMhash and per-instruction emulator charges at both boundaries. No physical timing,asyncIRQs,busfaults or fullgame claim.',new_training=False,default_promoted=False)
    save(out/'protocol.json',proof);save(ROOT/'verification/CPU-division-owner-check-current.json',proof)
    print(json.dumps({k:proof[k]for k in ['status','roundtrips','failed_roundtrips','C_original_opcode_fallback','C_rejections']}),flush=True)

if __name__=='__main__':main()
