#ifndef BIWN_ELEVATOR_DISPLAY_H
#define BIWN_ELEVATOR_DISPLAY_H
#include "biwn_input_dispatch.h"
enum biwn_elevator_display_status {BIWN_ELEVATOR_DISPLAY_OK=0,
 BIWN_ELEVATOR_DISPLAY_BAD_ARGUMENT=1,BIWN_ELEVATOR_DISPLAY_BUS_ERROR=2,
 BIWN_ELEVATOR_DISPLAY_DEPENDENCY_ERROR=3,BIWN_ELEVATOR_DISPLAY_LIMIT=4};
/* Complete source190BC..191F4 caller. scratch maps its private16byte
 * buffer (original entrySP-14). Formatter1B45A receives logical args
 * [scratch,190B8,word]; refresh12620 receives [4]. Both are external
 * dependencies. Each copied character consumes one host copy-budget unit.
 * Full D0 and public bus access order are retained, not private frame/CCR
 * or other registers. Errors preserve prior effects and unchanged outD0. */
enum biwn_elevator_display_status biwn_elevator_display(struct biwn_world_bus *,
 biwn_input_write8,uint32_t scratch,uint32_t copy_budget,
 uint32_t incoming_D0,uint32_t *out_D0);
#endif
