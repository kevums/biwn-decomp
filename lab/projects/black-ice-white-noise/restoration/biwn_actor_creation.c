#include "biwn_actor_creation.h"
#define R8(a,v) do{if(bus->read8(bus->context,(a),&(v)))return BIWN_ACTOR_BUS_ERROR;}while(0)
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_ACTOR_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_ACTOR_BUS_ERROR;}while(0)
#define W8(a,v) do{if(write8(bus->context,(a),(uint8_t)(v)))return BIWN_ACTOR_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_ACTOR_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_ACTOR_BUS_ERROR;}while(0)
#define CALL(a,n) do{if(bus->call(bus->context,(a),p,(n),&d0))return BIWN_ACTOR_DEPENDENCY_ERROR;}while(0)
#define WORK() do{if(!budget)return BIWN_ACTOR_WORK_LIMIT;--budget;}while(0)
static uint32_t sx(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}
static int less(uint16_t a,uint16_t b){return(a^0x8000u)<(b^0x8000u);}
static uint32_t asr10(uint32_t v){return(v>>10)|((v&0x80000000u)?0xffc00000u:0);}
static uint32_t word(uint32_t old,uint16_t v){return(old&0xffff0000u)|v;}
enum biwn_actor_status biwn_actor_service(struct biwn_world_bus *bus,biwn_actor_write8 write8,
 uint32_t entry,const uint32_t *args,uint32_t n,uint32_t incoming_D0,uint32_t budget,uint32_t *out_D0)
{
 uint32_t d0=incoming_D0,p[6],object,base,record,origin,value,x,z,dx,dz,heading,id,target,slot,offset,model,payload,callback=0;
 uint16_t w,v,count,i,mode,small;uint8_t byte;
 if(!bus||!out_D0||!args||!write8||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_ACTOR_BAD_ARGUMENT;
 if((entry==0x13ae0u||entry==0x137e0u)?n!=5u:entry==0x134dcu?n!=6u:(entry==0x10520u||entry==0x105dau)?n!=1u:1)return BIWN_ACTOR_BAD_ARGUMENT;
 if(entry==0x10520u||entry==0x105dau){
  object=args[0];R32(0x49c18u,base);
  if(entry==0x10520u){R32(object+4u,d0);R32(object+30u,origin);d0-=origin;dx=d0>>6;R32(object+10u,d0);R32(object+38u,origin);}
  else{R32(object+2u,d0);R32(0x49c6au,origin);d0-=origin;dx=d0>>6;R32(object+8u,d0);R32(0x49c72u,origin);}
  d0-=origin;dz=d0>>6;R16(base,count);i=(uint16_t)(count-1u);
  if(!(i&0x8000u))do{
   WORK();d0=sx(i)*24u;R32(base+4u,value);record=value+d0;R16(record+2u,w);
   if(!less((uint16_t)dx,w)){
    R16(record+2u,w);R16(record+6u,v);d0=word(d0,(uint16_t)(w+v));
    if(less((uint16_t)dx,(uint16_t)d0)){
     R16(record+4u,w);if(!less((uint16_t)dz,w)){
      R16(record+4u,w);R16(record+8u,v);d0=word(d0,(uint16_t)(w+v));
      if(less((uint16_t)dz,(uint16_t)d0))goto position_found;
     }
    }
   }
   i=(uint16_t)(i-1u);
  }while(i!=0xffffu);
  d0&=0xffff0000u;goto finish;
position_found:
  if(entry==0x105dau){W16(object+16u,i);d0=1;goto finish;}
  W16(object+42u,i);W32(object+44u,record);R16(record+2u,w);d0=word(d0,(uint16_t)(w<<6));R32(object+30u,origin);W32(object+52u,origin+sx((uint16_t)d0));
  R16(record+4u,w);d0=word(d0,(uint16_t)(w<<6));R32(object+38u,origin);W32(object+60u,origin+sx((uint16_t)d0));
  R16(record+6u,w);d0=word(d0,(uint16_t)(w<<6));R32(object+52u,origin);W32(object+48u,origin+sx((uint16_t)d0));
  R16(record+8u,w);d0=word(d0,(uint16_t)(w<<6));R32(object+60u,origin);W32(object+56u,origin+sx((uint16_t)d0));d0=1;goto finish;
 }
 id=(uint16_t)args[0];
 if(entry==0x13ae0u){
  R8(0x4208cu+sx((uint16_t)id),byte);
  if(byte&1u){
   for(i=0;i<40;i++){WORK();d0=sx(i)*206u;R16(0x49d6cu+d0,w);if(!w)break;}
   if(i==40)goto finish;
   p[0]=id;p[1]=i;p[2]=args[1];p[3]=(uint16_t)args[2];p[4]=args[3];p[5]=(uint16_t)args[4];CALL(0x134dcu,6);
  }else{for(i=0;i<5;i++)p[i]=args[i];CALL(0x137e0u,5);}
  goto finish;
 }
 if(entry==0x134dcu){
  slot=(uint16_t)args[1];object=0x49d6cu+sx((uint16_t)slot)*206u;x=args[2];z=args[4];heading=(uint16_t)args[5];
  W16(object,id);W16(object+2u,0);W32(object+4u,x);W16(object+8u,args[3]);W32(object+10u,z);
  W16(object+14u,0);W16(object+16u,0);W16(object+18u,0);
  R16(0x49c60u,w);W16(object+20u,w);R16(0x49c62u,w);W16(object+22u,w);R16(0x49c64u,w);W16(object+24u,w);
  for(i=0;i<4;i++){R32(0x49c66u+i*4u,value);W32(object+26u+i*4u,value);}
  R32(0x49c56u,d0);dz=asr10((z&0xfffffc00u)-(d0&0xfffffc00u));small=(uint16_t)(dz*5u+12u);
  R32(0x49c50u,d0);d0&=0xfffffc00u;dx=asr10((x&0xfffffc00u)-d0);W16(object+64u,(uint16_t)(small+(uint16_t)dx));
  W32(object+88u,0);W16(object+92u,0);W32(object+94u,0);W16(object+98u,0);W32(object+100u,0);W32(object+104u,0);W16(object+108u,0);W8(object+110u,heading);W8(object+111u,heading);
  W32(object+112u,0);W32(object+116u,0);W32(object+120u,0);W32(object+124u,0);W16(object+150u,0);W16(object+148u,0);W16(object+146u,0);W16(object+196u,0);W16(object+202u,1);
  R16(object+20u,mode);if(mode==1){p[0]=object;CALL(0x102c4u,1);}else{R16(object+20u,mode);if(mode==2){p[0]=object;CALL(0x10520u,1);}}
  d0=word(d0,(uint16_t)(id-4u));if((uint16_t)d0>114u)goto invalid_actor;
  d0=(uint16_t)d0;d0+=d0;R16(0x13620u+d0,w);d0=word(d0,w);target=0x13620u+sx(w);
  switch(target){
  case 0x13706u:callback=0xf4d8u;break;case 0x13714u:callback=0xedc4u;break;case 0x13722u:callback=0xfcc2u;break;
  case 0x13730u:callback=0x17f80u;break;case 0x1373eu:callback=0x178e0u;break;case 0x1374au:callback=0xf720u;break;
  case 0x13756u:callback=0x21d40u;break;case 0x13762u:callback=0x15080u;break;case 0x1376eu:callback=0x14fc0u;break;
  case 0x1377au:callback=0xf888u;break;case 0x13786u:callback=0x15140u;break;case 0x13792u:callback=0x14100u;break;
  case 0x1379eu:callback=0x11f80u;break;case 0x137aau:callback=0x128a0u;break;case 0x137b6u:callback=0x15a80u;break;
  case 0x137cau:goto invalid_actor;case 0x137dau:goto finish;default:return BIWN_ACTOR_UNSUPPORTED_DISPATCH;
  }
  p[0]=callback;p[1]=sx((uint16_t)slot);CALL(0xdf6cu,2);goto finish;
invalid_actor:
  d0=sx((uint16_t)slot)*206u;W16(0x49d6cu+d0,0);goto finish;
 }
 /* Static/sprite object path137E0. */
 x=args[1];z=args[3];heading=(uint16_t)args[4];
 for(i=0;i<40;i++){WORK();d0=sx(i)*30u;R16(0x4bd9cu+d0,w);if(!w)break;}
 if(i==40)goto finish;
 slot=i;offset=sx((uint16_t)slot)*30u;object=0x4bd9cu+offset;W16(object,id);W32(object+2u,x);W16(object+6u,args[2]);W32(object+8u,z);
 d0=z&0xfffffc00u;R32(0x49c56u,value);d0-=value&0xfffffc00u;d0=asr10(d0);small=(uint16_t)(d0*5u+12u);
 d0=x&0xfffffc00u;R32(0x49c50u,value);d0-=value&0xfffffc00u;d0=asr10(d0);W16(object+14u,(uint16_t)(small+(uint16_t)d0));p[0]=object;CALL(0x105dau,1);
 R8(0x4208cu+id,byte);
 if(byte&2u){
  heading=(uint16_t)(heading<<8);W8(object+12u,heading);d0=word(d0,(uint16_t)(id-104u));if((uint16_t)d0>34u)goto finish;
  d0=(uint16_t)d0;d0+=d0;R16(0x138bcu+d0,w);d0=word(d0,w);target=0x138bcu+sx(w);
  switch(target){
  case 0x13902u:callback=0x8f54u;break;case 0x1391au:callback=0x9de0u;break;case 0x13932u:callback=0xa2b8u;break;
  case 0x1394au:callback=0x9908u;break;case 0x139ceu:callback=0x8db0u;break;case 0x139e6u:callback=0xce20u;break;
  case 0x139feu:callback=0xb390u;break;case 0x13a16u:callback=0xc648u;break;
  case 0x13a2eu:d0=offset;W16(object,0);goto finish;case 0x13ad8u:goto finish;
  case 0x13962u:
   d0=offset;W32(object+24u,0x8b80u);R32(object+2u,value);W32(object+2u,value-32u);R16(object+16u,small);
   for(i=0;i<40;i++){WORK();d0=sx(i)*30u;R16(0x4bd9cu+d0,w);if(!w)break;}
   if(i==40)goto finish;
   d0=sx(i)*30u;object=0x4bd9cu+d0;W16(object+16u,small);W16(object,id);W32(object+2u,x);W16(object+6u,args[2]);W32(object+8u,z+32u);W8(object+12u,0);W32(object+24u,0x8c98u);goto finish;
  default:return BIWN_ACTOR_UNSUPPORTED_DISPATCH;
  }
  d0=offset;W32(object+24u,callback);goto finish;
 }
 R32(0x6e6a8u,d0);d0+=d0;p[0]=d0+16u;CALL(0x152a2u,1);W32(object+20u,d0);R32(d0,payload);W32(payload,0x20000u);
 R32(object+20u,value);R32(value,payload);R8(0x42000u+id,byte);d0=sx8(byte)<<2;R32(0x6e6acu+d0,value);model=0x6e6a0u+value;
 R8(model,byte);value=(uint32_t)byte<<16;R8(model+1u,byte);d0=byte;value|=d0;W32(payload+8u,value);
 R8(model,byte);d0=(uint32_t)byte<<2;R32(0x3bd20u+d0,value);W32(payload+12u,value);
 R32(object+20u,value);R32(value,p[2]);p[2]+=16u;R8(0x42000u+id,byte);d0=word(d0,(uint16_t)sx8(byte));p[1]=sx((uint16_t)d0);p[0]=0x6e6a0u;CALL(0xe2b8u,3);
finish:
 *out_D0=d0;return BIWN_ACTOR_OK;
}
