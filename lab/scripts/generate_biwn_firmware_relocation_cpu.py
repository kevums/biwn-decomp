"""Fixed ROM bootstrap relocation through its real JMP to RAM500D6.

No authentication, DSP boot-loader execution, or game dispatch claim.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_entry_setup_cpu as entry

ROOT=entry.ROOT
rename=lambda s:s.replace('biwn_entry_setup_cpu','biwn_firmware_relocation_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_FIRMWARE_RELOCATION_CPU')

def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly']
    if asm=='bsr.w $802070':
        return f'case {hex(pc)}u: CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc=0x802070u;break;'
    if asm=='rts':
        return f'case {hex(pc)}u: CHECK(read_value(&s,s.cpu.registers[15],4,&v));pop(&s,4);s.cpu.pc=v;break;'
    return rename(entry.emit(row))

def main():
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes()
    digest=hashlib.sha256(bios).hexdigest()
    assert digest=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b'
    rows=entry.loader.base.binary_tools.m68k_instructions(bios[0x2000:0x20b6],0x802000)[0]
    assert rows[-1]['assembly']=='rts'
    prefix=rename(entry.rename(entry.loader.base.PREFIX)).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('switch(s.cpu.pc){','if(s.cpu.pc==0x500d6u){*state=s.cpu;return BIWN_FIRMWARE_RELOCATION_CPU_READY;}switch(s.cpu.pc){')
    prefix=prefix.replace('s.bus=bus;', '(void)full_call;s.bus=bus;')
    # These instructions do not invoke services or use shift/sign-extension helpers.
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a)
    prefix=prefix[:a]+prefix[b:]
    prefix='\n'.join(line for line in prefix.splitlines() if not line.startswith(('static uint32_t sx16(', 'static int invoke(')))+'\n'
    header=rename(entry.rename(entry.loader.base.HEADER)).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_FIRMWARE_RELOCATION_CPU_H').replace('BIWN_FIRMWARE_RELOCATION_CPU_BAD_PC=7','BIWN_FIRMWARE_RELOCATION_CPU_BAD_PC=7,BIWN_FIRMWARE_RELOCATION_CPU_READY=8')
    a=header.index('/* Static');b=header.index('enum biwn_firmware_relocation_cpu_status biwn_firmware_relocation_cpu_body',a)
    header=header[:a]+'''/* UserROM802000..8020B6 bootstrap: source stack setup, display/main/
 * resident copies, real BSR/RTS802070, four table-selected resource copies,
 * source patch at196446 and natural JMP500D6. READY8 stops before relocated
 * main's first instruction. Initial ROM/CPU/bus/device state supplied.
 * No runtime decoder/original CPU execution. Firmware authentication,
 * initial game-stub delivery, DSP execution and global clocks separate. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration'
    names=['biwn_firmware_relocation_cpu.c','biwn_firmware_relocation_cpu.h']
    (src/names[0]).write_text(prefix+'\n'.join(emit(row)for row in rows)+'\n'+rename(entry.rename(entry.loader.base.SUFFIX)))
    (src/names[1]).write_text(header)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,BIOS_sha256=digest,stop_PC='0x500d6',table_data_ROM_interval=['0x8020b6','0x8020d6'],table_data_not_decoded_as_code=True,source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),full_firmware_boot_verified=False,whole_game_complete=False,implementation_authorship='coordinator')
    (session/'firmware-relocation-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))

if __name__=='__main__':main()
