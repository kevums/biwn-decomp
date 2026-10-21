#ifndef BIWN_ACTOR_COLLISION_NATIVE_H
#define BIWN_ACTOR_COLLISION_NATIVE_H
#include <stdint.h>
/* Both original packed entries. r0..14=D/A,r15=working originalSP,
 * r16=SR,r17=Ccontinuation,r18=original entry. Root save size8outdoor/4indoor.
 * Private704reserve is provisional until nested movement/task qualification. */
#define ACR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define ACR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define ACW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define ACW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_native_actor_collision_body(uint32_t *r);
void biwn_native_actor_collision_outside_index_capture(uint32_t *r);
void biwn_native_actor_collision_outside_scan_capture(uint32_t *r);
void biwn_native_actor_collision_inside_outside_capture(uint32_t *r);
void biwn_native_actor_collision_inside_index_capture(uint32_t *r);
#endif
