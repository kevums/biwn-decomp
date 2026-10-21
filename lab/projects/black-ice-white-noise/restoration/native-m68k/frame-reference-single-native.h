#ifndef BIWN_NATIVE_FRAME_REFERENCE_SINGLE_H
#define BIWN_NATIVE_FRAME_REFERENCE_SINGLE_H
#include <stdint.h>
/* Analyst name for1AE56..1AE86. r0..14=D0-D7/A0-A6,
 * r15=entrySP,r16=SR. WORD argument at entrySP+4; public D2 save at SP-4.
 * Negative ID words are compared literally; there is no negative-ID guard.
 * The first matching slot ends the scan, including a zero reference count.
 * Native volatile accesses, no original CPU calls or host callbacks.
 */
#define FS16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define FS32(a) (*(volatile uint32_t *)(uint32_t)(a))
void biwn_native_frame_reference_single_body(uint32_t *);
#endif
