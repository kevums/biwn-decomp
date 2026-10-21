#include "copy-native.h"

void biwn_native_copy_body(uint32_t *r) {
    uint32_t sp = r[15];
    uint32_t sr = r[16];

    uint32_t arg0 = CR32(sp + 4);
    uint32_t arg1 = CR32(sp + 8);
    uint32_t count = CR32(sp + 12);

    uint32_t source;
    uint32_t destination;
    if (r[17] == 0) {
        source = arg0;
        destination = arg1;
    } else {
        source = arg1;
        destination = arg0;
    }

    uint32_t result = r[0];

    if (count == 0) {
        r[1] = 0;
        r[8] = destination;
        r[9] = source;
        r[16] = (sr & 0xffe0u) | (sr & 16u) | 4u;
        return;
    }

    if (((count - 128u) & 0x80000000u) != 0) {
        do {
            uint8_t byte = CR8(source);
            source += 1u;
            CW8(destination, byte);
            destination += 1u;
            count -= 1u;
        } while (count != 0);

        r[1] = 0;
        r[8] = destination;
        r[9] = source;
        r[16] = (sr & 0xffe0u) | 4u;
        return;
    }

    CW32(0xf02204u, 0x4020u);
    CW32(0xf02228u, 0x4020u);
    CW32(sp - 4u, r[2]);
    CW32(sp - 8u, r[3]);
    CW32(sp - 12u, r[4]);

    uint32_t lastX = 0;

    while (count != 0) {
        uint32_t part = count;
        if (((part - 65536u) & 0x80000000u) == 0) {
            part = 65536u;
        }
        count -= part;

        uint32_t signed_half = (part >> 1) | (part & 0x80000000u);
        CW32(0xf0223cu, signed_half | 0x10000u);

        uint32_t aligned = destination & 0xfffffff8u;
        uint32_t destination_offset = (destination - aligned) >> 1;
        destination += part;
        CW32(0xf02200u, aligned);
        CW32(0xf0220cu, destination_offset);

        aligned = source & 0xfffffff8u;
        uint32_t source_byte_offset = source - aligned;
        lastX = source_byte_offset & 1u;
        uint32_t source_offset = source_byte_offset >> 1;
        source += part;
        CW32(0xf02224u, aligned);
        CW32(0xf02230u, source_offset);

        result = (source_offset > destination_offset) ? 0x01800005u : 0x01800001u;
        CW32(0xf02238u, result);
    }

    uint32_t saved4 = CR32(sp - 12u);
    uint32_t saved3 = CR32(sp - 8u);
    uint32_t saved2 = CR32(sp - 4u);

    r[4] = saved4;
    r[3] = saved3;
    r[2] = saved2;

    r[0] = result;
    r[1] = 0;
    r[8] = destination;
    r[9] = source;
    r[16] = (sr & 0xffe0u) | (lastX ? 16u : 0u) | (saved2 == 0 ? 4u : 0u) | (saved2 & 0x80000000u ? 8u : 0u);
}
