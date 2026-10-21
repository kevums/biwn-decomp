#ifndef BIWN_SCENE17_NATIVE_WAIT_CONTEXT_H
#define BIWN_SCENE17_NATIVE_WAIT_CONTEXT_H
#include "../../experimental/deck-scene-source/deck-scene-contract.h"
/* Original successful-entry contract. Helpers execute up to their outer RTS;
 * deck_call consumes that return. Host work/error limits are added behavior.
 * Native direct-bus builds must supply a single physical CLR instruction;
 * portable callback builds explicitly expose its operand read and zero write.
 */
static inline void scene17_clr(struct biwn_deck_context *s,uint32_t address){
 if(s->error)return;
#ifdef SCENE17_NATIVE_DIRECT
 volatile void *p=(volatile void *)(address&0xffffffu);
 __asm__ volatile("clr.l (%0)"::"a"(p):"memory","cc");
#else
 (void)deck_read(s,address,4);deck_write(s,address,4,0);
#endif
 deck_nz(s,0,32);
}
static inline void scene17_clr_push(struct biwn_deck_context *s){
 s->cpu.registers[15]-=4;deck_bank(s);scene17_clr(s,s->cpu.registers[15]);
}
static inline int scene17_work(struct biwn_deck_context *s){
 /* Original target waits/list walks have no synthetic work deadline.
  * Portable callback tests retain their separate finite host budget. */
 return !s->error;
}
static inline void scene17_completion(struct biwn_deck_context *s,
 uint32_t projection_return,uint32_t draw_return,uint32_t wait_return){
 deck_call(s,0xe19e,projection_return);deck_call(s,0xe202,draw_return);
 if(s->error)return;
 /* Original17E5C/17ED6: one long flag read and one backward BNE.
  * Hardware may keep the flag set across scheduler/GPU time slices.
  * Only the completed zero test is committed to the logical CPU context. */
 __asm__ volatile("1: tst.l 0x10a684\n\tbne.s 1b":::"memory","cc");
 deck_nz(s,0,32);
 deck_call(s,0xe098,wait_return);
}
#endif
