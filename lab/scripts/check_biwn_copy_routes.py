"""Execute the original two-entry copy selector, stopping before either copy path."""
from datetime import datetime,timezone
import json
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import *
import unicorn
import extract_biwn_stage as stage


def main():
    root=stage.ROOT
    session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=(session/'nextstage-68000-candidate.bin').read_bytes();assert stage.digest(image)==stage.STAGE_SHA
    rows=[]
    for entry in [0xe3e0,0xe3ee]:
        for count in [0,1,127,128,129,0x7fffffff,0x80000000,0x8000007f,0x80000080,0xffffffff]:
            cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
            cpu.mem_map(0,0x200000);cpu.mem_write(0x4000,image)
            args=[0x1ffe00,0x110000,0x120000,count]
            cpu.mem_write(0x1ff000,b''.join(x.to_bytes(4,'big') for x in args));cpu.reg_write(UC_M68K_REG_A7,0x1ff000)
            cpu.reg_write(UC_M68K_REG_D0,0xa5a5a5a5)
            trace=[];stops={0xe4a8:'zero_return',0xe4a2:'CPU_byte_copy',0xe408:'device_command_path'}
            def code(engine,address,size,_):
                if address in stops:engine.emu_stop();return
                assert 0xe3e0<=address<0xe408
                trace.append(address)
            cpu.hook_add(UC_HOOK_CODE,code);cpu.emu_start(entry,0,count=32,timeout=1_000_000)
            pc=cpu.reg_read(UC_M68K_REG_PC)
            negative=bool(((count-128)&0xffffffff)&0x80000000)
            expected=0xe4a8 if count==0 else 0xe4a2 if negative else 0xe408
            assert pc==expected
            assert cpu.reg_read(UC_M68K_REG_D0)==0xa5a5a5a5 and cpu.reg_read(UC_M68K_REG_D1)==count
            assert cpu.reg_read(UC_M68K_REG_A7)==0x1ff000
            expected_a0,expected_a1=(args[2],args[1]) if entry==0xe3e0 else (args[1],args[2])
            assert cpu.reg_read(UC_M68K_REG_A0)==expected_a0 and cpu.reg_read(UC_M68K_REG_A1)==expected_a1
            rows.append({'entry':hex(entry),'count':hex(count),'path':stops[pc],
                         'A0':hex(expected_a0),'A1':hex(expected_a1),'stopped_before':hex(pc),
                         'executed_instruction_addresses':[hex(a) for a in trace]})
    report={'time':datetime.now(timezone.utc).isoformat(),'status':'original_copy_entry_and_route_checks_passed',
            'stage_sha256':stage.STAGE_SHA,'CPU_model':'Unicorn '+unicorn.__version__+' M68000',
            'cases':len(rows),'fixtures':rows,
            'original_bytes_e3e0_e408':image[0xe3e0-0x4000:0xe408-0x4000].hex(),
            'facts':{'entries':['0xe3e0','0xe3ee'],'shared_branch':'0xe3fa',
                     'small_path_condition':'count nonzero and bit31 of wrapped(count-128) set',
                     'counterexample':'count0x80000000 reaches device command path; BMI is not a general signed less-than test'},
            'scope':'Stopped before byte-copy, device writes or RTS. Entry argument mapping and branch selection only; no completed copy, blitter behavior or hardware proof.'}
    (root/'verification/biwn-copy-route-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'status':report['status']}))


if __name__=='__main__':main()
