#include "biwn_resources.h"
struct resources {struct biwn_world_bus *bus;uint32_t remaining;};
#define R16(a,v) do {if(s.bus->read16(s.bus->context,(a),&(v)))return BIWN_RESOURCE_BUS_ERROR;}while(0)
#define R32(a,v) do {if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_RESOURCE_BUS_ERROR;}while(0)
#define W16(a,v) do {if(s.bus->write16(s.bus->context,(a),(uint16_t)(v)))return BIWN_RESOURCE_BUS_ERROR;}while(0)
#define W32(a,v) do {if(s.bus->write32(s.bus->context,(a),(uint32_t)(v)))return BIWN_RESOURCE_BUS_ERROR;}while(0)
#define CALL(a,p,n) do {if(s.bus->call(s.bus->context,(a),(p),(n),&d0))return BIWN_RESOURCE_DEPENDENCY_ERROR;}while(0)
#define STEP() do {if(!s.remaining)return BIWN_RESOURCE_WORK_LIMIT;--s.remaining;}while(0)
static uint32_t sx16(uint16_t value){return(uint32_t)(value&0x7fffu)-(uint32_t)(value&0x8000u);}
static int greater_signed(uint32_t a,uint32_t b){return(a^0x80000000u)>(b^0x80000000u);}
enum biwn_resource_status biwn_resource_get(struct biwn_world_bus *bus,uint16_t id,uint32_t budget,uint32_t *out_D0)
{
 struct resources s={bus,budget};uint32_t d0,offset=sx16(id)*12u,entry,i,p[5],value;uint16_t word;
 if(!bus||!out_D0||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_RESOURCE_BAD_ARGUMENT;
 R32(0x464d0u+offset,value);if(!value){*out_D0=0;return BIWN_RESOURCE_OK;}
 for(i=0;i<50;i++){
  STEP();d0=i*12u;entry=0x15b534u+d0;R16(entry,word);
  if(word==id){
   R16(entry+6u,word);
   if(word){
    R16(entry+6u,word);W16(entry+6u,(uint16_t)(word+1u));R16(entry+8u,word);
    if(!word)do{STEP();p[0]=1;CALL(0xdf8cu,p,1);R16(entry+8u,word);}while(!word);
    R32(entry+2u,d0);*out_D0=d0;return BIWN_RESOURCE_OK;
   }
  }
 }
 d0=49u*12u;
 for(i=0;i<50;i++){
  STEP();entry=0x15b534u+i*12u;R16(entry+6u,word);
  if(!word){
   R32(0x464d8u+offset,p[0]);CALL(0x152a2u,p,1);W32(entry+2u,d0);
   if(!d0){*out_D0=0;return BIWN_RESOURCE_OK;}
   W16(entry+8u,0);W16(entry,id);W16(entry+6u,1);
   p[4]=entry+8u;R32(0x464d8u+offset,p[3]);R32(entry+2u,p[2]);R32(0x464d4u+offset,p[1]);R32(0x464d0u+offset,p[0]);CALL(0x1b044u,p,5);
   R16(entry+6u,word);if(word!=1u){p[0]=1;CALL(0xdf9cu,p,1);}
   R32(entry+2u,d0);*out_D0=d0;return BIWN_RESOURCE_OK;
  }
 }
 *out_D0=0;return BIWN_RESOURCE_OK;
}
enum biwn_resource_status biwn_resource_release(struct biwn_world_bus *bus,uint16_t id,uint32_t budget,uint32_t *out_D0)
{
 struct resources s={bus,budget};uint32_t d0=0,i,entry,p[1];uint16_t word;
 if(!bus||!out_D0||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->call)return BIWN_RESOURCE_BAD_ARGUMENT;
 for(i=0;i<50;i++){
  STEP();d0=i*12u;entry=0x15b534u+d0;R16(entry,word);
  if(word==id){R16(entry+6u,word);word=(uint16_t)(word-1u);W16(entry+6u,word);
   if(!word){W16(entry,0xffffu);R32(entry+2u,p[0]);CALL(0x1545cu,p,1);}
  }
 }
 *out_D0=d0;return BIWN_RESOURCE_OK;
}
static enum biwn_resource_status load(struct biwn_world_bus *bus,uint32_t offset,uint32_t tag,
 uint32_t handle,uint32_t size,uint32_t completion,uint32_t budget,uint32_t *out_D0,int word_scan)
{
 struct resources s={bus,budget};uint32_t d0=0,p[3],end=0x1c8000u+size,source,value;uint16_t word;
 if(!bus||!out_D0||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_RESOURCE_BAD_ARGUMENT;
 R16(0x47b82u,word);
 if(word)do{STEP();CALL(0xdf60u,p,0);R16(0x47b82u,word);}while(word);
 R16(0x47b80u,word);
 while(word){STEP();CALL(0xdf60u,p,0);R16(0x47b80u,word);}
 W16(0x47b80u,1);
retry:
 STEP();W32(0x1126a0u,0);p[0]=2;p[1]=offset;CALL(0xd206u,p,2);
 p[0]=0x1c0000u;p[1]=end;p[2]=d0;CALL(0xd2f0u,p,3);W32(0x1126a0u,0);W32(0xbd848u,0);
 R32(0xbd848u,value);
 if(end>value)do{STEP();CALL(0xdf60u,p,0);R32(0xbd848u,value);}while(end>value);
 source=0x1c0000u;CALL(0xd306u,p,0);
scan_start:
 STEP();R32(source,value);source+=4u;if(value==tag)goto marker;
 if(word_scan){
  /* Isolated18byte1B0EE repair: overlap failed probes by one word, then
   * unsignedCMPA/BCS against1C7FFF. Matched16-longword runs stay intact. */
  source-=2u;
  if(source<0x1c7fffu)goto scan_start;
  W32(0xbd848u,0);goto retry;
 }
scan_next:
 STEP();d0=0x1c7fffu;
 if(greater_signed(source,d0)){W32(0xbd848u,0);goto retry;}
 R32(source,value);source+=4u;if(value!=tag)goto scan_next;
marker:
 d0=1;
 do{STEP();R32(source,value);source+=4u;if(value!=tag)goto scan_start;d0++;}while(d0<=15u);
 if(greater_signed(source,0x1c8000u))goto retry;
 if(!handle){*out_D0=source;return BIWN_RESOURCE_OK;}
 p[2]=size;R32(handle,p[1]);p[0]=source;CALL(0xe3e0u,p,3);W16(0x47b80u,0);
 if(completion)W16(completion,1);
 *out_D0=0;return BIWN_RESOURCE_OK;
}
enum biwn_resource_status biwn_resource_load(struct biwn_world_bus *bus,uint32_t offset,uint32_t tag,
 uint32_t handle,uint32_t size,uint32_t completion,uint32_t budget,uint32_t *out_D0)
{return load(bus,offset,tag,handle,size,completion,budget,out_D0,0);}
enum biwn_resource_status biwn_resource_load_word_scan(struct biwn_world_bus *bus,uint32_t offset,uint32_t tag,
 uint32_t handle,uint32_t size,uint32_t completion,uint32_t budget,uint32_t *out_D0)
{return load(bus,offset,tag,handle,size,completion,budget,out_D0,1);}
enum biwn_resource_status biwn_resource_textures(struct biwn_world_bus *bus,uint16_t mode,uint32_t scratch,uint32_t *out_D0)
{
 struct resources s={bus,0};uint32_t d0=0,i,p[5],value;
 if(!bus||!out_D0||!bus->read32||!bus->write16||!bus->write32||!bus->call||(mode==1u&&!scratch))return BIWN_RESOURCE_BAD_ARGUMENT;
 W16(0x15b532u,0);
 for(i=0;i<36;i++){W32(0x4674cu+i*8u,0x1134a0u+i*8192u);W32(0x46750u+i*8u,0x33020u);d0=i*4u;W16(0x15b4a0u+d0,0xffffu);W16(0x15b4a2u+d0,0);}
 W16(0x15b530u,mode);
 if(mode==1u){R32(0x4674cu,value);W32(scratch,value);p[0]=0xe3adc0u;p[1]=0x52545854u;p[2]=scratch;p[3]=0x1e000u;p[4]=0;CALL(0x1b044u,p,5);W16(0x15b532u,15);}
 *out_D0=d0;return BIWN_RESOURCE_OK;
}
