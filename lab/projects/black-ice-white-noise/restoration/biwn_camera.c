#include "biwn_camera.h"
#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_CAMERA_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_CAMERA_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_CAMERA_BUS_ERROR;}while(0)
#define W8(a,v) do {if(write8(bus->context,(a),(uint8_t)(v)))return BIWN_CAMERA_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_CAMERA_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_CAMERA_BUS_ERROR;}while(0)
#define CALL(a,args,n) do {if(bus->call(bus->context,(a),(args),(n),&d0))return BIWN_CAMERA_DEPENDENCY_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return (uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint16_t sx8(uint8_t v){return (uint16_t)((uint16_t)(v&0x7fu)-(uint16_t)(v&0x80u));}
static int less32(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}
static int greater16(uint16_t a,uint16_t b){return(a^0x8000u)>(b^0x8000u);}
static uint32_t asr14(uint32_t v){return(v>>14)|((v&0x80000000u)?0xfffc0000u:0);}
uint32_t biwn_multiply32(uint32_t a,uint32_t b){return a*b;}

enum biwn_camera_status biwn_camera_direction(struct biwn_world_bus *bus,
 uint16_t x,uint16_t z,uint32_t incoming_d0,uint32_t *out_d0)
{
 uint32_t d0=incoming_d0,params[2],ratio,threshold;unsigned quadrant,index;
 if(!bus||!out_d0||!bus->read32||!bus->call)return BIWN_CAMERA_BAD_ARGUMENT;
 if(x&0x8000u){x=(uint16_t)(0u-x);if(z&0x8000u){z=(uint16_t)(0u-z);quadrant=2;}else quadrant=1;}
 else if(z&0x8000u){z=(uint16_t)(0u-z);quadrant=3;}else quadrant=4;
 if(!z){index=64;d0=incoming_d0&0xffff0000u;}
 else {
  params[0]=(uint32_t)x<<16;params[1]=sx16(z);CALL(0xe588u,params,2);ratio=d0;
  for(index=0;index<64u;index++){
   d0=index*4u;R32(0x41f00u+d0,threshold);
   if(!less32(threshold,ratio))break;
  }
 }
 if(quadrant==2u)index=(128u-index)&255u;
 else if(quadrant==3u)index=(index+128u)&255u;
 else if(quadrant==4u)index=(0u-index)&255u;
 *out_d0=(d0&0xffff0000u)|(index&255u);return BIWN_CAMERA_OK;
}

enum biwn_camera_status biwn_camera_update(struct biwn_world_bus *bus,
 biwn_input_write8 write8,uint32_t incoming_d2,uint32_t incoming_d3,uint32_t *out_d0)
{
 uint32_t d0=0,d2=incoming_d2,d3=incoming_d3,value,a,b,params[5],x,z;
 uint16_t word,other,angle_word;uint8_t byte,angle;
 if(!bus||!write8||!out_d0||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_CAMERA_BAD_ARGUMENT;
 R8(0x49ba7u,byte);
 if(byte&0x80u){
  R8(0x49ba5u,byte);if(byte&0x10u){R32(0x49b98u,value);value++;W32(0x49b98u,value);R32(0x49b98u,value);if(less32(255u,value))W32(0x49b98u,0);}
  R8(0x49ba5u,byte);if(byte&0x20u){R32(0x49b98u,value);value--;W32(0x49b98u,value);if(value&0x80000000u)W32(0x49b98u,255);}
  R8(0x49ba5u,byte);if(byte&0x40u){R32(0x49b9cu,value);value++;W32(0x49b9cu,value);R32(0x49b9cu,value);if(less32(255u,value))W32(0x49b9cu,0);}
  R8(0x49ba5u,byte);if(byte&0x80u){R32(0x49b9cu,value);value--;W32(0x49b9cu,value);if(value&0x80000000u)W32(0x49b9cu,255);}
  R8(0x49ba5u,byte);if(byte&8u){R32(0x49ba0u,value);value++;W32(0x49ba0u,value);R32(0x49ba0u,value);if(less32(255u,value))W32(0x49ba0u,0);}
  R8(0x49ba7u,byte);if(byte&8u){R32(0x49ba0u,value);value--;W32(0x49ba0u,value);if(value&0x80000000u)W32(0x49ba0u,255);}
  R8(0x49ba5u,byte);if(byte&1u){R16(0x47b9cu,word);W16(0x47b9cu,(uint32_t)word-8u);R16(0x49b8eu,word);W16(0x49b8eu,(uint32_t)word-8u);}
  R8(0x49ba7u,byte);if(byte&1u){R16(0x47b9cu,word);W16(0x47b9cu,(uint32_t)word+8u);R16(0x49b8eu,word);W16(0x49b8eu,(uint32_t)word+8u);}
 }else {
  R16(0x3c840u,word);
  if(greater16(word,120)){W16(0x3c840u,0);}else {R16(0x3c840u,word);W16(0x3c840u,(uint32_t)word+1u);}
  R16(0x3c840u,word);
  if(greater16(word,60)){R16(0x3c840u,word);word=(uint16_t)(word-90u);}
  else {R16(0x3c840u,word);word=(uint16_t)(30u-word);}
  W32(0x3c846u,sx16(word));W32(0x3c846u,27);
  R16(0x49cdcu,word);z=sx16(word);params[0]=z;params[1]=27;CALL(0xe540u,params,2);a=d0;
  R16(0x49cd8u,word);x=sx16(word);R32(0x3c842u,params[1]);params[0]=x;CALL(0xe540u,params,2);d3=asr14(a-d0);
  R32(0x3c842u,params[1]);params[0]=z;CALL(0xe540u,params,2);b=d0;
  params[0]=x;params[1]=27;CALL(0xe540u,params,2);d2=asr14(0u-(b+d0));
  R32(0x49cc0u,value);W32(0x49b98u,value+8u);W32(0x49ba0u,0);
 }
 W16(0x47b9au,d3);R16(0x49ce0u,word);W16(0x47b9cu,word);W16(0x47b9eu,d2);
 R8(0x49cbau,angle);
 if((uint8_t)(angle+0xc0u)>0x80u){
  R16(0x49ce2u,word);params[1]=(uint16_t)((uint32_t)word-(uint16_t)d2);
  R16(0x49cdeu,word);R16(0x47b9au,other);params[0]=(uint16_t)((uint32_t)word-other);
  CALL(0x13440u,params,2);angle_word=sx8((uint8_t)d0);R8(0x49cbau,byte);
  angle_word=(uint16_t)((uint32_t)angle_word+sx8(byte));angle_word=(uint16_t)((angle_word>>1)|((angle_word&0x8000u)?0x8000u:0));W32(0x49b9cu,sx16(angle_word));
 }else {
  R16(0x49ce2u,word);R16(0x47b9eu,other);params[1]=(uint16_t)((uint32_t)word-other);
  R16(0x49cdeu,word);R16(0x47b9au,other);params[0]=(uint16_t)((uint32_t)word-other);
  CALL(0x13440u,params,2);R8(0x49cbau,byte);angle_word=(uint16_t)(((uint32_t)(uint8_t)d0+byte)>>1);W32(0x49b9cu,0);W8(0x49b9fu,angle_word);
 }
 R32(0x49ba0u,params[3]);R32(0x49b9cu,params[2]);R32(0x49b98u,params[1]);params[0]=0x47b88u;params[4]=0;CALL(0xe220u,params,5);
 R32(0x3c846u,d0);*out_d0=d0;return BIWN_CAMERA_OK;
}
