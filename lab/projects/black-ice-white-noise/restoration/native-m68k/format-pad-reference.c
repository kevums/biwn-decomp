#include "format-pad-native.h"
/* Coordinator reference, NOT local-model output or a training target. */
static void word(uint32_t *p,uint16_t v){*p=(*p&0xffff0000u)|v;}
static uint16_t sub1(uint16_t v,uint16_t *x){*x=v==0u?16u:0u;return (uint16_t)(v-1u);}
void biwn_native_format_pad_body(uint32_t *r){
 uint32_t sp=r[15];uint16_t x=(uint16_t)(r[16]&16u);
 PW32(sp-4u,r[2]);r[8]=PR32(sp+4u);r[9]=PR32(sp+10u);
 word(&r[1],PR16(sp+14u));uint16_t count=1u;
 if((int16_t)PR16(r[9])<=0){word(&r[0],0);goto finish;}
 PW8(r[8],PR8(sp+9u));r[8]++;
 word(&r[0],PR16(r[9]));word(&r[0],sub1((uint16_t)r[0],&x));PW16(r[9],r[0]);
 if((int16_t)r[0]<=0)goto result;
 for(;;){
  word(&r[1],sub1((uint16_t)r[1],&x));
  if((int16_t)r[1]<=0)break;
  PW8(r[8],32u);r[8]++;
  word(&r[0],PR16(r[9]));word(&r[0],sub1((uint16_t)r[0],&x));PW16(r[9],r[0]);
  x=count==65535u?16u:0u;count=(uint16_t)(count+1u);
  if((int16_t)r[0]<=0)break;
 }
result:word(&r[0],count);
finish:r[2]=PR32(sp-4u);r[16]=(r[16]&0xffffffe0u)|x|(r[2]==0?4u:0u)|((r[2]&0x80000000u)?8u:0u);
}
