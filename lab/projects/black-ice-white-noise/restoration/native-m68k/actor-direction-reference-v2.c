/* Coordinator native adaptation of the previously original-CPU-checked
 * portable13440 body. Actual original E588 division runs through the ABI bridge. */
#include "actor-direction-native.h"
struct direction {uint32_t *r;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void word(struct direction *s,unsigned i,uint16_t v){s->r[i]=(s->r[i]&0xffff0000u)|v;}
static void byte(struct direction *s,unsigned i,uint8_t v){s->r[i]=(s->r[i]&0xffffff00u)|v;}
static void nz8(struct direction *s,uint8_t v){s->r[16]=(uint16_t)((s->r[16]&0xfff0u)|(v?0:4)|(v&0x80u?8:0));}
static void xflag(struct direction *s,unsigned x){s->r[16]=(uint16_t)((s->r[16]&~0x10u)|(x?0x10u:0));}
#define R16(a,v) do{(v)=ADR16(a);}while(0)
#define R32(a,v) do{(v)=ADR32(a);}while(0)
#define W32(a,v) do{ADW32(a,v);}while(0)
#define PUSH(v) do{s.r[15]-=4;W32(s.r[15],(v));}while(0)
void biwn_native_actor_direction_body(uint32_t *r)
{
 struct direction s;uint16_t x,z;uint32_t threshold;unsigned index;int i;
 s.r=r;for(i=4;i>=2;i--)PUSH(s.r[i]);
 R16(s.r[15]+16u,x);R16(s.r[15]+18u,z);word(&s,0,x);word(&s,1,z);
 if(x&0x8000u){word(&s,0,(uint16_t)(0u-x));xflag(&s,x!=0);if(z&0x8000u){word(&s,1,(uint16_t)(0u-z));xflag(&s,z!=0);s.r[3]=2;}else s.r[3]=1;}
 else if(z&0x8000u){word(&s,1,(uint16_t)(0u-z));xflag(&s,z!=0);s.r[3]=3;}else s.r[3]=4;
 if(!(uint16_t)s.r[1])byte(&s,1,64);
 else{
  s.r[0]=(uint32_t)(uint16_t)s.r[0]<<16;s.r[8]=sx16((uint16_t)s.r[1]);PUSH(s.r[8]);PUSH(s.r[0]);
  s.r[16]=(uint16_t)((s.r[16]&0xfff0u)|(s.r[0]?0u:4u)|(s.r[0]&0x80000000u?8u:0u));
  biwn_native_actor_direction_division_capture(r);s.r[15]+=8;
  s.r[8]=s.r[0];byte(&s,1,0);word(&s,2,0);s.r[9]=0x41f00u;
  for(index=0;index<64;index++){
   byte(&s,2,(uint8_t)s.r[1]);word(&s,0,(uint16_t)s.r[2]);s.r[0]=sx16((uint16_t)s.r[0]);s.r[0]<<=2;xflag(&s,0);R32(s.r[9]+s.r[0],threshold);
   if((s.r[8]^0x80000000u)<=(threshold^0x80000000u))break;
   byte(&s,1,(uint8_t)(s.r[1]+1u));xflag(&s,(uint8_t)s.r[1]==0);
  }
 }
 if(s.r[3]==2){byte(&s,4,128);xflag(&s,(uint8_t)s.r[4]<(uint8_t)s.r[1]);byte(&s,4,(uint8_t)(s.r[4]-s.r[1]));byte(&s,1,(uint8_t)s.r[4]);}
 else if(s.r[3]==3){xflag(&s,(uint8_t)s.r[1]>127);byte(&s,1,(uint8_t)(s.r[1]+128u));}
 else if(s.r[3]==4){xflag(&s,(uint8_t)s.r[1]!=0);byte(&s,1,(uint8_t)(0u-(uint8_t)s.r[1]));}
 word(&s,0,0);byte(&s,0,(uint8_t)s.r[1]);nz8(&s,(uint8_t)s.r[0]);
 for(i=2;i<=4;i++){R32(s.r[15],s.r[i]);s.r[15]+=4;}
 return;
}