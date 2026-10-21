#include "biwn_display_list.h"
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_DISPLAY_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_DISPLAY_BUS_ERROR;}while(0)
#define W32(v) do{if(bus->write32(bus->context,output,(uint32_t)(v)))return BIWN_DISPLAY_BUS_ERROR;output+=4u;}while(0)
#define WORK() do{if(!work--)return BIWN_DISPLAY_WORK_LIMIT;}while(0)
enum biwn_display_status biwn_display_list(struct biwn_world_bus *bus,uint32_t records,uint32_t output,
 uint32_t *links,uint32_t capacity,uint32_t work,uint32_t *result)
{
 uint32_t count=1,row=records,i=0,cursor=0x776f0u>>3,d0=0,d1,d2,d3,value,index,mask;
 uint16_t type,word;int stop=0;
 if(!bus||!links||!capacity||!work||!result||!bus->read16||!bus->read32||!bus->write32)return BIWN_DISPLAY_BAD_ARGUMENT;
 WORK();R16(row,type);
 while(type!=4u){WORK();if(count==capacity)return BIWN_DISPLAY_WORK_LIMIT;count++;row+=36u;R16(row,type);}
 row=records;
 do{
  WORK();if(i>=count)return BIWN_DISPLAY_WORK_LIMIT;R16(row,type);
  if(type==0u){cursor=(cursor+1u)&0xfffffffeu;value=2;}
  else if(type==1u){cursor=(cursor+3u)&0xfffffffcu;value=3;}
  else value=1;
  links[i++]=cursor;cursor+=value;row+=36u;
 }while(type!=4u);
 cursor=0x776f0u>>3;row=records;i=0;
 do{
  WORK();if(i>=count)return BIWN_DISPLAY_WORK_LIMIT;
  d1=i+1u<count?links[i+1u]:0; /* Original final one-past value is unused. */
  R16(row,type);
  if(type<=4u){
   R16(row,type);if(type>4u)return BIWN_DISPLAY_BAD_LINK;
   R16(0x18690u+(uint32_t)type*2u,word);
   {static const uint16_t offsets[5]={0xau,0xeu,0x118u,0x134u,0x17cu};
    if(word!=offsets[type])return BIWN_DISPLAY_BAD_LINK;}
   switch(type){
   case 0:case 1:
    mask=type==0u?1u:3u;
    while(cursor&mask){WORK();cursor++;d0=(cursor&0x7ff00u)>>8;W32(d0);d0=(cursor&0xffu)<<24;W32(d0|3u);}
    R32(row+6u,value);
    if(value){R32(row+6u,value);index=value&0x3fffffffu;if(!index||index>count)return BIWN_DISPLAY_BAD_LINK;d1=links[index-1u];}
    R32(row+10u,d3);d3=(d3&0xfffff8u)<<8;d2=(d1&0x7ff00u)>>8;d1=(d1&0xffu)<<24;
    R16(row+14u,word);d0=(uint32_t)word<<14;d1|=d0;R16(row+4u,word);d0=(uint32_t)word<<3;d1|=d0;
    R16(row,word);d0=word;d3|=d2;W32(d3);d1|=d0;W32(d1);
    R16(row+28u,word);d3=(uint32_t)(uint16_t)(word<<1)<<16;
    R16(row+26u,word);d0=(uint32_t)word<<13;d3|=d0;R16(row+24u,word);d0=(uint32_t)word<<6;d3|=d0;
    R16(row+18u,word);d2=(word&0x3f0u)>>4;R16(row+18u,word);d1=(uint32_t)word<<28;
    R16(row+16u,word);d0=(uint32_t)(uint16_t)(word<<2)<<16;d1|=d0;
    R16(row+22u,word);d0=(uint32_t)word<<15;d1|=d0;R16(row+20u,word);d0=(uint32_t)word<<12;d1|=d0;
    R16(row+2u,word);d0=word;d3|=d2;W32(d3);d1|=d0;W32(d1);cursor+=2u;
    R16(row,type);
    if(type==1u){
     R16(row+34u,word);d0=(uint32_t)word<<16;R16(row+32u,word);d1=(uint32_t)word<<8;d0|=d1;
     R16(row+30u,word);d1=word;W32(0);d0|=d1;W32(d0);cursor++;
    }
    break;
   case 2:
    R32(row+10u,d0);d0<<=14;R16(row+4u,word);d1=(uint32_t)word<<3;d0|=d1;
    R16(row,word);d1=word;R32(row+6u,value);W32(value);d0|=d1;W32(d0);cursor++;break;
   case 3:
    R32(row+6u,value);index=value&0x3fffffffu;if(index>=count)return BIWN_DISPLAY_BAD_LINK;
    d1=links[index];d0=d1&0x7ff00u;d2=d0>>8;d1=(d1&0xffu)<<24;
    R16(row+2u,word);d0=(uint32_t)word<<14;d1|=d0;
    R16(row+4u,word);d0=((uint32_t)word<<3)&0xfff8u;d1|=d0;
    R16(row,word);d0=word;W32(d2);d1|=d0;W32(d1);
    /* Original type3 does not advance the packing cursor here. */
    break;
   case 4:
    R32(row+10u,d0);d0<<=4;R16(row+4u,word);d1=(uint32_t)(word&1u)<<3;d0|=d1;
    R16(row,word);d1=word;R32(row+6u,value);W32(value);d0|=d1;W32(d0);cursor++;stop=1;break;
   default:return BIWN_DISPLAY_BAD_LINK;
   }
  }
  i++;row+=36u;
 }while(!stop);
 *result=d0;return BIWN_DISPLAY_OK;
}
