#include "biwn_render_scene.h"
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_RENDER_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_RENDER_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_RENDER_BUS_ERROR;}while(0)
#define CALL(a,p,n) do{if(bus->call(bus->context,(a),(p),(n),&d0))return BIWN_RENDER_DEPENDENCY_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
enum biwn_render_status biwn_render_clear(struct biwn_world_bus *bus,uint32_t destination,uint32_t pattern,uint32_t budget)
{
 uint32_t value;
 if(!bus||!bus->read32||!bus->write32||!budget)return BIWN_RENDER_BAD_ARGUMENT;
 do{if(!budget--)return BIWN_RENDER_WORK_LIMIT;R32(0xf02238u,value);}while(!(value&1u));
 W32(0xf02268u,pattern);W32(0xf0226cu,pattern);W32(0xf02200u,destination);
 W32(0xf02204u,0x3e20u);W32(0xf0220cu,0);W32(0xf02210u,0x1ff20u);
 W32(0xf0223cu,0xb400e0u);W32(0xf02238u,0x10200u);return BIWN_RENDER_OK;
}
enum biwn_render_status biwn_render_rotate(struct biwn_world_bus *bus,uint32_t incoming,uint32_t *result)
{
 uint32_t d0=incoming,value,params[2]={0x43da0u,0x777c0u};
 if(!bus||!result||!bus->read32||!bus->write32||!bus->call)return BIWN_RENDER_BAD_ARGUMENT;
 R32(0xbd83cu,d0);R32(0xbd840u,value);W32(0xbd83cu,value);
 R32(0xbd844u,value);W32(0xbd840u,value);W32(0xbd844u,d0);
 R32(0xbd830u,d0);R32(0xbd834u,value);W32(0xbd830u,value);
 R32(0xbd838u,value);W32(0xbd834u,value);W32(0xbd838u,d0);
 R32(0xbd830u,value);W32(0x43daau,value);
 CALL(0x185b2u,params,2);*result=d0;return BIWN_RENDER_OK;
}
static enum biwn_render_status finish_draw(struct biwn_world_bus *bus,uint32_t *d0,uint32_t *budget)
{
 uint32_t value;
 if(bus->call(bus->context,0xe19eu,0,0,d0)||bus->call(bus->context,0xe202u,0,0,d0))return BIWN_RENDER_DEPENDENCY_ERROR;
 do{if(!(*budget)--)return BIWN_RENDER_WORK_LIMIT;if(bus->read32(bus->context,0x10a684u,&value))return BIWN_RENDER_BUS_ERROR;}while(value);
 if(bus->call(bus->context,0xe098u,0,0,d0))return BIWN_RENDER_DEPENDENCY_ERROR;
 return BIWN_RENDER_OK;
}
enum biwn_render_status biwn_render_scene(struct biwn_world_bus *bus,uint32_t budget,uint32_t incoming,uint32_t *result)
{
 uint32_t d0=incoming,params[2],value,index;uint16_t mode,word,count;enum biwn_render_status status;
 if(!bus||!result||!budget||!bus->read16||!bus->read32||!bus->write32||!bus->call)return BIWN_RENDER_BAD_ARGUMENT;
 R16(0x49c60u,mode);if(!mode){*result=d0;return BIWN_RENDER_OK;}
 R32(0xbd83cu,params[0]);params[1]=0;CALL(0xe03au,params,2);W32(0x49b88u,0);
 R16(0x49c60u,mode);
 if(mode==1){
  CALL(0xe0a6u,0,0);CALL(0x170a0u,0,0);R32(0x49b88u,value);
  if(value){status=finish_draw(bus,&d0,&budget);if(status)return status;}
 }else{
  R16(0x49c60u,mode);
  if(mode==2){
   R16(0x49c76u,word);W32(0x49c1cu,sx16(word));CALL(0xe0f2u,0,0);count=0;
   R32(0x10d688u,value);
   if(value!=0xffffu)for(;;){
    if(!budget--)return BIWN_RENDER_WORK_LIMIT;
    d0=sx16((uint16_t)(count+1u))<<2;R32(0x10d688u+d0,value);if(!value)break;
    index=sx16(count)<<2;d0=index;R32(0x10d688u+index,value);W32(0x49c1cu,value);
    CALL(0xe148u,0,0);CALL(0x170a0u,0,0);R32(0x49b88u,value);
    if(value){status=finish_draw(bus,&d0,&budget);if(status)return status;}
    count=(uint16_t)(count+2u);d0=sx16(count)<<2;R32(0x10d688u+d0,value);if(value==0xffffu)break;
   }
  }else{R16(0x49c60u,mode);if(mode==3)W32(0x49b88u,0);}
 }
 CALL(0x17f14u,0,0);*result=d0;return BIWN_RENDER_OK;
}
