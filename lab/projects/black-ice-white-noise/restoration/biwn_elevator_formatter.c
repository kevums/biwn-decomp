#include "biwn_elevator_formatter.h"
struct formatting {biwn_input_write8 write8;};
static int service(void *opaque,struct biwn_world_bus *bus,
 struct biwn_task_cpu *cpu,uint32_t target)
{
 struct formatting *ctx=opaque;
 switch(target){
 case 0x1b160u:case 0x1b1a8u:case 0x1b212u:case 0x1b29cu:
 case 0x1b45au:case 0xe61cu:case 0xe67cu:
  return biwn_formatter_cpu_body(bus,cpu,ctx->write8,service,ctx,20000u,0);
 default:return BIWN_FORMATTER_CPU_SERVICE_ERROR;
 }
}
int biwn_elevator_format(struct biwn_world_bus *bus,biwn_input_write8 write8,
 uint32_t scratch,uint32_t format,uint16_t word,uint32_t *out_D0)
{
 struct biwn_task_cpu cpu={0};struct formatting ctx={write8};int status;
 uint32_t stack=scratch-20u;
 if(!bus||!write8||!out_D0||scratch<20u||format!=0x190b8u||
    !bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32)
  return BIWN_FORMATTER_CPU_BAD_ARGUMENT;
 if(bus->write32(bus->context,stack,0x19186u)||
    bus->write32(bus->context,stack+4u,scratch)||
    bus->write32(bus->context,stack+8u,format)||
    bus->write16(bus->context,stack+12u,word))return BIWN_FORMATTER_CPU_BUS_ERROR;
 cpu.registers[0]=word;cpu.registers[10]=scratch;cpu.registers[15]=stack;
 cpu.pc=0x1b45au;cpu.usp=stack;
 status=biwn_formatter_cpu_call(bus,&cpu,write8,service,&ctx,20000u,0);
 if(status)return status;
 if(cpu.pc!=0x19186u||cpu.registers[15]!=stack+4u)return BIWN_FORMATTER_CPU_BAD_RETURN;
 *out_D0=cpu.registers[0];return 0;
}
