#include "frame-reference-release-native.h"
/* Coordinator adaptation of the recovered algorithm and original ABI.
 * Not new local-model authorship or a training target. */
void biwn_native_frame_reference_release_body(uint32_t *r)
{
    const uint32_t sp=r[15];
    uint16_t x=(uint16_t)(r[16]&16u);
    FR32(sp-4u)=r[3];
    FR32(sp-8u)=r[2];
    uint16_t wanted=FR16(sp+4u);
    if (!(wanted&0x8000u)) {
        uint16_t mode=FR16(0x15b530u);
        uint32_t signed_mode=(mode&0x8000u)?0xffff0000u|mode:mode;
        r[0]=signed_mode+signed_mode;
        x=(mode&0x8000u)?16u:0u;
        uint16_t remaining=FR16(0x464a0u+r[0]);
        r[1]&=0xffff0000u;
        r[8]=0x15b4a0u;
        uint16_t index=0;
        while (!(remaining&0x8000u) && remaining) {
            r[0]=(uint32_t)index*4u;
            /* ASL.L #2 of the signed-extended0..35index clears X. */
            x=0;
            uint16_t stored=FR16(r[8]+r[0]);
            if (stored==wanted) {
                uint16_t refs=FR16(r[8]+r[0]+2u);
                if (!(refs&0x8000u) && refs) {
                    /* SUBQ.W memory has a fresh RMW read after TST.W. */
                    refs=FR16(r[8]+r[0]+2u);
                    FR16(r[8]+r[0]+2u)=(uint16_t)(refs-1u);
                }
                remaining=(uint16_t)(remaining-1u);
                wanted=(uint16_t)(wanted+1u);
            }
            index=(uint16_t)(index+1u);
            r[1]=(r[1]&0xffff0000u)|index;
            /* ADDQ.W index0..35 never carries. The following CMP leaves X. */
            x=0;
            if (index>35u) break;
        }
    }
    r[2]=FR32(sp-8u);
    r[3]=FR32(sp-4u);
    /* Final MOVE.L restoring D3 defines N/Z and clears V/C; X survives. */
    r[16]=(r[16]&0xffffffe0u)|x|(r[3]==0?4u:0u)|((r[3]&0x80000000u)?8u:0u);
}
