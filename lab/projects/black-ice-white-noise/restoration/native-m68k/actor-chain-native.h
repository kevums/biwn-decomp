#ifndef BIWN_ACTOR_CHAIN_NATIVE_H
#define BIWN_ACTOR_CHAIN_NATIVE_H
#include <stdint.h>
/* 13C9A packed ABI; D2-D7/A2-A5 saved by root shim.
 * r0..14=D/A,r15=logical original SP,r16=SR,r17=continuation.
 * r18=collision entry,r19=owning public root. One shared context is below a320byte gap; internal collision uses the C ABI. */
#define AMR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define AMR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define AMR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define AMW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define AMW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_actor_chain_move_body(uint32_t *r);
void biwn_native_actor_move_direction_capture(uint32_t *r);
void biwn_native_actor_move_submit_capture(uint32_t *r);
void biwn_actor_chain_collision_call(uint32_t *r);

#define ACR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define ACR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define ACW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define ACW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_actor_chain_collision_body(uint32_t *r);
void biwn_native_actor_collision_outside_index_capture(uint32_t *r);
void biwn_native_actor_collision_outside_scan_capture(uint32_t *r);
void biwn_native_actor_collision_inside_outside_capture(uint32_t *r);
void biwn_native_actor_collision_inside_index_capture(uint32_t *r);
void biwn_actor_chain_outside_index_capture(uint32_t *r);
void biwn_actor_chain_outside_scan_capture(uint32_t *r);
void biwn_actor_chain_inside_outside_capture(uint32_t *r);
void biwn_actor_chain_inside_index_capture(uint32_t *r);
#endif
