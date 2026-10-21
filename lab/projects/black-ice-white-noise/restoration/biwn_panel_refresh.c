#include "biwn_panel_refresh.h"
#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_PANEL_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_PANEL_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_PANEL_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,(a),(v)))return BIWN_PANEL_BUS_ERROR;}while(0)
#define WORK() do {if(!budget--)return BIWN_PANEL_LIMIT;}while(0)
static uint32_t sx(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
/* EXT.L of the low coordinate is ORed with the high word, deliberately:
 * a negative low coordinate fills the high half, as the source does. */
static uint32_t xy(uint16_t high,uint16_t low){return((uint32_t)high<<16)|sx(low);}

enum biwn_panel_status biwn_panel_refresh(struct biwn_world_bus *bus,uint16_t id,
 uint32_t budget,uint32_t *out_D0)
{
 uint32_t offset=sx(id)*14u,record=0x410beu+offset,d0=offset,value,text,args[8];
 uint16_t border,x,y,width,height,w,other,n,doubled;uint8_t byte,xbyte;
 if(!bus||!out_D0||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write32||!bus->call)
  return BIWN_PANEL_BAD_ARGUMENT;
 R16(record+8u,border);R32(0xbd830u,value);W32(0xf02200u,value);W32(0xf02204u,0x33e20u);
 R16(record+2u,y);R16(record+8u,w);y=(uint16_t)(y+w);
 R16(record,x);R16(record+8u,w);x=(uint16_t)(x+w);W32(0xf0220cu,xy(y,x));
 R16(record+8u,w);doubled=(uint16_t)(w*2u);R16(record+4u,width);
 w=(uint16_t)(width-doubled);W32(0xf02210u,sx((uint16_t)(224u-w)));
 W32(0xf02214u,0);W32(0xf02218u,0);W32(0xf02220u,0);W32(0xf0221cu,1);
 W32(0xf02268u,0x88808880u);W32(0xf0226cu,0x88808880u);
 R16(record+8u,w);doubled=(uint16_t)(w*2u);R16(record+6u,height);height=(uint16_t)(height-doubled);
 R16(record+4u,width);width=(uint16_t)(width-doubled);W32(0xf0223cu,xy(height,width));W32(0xf02238u,0x01810200u);
 if(border){
  R16(record+2u,y);R16(record,x);W32(0xf0220cu,xy(y,x));
  R16(record+4u,width);W32(0xf02210u,sx((uint16_t)(224u-width)));
  W32(0xf02268u,0x88c088c0u);W32(0xf0226cu,0x88c088c0u);
  R16(record+8u,height);R16(record+4u,width);W32(0xf0223cu,xy(height,width));W32(0xf02238u,0x01810200u);
  R16(record+2u,y);R16(record+6u,height);y=(uint16_t)(y+height-border);R16(record,x);W32(0xf0220cu,xy(y,x));
  R16(record+4u,width);W32(0xf02210u,sx((uint16_t)(224u-width)));
  W32(0xf02268u,0x88408840u);W32(0xf0226cu,0x88408840u);
  R16(record+8u,height);R16(record+4u,width);W32(0xf0223cu,xy(height,width));W32(0xf02238u,0x01810200u);
  n=(uint16_t)(border-1u);
  do {
   WORK();R16(record+2u,y);y=(uint16_t)(y+n);R16(record,x);R16(record+4u,width);
   x=(uint16_t)(x+width-n-1u);W32(0xf0220cu,xy(y,x));W32(0xf02210u,223u);
   W32(0xf02268u,0x88608860u);W32(0xf0226cu,0x88608860u);
   doubled=(uint16_t)(n*2u);R16(record+6u,height);height=(uint16_t)(height-doubled);
   W32(0xf0223cu,((uint32_t)height<<16)|1u);W32(0xf02238u,0x01810200u);
   R16(record+2u,y);y=(uint16_t)(y+n);R16(record,x);x=(uint16_t)(x+n);
   W32(0xf0220cu,xy(y,x));W32(0xf02210u,223u);
   W32(0xf02268u,0x88a088a0u);W32(0xf0226cu,0x88a088a0u);
   R16(record+6u,height);height=(uint16_t)(height-doubled);
   W32(0xf0223cu,((uint32_t)height<<16)|1u);W32(0xf02238u,0x01810200u);
   other=n;n=(uint16_t)(n-1u);
  }while(other);
 }
 d0=offset;R32(record+10u,text);
 do {
  WORK();R8(text,xbyte);text++;R8(text,byte);text++;
  d0=(d0&0xffff0000u)|byte;
  args[7]=0;args[6]=0x88ffu;args[5]=0x4c3e0u;args[4]=0x3e20u;R32(0xbd830u,args[3]);args[2]=text;
  R16(record+2u,y);d0=(d0&0xffff0000u)|(uint16_t)((uint16_t)d0+y);args[1]=(uint16_t)d0;
  R16(record,x);args[0]=(uint16_t)(xbyte+x);
  if(bus->call(bus->context,0x149aeu,args,8,&d0))return BIWN_PANEL_DEPENDENCY_ERROR;
  do {WORK();R8(text,byte);text++;}while(byte);
  R8(text,byte);
 }while(byte);
 *out_D0=d0;return BIWN_PANEL_OK;
}
