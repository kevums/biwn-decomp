#ifndef BIWN_DECK_SCENE_CONTRACT_H
#define BIWN_DECK_SCENE_CONTRACT_H
#include "../deck-coordinate-update-v2/deck-coordinate-contract.h"
/* Coordinator source for complete original 11828..1186A and 11AD4..11B4C.
 * Explicit services stop at their own outer RTS. No decoding or CPU stepping.
 * Component comparisons and the connected experimental pipeline are separate.
 * Host errors retain prior RAM effects and leave the input CPU unchanged. */
static inline uint32_t scene_alu16(struct biwn_deck_context *s,uint32_t a,uint32_t b,int sub,int cmp) {
 uint32_t v;unsigned carry,overflow;a&=65535u;b&=65535u;
 v=(sub?a-b:a+b)&65535u;carry=sub?a<b:v<a;
 overflow=((sub?((a^b)&(a^v)):((~(a^b))&(a^v)))&0x8000u)!=0;
 deck_nz(s,v,16);s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0u)|(overflow?2u:0u));return v;
}
static inline uint32_t scene_shift(struct biwn_deck_context *s,uint32_t v,unsigned count,int left) {
 unsigned carry=0,overflow=0;
 for(unsigned i=0;i<count;i++){
  uint32_t old=v;
  if(left){carry=v>>31;v<<=1;overflow|=(old^v)>>31;}
  else{carry=v&1u;v>>=1;}
 }
 deck_nz(s,v,32);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(carry?0x11u:0u)|(overflow?2u:0u));return v;
}
static inline void scene_push_word(struct biwn_deck_context *s,uint32_t v) {
 s->cpu.registers[15]-=2;deck_bank(s);deck_write(s,s->cpu.registers[15],2,v);
}
int biwn_deck_scene_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
int biwn_deck_scene_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
#endif
