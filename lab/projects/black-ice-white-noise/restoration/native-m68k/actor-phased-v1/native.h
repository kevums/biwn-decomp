#ifndef BIWN_ACTOR_PHASED_H
#define BIWN_ACTOR_PHASED_H
#include <stdint.h>
/* Temporary r0..14 hardware registers, r15 original entry SP, r16 SR.
 * No C/context frame survives a game helper. r18 is the task callback. */
#define ADR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define ADR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define ADR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define AIR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define AIR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define AIR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define AIW8(a,v) (*(volatile uint8_t *)(uint32_t)(a)=(uint8_t)(v))
#define AIW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define AIW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
uint32_t biwn_actor_dispatch_phase(uint32_t *r);
uint32_t biwn_actor_initialize_start(uint32_t *r);
uint32_t biwn_actor_initialize_after_placement(uint32_t *r);
#endif
