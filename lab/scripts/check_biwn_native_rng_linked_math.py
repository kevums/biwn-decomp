"""Check arithmetic relocation in the new RNG-containing native bundle."""
from datetime import datetime, timezone
import json
from pathlib import Path
from check_biwn_native_optimized_math import Runner, BASE
from check_biwn_native_button_digit import ROOT, save, sha


def main():
    build_path=ROOT/'verification/native-rng-disc-build-current.json'
    build=json.loads(build_path.read_text())
    payload=Path(build['component']).read_bytes();assert sha(build['component'])==build['component_sha256']
    out=ROOT/'verification/native-rng-linked-math'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    image=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload
    symbols=build['symbols'];runner=Runner();rows=[];zero=[]
    names={0xe540:'biwn_native_multiply',0xe588:'biwn_native_division',0xe60a:'biwn_native_remainder'}
    pairs=[(0,1),(1,0xffff),(0xffffffff,3),(0x80000000,1),(0x80000000,0xffffffff),(0x12345678,0x80000000),(0x7fffffff,0x10000),(0xdeadbeef,0x5a5a5a5a)]
    try:
        for entry,name in names.items():
            for a,b in pairs:
                for mode in [0,0x2000]:
                    for ccr in range(32):
                        d2=[0,0x80000000,0xffffffff][ccr%3];sr=mode|ccr
                        expected,faults,_=runner.run(image,entry,[(0xe540,0xe61c)],a,b,sr,d2,0xdeadbeef)
                        actual,new_faults,_=runner.run(bytes(candidate),symbols[name],[(BASE,BASE+len(payload))],a,b,sr,d2,0xdeadbeef)
                        assert actual==expected and not faults and not new_faults,(entry,a,b,sr,expected,actual)
                        rows.append(dict(entry=hex(entry),a=a,b=b,SR=sr,D2=d2,full_CPU_match=True))
            print('linked math',hex(entry),len(rows),flush=True)
        for entry in [0xe588,0xe60a]:
            for a in [0,1,0x80000000,0xffffffff]:
                for mode in [0,0x2000]:
                    for ccr in range(32):
                        d2=[0,0x80000000,0xffffffff][ccr%3];sr=mode|ccr
                        expected,faults,_=runner.run(image,entry,[(0xe540,0xe61c)],a,0,sr,d2,0xdeadbeef)
                        actual,new_faults,_=runner.run(bytes(candidate),symbols[names[entry]],[(BASE,BASE+len(payload))],a,0,sr,d2,0xdeadbeef)
                        assert actual==expected and len(faults)==len(new_faults)==1
                        old=faults[0].copy();new=new_faults[0].copy();old_pc=old.pop('frame_PC');new_pc=new.pop('frame_PC');assert old==new
                        delta=old_pc-0xe606;assert delta in [0,2] and new_pc==symbols['biwn_native_division_fault']+delta
                        zero.append(dict(entry=hex(entry),numerator=a,SR=sr,full_return_CPU_and_trap_state_match=True,expected_fault_PC_relocation=True))
    finally:runner.n.close()
    save(out/'normal-results.json',rows);save(out/'zero-results.json',zero)
    report=dict(status='terminal_relocated_arithmetic_with_rng_bundle_pass',directory=str(out),
                build_proof=str(build_path),build_proof_sha256=sha(build_path),normal_cases=len(rows),zero_exception_cases=len(zero),
                source_sha256={str(p):sha(p)for p in [Path(__file__),Path(build['component']),ROOT/'scripts/check_biwn_native_optimized_math.py']},
                scope='Relocation regression for existing three arithmetic entry contracts within new RNG bundle. Zero cases execute native DIVU and an inert declared RTE handler with expected saved-PC relocation. This does not cover zero divisors inside the new C RNG interface, arbitrary exception handlers, game clocks or physical hardware.')
    save(out/'report.json',report);save(ROOT/'verification/native-rng-linked-math-current.json',report)
    print(report['status'],len(rows),len(zero),flush=True)


if __name__=='__main__':main()
