#include "rng-native.h"
#include <stdint.h>

static uint32_t sx16(uint16_t v) {
    return (uint32_t)(v & 0x7fffu) - (uint32_t)(v & 0x8000u);
}

static uint16_t asr16(uint16_t v, unsigned n) {
    return (uint16_t)((v >> n) | (v & 0x8000u ? 0xffffu << (16u - n) : 0u));
}

static uint16_t nz32(uint32_t v) {
    return (uint16_t)((v ? 0 : 4) | (v & 0x80000000u ? 8 : 0));
}

static uint32_t read_slot(uint16_t s) {
    return *(volatile uint32_t *)(uintptr_t)(0x113082u + (sx16(s) << 2));
}

static void write_slot(uint16_t s, uint32_t v) {
    *(volatile uint32_t *)(uintptr_t)(0x113082u + (sx16(s) << 2)) = v;
}

static void do_select(struct biwn_native_rng_frame *f, uint16_t new_sel) {
    volatile uint16_t *sel = (volatile uint16_t *)0x113080u;
    uint16_t old = *sel;
    uint32_t d0 = f->r[0];
    uint32_t d1 = f->r[1];
    uint16_t x = (f->sr >> 4) & 1;

    if (old > 255u) {
        uint32_t s = sx16(old);
        uint32_t t = ((s << 8) - s) << 7;
        uint32_t h = (s - t) >> 16;
        uint16_t k = asr16((uint16_t)(old + (uint16_t)h), 7);
        k = (uint16_t)(k - asr16(old, 15));
        d0 = (uint16_t)((uint16_t)(k << 8) - k);
        d1 = (t & 0xffff0000u) | k;
        uint16_t tmp = (uint16_t)(old - (uint16_t)d0);
        x = (old < (uint16_t)d0) ? 1 : 0;
        *sel = tmp;
    }
    *sel = new_sel;
    f->r[0] = d0;
    f->r[1] = d1;
    f->sr = (uint16_t)((f->sr & 0xffe0u) | (x << 4) | nz32(f->r[3]));
}

static void do_get(struct biwn_native_rng_frame *f) {
    volatile uint16_t *sel = (volatile uint16_t *)0x113080u;
    uint16_t s = *sel;
    uint32_t d0 = read_slot(s);
    f->r[0] = d0;
    f->r[8] = 0x113082u;
    f->sr = (uint16_t)((f->sr & 0xffe0u) | ((s & 0x8000u) ? 16 : 0) | nz32(d0));
}

static void do_set(struct biwn_native_rng_frame *f) {
    volatile uint16_t *sel = (volatile uint16_t *)0x113080u;
    uint32_t val = f->arg.long_value;
    uint32_t a0 = val - 1u;
    uint16_t x = (f->sr >> 4) & 1;
    uint32_t u = a0, v = 0x7ffffffdu;
    uint32_t res = u - v;
    uint16_t nz = nz32(res);
    uint16_t c = (u < v) ? 1 : 0;
    uint16_t vc = (((u ^ v) & (u ^ res)) & 0x80000000u) ? 1 : 0;

    if (a0 > 0x7ffffffdu) {
        f->r[8] = a0;
        f->r[9] = val;
        f->sr = (uint16_t)((f->sr & 0xffe0u) | (x << 4) | (vc << 1) | (c << 0) | nz);
        return;
    }

    uint16_t s = *sel;
    write_slot(s, val);
    f->r[0] = sx16(s) << 2;
    f->r[8] = 0x113082u;
    f->r[9] = val;
    f->sr = (uint16_t)((f->sr & 0xffe0u) | ((s & 0x8000u) ? 16 : 0) | nz32(val));
}

static void do_fill(struct biwn_native_rng_frame *f) {
    volatile uint32_t *q = (volatile uint32_t *)0x462f0u;
    volatile uint32_t *r = (volatile uint32_t *)0x462f4u;
    struct math_result mr = {0};
    uint32_t d0 = 0, d1 = 0, a0 = 0, a1 = 0;

    for (uint32_t i = 1; i <= 255; i++) {
        uint32_t seed = *(volatile uint32_t *)(uintptr_t)(0x113082u + (i - 1) * 4u);
        uint32_t qv = *q;
        biwn_native_remainder_result(seed, qv, f->sr, &mr);
        uint32_t rem = mr.d0;
        uint32_t temp2 = rem * 3275u;
        uint32_t base = rem * 22925u;

        qv = *q;
        biwn_native_division_result(seed, qv, f->sr, &mr);
        uint32_t quot = mr.d0;
        uint32_t rv = *r;
        biwn_native_multiply_result(quot, rv, f->sr, &mr);

        uint32_t state = base - mr.d0;
        *(volatile uint32_t *)(uintptr_t)(0x113082u + i * 4u) = state;
        if (state == 0 || (state & 0x80000000u)) {
            uint32_t v = *(volatile uint32_t *)(uintptr_t)(0x113082u + i * 4u);
            v += 0x7fffffffu;
            *(volatile uint32_t *)(uintptr_t)(0x113082u + i * 4u) = v;
        }
        d0 = i * 4u;
        d1 = mr.d1;
        a0 = temp2;
        a1 = base;
    }
    f->r[0] = d0;
    f->r[1] = d1;
    f->r[8] = a0;
    f->r[9] = a1;
    f->sr = (uint16_t)(f->sr & 0xffe0u);
}

static void do_seed(struct biwn_native_rng_frame *f, uint32_t seed) {
    volatile uint32_t *tbl = (volatile uint32_t *)0x113082u;
    if (seed == 0x7fffffffu) seed = 0;
    tbl[0] = seed;
    f->r[0] = seed;
    do_fill(f);
}

static void do_current(struct biwn_native_rng_frame *f) {
    volatile uint16_t *sel = (volatile uint16_t *)0x113080u;
    volatile uint32_t *q = (volatile uint32_t *)0x462e0u;
    volatile uint32_t *r = (volatile uint32_t *)0x462e4u;
    struct math_result mr = {0};
    uint16_t s = *sel;
    uint32_t seed = read_slot(s);
    uint32_t qv = *q;
    biwn_native_remainder_result(seed, qv, f->sr, &mr);
    uint32_t base = mr.d0 * 48271u;

    qv = *q;
    biwn_native_division_result(seed, qv, f->sr, &mr);
    uint32_t quot = mr.d0;
    uint32_t rv = *r;
    biwn_native_multiply_result(quot, rv, f->sr, &mr);

    uint32_t state = base - mr.d0;
    write_slot(s, state);
    if (state == 0 || (state & 0x80000000u)) {
        uint32_t v = read_slot(s);
        v += 0x7fffffffu;
        write_slot(s, v);
    }
    s = *sel;
    uint32_t d0 = read_slot(s);
    f->r[0] = d0;
    f->r[1] = mr.d1;
    f->r[8] = base;
    f->r[9] = seed;
    f->sr = (uint16_t)((f->sr & 0xffe0u) | ((s & 0x8000u) ? 16 : 0) | nz32(d0));
}

static void do_indexed(struct biwn_native_rng_frame *f) {
    volatile uint32_t *q = (volatile uint32_t *)0x462e8u;
    volatile uint32_t *r = (volatile uint32_t *)0x462ecu;
    struct math_result mr = {0};
    uint16_t s = f->arg.word_value;
    uint32_t seed = read_slot(s);
    uint32_t qv = *q;
    biwn_native_remainder_result(seed, qv, f->sr, &mr);
    uint32_t base = mr.d0 * 48271u;

    qv = *q;
    biwn_native_division_result(seed, qv, f->sr, &mr);
    uint32_t quot = mr.d0;
    uint32_t rv = *r;
    biwn_native_multiply_result(quot, rv, f->sr, &mr);

    uint32_t state = base - mr.d0;
    uint16_t x = (base < mr.d0) ? 1 : 0;
    write_slot(s, state);
    if (state == 0 || (state & 0x80000000u)) {
        uint32_t v = read_slot(s);
        v += 0x7fffffffu;
        write_slot(s, v);
        x = (v < 0x7fffffffu) ? 1 : 0;
    }
    uint32_t d0 = read_slot(s);
    f->r[0] = d0;
    f->r[1] = mr.d1;
    f->r[8] = base;
    f->r[9] = seed;
    f->sr = (uint16_t)((f->sr & 0xffe0u) | (x << 4) | nz32(d0));
}

static void do_init(struct biwn_native_rng_frame *f) {
    do_select(f, 0);
    do_seed(f, 0x075bcd15u);
}

void biwn_native_rng_dispatch(uint32_t pc, struct biwn_native_rng_frame *f) {
    switch (pc) {
        case 0x01a6e0u: do_init(f); break;
        case 0x01a6f8u: do_current(f); break;
        case 0x01a77cu: do_indexed(f); break;
        case 0x01a7f4u: do_fill(f); break;
        case 0x01a87au: do_select(f, f->arg.word_value); break;
        case 0x01a8c6u: do_seed(f, f->arg.long_value); break;
        case 0x01a8e2u: do_get(f); break;
        case 0x01a8f8u: do_set(f); break;
        default: break;
    }
}
