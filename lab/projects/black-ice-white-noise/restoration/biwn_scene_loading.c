#include "biwn_scene_loading.h"
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_SCENE_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_SCENE_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_SCENE_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_SCENE_BUS_ERROR;}while(0)
#define CALL(a,n) do{if(bus->call(bus->context,(a),p,(n),&d0))return BIWN_SCENE_DEPENDENCY_ERROR;}while(0)
#define WORK() do{if(!work_budget)return BIWN_SCENE_WORK_LIMIT;--work_budget;}while(0)
static uint32_t sx(uint16_t w){return (uint32_t)(w&0x7fffu)-(uint32_t)(w&0x8000u);}
static int less(uint16_t a,uint16_t b){return (a^0x8000u)<(b^0x8000u);}
static uint32_t asr10(uint32_t v){return (v>>10)|((v&0x80000000u)?0xffc00000u:0);}
static uint32_t rem1024(uint32_t v){uint32_t t=v;if(v&0x80000000u)t+=0x3ffu;t&=0xfffffc00u;return v-t;}
static enum biwn_scene_status queue_put(struct biwn_world_bus *bus,struct biwn_scene_texture_queue *queue,uint32_t offset,uint16_t value)
{
 uint32_t index=offset/2u;
 if(queue&&index>=queue->capacity)return BIWN_SCENE_QUEUE_FULL;
 if(!queue||index<50u){if(bus->write16(bus->context,0x15ec7cu+offset,value))return BIWN_SCENE_BUS_ERROR;}
 if(queue){queue->ids[index]=value;if(index>=queue->high_water)queue->high_water=index+1u;}
 return BIWN_SCENE_OK;
}
static enum biwn_scene_status queue_get(struct biwn_world_bus *bus,struct biwn_scene_texture_queue *queue,uint32_t offset,uint16_t *value)
{
 uint32_t index=offset/2u;
 if(queue&&(index>=queue->capacity||index>=queue->high_water))return BIWN_SCENE_QUEUE_FULL;
 if(!queue||index<50u){if(bus->read16(bus->context,0x15ec7cu+offset,value))return BIWN_SCENE_BUS_ERROR;}
 else *value=queue->ids[index];
 return BIWN_SCENE_OK;
}
#define QPUT(o,v) do{enum biwn_scene_status qstatus=queue_put(bus,queue,(o),(v));if(qstatus)return qstatus;}while(0)
#define QGET(o,v) do{enum biwn_scene_status qstatus=queue_get(bus,queue,(o),&(v));if(qstatus)return qstatus;}while(0)
enum biwn_scene_status biwn_scene_loading_with_queue(struct biwn_world_bus *bus,uint32_t entry,
 uint32_t argument0,uint32_t argument1,uint16_t argument2,
 uint32_t incoming_D0,uint32_t work_budget,uint32_t *out_D0,struct biwn_scene_texture_queue *queue)
{
 uint32_t d0=incoming_D0,p[5],a,base,ptr,index,offset,tag,x,z,rem;
 uint16_t w,v,count,i,j,mode;
 if(!bus||!out_D0||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_SCENE_BAD_ARGUMENT;
 if(queue&&(!queue->ids||queue->capacity<50u||queue->capacity>0x7fffu||queue->high_water>queue->capacity))return BIWN_SCENE_BAD_ARGUMENT;
 switch(entry){
 case 0x20b2au:
  for(j=0;j<4;j++){R16(argument0+j*2u,w);W16(argument1+j*2u,w);}
  for(j=0;j<4;j++){R16(argument0+8u+j*2u,w);W32(argument1+8u+j*4u,argument1+8u+sx(w));}
  d0=(d0&0xffff0000u)|(uint16_t)(argument2-16u);p[0]=argument0+16u;p[1]=argument1+24u;p[2]=sx((uint16_t)d0);CALL(0xe3e0u,3);
  i=0;R16(argument1+6u,count);
  while(less(i,count)){
   WORK();R16(0x15ece0u,w);d0=sx(w)*2u;R32(argument1+20u,ptr);R16(ptr+sx(i)*2u+4u,v);QPUT(d0,v);
   R16(0x15ece0u,w);W16(0x15ece0u,w+1u);i=(uint16_t)(i+3u);R16(argument1+6u,count);
  }
  R16(0x15ed46u,w);index=sx(w)*4u;R16(argument1+6u,w);d0=sx(w)*2u;R32(argument1+20u,ptr);d0+=ptr;W32(0x15ece2u+index,d0);
  R16(0x15ed46u,w);W16(0x15ed46u,w+1u);R16(0x15edacu,w);d0=sx(w)*4u;W32(0x15ed48u+d0,argument1);R16(0x15edacu,w);W16(0x15edacu,w+1u);break;
 case 0x20c16u:
  i=0;R16(0x15ece0u,count);
  while(less(i,count)){WORK();d0=sx(i)*2u;QGET(d0,w);p[0]=w;CALL(0x1ac68u,1);i=(uint16_t)(i+1u);R16(0x15ece0u,count);}
  W16(0x15ece0u,0);i=0;R16(0x15edacu,count);
  while(less(i,count)){
   WORK();d0=sx(i)*4u;R32(0x15ed48u+d0,base);R32(base+12u,ptr);j=0;R16(base+2u,w);
   while(less(j,w)){
    WORK();for(v=0;v<3;v++){R16(ptr+2u+v*2u,w);p[0]=w;CALL(0x1ac3cu,1);W16(ptr+2u+v*2u,d0);}
    ptr+=28u;j=(uint16_t)(j+1u);R16(base+2u,w);
   }
   i=(uint16_t)(i+1u);R16(0x15edacu,count);
  }
  W16(0x15edacu,0);break;
 case 0x20cf8u:
  p[0]=argument0;p[1]=argument1;p[2]=sx(argument2);CALL(0xe3e0u,3);
  R32(argument0+4u,a);W32(argument1+4u,argument1+a);R32(argument0+8u,a);base=argument1+a;W32(argument1+8u,base);
  R16(argument1+2u,w);d0=sx(w)*6u;ptr=base+d0;R16(ptr,count);ptr+=2u;
  while(less(0,count)){
   WORK();R16(0x15ece0u,w);d0=sx(w)*2u;R16(ptr,v);ptr+=2u;QPUT(d0,v);R16(0x15ece0u,w);W16(0x15ece0u,w+1u);count=(uint16_t)(count-1u);
  }
  R16(0x15ed46u,w);d0=sx(w)*4u;W32(0x15ece2u+d0,ptr);R16(0x15ed46u,w);W16(0x15ed46u,w+1u);break;
 case 0x20d7cu:
  i=0;R16(0x15ece0u,count);
  while(less(i,count)){WORK();d0=sx(i)*2u;QGET(d0,w);p[0]=w;CALL(0x1ac68u,1);i=(uint16_t)(i+1u);R16(0x15ece0u,count);}
  W16(0x15ece0u,0);R32(0x49c18u,base);R32(base+4u,ptr);i=0;R16(base,count);
  while(less(i,count)){
   WORK();for(j=0;j<6;j++){R16(ptr+10u+j*2u,w);p[0]=w;CALL(0x1ac3cu,1);W16(ptr+10u+j*2u,d0);}
   ptr+=24u;i=(uint16_t)(i+1u);R16(base,count);
  }
  break;
 case 0x20aa0u:
  i=0;R16(0x15ed46u,count);
  while(less(i,count)){
   WORK();d0=sx(i)*4u;R32(0x15ece2u+d0,ptr);R16(ptr,j);ptr+=2u;
   while(less(0,j)){
    WORK();R16(0x49c60u,mode);
    if(mode==1){R16(ptr,w);ptr+=2u;p[0]=w;R32(ptr,p[1]);ptr+=4u;R16(ptr,w);ptr+=2u;p[2]=w;R32(ptr,p[3]);ptr+=4u;}
    else{
     R16(0x49c60u,mode);
     if(mode!=2){j=(uint16_t)(j-1u);continue;}
     R16(ptr,w);ptr+=2u;p[0]=w;R16(ptr,w);ptr+=2u;x=sx(w);R32(0x49c6au,a);p[1]=x+a;p[2]=0;R16(ptr,w);ptr+=2u;z=sx(w);R32(0x49c72u,a);p[3]=z+a;
    }
    R16(ptr,w);ptr+=2u;d0=(d0&0xffff0000u)|w;p[4]=w;CALL(0x13ae0u,5);j=(uint16_t)(j-1u);
   }
   i=(uint16_t)(i+1u);R16(0x15ed46u,count);
  }
  W16(0x15ed46u,0);break;
 case 0x20f78u:
  mode=(uint16_t)argument0;
  if(mode==1){
   R32(0x49c50u,x);x=asr10(x-1u)-2u;R32(0x49c56u,z);z=asr10(0xbc01u-z)+2u;
   p[0]=x;p[1]=5;CALL(0xe60au,2);rem=d0;p[0]=x;p[1]=5;CALL(0xe588u,2);index=z*13u+d0;d0=index*0x1260u;offset=d0+0x930u;tag=index+0x2000u;
   for(i=0;i<25;i=(uint16_t)(i+5u)){
    WORK();p[0]=offset;p[1]=tag;p[2]=0;p[3]=0x1260;p[4]=0;CALL(0x1b044u,5);base=d0;ptr=base+rem*2u;
    for(j=0;j<5;j++){
     R16(ptr+2u+j*2u,w);R16(ptr+j*2u,v);p[2]=(uint16_t)(w-v);d0=sx((uint16_t)(i+j))*4u;R32(0x49bb4u+d0,p[1]);R16(ptr+j*2u,w);p[0]=base+sx(w);CALL(0x20b2au,3);
    }
    W16(0x47b80u,0);offset-=0xeee0u;tag-=13u;
   }
   W16(0x49c8cu,12);R32(0x49c50u,x);d0=rem1024(x);W16(0x49b8cu,d0+0x800u);R16(0x49c54u,w);W16(0x49b8eu,w-32u);R32(0x49c56u,z);d0=rem1024(z);W16(0x49b90u,d0+0x800u);
   W16(0x49b92u,0);W16(0x49b94u,0);W16(0x49b96u,0);CALL(0x20c16u,0);p[0]=0x49c4c;CALL(0x102c4u,1);W16(0x49c60u,1);CALL(0x20aa0u,0);
  }else if(mode==2){
   R16(0x49c64u,w);index=sx(w);d0=index*0x1260u+0x591c90u;p[0]=d0;p[1]=index+0x6000u;p[2]=0;p[3]=0x1260;p[4]=0;CALL(0x1b044u,5);
   R32(0x49c18u,p[1]);p[0]=d0;p[2]=0x1260;CALL(0x20cf8u,3);W16(0x47b80u,0);
   R16(0x49c52u,w);R16(0x49c6cu,v);W16(0x49b8cu,w-v);R16(0x49c54u,w);W16(0x49b8eu,w-32u);R16(0x49c58u,w);R16(0x49c74u,v);W16(0x49b90u,w-v);
   W16(0x49b92u,0);W16(0x49b94u,0);W16(0x49b96u,0);CALL(0x20d7cu,0);p[0]=0x49c4c;CALL(0x10520u,1);W16(0x49c60u,2);CALL(0x20aa0u,0);
  }
  break;
 default:return BIWN_SCENE_BAD_ARGUMENT;
 }
 *out_D0=d0;return BIWN_SCENE_OK;
}
enum biwn_scene_status biwn_scene_loading(struct biwn_world_bus *bus,uint32_t entry,
 uint32_t argument0,uint32_t argument1,uint16_t argument2,uint32_t incoming,uint32_t budget,uint32_t *out)
{return biwn_scene_loading_with_queue(bus,entry,argument0,argument1,argument2,incoming,budget,out,0);}
