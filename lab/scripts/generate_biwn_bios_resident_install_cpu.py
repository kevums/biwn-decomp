"""Fixed actual ROM80203E..802054 resident-image copy; no whole boot claim."""
import hashlib,json
from pathlib import Path
import generate_biwn_bios_setup_cpu as source
ROOT=source.ROOT
def main():
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();digest=hashlib.sha256(bios).hexdigest();assert digest=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b'
    rows=source.entry.loader.base.binary_tools.m68k_instructions(bios[0x203e:0x2054],0x80203e)[0]
    assert [r['assembly']for r in rows]==['lea.l $8084a6.l, a0','lea.l $3000.w, a1','lea.l $808e90.l, a2','move.l (a0)+, (a1)+','cmpa.l a2, a0','bcs.b $80204e']
    header='''#ifndef BIWN_BIOS_RESIDENT_INSTALL_CPU_H
#define BIWN_BIOS_RESIDENT_INSTALL_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
/* Actual ROM80203E resident-image copy stops before BSR802070 at802054.
 * Copies2540bytes ROM8084A6..808E92 intoRAM3000..39EC: long copy
 * overshoots nominal ROM end808E90 by2bytes. InitialROM/RAM/CPU/bus
 * supplied; preceding/following firmware, initial game-load and clocks
 * remain separate. No decoder or original CPU execution. */
enum biwn_bios_resident_install_status { BIWN_BIOS_RESIDENT_INSTALL_OK=0,
 BIWN_BIOS_RESIDENT_INSTALL_BAD_ARGUMENT=1,BIWN_BIOS_RESIDENT_INSTALL_BUS_ERROR=2,
 BIWN_BIOS_RESIDENT_INSTALL_WORK_LIMIT=4,BIWN_BIOS_RESIDENT_INSTALL_BAD_PC=7 };
enum biwn_bios_resident_install_status biwn_bios_resident_install_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
'''
    code='''#include "biwn_bios_resident_install_cpu.h"
enum biwn_bios_resident_install_status biwn_bios_resident_install_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_input_write8 w8,biwn_world_cpu_service service,void *context,uint32_t budget,int stop_flag){
 struct biwn_task_cpu s;uint32_t v,u,r; (void)w8;(void)service;(void)context;
 if(!bus||!state||!budget||!bus->read32||!bus->write32||stop_flag)return 1;
 s=*state;while(budget--){switch(s.pc){
 case 0x80203eu: s.registers[8]=0x8084a6u;s.pc=0x802044u;break;
 case 0x802044u: s.registers[9]=0x3000u;s.pc=0x802048u;break;
 case 0x802048u: s.registers[10]=0x808e90u;s.pc=0x80204eu;break;
 case 0x80204eu:
  if(bus->read32(bus->context,s.registers[8],&v))return 2;s.registers[8]+=4u;
  if(bus->write32(bus->context,s.registers[9],v))return 2;s.registers[9]+=4u;
  s.sr=(uint16_t)((s.sr&0xfff0u)|(v?0u:4u)|(v&0x80000000u?8u:0u));s.pc=0x802050u;break;
 case 0x802050u:
  u=s.registers[8];v=s.registers[10];r=u-v;
  s.sr=(uint16_t)((s.sr&0xfff0u)|(r?0u:4u)|(r&0x80000000u?8u:0u)|(((u^v)&(u^r)&0x80000000u)?2u:0u)|(u<v?1u:0u));s.pc=0x802052u;break;
 case 0x802052u:s.pc=(s.sr&1u)?0x80204eu:0x802054u;break;
 default:return 7;
 }if(s.pc==0x802054u){*state=s;return 0;}}
 return 4;
}
'''
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_bios_resident_install_cpu.c','biwn_bios_resident_install_cpu.h']
    (src/names[0]).write_text(code);(src/names[1]).write_text(header)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,BIOS_sha256=digest,source_ROM_range=['0x80203e','0x802054'],copy_ROM_interval=['0x8084a6','0x808e92'],copy_RAM_interval=['0x3000','0x39ec'],bytes_copied=2540,nominal_end_overshoot_bytes=2,source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False)
    (session/'bios-resident-install-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
