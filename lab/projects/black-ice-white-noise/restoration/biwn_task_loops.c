#include "biwn_task_loops.h"
enum biwn_task_loop_status biwn_task_loop_step(struct biwn_world_bus *bus,struct biwn_task_cpu *state,
    biwn_task_world_body world_body,void *context,uint32_t scan_limit)
{
    struct biwn_task_cpu cpu;uint32_t target;enum biwn_scheduler_status status;int body_status;
    if(!bus||!state||!scan_limit||!bus->read32||!bus->write32||!bus->read16||!bus->write16||state->sr&0x2000u)
        return BIWN_TASK_LOOP_BAD_ARGUMENT;
    cpu=*state;
    switch(cpu.pc){
    case 0x1a544u:
        if(!world_body)return BIWN_TASK_LOOP_BAD_ARGUMENT;
        cpu.registers[15]-=4u;
        if(bus->write32(bus->context,cpu.registers[15],0x1a54au))return BIWN_TASK_LOOP_BUS_ERROR;
        cpu.pc=0x1a188u;cpu.usp=cpu.registers[15];
        goto execute_world;
    case 0x1a26cu:
        if(!world_body)return BIWN_TASK_LOOP_BAD_ARGUMENT;
execute_world:
        body_status=world_body(context,bus,&cpu);
        if(body_status==6){
            if(cpu.pc!=0xdf60u)return BIWN_TASK_LOOP_BODY_ERROR;
            status=biwn_scheduler_yield(bus,&cpu,scan_limit);
            if(status)return BIWN_TASK_LOOP_SCHEDULER_ERROR;
            break;
        }
        if(body_status)return BIWN_TASK_LOOP_BODY_ERROR;
        if(bus->read32(bus->context,cpu.registers[15],&cpu.pc))return BIWN_TASK_LOOP_BUS_ERROR;
        cpu.registers[15]+=4u;break;
    case 0x1a54au:case 0xf360u:case 0xf880u:
        target=cpu.pc+6u;cpu.registers[15]-=4u;
        if(bus->write32(bus->context,cpu.registers[15],target))return BIWN_TASK_LOOP_BUS_ERROR;
        cpu.pc=0xdf60u;cpu.usp=cpu.registers[15];
        status=biwn_scheduler_yield(bus,&cpu,scan_limit);
        if(status)return BIWN_TASK_LOOP_SCHEDULER_ERROR;
        break;
    case 0x1a550u:cpu.pc=0x1a544u;break;
    case 0xf366u:cpu.pc=0xf360u;break;
    case 0xf886u:cpu.pc=0xf880u;break;
    default:return BIWN_TASK_LOOP_UNSUPPORTED_PC;
    }
    cpu.usp=cpu.registers[15];*state=cpu;return BIWN_TASK_LOOP_OK;
}
