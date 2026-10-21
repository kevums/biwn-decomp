#ifndef BIWN_TYPED_DECK_REGISTERS_H
#define BIWN_TYPED_DECK_REGISTERS_H
#include "../deck-geometry-helpers-v1/helper-contract.h"
/* Structured source helpers,not a decoder. D/A register numbers below are
 * each0..7. Memory accesses and host failure handling stay explicit in the
 * caller. The original CPU/RAM/error/order gate remains authoritative. */
static inline void deck_cpu_move_w_d(struct biwn_deck_context *s,unsigned d,uint32_t value){
 s->cpu.registers[d]=(s->cpu.registers[d]&0xffff0000u)|(value&65535u);deck_nz(s,value,16);
}
static inline void deck_cpu_ext_l_d(struct biwn_deck_context *s,unsigned d){
 s->cpu.registers[d]=deck_sx16(s->cpu.registers[d]);deck_nz(s,s->cpu.registers[d],32);
}
static inline void deck_cpu_asl6_l_d(struct biwn_deck_context *s,unsigned d){
 s->cpu.registers[d]=scene_shift(s,s->cpu.registers[d],6,1);
}
static inline void deck_cpu_move_l_d_a(struct biwn_deck_context *s,unsigned d,unsigned a){
 s->cpu.registers[8+a]=s->cpu.registers[d];
}
static inline void deck_cpu_adda_l(struct biwn_deck_context *s,unsigned a,uint32_t value){
 s->cpu.registers[8+a]+=value;
}
static inline void deck_cpu_clr_w_d(struct biwn_deck_context *s,unsigned d){
 s->cpu.registers[d]&=0xffff0000u;deck_nz(s,0,16);
}
static inline void deck_cpu_addq1_w_d(struct biwn_deck_context *s,unsigned d){
 uint32_t value=scene_alu16(s,s->cpu.registers[d],1,0,0);
 s->cpu.registers[d]=(s->cpu.registers[d]&0xffff0000u)|value;
}
static inline void deck_cpu_movea_w_d_a(struct biwn_deck_context *s,unsigned d,unsigned a){
 s->cpu.registers[8+a]=deck_sx16(s->cpu.registers[d]);
}
static inline void deck_cpu_cmp_l_a_d(struct biwn_deck_context *s,unsigned a,unsigned d){
 (void)deck_alu(s,s->cpu.registers[d],s->cpu.registers[8+a],1,1);
}
static inline int deck_cpu_bhi(const struct biwn_deck_context *s){return(s->cpu.sr&5u)==0;}
#endif
