#ifndef BIWN_ACTOR_DISPATCH_NATIVE_H
#define BIWN_ACTOR_DISPATCH_NATIVE_H
#include <stdint.h>
/* Coordinator ABI: r[0..14]=D0-D7/A0-A6, r[15]=root entry SP,
 * r[16] low WORD=SR; r[17] is private capture continuation. Original
 * D2-D5 are saved/restored by the root shim. Capture services load every
 * helper-visible register and call actual child entry134DC/137E0 at the
 * ORIGINAL guest argument SP, then replace r[0..14]/SR with child outputs.
 * No original dispatcher instructions execute. Private gap256 must be
 * checked with actual child/helper stack behavior before disc integration. */
#define ADR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define ADR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define ADR32(a) (*(volatile uint32_t *)(uint32_t)(a))
void biwn_native_actor_dispatch_body(uint32_t *r);
void biwn_native_actor_dispatch_actor_capture(uint32_t *r);
void biwn_native_actor_dispatch_sprite_capture(uint32_t *r);
#endif
