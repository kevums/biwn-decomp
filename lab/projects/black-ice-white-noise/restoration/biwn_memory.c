#include "biwn_memory.h"
struct memory {struct biwn_world_bus *bus;uint32_t remaining;};
#define R32(a,v) do {if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_MEMORY_BUS_ERROR;}while(0)
#define W32(a,v) do {if(s.bus->write32(s.bus->context,(a),(uint32_t)(v)))return BIWN_MEMORY_BUS_ERROR;}while(0)
#define STEP() do {if(!s.remaining)return BIWN_MEMORY_WORK_LIMIT;--s.remaining;}while(0)
static int greater_signed(uint32_t a,uint32_t b){return(a^0x80000000u)>(b^0x80000000u);}
static uint32_t asr1(uint32_t v){return(v>>1)|(v&0x80000000u);}
enum biwn_memory_status biwn_memory_allocate(struct biwn_world_bus *bus,uint32_t requested,uint32_t budget,uint32_t *out_D0)
{
 struct memory s={bus,budget};uint32_t size=(requested+15u)&0xfffffff8u,block,previous=0,value,left,d0,index,params[1];
 int from_head=1,compacted=0;
 if(!bus||!out_D0||!budget||!bus->read32||!bus->write32||!bus->call)return BIWN_MEMORY_BAD_ARGUMENT;
 R32(0x112d60u,block);
check_block:
 STEP();R32(block,value);
 if(greater_signed(size,value)){
  if(compacted){d0=0;goto finish;}
  previous=block;R32(block+4u,block);
  while(block){
   STEP();R32(block,value);
   if(!greater_signed(size,value)){from_head=0;goto fit;}
   previous=block;R32(block+4u,block);
  }
  d0=0; /* Original D0 is not used after the compaction call. */
  if(bus->call(bus->context,0x15200u,params,0,&d0))return BIWN_MEMORY_DEPENDENCY_ERROR;
  R32(0x112d60u,block);from_head=1;compacted=1;goto check_block;
 }
fit:
 R32(block,left);left-=size;
 if(greater_signed(left,15u)){
  W32(block,left);block+=left;W32(block,size);
 }else{
  R32(block+4u,value);
  if(from_head)W32(0x112d60u,value);else W32(previous+4u,value);
 }
 for(index=255u;;index--){
  STEP();R32(0x112960u+index*4u,value);
  if(!value)break;
  if(!index){d0=0;goto finish;}
 }
 W32(0x112960u+index*4u,block+8u);d0=0x112960u+index*4u;W32(block+4u,d0);
 R32(block,value);R32(0x112d64u,left);W32(0x112d64u,left-value);
finish:
 *out_D0=d0;return BIWN_MEMORY_OK;
}
enum biwn_memory_status biwn_memory_compact(struct biwn_world_bus *bus,uint32_t budget,uint32_t *out_D0)
{
 struct memory s={bus,budget};uint32_t destination,source,size,value,handle,d0=0x1bffffu,args[3];
 if(!bus||!out_D0||!budget||!bus->read32||!bus->write32||!bus->call)return BIWN_MEMORY_BAD_ARGUMENT;
 R32(0x112d60u,destination);R32(destination,size);source=destination+size;
 if(source>0x1bffffu)goto tail;
move_block:
 STEP();R32(source,size);args[0]=source;args[1]=destination;args[2]=size;
 if(bus->call(bus->context,0xe3e0u,args,3,&d0))return BIWN_MEMORY_DEPENDENCY_ERROR;
 R32(destination+4u,handle);W32(handle,destination+8u);R32(destination,value);source+=value;
 if(source>0x1bffffu)goto next_destination;
 R32(source+4u,value);if(value>=0x15edc0u)goto skip_block;
 R32(source+4u,value);if(value)goto next_destination;
 R32(source,value);source+=value;
 if(source>0x1bffffu)goto next_destination;
 R32(source+4u,value);if(value>=0x15edc0u)goto skip_block;
 R32(source+4u,value);if(value)goto next_destination;
skip_block:
 STEP();R32(source,value);source+=value;
 if(source>0x1bffffu)goto next_destination;
 R32(source+4u,value);if(value>=0x15edc0u)goto skip_block;
 /* The original rereads this field after its compare. */
 R32(source+4u,value);if(!value)goto skip_block;
next_destination:
 destination+=size;if(source<=0x1bffffu)goto move_block;
tail:
 W32(destination,0x1c0000u-destination);W32(destination+4u,0);W32(destination+8u,0);W32(0x112d60u,destination);
 *out_D0=d0;return BIWN_MEMORY_OK;
}
enum biwn_memory_status biwn_memory_copy(struct biwn_world_bus *bus,biwn_memory_write8 write8,
 uint32_t entry,uint32_t arg0,uint32_t arg1,uint32_t count,uint32_t incoming_D0,uint32_t budget,uint32_t *out_D0)
{
 struct memory s={bus,budget};uint32_t source,destination,d0=incoming_D0,chunk,aligned,source_offset,destination_offset;uint8_t byte;
 if(!bus||!out_D0||!budget||!bus->read8||!bus->write32||!write8||(entry!=0xe3e0u&&entry!=0xe3eeu))return BIWN_MEMORY_BAD_ARGUMENT;
 source=entry==0xe3e0u?arg0:arg1;destination=entry==0xe3e0u?arg1:arg0;
 if(!count)goto finish;
 /* Original BMI observes the wrapped subtraction N flag, not signed LT. */
 if((count-128u)&0x80000000u){
  do{
   STEP();if(bus->read8(bus->context,source++,&byte))return BIWN_MEMORY_BUS_ERROR;
   if(write8(bus->context,destination++,byte))return BIWN_MEMORY_BUS_ERROR;
  }while(--count);
 }else{
  d0=0x4020u;W32(0xf02204u,d0);W32(0xf02228u,d0);
  do{
   STEP();chunk=count;if(!((chunk-0x10000u)&0x80000000u))chunk=0x10000u;
   count-=chunk;d0=asr1(chunk)|0x10000u;W32(0xf0223cu,d0);
   aligned=destination&0xfffffff8u;destination_offset=asr1(destination-aligned);destination+=chunk;
   W32(0xf02200u,aligned);W32(0xf0220cu,destination_offset);
   aligned=source&0xfffffff8u;source_offset=asr1(source-aligned);source+=chunk;
   W32(0xf02224u,aligned);W32(0xf02230u,source_offset);
   d0=greater_signed(source_offset,destination_offset)?0x1800005u:0x1800001u;W32(0xf02238u,d0);
  }while(count);
 }
finish:
 *out_D0=d0;return BIWN_MEMORY_OK;
}
