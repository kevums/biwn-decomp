#ifndef BIWN_COPY_NATIVE_H
#define BIWN_COPY_NATIVE_H
#include <stdint.h>
/* Coordinator ABI. Frame: D0..D7/A0..A6=r[0..14], original SP=r[15],
 * saved low16SR=r[16], argument order selector=r[17] (0=E3E0,1=E3EE).
 * Change only r[0],r[1],r[8],r[9],r[16], plus r[2..4] from exact public
 * large-path restores. Public arguments begin at r[15]+4.
 * The96byte wrapper leaves the original large-path save locations at
 * originalSP-4/-8/-12 untouched for the body to write D2/D3/D4 in order.
 * After its final command, read SP-12(D4), SP-8(D3), SP-4(D2), in that order,
 * into r[4],r[3],r[2]; final N/Z must use that restored D2 value.
 * Source/destination must not alias private working stack/new code in tests.
 */
#define CR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define CW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
#define CR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define CW8(a,v) (*(volatile uint8_t *)(uint32_t)(a)=(uint8_t)(v))
#endif
