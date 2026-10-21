#ifndef BIWN_UNSIGNED_DIVISION_NATIVE_H
#define BIWN_UNSIGNED_DIVISION_NATIVE_H
#include <stdint.h>
/* r0..14=D0-D7/A0-A6,r15=original entrySP,r16=low16SR. Return1 for
 * native DIVU-zero continuation,0 for normal return. Stable stack arguments.
 * Preserve original public reads and E67C pushes/return-address read. */
#define UR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define UR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define UW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
int biwn_native_unsigned_divide_body(uint32_t *r);
int biwn_native_unsigned_remainder_body(uint32_t *r);
#endif
