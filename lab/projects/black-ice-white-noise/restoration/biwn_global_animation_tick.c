#include "biwn_global_animation_tick.h"

int biwn_global_animation_tick(struct biwn_world_bus *bus, uint32_t incoming_D0, uint32_t *out_D0) {
    if (!bus || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !out_D0) {
        return 1;
    }

    uint16_t timer;
    if (bus->read16(bus->context, 0x403D4, &timer) != 0) {
        return 2;
    }

    if ((timer & 0x8000) == 0 && timer != 0) {
        if (bus->read16(bus->context, 0x403D4, &timer) != 0) {
            return 2;
        }
        uint16_t new_timer = (uint16_t)(timer - 1);
        if (bus->write16(bus->context, 0x403D4, new_timer) != 0) {
            return 2;
        }
        *out_D0 = incoming_D0;
        return 0;
    }

    uint32_t pointer;
    if (bus->read32(bus->context, 0x400E6, &pointer) != 0) {
        return 2;
    }

    uint16_t timer_value;
    if (bus->read16(bus->context, pointer + 0x90, &timer_value) != 0) {
        return 2;
    }

    if (bus->write16(bus->context, 0x403D4, timer_value) != 0) {
        return 2;
    }

    uint16_t phase;
    if (bus->read16(bus->context, 0x403D0, &phase) != 0) {
        return 2;
    }

    uint16_t new_phase = (uint16_t)(phase + 1);
    if (bus->write16(bus->context, 0x403D0, new_phase) != 0) {
        return 2;
    }

    uint16_t limit;
    if (bus->read16(bus->context, 0x403D2, &limit) != 0) {
        return 2;
    }

    if (bus->read16(bus->context, 0x403D0, &phase) != 0) {
        return 2;
    }

    uint16_t limit_xor = (uint16_t)(limit ^ 0x8000);
    uint16_t phase_xor = (uint16_t)(phase ^ 0x8000);
    if (limit_xor <= phase_xor) {
        if (bus->write16(bus->context, 0x403D0, 0) != 0) {
            return 2;
        }
    }

    if (bus->read16(bus->context, 0x403D0, &phase) != 0) {
        return 2;
    }

    uint32_t table_index = (uint32_t)((phase & 1) + 1);
    uint32_t D0 = table_index * 4;

    uint32_t table_value;
    if (bus->read32(bus->context, 0x23F84 + D0, &table_value) != 0) {
        return 2;
    }

    if (bus->write32(bus->context, 0x23F84, table_value) != 0) {
        return 2;
    }

    if (bus->read16(bus->context, 0x403D0, &phase) != 0) {
        return 2;
    }

    uint16_t shifted = (uint16_t)((phase >> 1) | (phase & 0x8000));

    uint16_t offset;
    if (bus->read16(bus->context, 0x403DA, &offset) != 0) {
        return 2;
    }

    uint16_t result = (uint16_t)(shifted + offset);
    uint32_t sign_extended = (uint32_t)(result & 0x7FFF) - (uint32_t)(result & 0x8000);
    uint32_t D0_offset = sign_extended << 3;

    uint32_t graphics_value;
    if (bus->read32(bus->context, 0x4674C + D0_offset, &graphics_value) != 0) {
        return 2;
    }

    if (bus->write32(bus->context, 0x23F7C, graphics_value) != 0) {
        return 2;
    }

    *out_D0 = D0_offset;
    return 0;
}
