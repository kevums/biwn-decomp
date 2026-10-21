#ifndef BIWN_ACTOR_DIRECTION_NATIVE_H
#define BIWN_ACTOR_DIRECTION_NATIVE_H
#include <stdint.h>
/* r[0..14]=D0..D7/A0..A6; r15=original logicalSP; r16=SR;
 * r17=entry; r18=private C bridge stack. Original root saves D2-D4. */
#define ADR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define ADR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define ADW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_native_actor_direction_body(uint32_t *r);
void biwn_native_actor_direction_division_capture(uint32_t *r);
#endif
