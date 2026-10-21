#ifndef BIWN_GPU_MAILBOX_NATIVE_H
#define BIWN_GPU_MAILBOX_NATIVE_H
#include <stdint.h>
/* r0..14=D0-D7/A0-A6, r15=original entrySP, r16=SR,
 * r17=entry(E220 orE2B8), r18=private C bridge stack. */
#define GMR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define GMW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
/* Generic68000flags for MOVE.L and CMPI.L; neither changes X. */
static inline void gpu_mailbox_move_flags(uint32_t *r,uint32_t value){
 r[16]=(r[16]&0xfff0u)|(value?0u:4u)|(value&0x80000000u?8u:0u);
}
static inline void gpu_mailbox_compare_flags(uint32_t *r,uint32_t value,uint32_t operand){
 uint32_t result=value-operand;
 r[16]=(r[16]&0xfff0u)|(result?0u:4u)|(result&0x80000000u?8u:0u)|
  (((value^operand)&(value^result)&0x80000000u)?2u:0u)|(value<operand?1u:0u);
}
void biwn_native_gpu_mailbox_body(uint32_t *r);
void biwn_native_gpu_mailbox_wait_capture(uint32_t *r);
#endif
