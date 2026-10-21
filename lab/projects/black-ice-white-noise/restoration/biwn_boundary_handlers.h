#ifndef BIWN_BOUNDARY_HANDLERS_H
#define BIWN_BOUNDARY_HANDLERS_H
#include "biwn_world_update.h"
/* Analyst translations of CPU19F2C..19FDA and19FDA..1A0F8.
 * Nested geometry/transition helper targets remain explicit call callbacks.
 * Outputs preserve full original D0, including CLR.W retaining upper16bits.
 * Incoming D1 low word matters for type2 directions outside0..3.
 */
enum biwn_boundary_status { BIWN_BOUNDARY_OK=0,BIWN_BOUNDARY_BAD_ARGUMENT=1,
    BIWN_BOUNDARY_SCAN_LIMIT=2,BIWN_BOUNDARY_BUS_ERROR=3,BIWN_BOUNDARY_DEPENDENCY_ERROR=4 };
enum biwn_boundary_status biwn_boundary_type1(struct biwn_world_bus *,
    uint16_t edge,uint16_t direction,uint16_t delta,uint32_t incoming_d0,uint32_t *out_d0);
enum biwn_boundary_status biwn_boundary_type2(struct biwn_world_bus *,
    uint32_t object,uint16_t direction,uint32_t incoming_d0,uint32_t incoming_d1,
    uint32_t scan_limit,uint32_t *out_d0);
/* Added host errors/scan bounds preserve prior memory/helper effects and
 * leave out_d0 unchanged. Original private stack/full CCR excluded.
 */
#endif
