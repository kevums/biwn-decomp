#ifndef BIWN_NATIVE_RNG_H
#define BIWN_NATIVE_RNG_H
#include <stdint.h>
#include <stddef.h>

/* Native shim saves D0-D7/A0-A6, then the incoming SR, followed by the
 * untouched caller return and first argument. C updates the saved context;
 * the shim restores it and returns through the original caller stack. */
struct __attribute__((packed,aligned(2))) biwn_native_rng_frame {
    uint32_t r[15];
    uint16_t sr;
    uint32_t return_pc;
    union { uint32_t long_value; uint16_t word_value; } arg;
};
typedef char rng_sr_offset[offsetof(struct biwn_native_rng_frame,sr)==60?1:-1];
typedef char rng_arg_offset[offsetof(struct biwn_native_rng_frame,arg)==66?1:-1];

/* Same cross-translation-unit type/layout as accepted math-results-optimized.c. */
struct __attribute__((packed,aligned(2))) math_result {
    uint32_t d0,d1;
    uint16_t sr;
    uint32_t original_d2,original_d3;
};
extern void biwn_native_multiply_result(uint32_t,uint32_t,uint32_t,struct math_result *);
extern void biwn_native_division_result(uint32_t,uint32_t,uint32_t,struct math_result *);
extern void biwn_native_remainder_result(uint32_t,uint32_t,uint32_t,struct math_result *);
void biwn_native_rng_dispatch(uint32_t,struct biwn_native_rng_frame *);
#endif
