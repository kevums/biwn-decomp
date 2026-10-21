#include "biwn_actor_collision.h"
struct collision{struct biwn_world_bus *bus;struct biwn_task_cpu cpu;uint32_t limit;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void word(struct collision *s,unsigned i,uint16_t v){s->cpu.registers[i]=(s->cpu.registers[i]&0xffff0000u)|v;}
static void nz(struct collision *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:0xffffu,sign=1u<<(bits-1);v&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static void xflag(struct collision *s,unsigned x){s->cpu.sr=(uint16_t)((s->cpu.sr&~0x10u)|(x?0x10u:0));}
static uint16_t add(struct collision *s,uint16_t a,uint16_t b){uint32_t v=(uint32_t)a+b;xflag(s,v>0xffffu);return(uint16_t)v;}
static uint16_t sub(struct collision *s,uint16_t a,uint16_t b){xflag(s,a<b);return(uint16_t)(a-b);}
static uint16_t asr6(struct collision *s,uint16_t v){xflag(s,(v>>5)&1u);return(uint16_t)((v>>6)|(v&0x8000u?0xfc00u:0));}
#define R16(a,v) do{if(s.bus->read16(s.bus->context,(a),&(v)))return BIWN_ACTOR_COLLISION_BUS_ERROR;}while(0)
#define R32(a,v) do{if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_ACTOR_COLLISION_BUS_ERROR;}while(0)
#define W16(a,v) do{if(s.bus->write16(s.bus->context,(a),(uint16_t)(v)))return BIWN_ACTOR_COLLISION_BUS_ERROR;}while(0)
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_actor_collision_status)status;}while(0)
#define POP(n) do{s.cpu.registers[15]+=(n);s.cpu.usp=s.cpu.registers[15];}while(0)
static int push(struct collision *s,uint32_t v,unsigned width)
{s->cpu.registers[15]-=width;s->cpu.usp=s->cpu.registers[15];if(width==2){if(s->bus->write16(s->bus->context,s->cpu.registers[15],(uint16_t)v))return 3;}else if(s->bus->write32(s->bus->context,s->cpu.registers[15],v))return 3;nz(s,v,width*8);return 0;}
static int geometry(struct collision *s,uint32_t target,uint32_t ret)
{uint32_t sp,pc;int status=push(s,ret,4);if(status)return status;sp=s->cpu.registers[15];s->cpu.pc=target;status=biwn_geometry_cpu_body(s->bus,&s->cpu,s->limit);if(status)return status;if(s->cpu.registers[15]!=sp)return 4;if(s->bus->read32(s->bus->context,sp,&pc))return 3;if(pc!=ret)return 4;s->cpu.registers[15]+=4;s->cpu.usp=s->cpu.registers[15];s->cpu.pc=pc;return 0;}
enum biwn_actor_collision_status biwn_actor_collision_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
 struct collision s;uint32_t object,entry,value,old,scans=0;uint16_t w,b,edge,direction,index,flags,target;
 if(!bus||!state||!limit||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->sr&0x2000u||(state->pc!=0x13b5au&&state->pc!=0x13bb0u))return BIWN_ACTOR_COLLISION_BAD_ARGUMENT;
 s.bus=bus;s.cpu=*state;s.limit=limit;entry=s.cpu.pc;CHECK(push(&s,s.cpu.registers[10],4));
 if(entry==0x13b5au){
  CHECK(push(&s,s.cpu.registers[2],4));R32(s.cpu.registers[15]+12u,s.cpu.registers[10]);object=s.cpu.registers[10];R16(s.cpu.registers[15]+16u,edge);word(&s,1,edge);R16(s.cpu.registers[15]+20u,w);word(&s,2,w);word(&s,0,edge&0xf000u);
  if(!(edge&0xf000u)){word(&s,1,edge&0xfffu);CHECK(push(&s,s.cpu.registers[1],2));CHECK(push(&s,object,4));CHECK(geometry(&s,0x1039cu,0x13b80u));POP(6);}
  else if(edge==0xffffu){
   R16(object+64u,w);W16(object+64u,add(&s,w,(uint16_t)s.cpu.registers[2]));CHECK(push(&s,object,4));CHECK(geometry(&s,0x102c4u,0x13b96u));POP(4);
   if((uint16_t)s.cpu.registers[0]){s.cpu.registers[0]=1;nz(&s,1,32);}
   else{R16(object+64u,w);W16(object+64u,sub(&s,w,(uint16_t)s.cpu.registers[2]));word(&s,0,0);nz(&s,0,16);}
  }else{word(&s,0,0);nz(&s,0,16);}
  R32(s.cpu.registers[15],s.cpu.registers[2]);POP(4);nz(&s,s.cpu.registers[2],32);R32(s.cpu.registers[15],s.cpu.registers[10]);POP(4);s.cpu.pc=0x13baeu;*state=s.cpu;return BIWN_ACTOR_COLLISION_OK;
 }
 R32(s.cpu.registers[15]+8u,s.cpu.registers[10]);object=s.cpu.registers[10];R32(s.cpu.registers[15]+12u,s.cpu.registers[9]);R16(s.cpu.registers[15]+16u,direction);word(&s,0,direction);
 switch(direction){
 case 0:R16(object+6u,w);R16(object+54u,b);word(&s,0,asr6(&s,sub(&s,w,b)));word(&s,1,(uint16_t)s.cpu.registers[0]);R16(s.cpu.registers[9]+8u,w);word(&s,1,add(&s,(uint16_t)s.cpu.registers[1],w));break;
 case 1:R16(object+50u,w);R16(object+6u,b);word(&s,1,asr6(&s,sub(&s,w,b)));R16(s.cpu.registers[9]+8u,w);xflag(&s,(w>>15)&1u);word(&s,0,(uint16_t)(w<<1));R16(s.cpu.registers[9]+6u,w);word(&s,0,add(&s,(uint16_t)s.cpu.registers[0],w));word(&s,1,add(&s,(uint16_t)s.cpu.registers[1],(uint16_t)s.cpu.registers[0]));break;
 case 2:R16(object+58u,w);R16(object+12u,b);word(&s,0,asr6(&s,sub(&s,w,b)));R16(s.cpu.registers[9]+8u,w);word(&s,1,w);R16(s.cpu.registers[9]+6u,w);word(&s,1,add(&s,(uint16_t)s.cpu.registers[1],w));word(&s,1,add(&s,(uint16_t)s.cpu.registers[1],(uint16_t)s.cpu.registers[0]));break;
 case 3:R16(object+12u,w);R16(object+62u,b);word(&s,0,sub(&s,w,b));word(&s,1,asr6(&s,(uint16_t)s.cpu.registers[0]));break;
 default:break;
 }
 R16(s.cpu.registers[9]+22u,index);if(index==0xffffu)goto indoor_fail;
 R32(0x49c18u,s.cpu.registers[8]);R16(s.cpu.registers[9]+22u,index);s.cpu.registers[0]=sx16(index)*6u;R32(s.cpu.registers[8]+8u,value);old=s.cpu.registers[0];s.cpu.registers[0]+=value;xflag(&s,s.cpu.registers[0]<old);s.cpu.registers[8]=s.cpu.registers[0];
 for(;;){
  if(scans++>=limit)return BIWN_ACTOR_COLLISION_SCAN_LIMIT;R16(s.cpu.registers[8],w);
  if((uint16_t)s.cpu.registers[1]==w)break;
  R16(s.cpu.registers[8]+2u,flags);if(flags&0x8000u)goto indoor_fail;s.cpu.registers[8]+=6u;
 }
 R16(s.cpu.registers[8]+2u,flags);word(&s,0,flags&0x7000u);if(!(flags&0x7000u))goto indoor_fail;
 R16(s.cpu.registers[8]+4u,target);
 if(target!=0xffffu){R16(s.cpu.registers[8]+4u,target);CHECK(push(&s,target,2));CHECK(push(&s,object,4));CHECK(geometry(&s,0x10652u,0x13c86u));POP(6);goto indoor_done;}
 R16(object+22u,w);if(w)goto indoor_fail;CHECK(push(&s,object,4));CHECK(geometry(&s,0x1028eu,0x13c66u));POP(4);
 if((uint16_t)s.cpu.registers[0]){W16(object+20u,1);s.cpu.registers[0]=2;nz(&s,2,32);goto indoor_done;}
indoor_fail:
 word(&s,0,0);nz(&s,0,16);
indoor_done:
 R32(s.cpu.registers[15],s.cpu.registers[10]);POP(4);s.cpu.pc=0x13c98u;*state=s.cpu;return BIWN_ACTOR_COLLISION_OK;
}
enum biwn_actor_collision_status biwn_actor_collision_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
 struct biwn_task_cpu s;enum biwn_actor_collision_status status;if(!state)return BIWN_ACTOR_COLLISION_BAD_ARGUMENT;s=*state;
 status=biwn_actor_collision_body(bus,&s,limit);if(status)return status;if(bus->read32(bus->context,s.registers[15],&s.pc))return BIWN_ACTOR_COLLISION_BUS_ERROR;s.registers[15]+=4;s.usp=s.registers[15];*state=s;return BIWN_ACTOR_COLLISION_OK;
}
