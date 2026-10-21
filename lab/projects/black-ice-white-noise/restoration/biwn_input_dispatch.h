#ifndef BIWN_INPUT_DISPATCH_H
#define BIWN_INPUT_DISPATCH_H
#include "biwn_world_update.h"
typedef int (*biwn_input_write8)(void *,uint32_t,uint8_t);
enum biwn_dispatch_status { BIWN_DISPATCH_OK=0,BIWN_DISPATCH_BAD_ARGUMENT=1,
 BIWN_DISPATCH_BUS_ERROR=2,BIWN_DISPATCH_DEPENDENCY_ERROR=3,
 BIWN_DISPATCH_LIMIT=4,BIWN_DISPATCH_UNSUPPORTED_TABLE=5 };
/* Analyst name for the complete original CPU routine [191F4,19F2C).
 * Thirteen states, immutable original jump table, original memory order.
 * write8 extends the existing bus without changing its ABI. Calls use logical
 * stack arguments, word values zero-extended, and return D0. Other caller-saved
 * registers/CCR and private stack are excluded; helpers must preserve the
 * original callee-saved registers. Helpers remain explicit dependencies.
 * A shared nonzero loop budget bounds polling/animation waits only. Errors
 * preserve prior effects and leave out_d0 unchanged. No original CPU executes.
 */
enum biwn_dispatch_status biwn_input_dispatch(struct biwn_world_bus *,
 biwn_input_write8,uint32_t loop_budget,uint32_t incoming_d0,uint32_t *out_d0);
#endif
