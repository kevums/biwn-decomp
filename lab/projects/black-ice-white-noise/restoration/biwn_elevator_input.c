#include "biwn_elevator_input.h"

#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_ELEVATOR_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_ELEVATOR_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_ELEVATOR_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_ELEVATOR_BUS_ERROR;}while(0)
#define CALL(a,p,n) do {if(bus->call(bus->context,(a),(p),(n),&d0))return BIWN_ELEVATOR_DEPENDENCY_ERROR;}while(0)

enum biwn_elevator_status biwn_elevator_input(struct biwn_world_bus *bus,
 uint32_t incoming_D0,uint32_t *out_D0)
{
 uint32_t d0=incoming_D0,pointer,argument=2u;uint16_t word;uint8_t held;int down;
 if(!bus||!out_D0||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->call)
  return BIWN_ELEVATOR_BAD_ARGUMENT;
 R16(0x49c60u,word);if(word!=2u)goto done;
 R32(0x49c78u,pointer);d0=(d0&0xffff0000u)|0x8000u;
 R16(pointer,word);if(!(word&0x8000u))goto done;
 R8(0x49ba5u,held);
 if(held&0x10u) {
  R32(0x49c18u,pointer);R16(pointer+12u,word);
  d0=(d0&0xffff0000u)|((uint16_t)d0&word);
  if(!(uint16_t)d0)goto done;
  down=0;
 }else {
  /* The source rereads input and tests a byte of the permission word. */
  R8(0x49ba5u,held);if(!(held&0x20u))goto done;
  R32(0x49c18u,pointer);R8(pointer+12u,held);if(!(held&0x40u))goto done;
  down=1;
 }
 W16(0x49c60u,0);CALL(0x20f0cu,0,0);
 R16(0x49c62u,word);W16(0x49c62u,down?(uint32_t)word-1u:(uint32_t)word+1u);
 R16(0x49c64u,word);W16(0x49c64u,down?(uint32_t)word-1u:(uint32_t)word+1u);
 CALL(0x20f78u,&argument,1);
done:
 *out_D0=d0;return BIWN_ELEVATOR_OK;
}
