#include "biwn_scene_device_initialize.h"

int biwn_scene_device_initialize(struct biwn_world_bus *bus, uint32_t *out_D0)
{
    if (!bus || !out_D0 || !bus->write16 || !bus->write32) {
        return 1;
    }

    if (bus->write32(bus->context, 0xf02268, 0) != 0) return 2;
    if (bus->write32(bus->context, 0xf0226c, 0) != 0) return 2;
    if (bus->write32(bus->context, 0xf02200, 0xb29d0) != 0) return 2;
    if (bus->write32(bus->context, 0xf02204, 0x2e20) != 0) return 2;
    if (bus->write32(bus->context, 0xf0220c, 0) != 0) return 2;
    if (bus->write32(bus->context, 0xf0223c, 0x113b0) != 0) return 2;
    if (bus->write32(bus->context, 0xf02238, 0x10200) != 0) return 2;
    if (bus->write16(bus->context, 0x00113060, 0) != 0) return 2;
    if (bus->write16(bus->context, 0xf00400, 0x0000) != 0) return 2;
    if (bus->write16(bus->context, 0xf00402, 0x077f) != 0) return 2;
    if (bus->write16(bus->context, 0xf00404, 0x7040) != 0) return 2;
    if (bus->write16(bus->context, 0xf00406, 0x707f) != 0) return 2;

    *out_D0 = 0;
    return 0;
}

