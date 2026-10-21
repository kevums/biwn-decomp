#include <stdint.h>

int biwn_local_portal_key(unsigned direction, uint16_t x, uint16_t z,
                          uint16_t min_x, uint16_t max_x, uint16_t min_z, uint16_t max_z,
                          uint8_t encoded_key, uint16_t *key_out) {
    if (key_out == 0) return -1;
    if (direction >= 4) return -1;

    uint16_t diff;
    if (direction == 0) diff = (uint16_t)(x - min_x);
    else if (direction == 1) diff = (uint16_t)(max_x - x);
    else if (direction == 2) diff = (uint16_t)(max_z - z);
    else diff = (uint16_t)(z - min_z);

    uint16_t shifted_key = (uint16_t)(diff >> 6);
    if (diff & 0x8000u) shifted_key |= 0xFC00u;

    *key_out = shifted_key;

    uint16_t ext_key;
    if (encoded_key & 0x80u) ext_key = (uint16_t)(encoded_key | 0xFF00u);
    else ext_key = (uint16_t)encoded_key;

    if ((shifted_key & 0x000Fu) == ext_key) return 1;
    return 0;
}

#include "biwn_geometry.h"
#define R8(a,v) do {if(bus->read8(bus->context,a,&(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,a,&(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,a,&(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,a,(uint16_t)(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,a,(uint32_t)(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define RETURN_D0(v) do {*out_d0=(v);return BIWN_GEOMETRY_OK;}while(0)
static uint32_t sx16(uint16_t v){return v&0x8000u ? (uint32_t)v|0xffff0000u : v;}
static int32_t signed16(uint16_t v){return (int32_t)(v&0x7fffu)-(int32_t)(v&0x8000u);}
static int less16(uint16_t a,uint16_t b){return (a^0x8000u)<(b^0x8000u);}
static int less32(uint32_t a,uint32_t b){return (a^0x80000000u)<(b^0x80000000u);}
static uint16_t asr_word6(uint16_t v){return (uint16_t)((v>>6)|(v&0x8000u ? 0xfc00u : 0));}
static uint32_t asr_long6(uint32_t v){return (v>>6)|(v&0x80000000u ? 0xfc000000u : 0);}
static uint32_t word_shift6(uint16_t v){return sx16((uint16_t)((uint32_t)v<<6));}
static uint32_t long_shift6(uint16_t v){return sx16(v)<<6;}

enum biwn_geometry_status biwn_geometry_outside(struct biwn_world_bus *bus,
    uint32_t object,uint32_t incoming_d0,uint32_t *out_d0)
{
    uint32_t position,bound;
    if(!bus || !out_d0 || !bus->read32)return BIWN_GEOMETRY_BAD_ARGUMENT;
    R32(object+4u,position);R32(object+0x1eu,bound);if(less32(position,bound))RETURN_D0(1);
    R32(object+4u,position);R32(object+0x1au,bound);if(!less32(position,bound))RETURN_D0(1);
    R32(object+10u,position);R32(object+0x26u,bound);if(less32(position,bound))RETURN_D0(1);
    R32(object+10u,position);R32(object+0x22u,bound);
    RETURN_D0((incoming_d0&0xffff0000u)|(less32(position,bound) ? 0u : 1u));
}

static enum biwn_geometry_status tile_bounds(struct biwn_world_bus *bus,uint32_t object,uint32_t record,uint16_t index)
{
    uint32_t origin,value;
    uint16_t word;
    W16(object+0x42u,index);W32(object+0x44u,record);
    R32(object+4u,origin);R16(record+10u,word);W32(object+0x4cu,(origin&0xfffffc00u)+word_shift6(word));
    R32(object+10u,origin);R16(record+14u,word);W32(object+0x54u,(origin&0xfffffc00u)+word_shift6(word));
    R16(record+16u,word);R32(object+0x4cu,value);W32(object+0x48u,value+word_shift6(word));
    R16(record+18u,word);R32(object+0x54u,value);W32(object+0x50u,value+word_shift6(word));
    return BIWN_GEOMETRY_OK;
}

enum biwn_geometry_status biwn_geometry_find_tile(struct biwn_world_bus *bus,
    uint32_t object,uint32_t scan_limit,uint32_t *out_d0)
{
    uint32_t result,container,record,base,scans=0;
    uint16_t room,x,z,index,word,extent;
    enum biwn_geometry_status status;
    int found=0;
    if(!bus || !out_d0 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !scan_limit)return BIWN_GEOMETRY_BAD_ARGUMENT;
    R16(object+0x40u,room);result=sx16(room)<<2;R32(0x49bb4u+result,container);
    R32(object+4u,result);result=asr_long6(result);x=(uint16_t)result&15u;
    R32(object+10u,result);result=asr_long6(result);z=(uint16_t)result&15u;
    R16(container,index);index=(uint16_t)((uint32_t)index-1u);
    if(index&0x8000u)RETURN_D0(result&0xffff0000u);
    do {
        if(scans++>=scan_limit)return BIWN_GEOMETRY_SCAN_LIMIT;
        result=(uint32_t)(signed16(index)*20);R32(container+8u,base);record=base+result;
        R16(record+10u,word);
        if(!less16(x,word)) {
            R16(record+10u,word);R16(record+16u,extent);word=(uint16_t)((uint32_t)word+extent);result=(result&0xffff0000u)|word;
            if(less16(x,word)) {
                R16(record+14u,word);
                if(!less16(z,word)) {
                    R16(record+14u,word);R16(record+18u,extent);word=(uint16_t)((uint32_t)word+extent);result=(result&0xffff0000u)|word;
                    if(less16(z,word)){found=1;break;}
                }
            }
        }
        index=(uint16_t)((uint32_t)index-1u);
    }while(index!=0xffffu);
    if(!found)RETURN_D0(result&0xffff0000u);
    status=tile_bounds(bus,object,record,index);if(status)return status;RETURN_D0(1);
}

enum biwn_geometry_status biwn_geometry_select_tile(struct biwn_world_bus *bus,
    uint32_t object,uint16_t index,uint32_t *out_d0)
{
    uint16_t room,count;
    uint32_t result,container,base,record;
    enum biwn_geometry_status status;
    if(!bus || !out_d0 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32)return BIWN_GEOMETRY_BAD_ARGUMENT;
    R16(object+0x40u,room);result=sx16(room)<<2;R32(0x49bb4u+result,container);R16(container,count);
    if(!less16(index,count))RETURN_D0(result&0xffff0000u);
    result=(uint32_t)(signed16(index)*20);R32(container+8u,base);record=base+result;
    status=tile_bounds(bus,object,record,index);if(status)return status;RETURN_D0(1);
}

enum biwn_geometry_status biwn_geometry_select_portal(struct biwn_world_bus *bus,
    uint32_t object,uint16_t index,uint16_t direction,uint32_t incoming_d1,uint32_t incoming_d3,uint32_t *out_d0)
{
    uint16_t room,count,a,b,key=(uint16_t)incoming_d1,match=(uint16_t)incoming_d3,word;
    uint8_t byte;
    uint32_t result,container,base,record,origin;
    if(!bus || !out_d0 || !bus->read8 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32)return BIWN_GEOMETRY_BAD_ARGUMENT;
    R16(object+0x40u,room);result=sx16(room)<<2;R32(0x49bb4u+result,container);R16(container+2u,count);
    if(!less16(index,count))RETURN_D0(result&0xffff0000u);
    result=(uint32_t)(signed16(index)*28);R32(container+12u,base);record=base+result;result=record;
    R16(record+26u,word);if(word==0xffffu)RETURN_D0(result&0xffff0000u);
    switch(direction) {
    case 0:R16(object+6u,a);R16(object+0x4eu,b);key=(uint16_t)((uint32_t)a-b);R8(record+11u,byte);match=(uint16_t)(byte&0x80u ? (uint16_t)byte|0xff00u : byte);break;
    case 1:R16(object+0x4au,a);R16(object+6u,b);key=(uint16_t)((uint32_t)a-b);R8(record+13u,byte);match=(uint16_t)(byte&0x80u ? (uint16_t)byte|0xff00u : byte);break;
    case 2:R16(object+0x52u,a);R16(object+12u,b);key=(uint16_t)((uint32_t)a-b);R8(record+15u,byte);match=(uint16_t)(byte&0x80u ? (uint16_t)byte|0xff00u : byte);break;
    case 3:R16(object+12u,a);R16(object+0x56u,b);key=(uint16_t)((uint32_t)a-b);R8(record+17u,byte);match=(uint16_t)(byte&0x80u ? (uint16_t)byte|0xff00u : byte);break;
    default:break;
    }
    {
        int matches;
        /* Delta already follows the original bus-read order above. The local
         * value helper handles word shift/sign-extension and key matching. */
        if(direction<4u)matches=biwn_local_portal_key(0,key,0,0,0,0,0,byte,&key);
        else{key=asr_word6(key);matches=match==(key&15u);}
        result=(result&0xffff0000u)|key;
        if(!matches)RETURN_D0(result&0xffff0000u);
    }
    W16(object+0x16u,0);R16(record+26u,word);W16(object+0x18u,word);
    R16(record+18u,word);W32(object+0x1eu,long_shift6(word));
    R16(record+20u,word);W32(object+0x26u,long_shift6(word));
    R16(record+22u,word);R32(object+0x1eu,origin);W32(object+0x1au,origin+long_shift6(word));
    R16(record+24u,word);R32(object+0x26u,origin);W32(object+0x22u,origin+long_shift6(word));
    RETURN_D0(1);
}

enum biwn_geometry_status biwn_geometry_select_region(struct biwn_world_bus *bus,
    uint32_t object,uint16_t index,uint32_t incoming_d0,uint32_t *out_d0)
{
    uint16_t count,word;
    uint32_t container,base,record,origin;
    if(!bus || !out_d0 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32)return BIWN_GEOMETRY_BAD_ARGUMENT;
    R32(0x49c18u,container);R16(container,count);
    if(!less16(index,count))RETURN_D0(incoming_d0&0xffff0000u);
    R32(container+4u,base);record=base+(uint32_t)(signed16(index)*24);
    W16(object+0x2au,index);W32(object+0x2cu,record);
    R16(record+2u,word);R32(object+0x1eu,origin);W32(object+0x34u,origin+word_shift6(word));
    R16(record+4u,word);R32(object+0x26u,origin);W32(object+0x3cu,origin+word_shift6(word));
    R16(record+6u,word);R32(object+0x34u,origin);W32(object+0x30u,origin+word_shift6(word));
    R16(record+8u,word);R32(object+0x3cu,origin);W32(object+0x38u,origin+word_shift6(word));
    RETURN_D0(1);
}
