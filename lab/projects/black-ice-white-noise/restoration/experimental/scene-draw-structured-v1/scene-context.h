#ifndef BIWN_SCENE17_CONTEXT_H
#define BIWN_SCENE17_CONTEXT_H
#include "../deck-scene-source/deck-scene-contract.h"
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
 if(s->error)return 0;
 if(!s->budget){s->error=4;return 0;}s->budget--;return 1;
}
static inline void scene17_completion(struct biwn_deck_context *s,
 uint32_t projection_return,uint32_t draw_return,uint32_t wait_return){
 uint32_t v;
 deck_call(s,0xe19e,projection_return);deck_call(s,0xe202,draw_return);
 do{
  if(!scene17_work(s))return;
  v=deck_read(s,0x10a684,4);deck_nz(s,v,32);
 }while(v);
 deck_call(s,0xe098,wait_return);
}
#endif
