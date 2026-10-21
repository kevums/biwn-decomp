#include "biwn_overlay_format.h"
#include <stdio.h>
static int signed_word(uint16_t v){return(int)(v&0x7fffu)-(int)(v&0x8000u);}
enum biwn_overlay_status biwn_overlay_format(struct biwn_world_bus *bus,biwn_input_write8 write8,
 uint32_t destination,uint32_t format,uint16_t x,uint16_t z,uint16_t sector,uint32_t *out)
{
 const char *literal;char text[50];uint8_t byte;unsigned i;int count;
 if(!bus||!write8||!out||!bus->read8||(format!=0x181dau&&format!=0x181e9u))return BIWN_OVERLAY_BAD_ARGUMENT;
 literal=format==0x181dau?" %03d:%03d:B%d":" %03d:%03d:%d";
 for(i=0;;i++){
  if(bus->read8(bus->context,format+i,&byte))return BIWN_OVERLAY_BUS_ERROR;
  if(byte!=(uint8_t)literal[i])return BIWN_OVERLAY_BAD_ARGUMENT;
  if(!byte)break;
 }
 count=snprintf(text,sizeof text,literal,signed_word(x),signed_word(z),signed_word(sector));
 if(count<0||(unsigned)count>=sizeof text)return BIWN_OVERLAY_BAD_ARGUMENT;
 for(i=0;i<=(unsigned)count;i++)if(write8(bus->context,destination+i,(uint8_t)text[i]))return BIWN_OVERLAY_BUS_ERROR;
 *out=(uint32_t)count;return BIWN_OVERLAY_OK;
}
