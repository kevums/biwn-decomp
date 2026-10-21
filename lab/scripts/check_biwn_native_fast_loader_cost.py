"""Compare real retained-core startup cycles for old and fast resident builds."""
from datetime import datetime,timezone
import json
from pathlib import Path
from check_biwn_native_button_movable import CPU
from check_biwn_native_button_digit import ROOT,sha,save


def main():
    paths=[ROOT/'verification/native-rng-disc-build-current.json',ROOT/'verification/native-fast-rng-disc-build-current.json']
    cpu=CPU();results=[]
    try:
        for p in paths:
            b=json.loads(p.read_text());ram=bytearray(0x200000);ram[0x4000:0x100000]=Path(b['derived_stage']).read_bytes()
            n=cpu.native;l=n.lib;n.device.seed(bytes(ram),0);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x201f)
            for i in range(15):l.m68k_set_reg(i,0x12345678+i)
            l.m68k_set_reg(15,0x180000);l.m68k_set_reg(16,0x4000);cycles=steps=0
            for _ in range(10000):
                pc=l.m68k_get_reg(None,16)
                if pc==0x400a:break
                assert pc==0x4000 or b['staging_address']<=pc<b['staging_address']+b['native_entry_bytes'] or b['resident_address']<=pc<b['resident_address']+b['component_bytes']
                cycles+=l.m68k_execute(1);steps+=1
            else:raise AssertionError('loader no return')
            results.append(dict(build_proof=str(p),build_proof_sha256=sha(p),steps=steps,cycles=cycles,component_bytes=b['component_bytes'],heap_bytes_reserved=b['heap_bytes_reserved'],CPU=[l.m68k_get_reg(None,i)for i in range(18)]))
    finally:cpu.close()
    assert all(results[0][key]==results[1][key]for key in ['steps','cycles','component_bytes','heap_bytes_reserved','CPU'])
    result=dict(status='terminal_old_and_fast_loader_native_cycles_and_CPU_match',recorded_at=datetime.now(timezone.utc).isoformat(),results=results,source_sha256={str(Path(__file__)):sha(__file__)},scope='One direct startup comparison through400A in retained CPU core, alongside96entryCCR/register checks on each image. Same native cycles/instructions/copy size and heap reserve; no complete machine timing or bus contention proof.')
    save(ROOT/'verification/native-fast-loader-cost-current.json',result);print('Startup matched:',results[0]['steps'],'instructions',results[0]['cycles'],'cycles')


if __name__=='__main__':main()
