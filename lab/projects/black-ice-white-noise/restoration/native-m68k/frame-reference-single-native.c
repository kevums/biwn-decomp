#include "frame-reference-single-native.h"
/* Coordinator native ABI/CCR adaptation of original1AE56..1AE86. */
void biwn_native_frame_reference_single_body(uint32_t *r)
{
    const uint32_t sp=r[15];
    FS32(sp-4u)=r[2];
    const uint16_t wanted=FS16(sp+4u);
    uint16_t x=0;
    r[1]&=0xffff0000u;
    r[8]=0x15b4a0u;
    for (uint16_t index=0;index<36u;index++) {
        r[0]=(uint32_t)index*4u;
        if (FS16(r[8]+r[0])==wanted) {
            uint16_t refs=FS16(r[8]+r[0]+2u);
            if (refs) {
                /* TST.W and SUBQ.W memory perform separate fresh reads. */
                refs=FS16(r[8]+r[0]+2u);
                x=refs==0u?16u:0u;
                FS16(r[8]+r[0]+2u)=(uint16_t)(refs-1u);
            }
            break;
        }
        r[1]=(r[1]&0xffff0000u)|(uint16_t)(index+1u);
    }
    r[2]=FS32(sp-4u);
    /* The final MOVE.L restoring D2 defines N/Z, clears V/C and preserves X. */
    r[16]=(r[16]&0xffffffe0u)|x|(r[2]==0u?4u:0u)|((r[2]&0x80000000u)?8u:0u);
}
