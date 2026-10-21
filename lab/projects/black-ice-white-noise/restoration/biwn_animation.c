#include "biwn_animation.h"
#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_ANIMATION_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_ANIMATION_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_ANIMATION_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_ANIMATION_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_ANIMATION_BUS_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint16_t sx8(uint8_t v){return(uint16_t)((uint16_t)(v&0x7fu)-(uint16_t)(v&0x80u));}
static int positive(uint16_t v){return v && !(v&0x8000u);}

enum biwn_animation_status biwn_animation_enqueue(struct biwn_world_bus *bus,
 uint32_t model,uint32_t frame,uint32_t pose,uint32_t flip,
 uint32_t incoming_d0,uint32_t *out_d0)
{
 uint16_t count;uint32_t pointer;
 if(!bus||!out_d0||!bus->read16||!bus->write16||!bus->write32)return BIWN_ANIMATION_BAD_ARGUMENT;
 R16(0x112940u,count);
 if(!(count&0x8000u)&&count>39u){*out_d0=incoming_d0&0xffff0000u;return BIWN_ANIMATION_OK;}
 R16(0x112940u,count);pointer=0x1126c0u+sx16(count)*16u;
 W32(pointer+4u,frame);W32(pointer,model);W32(pointer+8u,pose);W32(pointer+12u,flip);
 R16(0x112940u,count);W16(0x112940u,(uint32_t)count+1u);
 *out_d0=1;return BIWN_ANIMATION_OK;
}

static enum biwn_animation_status emit(struct biwn_world_bus *bus,
 uint32_t object,uint32_t pointer,int reread_pointer,uint32_t *value)
{
 uint32_t d0=*value,params[4];uint8_t byte;
 R8(object+0xcau,byte);d0=((d0&0xffffff00u)|byte)>>7;params[3]=d0&1u;
 R32(object+0x5eu,params[2]);
 if(reread_pointer)R32(object+0x64u,pointer);
 R8(pointer,byte);d0=(d0&0xffff0000u)|sx8(byte);params[1]=sx16(sx8(byte));
 R32(object+0x58u,params[0]);
 if(bus->call(bus->context,0xeac4u,params,4,&d0))return BIWN_ANIMATION_DEPENDENCY_ERROR;
 *value=d0;return BIWN_ANIMATION_OK;
}

enum biwn_animation_status biwn_animation_update(struct biwn_world_bus *bus,
 uint32_t object,uint32_t incoming_d0,uint32_t work_budget,uint32_t *out_d0)
{
 uint32_t d0=incoming_d0,pending,pointer,offset;uint16_t word,delta;uint8_t step,duration,frame,next_frame;
 enum biwn_animation_status status;
 if(!bus||!out_d0||!work_budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_ANIMATION_BAD_ARGUMENT;
 R32(object+0x68u,pending);
 if(pending){
  R16(object+0xcau,word);if(word&0x8000u)word=(uint16_t)(0u-word);d0=sx16(word)*4u;
  R32(object+0x68u,pending);pointer=pending+d0-4u;W32(object+0x64u,pointer);W32(object+0x68u,0);
  R32(object+0x64u,pointer);R8(pointer+1u,duration);W16(object+0x62u,sx8(duration));
  status=emit(bus,object,0,1,&d0);if(status)return status;
  if((uint16_t)d0)W16(object+0xccu,0);
  *out_d0=d0;return BIWN_ANIMATION_OK;
 }
 R16(object+0x62u,word);R16(0x4c24eu,delta);word=(uint16_t)((uint32_t)word-delta);d0=(d0&0xffff0000u)|word;W16(object+0x62u,word);
 if(positive(word)){
  R16(object+0xccu,word);
  if(!word){*out_d0=d0;return BIWN_ANIMATION_OK;}
  status=emit(bus,object,0,1,&d0);if(status)return status;
  if((uint16_t)d0)W16(object+0xccu,0);
  *out_d0=d0;return BIWN_ANIMATION_OK;
 }
 for(;;){
  if(!work_budget--)return BIWN_ANIMATION_WORK_LIMIT;
  R32(object+0x64u,pointer);R8(pointer+3u,step);offset=sx16(sx8(step))*4u;d0=offset;
  R8(pointer+offset+1u,duration);d0=(d0&0xffff0000u)|sx8(duration);
  R16(object+0x62u,word);W16(object+0x62u,(uint32_t)word+(uint16_t)d0);
  R32(object+0x64u,pointer);R8(pointer+3u,step);d0=sx16(sx8(step))*4u;
  R8(pointer,frame);R8(pointer+d0,next_frame);
  if(frame==next_frame){R16(object+0xccu,word);if(!word){R32(object+0x64u,pointer);W32(object+0x64u,pointer+d0);goto check_timer;}}
  R32(object+0x64u,pointer);pointer+=d0;W32(object+0x64u,pointer);
  status=emit(bus,object,pointer,0,&d0);if(status)return status;
  if((uint16_t)d0)W16(object+0xccu,0);
check_timer:
  R16(object+0x62u,word);if(positive(word)){*out_d0=d0;return BIWN_ANIMATION_OK;}
 }
}
