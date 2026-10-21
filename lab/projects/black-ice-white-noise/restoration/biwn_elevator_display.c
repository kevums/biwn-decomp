#include "biwn_elevator_display.h"
#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_ELEVATOR_DISPLAY_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_ELEVATOR_DISPLAY_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_ELEVATOR_DISPLAY_BUS_ERROR;}while(0)
#define W8(a,v) do {if(write8(bus->context,(a),(uint8_t)(v)))return BIWN_ELEVATOR_DISPLAY_BUS_ERROR;}while(0)
#define CALL(a,p,n) do {if(bus->call(bus->context,(a),(p),(n),&d0))return BIWN_ELEVATOR_DISPLAY_DEPENDENCY_ERROR;}while(0)
static uint32_t signed_word(uint16_t word){return(uint32_t)(word&0x7fffu)-(uint32_t)(word&0x8000u);}

enum biwn_elevator_display_status biwn_elevator_display(struct biwn_world_bus *bus,
 biwn_input_write8 write8,uint32_t scratch,uint32_t budget,
 uint32_t incoming_D0,uint32_t *out_D0)
{
 uint32_t d0=incoming_D0,pointer,target,args[3],i;uint16_t floor;uint8_t byte;
 if(!bus||!write8||!out_D0||!scratch||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->call)
  return BIWN_ELEVATOR_DISPLAY_BAD_ARGUMENT;
 R32(0x49c18u,pointer);R8(pointer+12u,byte);
 for(i=0;i<4u;i++){
  static const uint8_t down[4]={'D','O','W','N'};
  R32(0x410bau,target);W8(target+i,(byte&0x40u)?down[i]:' ');
 }
 R32(0x49c18u,pointer);R16(pointer+12u,floor);
 for(i=0;i<2u;i++){
  static const uint8_t up[2]={'U','P'};
  R32(0x410b2u,target);W8(target+i,(floor&0x8000u)?up[i]:' ');
 }
 R16(0x49c62u,floor);d0=(d0&0xffff0000u)|floor;
 if(!(floor&0x8000u))d0=(d0&0xffff0000u)|(uint16_t)(floor+1u);
 args[0]=scratch;args[1]=0x190b8u;args[2]=(uint16_t)d0;CALL(0x1b45au,args,3);
 R8(scratch,byte);if(byte=='-')W8(scratch,'B');
 for(i=0;i<4u;i++){R32(0x410b6u,target);W8(target+i,' ');}
 d0&=0xffff0000u;R8(scratch,byte);
 if(byte)do {
  if(!budget--)return BIWN_ELEVATOR_DISPLAY_LIMIT;
  R32(0x410b6u,target);R8(scratch+signed_word((uint16_t)d0),byte);
  W8(target+signed_word((uint16_t)d0),byte);
  d0=(d0&0xffff0000u)|(uint16_t)(d0+1u);
  R8(scratch+signed_word((uint16_t)d0),byte);
 }while(byte);
 args[0]=4u;CALL(0x12620u,args,1);
 *out_D0=d0;return BIWN_ELEVATOR_DISPLAY_OK;
}
