#ifndef BIWN_RESOURCE_RELEASE_NATIVE_H
#define BIWN_RESOURCE_RELEASE_NATIVE_H
#include <stdint.h>
/* Coordinator ABI. r0..14=D0-D7/A0-A6, r15=original entrySP,
 * r16 low16=originalSR. Original12byte MOVEM save/restore is assembly.
 * Implement only void biwn_native_resource_release_body(uint32_t *r).
 * Semantic caller outputs are r0,r1,r8,r9,r16; other frame slots unchanged.
 * Argument is WORD at originalSP+4. Every RR16/RR32 is fresh/ordered.
 * Preserve original50slot scan, wrapped word counters, all matches, no guards.
 */
#define RR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define RR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define RW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
/* Runs actual public1545C on its target native dependency, no host effect.
 * r0/r1/r8/r9 seeded/captured, r16 captures returnedSR. Correct argument
 * push flags/X0 and cache-baseA2 are supplied by this coordinator assembly.
 * Semantic r0 must have its original pre-call value before calling.
 */
void biwn_native_release_free_capture(uint32_t *r,uint32_t handle);
#endif
