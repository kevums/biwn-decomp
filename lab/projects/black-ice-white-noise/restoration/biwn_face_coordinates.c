#include "biwn_face_coordinates.h"

int biwn_face_coordinates(struct biwn_world_bus *bus, uint32_t source,
                          uint32_t destination, uint16_t face, uint32_t *out_D0)
{
    if (!bus || !out_D0 || !bus->read16 || !bus->write16) {
        return 1;
    }

    uint16_t src_word;
    if (bus->read16(bus->context, source, &src_word) != 0) {
        return 2;
    }

    uint32_t d0 = (uint32_t)src_word;
    d0 <<= 5;
    uint32_t a0 = 0x400C4u + d0;

    if (face > 5u) {
        *out_D0 = d0;
        return 0;
    }

    d0 = 0;

    static const uint8_t offsets[6][12] = {
        {0x12, 0x0A, 0x1A, 0x12, 0x16, 0x1A, 0x06, 0x16, 0x1A, 0x06, 0x0A, 0x1A},
        {0x06, 0x0A, 0x0E, 0x06, 0x0A, 0x1A, 0x06, 0x16, 0x1A, 0x06, 0x16, 0x0E},
        {0x12, 0x0A, 0x0E, 0x06, 0x0A, 0x0E, 0x06, 0x16, 0x0E, 0x12, 0x16, 0x0E},
        {0x12, 0x0A, 0x1A, 0x12, 0x0A, 0x0E, 0x12, 0x16, 0x0E, 0x12, 0x16, 0x1A},
        {0x12, 0x16, 0x1A, 0x12, 0x16, 0x0E, 0x06, 0x16, 0x0E, 0x06, 0x16, 0x1A},
        {0x12, 0x0A, 0x1A, 0x06, 0x0A, 0x1A, 0x06, 0x0A, 0x0E, 0x12, 0x0A, 0x1A}
    };

    static const uint8_t scaled[6][12] = {
        {1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0},
        {0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1},
        {1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0},
        {0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1},
        {1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1},
        {1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1}
    };

    for (int i = 0; i < 12; i++) {
        uint32_t src_addr = a0 + offsets[face][i];
        uint16_t val;
        if (bus->read16(bus->context, src_addr, &val) != 0) {
            return 2;
        }

        uint16_t out_val;
        if (scaled[face][i]) {
            out_val = (uint16_t)((val << 3) & 0xFFFF);
            d0 = (d0 & 0xFFFF0000u) | (uint32_t)out_val;
        } else {
            out_val = val;
        }

        uint32_t dst_addr = destination + 0x24u + (2u * (uint32_t)i);
        if (bus->write16(bus->context, dst_addr, out_val) != 0) {
            return 2;
        }
    }

    *out_D0 = d0;
    return 0;
}
