#include "biwn_texture_cache.h"
struct state{struct biwn_world_bus *bus;uint32_t remaining;};
#define R16(a,v) do{if(s.bus->read16(s.bus->context,(a),&(v)))return BIWN_TEXTURE_BUS_ERROR;}while(0)
#define R32(a,v) do{if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_TEXTURE_BUS_ERROR;}while(0)
#define W16(a,v) do{if(s.bus->write16(s.bus->context,(a),(uint16_t)(v)))return BIWN_TEXTURE_BUS_ERROR;}while(0)
#define W32(a,v) do{if(s.bus->write32(s.bus->context,(a),(uint32_t)(v)))return BIWN_TEXTURE_BUS_ERROR;}while(0)
#define STEP() do{if(!s.remaining)return BIWN_TEXTURE_WORK_LIMIT;--s.remaining;}while(0)
static uint32_t sx(uint16_t w){return(uint32_t)(w&0x7fffu)-(uint32_t)(w&0x8000u);}
static int less(uint16_t a,uint16_t b){return(a^0x8000u)<(b^0x8000u);}
static uint32_t divide(uint16_t n,uint16_t d){int32_t a=(int32_t)sx(n),b=(int32_t)sx(d),q=a/b,r=a%b;return((uint32_t)(uint16_t)r<<16)|(uint16_t)q;}
enum biwn_texture_status biwn_texture_lookup(struct biwn_world_bus *bus,uint16_t id,uint32_t budget,uint32_t *out_D0)
{
 struct state s={bus,budget};uint16_t i,w;uint32_t d0;
 if(!bus||!out_D0||!bus->read16)return BIWN_TEXTURE_BAD_ARGUMENT;
 for(i=0;i<36;i++){STEP();d0=sx(i)*4u;R16(0x15b4a0u+d0,w);if(w==id){*out_D0=(d0&0xffff0000u)|i;return BIWN_TEXTURE_OK;}}
 *out_D0=0;return BIWN_TEXTURE_OK;
}
enum biwn_texture_status biwn_texture_acquire(struct biwn_world_bus *bus,uint16_t id,
 uint32_t scratch,uint32_t incoming_D0,uint32_t budget,uint32_t *out_D0)
{
 struct state s={bus,budget};uint16_t mode,relative,group,start,slot,limit,w,j;uint32_t d0=incoming_D0,offset_base,tag_base,offset,p[5],source_seed,size,pointer;
 if(!bus||!out_D0||!scratch||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_TEXTURE_BAD_ARGUMENT;
 R16(0x15b530u,mode);d0=(d0&0xffff0000u)|mode;
 if(less(3,mode)||less(mode,1))goto missing;
 d0=sx(mode);R16(0x464c8u+d0*2u,w);relative=(uint16_t)(id-w);R16(0x464a0u+d0*2u,group);d0*=4u;
 R32(0x464a8u+d0,offset_base);R32(0x464b8u+d0,tag_base);
 if(relative&0x8000u)goto missing;
 R16(0x15b532u,start);slot=start;limit=(uint16_t)(36u-group);d0=(uint16_t)(36u-group);
 if(less(slot,limit)){
  do{
   STEP();d0=sx(slot)*4u;R16(0x15b4a0u+d0,w);
   if(w==id){
    for(j=0;less(j,group);j=(uint16_t)(j+1u)){STEP();d0=sx((uint16_t)(slot+j))*4u;R16(0x15b4a2u+d0,w);W16(0x15b4a2u+d0,w+1u);}
    goto found;
   }
   slot=(uint16_t)(slot+group);
  }while(less(slot,limit));
 }
 if(!group)return BIWN_TEXTURE_DIVISION_BY_ZERO;
 d0=divide(relative,group);tag_base+=sx((uint16_t)d0);
 R16(0x15b532u,start);slot=start;limit=(uint16_t)(36u-group);d0=(uint16_t)(36u-group);
 if(less(slot,limit)){
  source_seed=sx(relative)<<13;size=sx(group)<<13;
  do{
   STEP();d0=sx(slot)*4u;R16(0x15b4a0u+d0,w);if(w==0xffffu)goto load;
   slot=(uint16_t)(slot+group);d0=(uint16_t)(36u-group);
  }while(less(slot,limit));
 }
 R16(0x15b532u,start);slot=start;limit=(uint16_t)(36u-group);d0=(uint16_t)(36u-group);
 if(!less(slot,limit))goto missing;
 source_seed=sx(relative)<<13;size=sx(group)<<13;
 do{
  STEP();d0=sx(slot)*4u;R16(0x15b4a2u+d0,w);if(!w)goto load;
  slot=(uint16_t)(slot+group);d0=(uint16_t)(36u-group);
 }while(less(slot,limit));
 goto missing;
load:
 d0=divide(relative,group);d0=(d0&0xffff0000u)|(uint16_t)((uint16_t)d0<<6);offset=source_seed+sx((uint16_t)d0)+offset_base;
 d0=sx(slot)*8u;R32(0x4674cu+d0,pointer);W32(scratch,pointer);
 /* descriptor data pointer is supplied through original private A6-4. */
 p[4]=0;p[3]=size;p[2]=scratch;p[1]=tag_base;p[0]=offset;
 if(bus->call(bus->context,0x1b044u,p,5,&d0))return BIWN_TEXTURE_DEPENDENCY_ERROR;
 for(j=0;less(j,group);j=(uint16_t)(j+1u)){STEP();d0=sx((uint16_t)(slot+j))*4u;W16(0x15b4a0u+d0,(uint16_t)(id+j));W16(0x15b4a2u+d0,1);}
found:
 *out_D0=(d0&0xffff0000u)|slot;return BIWN_TEXTURE_OK;
missing:
 *out_D0=0xffffffffu;return BIWN_TEXTURE_OK;
}
