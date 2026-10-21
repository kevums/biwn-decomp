/* Coordinator native adapter for the existing recovered input source.
 * Public entry is a C ABI fixture, not an installed 191F4 replacement.
 * Original helpers other than E588 remain explicit physical dependencies.
 */
#include "biwn_input_dispatch.h"
#include "biwn_signed_division.h"
#include <stddef.h>

/* GCC uses this for the private bus-structure initializer. No host libc. */
void *memcpy(void *destination,const void *source,size_t count)
{
 volatile uint8_t *to=destination;
 const volatile uint8_t *from=source;
 for(size_t i=0;i<count;i++)to[i]=from[i];
 return destination;
}

extern uint32_t biwn_input_physical_call(uint32_t,const uint32_t *,uint32_t,uint32_t,uint32_t);
static int read8(void *p,uint32_t a,uint8_t *v){(void)p;*v=*(volatile uint8_t *)a;return 0;}
static int read16(void *p,uint32_t a,uint16_t *v){(void)p;*v=*(volatile uint16_t *)a;return 0;}
static int read32(void *p,uint32_t a,uint32_t *v){(void)p;*v=*(volatile uint32_t *)a;return 0;}
static int write8(void *p,uint32_t a,uint8_t v){(void)p;*(volatile uint8_t *)a=v;return 0;}
static int write16(void *p,uint32_t a,uint16_t v){(void)p;*(volatile uint16_t *)a=v;return 0;}
static int write32(void *p,uint32_t a,uint32_t v){(void)p;*(volatile uint32_t *)a=v;return 0;}

static int call(void *p,uint32_t target,const uint32_t *args,uint32_t count,uint32_t *out)
{
 uint32_t mask=0,expected=0,remainder;
 (void)p;
 if(target==0xe588u){
  if(count!=2u||!args)return 1;
  return biwn_signed_division(args[0],args[1],out,&remainder);
 }
 switch(target){
 case 0xeb04u:case 0x1545cu:case 0x152a2u:case 0x1ab2au:expected=1;break;
 case 0x1b002u:case 0x1af04u:case 0x1aa40u:expected=1;mask=1;break;
 case 0x190bcu:case 0xe4c0u:case 0x1a0f8u:case 0xdf60u:
 case 0x1aadeu:case 0xdf22u:case 0x11e6cu:case 0x18160u:
 case 0xdf3eu:case 0x18e92u:case 0x18df2u:break;
 default:return 1;
 }
 if(count!=expected||(!args&&count)||!out)return 1;
 *out=biwn_input_physical_call(target,args,count,mask,*out);
 return 0;
}

int biwn_native_input_fixture(uint32_t incoming,uint32_t *output)
{
 struct biwn_world_bus bus={read8,read16,read32,write16,write32,call,0,0};
 /* Finite fixture budget. Yield/IRQ/private task-stack behavior is unqualified. */
 return biwn_input_dispatch(&bus,write8,0xffffffffu,incoming,output);
}
