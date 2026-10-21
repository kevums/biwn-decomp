#ifndef BIWN_RESOURCE_ACQUIRE_NATIVE_H
#define BIWN_RESOURCE_ACQUIRE_NATIVE_H
#include <stdint.h>
/* Coordinator native ABI, not the game algorithm. r0..14=D0-D7/A0-A6,
 * r15=original entrySP, r16 low16=SR. The assembly reproduces the original
 * 24-byte D2-D5/A2-A3 public MOVEM save and restore. Do not repeat it.
 * The ID is a WORD at entrySP+4. Caller-visible outputs are D0,D1,A0,A1,SR;
 * other unsaved registers must stay unchanged. Preserve source semantic D/A
 * inputs before dependency calls, including callee-saved values inherited by
 * a fresh task during a real loader yield. Original public saves restore the
 * caller's D2-D5/A2-A3 on return. All memory accesses are fresh/ordered.
 */
#define AR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define AR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define AW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define AW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
static inline void acquire_nz32(uint32_t *r,uint32_t v) {
    r[16]=(r[16]&~15u)|(v==0u?4u:0u)|((v&0x80000000u)?8u:0u);
}
static inline void acquire_nz16(uint32_t *r,uint16_t v) {
    r[16]=(r[16]&~15u)|(v==0u?4u:0u)|((v&0x8000u)?8u:0u);
}
static inline uint16_t acquire_add1w(uint32_t *r,uint16_t old) {
    uint16_t v=(uint16_t)(old+1u);
    r[16]=(r[16]&~31u)|(old==0xffffu?17u:0u)|(old==0x7fffu?2u:0u)|
        (v==0u?4u:0u)|((v&0x8000u)?8u:0u);
    return v;
}
static inline void acquire_cmp1w(uint32_t *r,uint16_t old) {
    uint16_t v=(uint16_t)(old-1u);
    r[16]=(r[16]&~15u)|(old==0u?1u:0u)|(old==0x8000u?2u:0u)|
        (v==0u?4u:0u)|((v&0x8000u)?8u:0u);
}
/* Helpers seed/capture guest registers and CCR around the target dependency.
 * Compiled private state starts512bytes below the original public save area;
 * adapters park that C stack in frame+68 and execute dependencies at their
 * original guest argument/SP positions. This preserves scheduler-visible SP
 * and helper outputs derived from it. Actual helper stack depth must fit the
 * checked gap, and compiled stack depth must fit each real task allocation.
 * Wait/signal reproduce PEA #1. Allocate performs the original fresh long
 * size read at descriptor+8 and MOVE.L argument push. Load performs the
 * original D1=entry+8 calculation (X=0 in the 50-slot cache), then pushes
 * ready pointer, descriptor+8, entry+2, descriptor+4, descriptor+0 in that
 * exact volatile read order. Caller must not duplicate these helper reads.
 * Child outputs replace frame caller-saved values; never restore stale locals.
 * Tests initially use explicitly declared target-CPU providers, not real I/O.
 */
void biwn_native_acquire_wait_capture(uint32_t *r);
void biwn_native_acquire_allocate_capture(uint32_t *r,uint32_t descriptor);
void biwn_native_acquire_load_capture(uint32_t *r,uint32_t descriptor,uint32_t entry);
void biwn_native_acquire_signal_capture(uint32_t *r);
void biwn_native_resource_acquire_body(uint32_t *r);
#endif
