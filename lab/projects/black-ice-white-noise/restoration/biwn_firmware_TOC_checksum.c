#include <stdint.h>
#include <stddef.h>

int biwn_firmware_TOC_checksum(const uint8_t *toc, const uint32_t *round_constants, uint32_t *out) {
    if (toc == NULL || round_constants == NULL || out == NULL) {
        return 1;
    }

    static const uint8_t s_table[4][4] = {
        {7, 12, 17, 22},
        {5, 9, 14, 20},
        {4, 11, 16, 23},
        {6, 10, 15, 21}
    };

    uint32_t A = 0x67452301u;
    uint32_t B = 0xefcdab89u;
    uint32_t C = 0x98badcfeu;
    uint32_t D = 0x10325476u;

    for (int block = 0; block < 16; ++block) {
        uint32_t AA = A;
        uint32_t BB = B;
        uint32_t CC = C;
        uint32_t DD = D;

        uint32_t X[16];
        for (int j = 0; j < 16; ++j) {
            const uint8_t *p = toc + (block * 64) + (j * 4);
            X[j] = ((uint32_t)p[0] << 24) |
                   ((uint32_t)p[1] << 16) |
                   ((uint32_t)p[2] << 8)  |
                   ((uint32_t)p[3]);
        }

        for (int i = 0; i < 64; ++i) {
            uint32_t F;
            int g;

            if (i < 16) {
                F = (B & C) | (~B & D);
                g = i;
            } else if (i < 32) {
                F = (D & B) | (~D & C);
                g = (5 * i + 1) % 16;
            } else if (i < 48) {
                F = B ^ C ^ D;
                g = (3 * i + 5) % 16;
            } else {
                F = C ^ (B | ~D);
                g = (7 * i) % 16;
            }

            int group = i / 16;
            int idx = i % 4;
            uint32_t S = s_table[group][idx];

            uint32_t t = A + F + round_constants[i] + X[g];
            uint32_t rotated = (t << S) | (t >> (32 - S));

            A = D;
            D = C;
            C = B;
            B = B + rotated;
        }

        A = AA + A;
        B = BB + B;
        C = CC + C;
        D = DD + D;
    }

    out[0] = A;
    out[1] = B;
    out[2] = C;
    out[3] = D;

    return 0;
}