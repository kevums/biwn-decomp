#ifndef BIWN_OVERLAY_H
#define BIWN_OVERLAY_H
#include "biwn_world_update.h"
/* Full original181F8..18554. scratch is the caller's mapped private text
 * buffer (original entrySP-54), not a host pointer. Logical stack args of
 * formatter1B45A: [scratch,format,Xword,Zword,sectorword]; text149AE:
 * [Xword,Yword,text,target,flags,font,colorword,modeword].
 * FullD0 is returned; other caller-saved registers/private stack/CCR are
 * outside this contract. Added host errors retain earlier bus effects and
 * leave out_D0 unchanged. Devices/dependencies remain callback boundaries.
 */
enum biwn_overlay_status {BIWN_OVERLAY_OK=0,BIWN_OVERLAY_BAD_ARGUMENT=1,
 BIWN_OVERLAY_BUS_ERROR=2,BIWN_OVERLAY_DEPENDENCY_ERROR=3};
enum biwn_overlay_status biwn_overlay(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t *);
#endif
