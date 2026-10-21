#ifndef BIWN_M68K_FACT_HELPERS_V2_H
#define BIWN_M68K_FACT_HELPERS_V2_H
#include <stdint.h>
/* Coordinator ISA primitives only, not a game-function implementation.
 * Valid widths for mf_logic:8,16,32. Word writes keep the incoming upper16.
 * mf_sub16/mf_add16 RETURN a word and update CCR ONLY; they do not store
 * any data register. Prefer mf_sub_word/mf_add_word below for Dn updates.
 * Helpers affect the semantic frame only; target memory stays explicit.
 */
static inline void mf_word(uint32_t *r,unsigned index,uint16_t value){
 r[index]=(r[index]&0xffff0000u)|value;
}
static inline void mf_logic(uint32_t *r,uint32_t value,unsigned bits){
 uint32_t mask=bits==32?0xffffffffu:((1u<<bits)-1u);
 value&=mask;
 r[16]=(r[16]&~15u)|(value==0u?4u:0u)|((value&(1u<<(bits-1u)))?8u:0u);
}
static inline uint16_t mf_sub16(uint32_t *r,uint16_t a,uint16_t b){
 uint16_t value=(uint16_t)((uint32_t)a-b);
 r[16]=(r[16]&~31u)|(a<b?17u:0u)|(((a^b)&(a^value)&0x8000u)?2u:0u)|
  (value==0u?4u:0u)|((value&0x8000u)?8u:0u);
 return value;
}
static inline uint16_t mf_add16(uint32_t *r,uint16_t a,uint16_t b){
 uint32_t sum=(uint32_t)a+b;uint16_t value=(uint16_t)sum;
 r[16]=(r[16]&~31u)|(sum>65535u?17u:0u)|((~(a^b)&(a^value)&0x8000u)?2u:0u)|
  (value==0u?4u:0u)|((value&0x8000u)?8u:0u);
 return value;
}
/* Whole register/CCR effects for the named ISA operation; source values
 * passed to these functions are evaluated once, including volatile reads.
 * MOVEA is intentionally absent: assign An without changing CCR.
 */
static inline void mf_move16(uint32_t *r,unsigned index,uint16_t value){
 mf_word(r,index,value);mf_logic(r,value,16);
}
static inline void mf_move32(uint32_t *r,unsigned index,uint32_t value){
 r[index]=value;mf_logic(r,value,32);
}
static inline void mf_sub_word(uint32_t *r,unsigned index,uint16_t value){
 uint16_t result=mf_sub16(r,(uint16_t)r[index],value);mf_word(r,index,result);
}
static inline void mf_add_word(uint32_t *r,unsigned index,uint16_t value){
 uint16_t result=mf_add16(r,(uint16_t)r[index],value);mf_word(r,index,result);
}
static inline uint32_t mf_gt(const uint32_t *r){
 return !(r[16]&4u)&&(((r[16]&8u)!=0u)==((r[16]&2u)!=0u));
}
static inline uint32_t mf_le(const uint32_t *r){
 return (r[16]&4u)||(((r[16]&8u)!=0u)!=((r[16]&2u)!=0u));
}
/* CMPA uses a full32bit subtraction even with a sign-extended word source.
 * Unlike SUBQ, comparison preserves X and does not store a register. */
static inline void mf_cmp32(uint32_t *r,uint32_t a,uint32_t b){
 uint32_t value=a-b;
 r[16]=(r[16]&~15u)|(a<b?1u:0u)|(((a^b)&(a^value)&0x80000000u)?2u:0u)|
  (value==0u?4u:0u)|((value&0x80000000u)?8u:0u);
}
#endif
