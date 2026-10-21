#ifndef BIWN_SIGNED_DIVISION_H
#define BIWN_SIGNED_DIVISION_H
#include <stdint.h>
enum biwn_signed_division_status { BIWN_SIGNED_DIVISION_OK=0,
 BIWN_SIGNED_DIVISION_BAD_ARGUMENT=1,BIWN_SIGNED_DIVISION_ZERO=2 };
/* Original E588..E60A: signed32 quotient D0 and remainder D1, represented
 * as raw two's-complement bits. INT_MIN/-1 wraps to INT_MIN. Zero division
 * is an added host error, not the original processor exception. No output
 * mutation on host errors. Caller-saved A0/A1/CCR are outside this interface. */
enum biwn_signed_division_status biwn_signed_division(uint32_t numerator,
 uint32_t denominator,uint32_t *quotient,uint32_t *remainder);
#endif
