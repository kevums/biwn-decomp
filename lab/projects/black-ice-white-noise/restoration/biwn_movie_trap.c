#include "biwn_movie_trap.h"
enum biwn_scheduler_status biwn_movie_trap_dispatch(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
    struct biwn_task_cpu cpu;uint32_t vector;enum biwn_scheduler_status status;
    if(!bus||!state||!limit||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->pc!=0xd414u||(state->sr&0xa000u))return BIWN_SCHEDULER_BAD_ARGUMENT;
    cpu=*state;cpu.usp=cpu.registers[15];cpu.registers[15]=cpu.ssp;
    cpu.registers[15]-=4u;
    if(bus->write32(bus->context,cpu.registers[15],0xd416u))return BIWN_SCHEDULER_BUS_ERROR;
    cpu.registers[15]-=2u;
    if(bus->write16(bus->context,cpu.registers[15],cpu.sr))return BIWN_SCHEDULER_BUS_ERROR;
    cpu.ssp=cpu.registers[15];cpu.sr|=0x2000u;
    if(bus->read32(bus->context,0x80u,&vector))return BIWN_SCHEDULER_BUS_ERROR;
    if(vector!=0xde08u)return BIWN_SCHEDULER_BAD_VECTOR;
    cpu.pc=vector;status=biwn_scheduler_dispatch(bus,&cpu,limit);
    if(status)return status;
    *state=cpu;return BIWN_SCHEDULER_OK;
}
