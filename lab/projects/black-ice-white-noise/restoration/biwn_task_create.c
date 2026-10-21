#include "biwn_task_create.h"
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_CREATE_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(v)))return BIWN_CREATE_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_CREATE_BUS_ERROR;}while(0)
enum biwn_task_create_status biwn_task_create(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu cpu;uint32_t value;
 if(!bus||!state||!bus->read32||!bus->write16||!bus->write32||
    (state->pc!=0xde5cu&&state->pc!=0xdf6cu))return BIWN_CREATE_BAD_ARGUMENT;
 cpu=*state;
 if(cpu.pc==0xdf6cu){R32(cpu.registers[15]+4u,cpu.registers[0]);R32(cpu.registers[15]+8u,cpu.registers[1]);}
 R32(0xc0920u,cpu.registers[8]);R32(0xc0924u,cpu.registers[9]);
 if(!cpu.registers[9])return BIWN_CREATE_NO_FREE;
 R32(cpu.registers[9],value);W32(0xc0924u,value);
 R32(cpu.registers[8],value);W32(cpu.registers[9],value);
 W32(cpu.registers[9]+4u,cpu.registers[8]);W32(cpu.registers[8],cpu.registers[9]);
 R32(cpu.registers[9],cpu.registers[8]);W32(cpu.registers[8]+4u,cpu.registers[9]);
 W32(cpu.registers[9]+8u,cpu.registers[0]);W32(cpu.registers[9]+16u,cpu.registers[0]);
 W32(cpu.registers[9]+30u,cpu.registers[1]);cpu.registers[8]=cpu.registers[9]+0x400u;W32(cpu.registers[9]+12u,cpu.registers[8]);
 W16(cpu.registers[9]+20u,0);W32(cpu.registers[9]+26u,0);W32(cpu.registers[9]+22u,0);W32(cpu.registers[9]+34u,0);
 cpu.registers[0]=cpu.registers[9];
 cpu.sr=(uint16_t)((cpu.sr&0xfff0u)|(cpu.registers[0]>>31?8u:0u));
 R32(cpu.registers[15],cpu.pc);cpu.registers[15]+=4u;
 if(cpu.sr&0x2000u)cpu.ssp=cpu.registers[15];else cpu.usp=cpu.registers[15];
 *state=cpu;return BIWN_CREATE_OK;
}
enum biwn_task_create_status biwn_task_create_logical(struct biwn_world_bus *bus,
 uint32_t callback,uint32_t parameter,uint32_t scratch,uint32_t *out_D0)
{
 struct biwn_task_cpu cpu={0};enum biwn_task_create_status status;
 if(!bus||!out_D0||!scratch||!bus->read32||!bus->write16||!bus->write32)return BIWN_CREATE_BAD_ARGUMENT;
 if(bus->write32(bus->context,scratch,0))return BIWN_CREATE_BUS_ERROR;
 cpu.pc=0xde5cu;cpu.registers[0]=callback;cpu.registers[1]=parameter;
 cpu.registers[15]=scratch;cpu.sr=0x2000u;cpu.ssp=scratch;
 status=biwn_task_create(bus,&cpu);
 if(!status)*out_D0=cpu.registers[0];
 return status;
}
