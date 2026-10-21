#include "biwn_bios_resident_install_cpu.h"
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
