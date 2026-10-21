/* Coordinator optimized C translation of original1B044..1B154 with the existing
 * separately authored18byte word-scan repair explicitly retained. Original
 * longword behavior remains in resource-load-reference.c. */
/* Scan comparisons have no observable call/return boundary before the next
 * explicit flag-setting operation. Defer their N/Z/V/C bookkeeping; CMP
 * preserves X. Each successful counter increment is1..16, so its X is0.
 * Full helper-visible and return CCR remains explicit. Execution tests must
 * prove this equivalence; intermediate emulated CPU/IRQ timing is not claimed.
 */
#include "resource-load-native.h"
static int signed_gt(uint32_t a,uint32_t b) {
 return (a^0x80000000u)>(b^0x80000000u);
}
void biwn_native_resource_load_body(uint32_t *r) {
 uint32_t value;uint16_t word;
 r[3]=LR32(r[15]+4u);load_nz32(r,r[3]);
 r[2]=LR32(r[15]+8u);load_nz32(r,r[2]);
 r[12]=LR32(r[15]+12u);r[11]=LR32(r[15]+16u);
 r[13]=LR32(r[15]+20u);
 word=LR16(0x47b82u);load_nz16(r,word);
 while(word!=0u) {
  biwn_native_load_yield_capture(r);
  word=LR16(0x47b82u);load_nz16(r,word);
 }
 word=LR16(0x47b80u);load_nz16(r,word);
 while(word!=0u) {
  biwn_native_load_yield_capture(r);
  word=LR16(0x47b80u);load_nz16(r,word);
 }
 LW16(0x47b80u,1u);load_nz16(r,1u);
retry:
 LW32(0x1126a0u,0u);load_nz32(r,0u);
 biwn_native_load_seek_capture(r);
 r[10]=0x1c8000u+r[11];
 biwn_native_load_start_capture(r);
 LW32(0x1126a0u,0u);load_nz32(r,0u);
 LW32(0xbd848u,0u);load_nz32(r,0u);
 value=LR32(0xbd848u);load_cmp32(r,r[10],value);
 if(r[10]>value) {
  r[10]=0x1c8000u+r[11];
  do {
   biwn_native_load_yield_capture(r);
   value=LR32(0xbd848u);load_cmp32(r,r[10],value);
  }while(r[10]>value);
 }
 r[10]=0x1c0000u;biwn_native_load_stop_capture(r);
scan_start:
 value=LR32(r[10]);r[10]+=4u;
 if(value==r[2])goto marker;
 /* Source form of the separately pinned18byte1B0EE repair. SUBQ on
  * A2 does not alter CCR; CMPA/BCS uses unsigned comparison. D0 is
  * not overwritten with the old longword-scan bound constant. */
 r[10]-=2u;
 if(r[10]<0x1c7fffu)goto scan_start;
 LW32(0xbd848u,0u);load_nz32(r,0u);goto retry;
marker:
 r[0]=1u;load_nz32(r,1u);
 do {
  value=LR32(r[10]);r[10]+=4u;
  if(value!=r[2])goto scan_start;
  ++r[0];r[16]&=~16u;r[1]=15u;
 }while(r[0]<=r[1]);
 load_cmp32(r,r[10],0x1c8000u);
 if(signed_gt(r[10],0x1c8000u))goto retry;
 load_cmp32(r,r[12],0u);
 if(r[12]==0u) {
  r[0]=r[10];load_nz32(r,r[0]);return;
 }
 biwn_native_load_copy_capture(r);
 LW16(0x47b80u,0u);load_nz16(r,0u);
 load_cmp32(r,r[13],0u);
 if(r[13]!=0u){LW16(r[13],1u);load_nz16(r,1u);}
 r[0]=0u;load_nz32(r,0u);
}
