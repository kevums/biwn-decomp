#include "biwn_scene_initial_setup.h"

int biwn_scene_initial_setup(struct biwn_world_bus *bus, uint32_t incoming_D0, uint32_t *out_D0) {
    if (0 == bus || 0 == out_D0 || 0 == bus->read32 || 0 == bus->write16 || 0 == bus->write32 || 0 == bus->call) {
        return 1;
    }

    uint32_t d0 = incoming_D0;
    uint32_t args[4];
    int rc;

    args[0] = 3;
    rc = bus->call(bus->context, 0x1AA40, args, 1, &d0);
    if (rc != 0) return 3;

    rc = bus->call(bus->context, 0x18160, 0, 0, &d0);
    if (rc != 0) return 3;

    rc = bus->write32(bus->context, 0x403DC, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x403E0, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x403D8, 0xFFFF);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x403D0, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x40400, 0);
    if (rc != 0) return 2;
    rc = bus->write32(bus->context, 0x4040A, 0);
    if (rc != 0) return 2;
    rc = bus->write32(bus->context, 0x40406, 0);
    if (rc != 0) return 2;
    rc = bus->write32(bus->context, 0x40402, 0);
    if (rc != 0) return 2;

    args[0] = 0;
    args[1] = 1;
    rc = bus->call(bus->context, 0x10968, args, 2, &d0);
    if (rc != 0) return 3;

    uint16_t matrix_values[9] = {0x4000, 0, 0, 0, 0x4000, 0, 0, 0, 0x4000};
    for (int i = 0; i < 9; i++) {
        rc = bus->write16(bus->context, 0x47B88 + (i * 2), matrix_values[i]);
        if (rc != 0) return 2;
    }

    args[0] = 1;
    rc = bus->call(bus->context, 0x10A6A, args, 1, &d0);
    if (rc != 0) return 3;

    uint32_t a0;
    rc = bus->read32(bus->context, 0x400E6, &a0);
    if (rc != 0) return 2;

    uint32_t z, y, x;
    rc = bus->read32(bus->context, a0 + 0xC, &z);
    if (rc != 0) return 2;
    rc = bus->read32(bus->context, a0 + 0x8, &y);
    if (rc != 0) return 2;
    rc = bus->read32(bus->context, a0 + 0x4, &x);
    if (rc != 0) return 2;

    args[0] = 1;
    args[1] = x;
    args[2] = y;
    args[3] = z;
    rc = bus->call(bus->context, 0x11762, args, 4, &d0);
    if (rc != 0) return 3;

    rc = bus->write16(bus->context, 0x47B9A, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x47B9C, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x47B9E, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x49B8C, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x49B8E, 0);
    if (rc != 0) return 2;
    rc = bus->write16(bus->context, 0x49B90, 0);
    if (rc != 0) return 2;

    *out_D0 = d0;
    return 0;
}
