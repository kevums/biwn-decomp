#include "biwn_movie_VBI_event.h"
int biwn_movie_VBI_event(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu s;uint32_t vector;
 if(!bus||!state||!bus->read32||!bus->write16||!bus->write32||state->pc!=0xd4a8u||!(state->sr&0x2000u))return 1;
 s=*state;if((s.sr&0x0700u)>=0x0200u)return 0;
 s.registers[15]-=4u;if(bus->write32(bus->context,s.registers[15],s.pc))return 2;
 s.registers[15]-=2u;if(bus->write16(bus->context,s.registers[15],s.sr))return 2;
 s.ssp=s.registers[15];s.sr=(uint16_t)((s.sr&~0x8700u)|0x2200u);
 if(bus->read32(bus->context,0x100u,&vector))return 2;if(vector!=0xe7d4u)return 7;
 s.pc=vector;*state=s;return 0;
}
