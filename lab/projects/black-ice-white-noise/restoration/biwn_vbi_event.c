#include "biwn_vbi_event.h"
int biwn_vbi_event(struct biwn_world_bus *bus,struct biwn_task_cpu *state){
 struct biwn_task_cpu s;uint32_t vector;uint16_t old;
 if(!bus||!state||!bus->read32||!bus->write16||!bus->write32)return 1;
 if((state->sr&0x0700u)>=0x0200u)return 3;
 s=*state;old=s.sr;
 if(s.sr&0x2000u)s.ssp=s.registers[15];else s.usp=s.registers[15];
 s.registers[15]=s.ssp;s.sr=(uint16_t)((old&~0x8700u)|0x2200u);
 s.registers[15]-=4u;if(bus->write32(bus->context,s.registers[15],s.pc))return 2;
 s.registers[15]-=2u;if(bus->write16(bus->context,s.registers[15],old))return 2;
 s.ssp=s.registers[15];if(bus->read32(bus->context,0x100u,&vector))return 2;
 if(vector!=0xe7d4u)return 1;s.pc=vector;*state=s;return 0;
}
