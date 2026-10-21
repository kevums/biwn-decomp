#include "interior-select-native.h"
static uint32_t extend_word(uint16_t v) { return (uint32_t)(int32_t)(int16_t)v; }
uint32_t biwn_interior_select_kernel(uint32_t object, uint32_t kind, uint32_t *out)
{
    volatile struct biwn_interior_actor *actor=(volatile struct biwn_interior_actor *)object;
    volatile struct biwn_interior_sprite *sprite=(volatile struct biwn_interior_sprite *)object;
    uint32_t header=*(volatile uint32_t *)0x49c18u;
    volatile struct biwn_interior_header *h=(volatile struct biwn_interior_header *)header;
    uint32_t x, z, origin, d0, record=0, xbit;
    if (!kind) {
        x=actor->x; origin=actor->origin_x; x=(x-origin)>>6;
        d0=actor->z; origin=actor->origin_z;
    } else {
        x=sprite->x; origin=*(volatile uint32_t *)0x49c6au; x=(x-origin)>>6;
        d0=sprite->z; origin=*(volatile uint32_t *)0x49c72u;
    }
    d0-=origin; z=d0>>6;
    uint16_t count=h->count, i=(uint16_t)(count-1u);
    xbit=count==0;
    if (!kind) out[1]=header; else out[2]=header;
    if (!(i&0x8000u)) {
        for (;;) {
            d0=extend_word(i)*24u;
            uint32_t base=h->records;
            record=base+d0;
            volatile struct biwn_interior_record *r=(volatile struct biwn_interior_record *)record;
            if (!kind) out[2]=record; else out[1]=record;
            uint16_t lower=r->x;
            if ((int16_t)(uint16_t)x>=(int16_t)lower) {
                lower=r->x; uint16_t width=r->width;
                uint32_t sum=(uint32_t)lower+width;
                xbit=sum>65535u; d0=(d0&0xffff0000u)|(uint16_t)sum;
                if ((int16_t)(uint16_t)x<(int16_t)(uint16_t)d0) {
                    lower=r->z;
                    if ((int16_t)(uint16_t)z>=(int16_t)lower) {
                        lower=r->z; uint16_t depth=r->depth;
                        sum=(uint32_t)lower+depth;
                        xbit=sum>65535u; d0=(d0&0xffff0000u)|(uint16_t)sum;
                        if ((int16_t)(uint16_t)z<(int16_t)(uint16_t)d0) break;
                    }
                }
            }
            i=(uint16_t)(i-1u);
            if (i==0xffffu) break;
        }
    }
    out[0]=(out[0]&0xffff0000u)|i;
    if (i&0x8000u) {out[3]=4u|(xbit?16u:0u);return d0&0xffff0000u;}
    if (kind) {sprite->selected=i;out[3]=xbit?16u:0u;return 1;}
    actor->selected=i; actor->record=record;
    volatile struct biwn_interior_record *r=(volatile struct biwn_interior_record *)record;
    uint16_t w=r->x; uint32_t scaled=extend_word((uint16_t)(w<<6));
    origin=actor->origin_x; actor->lower_x=origin+scaled;
    w=r->z; scaled=extend_word((uint16_t)(w<<6));
    origin=actor->origin_z; actor->lower_z=origin+scaled;
    w=r->width; scaled=extend_word((uint16_t)(w<<6));
    origin=actor->lower_x; actor->upper_x=origin+scaled;
    w=r->depth; scaled=extend_word((uint16_t)(w<<6));
    origin=actor->lower_z; uint32_t upper=origin+scaled; actor->upper_z=upper;
    out[1]=upper; out[3]=(w&0x400u)?16u:0u;
    return 1;
}
