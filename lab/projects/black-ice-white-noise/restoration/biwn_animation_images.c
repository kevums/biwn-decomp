#include "biwn_animation_images.h"
#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_IMAGES_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_IMAGES_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_IMAGES_BUS_ERROR;}while(0)
#define W8(a,v) do {if(write8(bus->context,(a),(uint8_t)(v)))return BIWN_IMAGES_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_IMAGES_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_IMAGES_BUS_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static int less16(uint16_t a,uint16_t b){return(a^0x8000u)<(b^0x8000u);}
enum biwn_animation_images_status biwn_animation_images_reset(struct biwn_world_bus *bus)
{
 if(!bus||!bus->write16)return BIWN_IMAGES_BAD_ARGUMENT;
 W16(0x112940u,0);return BIWN_IMAGES_OK;
}
enum biwn_animation_images_status biwn_animation_images_consume(struct biwn_world_bus *bus,
 biwn_input_write8 write8,uint32_t work_budget,uint32_t incoming_d0,uint32_t *out_d0)
{
 uint32_t d0=incoming_d0,row,handle,model,output,frame,offset,pointer,value,params[3];
 uint16_t count,index=0;uint8_t width,height,byte;
 if(!bus||!write8||!out_d0||!work_budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_IMAGES_BAD_ARGUMENT;
 R16(0x112940u,count);
 if(less16(0,count))do{
  if(!work_budget--)return BIWN_IMAGES_WORK_LIMIT;
  row=0x1126c0u+sx16(index)*16u;
  R32(row,handle);R32(handle,model);R32(row+8u,handle);R32(handle,output);
  R32(row+4u,frame);R32(model+12u+(frame<<2),offset);pointer=model+offset;
  R8(pointer,width);R8(pointer+1u,height);W32(output+8u,((uint32_t)width<<16)+height);
  R32(row+12u,value);if(value){R8(output+8u,byte);W8(output+8u,byte|0x80u);}
  R8(pointer,width);d0=(uint32_t)width*4u;R32(0x3bd20u+d0,value);W32(output+12u,value);
  /* These are original rereads after header preparation, not cached
   * handles/indices from the beginning of the request. */
  R32(row+8u,handle);R32(handle,value);params[2]=value+16u;
  R32(row+4u,params[1]);R32(row,handle);R32(handle,params[0]);
  if(bus->call(bus->context,0xe2b8u,params,3,&d0))return BIWN_IMAGES_DEPENDENCY_ERROR;
  index=(uint16_t)(index+1u);R16(0x112940u,count);
 }while(less16(index,count));
 W16(0x112940u,0);*out_d0=d0;return BIWN_IMAGES_OK;
}
