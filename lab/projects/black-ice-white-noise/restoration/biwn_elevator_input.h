#ifndef BIWN_ELEVATOR_INPUT_H
#define BIWN_ELEVATOR_INPUT_H
#include "biwn_world_update.h"
enum biwn_elevator_status {BIWN_ELEVATOR_OK=0,BIWN_ELEVATOR_BAD_ARGUMENT=1,
 BIWN_ELEVATOR_BUS_ERROR=2,BIWN_ELEVATOR_DEPENDENCY_ERROR=3};
/* Analyst name for source1A0F8..1A188. Full D0 and ordered public bus
 * effects; scene exit20F0C and setup20F78 remain explicit logical calls.
 * Host errors retain prior effects and leave output unchanged. Private
 * stack, CCR, other registers and asynchronous scheduler timing excluded. */
enum biwn_elevator_status biwn_elevator_input(struct biwn_world_bus *,
 uint32_t incoming_D0,uint32_t *out_D0);
#endif
