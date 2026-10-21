"""Reproduce direct SR read committing stale deferred flags; no game-code changes."""
import json
from pathlib import Path
import unicorn
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for early_read in [False,True]:
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000)
 cpu.mem_write(0xe098,bytes.fromhex('0cb90000000000f0320066f44e75'));cpu.mem_write(0xf03200,b'\0'*4);cpu.mem_write(0x1ff000,(0x1ffe00).to_bytes(4,'big'))
 cpu.reg_write(UC_M68K_REG_SR,7);cpu.reg_write(UC_M68K_REG_A7,0x1ff000);cpu.emu_start(0xe098,0x1ffe00,count=3)
 direct=cpu.reg_read(UC_M68K_REG_SR)if early_read else None
 cpu.mem_write(0x1ffe00,bytes.fromhex('40c7'));cpu.emu_start(0x1ffe00,0x1ffe02,count=1)
 rows.append({'direct_SR_read_before_probe':early_read,'direct_SR':direct,'materialized_SR_in_D7':cpu.reg_read(UC_M68K_REG_D7)})
assert rows[0]['materialized_SR_in_D7']==4 and rows[1]['direct_SR']==5 and rows[1]['materialized_SR_in_D7']==5
report={'unicorn_version':unicorn.__version__,'original_instruction_bytes':'0cb90000000000f0320066f44e75','probe_bytes':'40c7','rows':rows,
        'observation':'CMP.L0 against zero should clear C. Direct SR read returns staleC=1 here and commits it; a later MOVE.WSR,D7 cannot repair that read. Avoid any directSRread before the materialization probe.',
        'scope':'Specific reproducible API observation in this installed M68000 emulator; no claim about all instructions or other versions. Original game code and restored submit code remain unchanged.'}
(ROOT/'verification/unicorn-SR-read-side-effect.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
