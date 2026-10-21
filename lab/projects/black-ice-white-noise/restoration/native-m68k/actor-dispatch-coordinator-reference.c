/* Coordinator reference, withheld from local Author. Original13AE0body only. */
#include "actor-dispatch-native.h"
static uint32_t word(uint32_t old,uint16_t value){return(old&0xffff0000u)|value;}
static uint32_t sx(uint16_t x){return(uint32_t)(x&0x7fffu)-(uint32_t)(x&0x8000u);}
void biwn_native_actor_dispatch_body(uint32_t *r)
{
 uint32_t sp=r[15];
 r[9]=sx(ADR16(sp+4u));r[5]=ADR32(sp+6u);
 r[4]=word(r[4],ADR16(sp+10u));r[3]=ADR32(sp+12u);
 r[2]=word(r[2],ADR16(sp+16u));r[8]=0x4208cu;
 uint8_t flags=ADR8(r[8]+sx((uint16_t)r[9]));
 if(flags&1u){
  uint16_t i=0;r[8]=0x49d6cu;
  for(;;){
   r[0]=(uint32_t)i*206u;
   if(!ADR16(r[8]+r[0]))break;
   ++i;r[16]&=~16u;
   if(i==40){r[1]=word(r[1],i);r[16]&=~15u;return;}
  }
  r[1]=word(r[1],i);
  r[16]=(r[16]&~15u)|((uint16_t)r[9]==0?4u:0u)|((r[9]&0x8000u)?8u:0u);
  biwn_native_actor_dispatch_actor_capture(r);
 }else{
  r[16]=(r[16]&~15u)|((uint16_t)r[9]==0?4u:0u)|((r[9]&0x8000u)?8u:0u);
  biwn_native_actor_dispatch_sprite_capture(r);
 }
}
