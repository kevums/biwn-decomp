#include "biwn_scheduler.h"
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_SCHEDULER_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_SCHEDULER_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_SCHEDULER_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_SCHEDULER_BUS_ERROR;}while(0)
static void normalize_stack(struct biwn_task_cpu *cpu)
{if(cpu->sr&0x2000u)cpu->ssp=cpu->registers[15];else cpu->usp=cpu->registers[15];}
static enum biwn_scheduler_status select_next(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit)
{
    uint32_t value,clock,pc;uint16_t sr;
    for(;;){
        if(!limit--)return BIWN_SCHEDULER_SCAN_LIMIT;
        R32(cpu->registers[8],cpu->registers[8]);
        R32(cpu->registers[8]+26u,value);if(value)continue;
        R32(cpu->registers[8]+34u,value);if(value)continue;
        R32(cpu->registers[8]+22u,value);
        if(value){R32(cpu->registers[8]+22u,cpu->registers[0]);R32(0x778ccu,clock);if(cpu->registers[0]>clock)continue;W32(cpu->registers[8]+22u,0);}
        break;
    }
    W32(0xc0920u,cpu->registers[8]);
    R32(cpu->registers[8]+16u,pc);cpu->registers[15]-=4u;W32(cpu->registers[15],pc);
    R16(cpu->registers[8]+20u,sr);cpu->registers[15]-=2u;W16(cpu->registers[15],sr);
    R32(cpu->registers[8]+12u,cpu->registers[9]);cpu->usp=cpu->registers[9];
    /* M68000 RTE: pop SR+PC from supervisor stack, then select A7 bank. */
    R16(cpu->registers[15],sr);cpu->registers[15]+=2u;
    R32(cpu->registers[15],pc);cpu->registers[15]+=4u;cpu->ssp=cpu->registers[15];
    cpu->sr=sr;cpu->pc=pc;if(!(sr&0x2000u))cpu->registers[15]=cpu->usp;
    return BIWN_SCHEDULER_OK;
}
static enum biwn_scheduler_status dispatch(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit)
{
    uint32_t pc;uint16_t sr;
    R32(0xc0920u,cpu->registers[8]);cpu->registers[9]=cpu->usp;
    W32(cpu->registers[8]+12u,cpu->registers[9]);
    R16(cpu->registers[15],sr);cpu->registers[15]+=2u;W16(cpu->registers[8]+20u,sr);
    R32(cpu->registers[15],pc);cpu->registers[15]+=4u;W32(cpu->registers[8]+16u,pc);
    return select_next(bus,cpu,limit);
}
static enum biwn_scheduler_status resume_yield(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu)
{
    int i;
    if(cpu->pc==0xdf66u||cpu->pc==0xdf96u){
        for(i=2;i<=14;++i){if(i==8||i==9)continue;R32(cpu->registers[15],cpu->registers[i]);cpu->registers[15]+=4u;}
        R32(cpu->registers[15],cpu->pc);cpu->registers[15]+=4u;
    }
    normalize_stack(cpu);return BIWN_SCHEDULER_OK;
}
static enum biwn_scheduler_status remove_current(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit)
{
    uint32_t free_head;
    R32(0xc0920u,cpu->registers[8]);
    R32(cpu->registers[8],cpu->registers[9]);
    R32(0xc0924u,free_head);W32(cpu->registers[8],free_head);
    W32(0xc0924u,cpu->registers[8]);
    R32(cpu->registers[8]+4u,cpu->registers[8]);
    W32(cpu->registers[9]+4u,cpu->registers[8]);
    W32(cpu->registers[8],cpu->registers[9]);
    /* DEB6 discards its own exception frame; it never saves the dead task. */
    cpu->registers[15]+=6u;
    return select_next(bus,cpu,limit);
}
static int valid(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t limit)
{return bus&&cpu&&limit&&bus->read16&&bus->read32&&bus->write16&&bus->write32;}
enum biwn_scheduler_status biwn_scheduler_resume_saved(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
    struct biwn_task_cpu cpu;enum biwn_scheduler_status status;
    if(!bus||!state||!bus->read32)return BIWN_SCHEDULER_BAD_ARGUMENT;
    cpu=*state;status=resume_yield(bus,&cpu);if(!status)*state=cpu;return status;
}
enum biwn_scheduler_status biwn_scheduler_dispatch(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
    struct biwn_task_cpu cpu;enum biwn_scheduler_status status;
    if(!valid(bus,state,limit)||!(state->sr&0x2000u))return BIWN_SCHEDULER_BAD_ARGUMENT;
    cpu=*state;status=dispatch(bus,&cpu,limit);if(!status)*state=cpu;return status;
}
enum biwn_scheduler_status biwn_scheduler_yield(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
    struct biwn_task_cpu cpu;enum biwn_scheduler_status status;uint32_t vector;int i;
    if(!valid(bus,state,limit)||(state->sr&0x2000u))return BIWN_SCHEDULER_BAD_ARGUMENT;
    cpu=*state;
    /* Original MOVEM predecrement saves D2-D7/A2-A6 in reverse order. */
    for(i=14;i>=2;--i){if(i==9||i==8)continue;cpu.registers[15]-=4u;W32(cpu.registers[15],cpu.registers[i]);}
    cpu.usp=cpu.registers[15];cpu.registers[15]=cpu.ssp;
    cpu.registers[15]-=4u;W32(cpu.registers[15],0xdf66u);
    cpu.registers[15]-=2u;W16(cpu.registers[15],cpu.sr);cpu.sr|=0x2000u;
    R32(0x80u,vector);if(vector!=0xde08u)return BIWN_SCHEDULER_BAD_VECTOR;
    status=dispatch(bus,&cpu,limit);if(status)return status;
    /* A fresh task can enter elsewhere. Host continuation dispatch must
     * honor that selected PC, rather than returning to the yielding task. */
    status=resume_yield(bus,&cpu);if(status)return status;
    *state=cpu;return BIWN_SCHEDULER_OK;
}
enum biwn_scheduler_status biwn_scheduler_remove_dispatch(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
    struct biwn_task_cpu cpu;enum biwn_scheduler_status status;
    if(!valid(bus,state,limit)||!(state->sr&0x2000u)||state->pc!=0xdeb6u)return BIWN_SCHEDULER_BAD_ARGUMENT;
    cpu=*state;status=remove_current(bus,&cpu,limit);if(!status)*state=cpu;return status;
}
enum biwn_scheduler_status biwn_scheduler_remove(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
    struct biwn_task_cpu cpu;enum biwn_scheduler_status status;uint32_t vector;
    if(!valid(bus,state,limit)||(state->sr&0x2000u)||state->pc!=0xdf7au)return BIWN_SCHEDULER_BAD_ARGUMENT;
    cpu=*state;cpu.usp=cpu.registers[15];cpu.registers[15]=cpu.ssp;
    cpu.registers[15]-=4u;W32(cpu.registers[15],0xdf7cu);
    cpu.registers[15]-=2u;W16(cpu.registers[15],cpu.sr);cpu.sr|=0x2000u;
    R32(0x88u,vector);if(vector!=0xdeb6u)return BIWN_SCHEDULER_BAD_VECTOR;
    status=remove_current(bus,&cpu,limit);if(status)return status;
    status=resume_yield(bus,&cpu);if(status)return status;
    *state=cpu;return BIWN_SCHEDULER_OK;
}
