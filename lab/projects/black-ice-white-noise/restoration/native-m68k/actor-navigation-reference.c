/* Original-facing four navigation routines, coordinator adaptation of the
 * existing portable high-level body. Valid stored jump-table targets only;
 * altered/invalid computed code targets are outside the current contract. */
#include "actor-navigation-native.h"
struct navigation {uint32_t *r;};
static uint32_t sx16(uint16_t v){return (uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void word(struct navigation *s,unsigned i,uint16_t v){s->r[i]=(s->r[i]&0xffff0000u)|v;}
static void nz(struct navigation *s,uint32_t v){s->r[16]=(uint16_t)((s->r[16]&0xfff0u)|(v?0:4)|(v&0x80000000u?8:0));}
static void xflag(struct navigation *s,unsigned x){s->r[16]=(uint16_t)((s->r[16]&~0x10u)|(x?0x10u:0));}
#define R8(a,v) do{(v)=NAR8(a);}while(0)
#define R16(a,v) do{(v)=NAR16(a);}while(0)
#define R32(a,v) do{(v)=NAR32(a);}while(0)
#define W32(a,v) do{NAW32(a,v);}while(0)
void biwn_native_actor_navigation_body(uint32_t *r)
{
 struct navigation s;uint32_t object,record,value,table,target,base,old;uint16_t kind,offset;uint8_t heading;unsigned axis,form,index,neighbor;
 s.r=r;uint32_t entry=r[17];
 if(entry==0xf368u){
  s.r[15]-=4;W32(s.r[15],s.r[10]);
  s.r[15]-=4;W32(s.r[15],s.r[2]);
  R32(s.r[15]+12u,s.r[9]);object=s.r[9];
  word(&s,0,0);R8(object+111u,heading);word(&s,0,heading);
  if(heading!=0&&heading!=64&&heading!=128&&heading!=192)goto waypoint_return;
  R32(object+68u,s.r[8]);record=s.r[8];axis=(heading==64||heading==192);
  R16(record+(axis?18u:16u),kind);word(&s,0,kind);
  if(kind!=1&&kind!=2&&kind!=4)goto waypoint_return;
  /* OR32, plus96 or plus160. Separate original D0/D1 use is observable. */
  form=heading==0?(kind==1?0:kind==2?1:2):
       heading==64?(kind==1?0:kind==2?1:2):
       heading==128?(kind==4?1:0):(kind==4?1:0);
  if(form==1){
   R32(object+(axis?10u:4u),s.r[1]);word(&s,1,(uint16_t)s.r[1]&0xfc00u);
   R16(record+(axis?14u:10u),offset);word(&s,0,offset);xflag(&s,(offset>>10)&1u);word(&s,0,(uint16_t)(offset<<6));
   s.r[10]=s.r[1]+sx16((uint16_t)s.r[0])+96u;s.r[0]=s.r[10];
  }else{
   R32(object+(axis?10u:4u),s.r[0]);word(&s,0,(uint16_t)s.r[0]&0xfc00u);
   R16(record+(axis?14u:10u),offset);word(&s,1,offset);xflag(&s,(offset>>10)&1u);word(&s,1,(uint16_t)(offset<<6));
   s.r[10]=s.r[0]+sx16((uint16_t)s.r[1]);s.r[0]=s.r[10];
   if(form==2){old=s.r[0];s.r[0]+=160u;xflag(&s,s.r[0]<old);}
   else{s.r[2]=32;s.r[0]|=32u;}
  }
waypoint_return:
  R32(s.r[15],s.r[2]);s.r[15]+=4;nz(&s,s.r[2]);
  R32(s.r[15],s.r[10]);s.r[15]+=4;entry=0xf4d6u;return;
 }
 R32(s.r[15]+4u,s.r[8]);object=s.r[8];
 if(entry!=0x13feau){
  s.r[0]=3;R32(s.r[15]+8u,value);s.r[0]&=value;
  if(entry==0x13f7cu)s.r[1]=3;
  if(s.r[0]!=(entry==0x13f12u?0u:3u)){
   word(&s,0,0);s.r[16]=(uint16_t)((s.r[16]&0xfff0u)|4u);entry=entry==0x13f12u?0x13f7au:0x13fe8u;return;
  }
 }
 word(&s,0,0);R8(object+110u,heading);word(&s,0,(uint16_t)heading+32u);
 word(&s,0,(uint16_t)s.r[0]>>6);index=(uint16_t)s.r[0];
 /* Heading is a byte: index0..4. AND.L7 also clears incoming D0 high bits. */
 s.r[1]=7;s.r[0]&=7u;old=s.r[0];s.r[0]+=old;xflag(&s,s.r[0]<old);
 table=entry==0x13f12u?0x13f3eu:entry==0x13f7cu?0x13facu:0x1400eu;
 R16(table+s.r[0],offset);word(&s,0,offset);target=table+sx16((uint16_t)s.r[0]);base=table+10u;
 if(target==base)index=0;else if(target==base+18u)index=1;else if(target==base+28u)index=2;else if(target==base+38u)index=3;else __builtin_trap();
 if(entry==0x13f12u){const unsigned neighbors[4]={8,4,6,2};neighbor=neighbors[index];}
 else if(entry==0x13f7cu){const unsigned neighbors[4]={6,2,8,4};neighbor=neighbors[index];}
 else{const unsigned neighbors[4]={2,8,4,6};neighbor=neighbors[index];}
 R32(object+68u,s.r[8]);R16(s.r[8]+neighbor,offset);word(&s,0,offset&0xf000u);
 if(entry==0x13feau){s.r[0]=(uint16_t)s.r[0]?1u:0u;entry=s.r[0]?0x1404au:0x14028u;}
 else{value=(uint16_t)s.r[0]?0u:1u;entry=entry==0x13f12u?(value?0x13f58u:0x13f7au):(value?0x13fc6u:0x13fe8u);s.r[0]=value;}
 nz(&s,s.r[0]);return;
}
