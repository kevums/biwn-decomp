#ifndef BIWN_NATIVE_FRAME_REFERENCE_RELEASE_H
#define BIWN_NATIVE_FRAME_REFERENCE_RELEASE_H
#include <stdint.h>
/* Analyst name for original1AE88..1AED8. r0..14=D0-D7/A0-A6,
 * r15=entrySP,r16=SR. Original argument is WORD at entrySP+4.
 * Public saves: D3 at SP-4 followed by D2 at SP-8; restore both from RAM.
 * C uses native volatile target accesses, no host bus or original CPU calls.
 */
#define FR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define FR32(a) (*(volatile uint32_t *)(uint32_t)(a))
void biwn_native_frame_reference_release_body(uint32_t *);
#endif
