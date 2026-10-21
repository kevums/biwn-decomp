#ifndef BIWN_TASK_POOL_NATIVE_H
#define BIWN_TASK_POOL_NATIVE_H
#include <stdint.h>
/* r0..14=D/A,r15=entrySSP,r16=SR before mode transition,r17=USP.
 * Source-owned assembly performs original final MOVE SR/AND/MOVE SR and
 * continues at DDCC. Entry is supervisor mode. No returnPC is consumed. */
#define TPW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define TPW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
static inline void task_pool_move_flags(uint32_t*r,uint32_t value,unsigned bits){
 uint32_t mask=bits==16?0xffffu:0xffffffffu,sign=bits==16?0x8000u:0x80000000u;
 value&=mask;r[16]=(r[16]&0xfff0u)|(value?0u:4u)|(value&sign?8u:0u);
}
void biwn_native_task_pool_body(uint32_t*r);
void biwn_native_task_pool_set_usp(uint32_t value);
#endif
