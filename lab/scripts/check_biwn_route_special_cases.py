"""Original-core differential checks for new BSET byte and signed DIVS cases."""
import argparse, ctypes as c, hashlib, json, random
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
import check_biwn_media_setup_cpu as media

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--candidate',type=Path)
    parser.add_argument('--output-report',type=Path)
    args=parser.parse_args()
    if args.candidate and not args.output_report:
        parser.error('Custom candidates require an isolated --output-report')
    candidate=json.loads((args.candidate or ROOT/'verification/route-CPU-full-reference-experimental-candidate.json').read_text())
    native=scheduler.Native()
    core=native.lib
    ram=Path(candidate['warm_RAM_source']).read_bytes()
    native.device.seed(ram,0)
    library=c.CDLL(candidate['library'])
    step=library.biwn_route_CPU_step
    step.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p]
    step.restype=c.c_int
    types=media.scheduler.cleanup.world
    writes=[]
    def rd(width):
        def fn(_,address,value):value[0]=native.device.read(address,width);return 0
        return fn
    def wr(width):
        def fn(_,address,value):writes.append([address,width,value]);native.device.direct(address,width,value);return 0
        return fn
    callbacks=[types.R8(rd(1)),types.R16(rd(2)),types.R32(rd(4)),types.W16(wr(2)),types.W32(wr(4)),media.W8(wr(1))]
    bus=media.Bus(*callbacks[:5],types.CALL(),None,0)
    service=media.world_cpu.SERVICE(lambda *_:1)
    def seed(s):
        core.m68k_pulse_reset();core.m68k_set_irq(0)
        core.m68k_set_reg(17,0x2700);core.m68k_set_reg(15,s.ssp)
        core.m68k_set_reg(17,0x700);core.m68k_set_reg(15,s.usp)
        core.m68k_set_reg(17,s.sr)
        for i,v in enumerate(s.registers):core.m68k_set_reg(i,v)
        core.m68k_set_reg(16,s.pc)
    def cpu():
        s=media.CPU();s.registers[:]=[core.m68k_get_reg(None,i)for i in range(16)]
        s.pc=core.m68k_get_reg(None,16);s.sr=core.m68k_get_reg(None,17)
        s.usp=native.prefix[16]if s.sr&0x2000 else s.registers[15]
        s.ssp=s.registers[15]if s.sr&0x2000 else native.prefix[17]
        return s
    rng=random.Random(0xea781adea)
    totals={'BSET':0,'DIVS':0,'DIVS_overflow':0}
    digest=hashlib.sha256()
    out=ROOT/'verification/route-special-cases'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    def check(pc,value,sr,dividend=None,divisor=None):
        s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(16)]
        s.pc=pc;s.sr=sr;s.usp=0x1fe000;s.ssp=0x1ff000;s.registers[15]=s.ssp if sr&0x2000 else s.usp
        s.registers[10]=0x80000
        if dividend is not None:s.registers[0]=dividend&0xffffffff;s.registers[3]=(s.registers[3]&0xffff0000)|(divisor&0xffff)
        native.device.direct(0x80007,1,0xa5);native.device.direct(0x80008,1,value);native.device.direct(0x80009,1,0x5a)
        seed(s);cycles=core.m68k_execute(1);expected=cpu();byte=native.device.read(0x80008,1)
        native.device.direct(0x80008,1,value);writes.clear();rebuilt=media.CPU.from_buffer_copy(bytes(s))
        status=step(c.byref(bus),c.byref(rebuilt),callbacks[5],service,None)
        assert status==0 and bytes(expected)==bytes(rebuilt),(hex(pc),value,dividend,divisor,sr,media.scheduler.cpu_dict(expected),media.scheduler.cpu_dict(rebuilt))
        assert native.device.read(0x80008,1)==byte and native.device.read(0x80007,1)==0xa5 and native.device.read(0x80009,1)==0x5a
        assert writes==([[0x80008,1,value|128]]if pc==0xea78 else [])
        digest.update(bytes(expected)+cycles.to_bytes(4,'big',signed=True))
        return cycles
    try:
        for supervisor in [False,True]:
            for flags in range(32):
                sr=(0x2700 if supervisor else 0x700)|flags
                for value in range(256):
                    assert check(0xea78,value,sr)==20
                    totals['BSET']+=1
                dividends=[-2147483648,-1000000,-65536,-32769,-32768,-1,0,1,32767,32768,65535,1000000,2147483647]
                divisors=[-32768,-123,-2,-1,1,2,123,32767]
                for a in dividends:
                    for b in divisors:
                        # The pinned C interpreter divides signedint32 here;
                        # avoid its undefined INT32_MIN/-1 host operation.
                        if a==-2147483648 and b==-1:continue
                        check(0x1adea,0x33,sr,a,b);totals['DIVS']+=1
                        q=abs(a)//abs(b)*(-1 if(a<0)!=(b<0)else 1)
                        totals['DIVS_overflow']+=int(q< -32768 or q>32767)
        report=dict(status='original_C_special_instruction_states_and_memory_match',counts=totals,
            library=candidate['library'],library_sha256=hashlib.sha256(Path(candidate['library']).read_bytes()).hexdigest(),
            result_digest=digest.hexdigest(),limits=['Two source-specific instructions, both stack banks and32CCRpatterns; all256BSETinputbytes.','DIVSzero exceptions not implemented and explicitly reject. INT32_MIN/-1 excluded from original interpreter due host C undefined division.','BSET20cycle count checked; broader cost/state/whole route remains a separate runtime comparison.'],whole_game_complete=False)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        (args.output_report or ROOT/'verification/route-special-cases-current.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report),flush=True)
    finally:
        native.close()


if __name__=='__main__':main()
