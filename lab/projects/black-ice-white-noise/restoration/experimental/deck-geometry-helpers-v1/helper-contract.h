#ifndef BIWN_DECK_GEOMETRY_HELPERS_H
#define BIWN_DECK_GEOMETRY_HELPERS_H
#include "../deck-scene-source/deck-scene-contract.h"
typedef int (*biwn_deck_write8)(void *,uint32_t,uint8_t);
/* Added host failures leave input CPU unchanged, retaining earlier RAM effects.
 * CLR.B includes its original RAM read before writing. No MMIO/timing claim. */
static inline void helper_clr8(struct biwn_deck_context *s,biwn_deck_write8 w,uint32_t a) {
 uint8_t old=0;if(s->error)return;
 if(s->bus->read8(s->bus->context,a&0xffffffu,&old)||w(s->bus->context,a&0xffffffu,0))s->error=2;
 deck_nz(s,0,8);
}
static inline uint32_t helper_asr16(struct biwn_deck_context *s,uint32_t a) {
 uint32_t v=((a&65535u)>>1)|(a&0x8000u);unsigned carry=a&1u;
 deck_nz(s,v,16);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(carry?0x11u:0u));return v;
}
/* Model supplies only the three structured bodies, no instruction interpreter.
 * Set PC to the original outer RTS:1098E,10BB2/10C16,1142C respectively.
 * D0..D7 indices0..7,A0..A7 indices8..15. Partial MOVE.W preserves high16.
 * MOVEA/ADDA/LEA/PEA/RTS do not update CCR. PEA uses deck_push without nz.
 * byte_budget bounds CLR iterations; error4 on exhaustion, never clamp input.
 * Helper110D4 service is entered with original113FE return on guest stack.
 */
void biwn_geometry_helper_body(struct biwn_deck_context *,biwn_deck_write8,uint32_t);
int biwn_geometry_helper_call(struct biwn_world_bus *,biwn_deck_write8,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t,uint32_t);
#endif
