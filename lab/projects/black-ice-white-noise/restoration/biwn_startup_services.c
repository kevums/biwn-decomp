#include "biwn_startup_services.h"
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_SERVICES_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_SERVICES_BUS_ERROR;}while(0)
#define W8(a,v) do {if(write8(bus->context,(a),(uint8_t)(v)))return BIWN_SERVICES_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_SERVICES_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_SERVICES_BUS_ERROR;}while(0)
#define CALL(a,p,n) do {if(bus->call(bus->context,(a),(p),(n),&d0))return BIWN_SERVICES_DEPENDENCY_ERROR;}while(0)
enum biwn_services_status biwn_startup_service(struct biwn_world_bus *bus,
 biwn_startup_write8 write8,uint32_t entry,uint32_t incoming_D0,uint32_t *out_D0)
{
 uint32_t d0=incoming_D0,p[2],value,object;uint16_t word;unsigned i;
 if(!bus||!out_D0)return BIWN_SERVICES_BAD_ARGUMENT;
 switch(entry){
 case 0xe2f4u:
  if(!bus->write32)return BIWN_SERVICES_BAD_ARGUMENT;
  W32(0x10a680u,0);break;
 case 0x18160u:
  if(!bus->write32||!bus->write16)return BIWN_SERVICES_BAD_ARGUMENT;
  d0=0;W32(0xf02268u,0);W32(0xf0226cu,0);W32(0xf02200u,0xb29d0u);
  W32(0xf02204u,0x2e20u);W32(0xf0220cu,0);W32(0xf0223cu,0x113b0u);W32(0xf02238u,0x10200u);
  W16(0x113060u,0);W16(0xf00400u,0);W16(0xf00402u,0x77fu);W16(0xf00404u,0x7040u);W16(0xf00406u,0x707fu);break;
 case 0x1aedau:
  if(!bus->write16)return BIWN_SERVICES_BAD_ARGUMENT;
  for(i=0;i<50;i++){d0=i*12u;W16(0x15b534u+d0,0xffffu);W16(0x15b53au+d0,0);W16(0x15b53eu+d0,0);W16(0x15b53cu+d0,0);}break;
 case 0xf0c0u:
  if(!bus->write16||!bus->write32)return BIWN_SERVICES_BAD_ARGUMENT;
  for(i=0;i<6;i++)W16(0x49b8cu+i*2u,0);
  d0=8;W32(0x49b98u,d0);W32(0x49b9cu,d0);W32(0x49ba0u,0);break;
 case 0x21242u:
  if(!bus->write16||!bus->write32||!bus->call)return BIWN_SERVICES_BAD_ARGUMENT;
  W16(0x15ece0u,0);W16(0x15ed46u,0);W16(0x15edacu,0);
  for(i=0;i<25;i++){d0=i*4u;W32(0x49bb4u+d0,0x15b7c0u+i*540u);}
  W32(0x49c18u,0x15b7c0u);
  for(i=0;i<40;i++){d0=i*206u;W16(0x49d6cu+d0,0);}
  for(i=0;i<40;i++){d0=i*30u;W16(0x4bd9cu+d0,0);}
  W16(0x47b80u,0);W16(0x47b82u,0);p[0]=0;CALL(0x1aa40u,p,1);
  CALL(0x1aedau,p,0);CALL(0xea20u,p,0);CALL(0xf0c0u,p,0);break;
 case 0xdfc0u:
  if(!bus->read32||!bus->write16||!bus->call)return BIWN_SERVICES_BAD_ARGUMENT;
  CALL(0xe4c0u,p,0);R32(0x49ba4u,d0);
  if(d0&1u){W16(0x49b8cu,0);W16(0x49b8eu,0);W16(0x49b90u,0);CALL(0x11e6cu,p,0);}break;
 case 0x18ba8u:
  if(!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call||!write8)return BIWN_SERVICES_BAD_ARGUMENT;
  W16(0x49d5au,0);W16(0x49c4cu,0);W16(0x49c4eu,0);W32(0x49c50u,0x24a0u);W16(0x49c54u,0);
  W32(0x49c56u,0x9ca0u);W16(0x49c5au,0);W16(0x49c5cu,0);W16(0x49c5eu,0);W16(0x49c60u,0);
  R16(0x45d9au,word);p[0]=word;CALL(0x1af04u,p,1);W32(0x49ca4u,d0);
  R32(d0,object);R32(object+8u,d0);d0+=d0;p[0]=d0+16u;CALL(0x152a2u,p,1);
  W32(0x49caau,d0);R32(d0,object);W32(object,0x2c000u);W16(0x49ca8u,0);W16(0x49caeu,0);
  R16(0x49c4cu,word);d0=((uint32_t)(word&0x7fffu)-(uint32_t)(word&0x8000u))*20u;
  R16(0x49d5au,word);value=((uint32_t)(word&0x7fffu)-(uint32_t)(word&0x8000u))*4u;
  R32(0x45e30u+d0+value,object);W32(0x49cb0u,object);
  R16(0x49c4cu,word);d0=((uint32_t)(word&0x7fffu)-(uint32_t)(word&0x8000u))*20u;
  R32(0x45e30u+d0+value,object);W32(0x49cb4u,object);W16(0x49cb8u,1);W8(0x49cbau,0x80);W8(0x49cbbu,0);
  W32(0x49cbcu,0x0u);
  W32(0x49cc0u,0x0u);
  W32(0x49cc4u,0x0u);
  W32(0x49cc8u,0x0u);
  W16(0x49cdeu,0x0u);
  W16(0x49ce0u,0x0u);
  W16(0x49ce2u,0x0u);
  W16(0x49cecu,0x8u);
  W16(0x49ce4u,0x0u);
  W16(0x49cf0u,0xffe0u);
  W16(0x49cf2u,0xff60u);
  W16(0x49cf4u,0x0u);
  W16(0x49cf6u,0x20u);
  W16(0x49cf8u,0xff60u);
  W16(0x49cfau,0x0u);
  W16(0x49cfcu,0x20u);
  W16(0x49cfeu,0x0u);
  W16(0x49d00u,0x0u);
  W16(0x49d02u,0xffe0u);
  W16(0x49d04u,0x0u);
  W16(0x49d06u,0x0u);
  W16(0x49d12u,0xc8u);
  W16(0x49d14u,0x64u);
  W16(0x49d16u,0x1u);
  W32(0x49d1eu,0xc8u);
  W16(0x49d26u,0x64u);
  W16(0x49d28u,0xau);
  W16(0x49d22u,0x4bu);
  W16(0x49d24u,0x4bu);
  W16(0x49d54u,0x0u);
  W16(0x49d56u,0x0u);
  W16(0x49d58u,0x0u);
  p[0]=0x18b86u;p[1]=0x1388u;CALL(0xdf6cu,p,2);
  W16(0x49d2cu,0x41u);
  W16(0x49d2eu,0x24u);
  W16(0x49d30u,0x29u);
  W16(0x49d32u,0x46u);
  W16(0x49d34u,0x0u);
  W16(0x49d36u,0x0u);
  W16(0x49d38u,0x0u);
  W16(0x49d3au,0x0u);
  W16(0x49d3cu,0x0u);
  W16(0x49d3eu,0x0u);
  W16(0x49d2au,0x8u);
  CALL(0x1b786u,p,0);CALL(0x18888u,p,0);p[0]=1;CALL(0x1aa40u,p,1);CALL(0x20f78u,p,1);break;
 default:return BIWN_SERVICES_BAD_ARGUMENT;
 }
 *out_D0=d0;return BIWN_SERVICES_OK;
}
