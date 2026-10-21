#ifndef BIWN_PANEL_REFRESH_H
#define BIWN_PANEL_REFRESH_H
#include "biwn_world_update.h"
enum biwn_panel_status {BIWN_PANEL_OK=0,BIWN_PANEL_BAD_ARGUMENT=1,
 BIWN_PANEL_BUS_ERROR=2,BIWN_PANEL_DEPENDENCY_ERROR=3,BIWN_PANEL_LIMIT=4};
/* Analyst name for complete12620..12896. Signed word index selects14byte
 * records at410BE: X,Y,width,height,border,text pointer. MMIO is emitted
 * in source order; actual blitter effects belong to the supplied bus.
 * Text149AE logical args are [Xword,Yword,text,target,flags,font,color,mode].
 * Shared work budget bounds border iterations/text scanning. FullD0 and
 * public bus effects retained; private stack/CCR/other registers excluded.
 * Host errors retain prior effects and unchanged output. */
enum biwn_panel_status biwn_panel_refresh(struct biwn_world_bus *,uint16_t,
 uint32_t work_budget,uint32_t *out_D0);
#endif
