#ifndef BIWN_ACTOR_INITIALIZE_NATIVE_H
#define BIWN_ACTOR_INITIALIZE_NATIVE_H
#include <stdint.h>
/* Original134DC interface. r0..14=D0-D7/A0-A6,r15=rootSP,r16lowWORD=SR,
 * r17=capture continuation,r18=selected task callback. Root assembly restores
 * D2-D7/A2-A3. Captures load actual helper-visible CPU and original guest SP,
 * then replace all r0..14/SR with helper outputs. Private gap448 is a new
 * component-layout choice; nested native134DCinside native13AE0 needs its own
 * joint frame/real-helper qualification. */
#define AIR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define AIR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define AIR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define AIW8(a,v) (*(volatile uint8_t *)(uint32_t)(a)=(uint8_t)(v))
#define AIW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define AIW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_native_actor_initialize_body(uint32_t *r);
void biwn_native_actor_initialize_outside_capture(uint32_t *r);
void biwn_native_actor_initialize_inside_capture(uint32_t *r);
void biwn_native_actor_initialize_task_capture(uint32_t *r);
#endif
