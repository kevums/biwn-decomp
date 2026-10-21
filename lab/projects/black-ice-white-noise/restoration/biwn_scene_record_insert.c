#include "biwn_scene_record_insert.h"

int biwn_scene_record_insert(struct biwn_world_bus *bus,
                             uint16_t kind,
                             uint32_t x,
                             uint32_t y,
                             uint32_t z,
                             uint32_t incoming_D0,
                             uint32_t *out_D0)
{
    uint16_t D1;
    uint16_t tmp16;
    uint32_t D0;
    uint32_t polls = 0u;

    if (bus == 0 || out_D0 == 0) {
        return 1;
    }

    if (bus->read16 == 0 || bus->write16 == 0 || bus->write32 == 0) {
        return 1;
    }

    if (bus->read16(bus->context, 0x400E4u, &D1) != 0) {
        return 2;
    }

    if (bus->read16(bus->context, 0x400E4u, &tmp16) != 0) {
        return 2;
    }

    if ((int16_t)tmp16 > 0xF) {
        *out_D0 = incoming_D0;
        return 0;
    }

    D0 = (uint32_t)((int16_t)D1 * 46);

    if (bus->write16(bus->context, 0x400EAu + D0, kind) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 2u, x) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 6u, y) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 10u, z) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 14u, 0u) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 18u, 0u) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 22u, 0u) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 26u, 0u) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 30u, 0u) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 34u, 0u) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 38u, 0u) != 0) {
        return 2;
    }
    if (bus->write32(bus->context, 0x400EAu + D0 + 42u, 0u) != 0) {
        return 2;
    }

    for (;;) {
        D1 = (uint16_t)(D1 + 1u);
        D0 = (uint32_t)((int16_t)D1 * 46);

        if (polls >= bus->poll_limit) {
            return 4;
        }
        ++polls;

        if (bus->read16(bus->context, 0x400EAu + D0, &tmp16) != 0) {
            return 2;
        }

        if (tmp16 != 0u) {
            if ((int16_t)D1 > 0xF) {
                break;
            }
            continue;
        }

        if ((int16_t)D1 > 0xF) {
            break;
        }

        if (bus->write16(bus->context, 0x400E4u, D1) != 0) {
            return 2;
        }

        *out_D0 = D0;
        return 0;
    }

    D1 = 1u;

    if (bus->read16(bus->context, 0x40118u, &tmp16) != 0) {
        return 2;
    }

    if (tmp16 != 0u) {
        for (;;) {
            if (polls >= bus->poll_limit) {
                return 4;
            }
            ++polls;

            if ((int16_t)D1 > 0xF) {
                break;
            }

            D1 = (uint16_t)(D1 + 1u);
            D0 = (uint32_t)((int16_t)D1 * 46);

            if (bus->read16(bus->context, 0x400EAu + D0, &tmp16) != 0) {
                return 2;
            }

            if (tmp16 != 0u) {
                continue;
            }

            break;
        }
    }

    if (bus->write16(bus->context, 0x400E4u, D1) != 0) {
        return 2;
    }

    *out_D0 = D0;
    return 0;
}
