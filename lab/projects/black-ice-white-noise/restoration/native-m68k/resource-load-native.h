#ifndef BIWN_RESOURCE_LOAD_NATIVE_H
#define BIWN_RESOURCE_LOAD_NATIVE_H
#include <stdint.h>
/* Coordinator ABI/support only. r0..14=D0-D7/A0-A6; r15=entrySP,
 * r16 low16=SR. Assembly saves/restores original D2-D3/A2-A5 (24 bytes).
 * Five LONG arguments: disc offset, marker, handle pointer, byte size, ready ptr.
 * All other helper-visible source registers/CCR are the C body's responsibility.
 * Captures run real helpers at the original guest SP and mutate r0..14/r16.
 * Never restore caller-saved cells from stale locals after a capture.
 * Private C state is 256 bytes below public saves. Nested acquire's 512-byte
 * reservation is a separate, still-unverified integration constraint.
 */
#define LR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define LR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define LW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define LW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
static inline void load_nz32(uint32_t *r,uint32_t v) {
 r[16]=(r[16]&~15u)|(v==0u?4u:0u)|((v&0x80000000u)?8u:0u);
}
static inline void load_nz16(uint32_t *r,uint16_t v) {
 r[16]=(r[16]&~15u)|(v==0u?4u:0u)|((v&0x8000u)?8u:0u);
}
static inline void load_cmp32(uint32_t *r,uint32_t a,uint32_t b) {
 uint32_t d=a-b;
 r[16]=(r[16]&~15u)|(a<b?1u:0u)|(((a^b)&(a^d)&0x80000000u)?2u:0u)|
  (d==0u?4u:0u)|((d&0x80000000u)?8u:0u);
}
static inline void load_add1(uint32_t *r) {
 uint32_t a=r[0],d=a+1u;r[0]=d;
 r[16]=(r[16]&~31u)|(a==0xffffffffu?17u:0u)|(a==0x7fffffffu?2u:0u)|
  (d==0u?4u:0u)|((d&0x80000000u)?8u:0u);
}
void biwn_native_load_yield_capture(uint32_t *r);
/* Seek pushes D3 then PEA2; its8 argument bytes remain for the start call. */
void biwn_native_load_seek_capture(uint32_t *r);
/* Start leaves seek args intact and pushes D0,A2,#1C0000;20 bytes total. */
void biwn_native_load_start_capture(uint32_t *r);
void biwn_native_load_stop_capture(uint32_t *r);
/* Copy pushes A3,(A4),A2, with one fresh read of the handle pointer. */
void biwn_native_load_copy_capture(uint32_t *r);
void biwn_native_resource_load_body(uint32_t *r);
#endif
