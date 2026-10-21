#include "biwn_rng.h"
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_RNG_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_RNG_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_RNG_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_RNG_BUS_ERROR;}while(0)
#define CALL(a,p,n) do{if(bus->call(bus->context,(a),(p),(n),&d0))return BIWN_RNG_DEPENDENCY_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint16_t asr16(uint16_t v,unsigned n)
{return(uint16_t)((v>>n)|(v&0x8000u?0xffffu<<(16u-n):0u));}
enum biwn_rng_status biwn_rng_remainder(uint32_t numerator,uint32_t denominator,uint32_t *result)
{
 uint32_t q,r;
 if(!result)return BIWN_RNG_BAD_ARGUMENT;
 if(biwn_signed_division(numerator,denominator,&q,&r))return BIWN_RNG_DEPENDENCY_ERROR;
 *result=r;return BIWN_RNG_OK;
}
enum biwn_rng_status biwn_rng_select(struct biwn_world_bus *bus,uint16_t selector,uint32_t incoming,uint32_t *result)
{
 uint32_t d0=incoming,d1;uint16_t old,word;
 if(!bus||!result||!bus->read16||!bus->write16)return BIWN_RNG_BAD_ARGUMENT;
 R16(0x113080u,old);
 if(old>255u){
  d0=sx16(old);d1=(d0<<8)-d0;d1<<=7;d0-=d1;d0>>=16;
  word=(uint16_t)(old+(uint16_t)d0);word=asr16(word,7);
  word=(uint16_t)(word-asr16(old,15));
  d0=(uint16_t)((uint16_t)(word<<8)-word);
  old=(uint16_t)(old-(uint16_t)d0);W16(0x113080u,old);
 }
 W16(0x113080u,selector);*result=d0;return BIWN_RNG_OK;
}
enum biwn_rng_status biwn_rng_get(struct biwn_world_bus *bus,uint32_t *result)
{
 uint16_t selector;uint32_t d0;
 if(!bus||!result||!bus->read16||!bus->read32)return BIWN_RNG_BAD_ARGUMENT;
 R16(0x113080u,selector);d0=sx16(selector)<<2;R32(0x113082u+d0,d0);
 *result=d0;return BIWN_RNG_OK;
}
enum biwn_rng_status biwn_rng_set(struct biwn_world_bus *bus,uint32_t value,uint32_t incoming,uint32_t *result)
{
 uint16_t selector;uint32_t d0=incoming;
 if(!bus||!result||!bus->read16||!bus->write32)return BIWN_RNG_BAD_ARGUMENT;
 if(value-1u<=0x7ffffffdu){R16(0x113080u,selector);d0=sx16(selector)<<2;W32(0x113082u+d0,value);}
 *result=d0;return BIWN_RNG_OK;
}
static enum biwn_rng_status next(struct biwn_world_bus *bus,uint16_t selector,uint32_t q_address,uint32_t r_address,int reread,uint32_t *result)
{
 uint32_t d0=sx16(selector),offset=d0<<2,seed,params[2],value,state;
 R32(0x113082u+offset,seed);R32(q_address,params[1]);params[0]=seed;CALL(0xe60au,params,2);
 /* Literal source shift/add chain equals48271 times the raw remainder,
  * with all intermediates wrapping at32bits. Constants Q/R remain reads. */
 state=d0*48271u;
 R32(q_address,params[1]);params[0]=seed;CALL(0xe588u,params,2);
 params[0]=d0;R32(r_address,params[1]);CALL(0xe540u,params,2);
 state-=d0;W32(0x113082u+offset,state);
 if(!state||(state&0x80000000u)){R32(0x113082u+offset,value);W32(0x113082u+offset,value+0x7fffffffu);}
 if(reread){R16(0x113080u,selector);offset=sx16(selector)<<2;}
 R32(0x113082u+offset,d0);*result=d0;return BIWN_RNG_OK;
}
enum biwn_rng_status biwn_rng_current(struct biwn_world_bus *bus,uint32_t *result)
{
 uint16_t selector;
 if(!bus||!result||!bus->read16||!bus->read32||!bus->write32||!bus->call)return BIWN_RNG_BAD_ARGUMENT;
 R16(0x113080u,selector);return next(bus,selector,0x462e0u,0x462e4u,1,result);
}
enum biwn_rng_status biwn_rng_indexed(struct biwn_world_bus *bus,uint16_t selector,uint32_t *result)
{
 if(!bus||!result||!bus->read32||!bus->write32||!bus->call)return BIWN_RNG_BAD_ARGUMENT;
 return next(bus,selector,0x462e8u,0x462ecu,0,result);
}
enum biwn_rng_status biwn_rng_fill(struct biwn_world_bus *bus,uint32_t budget,uint32_t *result)
{
 uint32_t d0=0,seed,state,value,params[2],index;
 if(!bus||!result||!budget||!bus->read32||!bus->write32||!bus->call)return BIWN_RNG_BAD_ARGUMENT;
 for(index=1;index<=255;index++){
  if(!budget--)return BIWN_RNG_WORK_LIMIT;
  R32(0x113082u+(index-1u)*4u,seed);R32(0x462f0u,params[1]);params[0]=seed;CALL(0xe60au,params,2);
  /* The original initializer's separate chain is22925 times remainder. */
  state=d0*22925u;
  R32(0x462f0u,params[1]);params[0]=seed;CALL(0xe588u,params,2);
  params[0]=d0;R32(0x462f4u,params[1]);CALL(0xe540u,params,2);
  state-=d0;d0=index*4u;W32(0x113082u+d0,state);
  if(!state||(state&0x80000000u)){R32(0x113082u+d0,value);W32(0x113082u+d0,value+0x7fffffffu);}
 }
 *result=d0;return BIWN_RNG_OK;
}
enum biwn_rng_status biwn_rng_seed(struct biwn_world_bus *bus,uint32_t seed,uint32_t *result)
{
 uint32_t d0=seed==0x7fffffffu?0u:seed;
 if(!bus||!result||!bus->write32||!bus->call)return BIWN_RNG_BAD_ARGUMENT;
 W32(0x113082u,d0);CALL(0x1a7f4u,0,0);*result=d0;return BIWN_RNG_OK;
}
enum biwn_rng_status biwn_rng_init(struct biwn_world_bus *bus,uint32_t incoming,uint32_t *result)
{
 uint32_t d0=incoming,params[1]={0};
 if(!bus||!result||!bus->call)return BIWN_RNG_BAD_ARGUMENT;
 CALL(0x1a87au,params,1);params[0]=0x075bcd15u;CALL(0x1a8c6u,params,1);
 *result=d0;return BIWN_RNG_OK;
}
