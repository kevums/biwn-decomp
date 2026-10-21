#include "biwn_global_scene_prepare.h"

int biwn_global_scene_prepare(struct biwn_world_bus *bus, uint32_t incoming_D0, uint32_t *out_D0) {
    if (!bus || !out_D0 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !bus->call) {
        return 1;
    }

    uint32_t D0 = incoming_D0;

    uint32_t args[2] = {1, 7};
    int status = bus->call(bus->context, 0x10968, args, 2, &D0);
    if (status != 0) {
        return 3;
    }

    status = bus->write32(bus->context, 0x49B88, 0);
    if (status != 0) {
        return 2;
    }

    uint32_t val_40100 = 0;
    status = bus->read32(bus->context, 0x40100, &val_40100);
    if (status != 0) {
        return 2;
    }
    uint32_t A = (0x20 + val_40100) & 0xFF;

    uint32_t val_400F8 = 0;
    status = bus->read32(bus->context, 0x400F8, &val_400F8);
    if (status != 0) {
        return 2;
    }
    uint32_t B = (0x20 + val_400F8) & 0xFF;

    uint32_t val_400FC = 0;
    status = bus->read32(bus->context, 0x400FC, &val_400FC);
    if (status != 0) {
        return 2;
    }
    uint32_t C = (0x20 + val_400FC) & 0xFF;

    A = (A >> 6) << 5;
    D0 = (C >> 6) << 3;
    B = (B >> 6) * 2;

    uint32_t index = 0x3D7A2 + A + D0 + B;
    uint16_t word = 0;
    status = bus->read16(bus->context, index, &word);
    if (status != 0) {
        return 2;
    }

    status = bus->write16(bus->context, 0x403CE, word);
    if (status != 0) {
        return 2;
    }

    status = bus->call(bus->context, 0x11384, NULL, 0, &D0);
    if (status != 0) {
        return 3;
    }

    status = bus->call(bus->context, 0x10BA4, NULL, 0, &D0);
    if (status != 0) {
        return 3;
    }

    status = bus->call(bus->context, 0x1142E, NULL, 0, &D0);
    if (status != 0) {
        return 3;
    }

    status = bus->call(bus->context, 0x10734, NULL, 0, &D0);
    if (status != 0) {
        return 3;
    }

    *out_D0 = D0;
    return 0;
}
