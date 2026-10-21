/* Recovered sprite pool creation, 137E0..13ADE. Coordinator source.
 * Ordered volatile accesses preserve original handle rereads. Known inline
 * callback targets are decoded as data; modified unknown targets trap. */
#include "sprite-create-native.h"
static uint32_t sc_word(uint32_t old,uint16_t v){return(old&0xffff0000u)|v;}
static uint32_t sc_sx(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t sc_sx8(uint8_t v){return(uint32_t)(v&127u)-(uint32_t)(v&128u);}
static uint32_t sc_asr10(uint32_t v){return(v>>10)|((v&0x80000000u)?0xffc00000u:0);}
static uint32_t sc_nz(uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:((1u<<bits)-1u);v&=mask;return(v==0?4u:0u)|((v>>(bits-1))?8u:0u);}
static uint32_t sc_cmp16(uint16_t a,uint16_t b){uint16_t v=(uint16_t)(a-b);return sc_nz(v,16)|(a<b?1u:0u)|(((a^b)&(a^v)&0x8000u)?2u:0u);}
static uint32_t sc_add32(uint32_t a,uint32_t b){uint32_t v=a+b;return sc_nz(v,32)|(v<a?17u:0u)|((~(a^b)&(a^v)&0x80000000u)?2u:0u);}
static void sc_flags(uint32_t*r,uint32_t flags){r[16]=(r[16]&~31u)|flags;}
void biwn_native_sprite_create_body(uint32_t*r)
{
 uint32_t sp=r[15],xbit=r[16]&16u;
 r[10]=sc_sx(SCR16(sp+4u));r[14]=sc_sx(SCR16(sp+10u));r[13]=SCR32(sp+12u);
 r[6]=sc_word(r[6],SCR16(sp+16u));r[12]=0x6e6a0u;r[4]=sc_word(r[4],0);r[11]=0x4bd9cu;
 uint16_t slot;
 for(slot=0;slot<40;slot++){
  r[0]=sc_sx(slot)*30u;
  if(SCR16(r[11]+r[0])==0)break;
  r[4]=sc_word(r[4],(uint16_t)(slot+1u));xbit=0;
 }
 if(slot==40){sc_flags(r,xbit|sc_cmp16(40,39));return;}
 r[5]=sc_sx(slot)*30u;uint32_t object=r[11]+r[5];
 SCW16(object,r[10]);SCW32(object+2u,SCR32(sp+6u));SCW16(object+6u,r[14]);SCW32(object+8u,r[13]);
 r[3]=0xfffffc00u;r[0]=r[13]&r[3];r[1]=SCR32(0x49c56u)&r[3];r[0]=sc_asr10(r[0]-r[1]);
 r[7]=10;r[2]=r[0]*4u;r[9]=r[2]+r[0]+10u;r[2]=sc_word(r[9],(uint16_t)(r[9]+2u));
 r[0]=SCR32(sp+6u)&r[3];r[1]=SCR32(0x49c50u)&r[3];r[0]=sc_asr10(r[0]-r[1]);
 uint32_t sum=(uint16_t)r[2]+(uint32_t)(uint16_t)r[0];r[2]=sc_word(r[2],(uint16_t)sum);xbit=sum>0xffffu?16u:0u;
 SCW16(object+14u,r[2]);sc_flags(r,xbit|sc_nz(r[2],16));
 biwn_native_sprite_create_position_capture(r);
 r[2]=(uint16_t)r[10];r[8]=0x4208cu;
 uint8_t flags=SCR8(r[8]+r[2]);
 if(flags&2u){
  xbit=(r[6]&0x100u)?16u:0u;r[6]=sc_word(r[6],(uint16_t)(r[6]<<8));SCW8(r[11]+r[5]+12u,r[6]);
  uint16_t id=(uint16_t)r[10],index=(uint16_t)(id-104u);r[0]=sc_word(r[0],index);xbit=id>=104u?16u:0u;
  if(index>34u){sc_flags(r,xbit|sc_cmp16(index,34));return;}
  r[0]=(uint32_t)index*2u;uint16_t offset=SCR16(0x138bcu+r[0]);r[0]=sc_word(r[0],offset);xbit=0;
  sc_flags(r,sc_nz(offset,16));uint32_t callback;
  switch(0x138bcu+sc_sx(offset)){
   case 0x13902u:callback=0x8f54u;break;case 0x1391au:callback=0x9de0u;break;
   case 0x13932u:callback=0xa2b8u;break;case 0x1394au:callback=0x9908u;break;
   case 0x139ceu:callback=0x8db0u;break;case 0x139e6u:callback=0xce20u;break;
   case 0x139feu:callback=0xb390u;break;case 0x13a16u:callback=0xc648u;break;
   case 0x13ad8u:return;
   case 0x13a2eu:r[0]=sc_sx((uint16_t)r[4])*30u;r[8]=0x4bd9cu;SCW16(r[8]+r[0],0);sc_flags(r,4);return;
   case 0x13962u:{
    r[0]=sc_sx((uint16_t)r[4])*30u;r[8]=0x4bd9cu;SCW32(r[8]+r[0]+24u,0x8b80u);
    r[7]=0xffffffe0u;uint32_t old=SCR32(r[8]+r[0]+2u);SCW32(r[8]+r[0]+2u,old+r[7]);xbit=old>=32u?16u:0u;
    r[1]=sc_word(r[1],SCR16(r[8]+r[0]+16u));r[4]=sc_word(r[4],0);
    for(slot=0;slot<40;slot++){
     r[0]=sc_sx(slot)*30u;if(SCR16(r[8]+r[0])==0)break;
     r[4]=sc_word(r[4],(uint16_t)(slot+1u));xbit=0;
    }
    if(slot==40){sc_flags(r,xbit|sc_cmp16(40,39));return;}
    r[0]=sc_sx((uint16_t)r[4])*30u;object=r[8]+r[0];
    SCW16(object+16u,r[1]);SCW16(object,r[10]);SCW32(object+2u,SCR32(sp+6u));SCW16(object+6u,r[14]);
    r[13]+=32u;SCW32(object+8u,r[13]);SCW8(object+12u,0);SCW32(object+24u,0x8c98u);sc_flags(r,xbit|sc_nz(0x8c98,32));return;
   }
   default:__builtin_trap();
  }
  r[0]=sc_sx((uint16_t)r[4])*30u;r[8]=0x4bd9cu;SCW32(r[8]+r[0]+24u,callback);sc_flags(r,sc_nz(callback,32));return;
 }
 r[0]=SCR32(0x6e6a8u);uint32_t size=r[0];r[0]+=r[0];r[9]=r[0];r[18]=r[0]+16u;sc_flags(r,sc_add32(size,size));
 biwn_native_sprite_create_allocate_capture(r);
 r[8]=r[0];SCW32(r[11]+r[5]+20u,r[8]);r[8]=SCR32(r[8]);SCW32(r[8],0x20000u);
 r[8]=SCR32(r[11]+r[5]+20u);uint32_t payload=SCR32(r[8]);r[10]=0x42000u;
 uint8_t frame=SCR8(r[10]+r[2]);r[0]=sc_sx8(frame)*4u;r[9]=0x6e6a0u;r[12]+=SCR32(r[9]+r[0]+12u);
 r[1]=(uint32_t)SCR8(r[12])<<16;r[0]=SCR8(r[12]+1u);r[1]|=r[0];r[9]=payload;SCW32(r[9]+8u,r[1]);
 r[0]=(uint32_t)SCR8(r[12])*4u;r[8]=0x3bd20u;r[9]=payload;SCW32(r[9]+12u,SCR32(r[8]+r[0]));
 r[8]=SCR32(r[11]+r[5]+20u);uint32_t allocation=SCR32(r[8]);r[7]=16u+allocation;xbit=r[7]<16u?16u:0u;
 frame=SCR8(r[10]+r[2]);r[0]=sc_word(r[0],(uint16_t)sc_sx8(frame));r[9]=sc_sx((uint16_t)r[0]);
 sc_flags(r,xbit|sc_nz(r[0],16));biwn_native_sprite_create_decode_capture(r);
}
