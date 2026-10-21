/* Recovered134DC high-level initialization with explicit helper-visible ABI.
 * Coordinator source. Inline callback table remains an ordered guest WORD read. */
#include "native.h"
static uint32_t ai_word(uint32_t old,uint16_t v){return(old&0xffff0000u)|v;}
static uint32_t ai_sx(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t ai_asr10(uint32_t v){return(v>>10)|((v&0x80000000u)?0xffc00000u:0u);}
static uint32_t ai_nz16(uint16_t v){return(v==0?4u:0u)|((v&0x8000u)?8u:0u);}
static uint32_t ai_nz32(uint32_t v){return(v==0?4u:0u)|((v&0x80000000u)?8u:0u);}
uint32_t biwn_actor_initialize_start(uint32_t *r)
{
 uint32_t sp=r[15];
 r[10]=ai_sx(AIR16(sp+4u));r[7]=ai_word(r[7],AIR16(sp+6u));
 r[4]=AIR32(sp+8u);r[2]=AIR32(sp+14u);r[6]=ai_sx((uint16_t)r[7])*206u;r[9]=0x49d6cu;
 uint32_t object=r[9]+r[6];
 AIW16(object,r[10]);AIW16(object+2u,0);AIW32(object+4u,r[4]);
 AIW16(object+8u,AIR16(sp+12u));AIW32(object+10u,r[2]);
 AIW16(object+14u,0);AIW16(object+16u,0);AIW16(object+18u,0);
 AIW16(object+20u,AIR16(0x49c60u));AIW16(object+22u,AIR16(0x49c62u));AIW16(object+24u,AIR16(0x49c64u));
 for(uint32_t i=0;i<4;i++)AIW32(object+26u+4u*i,AIR32(0x49c66u+4u*i));
 r[3]=0xfffffc00u;r[2]&=r[3];r[0]=AIR32(0x49c56u)&r[3];r[2]=ai_asr10(r[2]-r[0]);r[5]=10;
 r[11]=r[2]*5u+10u;r[1]=ai_word(r[11],(uint16_t)(r[11]+2u));
 r[4]&=r[3];r[0]=AIR32(0x49c50u)&r[3];r[4]=ai_asr10(r[4]-r[0]);
 uint32_t room_sum=(uint32_t)(uint16_t)r[1]+(uint16_t)r[4];r[1]=ai_word(r[1],(uint16_t)room_sum);
 uint32_t room_X=room_sum>0xffffu?16u:0u;AIW16(object+64u,r[1]);
 AIW32(object+88u,0);AIW16(object+92u,0);AIW32(object+94u,0);AIW16(object+98u,0);
 AIW32(object+100u,0);AIW32(object+104u,0);AIW16(object+108u,0);
 AIW8(object+110u,AIR8(sp+19u));AIW8(object+111u,AIR8(sp+19u));
 AIW32(object+112u,0);AIW32(object+116u,0);AIW32(object+120u,0);AIW32(object+124u,0);
 r[8]=object;AIW16(object+150u,0);AIW16(object+148u,0);AIW16(object+146u,0);AIW16(object+196u,0);AIW16(object+202u,1);
 uint16_t mode=AIR16(r[9]+r[6]+20u);
 if(mode==1){r[16]=(r[16]&~31u)|room_X|ai_nz32(r[8]);return 1;}
 else{
  mode=AIR16(r[9]+r[6]+20u);
  if(mode==2){r[16]=(r[16]&~31u)|room_X|ai_nz32(r[8]);return 2;}
 }
 return 4;
}
uint32_t biwn_actor_initialize_after_placement(uint32_t *r)
{
 uint16_t id=(uint16_t)r[10],index=(uint16_t)(id-4u);uint32_t x=id<4u?16u:0u;
 r[0]=ai_word(r[0],index);
 if(index>114u)goto invalid;
 r[0]=(uint32_t)index*2u;uint16_t offset=AIR16(0x13620u+r[0]);r[0]=ai_word(r[0],offset);x=0;
 r[16]=(r[16]&~31u)|ai_nz16(offset);
 switch(0x13620u+ai_sx(offset)){
 case 0x13706u:r[18]=0xf4d8u;break;case 0x13714u:r[18]=0xedc4u;break;case 0x13722u:r[18]=0xfcc2u;break;
 case 0x13730u:r[18]=0x17f80u;break;case 0x1373eu:r[18]=0x178e0u;break;case 0x1374au:r[18]=0xf720u;break;
 case 0x13756u:r[18]=0x21d40u;break;case 0x13762u:r[18]=0x15080u;break;case 0x1376eu:r[18]=0x14fc0u;break;
 case 0x1377au:r[18]=0xf888u;break;case 0x13786u:r[18]=0x15140u;break;case 0x13792u:r[18]=0x14100u;break;
 case 0x1379eu:r[18]=0x11f80u;break;case 0x137aau:r[18]=0x128a0u;break;case 0x137b6u:r[18]=0x15a80u;break;
 case 0x137cau:goto invalid;case 0x137dau:return 0;default:__builtin_trap();
 }
 r[11]=ai_sx((uint16_t)r[7]);r[16]=(r[16]&~31u)|ai_nz32(r[11]);
 return 3;
invalid:
 r[0]=ai_sx((uint16_t)r[7])*206u;r[8]=0x49d6cu;AIW16(r[8]+r[0],0);r[16]=(r[16]&~31u)|x|4u;return 0;
}
