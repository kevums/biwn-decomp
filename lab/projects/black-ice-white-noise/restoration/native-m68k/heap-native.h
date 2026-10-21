#ifndef BIWN_HEAP_NATIVE_H
#define BIWN_HEAP_NATIVE_H
/* Coordinator frame/flag helpers. Algorithm bodies are local-model C.
 * r0..r14=D0..D7/A0..A6; r15=originalSP; r16=low16SR.
 * The wrapper restores registers and CCR; C must change only0,1,8,9,16.
 * All target accesses are volatile32; private frame accesses are ordinary.
 */
#include <stdint.h>
extern char biwn_native_heap_start;
#define BIWN_HEAP_FLOOR ((uint32_t)&biwn_native_heap_start)
#define HR(a) (*(volatile uint32_t *)(uint32_t)(a))
#define HW(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
extern void biwn_native_heap_compact_capture(uint32_t *r);
extern void biwn_native_heap_copy_capture(uint32_t *r,uint32_t source,uint32_t destination,uint32_t size);
extern void biwn_native_heap_clear_tail(uint32_t destination);
static inline uint32_t biwn_heap_sub_ccr(uint32_t a,uint32_t b,uint32_t value)
{return(value==0?4u:0u)|(value&0x80000000u?8u:0u)|((a^b)&(a^value)&0x80000000u?2u:0u)|(a<b?17u:0u);}
static inline void biwn_heap_zero_result(uint32_t *r)
{r[0]=0;r[16]=(r[16]&0xfff0u)|4u;}
#endif
