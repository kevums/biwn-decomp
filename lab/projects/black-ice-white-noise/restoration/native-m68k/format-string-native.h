#ifndef BIWN_FORMAT_STRING_NATIVE_H
#define BIWN_FORMAT_STRING_NATIVE_H
#include <stdint.h>
/* Coordinator ABI, not an original game symbol. r0..14=D0-D7/A0-A6,
 * r15=ORIGINAL entrySP, r16=low16SR. Implement the entire 1B1A8..1B200 body.
 * Body owns original A2 save at entrySP-4 and D2 save at entrySP-8, and their
 * ordered restores. Entry args: destination LONG+4, source LONG+8,
 * remaining-pointer LONG+12, width WORD+16. Source may be NULL; original
 * fallback string is at1B1A0. Preserve all visible registers and final CCR,
 * fresh volatile accesses, including repeated source tests/reads and memory
 * SUBQ read/write. No extra guards, loop bounds or host pointer callbacks.
 * Shim captures/restores private frame and performs RTS; r15 stays fixed.
 */
#define PR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define PR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define PR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define PW8(a,v) (*(volatile uint8_t *)(uint32_t)(a)=(uint8_t)(v))
#define PW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define PW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
#endif
