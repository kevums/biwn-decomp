#include "biwn_sprite_decode.h"

struct bitstream {
    struct biwn_sprite_bus *bus;
    uint32_t source,reservoir;
    int left;
};

#define CHECK(expression) do { enum biwn_sprite_status status=(expression);if (status!=BIWN_SPRITE_OK) return status; } while (0)

static enum biwn_sprite_status read_byte(struct biwn_sprite_bus *bus,uint32_t address,uint8_t *value)
{
    if (!bus->read_budget) return BIWN_SPRITE_READ_LIMIT;
    bus->read_budget--;
    return bus->read8(bus->context,address,value) ? BIWN_SPRITE_BUS_ERROR : BIWN_SPRITE_OK;
}

static enum biwn_sprite_status read_word(struct biwn_sprite_bus *bus,uint32_t address,uint16_t *value)
{
    if (!bus->read_budget) return BIWN_SPRITE_READ_LIMIT;
    bus->read_budget--;
    return bus->read16(bus->context,address,value) ? BIWN_SPRITE_BUS_ERROR : BIWN_SPRITE_OK;
}

static enum biwn_sprite_status read_long(struct biwn_sprite_bus *bus,uint32_t address,uint32_t *value)
{
    if (!bus->read_budget) return BIWN_SPRITE_READ_LIMIT;
    bus->read_budget--;
    return bus->read32(bus->context,address,value) ? BIWN_SPRITE_BUS_ERROR : BIWN_SPRITE_OK;
}

static enum biwn_sprite_status next_bit(struct bitstream *stream,uint32_t *value)
{
    uint8_t byte;
    if (!stream->left) {
        CHECK(read_byte(stream->bus,stream->source,&byte));stream->source++;
        stream->reservoir=byte;stream->left=8;
    }
    *value=(stream->reservoir>>7)&1u;
    stream->left--;stream->reservoir<<=1;
    return BIWN_SPRITE_OK;
}

static enum biwn_sprite_status next_field(struct bitstream *stream,unsigned width,uint32_t *value)
{
    uint8_t byte;
    stream->left-=(int)width;stream->reservoir<<=width;
    if (stream->left<0) {
        CHECK(read_byte(stream->bus,stream->source,&byte));stream->source++;
        stream->reservoir|=(uint32_t)byte<<(unsigned)-stream->left;stream->left+=8;
    }
    *value=(stream->reservoir>>8)&((1u<<width)-1u);
    return BIWN_SPRITE_OK;
}

enum biwn_sprite_status biwn_sprite_decode(struct biwn_sprite_bus *bus,uint32_t base,uint32_t index,uint32_t destination,struct biwn_sprite_result *result)
{
    struct bitstream stream;
    struct biwn_sprite_result output;
    uint32_t offset,palette_offset,first,second,length,i,counter;
    uint8_t byte,width,height,palette_index;
    uint16_t color;
    if (!bus || !result || !bus->read8 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32)
        return BIWN_SPRITE_BAD_ARGUMENT;
    CHECK(read_long(bus,base+4u,&palette_offset));output.palette=base+palette_offset;
    CHECK(read_long(bus,base+12u+(index<<2),&offset));stream.source=base+offset;
    CHECK(read_byte(bus,stream.source++,&width));CHECK(read_byte(bus,stream.source++,&height));
    CHECK(read_byte(bus,stream.source++,&byte));output.origin_x=(int16_t)(byte<128 ? byte : (int)byte-256);
    if (bus->write16(bus->context,destination-12u,(uint16_t)output.origin_x)) return BIWN_SPRITE_BUS_ERROR;
    CHECK(read_byte(bus,stream.source++,&byte));output.origin_y=(int16_t)(byte<128 ? byte : (int)byte-256);
    if (bus->write16(bus->context,destination-10u,(uint16_t)output.origin_y)) return BIWN_SPRITE_BUS_ERROR;
    output.width=width;output.height=height;output.declared_pixels=(uint32_t)width*height;output.emitted_pixels=0;
    counter=output.declared_pixels-1u;stream.bus=bus;stream.left=0;stream.reservoir=0;
    do {
        CHECK(next_bit(&stream,&first));
        if (first) {
            CHECK(next_field(&stream,4,&length));length+=2u;color=0;
        } else {
            CHECK(next_bit(&stream,&second));
            CHECK(next_field(&stream,second ? 3u : 4u,&length));length+=second ? 2u : 1u;
            if (second) {
                CHECK(read_byte(bus,stream.source++,&palette_index));
                CHECK(read_word(bus,output.palette+((uint32_t)palette_index<<1),&color));
            } else {
                counter-=length;
                CHECK(read_byte(bus,stream.source,&palette_index));
                for (i=0;i<length;i++) {
                    stream.source++;
                    CHECK(read_word(bus,output.palette+((uint32_t)palette_index<<1),&color));
                    if (bus->write16(bus->context,destination,color)) return BIWN_SPRITE_BUS_ERROR;
                    destination+=2u;output.emitted_pixels++;
                    /* Original delay-slot LOADB runs after the last item too. */
                    CHECK(read_byte(bus,stream.source,&palette_index));
                }
                continue;
            }
        }
        counter-=length;
        for (i=0;i<length;i++) {
            if (bus->write16(bus->context,destination,color)) return BIWN_SPRITE_BUS_ERROR;
            destination+=2u;output.emitted_pixels++;
        }
    } while (!(counter&0x80000000u));
    if (bus->write32(bus->context,0xf0211cu,0)) return BIWN_SPRITE_BUS_ERROR;
    output.source_next=stream.source;output.destination_next=destination;
    output.remaining_counter=counter;output.reservoir=stream.reservoir;output.bits_left=(uint32_t)stream.left;
    *result=output;return BIWN_SPRITE_OK;
}

#undef CHECK
