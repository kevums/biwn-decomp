#ifndef BIWN_TARGETING_H
#define BIWN_TARGETING_H
#include "biwn_world_update.h"
enum biwn_targeting_status {BIWN_TARGETING_OK=0,BIWN_TARGETING_BAD_ARGUMENT=1,
 BIWN_TARGETING_BUS_ERROR=2,BIWN_TARGETING_DEPENDENCY_ERROR=3};
/* Analyst name for complete CPU20820..20A9C:40candidate selection,
 * projection/cursor fields and a bounded low-word squared-distance loop.
 * Original multiply, direction and division remain explicit logical calls.
 * All arithmetic uses source widths/wrap and signed comparisons. Full D0
 * is returned separately from host status. Other caller-saved registers,
 * CCR/private stack and the producers of candidate/matrix records excluded. */
enum biwn_targeting_status biwn_targeting_update(struct biwn_world_bus *,
 uint32_t incoming_d0,uint32_t *out_d0);
#endif
