#include "biwn_gpu4720_submit_cpu.h"
static void bank(struct biwn_task_cpu *s){if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];}
static enum biwn_gpu4720_submit_cpu_status idle(struct biwn_world_bus *bus,struct biwn_task_cpu *s,uint32_t ret,uint32_t *budget)
{
 uint32_t value;s->registers[15]-=4;bank(s);
 if(bus->write32(bus->context,s->registers[15],ret))return BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR;
 do{if(!*budget)return BIWN_GPU4720_SUBMIT_CPU_READ_LIMIT;--*budget;if(bus->read32(bus->context,0xf03200u,&value))return BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR;}while(value);
 if(bus->read32(bus->context,s->registers[15],&value))return BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR;
 if(value!=ret)return BIWN_GPU4720_SUBMIT_CPU_BAD_RETURN;s->registers[15]+=4;bank(s);s->sr=(uint16_t)((s->sr&0xfff0u)|4u);return BIWN_GPU4720_SUBMIT_CPU_OK;
}
enum biwn_gpu4720_submit_cpu_status biwn_gpu4720_submit_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t budget)
{
 struct biwn_task_cpu s;uint32_t value;unsigned i;enum biwn_gpu4720_submit_cpu_status status;
 if(!bus||!state||!bus->read32||!bus->write32||state->pc!=0xe26cu)return BIWN_GPU4720_SUBMIT_CPU_BAD_ARGUMENT;
 s=*state;status=idle(bus,&s,0xe272u,&budget);if(status)return status;
 for(i=0;i<5;i++){if(bus->read32(bus->context,s.registers[15]+4u+i*4u,&value)||bus->write32(bus->context,0xf0320cu+i*4u,value))return BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR;}
 if(bus->write32(bus->context,0xf03204u,0x4720u))return BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR;
 do{if(!budget)return BIWN_GPU4720_SUBMIT_CPU_READ_LIMIT;--budget;if(bus->read32(bus->context,0xf03204u,&value))return BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR;}while(value==0x4720u);
 status=idle(bus,&s,0xe2b6u,&budget);if(status)return status;s.pc=0xe2b6u;*state=s;return BIWN_GPU4720_SUBMIT_CPU_OK;
}
enum biwn_gpu4720_submit_cpu_status biwn_gpu4720_submit_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t budget)
{
 struct biwn_task_cpu s;enum biwn_gpu4720_submit_cpu_status status;if(!state)return BIWN_GPU4720_SUBMIT_CPU_BAD_ARGUMENT;s=*state;
 status=biwn_gpu4720_submit_cpu_body(bus,&s,budget);if(status)return status;if(bus->read32(bus->context,s.registers[15],&s.pc))return BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR;
 s.registers[15]+=4;bank(&s);*state=s;return BIWN_GPU4720_SUBMIT_CPU_OK;
}
