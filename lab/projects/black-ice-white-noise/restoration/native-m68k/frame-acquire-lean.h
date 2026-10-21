#ifndef BIWN_FRAME_ACQUIRE_LEAN_H
#define BIWN_FRAME_ACQUIRE_LEAN_H
#include <stdint.h>
/* Same original public frame and capture ABI as the separately preserved
 * context-array port. Only X is live between explicit DIVS/call/return
 * boundaries: C comparisons implement source branches without exposing an
 * intermediate emulated NZVC value. Every volatile source access remains.
 * Actual DIVS and loader captures still restore/capture the full source CPU.
 */
#define FA16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define FA32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define FL_INLINE static inline __attribute__((always_inline))
FL_INLINE uint32_t fl_sx(uint32_t x) { return (uint32_t)(int32_t)(int16_t)x; }
FL_INLINE void fl_nz(uint32_t *r,uint32_t v,unsigned bits) {
    uint32_t sign=bits==16?0x8000u:0x80000000u;
    if(bits==16)v&=0xffffu;
    r[16]=(r[16]&~15u)|(v==0u?4u:0u)|((v&sign)?8u:0u);
}
FL_INLINE void fl_w(uint32_t *r,unsigned i,uint32_t v) {r[i]=(r[i]&0xffff0000u)|(v&0xffffu);}
FL_INLINE void fl_l(uint32_t *r,unsigned i,uint32_t v) {r[i]=v;}
FL_INLINE uint16_t fl_arithw(uint32_t *r,uint32_t a,uint32_t b,int subtract,int compare) {
    a&=0xffffu;b&=0xffffu;uint16_t d=(uint16_t)(subtract?a-b:a+b);
    if(!compare)r[16]=(r[16]&~16u)|((subtract?a<b:(uint32_t)d<a)?16u:0u);
    return d;
}
FL_INLINE void fl_aw(uint32_t *r,unsigned i,uint32_t b) {uint16_t d=fl_arithw(r,r[i],b,0,0);fl_w(r,i,d);}
FL_INLINE void fl_sw(uint32_t *r,unsigned i,uint32_t b) {uint16_t d=fl_arithw(r,r[i],b,1,0);fl_w(r,i,d);}
FL_INLINE void fl_asl(uint32_t *r,unsigned i,unsigned bits,unsigned count) {
    uint32_t mask=bits==16?0xffffu:0xffffffffu,v=r[i]&mask;
    r[i]=(r[i]&~mask)|((v<<count)&mask);
    r[16]=(r[16]&~16u)|(((v>>(bits-count))&1u)?16u:0u);
}
void biwn_frame_acquire_divs_capture(uint32_t *r);
void biwn_frame_acquire_load_capture(uint32_t *r);
void biwn_frame_acquire_body(uint32_t *r);
#endif
