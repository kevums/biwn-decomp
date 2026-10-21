/* Native ABI adaptation of the already recovered arithmetic and flag formulas.
 * Coordinator-authored glue; no CPU decoder or original game calls. */
#include <stdint.h>
#include <stddef.h>

struct __attribute__((packed,aligned(2))) math_result {
    uint32_t d0, d1;
    uint16_t sr;
    uint32_t original_d2, original_d3;
};

typedef char check_d2_offset[offsetof(struct math_result, original_d2) == 10 ? 1 : -1];
typedef char check_result_size[sizeof(struct math_result) == 18 ? 1 : -1];

extern uint32_t __udivsi3(uint32_t, uint32_t);

static uint16_t nz32(uint32_t v) {
    return (uint16_t)((v ? 0 : 4) | (v & 0x80000000u ? 8 : 0));
}

void biwn_native_multiply_result(uint32_t a, uint32_t b, uint32_t incoming_sr, struct math_result *out)
{
    uint32_t aa = a & 0x80000000u ? 0u - a : a;
    uint32_t bb = b & 0x80000000u ? 0u - b : b;
    
    /* 1. Multiplication: replace generic32bit multiply calls with three 16x16 unsigned products. */
    uint32_t a_lo = aa & 0xffffu;
    uint32_t a_hi = aa >> 16;
    uint32_t b_lo = bb & 0xffffu;
    uint32_t b_hi = bb >> 16;

    /* Cast at least one operand to uint32_t before multiplication to avoid signed-promotion overflow */
    uint32_t low = (uint32_t)a_lo * (uint32_t)b_lo;
    uint32_t cross = (uint32_t)a_lo * (uint32_t)b_hi + (uint32_t)a_hi * (uint32_t)b_lo;
    uint32_t partial = (cross & 0xffffu) << 16;
    uint32_t absolute = partial + low;

    uint16_t sign = (uint16_t)(a >> 16);
    if (b & 0x80000000u) sign = (uint16_t)~sign;
    
    uint16_t flags;
    /* out->d0 is the full 32-bit signed product. We compute it via the absolute value and sign. */
    if (sign & 0x8000u) {
        /* Negative result */
        uint32_t neg_abs = 0u - absolute;
        out->d0 = neg_abs;
        flags = (uint16_t)(nz32(out->d0) | (absolute ? 17 : 0) | (absolute == 0x80000000u ? 2 : 0));
    } else {
        /* Positive result */
        out->d0 = absolute;
        flags = (uint16_t)((absolute < partial ? 16 : 0) | (sign ? 0 : 4) | (sign & 0x8000u ? 8 : 0));
    }
    
    out->d1 = low;
    out->sr = (uint16_t)((incoming_sr & 0xffe0u) | flags);
}

void biwn_native_division_result(uint32_t a, uint32_t b, uint32_t incoming_sr, struct math_result *out)
{
    uint32_t q = 0, r = 0;
    uint32_t aa = a & 0x80000000u ? 0u - a : a;
    uint32_t bb = b & 0x80000000u ? 0u - b : b;
    unsigned x = (incoming_sr & 16u) != 0;

    /* Zero takes the native processor-exception entry before this C function. */
    if (b == 0) __builtin_trap();

    /* 2. Division: call __udivsi3 exactly once on unsigned magnitudes */
    q = __udivsi3(aa, bb);
    r = aa - q * bb;

    /* Negate quotient and remainder based on signs */
    if ((a ^ b) & 0x80000000u) {
        q = 0u - q;
    }
    if (a & 0x80000000u) {
        r = 0u - r;
    }

    /* Keep unsigned magnitudes for existing X-flag comparisons */
    if (b & 0x80000000u) x = 1;
    if (a & 0x80000000u) x = 1;
    if (aa >= bb && (b >> 16)) x = 0;
    if (a & 0x80000000u) x = r != 0;
    if ((a ^ b) & 0x80000000u) x = q != 0;

    out->d0 = q;
    out->d1 = r;
    out->sr = (uint16_t)((incoming_sr & 0xffe0u) | (x ? 16 : 0) | nz32(out->original_d2));
}

void biwn_native_remainder_result(uint32_t a, uint32_t b, uint32_t sr, struct math_result *out)
{
    biwn_native_division_result(a, b, sr, out);
    out->d0 = out->d1;
    out->sr = (uint16_t)((out->sr & 0xfff0u) | nz32(out->d0));
}
