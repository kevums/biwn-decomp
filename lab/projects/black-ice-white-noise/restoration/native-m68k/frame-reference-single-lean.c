#include <stdint.h>
/* Coordinator C reconstruction of 1AE56: return index in bits 8..15 and X in bit 4.
 * Preserve the distinct TST and SUBQ volatile reads, including wrap/borrow.
 * The shim restores the public D2 save and derives final MOVE.L flags there. */
uint32_t biwn_frame_single_lean_body(uint32_t wanted)
{
    volatile uint16_t *slot=(volatile uint16_t *)0x15b4a0u;
    for (uint32_t index=0;index<36u;index++,slot+=2) {
        if (slot[0]==(uint16_t)wanted) {
            uint32_t x=0;
            uint16_t refs=slot[1];
            if (refs) {
                refs=slot[1];
                x=refs==0u?16u:0u;
                slot[1]=(uint16_t)(refs-1u);
            }
            return (index<<8)|x;
        }
    }
    return 36u<<8;
}
