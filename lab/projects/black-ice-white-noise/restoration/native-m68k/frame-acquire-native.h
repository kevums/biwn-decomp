#ifndef BIWN_FRAME_ACQUIRE_NATIVE_H
#define BIWN_FRAME_ACQUIRE_NATIVE_H
#include <stdint.h>
/* 1AC68..1AE54: D/A register frame, original entrySP and SR.
 * Assembly reproduces LINK A6,#-4 and the 36-byte public MOVEM.
 * r14 is the original live FP; its four-byte scratch is at r14-4.
 * Private state begins 512 bytes below the 44-byte public frame.
 * r17 parks the C stack during a native dependency/division capture.
 * r18 names the original division site for diagnostic PC relocation only.
 * All game loads/stores are direct volatile accesses, not host callbacks.
 */
#define FA16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define FA32(a) (*(volatile uint32_t *)(uint32_t)(a))
static inline uint32_t fa_sx(uint32_t x) { return (x&0x8000u)?(x&0xffffu)|0xffff0000u:x&0xffffu; }
static inline void fa_nz(uint32_t *r,uint32_t v,unsigned bits) {
    uint32_t sign=bits==16?0x8000u:0x80000000u;
    if(bits==16)v&=0xffffu;
    r[16]=(r[16]&~15u)|(v==0u?4u:0u)|((v&sign)?8u:0u);
}
static inline void fa_w(uint32_t *r,unsigned i,uint32_t v) { r[i]=(r[i]&0xffff0000u)|(v&0xffffu);fa_nz(r,v,16); }
static inline void fa_l(uint32_t *r,unsigned i,uint32_t v) { r[i]=v;fa_nz(r,v,32); }
static inline uint16_t fa_arithw(uint32_t *r,uint32_t a,uint32_t b,int subtract,int compare) {
    a&=0xffffu;b&=0xffffu;uint16_t d=(uint16_t)(subtract?a-b:a+b);
    uint32_t carry=subtract?a<b:(uint32_t)d<a;
    uint32_t overflow=(subtract?(a^b):(uint32_t)~(a^b))&(a^d)&0x8000u;
    r[16]=(r[16]&~(compare?15u:31u))|(carry?(compare?1u:17u):0u)|(overflow?2u:0u)|(d==0?4u:0u)|((d&0x8000u)?8u:0u);
    return d;
}
static inline void fa_cmp(uint32_t *r,uint32_t a,uint32_t b) { (void)fa_arithw(r,a,b,1,1); }
static inline void fa_aw(uint32_t *r,unsigned i,uint32_t b) { uint16_t d=fa_arithw(r,r[i],b,0,0);r[i]=(r[i]&0xffff0000u)|d; }
static inline void fa_sw(uint32_t *r,unsigned i,uint32_t b) { uint16_t d=fa_arithw(r,r[i],b,1,0);r[i]=(r[i]&0xffff0000u)|d; }
static inline void fa_asl(uint32_t *r,unsigned i,unsigned bits,unsigned count) {
    uint32_t mask=bits==16?0xffffu:0xffffffffu,sign=bits==16?0x8000u:0x80000000u;
    uint32_t v=r[i]&mask,overflow=0,carry=0;
    for(unsigned n=0;n<count;n++){uint32_t old=v;carry=(old&sign)!=0;v=(old<<1)&mask;overflow|=(old^v)&sign;}
    r[i]=(r[i]&~mask)|v;
    r[16]=(r[16]&~31u)|(carry?17u:0u)|(overflow?2u:0u)|(v==0?4u:0u)|((v&sign)?8u:0u);
}
void biwn_frame_acquire_divs_capture(uint32_t *r);
void biwn_frame_acquire_load_capture(uint32_t *r);
void biwn_frame_acquire_body(uint32_t *r);
#endif
