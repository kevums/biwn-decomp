#include "doorway-native.h"
#include <stdint.h>

static uint32_t biwn_se16(uint16_t v) {
    return (uint32_t)(int16_t)v;
}

static uint32_t biwn_se8(uint8_t v) {
    return (uint32_t)(int8_t)v;
}

static uint16_t biwn_asr16(uint16_t v, uint32_t sh) {
    uint32_t u = (uint32_t)v;
    if (sh >= 16u) {
        return (u & 0x8000u) ? (uint16_t)0xFFFFu : (uint16_t)0u;
    }
    uint32_t shifted = u >> sh;
    if (u & 0x8000u) {
        shifted |= (0xFFFFFFFFu << (16u - sh));
    }
    return (uint16_t)(shifted & 0xFFFFu);
}

uint32_t biwn_doorway_kernel(uint32_t object, uint32_t requested, uint32_t direction,
                             uint32_t incoming_D1, uint32_t incoming_D3, uint32_t *out)
{
    volatile struct biwn_door_actor *actor = (volatile struct biwn_door_actor *)object;
    uint32_t d0, d1, a0;
    uint32_t ccr;

    uint16_t sector = actor->sector;
    d0 = biwn_se16(sector) * 4u;

    volatile uint32_t *table_slot = (volatile uint32_t *)(0x49BB4u + d0);
    uint32_t header_ptr = *table_slot;
    volatile struct biwn_door_header *header = (volatile struct biwn_door_header *)header_ptr;
    uint16_t count = header->count;

    if ((int16_t)requested >= (int16_t)count) {
        d0 = d0 & 0xFFFF0000u;
        d1 = incoming_D1;
        a0 = header_ptr;
        ccr = 4u | (sector & 0x8000u ? 16u : 0u);
        out[0] = d1;
        out[1] = a0;
        out[2] = ccr & 0x1Fu;
        return d0;
    }

    d0 = biwn_se16((uint16_t)requested) * 28u;
    uint32_t records_base = header->records;
    d0 = d0 + records_base;
    a0 = d0;

    volatile struct biwn_door_record *record = (volatile struct biwn_door_record *)a0;
    uint16_t target = record->target;

    if (target == 0xFFFFu) {
        d0 = a0 & 0xFFFF0000u;
        d1 = incoming_D1;
        ccr = 4u | ((records_base + biwn_se16((uint16_t)requested) * 28u) < records_base ? 16u : 0u);
        out[0] = d1;
        out[1] = a0;
        out[2] = ccr & 0x1Fu;
        return d0;
    }

    uint16_t keyWord = (uint16_t)(incoming_D1 & 0xFFFFu);
    uint16_t compareWord = (uint16_t)(incoming_D3 & 0xFFFFu);

    if (direction == 0u) {
        uint16_t a = actor->x_low;
        uint16_t b = actor->lower_x_low;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        compareWord = (uint16_t)(biwn_se8(record->west) & 0xFFFFu);
    } else if (direction == 1u) {
        uint16_t a = actor->upper_x_low;
        uint16_t b = actor->x_low;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        compareWord = (uint16_t)(biwn_se8(record->east) & 0xFFFFu);
    } else if (direction == 2u) {
        uint16_t a = actor->upper_z_low;
        uint16_t b = actor->z_low;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        compareWord = (uint16_t)(biwn_se8(record->north) & 0xFFFFu);
    } else if (direction == 3u) {
        uint16_t a = actor->z_low;
        uint16_t b = actor->lower_z_low;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        compareWord = (uint16_t)(biwn_se8(record->south) & 0xFFFFu);
    }

    uint16_t asr_result = biwn_asr16(keyWord, 6u);
    uint16_t nibble = (uint16_t)(asr_result & 0x0Fu);
    d1 = (incoming_D1 & 0xFFFF0000u) | (uint32_t)nibble;

    if (compareWord != nibble) {
        d0 = a0 & 0xFFFF0000u;
        ccr = 4u | ((keyWord & 0x0020u) ? 16u : 0u);
        out[0] = d1;
        out[1] = a0;
        out[2] = ccr & 0x1Fu;
        return d0;
    }

    actor->transition = 0u;
    target = record->target;
    actor->target = target;

    uint16_t w;
    w = record->x;
    d0 = biwn_se16(w) << 6;
    actor->entry_base_x = d0;

    w = record->z;
    d0 = biwn_se16(w) << 6;
    actor->entry_base_z = d0;

    w = record->width;
    d0 = biwn_se16(w) << 6;
    uint32_t origin = actor->entry_base_x;
    d0 = d0 + origin;
    actor->entry_upper_x = d0;

    w = record->depth;
    d0 = biwn_se16(w) << 6;
    origin = actor->entry_base_z;
    uint32_t sum = d0 + origin;
    uint32_t carry = (sum < origin) ? 1u : 0u;
    actor->entry_upper_z = sum;

    d0 = 1u;
    ccr = carry ? 16u : 0u;
    out[0] = d1;
    out[1] = a0;
    out[2] = ccr & 0x1Fu;
    return d0;
}
