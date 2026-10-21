#ifndef BIWN_ANIMATION_H
#define BIWN_ANIMATION_H
#include "biwn_world_update.h"
enum biwn_animation_status { BIWN_ANIMATION_OK=0,BIWN_ANIMATION_BAD_ARGUMENT=1,
 BIWN_ANIMATION_BUS_ERROR=2,BIWN_ANIMATION_DEPENDENCY_ERROR=3,
 BIWN_ANIMATION_WORK_LIMIT=4 };
/* Analyst names for EAC4..EB04 and EB04..EC04. Four-byte frame records use
 * signed byte duration/relative-step fields. Queue args are four original
 * long stack arguments; callback input/result D0 stays explicit because the
 * queue's rejected path clears only its low word. Other caller-saved
 * registers/CCR/private stack are excluded. Partial effects stay on errors.
 * A nonzero host budget bounds catch-up loops; no original code executes. */
enum biwn_animation_status biwn_animation_enqueue(struct biwn_world_bus *,
 uint32_t model,uint32_t frame,uint32_t pose,uint32_t flip,
 uint32_t incoming_d0,uint32_t *out_d0);
enum biwn_animation_status biwn_animation_update(struct biwn_world_bus *,
 uint32_t object,uint32_t incoming_d0,uint32_t work_budget,uint32_t *out_d0);
#endif
