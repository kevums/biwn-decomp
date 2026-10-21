#include "biwn_debug_overlay.h"
int biwn_debug_overlay(struct biwn_world_bus *bus, uint32_t scratch, uint32_t incoming_D0, uint32_t *out_D0) {
    if (!bus || !bus->read16 || !bus->read32 || !bus->write32 || !bus->call || !out_D0) {
        return BIWN_WORLD_BAD_ARGUMENT;
    }

    uint32_t d0 = incoming_D0;

    if (bus->write32(bus->context, 0xF02268, 0) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write32(bus->context, 0xF0226C, 0) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write32(bus->context, 0xF02200, 0xB29D0) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write32(bus->context, 0xF02204, 0x1820) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write32(bus->context, 0xF0220C, 0) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write32(bus->context, 0xF0223C, 0x113B0) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write32(bus->context, 0xF02238, 0x10200) != 0) return BIWN_WORLD_BUS_ERROR;

    uint16_t flag;
    if (bus->read16(bus->context, 0x403CC, &flag) != 0) return BIWN_WORLD_BUS_ERROR;
    if (flag == 0) {
        *out_D0 = d0;
        return BIWN_WORLD_OK;
    }

    struct {
        uint32_t value_addr;
        uint32_t format_addr;
        uint16_t x;
        uint16_t y;
    } rows[8] = {
        {0x400EC, 0x106E0, 0x14, 0x02},
        {0x400F0, 0x106EB, 0x14, 0x0C},
        {0x400F4, 0x106F6, 0x14, 0x16},
        {0x400FC, 0x10701, 0x78, 0x02},
        {0x400F8, 0x1070C, 0x78, 0x0C},
        {0x40100, 0x10717, 0x78, 0x16},
        {0x403D0, 0x10722, 0x14, 0x20},
        {0x403CA, 0x10730, 0x14, 0x2A}
    };

    for (int i = 0; i < 8; i++) {
        uint32_t value;
        if (i < 6) {
            if (bus->read32(bus->context, rows[i].value_addr, &value) != 0) return BIWN_WORLD_BUS_ERROR;
        } else if (i == 6) {
            uint16_t v16;
            if (bus->read16(bus->context, rows[i].value_addr, &v16) != 0) return BIWN_WORLD_BUS_ERROR;
            value = (v16 < 32768) ? (uint32_t)v16 : ((uint32_t)v16 | 0xFFFF0000u);
        } else {
            uint16_t v16;
            if (bus->read16(bus->context, rows[i].value_addr, &v16) != 0) return BIWN_WORLD_BUS_ERROR;
            value = (uint32_t)v16 * 24u + 0x3FB0Cu;
            d0 = value;
        }

        uint32_t fmt_args[3] = {scratch, rows[i].format_addr, value};
        if (bus->call(bus->context, 0x1B45A, fmt_args, 3, &d0) != 0) return BIWN_WORLD_DEPENDENCY_ERROR;

        uint32_t text_args[8] = {rows[i].x, rows[i].y, scratch, 0xB29D0, 0x3E08, 0x4C3E0, 3, 0};
        if (bus->call(bus->context, 0x149AE, text_args, 8, &d0) != 0) return BIWN_WORLD_DEPENDENCY_ERROR;
    }

    *out_D0 = d0;
    return BIWN_WORLD_OK;
}
