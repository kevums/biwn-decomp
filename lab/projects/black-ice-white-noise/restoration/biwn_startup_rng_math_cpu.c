/* Generated separately from the accepted user-only RNG math.
 * Both-stack-bank derivative; see startup generator and comparison. */
#include "biwn_startup_rng_math_cpu.h"
#include "biwn_signed_division.h"
#include "biwn_camera.h"
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void nz(struct biwn_task_cpu *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:0xffffu,sign=1u<<(bits-1);v&=mask;s->sr=(uint16_t)((s->sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static void xflag(struct biwn_task_cpu *s,unsigned x){s->sr=(uint16_t)((s->sr&~0x10u)|(x?0x10u:0));}
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_STARTUP_RNG_MATH_CPU_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_STARTUP_RNG_MATH_CPU_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_STARTUP_RNG_MATH_CPU_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_STARTUP_RNG_MATH_CPU_BUS_ERROR;}while(0)
#define CHECK(e) do{enum biwn_startup_rng_math_cpu_status status=(e);if(status)return status;}while(0)
static enum biwn_startup_rng_math_cpu_status push(struct biwn_world_bus *bus,struct biwn_task_cpu *s,uint32_t v,unsigned width)
{s->registers[15]-=width;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];if(width==2){W16(s->registers[15],v);}else{W32(s->registers[15],v);}return BIWN_STARTUP_RNG_MATH_CPU_OK;}
static enum biwn_startup_rng_math_cpu_status run(struct biwn_world_bus *,struct biwn_task_cpu *);
static enum biwn_startup_rng_math_cpu_status subcall(struct biwn_world_bus *bus,struct biwn_task_cpu *s,uint32_t target,uint32_t ret)
{CHECK(push(bus,s,ret,4));s->pc=target;CHECK(run(bus,s));R32(s->registers[15],s->pc);s->registers[15]+=4;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];return s->pc==ret?BIWN_STARTUP_RNG_MATH_CPU_OK:BIWN_STARTUP_RNG_MATH_CPU_BAD_RETURN;}
static enum biwn_startup_rng_math_cpu_status division(struct biwn_world_bus *bus,struct biwn_task_cpu *s)
{
 uint32_t numerator,denominator,q,r,absn,absd;uint16_t sign,high;
 s->registers[8]=s->registers[2];s->registers[9]=s->registers[3];CHECK(push(bus,s,0,2));
 s->registers[0]=0;R32(s->registers[15]+10u,denominator);s->registers[2]=denominator;
 if(!denominator)return BIWN_STARTUP_RNG_MATH_CPU_ZERO_DIVISOR;
 absd=denominator&0x80000000u?0u-denominator:denominator;
 if(denominator&0x80000000u){xflag(s,1);R16(s->registers[15],sign);W16(s->registers[15],(uint16_t)~sign);}
 s->registers[2]=absd;R32(s->registers[15]+6u,numerator);s->registers[1]=numerator;
 absn=numerator&0x80000000u?0u-numerator:numerator;
 if(numerator&0x80000000u){xflag(s,1);R16(s->registers[15],sign);W16(s->registers[15],(uint16_t)~sign);}
 if(absn>=absd){
  R16(s->registers[15]+10u,high);
  /* A positive word divisor uses DIVU, which preserves X. The restoring
   * 32-step path finishes with X=0: its remainder<absd<=0x80000000 before
   * each shift, and any quotient-bit ADDQ adds1 to an even low word. */
  if(high)xflag(s,0);
 }
 if(biwn_signed_division(numerator,denominator,&q,&r))return BIWN_STARTUP_RNG_MATH_CPU_ZERO_DIVISOR;
 R16(s->registers[15]+6u,high);
 if(high&0x8000u)xflag(s,r!=0);
 R16(s->registers[15],sign);s->registers[15]+=2;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];
 if(sign&0x8000u)xflag(s,q!=0);
 s->registers[0]=q;s->registers[1]=r;s->registers[3]=s->registers[9];s->registers[2]=s->registers[8];nz(s,s->registers[2],32);s->pc=0xe604u;return BIWN_STARTUP_RNG_MATH_CPU_OK;
}
static enum biwn_startup_rng_math_cpu_status multiply(struct biwn_world_bus *bus,struct biwn_task_cpu *s)
{
 uint16_t words[4],sign;uint32_t a,b,absa,absb,cross,low,partial,result;unsigned i;
 s->registers[8]=s->registers[2];s->registers[9]=s->registers[3];
 for(i=0;i<4;i++){R16(s->registers[15]+4u+i*2u,words[i]);s->registers[i]=sx16(words[i]);}
 a=((uint32_t)words[0]<<16)|words[1];b=((uint32_t)words[2]<<16)|words[3];
 CHECK(push(bus,s,words[0],2));
 if(b&0x80000000u){R16(s->registers[15],sign);W16(s->registers[15],(uint16_t)~sign);}
 absa=a&0x80000000u?0u-a:a;absb=b&0x80000000u?0u-b:b;
 cross=biwn_multiply32(absa>>16,absb&0xffffu)+biwn_multiply32(absb>>16,absa&0xffffu);
 partial=(cross&0xffffu)<<16;low=biwn_multiply32(absa&0xffffu,absb&0xffffu);result=partial+low;
 xflag(s,result<partial);s->registers[0]=biwn_multiply32(a,b);s->registers[1]=low;
 s->registers[3]=s->registers[9];s->registers[2]=s->registers[8];
 R16(s->registers[15],sign);s->registers[15]+=2;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];nz(s,sign,16);
 if(sign&0x8000u){
  xflag(s,result!=0);nz(s,s->registers[0],32);
  if(result)s->sr|=1u;if(result==0x80000000u)s->sr|=2u;
 }
 s->pc=0xe586u;return BIWN_STARTUP_RNG_MATH_CPU_OK;
}
static enum biwn_startup_rng_math_cpu_status run(struct biwn_world_bus *bus,struct biwn_task_cpu *s)
{
 uint32_t value,address,product;uint16_t selector;int i;
 if(s->pc==0xe588u)return division(bus,s);
 if(s->pc==0xe540u)return multiply(bus,s);
 if(s->pc==0xe60au){
  R32(s->registers[15]+8u,value);CHECK(push(bus,s,value,4));
  R32(s->registers[15]+8u,value);CHECK(push(bus,s,value,4));
  CHECK(subcall(bus,s,0xe588u,0xe616u));s->registers[15]+=8;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];
  s->registers[0]=s->registers[1];nz(s,s->registers[0],32);s->pc=0xe61au;return BIWN_STARTUP_RNG_MATH_CPU_OK;
 }
 for(i=10;i>=2;i--)if(i==10||i==4||i==3||i==2)CHECK(push(bus,s,s->registers[i],4));
 R16(s->registers[15]+20u,selector);s->registers[0]=sx16(selector);s->registers[10]=0x113082u;s->registers[4]=s->registers[0]<<2;
 address=s->registers[10]+s->registers[4];R32(address,s->registers[3]);
 R32(0x462e8u,value);CHECK(push(bus,s,value,4));CHECK(push(bus,s,s->registers[3],4));CHECK(subcall(bus,s,0xe60au,0x1a7a2u));
 s->registers[15]+=8;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];s->registers[2]=s->registers[0]*48271u;
 R32(0x462e8u,value);CHECK(push(bus,s,value,4));CHECK(push(bus,s,s->registers[3],4));CHECK(subcall(bus,s,0xe588u,0x1a7c8u));
 s->registers[15]+=4;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];R32(0x462ecu,value);W32(s->registers[15],value);
 CHECK(push(bus,s,s->registers[0],4));CHECK(subcall(bus,s,0xe540u,0x1a7d8u));s->registers[15]+=8;if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];
 product=s->registers[0];value=s->registers[2];s->registers[2]-=product;xflag(s,value<product);W32(address,s->registers[2]);
 if(!s->registers[2]||(s->registers[2]&0x80000000u)){R32(address,value);product=value+0x7fffffffu;W32(address,product);xflag(s,product<value);}
 R32(address,s->registers[0]);nz(s,s->registers[0],32);
 for(i=2;i<=10;i++)if(i==2||i==3||i==4||i==10){R32(s->registers[15],s->registers[i]);s->registers[15]+=4;}
 if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];s->pc=0x1a7f2u;return BIWN_STARTUP_RNG_MATH_CPU_OK;
}
enum biwn_startup_rng_math_cpu_status biwn_startup_rng_math_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu s;enum biwn_startup_rng_math_cpu_status status;
 if(!bus||!state||!bus->read16||!bus->read32||!bus->write16||!bus->write32||
    (state->pc!=0x1a77cu&&state->pc!=0xe60au&&state->pc!=0xe588u&&state->pc!=0xe540u))return BIWN_STARTUP_RNG_MATH_CPU_BAD_ARGUMENT;
 s=*state;status=run(bus,&s);if(status)return status;*state=s;return BIWN_STARTUP_RNG_MATH_CPU_OK;
}
enum biwn_startup_rng_math_cpu_status biwn_startup_rng_math_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state)
{
 struct biwn_task_cpu s;enum biwn_startup_rng_math_cpu_status status;if(!state)return BIWN_STARTUP_RNG_MATH_CPU_BAD_ARGUMENT;s=*state;
 status=biwn_startup_rng_math_cpu_body(bus,&s);if(status)return status;
 R32(s.registers[15],s.pc);s.registers[15]+=4;if(s.sr&0x2000u)s.ssp=s.registers[15];else s.usp=s.registers[15];*state=s;return BIWN_STARTUP_RNG_MATH_CPU_OK;
}
