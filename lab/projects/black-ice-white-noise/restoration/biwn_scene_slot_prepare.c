#include "biwn_scene_slot_prepare.h"
int biwn_scene_slot_prepare(struct biwn_world_bus *bus, uint32_t incoming_D0, uint32_t *out_D0) {
    (void)incoming_D0;
    if (!bus || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !bus->call || !out_D0) {
        return BIWN_WORLD_BAD_ARGUMENT;
    }

    uint32_t val;
    if (bus->read32(bus->context, 0x49B88u, &val) != 0) return BIWN_WORLD_BUS_ERROR;
    val = val + 1u;
    if (bus->write32(bus->context, 0x49B88u, val) != 0) return BIWN_WORLD_BUS_ERROR;

    if (bus->read32(bus->context, 0x49B88u, &val) != 0) return BIWN_WORLD_BUS_ERROR;
    uint32_t d0 = val << 6u;
    uint32_t slot = 0x47B88u + d0;

    if (bus->write16(bus->context, slot + 0x00u, 0x4000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x02u, 0x0000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x04u, 0x0000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x06u, 0x0000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x08u, 0x4000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x0Au, 0x0000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x0Cu, 0x0000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x0Eu, 0x0000u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x10u, 0x4000u) != 0) return BIWN_WORLD_BUS_ERROR;

    uint16_t w;
    if (bus->read16(bus->context, 0x49B8Cu, &w) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x12u, (uint16_t)(0u - (uint32_t)w)) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->read16(bus->context, 0x49B8Eu, &w) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x14u, (uint16_t)(0u - (uint32_t)w)) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->read16(bus->context, 0x49B90u, &w) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, slot + 0x16u, (uint16_t)(0u - (uint32_t)w)) != 0) return BIWN_WORLD_BUS_ERROR;

    uint16_t face;
    if (bus->read16(bus->context, 0x403CEu, &face) != 0) return BIWN_WORLD_BUS_ERROR;
    uint32_t src_ptr;
    if (bus->read32(bus->context, 0x400E6u, &src_ptr) != 0) return BIWN_WORLD_BUS_ERROR;

    uint32_t args[3] = { src_ptr, slot, (uint32_t)face };
    uint32_t ret_d0 = d0;
    if (bus->call(bus->context, 0x110D4u, args, 3u, &ret_d0) != 0) return BIWN_WORLD_DEPENDENCY_ERROR;

    if (bus->read32(bus->context, 0x49B88u, &val) != 0) return BIWN_WORLD_BUS_ERROR;
    d0 = val << 6u;
    if (bus->write16(bus->context, 0x47B88u + d0 + 0x20u, 0x0007u) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->read32(bus->context, 0x400C4u, &val) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write32(bus->context, 0x47B88u + d0 + 0x3Cu, val) != 0) return BIWN_WORLD_BUS_ERROR;

    if (bus->read32(bus->context, 0x49B88u, &val) != 0) return BIWN_WORLD_BUS_ERROR;
    d0 = (val - 1u) << 6u;
    if (bus->read16(bus->context, 0x49B8Au, &w) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->write16(bus->context, 0x47B88u + d0 + 0x18u, w) != 0) return BIWN_WORLD_BUS_ERROR;

    *out_D0 = d0;
    return BIWN_WORLD_OK;
}
