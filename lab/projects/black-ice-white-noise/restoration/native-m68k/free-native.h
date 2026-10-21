#ifndef BIWN_FREE_NATIVE_H
#define BIWN_FREE_NATIVE_H
#include <stdint.h>
/* Coordinator ABI, not model authorship:
 * r[0]=D0,r[1]=D1,r[2..7]=D2..D7,r[8]=A0,r[9]=A1,
 * r[10]=A2,r[11]=A3,r[12..14]=A4..A6,r[15]=original entry SP,
 * r[16]=saved low16 SR. All uint32 arithmetic wraps.
 * Change only D0,D1,A0,A1,SR and A2/A3 from exact original save-slot reads.
 * Before reading the public handle argument at originalSP+4, write original
 * A3 to originalSP-4, then original A2 to originalSP-8. On every exit read
 * originalSP-8 into r[10], then originalSP-4 into r[11]. Do not change r[15].
 * Private96byte frame lies below these8 original public bytes.
 */
#define FR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define FW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
/* Exact original CLR.L read/write instruction. Do not add a separate read. */
extern void biwn_native_free_clear32(uint32_t address);
static inline uint32_t biwn_free_add(uint32_t a,uint32_t b,uint32_t *X)
{uint32_t result=a+b;*X=result<a?16u:0u;return result;}
#endif
