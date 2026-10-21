#include "biwn_actor_direction.h"
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void word(struct biwn_task_cpu *s,unsigned i,uint16_t v){s->registers[i]=(s->registers[i]&0xffff0000u)|v;}
static void byte(struct biwn_task_cpu *s,unsigned i,uint8_t v){s->registers[i]=(s->registers[i]&0xffffff00u)|v;}
static void nz8(struct biwn_task_cpu *s,uint8_t v){s->sr=(uint16_t)((s->sr&0xfff0u)|(v?0:4)|(v&0x80u?8:0));}
static void xflag(struct biwn_task_cpu *s,unsigned x){s->sr=(uint16_t)((s->sr&~0x10u)|(x?0x10u:0));}
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_RNG_CPU_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_RNG_CPU_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_RNG_CPU_BUS_ERROR;}while(0)
#define PUSH(v) do{s.registers[15]-=4;s.usp=s.registers[15];W32(s.registers[15],(v));}while(0)
enum biwn_rng_cpu_status biwn_actor_direction_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu s;uint16_t x,z;uint32_t threshold,value,sp;unsigned index;int i;enum biwn_rng_cpu_status status;
 if(!bus||!state||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->sr&0x2000u||state->pc!=0x13440u)return BIWN_RNG_CPU_BAD_ARGUMENT;
 s=*state;for(i=4;i>=2;i--)PUSH(s.registers[i]);
 R16(s.registers[15]+16u,x);R16(s.registers[15]+18u,z);word(&s,0,x);word(&s,1,z);
 if(x&0x8000u){word(&s,0,(uint16_t)(0u-x));xflag(&s,x!=0);if(z&0x8000u){word(&s,1,(uint16_t)(0u-z));xflag(&s,z!=0);s.registers[3]=2;}else s.registers[3]=1;}
 else if(z&0x8000u){word(&s,1,(uint16_t)(0u-z));xflag(&s,z!=0);s.registers[3]=3;}else s.registers[3]=4;
 if(!(uint16_t)s.registers[1])byte(&s,1,64);
 else{
  s.registers[0]=(uint32_t)(uint16_t)s.registers[0]<<16;s.registers[8]=sx16((uint16_t)s.registers[1]);PUSH(s.registers[8]);PUSH(s.registers[0]);PUSH(0x13486u);sp=s.registers[15];s.pc=0xe588u;
  status=biwn_rng_cpu_body(bus,&s);if(status)return status;if(s.registers[15]!=sp)return BIWN_RNG_CPU_BAD_RETURN;R32(sp,value);if(value!=0x13486u)return BIWN_RNG_CPU_BAD_RETURN;s.registers[15]+=12;s.usp=s.registers[15];
  s.registers[8]=s.registers[0];byte(&s,1,0);word(&s,2,0);s.registers[9]=0x41f00u;
  for(index=0;index<64;index++){
   byte(&s,2,(uint8_t)s.registers[1]);word(&s,0,(uint16_t)s.registers[2]);s.registers[0]=sx16((uint16_t)s.registers[0]);s.registers[0]<<=2;xflag(&s,0);R32(s.registers[9]+s.registers[0],threshold);
   if((s.registers[8]^0x80000000u)<=(threshold^0x80000000u))break;
   byte(&s,1,(uint8_t)(s.registers[1]+1u));xflag(&s,(uint8_t)s.registers[1]==0);
  }
 }
 if(s.registers[3]==2){byte(&s,4,128);xflag(&s,(uint8_t)s.registers[4]<(uint8_t)s.registers[1]);byte(&s,4,(uint8_t)(s.registers[4]-s.registers[1]));byte(&s,1,(uint8_t)s.registers[4]);}
 else if(s.registers[3]==3){xflag(&s,(uint8_t)s.registers[1]>127);byte(&s,1,(uint8_t)(s.registers[1]+128u));}
 else if(s.registers[3]==4){xflag(&s,(uint8_t)s.registers[1]!=0);byte(&s,1,(uint8_t)(0u-(uint8_t)s.registers[1]));}
 word(&s,0,0);byte(&s,0,(uint8_t)s.registers[1]);nz8(&s,(uint8_t)s.registers[0]);
 for(i=2;i<=4;i++){R32(s.registers[15],s.registers[i]);s.registers[15]+=4;}
 s.usp=s.registers[15];s.pc=0x134dau;*state=s;return BIWN_RNG_CPU_OK;
}
enum biwn_rng_cpu_status biwn_actor_direction_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu s;enum biwn_rng_cpu_status status;if(!state)return BIWN_RNG_CPU_BAD_ARGUMENT;s=*state;
 status=biwn_actor_direction_body(bus,&s);if(status)return status;R32(s.registers[15],s.pc);s.registers[15]+=4;s.usp=s.registers[15];*state=s;return BIWN_RNG_CPU_OK;
}
