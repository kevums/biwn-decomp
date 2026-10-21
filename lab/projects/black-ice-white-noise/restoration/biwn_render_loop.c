#include "biwn_render_loop.h"
static void move_flags(struct biwn_task_cpu *cpu,uint32_t value)
{cpu->sr=(uint16_t)((cpu->sr&0xfff0u)|(value==0?4u:0u)|(value>>31?8u:0u));}
static uint32_t subtract(struct biwn_task_cpu *cpu,uint32_t a,uint32_t b)
{
 uint32_t value=a-b;unsigned carry=a<b,overflow=((a^b)&(a^value))>>31;
 cpu->sr=(uint16_t)((cpu->sr&0xffe0u)|(carry?17u:0u)|(overflow?2u:0u)|(value==0?4u:0u)|(value>>31?8u:0u));return value;
}
enum biwn_render_loop_status biwn_render_loop_step(struct biwn_world_bus *bus,struct biwn_task_cpu *state,
 biwn_render_service service,void *context,uint32_t scan_limit)
{
 struct biwn_task_cpu cpu;uint32_t target=0,returned=0,clock;enum biwn_scheduler_status status;
 if(!bus||!state||!scan_limit||!bus->read32||!bus->write32||!bus->read16||!bus->write16||state->sr&0x2000u)return BIWN_RENDER_LOOP_BAD_ARGUMENT;
 cpu=*state;
 switch(cpu.pc){
 case 0x17dc2u:
  if(bus->read32(bus->context,0x778ccu,&clock))return BIWN_RENDER_LOOP_BUS_ERROR;
  cpu.registers[2]=clock;move_flags(&cpu,clock);target=0xdf60u;returned=0x17dceu;break;
 case 0x17dceu:target=0xea28u;returned=0x17dd4u;break;
 case 0x17dd4u:case 0x17de0u:
  if(bus->read32(bus->context,0x778ccu,&clock))return BIWN_RENDER_LOOP_BUS_ERROR;
  cpu.registers[cpu.pc==0x17dd4u?3:4]=clock;move_flags(&cpu,clock);
  target=cpu.pc==0x17dd4u?0x17e0eu:0x181f8u;returned=cpu.pc==0x17dd4u?0x17de0u:0x17decu;break;
 case 0x17decu:
  if(bus->read32(bus->context,0x778ccu,&clock))return BIWN_RENDER_LOOP_BUS_ERROR;
  cpu.registers[1]=clock;move_flags(&cpu,clock);cpu.registers[1]=subtract(&cpu,cpu.registers[1],cpu.registers[2]);
  if(bus->write32(bus->context,0x4c250u,cpu.registers[1]))return BIWN_RENDER_LOOP_BUS_ERROR;
  move_flags(&cpu,cpu.registers[1]);cpu.registers[1]=cpu.registers[3];move_flags(&cpu,cpu.registers[1]);
  cpu.registers[1]=subtract(&cpu,cpu.registers[1],cpu.registers[2]);
  if(bus->write32(bus->context,0x4c254u,cpu.registers[1]))return BIWN_RENDER_LOOP_BUS_ERROR;
  move_flags(&cpu,cpu.registers[1]);cpu.registers[4]=subtract(&cpu,cpu.registers[4],cpu.registers[3]);
  if(bus->write32(bus->context,0x4c258u,cpu.registers[4]))return BIWN_RENDER_LOOP_BUS_ERROR;
  move_flags(&cpu,cpu.registers[4]);cpu.pc=0x17dc2u;cpu.usp=cpu.registers[15];*state=cpu;return BIWN_RENDER_LOOP_OK;
 default:return BIWN_RENDER_LOOP_UNSUPPORTED_PC;
 }
 if(target!=0xdf60u&&!service)return BIWN_RENDER_LOOP_BAD_ARGUMENT;
 cpu.registers[15]-=4u;cpu.usp=cpu.registers[15];
 if(bus->write32(bus->context,cpu.registers[15],returned))return BIWN_RENDER_LOOP_BUS_ERROR;
 cpu.pc=target;
 if(target==0xdf60u){
  status=biwn_scheduler_yield(bus,&cpu,scan_limit);if(status)return BIWN_RENDER_LOOP_SCHEDULER_ERROR;
 }else{
  if(service(context,bus,&cpu,target))return BIWN_RENDER_LOOP_SERVICE_ERROR;
  if(bus->read32(bus->context,cpu.registers[15],&cpu.pc))return BIWN_RENDER_LOOP_BUS_ERROR;
  cpu.registers[15]+=4u;cpu.usp=cpu.registers[15];
 }
 *state=cpu;return BIWN_RENDER_LOOP_OK;
}
