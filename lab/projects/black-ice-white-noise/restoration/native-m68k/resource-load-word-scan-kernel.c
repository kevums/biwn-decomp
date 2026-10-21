/* Coordinator C control flow with source-assembled native scan kernel; of original1B044..1B154 with the existing
 * separately authored18byte word-scan repair explicitly retained. Original
 * longword behavior remains in resource-load-reference.c. */
#include "resource-load-native.h"
extern uint32_t biwn_native_load_scan(uint32_t *r);
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
 if(!biwn_native_load_scan(r))goto retry;
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
