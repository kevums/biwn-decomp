#include "biwn_inventory_draw.h"

#define CHECK_BUS(expression) do { if (expression) return BIWN_DRAW_BUS_ERROR; } while (0)
#define CHECK_RESULT(expression) do { \
    enum biwn_inventory_draw_result checked=(expression); \
    if (checked!=BIWN_DRAW_OK) return checked; \
} while (0)
#define WRITE(address,value) CHECK_BUS(bus->write32(bus->context,(address),(value)))

static int32_t signed16(uint32_t value)
{
    value&=0xffffu;
    return value<0x8000u ? (int32_t)value : (int32_t)value-65536;
}

static int32_t signed8(uint8_t value)
{
    return value<128u ? (int32_t)value : (int32_t)value-256;
}

static uint32_t extend16(uint32_t value)
{
    value&=0xffffu;
    return (value&0x8000u) ? value|0xffff0000u : value;
}

static enum biwn_inventory_draw_result slot_index(struct biwn_inventory_draw_bus *bus,unsigned row,int32_t *index)
{
    uint16_t start;
    CHECK_BUS(bus->read16(bus->context,0x49d54u,&start));
    *index=signed16((uint16_t)(start+row))%10;
    return BIWN_DRAW_OK;
}

static void money_string(uint32_t money,char output[24])
{
    char reverse[10];
    unsigned n=0,i=0;
    uint32_t magnitude=(money&0x80000000u) ? 0u-money : money;
    output[i++]='$';
    if (money&0x80000000u) output[i++]='-';
    do { reverse[n++]=(char)('0'+magnitude%10u);magnitude/=10u; } while (magnitude);
    while (n) output[i++]=reverse[--n];
    output[i]='\0';
}

static enum biwn_inventory_draw_result label_pointer(struct biwn_inventory_draw_bus *bus,unsigned row,unsigned field,uint32_t *pointer)
{
    int32_t index,mapped;
    uint16_t item;
    uint8_t byte;
    CHECK_RESULT(slot_index(bus,row,&index));
    CHECK_BUS(bus->read16(bus->context,0x49d2cu+(uint32_t)(index*2),&item));
    CHECK_BUS(bus->read8(bus->context,0x42000u+(uint32_t)signed16(item),&byte));
    mapped=signed8(byte);
    CHECK_BUS(bus->read32(bus->context,0x46a60u+(uint32_t)(mapped*22)+(uint32_t)field,pointer));
    return BIWN_DRAW_OK;
}

enum biwn_inventory_draw_result biwn_inventory_draw(struct biwn_inventory_draw_bus *bus)
{
    struct biwn_inventory_text text;
    char money[24];
    uint32_t value,frame_address,offset,flags,target;
    uint16_t selected,item;
    uint8_t byte,height,width;
    int32_t index,mapped;
    unsigned row,line;
    if (!bus || !bus->read8 || !bus->read16 || !bus->read32 || !bus->write32 || !bus->sprite || !bus->text)
        return BIWN_DRAW_BAD_ARGUMENT;
    WRITE(0xf02200u,0xb5130u);
    WRITE(0xf02204u,0x33420u);
    WRITE(0xf0220cu,0);WRITE(0xf02210u,0);WRITE(0xf02214u,0);WRITE(0xf02218u,0);
    WRITE(0xf02220u,0);WRITE(0xf0221cu,1);
    WRITE(0xf02224u,0x69a60u);WRITE(0xf02228u,0x13420u);
    WRITE(0xf02230u,0);WRITE(0xf02234u,0);
    WRITE(0xf0223cu,0x10780u);WRITE(0xf02238u,0x1800601u);
    CHECK_BUS(bus->read32(bus->context,0x49d1eu,&value));money_string(value,money);
    text.x=0x14;text.y=5;text.text_address=0;text.target=0xb5130u;text.target_flags=0x3420u;
    text.font=0x4c3e0u;text.color=0x7fc0;text.mode=1;text.local_text=money;
    if (bus->text(bus->context,&text)) return BIWN_DRAW_DEPENDENCY_ERROR;
    for (row=0;row<5;row++) {
        target=0xb5130u+(0x780u+row*0xc00u)*2u;
        WRITE(0xf02200u,target);WRITE(0xf02204u,0x33420u);WRITE(0xf0220cu,0);
        CHECK_RESULT(slot_index(bus,row,&index));CHECK_BUS(bus->read16(bus->context,0x49d56u,&selected));
        WRITE(0xf02224u,index==signed16(selected) ? 0x68260u : 0x66a60u);
        WRITE(0xf02228u,0x13420u);WRITE(0xf02230u,0);WRITE(0xf02234u,0);
        WRITE(0xf0223cu,0x10c00u);WRITE(0xf02238u,0x9800609u);
        WRITE(0xf02268u,0);WRITE(0xf0226cu,0);
        CHECK_RESULT(slot_index(bus,row,&index));
        CHECK_BUS(bus->read16(bus->context,0x49d2cu+(uint32_t)(index*2),&item));
        CHECK_BUS(bus->read8(bus->context,0x42000u+(uint32_t)signed16(item),&byte));mapped=signed8(byte);
        CHECK_BUS(bus->read32(bus->context,0x6e6acu+(uint32_t)(mapped*4),&offset));frame_address=0x6e6a0u+offset;
        CHECK_BUS(bus->read16(bus->context,0x49d2cu+(uint32_t)(index*2),&item));
        if (item) {
            if (bus->sprite(bus->context,0x6e6a0u,(uint32_t)mapped,0x10a688u)) return BIWN_DRAW_DEPENDENCY_ERROR;
            WRITE(0xf02200u,target);WRITE(0xf02204u,0x33420u);
            CHECK_BUS(bus->read8(bus->context,frame_address+1u,&height));
            value=(uint32_t)(uint16_t)(16u-(height>>1))<<16;
            CHECK_BUS(bus->read8(bus->context,frame_address,&width));
            value|=extend16(94u-width);WRITE(0xf0220cu,value);
            CHECK_BUS(bus->read8(bus->context,frame_address,&width));WRITE(0xf02210u,extend16(96u-width));
            WRITE(0xf02224u,0x10a688u);
            CHECK_BUS(bus->read8(bus->context,frame_address,&width));
            CHECK_BUS(bus->read32(bus->context,0x3bd20u+(uint32_t)width*4u,&flags));WRITE(0xf02228u,flags^0x20000u);
            WRITE(0xf02230u,0);
            CHECK_BUS(bus->read8(bus->context,frame_address+1u,&height));
            CHECK_BUS(bus->read8(bus->context,frame_address,&width));
            WRITE(0xf0223cu,((uint32_t)height<<16)|width);WRITE(0xf02238u,0x9800609u);
            for (line=0;line<3;line++) {
                CHECK_RESULT(label_pointer(bus,row,10u+line*4u,&value));
                text.x=0x10;text.y=(uint16_t)(1u+line*10u);text.text_address=value;text.target=target;text.target_flags=0x3420u;
                text.font=0x4cca0u;text.color=2;text.mode=0;text.local_text=0;
                if (bus->text(bus->context,&text)) return BIWN_DRAW_DEPENDENCY_ERROR;
            }
        }
        WRITE(0xf02200u,target);WRITE(0xf02204u,0x33420u);WRITE(0xf0220cu,0xa0003u);WRITE(0xf02210u,0x54u);
        CHECK_RESULT(slot_index(bus,row,&index));
        CHECK_BUS(bus->read32(bus->context,0x468a0u+(uint32_t)(index*4),&value));WRITE(0xf02224u,value);
        WRITE(0xf02228u,0x11c20u);WRITE(0xf02230u,0);WRITE(0xf02234u,0);WRITE(0xf02268u,0);WRITE(0xf0226cu,0);
        WRITE(0xf0223cu,0xb000cu);WRITE(0xf02238u,0x9800609u);
    }
    return BIWN_DRAW_OK;
}

#undef WRITE
#undef CHECK_RESULT
#undef CHECK_BUS
