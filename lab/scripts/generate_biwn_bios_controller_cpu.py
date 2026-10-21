"""Actual user BIOS resident3000 CD/GPU ISR setup, mapped from ROM84A6."""
import hashlib,json
from pathlib import Path
import generate_biwn_entry_setup_cpu as entry
ROOT=entry.ROOT
rename=lambda s:s.replace('biwn_entry_setup_cpu','biwn_bios_controller_cpu').replace('BIWN_ENTRY_SETUP_CPU','BIWN_BIOS_CONTROLLER_CPU')
def main():
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();assert hashlib.sha256(bios).hexdigest()=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b';resident=bios[0x84a6:0x92a6];frozen=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    for a,b in [(0x3048,0x304c),(0x35de,0x3610)]:
        assert resident[a-0x3000:b-0x3000]==frozen[a:b];rows+=entry.loader.base.binary_tools.m68k_instructions(resident[a-0x3000:b-0x3000],a)[0]
    prefix=rename(entry.rename(entry.loader.base.PREFIX)).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    prefix='\n'.join(l for l in prefix.splitlines()if not l.startswith(('static uint32_t sx8(', 'static uint32_t sx16(', 'static int push(', 'static int invoke(', 'static uint32_t alu(', 'static void put(')))+'\n'
    prefix=prefix.replace('struct dispatch s;uint32_t v,u;','struct dispatch s;uint32_t v;')
    header=rename(entry.rename(entry.loader.base.HEADER)).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_BIOS_CONTROLLER_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_bios_controller_cpu_status biwn_bios_controller_cpu_body',a)
    header=header[:a]+'''/* Actual user BIOS entry3048/35DE..3610 controller initialization.
 * ROM84A6..92A6 supplies the resident image at3000; source function
 * writes BUTCH control/DSC/I2S/reset and DSA command7001. Firmware
 * transport/device effects are supplied by the hardware bus.
 * Full CPU/private frame/bothstackbanks; shared hardware bus is supplied.
 * No runtime decoder/originalCPU calls. Boot/firmware relocation, BUTCH
 * transport, other BIOS entries/CDGPUISR execution remain separate. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_bios_controller_cpu.c','biwn_bios_controller_cpu.h'];(src/names[0]).write_text(prefix+'\n'.join(rename(entry.emit(r))for r in rows)+'\n'+rename(entry.rename(entry.loader.base.SUFFIX)));(src/names[1]).write_text(header)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,BIOS_sha256=hashlib.sha256(bios).hexdigest(),ROM_resident_offset='0x84a6',resident_RAM_base='0x3000',resident_bytes=0xe00,resident_sha256=hashlib.sha256(resident).hexdigest(),BIOS_entry='0x3048',BUTCH_register_writes=['0xdfff00','0xdfff04','0xdfff10','0xdfff0a'],source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False);(session/'bios-controller-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
