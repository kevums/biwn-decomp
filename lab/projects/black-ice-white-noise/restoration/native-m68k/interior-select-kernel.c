#include "interior-select-native.h"

static uint32_t rd_l(const void *p) {
    const volatile uint32_t *v = (const volatile uint32_t *)p;
    return *v;
}
static uint16_t rd_w(const void *p) {
    const volatile uint16_t *v = (const volatile uint16_t *)p;
    return *v;
}
static void wr_l(void *p, uint32_t v) {
    volatile uint32_t *w = (volatile uint32_t *)p;
    *w = v;
}
static void wr_w(void *p, uint16_t v) {
    volatile uint16_t *w = (volatile uint16_t *)p;
    *w = v;
}

uint32_t biwn_interior_select_kernel(uint32_t object, uint32_t kind, uint32_t *out) {
    uint32_t d1_in = out[0];
    uint32_t a0_in = out[1];
    uint32_t a1_in = out[2];

    uint32_t hdr = rd_l((const void *)0x49C18u);
    uint32_t d0, d2, d3;
    uint32_t a0, a1;
    uint16_t x, z;
    uint16_t count;
    uint16_t idx;
    uint32_t d1;
    uint32_t rec_ptr;
    uint32_t ccr;
    int x_flag;

    if (kind == 0) {
        a0 = hdr;
        a1 = a1_in;
        uint32_t xv = rd_l((const void *)(object + 4u));
        uint32_t ox = rd_l((const void *)(object + 30u));
        d0 = xv - ox;
        d3 = d0 >> 6;
        uint32_t zv = rd_l((const void *)(object + 10u));
        uint32_t oz = rd_l((const void *)(object + 38u));
        d0 = zv - oz;
        d2 = d0 >> 6;
        x = (uint16_t)d3;
        z = (uint16_t)d2;
    } else {
        a1 = hdr;
        a0 = a0_in;
        uint32_t xv = rd_l((const void *)(object + 2u));
        uint32_t gx = rd_l((const void *)0x49C6Au);
        d0 = xv - gx;
        d3 = d0 >> 6;
        uint32_t zv = rd_l((const void *)(object + 8u));
        uint32_t gz = rd_l((const void *)0x49C72u);
        d0 = zv - gz;
        d2 = d0 >> 6;
        x = (uint16_t)d3;
        z = (uint16_t)d2;
    }

    count = rd_w((const void *)hdr);
    idx = (uint16_t)(count - 1u);
    d1 = (d1_in & 0xFFFF0000u) | (uint32_t)idx;
    x_flag = (count == 0u) ? 1 : 0;

    if (idx & 0x8000u) {
        d0 &= 0xFFFF0000u;
        ccr = 4u | (x_flag ? 16u : 0u);
        out[0] = d1;
        out[1] = a0;
        out[2] = a1;
        out[3] = ccr;
        return d0;
    }

    int matched = 0;

    for (;;) {
        d0 = (uint32_t)idx * 24u;
        uint32_t recs = rd_l((const void *)(hdr + 4u));
        rec_ptr = d0 + recs;

        if (kind == 0) {
            a1 = rec_ptr;
        } else {
            a0 = rec_ptr;
        }

        uint16_t rx = rd_w((const void *)(rec_ptr + 2u));
        if ((int16_t)x < (int16_t)rx) {
            idx = (uint16_t)(idx - 1u);
            d1 = (d1 & 0xFFFF0000u) | (uint32_t)idx;
            if (idx == 0xFFFFu) break;
            continue;
        }

        rx = rd_w((const void *)(rec_ptr + 2u));
        uint16_t rw = rd_w((const void *)(rec_ptr + 6u));
        uint32_t sum_x = (uint32_t)rx + (uint32_t)rw;
        x_flag = (sum_x > 0xFFFFu) ? 1 : 0;
        d0 = (d0 & 0xFFFF0000u) | (uint32_t)(uint16_t)sum_x;
        if ((int16_t)(uint16_t)sum_x <= (int16_t)x) {
            idx = (uint16_t)(idx - 1u);
            d1 = (d1 & 0xFFFF0000u) | (uint32_t)idx;
            if (idx == 0xFFFFu) break;
            continue;
        }

        uint16_t rz = rd_w((const void *)(rec_ptr + 4u));
        if ((int16_t)z < (int16_t)rz) {
            idx = (uint16_t)(idx - 1u);
            d1 = (d1 & 0xFFFF0000u) | (uint32_t)idx;
            if (idx == 0xFFFFu) break;
            continue;
        }

        rz = rd_w((const void *)(rec_ptr + 4u));
        uint16_t rd = rd_w((const void *)(rec_ptr + 8u));
        uint32_t sum_z = (uint32_t)rz + (uint32_t)rd;
        x_flag = (sum_z > 0xFFFFu) ? 1 : 0;
        d0 = (d0 & 0xFFFF0000u) | (uint32_t)(uint16_t)sum_z;
        if ((int16_t)(uint16_t)sum_z > (int16_t)z) {
            matched = 1;
            break;
        }

        idx = (uint16_t)(idx - 1u);
        d1 = (d1 & 0xFFFF0000u) | (uint32_t)idx;
        if (idx == 0xFFFFu) break;
    }

    if (!matched) {
        d0 &= 0xFFFF0000u;
        d1 = (d1 & 0xFFFF0000u) | 0xFFFFu;
        ccr = 4u | (x_flag ? 16u : 0u);
        out[0] = d1;
        out[1] = a0;
        out[2] = a1;
        out[3] = ccr;
        return d0;
    }

    if (kind == 1) {
        wr_w((void *)(object + 16u), idx);
        d0 = 1u;
        d1 = (d1 & 0xFFFF0000u) | (uint32_t)idx;
        ccr = x_flag ? 16u : 0u;
        out[0] = d1;
        out[1] = a0;
        out[2] = a1;
        out[3] = ccr;
        return d0;
    }

    wr_w((void *)(object + 42u), idx);
    wr_l((void *)(object + 44u), rec_ptr);

    uint16_t rx2 = rd_w((const void *)(rec_ptr + 2u));
    uint16_t sx2 = (uint16_t)((uint32_t)rx2 << 6);
    int32_t sx32 = (int32_t)(int16_t)sx2;
    uint32_t ox2 = rd_l((const void *)(object + 30u));
    uint32_t lower_x = (uint32_t)sx32 + ox2;
    wr_l((void *)(object + 52u), lower_x);

    uint16_t rz2 = rd_w((const void *)(rec_ptr + 4u));
    uint16_t sz2 = (uint16_t)((uint32_t)rz2 << 6);
    int32_t sz32 = (int32_t)(int16_t)sz2;
    uint32_t oz2 = rd_l((const void *)(object + 38u));
    uint32_t lower_z = (uint32_t)sz32 + oz2;
    wr_l((void *)(object + 60u), lower_z);

    uint16_t rw2 = rd_w((const void *)(rec_ptr + 6u));
    uint16_t sw2 = (uint16_t)((uint32_t)rw2 << 6);
    int32_t sw32 = (int32_t)(int16_t)sw2;
    uint32_t lx2 = rd_l((const void *)(object + 52u));
    uint32_t upper_x = (uint32_t)sw32 + lx2;
    wr_l((void *)(object + 48u), upper_x);

    uint16_t rd2 = rd_w((const void *)(rec_ptr + 8u));
    uint16_t sd2 = (uint16_t)((uint32_t)rd2 << 6);
    int32_t sd32 = (int32_t)(int16_t)sd2;
    uint32_t lz2 = rd_l((const void *)(object + 60u));
    uint32_t upper_z = (uint32_t)sd32 + lz2;
    wr_l((void *)(object + 56u), upper_z);

    d0 = 1u;
    d1 = (d1 & 0xFFFF0000u) | (uint32_t)idx;
    a1 = rec_ptr;
    a0 = upper_z;
    ccr = (rd2 & 0x0400u) ? 16u : 0u;
    out[0] = d1;
    out[1] = a0;
    out[2] = a1;
    out[3] = ccr;
    return d0;
}
