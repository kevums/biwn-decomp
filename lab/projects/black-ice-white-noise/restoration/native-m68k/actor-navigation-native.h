#ifndef BIWN_ACTOR_NAVIGATION_NATIVE_H
#define BIWN_ACTOR_NAVIGATION_NATIVE_H
#include <stdint.h>
/* r0..14=D0-D7/A0-A6, r15=logical originalSP, r16=SR,
 * r17=original entry. No original helper calls in these four leaf routines. */
#define NAR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define NAR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define NAR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define NAW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_native_actor_navigation_body(uint32_t *r);
void biwn_native_actor_nav_left(uint32_t *r);
#endif
