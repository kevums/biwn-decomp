#include "biwn_actor_navigation.h"
static uint32_t sx16(uint16_t v){return (uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void word(struct biwn_task_cpu *s,unsigned r,uint16_t v){s->registers[r]=(s->registers[r]&0xffff0000u)|v;}
static void nz(struct biwn_task_cpu *s,uint32_t v){s->sr=(uint16_t)((s->sr&0xfff0u)|(v?0:4)|(v&0x80000000u?8:0));}
static void xflag(struct biwn_task_cpu *s,unsigned x){s->sr=(uint16_t)((s->sr&~0x10u)|(x?0x10u:0));}
#define R8(a,v) do{if(bus->read8(bus->context,(a),&(v)))return BIWN_ACTOR_NAVIGATION_BUS_ERROR;}while(0)
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_ACTOR_NAVIGATION_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_ACTOR_NAVIGATION_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_ACTOR_NAVIGATION_BUS_ERROR;}while(0)
enum biwn_actor_navigation_status biwn_actor_navigation_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu s;uint32_t object,record,value,table,target,base,old;uint16_t kind,offset;uint8_t heading;unsigned axis,form,index,neighbor;
 if(!bus||!state||!bus->read8||!bus->read16||!bus->read32||!bus->write32||state->sr&0x2000u||
    (state->pc!=0xf368u&&state->pc!=0x13f12u&&state->pc!=0x13f7cu&&state->pc!=0x13feau))return BIWN_ACTOR_NAVIGATION_BAD_ARGUMENT;
 s=*state;
 if(s.pc==0xf368u){
  s.registers[15]-=4;W32(s.registers[15],s.registers[10]);
  s.registers[15]-=4;W32(s.registers[15],s.registers[2]);
  R32(s.registers[15]+12u,s.registers[9]);object=s.registers[9];
  word(&s,0,0);R8(object+111u,heading);word(&s,0,heading);
  if(heading!=0&&heading!=64&&heading!=128&&heading!=192)goto waypoint_return;
  R32(object+68u,s.registers[8]);record=s.registers[8];axis=(heading==64||heading==192);
  R16(record+(axis?18u:16u),kind);word(&s,0,kind);
  if(kind!=1&&kind!=2&&kind!=4)goto waypoint_return;
  /* OR32, plus96 or plus160. Separate original D0/D1 use is observable. */
  form=heading==0?(kind==1?0:kind==2?1:2):
       heading==64?(kind==1?0:kind==2?1:2):
       heading==128?(kind==4?1:0):(kind==4?1:0);
  if(form==1){
   R32(object+(axis?10u:4u),s.registers[1]);word(&s,1,(uint16_t)s.registers[1]&0xfc00u);
   R16(record+(axis?14u:10u),offset);word(&s,0,offset);xflag(&s,(offset>>10)&1u);word(&s,0,(uint16_t)(offset<<6));
   s.registers[10]=s.registers[1]+sx16((uint16_t)s.registers[0])+96u;s.registers[0]=s.registers[10];
  }else{
   R32(object+(axis?10u:4u),s.registers[0]);word(&s,0,(uint16_t)s.registers[0]&0xfc00u);
   R16(record+(axis?14u:10u),offset);word(&s,1,offset);xflag(&s,(offset>>10)&1u);word(&s,1,(uint16_t)(offset<<6));
   s.registers[10]=s.registers[0]+sx16((uint16_t)s.registers[1]);s.registers[0]=s.registers[10];
   if(form==2){old=s.registers[0];s.registers[0]+=160u;xflag(&s,s.registers[0]<old);}
   else{s.registers[2]=32;s.registers[0]|=32u;}
  }
waypoint_return:
  R32(s.registers[15],s.registers[2]);s.registers[15]+=4;nz(&s,s.registers[2]);
  R32(s.registers[15],s.registers[10]);s.registers[15]+=4;s.usp=s.registers[15];s.pc=0xf4d6u;*state=s;return BIWN_ACTOR_NAVIGATION_OK;
 }
 R32(s.registers[15]+4u,s.registers[8]);object=s.registers[8];
 if(s.pc!=0x13feau){
  s.registers[0]=3;R32(s.registers[15]+8u,value);s.registers[0]&=value;
  if(s.pc==0x13f7cu)s.registers[1]=3;
  if(s.registers[0]!=(s.pc==0x13f12u?0u:3u)){
   word(&s,0,0);s.sr=(uint16_t)((s.sr&0xfff0u)|4u);s.pc=s.pc==0x13f12u?0x13f7au:0x13fe8u;*state=s;return BIWN_ACTOR_NAVIGATION_OK;
  }
 }
 word(&s,0,0);R8(object+110u,heading);word(&s,0,(uint16_t)heading+32u);
 word(&s,0,(uint16_t)s.registers[0]>>6);index=(uint16_t)s.registers[0];
 /* Heading is a byte: index0..4. AND.L7 also clears incoming D0 high bits. */
 s.registers[1]=7;s.registers[0]&=7u;old=s.registers[0];s.registers[0]+=old;xflag(&s,s.registers[0]<old);
 table=s.pc==0x13f12u?0x13f3eu:s.pc==0x13f7cu?0x13facu:0x1400eu;
 R16(table+s.registers[0],offset);word(&s,0,offset);target=table+sx16((uint16_t)s.registers[0]);base=table+10u;
 if(target==base)index=0;else if(target==base+18u)index=1;else if(target==base+28u)index=2;else if(target==base+38u)index=3;else return BIWN_ACTOR_NAVIGATION_BAD_TABLE;
 if(s.pc==0x13f12u){const unsigned neighbors[4]={8,4,6,2};neighbor=neighbors[index];}
 else if(s.pc==0x13f7cu){const unsigned neighbors[4]={6,2,8,4};neighbor=neighbors[index];}
 else{const unsigned neighbors[4]={2,8,4,6};neighbor=neighbors[index];}
 R32(object+68u,s.registers[8]);R16(s.registers[8]+neighbor,offset);word(&s,0,offset&0xf000u);
 if(s.pc==0x13feau){s.registers[0]=(uint16_t)s.registers[0]?1u:0u;s.pc=s.registers[0]?0x1404au:0x14028u;}
 else{value=(uint16_t)s.registers[0]?0u:1u;s.pc=s.pc==0x13f12u?(value?0x13f58u:0x13f7au):(value?0x13fc6u:0x13fe8u);s.registers[0]=value;}
 nz(&s,s.registers[0]);*state=s;return BIWN_ACTOR_NAVIGATION_OK;
}
enum biwn_actor_navigation_status biwn_actor_navigation_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu s;enum biwn_actor_navigation_status status;
 if(!state)return BIWN_ACTOR_NAVIGATION_BAD_ARGUMENT;s=*state;
 status=biwn_actor_navigation_body(bus,&s);if(status)return status;
 if(bus->read32(bus->context,s.registers[15],&s.pc))return BIWN_ACTOR_NAVIGATION_BUS_ERROR;
 s.registers[15]+=4;s.usp=s.registers[15];*state=s;return BIWN_ACTOR_NAVIGATION_OK;
}
