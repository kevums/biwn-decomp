"""Finite native source-API error propagation checks, not original CPU behavior."""
import json,sys,copy,os
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_actor_source_group_v3 as g
from check_biwn_scheduler import Native

def main():
    proof_path=Path(sys.argv[1]);proof=g.read(proof_path);assert proof['status']=='terminal_coupled_target_compiled_actor_source_group_pass'
    payload=Path(proof['binary']).read_bytes();symbols={v[2]:int(v[0],16)for line in (Path(proof['ELF']).parent/'symbols.txt').read_text().splitlines()if len(v:=line.split())==3}
    snapshot=(g.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[];native=Native()
    out=g.ROOT/'verification/native-actor-group-errors'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    vectors=[('unknown_root',0x12345,1,None),('direct_external',0x137e0,17,0x152a2),('nested_external',0x13ae0,17,0x152a2),('direct_inline_dispatch',0x134dc,5,None),('nested_inline_dispatch',0x13ae0,5,None)]
    try:
        for name,entry,want,external in vectors:
            case=copy.deepcopy(next(c for c in g.cases()if c['entry']==(0x13ae0 if entry==0x12345 else entry)));case['entry']=entry
            if entry==0x134dc:case['params']=[4,0,0x1000,0,0x1000,0]
            else:case['params']=[4,0x1000,0,0x1000,0]
            case['initial'] += [[0x4208c+4,1,1 if 'inline'in name else 0],[0x49d6c,2,0],[0x4bd9c,2,0],[0x49c60,2,0],[0x13620,2,0x100],[0x49c18,4,0x84000],[0x84000,2,0]]
            memory=bytearray(g.prior.Script(snapshot,case).memory);memory[g.BASE:g.BASE+len(payload)]=payload;memory[g.EXTERNAL:g.EXTERNAL+2]=b'\x4e\x75'
            argv=b''.join(v.to_bytes(4,'big')for v in case['params']);memory[g.ARGV:g.ARGV+len(argv)]=argv;memory[g.OUTPUT:g.OUTPUT+4]=b'\xa5\x5a\xa5\x5a'
            params=b''.join(v.to_bytes(4,'big')for v in [entry,g.ARGV,case['incoming'][0],g.OUTPUT]);memory[g.SP:g.SP+4+len(params)]=g.STOP.to_bytes(4,'big')+params
            native.device.seed(bytes(memory),0);lib=native.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0);lib.m68k_set_reg(17,0x2000)
            for i,v in enumerate(case['incoming']):lib.m68k_set_reg(i,v)
            lib.m68k_set_reg(15,g.SP);lib.m68k_set_reg(16,symbols['biwn_actor_group_invoke']);services=[]
            for steps in range(100000):
                pc=lib.m68k_get_reg(None,16)
                if pc==g.STOP:break
                if pc==g.EXTERNAL:
                    ram=native.device.ram();sp=lib.m68k_get_reg(None,15)
                    def word(a):return int.from_bytes(ram[a:a+4],'big')
                    target,argv,n,output=[word(sp+i)for i in [4,8,12,16]]
                    assert target==external and external==0x152a2,(name,hex(target))
                    services.append(target);native.device.direct(output,4,0xdeadbeef);lib.m68k_set_reg(0,17)
                else:assert g.BASE<=pc<g.BASE+len(payload),(name,hex(pc))
                lib.m68k_execute(1)
            else:raise AssertionError('Native source error did not return')
            ram=native.device.ram();status=lib.m68k_get_reg(None,0)
            assert status==want and ram[g.OUTPUT:g.OUTPUT+4]==b'\xa5\x5a\xa5\x5a',(name,status)
            assert lib.m68k_get_reg(None,15)==g.SP+4 and ram[g.SP+4:g.SP+4+len(params)]==params
            assert all(lib.m68k_get_reg(None,i)==v for i,v in enumerate(case['incoming'])if i not in [0,1,8,9])
            assert ram[g.BASE:g.BASE+len(payload)]==payload
            if 'inline'in name:assert int.from_bytes(ram[0x49d6c:0x49d6e],'big')==4,'Earlier stores should survive source dispatch error'
            assert services==([external]if external else[])
            rows.append(dict(name=name,root_entry=hex(entry),source_status=status,root_output_unchanged=True,earlier_actor_store_retained='inline'in name,external_services=services,instructions=steps))
        paths=[Path(__file__),proof_path,Path(proof['binary']),Path(proof['ELF']),g.ROOT/'scripts/check_biwn_scheduler.py',g.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']
        record=dict(status='terminal_native_actor_source_API_errors_pass',directory=str(out),cases=rows,source_sha256={str(p):g.sha(p)for p in paths},scope=__doc__,original_error_domain_equivalence=False,new_predictions=0,disc_integrated=False)
        g.save(out/'protocol.json',record);g.save(g.ROOT/'verification/native-actor-group-errors-current.json',record);print(json.dumps(record,indent=2))
    finally:native.close()

if __name__=='__main__':main()
