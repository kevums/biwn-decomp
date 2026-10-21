#include "biwn_overlay.h"
#define R8(a,v) do{if(bus->read8(bus->context,(a),&(v)))return BIWN_OVERLAY_BUS_ERROR;}while(0)
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_OVERLAY_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_OVERLAY_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_OVERLAY_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_OVERLAY_BUS_ERROR;}while(0)
#define CALL(a,p,n) do{if(bus->call(bus->context,(a),(p),(n),&d0))return BIWN_OVERLAY_DEPENDENCY_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t shift6(uint32_t v){return(v>>6)|(v&0x80000000u?0xfc000000u:0u);}
/* Preserve the source's Yword/Xword rereads and ADD.L (rather than OR)
 * so a negative signed X offset can borrow from the packed Y field. */
static enum biwn_overlay_status marker_xy(struct biwn_world_bus *bus,uint32_t y_address,uint32_t x_address)
{
 uint16_t y,x;uint32_t xy;
 R16(y_address,y);y=(uint16_t)(y-8u);R16(x_address,x);x=(uint16_t)(x-16u);
 xy=((uint32_t)y<<16)+(sx16(x)<<1);W32(0xf0220cu,xy);return BIWN_OVERLAY_OK;
}
enum biwn_overlay_status biwn_overlay(struct biwn_world_bus *bus,uint32_t scratch,uint32_t incoming,uint32_t *result)
{
 uint32_t d0=incoming,d1,format,params[8],value;uint16_t word,cached,sector;uint8_t byte;enum biwn_overlay_status status;
 if(!bus||!result||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_OVERLAY_BAD_ARGUMENT;
 R16(0x4451cu,word);
 if(word){
  W32(0xf02268u,0);W32(0xf0226cu,0);W32(0xf02200u,0xb29d0u);W32(0xf02204u,0x14600u);
  status=marker_xy(bus,0x44518u,0x4451au);if(status)return status;
  W32(0xf02210u,0x180u);W32(0xf0223cu,0xf0040u);W32(0xf02238u,0x10010208u);
 }
 R16(0x49d6au,word);W16(0x44518u,word);R16(0x49d68u,word);W16(0x4451au,word);R16(0x49d5cu,word);W16(0x4451cu,word);
 if(word){
  W32(0xf02200u,0xb29d0u);W32(0xf02204u,0x14600u);status=marker_xy(bus,0x49d6au,0x49d68u);if(status)return status;
  W32(0xf02210u,0x1ffc0u);R16(0x49d5eu,word);W32(0xf02224u,word?0x444a0u:0x44428u);
  W32(0xf02228u,0x13000u);W32(0xf02230u,0);W32(0xf0223cu,0xf0040u);W32(0xf02238u,0x11800209u);
 }
 R16(0x113060u,word);
 if(!word){
  W32(0xf02200u,0xb29d0u);W32(0xf02204u,0x12620u);W32(0xf0220cu,0x40010u);W32(0xf02210u,0x12u);
  W32(0xf02224u,0x44000u);W32(0xf02228u,0x11a20u);W32(0xf02230u,0);W32(0xf0223cu,0x12000au);
  W32(0xf02238u,0x1800201u);W16(0x113060u,1);
 }
 W32(0xf02200u,0xb29d0u);W32(0xf02204u,0x14600u);W32(0xf0220cu,0x90102u);W32(0xf02210u,0x124u);
 W32(0xf02224u,0x44168u);W32(0xf02228u,0x14800u);R8(0x49cbau,byte);d0=(0xb0u-byte)&0xfeu;
 W32(0xf02230u,d0);W32(0xf02234u,0x164u);W32(0xf0223cu,0xb009cu);W32(0xf02238u,0x1800609u);
 R32(0x49c50u,value);d0=shift6(value);R16(0x4451eu,cached);
 if((uint16_t)d0==cached){
  R32(0x49c56u,value);d0=shift6(value);R16(0x44520u,cached);
  if((uint16_t)d0==cached){R16(0x49c62u,word);R16(0x44522u,cached);if(word==cached){*result=d0;return BIWN_OVERLAY_OK;}}
 }
 R32(0x49c50u,d0);d1=shift6(d0);W16(0x4451eu,d1);R32(0x49c56u,d0);d0=shift6(d0);W16(0x44520u,d0);
 R16(0x49c62u,word);W16(0x44522u,word);format=word&0x8000u?0x181dau:0x181e9u;
 R16(0x44522u,sector);sector=(uint16_t)(word&0x8000u?0u-sector:sector+1u);
 params[0]=scratch;params[1]=format;params[2]=d1&0xffffu;params[3]=d0&0xffffu;params[4]=sector;
 CALL(0x1b45au,params,5);
 W32(0xf02268u,0);W32(0xf0226cu,0);W32(0xf02200u,0xb29d0u);W32(0xf02204u,0x2620u);W32(0xf02210u,0x13u);
 W32(0xf0220cu,0x40002u);W32(0xf0223cu,0x70009u);W32(0xf02238u,0x10200u);
 params[0]=22;params[1]=2;params[2]=scratch;params[3]=0xb29d0u;params[4]=0x3e08u;params[5]=0x4c3e0u;params[6]=3;params[7]=2;
 CALL(0x149aeu,params,8);*result=d0;return BIWN_OVERLAY_OK;
}
