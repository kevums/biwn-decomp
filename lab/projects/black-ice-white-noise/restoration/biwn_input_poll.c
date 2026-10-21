#include "biwn_input_poll.h"
static uint32_t ror32(uint32_t v,unsigned n){return(v>>n)|(v<<(32u-n));}
static uint32_t rol32(uint32_t v,unsigned n){return(v<<n)|(v>>(32u-n));}
enum biwn_input_status biwn_input_poll(struct biwn_world_bus *bus)
{
    uint32_t row,held=0xffffffffu,previous;
    if(!bus||!bus->read32||!bus->write16||!bus->write32)return BIWN_INPUT_BAD_ARGUMENT;
    if(bus->write16(bus->context,0xf14000u,0x810eu)||bus->read32(bus->context,0xf14000u,&row))return BIWN_INPUT_BUS_ERROR;
    held&=ror32(row|0xf0fffffcu,4);
    if(bus->write16(bus->context,0xf14000u,0x810du)||bus->read32(bus->context,0xf14000u,&row))return BIWN_INPUT_BUS_ERROR;
    held&=ror32(row|0xf0fffffcu,8);
    if(bus->write16(bus->context,0xf14000u,0x810bu)||bus->read32(bus->context,0xf14000u,&row))return BIWN_INPUT_BUS_ERROR;
    held&=rol32(rol32(row|0xf0fffffcu,6),6);
    if(bus->write16(bus->context,0xf14000u,0x8107u)||bus->read32(bus->context,0xf14000u,&row))return BIWN_INPUT_BUS_ERROR;
    held&=rol32(row|0xf0fffffcu,8);held=~held;
    if(bus->read32(bus->context,0x49ba4u,&previous))return BIWN_INPUT_BUS_ERROR;
    if(bus->write32(bus->context,0x49ba4u,held))return BIWN_INPUT_BUS_ERROR;
    if(bus->write32(bus->context,0x49bacu,(previous^held)&held))return BIWN_INPUT_BUS_ERROR;
    return BIWN_INPUT_OK;
}
