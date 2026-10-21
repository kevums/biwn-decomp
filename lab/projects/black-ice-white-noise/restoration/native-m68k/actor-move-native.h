#ifndef BIWN_ACTOR_MOVE_NATIVE_H
#define BIWN_ACTOR_MOVE_NATIVE_H
#include <stdint.h>
/* 13C9A packed ABI; D2-D7/A2-A5 saved by root shim.
 * r0..14=D/A,r15=logical original SP,r16=SR,r17=continuation.
 * C uses explicit original SP while its own frame is below a448byte gap. */
#define AMR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define AMR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define AMR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define AMW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define AMW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_native_actor_move_body(uint32_t *r);
void biwn_native_actor_move_direction_capture(uint32_t *r);
void biwn_native_actor_move_submit_capture(uint32_t *r);
void biwn_native_actor_move_outdoor_capture(uint32_t *r);
void biwn_native_actor_move_indoor_capture(uint32_t *r);
#endif
