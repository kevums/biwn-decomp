#include "biwn_input_poll_cpu.h"
static uint32_t ror(uint32_t v,unsigned n){return(v>>n)|(v<<(32u-n));}
static uint32_t rol(uint32_t v,unsigned n){return(v<<n)|(v>>(32u-n));}
static void bank(struct biwn_task_cpu *cpu){if(cpu->sr&0x2000u)cpu->ssp=cpu->registers[15];else cpu->usp=cpu->registers[15];}
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_POLL_CPU_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_POLL_CPU_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_POLL_CPU_BUS_ERROR;}while(0)
enum biwn_input_poll_cpu_status biwn_input_poll_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu cpu;unsigned i;
 if(!bus||!state||!bus->read32||!bus->write16||!bus->write32||state->pc!=0xe4c0u)return BIWN_POLL_CPU_BAD_ARGUMENT;
 cpu=*state;
 for(i=3;i-->0;){cpu.registers[15]-=4;bank(&cpu);W32(cpu.registers[15],cpu.registers[i]);}
 cpu.registers[1]=0xf0fffffcu;cpu.registers[2]=0xffffffffu;
 W16(0xf14000u,0x810eu);R32(0xf14000u,cpu.registers[0]);cpu.registers[0]=ror(cpu.registers[0]|cpu.registers[1],4);cpu.registers[2]&=cpu.registers[0];
 W16(0xf14000u,0x810du);R32(0xf14000u,cpu.registers[0]);cpu.registers[0]=ror(cpu.registers[0]|cpu.registers[1],8);cpu.registers[2]&=cpu.registers[0];
 W16(0xf14000u,0x810bu);R32(0xf14000u,cpu.registers[0]);cpu.registers[0]=rol(rol(cpu.registers[0]|cpu.registers[1],6),6);cpu.registers[2]&=cpu.registers[0];
 W16(0xf14000u,0x8107u);R32(0xf14000u,cpu.registers[0]);cpu.registers[0]=rol(cpu.registers[0]|cpu.registers[1],8);cpu.registers[2]&=cpu.registers[0];cpu.registers[2]=~cpu.registers[2];
 R32(0x49ba4u,cpu.registers[0]);W32(0x49ba4u,cpu.registers[2]);cpu.registers[0]=(cpu.registers[0]^cpu.registers[2])&cpu.registers[2];W32(0x49bacu,cpu.registers[0]);
 cpu.sr=(uint16_t)((cpu.sr&0xfff0u)|(cpu.registers[0]?0:4)|(cpu.registers[0]&0x80000000u?8:0));
 for(i=0;i<3;i++){R32(cpu.registers[15],cpu.registers[i]);cpu.registers[15]+=4;bank(&cpu);}cpu.pc=0xe53au;*state=cpu;return BIWN_POLL_CPU_OK;
}
enum biwn_input_poll_cpu_status biwn_input_poll_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{struct biwn_task_cpu cpu;enum biwn_input_poll_cpu_status status;uint32_t pc;if(!state)return BIWN_POLL_CPU_BAD_ARGUMENT;cpu=*state;status=biwn_input_poll_cpu_body(bus,&cpu);if(status)return status;R32(cpu.registers[15],pc);cpu.pc=pc;cpu.registers[15]+=4;bank(&cpu);*state=cpu;return BIWN_POLL_CPU_OK;}
