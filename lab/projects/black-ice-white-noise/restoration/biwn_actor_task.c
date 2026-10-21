#include "biwn_actor_task.h"
struct task{struct biwn_world_bus *bus;struct biwn_task_cpu cpu;biwn_actor_task_service service;void *context;uint32_t budget;};
#define R8(a,v) do{if(s.bus->read8(s.bus->context,(a),&(v)))return BIWN_ACTOR_TASK_BUS_ERROR;}while(0)
#define R16(a,v) do{if(s.bus->read16(s.bus->context,(a),&(v)))return BIWN_ACTOR_TASK_BUS_ERROR;}while(0)
#define R32(a,v) do{if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_ACTOR_TASK_BUS_ERROR;}while(0)
#define W8(a,v) do{if(write8(s.bus->context,(a),(v)))return BIWN_ACTOR_TASK_BUS_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint16_t sx8w(uint8_t v){return(uint16_t)((uint16_t)(v&0x7fu)-(uint16_t)(v&0x80u));}
static int less32(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}
static void flags(struct task *s,uint32_t value,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);value&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(value?0:4)|(value&sign?8:0));}
static void regword(struct task *s,unsigned i,uint16_t v){s->cpu.registers[i]=(s->cpu.registers[i]&0xffff0000u)|v;}
static void regbyte(struct task *s,unsigned i,uint8_t v){s->cpu.registers[i]=(s->cpu.registers[i]&0xffffff00u)|v;}
static void bank(struct task *s){s->cpu.usp=s->cpu.registers[15];}
static int push(struct task *s,uint32_t v,unsigned width,int moved){s->cpu.registers[15]-=width;bank(s);if(width==2){if(s->bus->write16(s->bus->context,s->cpu.registers[15],(uint16_t)v))return 2;}else if(s->bus->write32(s->bus->context,s->cpu.registers[15],v))return 2;if(moved)flags(s,v,width*8);return 0;}
static int call(struct task *s,uint32_t target,uint32_t ret){uint32_t sp;int status=push(s,ret,4,0);if(status)return status;s->cpu.pc=target;sp=s->cpu.registers[15];
 if(target==0xdfa6u){if(s->bus->read32(s->bus->context,0xc0920u,&s->cpu.registers[8])||s->bus->read32(s->bus->context,s->cpu.registers[8]+30u,&s->cpu.registers[0]))return 2;flags(s,s->cpu.registers[0],32);}
 else if(s->service(s->context,s->bus,&s->cpu,target))return 3;
 if(s->cpu.registers[15]!=sp)return 5;if(s->bus->read32(s->bus->context,sp,&s->cpu.pc))return 2;s->cpu.registers[15]+=4;bank(s);return s->cpu.pc==ret?0:5;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_actor_task_status)status;}while(0)
#define W16(a,v) do{if(s.bus->write16(s.bus->context,(a),(uint16_t)(v)))return BIWN_ACTOR_TASK_BUS_ERROR;}while(0)
#define W32(a,v) do{if(s.bus->write32(s.bus->context,(a),(v)))return BIWN_ACTOR_TASK_BUS_ERROR;}while(0)
#define WORK() do{if(!s.budget)return BIWN_ACTOR_TASK_WORK_LIMIT;--s.budget;}while(0)
#define POP(n) do{s.cpu.registers[15]+=(n);bank(&s);}while(0)
enum biwn_actor_task_status biwn_actor_task_run(struct biwn_world_bus *bus,
 struct biwn_task_cpu *state,biwn_actor_task_write8 write8,biwn_actor_task_service service,void *context,uint32_t budget)
{
 struct task s;uint32_t object,value,speed,d0,diff;uint16_t w;uint8_t b,c;int i;
 if(!bus||!state||!write8||!service||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->sr&0x2000u||(state->pc!=0xf4d8u&&state->pc!=0xf56eu&&state->pc!=0xf70cu))return BIWN_ACTOR_TASK_BAD_ARGUMENT;
 s.bus=bus;s.cpu=*state;s.service=service;s.context=context;s.budget=budget;
 if(s.cpu.pc==0xf70cu){POP(8);s.cpu.pc=0xf56eu;}
 if(s.cpu.pc==0xf4d8u){
  for(i=13;i>=2;i--)if(i<=7||i>=10)CHECK(push(&s,s.cpu.registers[i],4,0));
  regword(&s,6,0);flags(&s,0,16);CHECK(call(&s,0xdfa6u,0xf4e4u));s.cpu.registers[7]=s.cpu.registers[0];value=s.cpu.registers[0]*103u;s.cpu.registers[0]=value*2u;s.cpu.sr=(uint16_t)((s.cpu.sr&~0x10u)|((value>>31)?0x10u:0));s.cpu.registers[10]=0x49d6cu+s.cpu.registers[0];object=s.cpu.registers[10];
  W32(object+88u,0);W32(object+94u,0);W32(object+100u,0);W16(object+160u,7);
  CHECK(push(&s,s.cpu.registers[7],2,1));CHECK(call(&s,0x1a77cu,0xf516u));s.cpu.registers[2]=3;s.cpu.registers[0]&=3u;POP(2);
  value=s.cpu.registers[0];s.cpu.registers[2]=value<=1?1:value==2?2:3;W32(object+188u,value<=1?0x89ecu:value==2?0x85e0u:0x8858u);
  CHECK(push(&s,object,4,1));CHECK(call(&s,0xf368u,0xf55cu));s.cpu.registers[4]=s.cpu.registers[0];flags(&s,s.cpu.registers[4],32);POP(4);s.cpu.registers[12]=0x13f12u;s.cpu.registers[11]=0x13f7cu;regword(&s,5,0);flags(&s,0,16);
 }
 object=s.cpu.registers[10];WORK();R16(object+2u,w);
 if(w){W16(object,0);flags(&s,0,16);CHECK(push(&s,0xf57cu,4,0));s.cpu.pc=0xdf7au;*state=s.cpu;return BIWN_ACTOR_TASK_EXIT_BOUNDARY;}
 if((uint16_t)s.cpu.registers[6]){
  R8(object+110u,b);regbyte(&s,1,b);R8(object+111u,c);regbyte(&s,1,(uint8_t)(b-c));
  if((uint8_t)s.cpu.registers[1]){
   regbyte(&s,0,(uint8_t)s.cpu.registers[1]);regword(&s,0,sx8w((uint8_t)s.cpu.registers[0]));s.cpu.registers[8]=sx16((uint16_t)s.cpu.registers[0]);R32(0x4c24cu,s.cpu.registers[0]);s.cpu.registers[0]=0u-s.cpu.registers[0];
   if(less32(s.cpu.registers[8],s.cpu.registers[0])){R8(0x4c24fu,b);regbyte(&s,1,(uint8_t)(0u-b));}
   regbyte(&s,0,(uint8_t)s.cpu.registers[1]);regword(&s,0,sx8w((uint8_t)s.cpu.registers[0]));s.cpu.registers[8]=sx16((uint16_t)s.cpu.registers[0]);R32(0x4c24cu,speed);if(less32(speed,s.cpu.registers[8])){R8(0x4c24fu,b);regbyte(&s,1,b);}
   R32(0x4c24cu,s.cpu.registers[0]);s.cpu.registers[0]=(s.cpu.registers[0]>>2)|((s.cpu.registers[0]&0x80000000u)?0xc0000000u:0);s.cpu.registers[0]++;W32(object+120u,s.cpu.registers[0]);R8(object+110u,b);W8(object+110u,(uint8_t)(b-(uint8_t)s.cpu.registers[1]));
  }else{regword(&s,6,0);flags(&s,0,16);}
  CHECK(push(&s,object,4,1));CHECK(call(&s,0xf368u,0xf5d6u));s.cpu.registers[4]=s.cpu.registers[0];flags(&s,s.cpu.registers[4],32);POP(4);goto velocity;
 }
 R32(0x4c24cu,value);W32(object+120u,value);R16(object+196u,w);
 if(w){R32(object+68u,s.cpu.registers[8]);R16(s.cpu.registers[8],w);if((w^0x8000u)<=((uint16_t)80^0x8000u)){
  W16(object+196u,0);
retry:
  WORK();CHECK(push(&s,s.cpu.registers[7],2,1));CHECK(call(&s,0x1a77cu,0xf604u));s.cpu.registers[13]=s.cpu.registers[0];CHECK(push(&s,s.cpu.registers[13],4,1));CHECK(push(&s,object,4,1));CHECK(call(&s,s.cpu.registers[12],0xf60cu));POP(10);
  if((uint16_t)s.cpu.registers[0]){R8(object+111u,b);W8(object+111u,(uint8_t)(b+64u));s.cpu.registers[6]=1;goto course;}
  CHECK(push(&s,s.cpu.registers[13],4,1));CHECK(push(&s,object,4,1));CHECK(call(&s,s.cpu.registers[11],0xf624u));POP(8);
  if((uint16_t)s.cpu.registers[0]){R8(object+111u,b);W8(object+111u,(uint8_t)(b+192u));s.cpu.registers[6]=1;goto course;}
  CHECK(push(&s,object,4,1));CHECK(call(&s,0x13feau,0xf63cu));POP(4);
  if((uint16_t)s.cpu.registers[0]){
   CHECK(push(&s,0,4,1));CHECK(push(&s,object,4,1));CHECK(call(&s,s.cpu.registers[12],0xf648u));POP(8);if((uint16_t)s.cpu.registers[0])goto retry;
   CHECK(push(&s,3,4,0));CHECK(push(&s,object,4,1));CHECK(call(&s,s.cpu.registers[11],0xf656u));POP(8);if((uint16_t)s.cpu.registers[0])goto retry;
   R8(object+111u,b);W8(object+111u,(uint8_t)(b+128u));s.cpu.registers[6]=1;
  }
  if(!(uint16_t)s.cpu.registers[6]){CHECK(push(&s,object,4,1));CHECK(call(&s,0xf368u,0xf670u));s.cpu.registers[4]=s.cpu.registers[0];flags(&s,s.cpu.registers[4],32);POP(4);}
 }}
course:
 W16(object+196u,0);R8(object+111u,b);regbyte(&s,5,b);
 switch((uint16_t)s.cpu.registers[5]){case 0:R32(object+4u,s.cpu.registers[3]);s.cpu.registers[3]-=s.cpu.registers[4];break;case 64:R32(object+10u,s.cpu.registers[3]);s.cpu.registers[3]-=s.cpu.registers[4];break;case 128:R32(object+4u,value);s.cpu.registers[3]=s.cpu.registers[4]-value;break;case 192:R32(object+10u,value);s.cpu.registers[3]=s.cpu.registers[4]-value;break;default:break;}
 if(less32(s.cpu.registers[3],0xfffffff8u))s.cpu.registers[3]=0xfffffff8u;if(less32(8u,s.cpu.registers[3]))s.cpu.registers[3]=8;
 s.cpu.registers[2]=8;regbyte(&s,2,(uint8_t)s.cpu.registers[3]);R8(object+111u,b);regbyte(&s,2,(uint8_t)((uint8_t)s.cpu.registers[2]+b));W8(object+110u,(uint8_t)s.cpu.registers[2]);
velocity:
 R8(object+111u,b);regbyte(&s,0,b);s.cpu.registers[0]>>=1;s.cpu.registers[2]=127;s.cpu.registers[0]&=127u;regword(&s,0,(uint16_t)(s.cpu.registers[0]+4u));R16(object+8u,w);regword(&s,0,(uint16_t)((uint16_t)s.cpu.registers[0]+w));
 if(((uint16_t)s.cpu.registers[0]^0x8000u)<(0xfff8u^0x8000u))s.cpu.registers[0]=0xfffffff8u;if((8u^0x8000u)<((uint16_t)s.cpu.registers[0]^0x8000u))s.cpu.registers[0]=8;
 d0=s.cpu.registers[0];diff=(uint16_t)d0;s.cpu.sr=(uint16_t)((s.cpu.sr&~0x10u)|(diff?0x10u:0));regword(&s,0,(uint16_t)(0u-(uint16_t)d0));s.cpu.registers[9]=sx16((uint16_t)s.cpu.registers[0]);W32(object+116u,s.cpu.registers[9]);
 CHECK(push(&s,0x3c860u,4,0));CHECK(push(&s,object,4,1));CHECK(call(&s,0x13c9au,0xf706u));CHECK(push(&s,0xf70cu,4,0));s.cpu.pc=0xdf60u;*state=s.cpu;return BIWN_ACTOR_TASK_OK;
}
