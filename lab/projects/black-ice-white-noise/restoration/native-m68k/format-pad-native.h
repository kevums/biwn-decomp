#ifndef BIWN_FORMAT_PAD_NATIVE_H
#define BIWN_FORMAT_PAD_NATIVE_H
#include <stdint.h>
/* Coordinator ABI: r0..14=D0-D7/A0-A6,r15=original entrySP,r16=low16SR.
 * Implement void biwn_native_format_pad_body(uint32_t *r).
 * Assembly only captures/restores this frame. Body reproduces original
 * public D2 save at entrySP-4 and restore from that location, plus all
 * semantic register/CCR outputs. Arguments use their ORIGINAL widths/offsets:
 * destination LONG entrySP+4,character WORD entrySP+8,remaining pointer
 * LONG entrySP+10,width WORD entrySP+14. All target accesses fresh/ordered.
 * Full frame private; no host pointers/callbacks. No guards or loop bounds.
 */
#define PR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define PR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define PR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define PW8(a,v) (*(volatile uint8_t *)(uint32_t)(a)=(uint8_t)(v))
#define PW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define PW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
#endif
