#include "biwn_text.h"

static uint32_t extend16(uint32_t value)
{
    value&=0xffffu;
    return (value&0x8000u) ? value|0xffff0000u : value;
}

static enum biwn_text_result read8(struct biwn_text_bus *bus,uint32_t address,uint8_t *value)
{
    if (!bus->read_budget) return BIWN_TEXT_READ_LIMIT;
    bus->read_budget--;
    return bus->read8(bus->context,address,value) ? BIWN_TEXT_BUS_ERROR : BIWN_TEXT_OK;
}

static enum biwn_text_result read16(struct biwn_text_bus *bus,uint32_t address,uint16_t *value)
{
    if (!bus->read_budget) return BIWN_TEXT_READ_LIMIT;
    bus->read_budget--;
    return bus->read16(bus->context,address,value) ? BIWN_TEXT_BUS_ERROR : BIWN_TEXT_OK;
}

#define CHECK(expression) do { enum biwn_text_result status=(expression); if (status!=BIWN_TEXT_OK) return status; } while (0)
#define WRITE(address,value) do { if (bus->write32(bus->context,(address),(value))) return BIWN_TEXT_BUS_ERROR; } while (0)
#define BYTE(address,value) CHECK(read8(bus,(address),&(value)))
#define WORD(address,value) CHECK(read16(bus,(address),&(value)))

static int valid(struct biwn_text_bus *bus,const struct biwn_text_args *args,uint32_t *d0)
{
    return bus && args && d0 && bus->read8 && bus->read16 && bus->write32;
}

uint32_t biwn_text_alignment(uint16_t position,uint16_t width,uint16_t mask)
{
    uint16_t value=(uint16_t)(position+width)&mask;
    uint16_t result=(uint16_t)(0u-width);
    if (value) result=(uint16_t)(result-(uint16_t)(mask-(uint16_t)(value-1u)));
    return 0x10000u|result;
}

enum biwn_text_result biwn_text_draw_format3(struct biwn_text_bus *bus,const struct biwn_text_args *args,uint32_t *d0)
{
    uint8_t width,height,character,first,last;
    uint16_t source;
    uint32_t xy,result,count,mask,flags,font_flags,step_destination,step_source,command,amount;
    uint16_t word;
    uint32_t pointer;
    if (!valid(bus,args,d0)) return BIWN_TEXT_BAD_ARGUMENT;
    BYTE(args->font+2u,width);
    xy=((uint32_t)args->y<<16)|args->x;
    WRITE(0xf02224u,args->font+8u);WRITE(0xf02200u,args->target);
    flags=args->target_flags;
    switch (flags&0x38u) {
    case 0: case 8: case 16: mask=0;break;
    case 24: mask=7;break;
    case 32: mask=3;break;
    default: mask=1;break;
    }
    WORD(args->font+6u,word);font_flags=extend16(word)&0xfffcffffu;
    flags&=0xfffcffffu;
    if (!mask) { font_flags|=0x10000u;flags|=0x10000u; }
    WRITE(0xf02228u,font_flags);WRITE(0xf02204u,flags);
    WRITE(0xf02268u,0);WRITE(0xf0226cu,0);
    BYTE(args->font+3u,height);result=(uint32_t)height<<16;count=result|width;
    pointer=args->text;BYTE(pointer++,character);
    while (character) {
        BYTE(args->font+4u,first);
        if (character<first) last=0;
        else { BYTE(args->font+5u,last); }
        if (character<first || character>last) amount=width;
        else {
            source=(uint16_t)((uint32_t)(character-first)*width);
            step_destination=biwn_text_alignment((uint16_t)xy,width,(uint16_t)mask);
            step_source=biwn_text_alignment(source,width,(uint16_t)mask);
            if (step_source>step_destination) step_source-=(mask+1u)&15u;
            WRITE(0xf02210u,step_destination);WRITE(0xf02234u,step_source);
            WRITE(0xf02230u,extend16(source));WRITE(0xf0220cu,xy);WRITE(0xf0223cu,count);
            command=0x9800609u;
            if ((source&mask) && (xy&mask&7u)<(source&mask&7u)) command|=4u;
            WRITE(0xf02238u,command);amount=width;
        }
        xy+=amount;result+=amount;
        BYTE(pointer++,character);
    }
    *d0=result;return BIWN_TEXT_OK;
}

enum biwn_text_result biwn_text_draw(struct biwn_text_bus *bus,const struct biwn_text_args *args,uint32_t *d0)
{
    uint8_t type,byte,height,character,first,last;
    uint16_t rounded,shift,stride,glyph_width=0,columns,index,word,color,mode;
    uint32_t width_table=0,count=0,xy,command,flags,result,pointer;
    if (!valid(bus,args,d0)) return BIWN_TEXT_BAD_ARGUMENT;
    BYTE(args->font,type);
    if (type==3) return biwn_text_draw_format3(bus,args,d0);
    if (type==2) {
        BYTE(args->font+1u,byte);BYTE(args->font+3u,height);
        width_table=args->font+8u+(uint32_t)byte*height*2u;
    }
    BYTE(args->font+2u,byte);rounded=(uint16_t)((byte+7u)&0xfff8u);
    if (rounded==16) { shift=1;stride=2; }
    else if (rounded==24 || rounded==32) { shift=2;stride=4; }
    else { shift=0;stride=1; }
    if (!width_table) {
        BYTE(args->font+2u,byte);
        if (byte>8) { BYTE(args->font+2u,byte);glyph_width=(uint16_t)(((byte+7u)&7u)+1u); }
        else { BYTE(args->font+2u,byte);glyph_width=byte; }
        BYTE(args->font+3u,height);count=((uint32_t)height<<16)|glyph_width;
    }
    xy=((uint32_t)args->y<<16)|args->x;
    color=args->color;mode=args->mode;command=0x14010604u;flags=args->target_flags&0x38u;
    if (flags==0) { if (color) color=255;if (mode) mode=255;command=0x1401060cu; }
    else if (flags==8 || flags==16) {
        if (flags==8) { color=(uint16_t)(color|(uint16_t)(color<<2));mode=(uint16_t)(mode|(uint16_t)(mode<<2)); }
        color=(uint16_t)(color|(uint16_t)(color<<4));mode=(uint16_t)(mode|(uint16_t)(mode<<4));command=0x1401060cu;
    }
    WRITE(0xf02268u,color);
    if (mode) { WRITE(0xf02248u,mode); }
    else command|=8u;
    WRITE(0xf02224u,args->font+8u);WRITE(0xf02200u,args->target);
    WORD(args->font+6u,word);flags=extend16((uint16_t)((word&0x7e00u)-0x1800u))|0x10018u;
    WRITE(0xf02228u,flags);WRITE(0xf02204u,(args->target_flags&0xfffcffffu)|0x10000u);WRITE(0xf02234u,0x1ffffu);
    BYTE(args->font+3u,height);result=(uint32_t)height<<16;
    pointer=args->text;BYTE(pointer++,character);
    while (character) {
        BYTE(args->font+4u,first);
        if (character<first) last=0;
        else { BYTE(args->font+5u,last); }
        index=(character<first || character>last) ? 0 : (uint16_t)(character-first);
        if (width_table) {
            BYTE(width_table+index,byte);glyph_width=byte;columns=(uint16_t)((glyph_width+7u)>>3);
            if (glyph_width>8) glyph_width=(uint16_t)(((glyph_width-1u)&7u)+1u);
            BYTE(args->font+3u,height);count=((uint32_t)height<<16)|glyph_width;
            index=(uint16_t)(index<<shift);
            if (columns<stride) index=(uint16_t)(index+stride-columns);
        } else { columns=stride;index=(uint16_t)(index<<shift); }
        WRITE(0xf02230u,extend16(index));WRITE(0xf0220cu,xy);WRITE(0xf0223cu,count);
        WRITE(0xf02210u,0x10000u|(uint16_t)(0u-glyph_width));WRITE(0xf02238u,command);
        xy+=extend16(glyph_width);result+=extend16(glyph_width);
        if (columns>1) {
            columns--;index=(uint16_t)(index+1u);WRITE(0xf02210u,0x1fff8u);
            while (columns) {
                WRITE(0xf02230u,extend16(index));WRITE(0xf0220cu,xy);
                BYTE(args->font+3u,height);WRITE(0xf0223cu,((uint32_t)height<<16)|8u);WRITE(0xf02238u,command);
                xy+=8u;index=(uint16_t)(index+1u);result+=8u;columns--;
            }
        }
        BYTE(pointer++,character);
    }
    *d0=result;return BIWN_TEXT_OK;
}

#undef WORD
#undef BYTE
#undef WRITE
#undef CHECK
