/* Readable source10430 reconstruction. Local27B model authored the body
 * after two directed repairs; coordinator recovered the algorithm/API and
 * wrote original-opcode verification. No body edits after the accepted draft.
 * 1093 original comparisons /56 native crosschecks /28 host guards.
 * Public bus/fullD0 only: private stack, CCR, timing and frame substitution
 * are excluded. This upgrades an existing logical function, not a new count.
 */
#include "biwn_doorway_enter.h"
#include <stddef.h>

static uint32_t biwn_se16(uint16_t v) {
    return (uint32_t)((int16_t)v);
}

static uint32_t biwn_se8(uint8_t v) {
    return (uint32_t)((int8_t)v);
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

enum biwn_portal_status biwn_doorway_enter(struct biwn_world_bus *bus,
    uint32_t object, uint16_t door_index, uint16_t direction,
    uint32_t incoming_D1, uint32_t incoming_D3, uint32_t *out_D0)
{
    if (bus == NULL || out_D0 == NULL ||
        bus->read8 == NULL || bus->read16 == NULL || bus->read32 == NULL ||
        bus->write16 == NULL || bus->write32 == NULL) {
        return BIWN_PORTAL_BAD_ARGUMENT;
    }

    uint16_t tileIndex;
    if (bus->read16(bus->context, object + 64u, &tileIndex) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    uint32_t d0 = biwn_se16(tileIndex) * 4u;

    uint32_t tile;
    if (bus->read32(bus->context, 0x49BB4u + d0, &tile) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    uint16_t count;
    if (bus->read16(bus->context, tile + 2u, &count) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    if ((int16_t)door_index >= (int16_t)count) {
        *out_D0 = d0 & 0xFFFF0000u;
        return BIWN_PORTAL_OK;
    }

    d0 = biwn_se16(door_index) * 28u;

    uint32_t table;
    if (bus->read32(bus->context, tile + 12u, &table) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    d0 = d0 + table;
    uint32_t portal = d0;

    uint16_t target;
    if (bus->read16(bus->context, portal + 26u, &target) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    if (target == 0xFFFFu) {
        *out_D0 = d0 & 0xFFFF0000u;
        return BIWN_PORTAL_OK;
    }

    uint16_t keyWord = (uint16_t)(incoming_D1 & 0xFFFFu);
    uint16_t compareWord = (uint16_t)(incoming_D3 & 0xFFFFu);

    if (direction == 0u) {
        uint16_t a, b;
        if (bus->read16(bus->context, object + 6u, &a) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        if (bus->read16(bus->context, object + 78u, &b) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        uint8_t byte;
        if (bus->read8(bus->context, portal + 11u, &byte) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        compareWord = (uint16_t)(biwn_se8(byte) & 0xFFFFu);
    } else if (direction == 1u) {
        uint16_t a, b;
        if (bus->read16(bus->context, object + 74u, &a) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        if (bus->read16(bus->context, object + 6u, &b) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        uint8_t byte;
        if (bus->read8(bus->context, portal + 13u, &byte) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        compareWord = (uint16_t)(biwn_se8(byte) & 0xFFFFu);
    } else if (direction == 2u) {
        uint16_t a, b;
        if (bus->read16(bus->context, object + 82u, &a) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        if (bus->read16(bus->context, object + 12u, &b) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        uint8_t byte;
        if (bus->read8(bus->context, portal + 15u, &byte) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        compareWord = (uint16_t)(biwn_se8(byte) & 0xFFFFu);
    } else if (direction == 3u) {
        uint16_t a, b;
        if (bus->read16(bus->context, object + 12u, &a) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        if (bus->read16(bus->context, object + 86u, &b) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        keyWord = (uint16_t)((uint32_t)a - (uint32_t)b);
        uint8_t byte;
        if (bus->read8(bus->context, portal + 17u, &byte) != 0)
            return BIWN_PORTAL_BUS_ERROR;
        compareWord = (uint16_t)(biwn_se8(byte) & 0xFFFFu);
    }

    d0 = (d0 & 0xFFFF0000u) | (uint32_t)biwn_asr16(keyWord, 6u);

    if ((uint16_t)(d0 & 0x0Fu) != compareWord) {
        *out_D0 = d0 & 0xFFFF0000u;
        return BIWN_PORTAL_OK;
    }

    if (bus->write16(bus->context, object + 22u, 0u) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    if (bus->read16(bus->context, portal + 26u, &target) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    if (bus->write16(bus->context, object + 24u, target) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    uint16_t w;
    if (bus->read16(bus->context, portal + 18u, &w) != 0)
        return BIWN_PORTAL_BUS_ERROR;
    d0 = biwn_se16(w) * 64u;
    if (bus->write32(bus->context, object + 30u, d0) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    if (bus->read16(bus->context, portal + 20u, &w) != 0)
        return BIWN_PORTAL_BUS_ERROR;
    d0 = biwn_se16(w) * 64u;
    if (bus->write32(bus->context, object + 38u, d0) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    if (bus->read16(bus->context, portal + 22u, &w) != 0)
        return BIWN_PORTAL_BUS_ERROR;
    d0 = biwn_se16(w) * 64u;
    uint32_t origin;
    if (bus->read32(bus->context, object + 30u, &origin) != 0)
        return BIWN_PORTAL_BUS_ERROR;
    d0 = d0 + origin;
    if (bus->write32(bus->context, object + 26u, d0) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    if (bus->read16(bus->context, portal + 24u, &w) != 0)
        return BIWN_PORTAL_BUS_ERROR;
    d0 = biwn_se16(w) * 64u;
    if (bus->read32(bus->context, object + 38u, &origin) != 0)
        return BIWN_PORTAL_BUS_ERROR;
    d0 = d0 + origin;
    if (bus->write32(bus->context, object + 34u, d0) != 0)
        return BIWN_PORTAL_BUS_ERROR;

    *out_D0 = 1u;
    return BIWN_PORTAL_OK;
}
