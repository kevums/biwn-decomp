#include "biwn_render_startup.h"
struct startup {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;biwn_render_service service;void *context;};
static void stack_bank(struct biwn_task_cpu *cpu){if(cpu->sr&0x2000u)cpu->ssp=cpu->registers[15];else cpu->usp=cpu->registers[15];}
static void move_flags(struct biwn_task_cpu *cpu,uint32_t v){cpu->sr=(uint16_t)((cpu->sr&0xfff0u)|(v?0u:4u)|(v>>31?8u:0u));}
static enum biwn_startup_status store(struct startup *s,uint32_t a,uint32_t v)
{if(s->bus->write32(s->bus->context,a,v))return BIWN_STARTUP_BUS_ERROR;move_flags(&s->cpu,v);return BIWN_STARTUP_OK;}
static enum biwn_startup_status push(struct startup *s,uint32_t v,int flags)
{
 s->cpu.registers[15]-=4u;stack_bank(&s->cpu);
 if(s->bus->write32(s->bus->context,s->cpu.registers[15],v))return BIWN_STARTUP_BUS_ERROR;
 if(flags)move_flags(&s->cpu,v);return BIWN_STARTUP_OK;
}
static enum biwn_startup_status call(struct startup *s,uint32_t target,uint32_t returned)
{
 enum biwn_startup_status status=push(s,returned,0);uint32_t entry_sp;
 if(status)return status;
 s->cpu.pc=target;entry_sp=s->cpu.registers[15];
 if(target==0xdf6cu){if(biwn_task_create(s->bus,&s->cpu))return BIWN_STARTUP_SERVICE_ERROR;}
 else{
  if(s->service(s->context,s->bus,&s->cpu,target))return BIWN_STARTUP_SERVICE_ERROR;
  if(s->cpu.registers[15]!=entry_sp)return BIWN_STARTUP_BAD_RETURN;
  if(s->bus->read32(s->bus->context,s->cpu.registers[15],&s->cpu.pc))return BIWN_STARTUP_BUS_ERROR;
  s->cpu.registers[15]+=4u;stack_bank(&s->cpu);
 }
 if(s->cpu.pc!=returned)return BIWN_STARTUP_BAD_RETURN;
 return BIWN_STARTUP_OK;
}
#define CHECK(e) do{enum biwn_startup_status code=(e);if(code)return code;}while(0)
enum biwn_startup_status biwn_render_startup(struct biwn_world_bus *bus,struct biwn_task_cpu *state,
 biwn_render_service service,void *context)
{
 struct startup s;unsigned i,j;
 static const uint32_t globals[][2]={{0xbd830u,0x778d0u},{0xbd834u,0x8b3d0u},{0xbd838u,0x9eed0u},
  {0xbd83cu,0x8b3d0u},{0xbd840u,0x9eed0u},{0xbd844u,0x778d0u}};
 static const uint32_t tasks[16]={0x21d1au,0x1a544u,0x17520u,0x12ee0u,0x155e0u,0x14cc0u,0x179c0u,
  0x17380u,0x17640u,0x1a560u,0x1a920u,0xefa0u,0xec20u,0x1b480u,0xf880u,0xf360u};
 static const uint32_t returns[16]={0x17d0eu,0x17d18u,0x17d22u,0x17d30u,0x17d3au,0x17d44u,0x17d4eu,
  0x17d5cu,0x17d66u,0x17d70u,0x17d7au,0x17d88u,0x17d92u,0x17d9cu,0x17da6u,0x17db4u};
 if(!bus||!state||!service||!bus->read32||!bus->write16||!bus->write32||state->pc!=0x17c40u||state->sr&0x2000u)return BIWN_STARTUP_BAD_ARGUMENT;
 s.bus=bus;s.cpu=*state;s.service=service;s.context=context;
 CHECK(push(&s,s.cpu.registers[10],0));CHECK(push(&s,s.cpu.registers[4],0));CHECK(push(&s,s.cpu.registers[3],0));CHECK(push(&s,s.cpu.registers[2],0));
 CHECK(call(&s,0x4088u,0x17c4au));CHECK(call(&s,0x1a6e0u,0x17c50u));
 for(i=0;i<6;i++)CHECK(store(&s,globals[i][0],globals[i][1]));
 CHECK(push(&s,0,1));CHECK(push(&s,0x778d0u,0));CHECK(call(&s,0xe03au,0x17c9au));s.cpu.registers[15]+=8u;stack_bank(&s.cpu);
 CHECK(store(&s,0x49c44u,0x6a960u));CHECK(store(&s,0x43dceu,0x6a960u));
 CHECK(store(&s,0x49c48u,0xb5130u));CHECK(store(&s,0x43df2u,0xb5130u));
 CHECK(push(&s,0x777c0u,0));CHECK(push(&s,0x43da0u,0));CHECK(call(&s,0x185b2u,0x17cd6u));
 /* No cleanup here: the original keeps these8bytes across later calls. */
 CHECK(store(&s,0x778c0u,0x777c0u));
 CHECK(call(&s,0xe2f4u,0x17ce6u));CHECK(call(&s,0x18160u,0x17cecu));
 CHECK(call(&s,0x21242u,0x17cf2u));CHECK(call(&s,0x18ba8u,0x17cf8u));CHECK(call(&s,0xdfc0u,0x17cfeu));
 for(i=0;i<3;i++){
  CHECK(push(&s,0,1));CHECK(push(&s,tasks[i],0));if(!i)s.cpu.registers[10]=0xdf6cu;
  CHECK(call(&s,s.cpu.registers[10],returns[i]));
 }
 s.cpu.registers[15]+=28u;stack_bank(&s.cpu);
 for(j=0;j<3;j++){
  CHECK(store(&s,s.cpu.registers[15],0));
  for(i=3u+j*4u;i<7u+j*4u;i++){
   if(i!=3u+j*4u)CHECK(push(&s,0,1));
   CHECK(push(&s,tasks[i],0));CHECK(call(&s,s.cpu.registers[10],returns[i]));
  }
  s.cpu.registers[15]+=28u;stack_bank(&s.cpu);
 }
 CHECK(store(&s,s.cpu.registers[15],0));CHECK(push(&s,tasks[15],0));CHECK(call(&s,s.cpu.registers[10],returns[15]));
 CHECK(store(&s,0x778ccu,0));CHECK(store(&s,0x4c24cu,0));s.cpu.registers[15]+=8u;stack_bank(&s.cpu);
 s.cpu.pc=0x17dc2u;*state=s.cpu;return BIWN_STARTUP_OK;
}
