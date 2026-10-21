#include "biwn_targeting.h"
#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_TARGETING_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_TARGETING_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_TARGETING_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_TARGETING_BUS_ERROR;}while(0)
#define CALL(a,args,n) do {if(bus->call(bus->context,(a),(args),(n),&d0))return BIWN_TARGETING_DEPENDENCY_ERROR;}while(0)
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}
static int less32(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}
static int less16(uint16_t a,uint16_t b){return(a^0x8000u)<(b^0x8000u);}
static uint16_t asr3(uint16_t v){return(uint16_t)((v>>3)|((v&0x8000u)?0xe000u:0));}
/* Original compares twice and rereads shared cursor words between branches. */
static enum biwn_targeting_status approach(struct biwn_world_bus *bus,
 uint32_t address,uint16_t target)
{
 uint16_t current,base,difference;
 R16(address,current);
 if(less16(target,current)){
  R16(address,base);base=(uint16_t)(base-1u);R16(address,current);difference=(uint16_t)((uint32_t)current-target);
  W16(address,(uint32_t)base-asr3(difference));
 }
 R16(address,current);
 if(less16(current,target)){
  R16(address,base);base=(uint16_t)(base+1u);R16(address,current);difference=(uint16_t)((uint32_t)target-current);
  W16(address,(uint32_t)base+asr3(difference));
 }
 return BIWN_TARGETING_OK;
}
enum biwn_targeting_status biwn_targeting_update(struct biwn_world_bus *bus,
 uint32_t incoming_d0,uint32_t *out_d0)
{
 uint32_t d0=incoming_d0,best=0xfffffu,selected=0xffffffffu,distance=0,record,matrix,dx,dz,part,xsquare,score,value,params[2],depth;
 uint16_t old_flag,word,slot,target_x,target_y,coordinate;uint8_t angle;unsigned i;
 enum biwn_targeting_status status;
 if(!bus||!out_d0||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->call)return BIWN_TARGETING_BAD_ARGUMENT;
 R16(0x49d5cu,old_flag);W16(0x49d5cu,0);
 for(i=0;i<40u;i++){
  record=0x49d6cu+i*206u;R16(record,word);if(!word)continue;
  R16(record+0x6cu,word);if(!word)continue;
  R16(record+0xc0u,word);d0=sx16(word)*64u;matrix=0x47b88u+d0;
  R16(matrix+0x16u,word);if(!less16(15,word))continue;
  R16(matrix+0x16u,word);if(less16(1024,word))continue;
  R32(0x49c50u,value);R32(record+4u,dx);dx=value-dx;
  R32(0x49c56u,value);R32(record+10u,dz);dz=value-dz;
  params[0]=(uint16_t)(0u-dx);params[1]=(uint16_t)(0u-dz);CALL(0x13440u,params,2);
  R8(0x49cbau,angle);angle=(uint8_t)((uint8_t)d0-angle);d0=(d0&0xffffff00u)|angle;
  if((angle<0x80u&&angle>5u)||(angle>=0x80u&&angle<0xfbu))continue;
  d0=sx8(angle);params[0]=d0;params[1]=d0*20u;CALL(0xe540u,params,2);part=d0;
  params[0]=dx;params[1]=dx;CALL(0xe540u,params,2);xsquare=d0;part+=xsquare;
  params[0]=dz;params[1]=dz;CALL(0xe540u,params,2);score=part+d0;
  if(!less32(score,best))continue;
  best=score;selected=(selected&0xffff0000u)|i;distance=xsquare+d0;
 }
 if((uint16_t)selected==0xffffu)goto done;
 R16(0x49d5au,slot);d0=sx16(slot)*4u;R32(0x4c280u+d0,value);if(!less32(distance,value))goto done;
 d0=(uint16_t)selected*206u;R16(0x49e2cu+d0,word);matrix=0x47b88u+sx16(word)*64u;
 R16(matrix+0x16u,word);depth=sx16(word);
 R16(matrix+0x12u,word);params[0]=sx16(word)*173u;params[1]=depth;CALL(0xe588u,params,2);target_x=(uint16_t)((uint16_t)d0+112u);
 R16(matrix+0x14u,word);word=(uint16_t)(word-20u);params[0]=sx16(word)*173u;params[1]=depth;CALL(0xe588u,params,2);target_y=(uint16_t)((uint16_t)d0+90u);
 status=approach(bus,0x49d68u,target_x);if(status)return status;
 status=approach(bus,0x49d6au,target_y);if(status)return status;
 R16(0x49d68u,word);
 if(word==target_x){R16(0x49d6au,word);if(word==target_y){W16(0x49d5eu,1);goto bounds;}}
 W16(0x49d5eu,0);
bounds:
 R16(0x49d68u,coordinate);d0=(d0&0xffff0000u)|(uint16_t)(coordinate-1u);
 if((uint16_t)d0<=222u){
  R16(0x49d6au,coordinate);d0=(d0&0xffff0000u)|(uint16_t)(coordinate-9u);
  if((uint16_t)d0<=162u){if(!old_flag){W16(0x49d68u,112);W16(0x49d6au,90);}W16(0x49d5cu,1);}
 }
 W16(0x49d60u,selected);W16(0x49d64u,distance);
 for(i=1;i<=255u;i++){
  R16(0x49d64u,word);value=sx16(word);params[0]=i;params[1]=i;CALL(0xe540u,params,2);
  if(less32(value,d0)){W16(0x49d66u,256u-i);break;}
 }
done:*out_d0=d0;return BIWN_TARGETING_OK;
}
